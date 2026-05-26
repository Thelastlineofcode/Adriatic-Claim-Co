# County Expansion Playbook

The ETL is designed to expand outward from Harris County. Each new county requires:

1. **Scraper** — add `etl/scrapers/<county>.py` with an `ingest()` function
2. **FEMA download** — add URL to `scripts/download_fema.py` FEMA_URLS dict
3. **Register** — add county to `COUNTY_ORDER` in `run.py` and `SCRAPER_MAP` in `orchestrator.py`
4. **Test** — `python run.py --county <county> --dry-run`

## Expansion Priority Order

| Priority | County | CAD Source | Delinquent Source | Notes |
|---|---|---|---|---|
| 1 | Harris | hcad.org | caopay.harriscountytx.gov | Primary — Houston |
| 2 | Bell | bellcad.org/data-portal | bellcountytax.com | Morgan's Point Resort |
| 3 | Fort Bend | fbcad.org | fortbendcountytx.gov | SW Houston growth |
| 4 | Galveston | galvestoncad.org | galvestoncountytx.gov | Coastal, waterfront |
| 5 | Montgomery | mcad-tx.org | mctx.org | N Houston, appreciating |
| 6 | Brazoria | brazoriacad.org | brazoriacountytx.gov | SE Houston |
| 7 | Chambers | chamberscad.org | chamberscountytx.gov | East, lower competition |

## Data Source Map

- **mvbalaw.com** — covers most Texas counties, monthly auction lists (free)
- **foreclosehouston.com** — Harris-specific pre-sale list (free tier)
- **caopay.harriscountytx.gov** — Harris delinquent account search
- **Texas Comptroller county directory** — https://comptroller.texas.gov/taxes/property-tax/county-directory/

## Adding a New Scraper (Template)

```python
# etl/scrapers/<county>.py
from typing import List, Dict

def ingest() -> List[Dict]:
    records = []
    # 1. Try bulk CSV from CAD data portal
    # 2. Fallback: scrape individual property search
    # 3. Merge with mvbalaw auction list
    return records
```
