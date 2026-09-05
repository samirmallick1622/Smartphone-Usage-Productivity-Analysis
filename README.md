# Smartphone Usage & Productivity — Streamlit Dashboard

An interactive rebuild of the `Smartphone-Usage-Productivity-Analysis.ipynb` notebook.

## Setup

```bash
pip install -r requirements.txt
```

## Run

Put `Smartphone_Usage_Productivity_Dataset_50000.csv` in the same folder as `app.py`
(or upload any CSV with the same columns from the sidebar), then:

```bash
streamlit run app.py
```

## What it does

- Recreates the notebook's cleaning + feature engineering: dedup, `phone_usage_category`
  (Low/Medium/High), `sleep_health` (Good/Poor), `risk_score`, `risk_level`, and `high_risk` flag.
- Sidebar filters: gender, occupation, device type, risk level, age range, daily phone hours.
- Tabs mirroring the notebook's EDA: Overview, Phone Usage vs Productivity, Sleep vs Stress,
  Social Media vs Stress, Risk Analysis, Correlation, and a raw Data Explorer.
- KPI cards, interactive Plotly charts (hover/zoom), and a "download filtered data" button.
