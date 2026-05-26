# Z-34 Laptop Server Setup

Adrianne's machine is the server. Zero cloud spend. All data stays local.

## Prerequisites

```bash
# Python 3.11+
python --version

# Install deps
cd services/tax-etl
pip install -r requirements.txt
```

## First Run (Harris County)

```bash
# 1. Copy env
cp .env.example .env
# Edit .env if you want webhook alerts (optional)

# 2. Download FEMA flood zone data for Harris County (~200MB)
python scripts/download_fema.py --county harris

# 3. Run the ETL
python run.py --county harris

# 4. Launch dashboard
streamlit run dashboard.py
# → Opens at http://localhost:8501
```

## Keep It Running Nightly

```bash
# Option A: leave scheduler running in a terminal
python scripts/schedule.py

# Option B: add to crontab (Mac/Linux)
crontab -e
# Add: 0 2 * * * cd /path/to/services/tax-etl && python run.py --county harris
```

## Sharing Dashboard on Local Network

If Adrianne wants Travone to see the dashboard from another machine on the same WiFi:

```bash
streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501
# Other devices access: http://<Z-34-IP>:8501
```

Find Z-34's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

## Data Location

```
services/tax-etl/
  data/
    tax_lien.db      ← SQLite database (all scored properties)
    fema/
      harris/        ← FEMA flood zone shapefiles
      bell/
```

## Troubleshooting

| Issue | Fix |
|---|---|
| `No data yet` in dashboard | Run `python run.py --county harris` first |
| FEMA flood check returning None | Run `python scripts/download_fema.py --county harris` |
| Scraper returns 0 records | Site structure may have changed — check logs, update selector |
| DB locked | Close dashboard, run ETL, reopen |
