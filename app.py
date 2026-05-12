import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Genome Session Visualizer", page_icon="🧬", layout="wide")


def load_payload(uploaded_file) -> List[Dict[str, Any]]:
    if uploaded_file is not None:
        return json.load(uploaded_file)

    default_path = Path("sample_genome_session.json")
    if default_path.exists():
        with default_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def parse_count(value: str) -> int:
    return int(value.replace(",", ""))


def render_top_cards(session: Dict[str, Any]) -> None:
    user_profile = session.get("user_profile", {})
    stats = session.get("view_2_genomic_library_simulation", {}).get("summary_stats", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("User", user_profile.get("name", "Unknown"))
    c2.metric("Records Loaded", f"{user_profile.get('records_loaded', 0):,}")
    c3.metric("Data Source", user_profile.get("data_source", "N/A"))
    c4.metric("Session Timestamp", session.get("timestamp", "N/A"))

    st.subheader("Variant Distribution Snapshot")
    if stats:
        summary_df = pd.DataFrame(
            {
                "Region": list(stats.keys()),
                "Variants": [parse_count(v) for v in stats.values()],
            }
        )
        chart = px.bar(
            summary_df,
            x="Region",
            y="Variants",
            color="Region",
            title="Variant and Missing Call Counts",
        )
        st.plotly_chart(chart, use_container_width=True)


def render_variant_details(session: Dict[str, Any]) -> None:
    library = session.get("view_2_genomic_library_simulation", {})
    active = library.get("active_search_simulation", {}).get("result", {})
    discovery = library.get("random_discovery_simulation", {})

    st.subheader("Variant Deep Dive")
    left, right = st.columns(2)

    with left:
        st.markdown("### Active Search Result")
        if active:
            st.json(active)
        else:
            st.info("No active search result available.")

    with right:
        st.markdown("### Random Discovery")
        if discovery:
            st.json(discovery)
        else:
            st.info("No random discovery data available.")


def render_context_feeds(session: Dict[str, Any]) -> None:
    morning = session.get("view_1_morning_briefing", {})
    local_news = morning.get("chicago_news_mock", [])
    vet_news = morning.get("veterinary_news_mock", [])

    st.subheader("Context Feeds")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Local News")
        if local_news:
            st.dataframe(pd.DataFrame(local_news), use_container_width=True)
        else:
            st.info("No local news items.")

    with col_b:
        st.markdown("### Veterinary / Genetics News")
        if vet_news:
            st.dataframe(pd.DataFrame(vet_news), use_container_width=True)
        else:
            st.info("No veterinary items.")


def render_journal_and_health(session: Dict[str, Any]) -> None:
    journal = session.get("view_3_personal_journal_entry", {})
    health = session.get("system_health", {})

    st.subheader("Journal + System")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Journal Prompt")
        st.write(f"**Date:** {journal.get('date', 'N/A')}")
        st.write(journal.get("auto_prompt", "No prompt"))
        st.text_area(
            "Note",
            value=journal.get("user_note_placeholder", ""),
            height=150,
        )

    with col_b:
        st.markdown("### System Health")
        st.json(health)


def main() -> None:
    st.title("🧬 Genome Session Visualizer")
    st.caption("Load your structured JSON snapshot and explore genomic + contextual signals.")

    uploaded = st.sidebar.file_uploader("Upload JSON", type=["json"])
    payload = load_payload(uploaded)

    if not payload:
        st.warning("No JSON payload found. Upload a file in the sidebar or add sample_genome_session.json.")
        return

    session_names = [entry.get("simulation_name", f"Session {i + 1}") for i, entry in enumerate(payload)]
    selected_name = st.sidebar.selectbox("Simulation", session_names)
    selected_session = payload[session_names.index(selected_name)]

    render_top_cards(selected_session)
    render_variant_details(selected_session)
    render_context_feeds(selected_session)
    render_journal_and_health(selected_session)


if __name__ == "__main__":
    main()
