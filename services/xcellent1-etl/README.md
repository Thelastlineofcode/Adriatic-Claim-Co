# Xcellent1 Lawn Care — Houston Area Property ETL

Real estate investment pipeline for Xcellent1 Lawn Care & Landscaping family business.
Target areas: Houston metro suburban neighborhoods where landscaping business operates.

## Target Geography
- **Primary**: Harris County (inner loop + NW Houston suburbs where Xcellent1 operates)
- **Secondary**: Fort Bend (SW), Montgomery (N), Brazoria (SE)
- **Asset Type Focus**: Distressed single-family residential, vacant lots, small commercial
- **Strategy**: Leverage existing service area knowledge — Xcellent1 crew sees these neighborhoods daily

## Competitive Advantage
- Xcellent1 field crew = ground-level intel on neighborhood condition, vacancy, distress
- Lawn care clients may be motivated sellers (deferred maintenance, moving)
- Service routes map directly to target acquisition zones

## Data Sources

| Source | Type | Notes |
|---|---|---|
| HCAD bulk download | Free full-county parcel data | Reuses harris.py from tax-etl |
| hctax.net | Delinquent / auction lists | Harris primary |
| mvbalaw.com | Multi-county auction aggregator | Harris + ring |
| HAR.com (Houston MLS) | Days-on-market, price reductions | Playwright — JS-rendered |
| Zillow (Houston) | Zestimate + DOM comps | Playwright |
| Realtor.com (Houston) | Price history | Playwright |
| Code enforcement (COH) | Violations + dangerous structures | city of Houston open data |

## Strategy Filter
Xcellent1 targets overlap with service routes. The scorer adds a `service_route_proximity` flag
if the property is within 5 miles of known Xcellent1 service ZIP codes.

## CLI
```bash
python run.py --zone harris_nw        # NW Houston (primary service area)
python run.py --zone all              # full Houston metro
python run.py --zone harris_nw --dry-run
```

## Playwright Note
HAR.com, Zillow, and Realtor.com are JS-rendered. Static httpx will not work.
This pipeline uses the shared Crawler class from grandees-etl (or local copy).
