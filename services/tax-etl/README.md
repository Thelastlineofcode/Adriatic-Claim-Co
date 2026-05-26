# Tax Lien ETL Pipeline

Adrianne's local tax opportunity finder. Runs entirely on **Z-34 laptop** — no cloud dependency, no per-lead fees.

## Architecture

```
HCAD (Harris County) → raw ingest → normalize → score → SQLite DB → local dashboard
     ↓
Harris County Delinquent Accounts (caopay.harriscountytx.gov)
     ↓
mvbalaw.com monthly auction list
     ↓
FEMA NFHL flood zone lookup (local GeoJSON)
```

## County Expansion Order
1. **Harris** (primary — Houston, current)
2. **Bell** (Morgan's Point Resort target area)
3. **Fort Bend** (adjacent, growing)
4. **Galveston** (coastal, waterfront opportunity)
5. **Montgomery** (north Houston, appreciating)

## Local Server Setup (Z-34)

```bash
# Prerequisites
pip install -r requirements.txt

# One-time: download FEMA flood zones for Harris County
python scripts/download_fema.py --county harris

# Run ETL (Harris County)
python run.py --county harris

# Start dashboard
python dashboard.py
# Open http://localhost:8501
```

## Scoring Logic

| Signal | Points |
|---|---|
| On delinquent tax roll | +35 |
| On upcoming auction list | +30 |
| Tax due > $2,000 | +15 |
| Appraised value < $150K | +10 |
| NOT in FEMA flood zone | +10 |

**Tier A ≥ 65** → auto-alert (Adrianne priority)
**Tier B 40–64** → watchlist
**Tier C < 40** → skip

## Data Sources
- HCAD property search: https://hcad.org
- Harris delinquent accounts: https://caopay.harriscountytx.gov
- Monthly auction lists: https://mvbalaw.com/tax-sales/month-sales/
- Foreclosure Houston (pre-sale list): https://www.foreclosehouston.com
- FEMA NFHL flood zones: https://msc.fema.gov
