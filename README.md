# ServiceNow HR Case Pipeline

This lightweight pipeline prepares ServiceNow case exports for repeated analysis and Streamlit ingestion.

## What it does
- Reads `.xlsx` or `.csv` ServiceNow exports
- Normalizes columns, state labels, and priorities
- Cleans short-description text
- Adds request categories using a rules-based rubric
- Adds operational signals (urgent, blocked, follow-up, KB opportunity)
- Computes case age in days from the created timestamp
- Flags aging cases (>7 days, >30 days)
- Exports enriched case-level data and summary outputs

## Run
```bash
python3 servicenow_pipeline.py /path/to/export.xlsx --output-dir ./output