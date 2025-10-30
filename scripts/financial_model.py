#!/usr/bin/env python3
"""Small financial model generator for Adriatic Claim Co.

Generates a simple 3-year forecast (annual) for conservative/base/aggressive scenarios
using the Revenue Strategist assumptions. Outputs JSON to `docs/financials/forecast.json`.
"""
import json
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'financials')
os.makedirs(OUT_DIR, exist_ok=True)

ASSUMPTIONS = {
    'avg_claim_amount': 1200,
    'contingency_pct': 0.10,
    'claims_in_texas_per_year': 352000,  # derived from market doc / avg claim
}

SCENARIOS = {
    'conservative': {'penetration': [0.00005, 0.0001, 0.0002]},
    'base': {'penetration': [0.0005, 0.0015, 0.004]},
    'aggressive': {'penetration': [0.002, 0.006, 0.02]},
}

def run():
    results = {'assumptions': ASSUMPTIONS, 'scenarios': {}}

    for name, s in SCENARIOS.items():
        years = []
        for y, pen in enumerate(s['penetration'], start=1):
            recoveries = int(ASSUMPTIONS['claims_in_texas_per_year'] * pen)
            revenue = recoveries * ASSUMPTIONS['avg_claim_amount'] * ASSUMPTIONS['contingency_pct']
            years.append({'year': y, 'penetration': pen, 'recoveries': recoveries, 'revenue': revenue})
        results['scenarios'][name] = years

    out_json = os.path.join(OUT_DIR, 'forecast.json')
    with open(out_json, 'w') as f:
        json.dump(results, f, indent=2)

    # also write a human-readable summary
    out_md = os.path.join(OUT_DIR, 'forecast.md')
    with open(out_md, 'w') as f:
        f.write('# Financial model forecast\n\n')
        f.write('Assumptions:\n')
        for k, v in ASSUMPTIONS.items():
            f.write(f'- {k}: {v}\n')
        f.write('\n')
        for name, years in results['scenarios'].items():
            f.write(f'## {name.capitalize()}\n')
            for y in years:
                f.write(f"- Year {y['year']}: recoveries={y['recoveries']}, revenue=${y['revenue']:,}\n")
            f.write('\n')

    print('Forecast written to', out_json)

if __name__ == '__main__':
    run()
