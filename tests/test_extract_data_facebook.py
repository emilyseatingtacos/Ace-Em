from __future__ import annotations

import csv
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import extractDataFacebook as pipeline


class FacebookPipelineTests(unittest.TestCase):
    def config(self, **overrides):
        values = {
            "access_token": "token",
            "page_id": "page-id",
            "page_username": "thevetcsr",
            "page_url": "https://www.facebook.com/thevetcsr/",
            "api_version": "v21.0",
            "post_limit": 3,
            "page_size": 2,
            "output_dir": Path("."),
            "since": None,
            "until": None,
            "append_posts": False,
            "sample_data": False,
            "timeout": 30,
        }
        values.update(overrides)
        return pipeline.PipelineConfig(**values)

    def test_fetch_posts_paginates_until_limit(self):
        responses = [
            {
                "data": [{"id": "1"}, {"id": "2"}],
                "paging": {"cursors": {"after": "cursor-1"}},
            },
            {
                "data": [{"id": "3"}, {"id": "4"}],
                "paging": {"cursors": {"after": "cursor-2"}},
            },
        ]

        with patch.object(pipeline, "graph_get", side_effect=responses) as graph_get:
            posts = pipeline.fetch_posts(object(), self.config(), "page-id")

        self.assertEqual(["1", "2", "3"], [post["id"] for post in posts])
        self.assertEqual(2, graph_get.call_count)
        second_call_params = graph_get.call_args_list[1].args[3]
        self.assertEqual("cursor-1", second_call_params["after"])
        self.assertEqual(1, second_call_params["limit"])

    def test_run_pipeline_sample_data_writes_csv_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self.config(
                access_token=None,
                output_dir=Path(tmpdir),
                sample_data=True,
                page_id=None,
            )
            with redirect_stdout(StringIO()):
                followers_path, posts_path, post_count = pipeline.run_pipeline(config)

            self.assertEqual(2, post_count)
            self.assertTrue(followers_path.exists())
            self.assertTrue(posts_path.exists())

            with followers_path.open(newline="", encoding="utf-8") as csv_file:
                followers = list(csv.DictReader(csv_file))
            with posts_path.open(newline="", encoding="utf-8") as csv_file:
                posts = list(csv.DictReader(csv_file))

        self.assertEqual("The Vet CSR", followers[0]["page_name"])
        self.assertEqual("thevetcsr_sample_page", followers[0]["page_id"])
        self.assertEqual("2", str(len(posts)))
        self.assertEqual("80", posts[0]["likes"])


if __name__ == "__main__":
    unittest.main()
