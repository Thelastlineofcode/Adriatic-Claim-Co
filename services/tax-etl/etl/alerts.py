"""
Tier A alert system — fires webhook when high-value leads are found.
Works with Discord, Slack, or any webhook URL.
"""
import os
import logging
import httpx
from typing import List, Dict

WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")

def fire_tier_a_alerts(tier_a_properties: List[Dict]):
    if not WEBHOOK_URL or not tier_a_properties:
        if not WEBHOOK_URL:
            logging.info("No ALERT_WEBHOOK_URL set — skipping alerts")
        return

    for p in tier_a_properties:
        msg = (
            f"🔴 **TIER A TAX LEAD** — Adriatic Claim Co\n"
            f"Address: {p.get('address')}\n"
            f"County: {p.get('county', '').upper()}\n"
            f"Score: {p.get('distress_score')}/100\n"
            f"Est Tax Due: ${p.get('est_tax_due', 0):,.2f}\n"
            f"Min Bid: ${p.get('min_bid', 0):,.2f}\n"
            f"Appraised: ${p.get('appraised_value', 0):,.2f}\n"
            f"Flood Zone: {'⚠️ YES' if p.get('is_flood_zone') else '✅ NO' if p.get('is_flood_zone') is False else '❓ Unchecked'}\n"
            f"Auction Date: {p.get('auction_date') or 'Not listed yet'}\n"
            f"Owner: {p.get('owner_name')}"
        )
        try:
            httpx.post(WEBHOOK_URL, json={"content": msg}, timeout=10)
            logging.info(f"Alert sent for {p.get('address')}")
        except Exception as e:
            logging.warning(f"Alert failed for {p.get('address')}: {e}")
