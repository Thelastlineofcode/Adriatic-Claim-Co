# Gulf Coast County Coverage

Adriatic Claim Co pipeline starts from Harris County and expands outward through the full Gulf Coast metro.

## Active Counties

| # | County | FIPS | CAD | Auction / Delinquency Source | Records | Verified |
|---|---|---|---|---|---|---|
| 1 | **Harris** | 48201 | hcad.org (bulk) | HCAD bulk (distress filter) | 600,432 | ✅ |
| 2 | **Montgomery** | 48339 | mcad-tx.org | County XLSX delinquent roll | 35,195 | ✅ |
| 3 | **Galveston** | 48167 | galvestoncad.org | LGBS REST API | 211 | ✅ |
| 4 | **Liberty** | 48291 | libertycad.org | LGBS REST API | 110 | ✅ |
| 5 | **Fort Bend** | 48157 | fbcad.org | LGBS REST API | 23 | ✅ |
| 6 | **Brazoria** | 48039 | brazoriacad.org | PBFCM PDF | 16 | ✅ |
| 7 | **Chambers** | 48071 | chamberscad.org | PBFCM PDF | 8 | ✅ |
| 8 | **Bell** | 48027 | bellcad.org | *(pending)* | — | ❌ |

## Source Map

### LGBS REST API (taxsales.lgbs.com/api/)
All counties served by Linebarger Goggan & Sampson. REST JSON — no scraping needed.
- `GET /api/property_sales/?county={NAME}&state=TX&in_bbox={BBOX}&sale_type=SALE,RESALE,STRUCK+OFF,FUTURE+SALE`
- Returns: `account_nbr`, `prop_address_one`, `prop_city`, `value`, `minimum_bid`, `cause_nbr`, `sale_type`, `status`
- **Galveston** (211), **Liberty** (110), **Fort Bend** (23)
- Also available (not yet integrated): Montgomery, Bexar, Dallas, and 100+ other counties

### PBFCM PDFs (pbfcm.com/docs/taxdocs/sales/)
Two distinct PDF formats:
1. **Brazoria** — Item table format: blocks split by `\n(\d+)\s+(\d{5,8}-T)` pattern including GeoIDs, Adjudged Value, Min Bid
2. **Chambers** — Column table format: cause-number-delimited records with CAD account numbers, two dollar amounts, property IDs

### HCAD Bulk (Harris)
- Tab-delimited real_acct.txt (1.6M parcels), cached locally after first download
- Distress filter: low appraised value, tax-exempt owner signals, etc.

### Montgomery County XLSX
- Direct XLSX delinquent roll: 59 columns, header at row 2, 35K aggregated parcels
- URL constructed from county site's request sequence number

## Adding a New County

1. Add `etl/scrapers/<county>.py` with `ingest() -> List[Dict]`
2. Register in `SCRAPER_MAP` in `orchestrator.py`
3. For LGBS counties: add entry in `lgbs.py` `COUNTIES` dict
4. Add schedule slot in `scripts/schedule.py`
5. Test: `python run.py --county <county> --dry-run`
6. Full run: `python run.py --county gulf_coast`

## Texas Deed Sale Reminder

Texas is NOT a lien certificate state. Winning bidders receive a **Constable's/Sheriff's Deed without warranty**.
- Homestead/agricultural: 6-month right of redemption (owner pays bid + 25%)
- All other: 2-year right of redemption (bid + 25% yr1, bid + 50% yr2)
- Always run title search before bidding. Flood zone status is binary: bid or skip.
