"""
City of Houston Code Enforcement violations — open data.
Distressed properties with violations = motivated sellers + below-market pricing.

Source: City of Houston Open Data Portal
https://cohgis-mycity.opendata.arcgis.com/datasets/coh-code-enforcement-cases

This is a GeoJSON API — no JS rendering needed, pure httpx.
"""
import logging
import httpx
from typing import List, Dict

logger = logging.getLogger(__name__)

COH_API = (
    "https://cohgis-mycity.opendata.arcgis.com/datasets/coh-code-enforcement-cases"
    "/api/query?outFields=*&where=1%3D1&f=geojson&resultRecordCount=2000"
    "&orderByFields=OPEN_DATE+DESC"
)


def get_violations(zip_codes: set = None) -> List[Dict]:
    """Fetch recent CoH code enforcement violations. Optionally filter by ZIP."""
    try:
        resp = httpx.get(COH_API, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        records = []
        for f in features:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [])
            zip_code = str(props.get("ZIP_CODE", "")).strip()
            if zip_codes and zip_code not in zip_codes:
                continue
            records.append({
                "address": props.get("ADDRESS", ""),
                "zip_code": zip_code,
                "violation_type": props.get("CASE_TYPE", ""),
                "violation_status": props.get("CASE_STATUS", ""),
                "open_date": props.get("OPEN_DATE", ""),
                "lat": coords[1] if len(coords) >= 2 else None,
                "lon": coords[0] if len(coords) >= 2 else None,
                "source": "coh_code_enforcement",
            })
        logger.info(f"[xcellent1/code_enforcement] {len(records)} violations")
        return records
    except Exception as e:
        logger.warning(f"[xcellent1/code_enforcement] failed: {e}")
        return []
