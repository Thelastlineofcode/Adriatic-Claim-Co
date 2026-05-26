"""
FEMA flood zone lookup using local GeoJSON/Shapefile.
Download once, query locally — no API key needed.
"""
import os
import logging
from typing import Optional

FEMA_DATA_DIR = os.getenv("FEMA_DATA_DIR", "./data/fema")

_flood_gdf = None

def _load_flood_gdf():
    global _flood_gdf
    if _flood_gdf is not None:
        return _flood_gdf
    try:
        import geopandas as gpd
        path = os.path.join(FEMA_DATA_DIR, "S_Fld_Haz_Ar.shp")
        if not os.path.exists(path):
            logging.warning(f"FEMA shapefile not found at {path}. Run: python scripts/download_fema.py")
            return None
        _flood_gdf = gpd.read_file(path)
        logging.info(f"Loaded FEMA flood zones: {len(_flood_gdf)} polygons")
    except Exception as e:
        logging.warning(f"Failed to load FEMA data: {e}")
        return None
    return _flood_gdf

def check_flood_zone(lat: float, lon: float) -> dict:
    """
    Returns {is_flood_zone: bool, zone_code: str}
    Zone A/AE/AO = high risk. Zone X = minimal risk.
    """
    gdf = _load_flood_gdf()
    if gdf is None:
        return {"is_flood_zone": None, "flood_zone_code": None}
    try:
        from shapely.geometry import Point
        point = Point(lon, lat)
        matches = gdf[gdf.geometry.contains(point)]
        if matches.empty:
            return {"is_flood_zone": False, "flood_zone_code": "X"}
        zone = matches.iloc[0].get("FLD_ZONE", "")
        high_risk = zone.upper().startswith(("A", "V"))
        return {"is_flood_zone": high_risk, "flood_zone_code": zone}
    except Exception as e:
        logging.warning(f"Flood zone check failed: {e}")
        return {"is_flood_zone": None, "flood_zone_code": None}
