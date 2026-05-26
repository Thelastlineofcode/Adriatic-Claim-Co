# Gulf Coast County Coverage

Adriatic Claim Co pipeline starts from Harris County and expands outward through the full Gulf Coast metro.

## Active Counties

| Priority | County | FIPS | CAD | Auction Source | Notes |
|---|---|---|---|---|---|
| 1 | **Harris** | 48201 | hcad.org (bulk download) | hctax.net + mvbalaw + foreclosehouston | PRIMARY — Houston, 1.6M parcels |
| 2 | **Galveston** | 48167 | galvestoncad.org | mvbalaw | Gulf Coast / waterfront / island |
| 3 | **Fort Bend** | 48157 | fbcad.org | mvbalaw + constable list | SW Houston growth corridor |
| 4 | **Brazoria** | 48039 | brazoriacad.org | mvbalaw + delinquent roll | SE / Gulf Coast |
| 5 | **Montgomery** | 48339 | mcad-tx.org | mvbalaw | North Houston, The Woodlands |
| 6 | **Chambers** | 48071 | chamberscad.org | mvbalaw | East Harris — low competition |
| 7 | **Liberty** | 48291 | libertycad.org | mvbalaw | NE rural — very low competition |
| 8 | **Bell** | 48027 | bellcad.org/data-portal | mvbalaw | Adrianne's Bramble Bush target |

## HCAD Bulk Download (Harris — Critical)

Harris is the only county with a true public bulk data download:
- URL: https://hcad.org/pdata/pdata-property-downloads.html
- Format: pipe-delimited `.txt` files inside `.zip`
- Key files: `real_acct.txt`, `land.txt`, delinquent file
- Size: ~500MB compressed
- Update cadence: certified annually, preliminary quarterly

All other counties use mvbalaw.com auction lists as the primary delinquency signal.
Fort Bend also has a direct constable precinct auction list.
Brazoria publishes a delinquent tax roll at the county website.

## Adding a New County

1. Add `etl/scrapers/<county>.py` with `ingest() -> List[Dict]`
2. Register in `SCRAPER_MAP` in `orchestrator.py`
3. Add FEMA URL to `scripts/download_fema.py`
4. Add schedule slot in `scripts/schedule.py`
5. Test: `python run.py --county <county> --dry-run`

## Texas Deed Sale Reminder

Texas is NOT a lien certificate state. Winning bidders receive a **Constable's/Sheriff's Deed without warranty**.
- Homestead/agricultural: 6-month right of redemption (owner pays bid + 25%)
- All other: 2-year right of redemption (bid + 25% yr1, bid + 50% yr2)
- Always run title search before bidding. Flood zone status is binary: bid or skip.
