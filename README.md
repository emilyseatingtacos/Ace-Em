# Ace-Em

Simple Streamlit app for visualizing a structured genome session JSON snapshot.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit (typically `http://localhost:8501`).

## Input format

The app expects a JSON array of session objects like this:

- `simulation_name`
- `timestamp`
- `user_profile`
- `view_1_morning_briefing`
- `view_2_genomic_library_simulation`
- `view_3_personal_journal_entry`
- `system_health`

A working sample file is included at `sample_genome_session.json`.
