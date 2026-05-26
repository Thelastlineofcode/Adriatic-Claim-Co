"""
Local SQLite database — runs entirely on Z-34, no cloud needed.
Uses SQLAlchemy core for portability (can swap to Postgres later).
"""
import os
import logging
from datetime import datetime
from typing import List, Dict
from sqlalchemy import create_engine, text, MetaData, Table, Column
from sqlalchemy import String, Float, Boolean, Integer, DateTime

DB_PATH = os.getenv("DB_PATH", "./data/tax_lien.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    engine = create_engine(f"sqlite:///{DB_PATH}")
    _ensure_schema(engine)
    return engine

def _ensure_schema(engine):
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parcel_id TEXT,
                owner_name TEXT,
                address TEXT,
                city TEXT,
                county TEXT,
                appraised_value REAL,
                est_tax_due REAL,
                min_bid REAL,
                is_delinquent INTEGER,
                on_auction_list INTEGER,
                auction_date TEXT,
                is_flood_zone INTEGER,
                flood_zone_code TEXT,
                distress_score INTEGER,
                distress_tier TEXT,
                source TEXT,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE(parcel_id, county)
            )
        """))
        conn.commit()

def upsert_properties(engine, records: List[Dict]):
    now = datetime.utcnow().isoformat()
    with engine.connect() as conn:
        for r in records:
            conn.execute(text("""
                INSERT INTO properties (
                    parcel_id, owner_name, address, city, county,
                    appraised_value, est_tax_due, min_bid,
                    is_delinquent, on_auction_list, auction_date,
                    is_flood_zone, flood_zone_code,
                    distress_score, distress_tier, source,
                    created_at, updated_at
                ) VALUES (
                    :parcel_id, :owner_name, :address, :city, :county,
                    :appraised_value, :est_tax_due, :min_bid,
                    :is_delinquent, :on_auction_list, :auction_date,
                    :is_flood_zone, :flood_zone_code,
                    :distress_score, :distress_tier, :source,
                    :created_at, :updated_at
                )
                ON CONFLICT(parcel_id, county) DO UPDATE SET
                    distress_score=excluded.distress_score,
                    distress_tier=excluded.distress_tier,
                    is_delinquent=excluded.is_delinquent,
                    on_auction_list=excluded.on_auction_list,
                    est_tax_due=excluded.est_tax_due,
                    min_bid=excluded.min_bid,
                    auction_date=excluded.auction_date,
                    updated_at=excluded.updated_at
            """), {**r, "created_at": now, "updated_at": now})
        conn.commit()
    logging.info(f"Upserted {len(records)} records to DB")
