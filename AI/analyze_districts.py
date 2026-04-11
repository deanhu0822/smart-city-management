"""
District-Level Analysis — Every district gets a full profile.

No ranking. No competition between districts. Just the facts:
- How much energy does this district use?
- How much waste does it produce?
- How much organic waste is going to landfill that could be energy?
- How close is the nearest AD facility?
- How many buildings are solar-ready?
- What are the complaints about?

Outputs one comprehensive JSON with all 59 districts.

Usage (on GB10):
    python AI/analyze_districts.py

    # With Qwen analysis (adds LLM narrative per district):
    QWEN_URL=http://localhost:3000/v1 python AI/analyze_districts.py
"""
import json
import os
import sys
import time
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.getenv("RAW_DIR", os.path.join(BASE_DIR, "data", "raw"))
OUT_DIR = os.getenv("OUT_DIR", os.path.join(BASE_DIR, "data", "gold"))
os.makedirs(OUT_DIR, exist_ok=True)

KBTU_TO_KWH = 0.293071
ORGANIC_FRACTION = 0.34  # from W12 waste characterization
KWH_PER_TON_AD = 500     # biogas yield from anaerobic digestion
NYC_AVG_APT_KWH_MO = 900 # average NYC apartment monthly kWh
CO2_PER_MWH = 0.288      # tons CO₂ per MWh displaced from grid

# Known AD facilities
AD_FACILITIES = [
    {"name": "Newtown Creek WRRF", "borough": "Brooklyn", "lat": 40.7388, "lon": -73.9525, "capacity_tons_day": 500},
    {"name": "Hunts Point WRRF", "borough": "Bronx", "lat": 40.8080, "lon": -73.8712, "capacity_tons_day": 250},
]

# ---------------------------------------------------------------------------
# File resolver
# ---------------------------------------------------------------------------
FILE_PATTERNS = {
    "E1": ["E1_energy_cost_savings.csv", "Value_of_Energy_Cost_Savings"],
    "E3": ["E3_electric_consumption.csv", "Electric_Consumption_And_Cost"],
    "E4": ["E4_ev_fleet_stations.csv", "NYC_EV_Fleet_Station_Network"],
    "E5": ["E5_solar_readiness.csv", "City_of_New_York_Municipal_Solar", "Municipal_Solar"],
    "E7": ["E7_ll84_monthly.csv", "Local_Law_84_Monthly_Data"],
    "E10": ["E10_ll84_benchmarking.csv", "NYC_Building_Energy_and_Water_Data"],
    "W1": ["W1_dsny_monthly_tonnage.csv", "DSNY_Monthly_Tonnage"],
    "W2": ["W2_311_dsny.csv", "311_Service_Requests"],
    "W3": ["W3_litter_baskets.csv", "DSNY_Litter_Basket_Inventory"],
    "W7": ["W7_food_scrap_dropoffs.csv", "Food_Scrap_Drop-Off", "Food_Scrap_Drop_Off"],
    "W8": ["W8_disposal_facilities.csv", "Location_of_Disposal_Facilities"],
    "W12": ["W12_waste_characterization.csv", "DSNY_Waste_Characterization"],
}

def find_raw_file(key):
    patterns = FILE_PATTERNS.get(key, [])
    files = os.listdir(RAW_DIR)
    for p in patterns:
        if p in files:
            return os.path.join(RAW_DIR, p)
    for p in patterns:
        for f in files:
            if p.lower() in f.lower() and f.endswith(".csv"):
                return os.path.join(RAW_DIR, f)
    return None

def sf(s):
    return pd.to_numeric(s, errors="coerce")

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))


# ═══════════════════════════════════════════════════════════════════════════
# BUILD DISTRICT PROFILES
# ═══════════════════════════════════════════════════════════════════════════

def build_all_districts():
    print("── LOADING & AGGREGATING ALL DATA ──\n")

    # ── E5: Building stock per district ──
    print("  [E5] Building inventory...")
    e5 = pd.read_csv(find_raw_file("E5"), low_memory=False)
    e5["community_board"] = sf(e5["Community Board"]).fillna(0).astype(int)
    e5["_boro_code"] = e5["community_board"] // 100
    e5["_cd"] = e5["community_board"] % 100
    boro_map = {1: "Manhattan", 2: "Bronx", 3: "Brooklyn", 4: "Queens", 5: "Staten Island"}
    e5["borough"] = e5["_boro_code"].map(boro_map)
    e5["solar_kwh"] = sf(e5["Estimated Annual Production"].astype(str).str.replace(",", "")).fillna(0)
    e5["is_ej"] = (e5["Environmental Justice Area"].astype(str).str.lower() == "yes").astype(int)
    e5["roof_good"] = (e5["Roof Condition"].astype(str).str.lower().str.strip() == "good").astype(int)
    e5["has_solar"] = (e5["solar_kwh"] > 0).astype(int)
    e5["sqft"] = sf(e5["Total Gross Square Footage"].astype(str).str.replace(",", "").str.replace("GSF", "")).fillna(0)
    e5["lat"] = sf(e5["Latitude"])
    e5["lon"] = sf(e5["Longitude"])

    # We'll build buildings_by_district later after merging energy data
    # For now, store the full E5 dataframe
    e5_full = e5.copy()

    e5_agg = e5.groupby(["borough", "_cd"]).agg(
        num_buildings=("Site", "count"),
        num_ej=("is_ej", "sum"),
        pct_ej=("is_ej", "mean"),
        total_solar_kwh=("solar_kwh", "sum"),
        avg_solar_kwh=("solar_kwh", "mean"),
        num_solar_ready=("has_solar", "sum"),
        pct_roof_good=("roof_good", "mean"),
        total_sqft=("sqft", "sum"),
        centroid_lat=("lat", "mean"),
        centroid_lon=("lon", "mean"),
    ).reset_index().rename(columns={"_cd": "cd"})
    print(f"    → {len(e5_agg)} districts, {len(e5)} buildings")

    # ── E7: Monthly energy per property (aggregate to BBL) ──
    print("  [E7] Monthly energy consumption (2.2M rows)...")
    e7 = pd.read_csv(find_raw_file("E7"), low_memory=False)
    elec_col = [c for c in e7.columns if "Electricity" in c and "kBtu" in c]
    gas_col = [c for c in e7.columns if "Natural Gas" in c and "kBtu" in c]
    e7["elec_kwh"] = sf(e7[elec_col[0]]) * KBTU_TO_KWH if elec_col else 0
    e7["gas_kwh"] = sf(e7[gas_col[0]]) * KBTU_TO_KWH if gas_col else 0
    e7["total_kwh"] = e7["elec_kwh"].fillna(0) + e7["gas_kwh"].fillna(0)
    e7 = e7[e7["total_kwh"] > 0]
    e7["Property Id"] = e7["Property Id"].astype(str)

    e7_agg = e7.groupby("Property Id").agg(
        e7_avg_elec_kwh=("elec_kwh", "mean"),
        e7_avg_gas_kwh=("gas_kwh", "mean"),
        e7_avg_total_kwh=("total_kwh", "mean"),
        e7_peak_elec_kwh=("elec_kwh", "max"),
        e7_months=("elec_kwh", "count"),
    ).reset_index()

    # Seasonality
    e7_std = e7.groupby("Property Id")["elec_kwh"].std().reset_index(name="e7_std")
    e7_mean = e7.groupby("Property Id")["elec_kwh"].mean().reset_index(name="e7_mean")
    e7_seas = e7_std.merge(e7_mean, on="Property Id")
    e7_seas["seasonality"] = (e7_seas["e7_std"] / e7_seas["e7_mean"].replace(0, np.nan)).fillna(0)
    e7_agg = e7_agg.merge(e7_seas[["Property Id", "seasonality"]], on="Property Id", how="left")
    print(f"    → {len(e7_agg)} properties aggregated")

    # ── E10: Benchmarking (bridge: property_id → BBL) ──
    print("  [E10] Benchmarking + BBL bridge...")
    e10_usecols = ["Property ID", "NYC Borough, Block and Lot (BBL)",
                   "ENERGY STAR Score", "Site EUI (kBtu/ft²)",
                   "Total (Location-Based) GHG Emissions (Metric Tons CO2e)",
                   "Year Built", "Primary Property Type - Self Selected"]
    e10 = pd.read_csv(find_raw_file("E10"), usecols=e10_usecols, low_memory=False)
    e10.columns = ["prop_id", "bbl", "energy_star", "site_eui", "ghg", "year_built", "prop_type"]
    e10["bbl"] = e10["bbl"].astype(str).str.strip().str.split(".").str[0].str.zfill(10)
    e10["prop_id"] = e10["prop_id"].astype(str)
    e10["energy_star"] = sf(e10["energy_star"]).fillna(-1).astype(int)
    e10["site_eui"] = sf(e10["site_eui"])
    e10["ghg"] = sf(e10["ghg"])
    e10["year_built"] = sf(e10["year_built"]).fillna(0).astype(int)
    e10 = e10.sort_values("energy_star", ascending=False).drop_duplicates("bbl", keep="first")
    print(f"    → {len(e10)} properties (deduplicated by BBL)")

    # Bridge E7 → BBL via E10
    e10_bridge = e10[["prop_id", "bbl"]].drop_duplicates()
    e7_with_bbl = e7_agg.merge(e10_bridge, left_on="Property Id", right_on="prop_id", how="inner")
    e7_by_bbl = e7_with_bbl.groupby("bbl").agg(
        avg_elec_kwh_mo=("e7_avg_elec_kwh", "mean"),
        avg_gas_kwh_mo=("e7_avg_gas_kwh", "mean"),
        avg_total_kwh_mo=("e7_avg_total_kwh", "mean"),
        peak_elec_kwh_mo=("e7_peak_elec_kwh", "max"),
        seasonality=("seasonality", "mean"),
    ).reset_index()
    print(f"    → {len(e7_by_bbl)} BBLs with energy data")

    # ── Merge energy data onto E5 buildings ──
    print("  [MERGE] Building-level energy profiles...")
    e5_full["bbl"] = e5_full["BBL"].astype(str).str.strip().str.split(".").str[0].str.zfill(10)

    # E10 benchmarking
    e5_full = e5_full.merge(
        e10[["bbl", "energy_star", "site_eui", "ghg", "year_built", "prop_type"]],
        on="bbl", how="left"
    )
    # E7 consumption
    e5_full = e5_full.merge(e7_by_bbl, on="bbl", how="left")

    # BESS sizing per building
    e5_full["avg_total_kwh_mo"] = e5_full["avg_total_kwh_mo"].fillna(0)
    e5_full["peak_elec_kwh_mo"] = e5_full["peak_elec_kwh_mo"].fillna(0)
    e5_full["solar_kwh"] = e5_full["solar_kwh"].fillna(0)

    # Estimate peak kW from monthly kWh (monthly kWh / 730 hours ≈ avg kW, peak ≈ 1.5x avg)
    e5_full["est_peak_kw"] = (e5_full["peak_elec_kwh_mo"] / 730 * 1.5).clip(lower=0)
    # Annual energy cost estimate
    e5_full["est_annual_cost_usd"] = e5_full["avg_elec_kwh_mo"].fillna(0) * 0.22 * 12

    # BESS recommendation per building
    def bess_size(row):
        solar = row["solar_kwh"]
        peak = row["est_peak_kw"]
        if solar > 200000 or peak > 500:
            return 1000, 250
        elif solar > 100000 or peak > 200:
            return 750, 188
        elif solar > 50000 or peak > 100:
            return 500, 125
        elif solar > 10000 or peak > 50:
            return 250, 63
        else:
            return 100, 25

    bess = e5_full.apply(bess_size, axis=1, result_type="expand")
    e5_full["bess_kwh"] = bess[0].astype(int)
    e5_full["bess_kw"] = bess[1].astype(int)
    # Estimated annual savings from BESS (peak shaving)
    e5_full["bess_savings_usd"] = (e5_full["bess_kw"] * 0.14 * 14 * 365).astype(int)  # 14 peak hours/day, $0.14/kWh differential

    # Build per-district building lists
    buildings_by_district = {}
    for _, row in e5_full.iterrows():
        key = (row["borough"], row["_cd"])
        if key not in buildings_by_district:
            buildings_by_district[key] = []
        buildings_by_district[key].append({
            "site": str(row.get("Site", "")),
            "address": str(row.get("Address", "")),
            "agency": str(row.get("Agency", "")),
            "ej": bool(row["is_ej"]),
            "roof": str(row.get("Roof Condition", "Unknown")),
            "sqft": float(row["sqft"]),
            "energy": {
                "solar_production_kwh_yr": float(row["solar_kwh"]),
                "avg_elec_kwh_mo": round(float(row.get("avg_elec_kwh_mo", 0) or 0), 0),
                "avg_gas_kwh_mo": round(float(row.get("avg_gas_kwh_mo", 0) or 0), 0),
                "avg_total_kwh_mo": round(float(row.get("avg_total_kwh_mo", 0) or 0), 0),
                "peak_elec_kwh_mo": round(float(row.get("peak_elec_kwh_mo", 0) or 0), 0),
                "est_peak_kw": round(float(row.get("est_peak_kw", 0) or 0), 1),
                "est_annual_cost_usd": round(float(row.get("est_annual_cost_usd", 0) or 0), 0),
                "seasonality": round(float(row.get("seasonality", 0) or 0), 2),
                "energy_star_score": int(sf(pd.Series([row.get("energy_star", -1)])).fillna(-1).iloc[0]),
                "site_eui": round(float(sf(pd.Series([row.get("site_eui", 0)])).fillna(0).iloc[0]), 1),
                "ghg_tons_co2e_yr": round(float(sf(pd.Series([row.get("ghg", 0)])).fillna(0).iloc[0]), 1),
                "year_built": int(sf(pd.Series([row.get("year_built", 0)])).fillna(0).iloc[0]),
                "property_type": str(row.get("prop_type", "Unknown") or "Unknown"),
            },
            "bess_recommendation": {
                "capacity_kwh": int(row["bess_kwh"]),
                "power_kw": int(row["bess_kw"]),
                "est_annual_savings_usd": int(row["bess_savings_usd"]),
            },
        })

    matched = e5_full["avg_total_kwh_mo"].gt(0).sum()
    print(f"    → {matched} / {len(e5_full)} buildings have energy consumption data")
    print(f"    → {e5_full['energy_star'].gt(0).sum()} buildings have ENERGY STAR scores")

    # ── W1: Waste tonnage ──
    print("  [W1] Waste tonnage...")
    w1 = pd.read_csv(find_raw_file("W1"), low_memory=False)
    for c in ["REFUSETONSCOLLECTED", "PAPERTONSCOLLECTED", "MGPTONSCOLLECTED",
              "RESORGANICSTONS", "SCHOOLORGANICTONS", "LEAVESORGANICTONS"]:
        if c in w1.columns:
            w1[c] = sf(w1[c]).fillna(0)
    w1["organics_collected"] = w1.get("RESORGANICSTONS", 0) + w1.get("SCHOOLORGANICTONS", 0) + w1.get("LEAVESORGANICTONS", 0)
    w1["recycling"] = w1["PAPERTONSCOLLECTED"] + w1["MGPTONSCOLLECTED"]
    w1["total"] = w1["REFUSETONSCOLLECTED"] + w1["recycling"] + w1["organics_collected"]
    w1["diversion"] = (w1["recycling"] + w1["organics_collected"]) / w1["total"].replace(0, np.nan)
    w1["cd"] = sf(w1["COMMUNITYDISTRICT"]).fillna(0).astype(int)

    w1_agg = w1.groupby(["BOROUGH", "cd"]).agg(
        refuse_tons_mo=("REFUSETONSCOLLECTED", "mean"),
        paper_tons_mo=("PAPERTONSCOLLECTED", "mean"),
        mgp_tons_mo=("MGPTONSCOLLECTED", "mean"),
        organics_collected_mo=("organics_collected", "mean"),
        recycling_tons_mo=("recycling", "mean"),
        total_tons_mo=("total", "mean"),
        diversion_rate=("diversion", "mean"),
    ).reset_index().rename(columns={"BOROUGH": "borough"})
    print(f"    → {len(w1_agg)} districts")

    # ── W2: 311 complaints ──
    print("  [W2] 311 complaints...")
    w2 = pd.read_csv(find_raw_file("W2"), low_memory=False)
    w2.columns = w2.columns.str.strip().str.lower()
    cb = w2.get("community_board", w2.get("community board", pd.Series("0")))
    w2["cd"] = sf(cb.astype(str).str.extract(r"(\d+)", expand=False)).fillna(0).astype(int)
    w2["borough"] = w2.get("borough", "").astype(str).str.strip().str.title()
    ct = w2.get("complaint_type", w2.get("complaint type", pd.Series(""))).astype(str).str.lower()
    w2["is_missed"] = ct.str.contains("missed", na=False).astype(int)
    w2["is_overflow"] = (ct.str.contains("overflow", na=False) | ct.str.contains("litter basket", na=False)).astype(int)
    w2["is_dumping"] = ct.str.contains("dump", na=False).astype(int)
    w2["is_dirty"] = ct.str.contains("dirty", na=False).astype(int)

    w2_agg = w2.groupby(["borough", "cd"]).agg(
        total_complaints=("cd", "count"),
        missed=("is_missed", "sum"),
        overflow=("is_overflow", "sum"),
        dumping=("is_dumping", "sum"),
        dirty=("is_dirty", "sum"),
    ).reset_index()
    print(f"    → {len(w2_agg)} districts")

    # ── E4: EV stations (spatial count per district) ──
    print("  [E4] EV stations...")
    e4 = pd.read_csv(find_raw_file("E4"), low_memory=False)
    e4.columns = e4.columns.str.strip().str.upper()
    e4["lat"] = sf(e4["LATITUDE"])
    e4["lon"] = sf(e4["LONGITUDE"])
    e4["ports"] = sf(e4.get("NO. OF PLUGS", pd.Series(1))).fillna(1).astype(int)
    e4 = e4.dropna(subset=["lat", "lon"])

    # ── W7: Composting sites ──
    print("  [W7] Composting sites...")
    w7 = pd.read_csv(find_raw_file("W7"), low_memory=False)
    w7["lat"] = sf(w7["Latitude"])
    w7["lon"] = sf(w7["Longitude"])
    w7 = w7.dropna(subset=["lat", "lon"])

    # ── W8: Transfer stations ──
    print("  [W8] Transfer stations...")
    w8 = pd.read_csv(find_raw_file("W8"), low_memory=False)
    w8["lat"] = sf(w8["Latitude"])
    w8["lon"] = sf(w8["Longitude"])
    w8 = w8.dropna(subset=["lat", "lon"])
    w8_nyc = w8[(w8["lat"] > 40.4) & (w8["lat"] < 41.0) & (w8["lon"] > -74.3) & (w8["lon"] < -73.7)]

    ad_lats = np.array([f["lat"] for f in AD_FACILITIES])
    ad_lons = np.array([f["lon"] for f in AD_FACILITIES])

    # ── Spatial features per district ──
    print("  [SPATIAL] Computing proximity for each district...")
    spatial = []
    for _, d in e5_agg.iterrows():
        clat, clon = d["centroid_lat"], d["centroid_lon"]
        if pd.isna(clat) or pd.isna(clon):
            spatial.append({"borough": d["borough"], "cd": d["cd"],
                            "ev_stations_2km": 0, "ev_ports_2km": 0,
                            "compost_sites_2km": 0,
                            "nearest_transfer_km": 999, "nearest_transfer_name": "Unknown",
                            "nearest_ad_km": 999, "nearest_ad_name": "Unknown"})
            continue

        # EV
        ev_d = haversine_km(clat, clon, e4["lat"].values, e4["lon"].values)
        ev_mask = ev_d <= 2.0
        # Compost
        comp_d = haversine_km(clat, clon, w7["lat"].values, w7["lon"].values)
        # Transfer
        ts_d = haversine_km(clat, clon, w8_nyc["lat"].values, w8_nyc["lon"].values)
        # AD
        ad_d = haversine_km(clat, clon, ad_lats, ad_lons)

        spatial.append({
            "borough": d["borough"], "cd": d["cd"],
            "ev_stations_2km": int(ev_mask.sum()),
            "ev_ports_2km": int(e4.loc[ev_mask, "ports"].sum()) if ev_mask.any() else 0,
            "compost_sites_2km": int((comp_d <= 2.0).sum()),
            "nearest_transfer_km": round(float(ts_d.min()), 1) if len(ts_d) > 0 else 999,
            "nearest_transfer_name": str(w8_nyc.iloc[ts_d.argmin()]["Name"]) if len(ts_d) > 0 else "Unknown",
            "nearest_ad_km": round(float(ad_d.min()), 1),
            "nearest_ad_name": AD_FACILITIES[int(ad_d.argmin())]["name"],
        })
    spatial_df = pd.DataFrame(spatial)
    print(f"    → done")

    # ── MERGE ──
    print("\n  [MERGE] Building district profiles...")
    districts = e5_agg.copy()
    districts = districts.merge(w1_agg, on=["borough", "cd"], how="left")
    districts = districts.merge(w2_agg, on=["borough", "cd"], how="left")
    districts = districts.merge(spatial_df, on=["borough", "cd"], how="left")

    # Fill NaN
    num_cols = districts.select_dtypes(include=[np.number]).columns
    districts[num_cols] = districts[num_cols].fillna(0)

    # ── Derived: waste-to-energy ──
    districts["organics_in_refuse_mo"] = districts["refuse_tons_mo"] * ORGANIC_FRACTION
    districts["total_organic_potential_mo"] = districts["organics_collected_mo"] + districts["organics_in_refuse_mo"]
    districts["energy_potential_mwh_mo"] = districts["organics_in_refuse_mo"] * KWH_PER_TON_AD / 1000
    districts["energy_potential_mwh_yr"] = districts["energy_potential_mwh_mo"] * 12
    districts["homes_powered_mo"] = districts["organics_in_refuse_mo"] * KWH_PER_TON_AD / NYC_AVG_APT_KWH_MO
    districts["co2_avoided_tons_mo"] = districts["energy_potential_mwh_mo"] * CO2_PER_MWH
    districts["diversion_gap_pct"] = (0.30 - districts["diversion_rate"]) * 100

    # District code
    bp = {"Manhattan": "MN", "Bronx": "BX", "Brooklyn": "BK", "Queens": "QN", "Staten Island": "SI"}
    districts["district_code"] = districts["borough"].map(bp).fillna("XX") + districts["cd"].astype(str).str.zfill(2)

    print(f"    → {len(districts)} districts profiled\n")

    return districts, buildings_by_district


# ═══════════════════════════════════════════════════════════════════════════
# OPTIONAL: Qwen analysis per district
# ═══════════════════════════════════════════════════════════════════════════

def qwen_analyze(districts):
    """If Qwen is available, generate a narrative for each district."""
    qwen_url = os.getenv("QWEN_URL", "")
    if not qwen_url:
        print("  [SKIP] No QWEN_URL set — skipping LLM narratives")
        return {}

    from openai import OpenAI
    client = OpenAI(base_url=qwen_url, api_key="not-needed")

    print(f"  [QWEN] Generating narratives via {qwen_url}...")

    system = """You are a NYC urban sustainability analyst. Given a community district profile with energy, waste, and infrastructure data, write a 3-4 sentence analysis covering:
1. The district's key challenge (energy, waste, or both)
2. The biggest opportunity (what specific action would have most impact)
3. The waste-to-energy potential (how much organic waste could become energy)
4. Any equity considerations (Environmental Justice areas)

Be specific with numbers from the data. No generic advice."""

    narratives = {}
    total = len(districts)

    for i, (_, d) in enumerate(districts.iterrows()):
        profile = {k: (round(v, 1) if isinstance(v, float) else v)
                    for k, v in d.to_dict().items()
                    if not isinstance(v, float) or not np.isnan(v)}

        try:
            resp = client.chat.completions.create(
                model=os.getenv("QWEN_MODEL", "qwen3-80b"),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Analyze district {d['district_code']}:\n{json.dumps(profile, default=str)}"},
                ],
                temperature=0.2,
                max_tokens=300,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            )
            text = resp.choices[0].message.content.strip()
            if "</think>" in text:
                text = text.split("</think>")[-1].strip()
            narratives[d["district_code"]] = text
            print(f"    [{i+1}/{total}] {d['district_code']} ✓")
        except Exception as e:
            print(f"    [{i+1}/{total}] {d['district_code']} ✗ ({e})")
            narratives[d["district_code"]] = ""

    return narratives


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════════════════

def save_output(districts, buildings_by_district, narratives):
    """Save comprehensive district analysis as JSON + parquet."""

    # Build one rich object per district
    output = []
    for _, d in districts.iterrows():
        key = (d["borough"], d["cd"])
        bldgs = buildings_by_district.get(key, [])

        # Sort buildings by solar potential
        bldgs_sorted = sorted(bldgs, key=lambda x: x["energy"]["solar_production_kwh_yr"], reverse=True)

        district = {
            # Identity
            "district_code": d["district_code"],
            "borough": d["borough"],
            "community_district": int(d["cd"]),
            "centroid_lat": round(d["centroid_lat"], 6),
            "centroid_lon": round(d["centroid_lon"], 6),

            # Building stock summary (district-level aggregate)
            "buildings_summary": {
                "total": int(d["num_buildings"]),
                "environmental_justice": int(d["num_ej"]),
                "pct_ej": round(d["pct_ej"] * 100, 1),
                "solar_ready": int(d["num_solar_ready"]),
                "total_solar_potential_kwh_yr": round(d["total_solar_kwh"], 0),
                "avg_solar_per_building_kwh_yr": round(d["avg_solar_kwh"], 0),
                "pct_roof_good": round(d["pct_roof_good"] * 100, 1),
                "total_sqft": round(d["total_sqft"], 0),
                "with_energy_data": sum(1 for b in bldgs if b["energy"]["avg_total_kwh_mo"] > 0),
                "with_energy_star": sum(1 for b in bldgs if b["energy"]["energy_star_score"] > 0),
                "total_bess_capacity_kwh": sum(b["bess_recommendation"]["capacity_kwh"] for b in bldgs),
                "total_bess_savings_usd_yr": sum(b["bess_recommendation"]["est_annual_savings_usd"] for b in bldgs),
            },

            # Every building in this district with its own energy profile
            "buildings": bldgs_sorted,

            # Waste
            "waste": {
                "refuse_tons_per_month": round(d["refuse_tons_mo"], 0),
                "paper_recycling_tons_per_month": round(d.get("paper_tons_mo", 0), 0),
                "mgp_recycling_tons_per_month": round(d.get("mgp_tons_mo", 0), 0),
                "organics_collected_tons_per_month": round(d["organics_collected_mo"], 0),
                "total_tons_per_month": round(d["total_tons_mo"], 0),
                "diversion_rate_pct": round(d["diversion_rate"] * 100, 1),
                "diversion_gap_pct": round(d["diversion_gap_pct"], 1),
            },

            # Waste-to-energy
            "waste_to_energy": {
                "organics_in_refuse_tons_per_month": round(d["organics_in_refuse_mo"], 0),
                "if_diverted_to_AD": {
                    "energy_mwh_per_month": round(d["energy_potential_mwh_mo"], 0),
                    "energy_mwh_per_year": round(d["energy_potential_mwh_yr"], 0),
                    "apartments_powered_per_month": round(d["homes_powered_mo"], 0),
                    "co2_avoided_tons_per_month": round(d["co2_avoided_tons_mo"], 0),
                    "co2_avoided_tons_per_year": round(d["co2_avoided_tons_mo"] * 12, 0),
                },
                "nearest_ad_facility": d["nearest_ad_name"],
                "nearest_ad_distance_km": d["nearest_ad_km"],
            },

            # 311 complaints
            "complaints": {
                "total": int(d["total_complaints"]),
                "missed_collection": int(d["missed"]),
                "overflow": int(d["overflow"]),
                "illegal_dumping": int(d["dumping"]),
                "dirty_conditions": int(d["dirty"]),
            },

            # Infrastructure
            "infrastructure": {
                "ev_stations_within_2km": int(d["ev_stations_2km"]),
                "ev_ports_within_2km": int(d["ev_ports_2km"]),
                "composting_sites_within_2km": int(d["compost_sites_2km"]),
                "nearest_transfer_station": d["nearest_transfer_name"],
                "nearest_transfer_distance_km": d["nearest_transfer_km"],
            },

            # Qwen narrative (if available)
            "ai_analysis": narratives.get(d["district_code"], ""),
        }

        output.append(district)

    # Save JSON
    json_path = os.path.join(OUT_DIR, "district_analysis.json")
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"[SAVED] {json_path} — {len(output)} districts")

    # Save parquet (flat table for dashboard)
    districts.to_parquet(os.path.join(OUT_DIR, "district_profiles.parquet"), index=False)
    print(f"[SAVED] district_profiles.parquet")

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"  DISTRICT ANALYSIS — ALL {len(output)} DISTRICTS")
    print(f"{'=' * 70}")

    for d in output:
        w2e = d["waste_to_energy"]
        bldg = d["buildings"]
        waste = d["waste"]
        bldg_sum = d["buildings_summary"]
        print(f"\n  ┌─ {d['district_code']} ({d['borough']} District {d['community_district']}) ──────────")
        print(f"  │ DISTRICT LEVEL (energy + waste + BESS):")
        print(f"  │   Buildings:  {bldg_sum['total']} total, {bldg_sum['environmental_justice']} EJ ({bldg_sum['pct_ej']}%), {bldg_sum['solar_ready']} solar-ready")
        print(f"  │   Waste:      {waste['refuse_tons_per_month']:,.0f} t refuse/mo, {waste['diversion_rate_pct']:.1f}% diversion (gap: {waste['diversion_gap_pct']:.1f}%)")
        print(f"  │   Organics:   {w2e['organics_in_refuse_tons_per_month']:,.0f} t/mo in refuse → could be energy")
        if w2e["organics_in_refuse_tons_per_month"] > 0:
            ad = w2e["if_diverted_to_AD"]
            print(f"  │   If → AD:    {ad['energy_mwh_per_month']:,.0f} MWh/mo, powers {ad['apartments_powered_per_month']:,.0f} apts, avoids {ad['co2_avoided_tons_per_month']:,.0f}t CO₂/mo")
            print(f"  │   Nearest AD: {w2e['nearest_ad_facility']} ({w2e['nearest_ad_distance_km']} km)")
        print(f"  │   BESS total: {bldg_sum['total_bess_capacity_kwh']:,} kWh across district → ${bldg_sum['total_bess_savings_usd_yr']:,}/yr")
        print(f"  │   EV: {d['infrastructure']['ev_ports_within_2km']} ports | Compost: {d['infrastructure']['composting_sites_within_2km']} sites")
        # Top 3 buildings by energy
        top_bldgs = [b for b in d["buildings"] if b["energy"]["avg_total_kwh_mo"] > 0][:3]
        if top_bldgs:
            print(f"  │ BUILDING LEVEL (energy only) — top {len(top_bldgs)} consumers:")
            for b in top_bldgs:
                e = b["energy"]
                bess = b["bess_recommendation"]
                print(f"  │   • {b['site'][:35]:35s}  {e['avg_total_kwh_mo']:>10,.0f} kWh/mo  "
                      f"peak:{e['est_peak_kw']:>6.0f}kW  solar:{e['solar_production_kwh_yr']:>8,.0f}  "
                      f"BESS:{bess['capacity_kwh']}kWh→${bess['est_annual_savings_usd']:,}/yr")
        if d["ai_analysis"]:
            print(f"  │ AI: {d['ai_analysis'][:100]}...")
        print(f"  └{'─' * 70}")

    # Citywide
    total_organic = sum(d["waste_to_energy"]["organics_in_refuse_tons_per_month"] for d in output)
    total_mwh_yr = sum(d["waste_to_energy"]["if_diverted_to_AD"]["energy_mwh_per_year"] for d in output)
    total_homes = sum(d["waste_to_energy"]["if_diverted_to_AD"]["apartments_powered_per_month"] for d in output)
    total_co2_yr = sum(d["waste_to_energy"]["if_diverted_to_AD"]["co2_avoided_tons_per_year"] for d in output)

    print(f"\n{'=' * 70}")
    print(f"  CITYWIDE TOTALS")
    print(f"  Organic waste in refuse:    {total_organic:>10,.0f} tons/month")
    print(f"  Energy if diverted to AD:   {total_mwh_yr:>10,.0f} MWh/year")
    print(f"  Apartments powerable:       {total_homes:>10,.0f} per month")
    print(f"  CO₂ avoidable:              {total_co2_yr:>10,.0f} tons/year")
    print(f"{'=' * 70}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  NYC DISTRICT ANALYSIS — Every District, Full Profile")
    print(f"  Raw data: {RAW_DIR}")
    print("=" * 70)

    t0 = time.time()

    districts, buildings_by_district = build_all_districts()
    narratives = qwen_analyze(districts)
    save_output(districts, buildings_by_district, narratives)

    print(f"\n  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
