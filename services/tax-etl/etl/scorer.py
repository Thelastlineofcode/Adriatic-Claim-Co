"""
Distress scoring engine.
Scores 0-100. Tier A >= 65, Tier B 40-64, Tier C < 40.
Texas is a deed-sale state — weight delinquency and auction status heavily.
"""
from typing import List, Dict

def score_property(p: Dict) -> int:
    score = 0
    if p.get("is_delinquent"):
        score += 35
    if p.get("on_auction_list"):
        score += 30
    if p.get("est_tax_due", 0) > 2000:
        score += 15
    elif p.get("min_bid", 0) > 0:  # fallback for auction-only records
        score += 10
    if 0 < p.get("appraised_value", 0) < 150_000:
        score += 10
    # Flood zone: penalize if in zone A/AE, reward if confirmed safe
    if p.get("is_flood_zone") is False:
        score += 10
    elif p.get("is_flood_zone") is True:
        score -= 20
    return max(0, min(100, score))

def get_tier(score: int) -> str:
    if score >= 65:
        return "A"
    elif score >= 40:
        return "B"
    return "C"

def score_properties(records: List[Dict]) -> List[Dict]:
    for r in records:
        r["distress_score"] = score_property(r)
        r["distress_tier"] = get_tier(r["distress_score"])
    return sorted(records, key=lambda x: x["distress_score"], reverse=True)
