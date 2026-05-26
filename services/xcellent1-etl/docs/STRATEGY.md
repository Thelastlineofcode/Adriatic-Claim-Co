# Xcellent1 Real Estate Strategy — LaPlace, LA

## Base of Operations
Xcellent1 Lawn Care & Landscaping operates out of LaPlace, Louisiana,
in St. John the Baptist Parish. Service routes cover LaPlace, Reserve,
Garyville, and Edgard.

## The Edge
Xcellent1 field crews run service routes across St. John the Baptist Parish daily.
They see overgrown yards, boarded windows, accumulated mail, deferred maintenance.
Every route is a live property condition scan. That ground-level signal is combined
with public adjudicated property data here to surface the highest-quality leads.

## Target Profile
- St. John the Baptist Parish, LA
- Adjudicated OR delinquent
- SFR, vacant lot, or small commercial
- Within Xcellent1 service ZIPs (LaPlace 70068, Reserve 70084, Garyville 70051)
- Properties where crew has observed distress = acquisition_priority HIGH

## Acquisition Priority Tiers
| Tier | Criteria | Action |
|---|---|---|
| HIGH | In service ZIP + adjudicated/delinquent | Bid / contact parish council immediately |
| MEDIUM | Ring parish (St. Charles or St. James) + adjudicated | Research title, watch list |
| LOW | Out of area, low distress signal | Skip |

## Louisiana Adjudicated vs. Texas Tax Deed
| Factor | Louisiana (Adjudicated) | Texas (Tax Deed) |
|---|---|---|
| Redemption period | None after completed sale | 2 years (non-homestead) |
| Seller | Parish council directly | Constable/Sheriff auction |
| Price | Often well below market | Competitive bidding |
| Title risk | Prior mortgages may survive | Same |
| Investor competition | Very low (LaPlace market) | High (Houston market) |

## Ring Strategy
St. Charles (Destrehan/Luling) and St. James (Gramercy/Lutcher) border St. John
and are already partially covered by Grandee's pipeline. Xcellent1 ring scrapers
are lightweight fallbacks that pull lataxauction.com for these parishes in case
Grandee's ETL has not run or data is stale.

## Full Nightly Schedule Context
| Time CDT | Pipeline | Task |
|---|---|---|
| 1:00 AM | tax-etl (AdriaticCC) | Harris HCAD bulk |
| 1:30–3:30 AM | tax-etl | Gulf Coast ring |
| 4:00 AM | grandees-etl | St. Charles primary |
| 4:30–5:00 AM | grandees-etl | Jefferson, St. John |
| 5:30 AM | xcellent1-etl | St. John the Baptist (LaPlace) |
| 5:50 AM | xcellent1-etl | St. Charles ring |
| 6:10 AM | xcellent1-etl | St. James ring |
