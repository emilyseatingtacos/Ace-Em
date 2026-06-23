"""Extract scalable Facebook page metrics for The Vet CSR.

The script reads a Facebook Page access token from a .env file, calls the
Facebook Graph API, and writes follower and recent-post metrics to CSV files.
It supports pagination, retry-enabled HTTP requests, and a sample-data mode so
that the pipeline can be run without live Facebook credentials.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_API_VERSION = "v21.0"
DEFAULT_PAGE_USERNAME = "thevetcsr"
DEFAULT_PAGE_URL = "https://www.facebook.com/thevetcsr/"
DEFAULT_POST_LIMIT = 500
DEFAULT_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30
FOLLOWERS_CSV = "facebook_followers.csv"
POSTS_CSV = "facebook_posts.csv"
POST_FIELDS = ",".join(
    [
        "id",
        "permalink_url",
        "created_time",
        "message",
        "shares",
        "likes.summary(true).limit(0)",
        "comments.summary(true).limit(0)",
    ]
)


class FacebookAPIError(RuntimeError):
    """Raised when the Facebook Graph API returns an error response."""


@dataclass(frozen=True)
class PipelineConfig:
    """Runtime settings for a Facebook metrics extraction run."""

    access_token: str | None
    page_id: str | None
    page_username: str
    page_url: str
    api_version: str
    post_limit: int
    page_size: int
    output_dir: Path
    since: str | None
    until: str | None
    append_posts: bool
    sample_data: bool
    timeout: int

    @property
    def page_identifier(self) -> str:
        """Return the numeric page ID when provided, otherwise the username."""
        return self.page_id or self.page_username


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        description="Extract follower and post interaction metrics for The Vet CSR Facebook page."
    )
    parser.add_argument(
        "--page-id",
        default=os.getenv("PAGE_ID") or None,
        help="Facebook page ID. Defaults to PAGE_ID from .env when present.",
    )
    parser.add_argument(
        "--page-username",
        default=os.getenv("PAGE_USERNAME", DEFAULT_PAGE_USERNAME),
        help="Facebook page username/slug used when PAGE_ID is not set.",
    )
    parser.add_argument(
        "--page-url",
        default=os.getenv("FACEBOOK_PAGE_URL", DEFAULT_PAGE_URL),
        help="Canonical Facebook page URL to include in CSV output.",
    )
    parser.add_argument(
        "--api-version",
        default=os.getenv("GRAPH_API_VERSION", DEFAULT_API_VERSION),
        help="Facebook Graph API version to use.",
    )
    parser.add_argument(
        "--post-limit",
        type=positive_int,
        default=positive_int(os.getenv("POST_LIMIT", str(DEFAULT_POST_LIMIT))),
        help="Maximum number of recent posts to collect across paginated API responses.",
    )
    parser.add_argument(
        "--page-size",
        type=positive_int,
        default=positive_int(os.getenv("PAGE_SIZE", str(DEFAULT_PAGE_SIZE))),
        help="Number of posts to request per Graph API page. Facebook may cap this value.",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("OUTPUT_DIR", "."),
        help="Directory where CSV files will be written.",
    )
    parser.add_argument(
        "--since",
        default=os.getenv("SINCE") or None,
        help="Optional lower date/time bound for posts, accepted by Graph API (for example 2026-01-01).",
    )
    parser.add_argument(
        "--until",
        default=os.getenv("UNTIL") or None,
        help="Optional upper date/time bound for posts, accepted by Graph API (for example 2026-06-01).",
    )
    parser.add_argument(
        "--append-posts",
        action="store_true",
        default=env_bool("APPEND_POSTS"),
        help="Append post rows instead of replacing facebook_posts.csv on each run.",
    )
    parser.add_argument(
        "--sample-data",
        action="store_true",
        default=env_bool("SAMPLE_DATA"),
        help="Run without Facebook credentials using representative The Vet CSR sample data.",
    )
    parser.add_argument(
        "--timeout",
        type=positive_int,
        default=positive_int(os.getenv("REQUEST_TIMEOUT", str(DEFAULT_TIMEOUT))),
        help="HTTP timeout in seconds for Facebook Graph API requests.",
    )
    return parser.parse_args()


def positive_int(value: str) -> int:
    """Parse a positive integer for CLI/environment configuration."""
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return parsed


def env_bool(name: str) -> bool:
    """Read common boolean-like environment variable values."""
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y", "on"}


def build_config(args: argparse.Namespace) -> PipelineConfig:
    """Create a typed runtime config from parsed arguments and environment."""
    return PipelineConfig(
        access_token=os.getenv("PAGE_ACCESS_TOKEN") or None,
        page_id=args.page_id,
        page_username=args.page_username,
        page_url=args.page_url,
        api_version=args.api_version,
        post_limit=args.post_limit,
        page_size=args.page_size,
        output_dir=Path(args.output_dir),
        since=args.since,
        until=args.until,
        append_posts=args.append_posts,
        sample_data=args.sample_data,
        timeout=args.timeout,
    )


def create_session() -> requests.Session:
    """Create a requests session with retry behavior for transient API failures."""
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def decode_json(response: requests.Response) -> dict[str, Any]:
    """Decode a JSON response and raise a helpful API error on failure."""
    try:
        payload = response.json()
    except ValueError as exc:
        raise FacebookAPIError(
            f"Facebook API returned non-JSON response with status {response.status_code}: "
            f"{response.text[:500]}"
        ) from exc

    if response.status_code >= 400 or "error" in payload:
        error = payload.get("error", {})
        message = error.get("message", response.text)
        code = error.get("code", response.status_code)
        raise FacebookAPIError(f"Facebook API error {code}: {message}")

    return payload


def graph_get(
    session: requests.Session,
    api_version: str,
    node: str,
    params: dict[str, Any],
    timeout: int,
) -> dict[str, Any]:
    """Request a Facebook Graph API node and return decoded JSON."""
    url = f"https://graph.facebook.com/{api_version}/{node.lstrip('/')}"
    response = session.get(url, params=params, timeout=timeout)
    return decode_json(response)


def resolve_page(session: requests.Session, config: PipelineConfig) -> dict[str, Any]:
    """Resolve a page ID or username into page metadata and follower totals."""
    fields = "id,name,followers_count,fan_count,link"
    return graph_get(
        session,
        config.api_version,
        config.page_identifier,
        {"fields": fields, "access_token": config.access_token},
        config.timeout,
    )


def post_query_params(config: PipelineConfig, after: str | None = None) -> dict[str, Any]:
    """Build Graph API parameters for a paginated posts request."""
    params: dict[str, Any] = {
        "fields": POST_FIELDS,
        "limit": min(config.page_size, config.post_limit),
        "access_token": config.access_token,
    }
    if after:
        params["after"] = after
    if config.since:
        params["since"] = config.since
    if config.until:
        params["until"] = config.until
    return params


def fetch_posts(session: requests.Session, config: PipelineConfig, page_id: str) -> list[dict[str, Any]]:
    """Fetch recent posts with engagement summaries across paginated responses."""
    posts: list[dict[str, Any]] = []
    after: str | None = None

    while len(posts) < config.post_limit:
        remaining = config.post_limit - len(posts)
        page_config = replace(config, page_size=min(config.page_size, remaining))
        payload = graph_get(
            session,
            config.api_version,
            f"{page_id}/posts",
            post_query_params(page_config, after),
            config.timeout,
        )
        posts.extend(payload.get("data", []))

        cursors = payload.get("paging", {}).get("cursors", {})
        next_after = cursors.get("after")
        if not payload.get("data") or not next_after or next_after == after:
            break
        after = next_after

    return posts[: config.post_limit]


def sample_page(config: PipelineConfig) -> dict[str, Any]:
    """Return representative page data for local sample runs."""
    return {
        "id": config.page_id or "thevetcsr_sample_page",
        "name": "The Vet CSR",
        "followers_count": 12345,
        "fan_count": 12000,
        "link": config.page_url,
    }


def sample_posts() -> list[dict[str, Any]]:
    """Return representative post data for local sample runs."""
    return [
        {
            "id": "thevetcsr_sample_page_001",
            "permalink_url": "https://www.facebook.com/thevetcsr/posts/sample001",
            "created_time": "2026-05-25T18:20:00+0000",
            "message": "Sample The Vet CSR community update.",
            "shares": {"count": 7},
            "likes": {"summary": {"total_count": 80}},
            "comments": {"summary": {"total_count": 15}},
        },
        {
            "id": "thevetcsr_sample_page_002",
            "permalink_url": "https://www.facebook.com/thevetcsr/posts/sample002",
            "created_time": "2026-05-26T14:10:00+0000",
            "message": "Sample pet wellness reminder.",
            "shares": {"count": 4},
            "likes": {"summary": {"total_count": 56}},
            "comments": {"summary": {"total_count": 9}},
        },
    ]


def summary_count(item: dict[str, Any], key: str) -> int:
    """Return a Graph API summary total_count value for likes/comments."""
    return int(item.get(key, {}).get("summary", {}).get("total_count", 0))


def shares_count(item: dict[str, Any]) -> int:
    """Return a Graph API shares count value."""
    return int(item.get("shares", {}).get("count", 0))


def follower_row(page: dict[str, Any], page_url: str, extracted_at: str) -> dict[str, Any]:
    """Build a follower snapshot row."""
    return {
        "extracted_at": extracted_at,
        "page_id": page.get("id"),
        "page_name": page.get("name"),
        "page_url": page.get("link") or page_url,
        "followers": page.get("followers_count"),
        "fans": page.get("fan_count"),
    }


def post_row(post: dict[str, Any], page: dict[str, Any], extracted_at: str) -> dict[str, Any]:
    """Build a post metrics row."""
    return {
        "extracted_at": extracted_at,
        "page_id": page.get("id"),
        "page_name": page.get("name"),
        "post_id": post.get("id"),
        "created_time": post.get("created_time"),
        "permalink_url": post.get("permalink_url"),
        "message": post.get("message", ""),
        "likes": summary_count(post, "likes"),
        "comments": summary_count(post, "comments"),
        "shares": shares_count(post),
    }


def write_csv(path: Path, rows: list[dict[str, Any]], append: bool = False) -> None:
    """Write dictionaries to a CSV file, optionally appending to existing data."""
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    mode = "a" if append else "w"
    write_header = not append or not path.exists()

    with path.open(mode, newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def print_summary(page: dict[str, Any], posts: list[dict[str, Any]], sample_data: bool) -> None:
    """Print a compact run summary to stdout."""
    if sample_data:
        print("Running with sample data; no Facebook API request was made.\n")

    print("Getting page follower count...\n")
    print(f"Page: {page.get('name')} ({page.get('id')})")
    print(f"Followers: {page.get('followers_count')}")
    print(f"Fans: {page.get('fan_count')}\n")

    print(f"Getting posts and metrics ({len(posts)} posts)...\n")
    for post in posts[:10]:
        print(f"Post ID: {post.get('id')}")
        print(f"URL: {post.get('permalink_url')}")
        print(f"Created at: {post.get('created_time')}")
        print(f"Likes: {summary_count(post, 'likes')}")
        print(f"Comments: {summary_count(post, 'comments')}")
        print(f"Shares: {shares_count(post)}")
        print("-" * 50)

    if len(posts) > 10:
        print(f"... skipped printing {len(posts) - 10} additional posts")


def run_pipeline(config: PipelineConfig) -> tuple[Path, Path, int]:
    """Run the extraction pipeline and return output file paths and post count."""
    extracted_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    if config.sample_data:
        page = sample_page(config)
        posts = sample_posts()[: config.post_limit]
    else:
        if not config.access_token:
            raise FacebookAPIError(
                "Missing PAGE_ACCESS_TOKEN. Create a .env file from .env.example and add a valid "
                "Facebook Page access token, or run with --sample-data."
            )
        session = create_session()
        page = resolve_page(session, config)
        posts = fetch_posts(session, config, page["id"])

    follower_rows = [follower_row(page, config.page_url, extracted_at)]
    post_rows = [post_row(post, page, extracted_at) for post in posts]

    followers_path = config.output_dir / FOLLOWERS_CSV
    posts_path = config.output_dir / POSTS_CSV
    write_csv(followers_path, follower_rows, append=True)
    write_csv(posts_path, post_rows, append=config.append_posts)
    print_summary(page, posts, config.sample_data)
    print(f"\nSaved follower snapshot to {followers_path}")
    print(f"Saved {len(post_rows)} post rows to {posts_path}")

    return followers_path, posts_path, len(post_rows)


def main() -> int:
    """Run the Facebook metrics extraction pipeline."""
    load_dotenv()
    config = build_config(parse_args())

    try:
        run_pipeline(config)
    except FacebookAPIError as exc:
        print(exc, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
