#!/usr/bin/env python3
"""
One-time FEMA flood zone data download.
Usage: python scripts/download_fema.py --county harris
"""
import os
import zipfile
import argparse
import httpx
from pathlib import Path

FEMA_URLS = {
    "harris": "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48201C_20231101",
    "bell":   "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48027C_20240101",
    "fort_bend": "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48157C_20231101",
    "galveston": "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48167C_20231101",
    "montgomery": "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48339C_20231101",
}

FEMA_DATA_DIR = os.getenv("FEMA_DATA_DIR", "./data/fema")

def download_fema(county: str):
    url = FEMA_URLS.get(county)
    if not url:
        print(f"No FEMA URL for county: {county}")
        return
    dest_dir = Path(FEMA_DATA_DIR) / county
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / f"{county}_fema.zip"
    print(f"Downloading FEMA data for {county}...")
    with httpx.stream("GET", url, follow_redirects=True, timeout=120) as r:
        with open(zip_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    print(f"Extracting to {dest_dir}...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    print(f"Done. Shapefiles in {dest_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--county", choices=list(FEMA_URLS.keys()) + ["all"], default="harris")
    args = parser.parse_args()
    counties = list(FEMA_URLS.keys()) if args.county == "all" else [args.county]
    for c in counties:
        download_fema(c)
