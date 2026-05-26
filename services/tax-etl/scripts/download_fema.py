#!/usr/bin/env python3
"""
One-time FEMA flood zone download for all Gulf Coast counties.
Usage:
  python scripts/download_fema.py --county harris
  python scripts/download_fema.py --county gulf_coast
  python scripts/download_fema.py --county all
"""
import os
import zipfile
import argparse
import httpx
from pathlib import Path

# FEMA NFHL product IDs per county (Texas FIPS codes)
FEMA_URLS = {
    "harris":     "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48201C_20231101",
    "galveston":  "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48167C_20231101",
    "fort_bend":  "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48157C_20231101",
    "brazoria":   "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48039C_20231101",
    "montgomery": "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48339C_20231101",
    "chambers":   "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48071C_20231101",
    "liberty":    "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48291C_20231101",
    "bell":       "https://msc.fema.gov/portal/downloadProduct?productID=NFHL_48027C_20240101",
}

GULF_COAST = ["harris", "galveston", "fort_bend", "brazoria", "montgomery", "chambers", "liberty"]
FEMA_DATA_DIR = os.getenv("FEMA_DATA_DIR", "./data/fema")


def download_fema(county: str):
    url = FEMA_URLS.get(county)
    if not url:
        print(f"No FEMA URL configured for: {county}")
        return
    dest_dir = Path(FEMA_DATA_DIR) / county
    dest_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dest_dir / f"{county}_fema.zip"
    print(f"[{county}] Downloading FEMA NFHL flood zones...")
    with httpx.stream("GET", url, follow_redirects=True, timeout=300) as r:
        downloaded = 0
        with open(zip_path, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=65536):
                f.write(chunk)
                downloaded += len(chunk)
        print(f"[{county}] Downloaded {downloaded/1024/1024:.1f} MB")
    print(f"[{county}] Extracting...")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    print(f"[{county}] Done. Shapefiles at {dest_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--county",
        choices=list(FEMA_URLS.keys()) + ["gulf_coast", "all"],
        default="harris"
    )
    args = parser.parse_args()
    if args.county == "gulf_coast":
        counties = GULF_COAST
    elif args.county == "all":
        counties = list(FEMA_URLS.keys())
    else:
        counties = [args.county]
    for c in counties:
        download_fema(c)
    print("\nAll FEMA downloads complete.")
