# Xcellent1 Lawn Care — LaPlace, LA Property ETL

Real estate investment pipeline for Xcellent1 Lawn Care & Landscaping family business.
Operates out of LaPlace, Louisiana — St. John the Baptist Parish.

## Target Geography
- **Primary**: St. John the Baptist Parish, LA (LaPlace, Reserve, Garyville, Edgard)
- **Secondary ring**: St. Charles Parish (Hahnville, Destrehan, Luling), St. James Parish (Lutcher, Gramercy)
- **Asset Types**: Distressed SFR, vacant lots, adjudicated properties, commercial
- **Strategy**: Xcellent1 service routes = ground-level neighborhood intel on condition + vacancy

## Competitive Advantage
- Field crews operating in LaPlace daily see overgrown lots, boarded windows, deferred maintenance
- Service route ZIPs map directly to acquisition targets
- Same adjudicated property acquisition path as Grandee's (St. Charles) — no redemption period

## Data Sources

| Source | Type | Notes |
|---|---|---|
| St. John the Baptist Assessor | Parcel data | https://www.sjbassessor.org |
| St. John Parish Govt | Adjudicated + tax sale | https://www.stjohnla.gov |
| lataxauction.com | LA adjudicated aggregator | Playwright — JS-rendered |
| St. Charles Assessor | Secondary ring | https://www.stcharlesassessor.org |
| St. James Parish | Secondary ring | https://www.stjamesla.gov |
| Louisiana Tax Commission | State-level land sales | https://revenue.louisiana.gov/LandSales |

## CLI
```bash
python run.py --parish st_john_the_baptist   # primary
python run.py --parish all                   # full ring
python run.py --parish st_john_the_baptist --dry-run
```

## Louisiana Adjudicated Property
Same process as Grandee's pipeline. See `services/grandees-etl/docs/LOUISIANA_NOTES.md`.
Key: no redemption period post-sale, below-market pricing, low investor competition vs. Texas.
