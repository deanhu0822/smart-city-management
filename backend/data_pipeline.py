"""
NYC Smart City Nexus — Data Pipeline
Reads 12 raw CSVs from data/raw/ → produces 3 parquet files in data/processed/

Designed to run on NVIDIA GB10 with RAPIDS cuDF.
Falls back to pandas if cuDF is not available (for local dev/testing).

Usage:
    python backend/data_pipeline.py
"""
import os
import sys
import time
import warnings
import numpy as np

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# GPU vs CPU: try cuDF first, fall back to pandas
# ---------------------------------------------------------------------------
try:
    import cudf as pd_engine
    GPU_MODE = True
    print("[GPU MODE] RAPIDS cuDF loaded — processing on GPU")
except ImportError:
    import pandas as pd_engine
    GPU_MODE = False
    print("[CPU MODE] cuDF not available — falling back to pandas")

import pandas as pd  # always available for small ops

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
OUT_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)


def raw(name):
    return os.path.join(RAW_DIR, name)


def timer(label):
    """Simple timer context manager."""
    class Timer:
        def __enter__(self):
            self.t = time.time()
            print(f"  [{label}] ...", end="", flush=True)
            return self
        def __exit__(self, *a):
            elapsed = time.time() - self.t
            print(f" done ({elapsed:.1f}s)")
    return Timer()


def safe_float(series):
    """Convert to float, coercing errors."""
    return pd_engine.to_numeric(series, errors="coerce")


def pct_to_float(series):
    """Convert '0.8%' string to 0.008 float."""
    return pd_engine.to_numeric(
        series.astype(str).str.replace("%", "").str.strip(),
        errors="coerce"
    ) / 100


# ═══════════════════════════════════════════════════════════════════════════
# CLEAN INDIVIDUAL DATASETS
# ═══════════════════════════════════════════════════════════════════════════

def clean_e1():
    """E1: Energy Cost Savings Program — cost burden by location."""
    with timer("E1 Energy Cost Savings"):
        df = pd_engine.read_csv(raw("E1_energy_cost_savings.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        df["total_savings"] = safe_float(df["total_savings"])
        df["electric_savings"] = safe_float(df["electric_savings"])
        df["gas_savings"] = safe_float(df["gas_savings"])
        df["latitude"] = safe_float(df["latitude"])
        df["longitude"] = safe_float(df["longitude"])
        df["bbl"] = df["bbl"].astype(str).str.strip().str.split(".").str[0].str.zfill(10)

        df = df.dropna(subset=["latitude", "longitude"])
        df = df[df["total_savings"] > 0]

        out = df[["address", "borough", "bbl", "latitude", "longitude",
                   "total_savings", "electric_savings", "gas_savings",
                   "industry"]].copy()
        out.columns = ["address", "borough", "bbl", "lat", "lon",
                        "total_savings_usd", "elec_savings_usd", "gas_savings_usd",
                        "industry"]
        print(f"    → {len(out)} rows")
        return out


def clean_e3():
    """E3: Electric Consumption & Cost (NYCHA) — monthly demand profiles."""
    with timer("E3 Electric Consumption"):
        df = pd_engine.read_csv(raw("E3_electric_consumption.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

        df["consumption_kwh"] = safe_float(df["consumption_kwh"])
        df["consumption_kw"] = safe_float(df["consumption_kw"])
        df["current_charges"] = safe_float(df["current_charges"])

        # revenue_month is like "2010-01"
        df["yyyy_mm"] = df["revenue_month"].astype(str).str.strip().str[:7]
        df = df.dropna(subset=["consumption_kwh"])
        df = df[df["consumption_kwh"] > 0]

        # Aggregate for site table
        agg = df.groupby(["development_name", "borough"]).agg(
            avg_monthly_kwh=("consumption_kwh", "mean"),
            max_peak_kw=("consumption_kw", "max"),
            avg_monthly_cost=("current_charges", "mean"),
            months_of_data=("consumption_kwh", "count"),
        ).reset_index()

        # Time series for dispatch simulator
        ts = df[["development_name", "borough", "yyyy_mm",
                  "consumption_kwh", "consumption_kw", "current_charges"]].copy()
        ts.columns = ["property_id", "borough", "yyyy_mm",
                       "electricity_kwh", "peak_kw", "cost_usd"]
        ts["source"] = "nycha"
        ts["gas_kwh"] = 0.0
        ts["total_kwh"] = ts["electricity_kwh"]

        print(f"    → {len(agg)} developments (aggregated), {len(ts)} time series rows")
        return agg, ts


def clean_e4():
    """E4: EV Fleet Station Network — charger locations."""
    with timer("E4 EV Fleet Stations"):
        df = pd_engine.read_csv(raw("E4_ev_fleet_stations.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace(".", "")

        df["latitude"] = safe_float(df["latitude"])
        df["longitude"] = safe_float(df["longitude"])
        df["no_of_plugs"] = safe_float(df["no_of_plugs"]).fillna(1).astype(int)
        df["bbl"] = df["bbl"].astype(str).str.strip().str.split(".").str[0].str.zfill(10)

        df = df.dropna(subset=["latitude", "longitude"])

        out = df[["station_name", "borough", "bbl", "latitude", "longitude",
                   "type_of_charger", "no_of_plugs"]].copy()
        out.columns = ["station_name", "borough", "bbl", "lat", "lon",
                        "charger_type", "num_ports"]
        print(f"    → {len(out)} stations")
        return out


def clean_e5():
    """E5: Municipal Solar Readiness (LL24) — BASE TABLE."""
    with timer("E5 Solar Readiness (BASE)"):
        df = pd_engine.read_csv(raw("E5_solar_readiness.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        df["latitude"] = safe_float(df["latitude"])
        df["longitude"] = safe_float(df["longitude"])
        df["estimated_annual_production"] = safe_float(
            df["estimated_annual_production"].astype(str).str.replace(",", "")
        )
        df["estimated_annual_energy_savings"] = safe_float(
            df["estimated_annual_energy_savings"]
        )
        df["upfront_project_cost"] = safe_float(
            df["upfront_project_cost"].astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "")
        )
        df["bbl"] = df["bbl"].astype(str).str.strip().str.split(".").str[0].str.zfill(10)
        df["bin"] = df["bin"].astype(str).str.strip().str.split(".").str[0]

        # Normalize roof condition
        df["roof_condition"] = df["roof_condition"].astype(str).str.strip().str.lower()
        df["roof_condition"] = df["roof_condition"].where(
            df["roof_condition"].isin(["good", "fair", "poor"]), "unknown"
        )

        # Environmental justice
        df["is_env_justice"] = df["environmental_justice_area"].astype(str).str.strip().str.lower() == "yes"

        # Community board → community district
        df["community_board"] = safe_float(df["community_board"])
        df["community_district"] = df["community_board"].fillna(0).astype(int)

        # Deduplicate: keep latest year_of_report per BBL
        df["year_of_report"] = safe_float(df["year_of_report"]).fillna(0).astype(int)
        df = df.sort_values("year_of_report", ascending=False).drop_duplicates(subset=["bbl"], keep="first")

        df["site_id"] = range(len(df))

        out = df[["site_id", "agency", "site", "address", "borough", "bbl", "bin",
                   "latitude", "longitude", "community_district", "is_env_justice",
                   "roof_condition", "estimated_annual_production",
                   "estimated_annual_energy_savings", "upfront_project_cost"]].copy()
        out.columns = ["site_id", "agency", "site_name", "address", "borough",
                        "bbl", "bin", "lat", "lon", "community_district",
                        "is_env_justice", "roof_condition",
                        "solar_production_kwh_yr", "solar_savings_usd_yr",
                        "upfront_solar_cost_usd"]

        print(f"    → {len(out)} buildings (base table)")
        return out


def clean_e7():
    """E7: LL84 Monthly Energy Data — 2.2M rows of monthly building energy."""
    with timer("E7 LL84 Monthly Energy (2.2M rows)"):
        df = pd_engine.read_csv(raw("E7_ll84_monthly.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # kBtu → kWh (× 0.293071)
        KBTU_TO_KWH = 0.293071

        for col in ["electricity_use__(kbtu)", "natural_gas_use_-_monthly_(kbtu)",
                     "fuel_oil_#1_use_-_monthly_(kbtu)_", "fuel_oil_#2_use_-_monthly_(kbtu)",
                     "fuel_oil_#4_use_-_monthly_(kbtu)", "fuel_oil_#5&6_use_-_monthly_(kbtu)"]:
            if col in df.columns:
                df[col] = safe_float(df[col])

        elec_col = [c for c in df.columns if "electricity" in c and "kbtu" in c.lower()]
        gas_col = [c for c in df.columns if "natural_gas" in c and "kbtu" in c.lower()]
        fuel_cols = [c for c in df.columns if "fuel_oil" in c and "kbtu" in c.lower()]

        df["electricity_kwh"] = safe_float(df[elec_col[0]]) * KBTU_TO_KWH if elec_col else 0
        df["gas_kwh"] = safe_float(df[gas_col[0]]) * KBTU_TO_KWH if gas_col else 0
        fuel_sum = sum(safe_float(df[c]).fillna(0) for c in fuel_cols) * KBTU_TO_KWH if fuel_cols else 0
        df["total_kwh"] = df["electricity_kwh"].fillna(0) + df["gas_kwh"].fillna(0) + fuel_sum

        df["property_id"] = df["property_id"].astype(str).str.strip()

        # Build yyyy_mm from calendar_year + month
        df["calendar_year"] = safe_float(df["calendar_year"]).fillna(0).astype(int)
        df["yyyy_mm"] = df["calendar_year"].astype(str) + "-" + df["month"].astype(str).str.strip()

        # Drop rows with no energy data
        df = df[df["total_kwh"] > 0]

        # Aggregate for site table
        agg = df.groupby(["property_id", "property_name"]).agg(
            avg_monthly_elec_kwh=("electricity_kwh", "mean"),
            avg_monthly_gas_kwh=("gas_kwh", "mean"),
            avg_monthly_total_kwh=("total_kwh", "mean"),
            peak_monthly_elec_kwh=("electricity_kwh", "max"),
            months_reported=("electricity_kwh", "count"),
        ).reset_index()

        # Seasonality index: std / mean
        std_df = df.groupby("property_id")["electricity_kwh"].std().reset_index()
        std_df.columns = ["property_id", "elec_std"]
        mean_df = df.groupby("property_id")["electricity_kwh"].mean().reset_index()
        mean_df.columns = ["property_id", "elec_mean"]
        season = std_df.merge(mean_df, on="property_id")
        season["seasonality_index"] = (season["elec_std"] / season["elec_mean"].replace(0, np.nan)).fillna(0)
        agg = agg.merge(season[["property_id", "seasonality_index"]], on="property_id", how="left")

        # Time series
        ts = df[["property_id", "property_name", "yyyy_mm",
                  "electricity_kwh", "gas_kwh", "total_kwh"]].copy()
        # Get borough from property_name (not available directly — leave blank)
        ts["borough"] = ""
        ts["source"] = "ll84"
        ts["cost_usd"] = np.nan
        ts["peak_kw"] = np.nan
        ts = ts.rename(columns={"property_name": "borough_tmp"})
        ts = ts[["source", "property_id", "borough", "yyyy_mm",
                 "electricity_kwh", "gas_kwh", "total_kwh", "cost_usd", "peak_kw"]]

        print(f"    → {len(agg)} properties (aggregated), {len(ts)} time series rows")
        return agg, ts


def clean_e10():
    """E10: LL84 Annual Benchmarking — ENERGY STAR scores, GHG, building type."""
    with timer("E10 LL84 Benchmarking"):
        # This CSV has 300+ columns — only read what we need
        usecols = [
            "Calendar Year", "Property ID", "Property Name",
            "NYC Borough, Block and Lot (BBL)",
            "Primary Property Type - Self Selected",
            "Year Built", "ENERGY STAR Score",
            "Site EUI (kBtu/ft²)",
            "Total (Location-Based) GHG Emissions (Metric Tons CO2e)",
            "Latitude", "Longitude", "Borough"
        ]
        df = pd_engine.read_csv(raw("E10_ll84_benchmarking.csv"),
                                usecols=usecols, low_memory=False)
        df.columns = ["cal_year", "property_id", "property_name", "bbl",
                       "property_type", "year_built", "energy_star_score",
                       "site_eui", "ghg_tons_co2e", "lat", "lon", "borough"]

        df["bbl"] = df["bbl"].astype(str).str.strip().str.split(".").str[0].str.zfill(10)
        df["energy_star_score"] = safe_float(df["energy_star_score"]).fillna(-1).astype(int)
        df["site_eui"] = safe_float(df["site_eui"])
        df["ghg_tons_co2e"] = safe_float(df["ghg_tons_co2e"])
        df["year_built"] = safe_float(df["year_built"]).fillna(0).astype(int)
        df["cal_year"] = safe_float(df["cal_year"]).fillna(0).astype(int)

        # Keep latest year per BBL
        df = df.sort_values("cal_year", ascending=False).drop_duplicates(subset=["bbl"], keep="first")

        out = df[["bbl", "energy_star_score", "site_eui", "ghg_tons_co2e",
                   "year_built", "property_type"]].copy()
        print(f"    → {len(out)} properties (deduplicated)")
        return out


def clean_w1():
    """W1: DSNY Monthly Tonnage — waste volumes by community district."""
    with timer("W1 DSNY Monthly Tonnage"):
        df = pd_engine.read_csv(raw("W1_dsny_monthly_tonnage.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()

        for col in ["refusetonscollected", "papertonscollected", "mgptonscollected",
                     "resorganicstons", "schoolorganictons", "leavesorganictons",
                     "xmastreetons", "otherorganicstons"]:
            if col in df.columns:
                df[col] = safe_float(df[col]).fillna(0)

        df["all_organics"] = (df.get("resorganicstons", 0) +
                              df.get("schoolorganictons", 0) +
                              df.get("leavesorganictons", 0) +
                              df.get("xmastreetons", 0) +
                              df.get("otherorganicstons", 0))
        df["recycling"] = df["papertonscollected"] + df["mgptonscollected"]
        df["total_tons"] = df["refusetonscollected"] + df["recycling"] + df["all_organics"]
        df["diversion_rate"] = (df["recycling"] + df["all_organics"]) / df["total_tons"].replace(0, np.nan)

        df["community_district"] = safe_float(df["communitydistrict"]).fillna(0).astype(int)

        # Borough mapping
        borough_map = {"Bronx": "Bronx", "Brooklyn": "Brooklyn", "Manhattan": "Manhattan",
                        "Queens": "Queens", "Staten Island": "Staten Island"}
        df["borough"] = df["borough"].map(borough_map).fillna(df["borough"])

        # Aggregate per district
        agg = df.groupby(["borough", "community_district"]).agg(
            avg_refuse_tons_mo=("refusetonscollected", "mean"),
            avg_recycling_tons_mo=("recycling", "mean"),
            avg_organics_tons_mo=("all_organics", "mean"),
            avg_total_tons_mo=("total_tons", "mean"),
            diversion_rate=("diversion_rate", "mean"),
        ).reset_index()

        # District code
        borough_prefix = {"Bronx": "BX", "Brooklyn": "BK", "Manhattan": "MN",
                          "Queens": "QN", "Staten Island": "SI"}
        agg["district_code"] = agg["borough"].map(borough_prefix).fillna("XX") + \
                               agg["community_district"].astype(str).str.zfill(2)

        print(f"    → {len(agg)} community districts")
        return agg


def clean_w2():
    """W2: 311 Requests (DSNY) — complaint hotspots."""
    with timer("W2 311 DSNY Complaints"):
        df = pd_engine.read_csv(raw("W2_311_dsny.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        df["latitude"] = safe_float(df["latitude"])
        df["longitude"] = safe_float(df["longitude"])

        # Categorize complaint types
        df["complaint_cat"] = "other"
        ct = df["complaint_type"].astype(str).str.lower()
        df.loc[ct.str.contains("missed", na=False), "complaint_cat"] = "missed"
        df.loc[ct.str.contains("dirty", na=False), "complaint_cat"] = "dirty"
        df.loc[ct.str.contains("overflow", na=False) | ct.str.contains("litter basket", na=False), "complaint_cat"] = "overflow"
        df.loc[ct.str.contains("dump", na=False), "complaint_cat"] = "dumping"

        # Extract community district from community_board ("13 BROOKLYN" → 13)
        df["community_district"] = safe_float(
            df["community_board"].astype(str).str.extract(r"(\d+)", expand=False)
        ).fillna(0).astype(int)

        df["borough"] = df["borough"].astype(str).str.strip().str.title()

        # Aggregate per district
        agg = df.groupby(["borough", "community_district"]).agg(
            total_complaints=("complaint_cat", "count"),
        ).reset_index()

        # Complaint type counts
        for cat in ["missed", "overflow", "dumping", "dirty"]:
            cat_df = df[df["complaint_cat"] == cat].groupby(
                ["borough", "community_district"]
            ).size().reset_index(name=f"{cat}_count")
            agg = agg.merge(cat_df, on=["borough", "community_district"], how="left")
            agg[f"{cat}_count"] = agg[f"{cat}_count"].fillna(0).astype(int)

        print(f"    → {len(agg)} districts with complaint data")
        return agg


def clean_w3():
    """W3: Litter Basket Inventory — public trash can locations."""
    with timer("W3 Litter Baskets"):
        df = pd_engine.read_csv(raw("W3_litter_baskets.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()

        # Extract lat/lon from point column: "POINT (-74.003 40.651)"
        if "point" in df.columns:
            coords = df["point"].astype(str).str.extract(
                r"POINT\s*\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s*\)"
            )
            df["lon"] = safe_float(coords[0])
            df["lat"] = safe_float(coords[1])

        df = df.dropna(subset=["lat", "lon"])

        out = df[["basketid", "baskettype", "lat", "lon", "section"]].copy()
        out.columns = ["basket_id", "basket_type", "lat", "lon", "section"]
        print(f"    → {len(out)} baskets with coordinates")
        return out


def clean_w7():
    """W7: Food Scrap Drop-Off Locations — composting access points."""
    with timer("W7 Food Scrap Drop-Offs"):
        df = pd_engine.read_csv(raw("W7_food_scrap_dropoffs.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()

        df["latitude"] = safe_float(df["latitude"])
        df["longitude"] = safe_float(df["longitude"])
        df = df.dropna(subset=["latitude", "longitude"])

        out = df[["sitename", "siteaddr", "borough", "latitude", "longitude"]].copy()
        out.columns = ["site_name", "address", "borough", "lat", "lon"]
        print(f"    → {len(out)} composting sites")
        return out


def clean_w8():
    """W8: Disposal Facility Locations — transfer stations (cuOpt depots)."""
    with timer("W8 Disposal Facilities"):
        df = pd_engine.read_csv(raw("W8_disposal_facilities.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()

        df["latitude"] = safe_float(df["latitude"])
        df["longitude"] = safe_float(df["longitude"])

        # Column names after lowercasing have slashes and spaces
        col_map = {c.lower(): c for c in df.columns}
        addr_col = col_map.get("street address", col_map.get("street_address", None))
        city_col = col_map.get("borough/city", col_map.get("borough_city", None))

        out = pd.DataFrame({
            "facility_name": df[col_map["name"]],
            "facility_type": df[col_map["type"]],
            "address": df[addr_col] if addr_col else "",
            "city": df[city_col] if city_col else "",
            "state": df[col_map["state"]],
            "lat": df["latitude"],
            "lon": df["longitude"],
        })
        print(f"    → {len(out)} facilities")
        return out


def clean_w12():
    """W12: Waste Characterization — what's in the trash."""
    with timer("W12 Waste Characterization"):
        df = pd_engine.read_csv(raw("W12_waste_characterization.csv"), low_memory=False)
        df.columns = df.columns.str.strip().str.lower()

        # Column names have spaces (e.g., "material group")
        gen_col = [c for c in df.columns if "generator" in c]
        period_col = [c for c in df.columns if "period" in c]
        mat_group_col = [c for c in df.columns if "material group" in c or "material_group" in c][0]
        mat_cat_col = [c for c in df.columns if "material category" in c or "material_category" in c][0]

        if gen_col:
            df = df[df[gen_col[0]].astype(str).str.lower() == "aggregate"]
        if period_col:
            df = df[df[period_col[0]].astype(str).str.lower() == "annual"]

        # Parse percentages
        pct_col = [c for c in df.columns if "aggregate percent" in c or "aggregate_percent" in c]
        if pct_col:
            df["aggregate_pct"] = pct_to_float(df[pct_col[0]])
        else:
            df["aggregate_pct"] = 0.0

        out = pd.DataFrame({
            "material_group": df[mat_group_col].values,
            "material_category": df[mat_cat_col].values,
            "pct": df["aggregate_pct"].values,
        })

        print(f"    → {len(out)} material categories")
        return out


# ═══════════════════════════════════════════════════════════════════════════
# SPATIAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def haversine_dist(lat1, lon1, lat2, lon2):
    """Vectorized haversine distance in meters."""
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))


def count_within_radius(sites_df, points_df, radius_m):
    """Count how many points are within radius_m of each site. Brute-force but fine for <5K sites."""
    counts = []
    sites_lat = sites_df["lat"].values
    sites_lon = sites_df["lon"].values
    pts_lat = points_df["lat"].values
    pts_lon = points_df["lon"].values

    for i in range(len(sites_lat)):
        dists = haversine_dist(sites_lat[i], sites_lon[i], pts_lat, pts_lon)
        counts.append(int(np.sum(dists <= radius_m)))
    return counts


def nearest_distance(sites_df, points_df):
    """Find distance to nearest point for each site."""
    dists = []
    sites_lat = sites_df["lat"].values
    sites_lon = sites_df["lon"].values
    pts_lat = points_df["lat"].values
    pts_lon = points_df["lon"].values

    for i in range(len(sites_lat)):
        d = haversine_dist(sites_lat[i], sites_lon[i], pts_lat, pts_lon)
        dists.append(float(np.min(d)) if len(d) > 0 else 999999)
    return dists


def nearest_name(sites_df, points_df, name_col="facility_name"):
    """Find name of nearest point for each site."""
    names = []
    sites_lat = sites_df["lat"].values
    sites_lon = sites_df["lon"].values
    pts_lat = points_df["lat"].values
    pts_lon = points_df["lon"].values
    pts_names = points_df[name_col].values

    for i in range(len(sites_lat)):
        d = haversine_dist(sites_lat[i], sites_lon[i], pts_lat, pts_lon)
        names.append(str(pts_names[np.argmin(d)]) if len(d) > 0 else "Unknown")
    return names


# ═══════════════════════════════════════════════════════════════════════════
# BUILD OUTPUT TABLES
# ═══════════════════════════════════════════════════════════════════════════

def build_unified_sites(e1, e3_agg, e4, e5, e7_agg, e10, w1_agg, w2_agg, w3, w7, w8):
    """Build TABLE 1: unified_sites — one row per municipal building."""
    with timer("Building unified_sites"):
        sites = e5.copy()

        # Convert to pandas for joins if using cuDF
        if GPU_MODE:
            sites = sites.to_pandas()
            e7_agg_pd = e7_agg.to_pandas()
            e10_pd = e10.to_pandas()
            e1_pd = e1.to_pandas()
            e4_pd = e4.to_pandas()
            w1_agg_pd = w1_agg.to_pandas()
            w2_agg_pd = w2_agg.to_pandas()
            w3_pd = w3.to_pandas()
            w7_pd = w7.to_pandas()
            w8_pd = w8.to_pandas()
        else:
            e7_agg_pd = e7_agg
            e10_pd = e10
            e1_pd = e1
            e4_pd = e4
            w1_agg_pd = w1_agg
            w2_agg_pd = w2_agg
            w3_pd = w3
            w7_pd = w7
            w8_pd = w8

        # --- BBL joins ---
        # E7: LL84 energy aggregates
        sites = sites.merge(
            e7_agg_pd[["property_id", "avg_monthly_elec_kwh", "avg_monthly_gas_kwh",
                        "avg_monthly_total_kwh", "peak_monthly_elec_kwh",
                        "months_reported", "seasonality_index"]].rename(
                            columns={"property_id": "bbl_match"}),
            left_on="bbl", right_on="bbl_match", how="left"
        ).drop(columns=["bbl_match"], errors="ignore")

        # E10: Benchmarking
        sites = sites.merge(e10_pd, on="bbl", how="left")

        # E1: Energy savings (aggregate by BBL)
        if len(e1_pd) > 0:
            e1_bbl = e1_pd.groupby("bbl").agg(
                area_elec_savings=("elec_savings_usd", "sum"),
            ).reset_index()
            sites = sites.merge(e1_bbl, on="bbl", how="left")
            sites["area_elec_savings"] = sites["area_elec_savings"].fillna(0)

        # Estimate annual cost
        sites["annual_energy_cost_usd"] = sites.get("avg_monthly_elec_kwh", pd.Series(dtype=float)).fillna(0) * 0.22 * 12

        # --- Spatial joins ---
        print("    Spatial: EV stations...", end="", flush=True)
        sites["ev_ports_500m"] = count_within_radius(sites, e4_pd, 500)
        sites["ev_ports_1km"] = count_within_radius(sites, e4_pd, 1000)
        sites["nearest_ev_dist_m"] = nearest_distance(sites, e4_pd)
        print(" done")

        print("    Spatial: Composting sites...", end="", flush=True)
        sites["compost_sites_1km"] = count_within_radius(sites, w7_pd, 1000)
        print(" done")

        print("    Spatial: Transfer stations...", end="", flush=True)
        w8_valid = w8_pd.dropna(subset=["lat", "lon"])
        if len(w8_valid) > 0:
            sites["nearest_transfer_km"] = [d / 1000 for d in nearest_distance(sites, w8_valid)]
            sites["nearest_transfer_stn"] = nearest_name(sites, w8_valid, "facility_name")
        print(" done")

        # --- District joins ---
        sites = sites.merge(
            w1_agg_pd[["borough", "community_district", "avg_refuse_tons_mo",
                        "avg_organics_tons_mo", "diversion_rate"]].rename(
                            columns={"diversion_rate": "district_diversion_rate"}),
            on=["borough", "community_district"], how="left"
        )
        sites = sites.merge(
            w2_agg_pd[["borough", "community_district", "total_complaints"]].rename(
                columns={"total_complaints": "district_complaints"}),
            on=["borough", "community_district"], how="left"
        )

        # --- Computed scores ---
        sites["solar_score"] = sites["solar_production_kwh_yr"].rank(pct=True)
        roof_map = {"good": 1.0, "fair": 0.6, "poor": 0.2, "unknown": 0.4}
        sites["roof_score"] = sites["roof_condition"].map(roof_map).fillna(0.4)
        sites["equity_flag"] = sites["is_env_justice"].astype(float)
        sites["ev_density_score"] = sites["ev_ports_1km"].rank(pct=True)
        sites["energy_intensity_score"] = sites["avg_monthly_total_kwh"].rank(pct=True)
        sites["waste_burden_score"] = sites["avg_refuse_tons_mo"].rank(pct=True)

        # Fill NaNs
        for col in sites.select_dtypes(include=[np.number]).columns:
            sites[col] = sites[col].fillna(0)

        print(f"    → {len(sites)} sites × {len(sites.columns)} columns")
        return sites


def build_district_waste(w1_agg, w2_agg, w3, w7, w8, w12):
    """Build TABLE 2: district_waste — one row per community district."""
    with timer("Building district_waste"):
        if GPU_MODE:
            districts = w1_agg.to_pandas()
            w2_agg_pd = w2_agg.to_pandas()
        else:
            districts = w1_agg.copy()
            w2_agg_pd = w2_agg

        # Merge 311 complaint data
        districts = districts.merge(w2_agg_pd, on=["borough", "community_district"], how="left")

        # Fill NaN complaint counts
        for col in ["total_complaints", "missed_count", "overflow_count",
                     "dumping_count", "dirty_count"]:
            if col in districts.columns:
                districts[col] = districts[col].fillna(0).astype(int)

        # Waste composition → estimate divertible organics
        # Average organic fraction from W12 (roughly ~34% of refuse is organic)
        organic_fraction = 0.34  # from waste characterization data
        districts["est_divertible_organics_tons"] = districts["avg_refuse_tons_mo"] * organic_fraction
        districts["est_energy_potential_kwh"] = districts["est_divertible_organics_tons"] * 500  # kWh per ton via AD

        # Diversion gap
        districts["diversion_gap"] = 0.30 - districts["diversion_rate"]

        # Computed scores
        districts["waste_intensity_score"] = districts["avg_total_tons_mo"].rank(pct=True)

        print(f"    → {len(districts)} districts × {len(districts.columns)} columns")
        return districts


def build_time_series(e3_ts, e7_ts):
    """Build TABLE 3: time_series — monthly energy readings."""
    with timer("Building time_series"):
        if GPU_MODE:
            e3_pd = e3_ts.to_pandas()
            e7_pd = e7_ts.to_pandas()
        else:
            e3_pd = e3_ts
            e7_pd = e7_ts

        common_cols = ["source", "property_id", "borough", "yyyy_mm",
                       "electricity_kwh", "gas_kwh", "total_kwh", "cost_usd", "peak_kw"]

        # Align columns
        for col in common_cols:
            if col not in e3_pd.columns:
                e3_pd[col] = np.nan
            if col not in e7_pd.columns:
                e7_pd[col] = np.nan

        ts = pd.concat([e7_pd[common_cols], e3_pd[common_cols]], ignore_index=True)
        print(f"    → {len(ts)} total time series rows")
        return ts


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print("  NYC SMART CITY NEXUS — DATA PIPELINE")
    print(f"  Mode: {'GPU (RAPIDS cuDF)' if GPU_MODE else 'CPU (pandas)'}")
    print("=" * 60)

    total_start = time.time()

    # --- Phase 1: Clean each dataset ---
    print("\n─── PHASE 1: CLEAN RAW DATASETS ───")
    e1 = clean_e1()
    e3_agg, e3_ts = clean_e3()
    e4 = clean_e4()
    e5 = clean_e5()
    e7_agg, e7_ts = clean_e7()
    e10 = clean_e10()
    w1_agg = clean_w1()
    w2_agg = clean_w2()
    w3 = clean_w3()
    w7 = clean_w7()
    w8 = clean_w8()
    w12 = clean_w12()

    # --- Phase 2: Build output tables ---
    print("\n─── PHASE 2: BUILD OUTPUT TABLES ───")
    sites = build_unified_sites(e1, e3_agg, e4, e5, e7_agg, e10,
                                 w1_agg, w2_agg, w3, w7, w8)
    districts = build_district_waste(w1_agg, w2_agg, w3, w7, w8, w12)
    ts = build_time_series(e3_ts, e7_ts)

    # --- Phase 3: Save ---
    print("\n─── PHASE 3: SAVE PARQUET FILES ───")
    sites_path = os.path.join(OUT_DIR, "unified_sites.parquet")
    districts_path = os.path.join(OUT_DIR, "district_waste.parquet")
    ts_path = os.path.join(OUT_DIR, "time_series.parquet")

    sites.to_parquet(sites_path, index=False)
    print(f"  [SAVED] {sites_path} — {len(sites)} rows × {len(sites.columns)} cols")

    districts.to_parquet(districts_path, index=False)
    print(f"  [SAVED] {districts_path} — {len(districts)} rows × {len(districts.columns)} cols")

    ts.to_parquet(ts_path, index=False)
    print(f"  [SAVED] {ts_path} — {len(ts)} rows × {len(ts.columns)} cols")

    # --- Summary ---
    elapsed = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s total")
    print(f"  Mode: {'GPU' if GPU_MODE else 'CPU'}")
    print(f"  unified_sites.parquet    {len(sites):>6,} rows × {len(sites.columns)} cols")
    print(f"  district_waste.parquet   {len(districts):>6,} rows × {len(districts.columns)} cols")
    print(f"  time_series.parquet      {len(ts):>8,} rows × {len(ts.columns)} cols")
    print("=" * 60)


if __name__ == "__main__":
    main()
