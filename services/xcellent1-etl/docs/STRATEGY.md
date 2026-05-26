# Xcellent1 Real Estate Strategy

## The Edge
Xcellent1's lawn care service routes are a real-time neighborhood intelligence feed.
Field crews see: overgrown yards, accumulated mail, boarded windows, deferred maintenance.
Every route is a property scan. That ground-level signal is combined with public data here.

## Target Profile
- Harris County residential, class A/R (SFR)
- Appraised value $40k–$250k
- Delinquent OR on auction list
- Code enforcement violations (City of Houston open data)
- Within Xcellent1 service ZIP codes = acquisition priority HIGH

## Acquisition Priority Tiers
| Tier | Criteria | Action |
|---|---|---|
| HIGH | In service zone + delinquent + code violations | Bid immediately, skip-trace owner |
| MEDIUM | In service zone + delinquent, no violations | Research title, add to watch list |
| LOW | Out of zone but strong distress signal | Hold for future expansion routes |

## HAR.com Comp Enrichment
HAR (Houston Association of Realtors) is the Houston MLS. Days on market, price reductions,
and sold comps from HAR give an ARV estimate for each candidate. Playwright scrapes
the JS-rendered search results and attaches `arv_estimate` + `comp_count` to each record.

## City of Houston Code Enforcement
CoH open data GeoJSON endpoint returns active code enforcement cases with addresses.
Violations = high distress signal. Cross-referencing delinquent tax parcels with
open code cases produces the highest-quality lead list in the pipeline.

## Nightly Schedule
Runs at 5:30 AM CDT — AFTER tax-etl Harris bulk download (1 AM) completes.
Pipelines are independent but share the same HCAD data layer.
