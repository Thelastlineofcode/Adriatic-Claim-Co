# Grandee's — St. Charles Parish Property ETL

Real estate investment pipeline for Grandee's Snoball Kitchen and Food Commissary operations in St. Charles Parish, Louisiana.

## Target Geography
- **Primary**: St. Charles Parish, LA (Jefferson, St. John the Baptist as secondary ring)
- **Parish Seat**: Hahnville, LA
- **Target Asset Types**: Distressed commercial, vacant land, tax-adjudicated properties

## Data Sources

| Source | Type | URL |
|---|---|---|
| St. Charles Parish Tax Assessor | Free parcel data | https://www.stcharlesassessor.org |
| Louisiana Tax Commission | Adjudicated property rolls | https://revenue.louisiana.gov/LandSales |
| louisiana.gov adjudicated auctions | Tax-adjudicated listings | https://www.louisiana.gov/services/land-sales |
| St. Charles Parish Govt | Tax sale notices | https://www.stcharlesgov.net |
| Zillow/Realtor (Playwright) | Market comps | JS-rendered pages |
| LATA (Louisiana Tax Auction) | Monthly listings | https://lataxauction.com |

## Tech Stack
- **Crawler**: Playwright (Python async) — handles JS-rendered pages, anti-bot resistance
- **Parser**: BeautifulSoup + lxml for static, Playwright locators for dynamic
- **Storage**: SQLite (local dev) → Postgres (prod)
- **Scheduler**: APScheduler nightly

## CLI
```bash
python run.py --parish st_charles          # single parish
python run.py --parish all                 # full ring
python run.py --parish st_charles --dry-run
```

## Louisiana Tax-Adjudicated Property Notes
- Louisiana parishes maintain a list of "adjudicated" properties — tax delinquent so long the parish has taken ownership
- These are sold via "adjudicated property sales" — often well below market, no redemption period once sold
- St. Charles Parish processes these through the Parish Council — check stcharlesgov.net for current rolls
- Jefferson Parish is high volume; St. John the Baptist is the growth corridor east of St. Charles
