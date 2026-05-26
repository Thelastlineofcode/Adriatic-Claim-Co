"""
Adrianne's local dashboard — runs on Z-34 at http://localhost:8501
Streamlit app showing scored properties with filters.
"""
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

DB_PATH = os.getenv("DB_PATH", "./data/tax_lien.db")

st.set_page_config(page_title="Adriatic Claim Co — Tax Leads", page_icon="🏠", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    engine = create_engine(f"sqlite:///{DB_PATH}")
    try:
        return pd.read_sql("SELECT * FROM properties ORDER BY distress_score DESC", engine)
    except Exception:
        return pd.DataFrame()

df = load_data()

st.title("🏠 Adriatic Claim Co — Tax Lien Lead Finder")
st.caption("Z-34 Local Server | Harris County → Expanding")

if df.empty:
    st.warning("No data yet. Run: `python run.py --county harris`")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("Filters")
counties = st.sidebar.multiselect("County", df["county"].unique().tolist(), default=df["county"].unique().tolist())
tiers = st.sidebar.multiselect("Distress Tier", ["A", "B", "C"], default=["A", "B"])
flood_filter = st.sidebar.radio("Flood Zone", ["All", "Non-Flood Only", "Flood Zone Only"], index=1)

filtered = df[df["county"].isin(counties) & df["distress_tier"].isin(tiers)]
if flood_filter == "Non-Flood Only":
    filtered = filtered[filtered["is_flood_zone"] != 1]
elif flood_filter == "Flood Zone Only":
    filtered = filtered[filtered["is_flood_zone"] == 1]

# --- KPI Row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", len(filtered))
col2.metric("Tier A", len(filtered[filtered["distress_tier"] == "A"]))
col3.metric("Tier B", len(filtered[filtered["distress_tier"] == "B"]))
col4.metric("Avg Score", f"{filtered['distress_score'].mean():.1f}" if not filtered.empty else "—")

# --- Score Distribution Chart ---
if not filtered.empty:
    fig = px.histogram(filtered, x="distress_score", color="distress_tier",
                       color_discrete_map={"A": "#ef4444", "B": "#f97316", "C": "#6b7280"},
                       title="Distress Score Distribution", nbins=20)
    st.plotly_chart(fig, use_container_width=True)

# --- Lead Table ---
st.subheader(f"📋 Leads ({len(filtered)})")
display_cols = ["distress_tier", "distress_score", "address", "county", "owner_name",
                "est_tax_due", "min_bid", "appraised_value", "on_auction_list",
                "auction_date", "is_flood_zone", "source"]
available = [c for c in display_cols if c in filtered.columns]
st.dataframe(
    filtered[available].rename(columns={
        "distress_tier": "Tier", "distress_score": "Score",
        "address": "Address", "county": "County",
        "owner_name": "Owner", "est_tax_due": "Tax Due ($)",
        "min_bid": "Min Bid ($)", "appraised_value": "Appraised ($)",
        "on_auction_list": "At Auction", "auction_date": "Auction Date",
        "is_flood_zone": "Flood Zone", "source": "Source"
    }),
    use_container_width=True,
    height=500
)

# --- CSV Export ---
csv = filtered.to_csv(index=False)
st.download_button("⬇️ Export Leads CSV", csv, "tax_leads.csv", "text/csv")
