"""
Step 2: Clean data, merge datasets, and engineer features for BESS site ranking.
Produces a unified site table with all features needed for scoring.
"""
import os
import numpy as np
import pandas as pd
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(series: pd.Series) -> pd.Series:
    """Convert to float, coercing errors to NaN."""
    return pd.to_numeric(series, errors="coerce")


def _kbtu_to_kwh(kbtu: pd.Series) -> pd.Series:
    """Convert kBTU to kWh (1 kBTU = 0.293071 kWh)."""
    return _safe_float(kbtu) * 0.293071


def _load_raw(name: str) -> pd.DataFrame:
    path = os.path.join(RAW_DATA_DIR, f"{name}.csv")
    return pd.read_csv(path, low_memory=False)


# ---------------------------------------------------------------------------
# Per-dataset cleaning
# ---------------------------------------------------------------------------

def clean_solar_readiness() -> pd.DataFrame:
    """Clean solar-readiness data: keep relevant columns, parse numerics."""
    df = _load_raw("solar_readiness")
    df["latitude"] = _safe_float(df.get("latitude"))
    df["longitude"] = _safe_float(df.get("longitude"))
    df["estimated_annual_production_kwh"] = _safe_float(
        df.get("estimated_annual_production", pd.Series(dtype=float))
    )
    df["estimated_annual_energy_savings"] = _safe_float(
        df.get("estimated_annual_energy", pd.Series(dtype=float))
    )
    df["solar_readiness_flag"] = df.get("solar_readiness_assessment", "").astype(str)
    df["roof_condition"] = df.get("roof_condition", "").astype(str)
    df["roof_age"] = df.get("roof_age", "").astype(str)
    df["env_justice_area"] = df.get("environmental_justice_area", "").astype(str)
    df["bbl"] = df.get("bbl", "").astype(str)

    keep = [
        "agency", "site", "address", "borough", "bbl",
        "latitude", "longitude", "estimated_annual_production_kwh",
        "estimated_annual_energy_savings", "solar_readiness_flag",
        "roof_condition", "roof_age", "env_justice_area",
    ]
    return df[[c for c in keep if c in df.columns]].copy()


def clean_ev_stations() -> pd.DataFrame:
    """Clean EV station data: parse charger counts and locations."""
    df = _load_raw("ev_stations")
    df["latitude"] = _safe_float(df.get("latitude"))
    df["longitude"] = _safe_float(df.get("longitude"))
    df["no_of_ports"] = _safe_float(df.get("no_of_ports")).fillna(0).astype(int)
    df["bbl"] = df.get("bbl", "").astype(str)
    return df[["station_name", "borough", "bbl", "latitude", "longitude",
               "no_of_ports", "type_of_charger"]].copy()


def clean_electric_consumption() -> pd.DataFrame:
    """Clean electric consumption data: monthly kWh and costs per site."""
    df = _load_raw("electric_consumption")
    df["consumption_kwh"] = _safe_float(df.get("consumption_kwh"))
    df["current_charges"] = _safe_float(df.get("current_charges"))
    df["consumption_kw"] = _safe_float(df.get("consumption_kw"))
    df["borough"] = df.get("borough", "").astype(str)

    # Aggregate to site level
    agg = df.groupby(["development_name", "borough"]).agg(
        avg_monthly_kwh=("consumption_kwh", "mean"),
        peak_kw=("consumption_kw", "max"),
        avg_monthly_cost=("current_charges", "mean"),
        total_records=("consumption_kwh", "count"),
    ).reset_index()

    return agg


def clean_ll84_monthly() -> pd.DataFrame:
    """Clean LL84 monthly data: aggregate electricity use per property."""
    df = _load_raw("ll84_monthly")
    df["electricity_kwh"] = _kbtu_to_kwh(df.get("electricity_use_kbtu"))
    df["natural_gas_kwh"] = _kbtu_to_kwh(df.get("natural_gas_use_kbtu"))

    agg = df.groupby(["property_id", "property_name"]).agg(
        avg_monthly_elec_kwh=("electricity_kwh", "mean"),
        avg_monthly_gas_kwh=("natural_gas_kwh", "mean"),
        months_reported=("electricity_kwh", "count"),
    ).reset_index()

    return agg


def clean_energy_savings() -> pd.DataFrame:
    """Clean energy cost savings program data."""
    df = _load_raw("energy_savings")
    df["total_savings"] = _safe_float(df.get("total_savings"))
    df["electric_savings"] = _safe_float(df.get("electric_savings"))
    df["latitude"] = _safe_float(df.get("latitude"))
    df["longitude"] = _safe_float(df.get("longitude"))
    df["bbl"] = df.get("bbl", "").astype(str)

    keep = ["address", "borough", "bbl", "latitude", "longitude",
            "total_savings", "electric_savings", "industry"]
    return df[[c for c in keep if c in df.columns]].copy()


def clean_dcas_energy() -> pd.DataFrame:
    """Clean DCAS managed building energy usage."""
    df = _load_raw("dcas_energy")
    # Column name is very long — find the energy usage column
    energy_col = [c for c in df.columns if "energy_usage" in c.lower() or "mmbtu" in c.lower()]
    df["energy_mmbtu"] = _safe_float(df[energy_col[0]]) if energy_col else 0
    df["energy_kwh"] = df["energy_mmbtu"] * 293.071  # MMBTU to kWh
    df["latitude"] = _safe_float(df.get("latitude"))
    df["longitude"] = _safe_float(df.get("longitude"))
    df["bbl"] = df.get("bbl", "").astype(str)

    return df[["building_name", "building_address", "borough", "bbl",
               "latitude", "longitude", "energy_kwh"]].copy()


# ---------------------------------------------------------------------------
# Merge & Feature Engineering
# ---------------------------------------------------------------------------

def build_site_table() -> pd.DataFrame:
    """
    Build the unified site table by merging solar readiness (primary)
    with EV stations, energy consumption, and savings data.
    """
    print("[FEATURES] Loading cleaned datasets...")

    solar = clean_solar_readiness()
    ev = clean_ev_stations()
    elec = clean_electric_consumption()
    savings = clean_energy_savings()
    dcas = clean_dcas_energy()

    # --- Start from solar readiness as the base (municipal buildings) ---
    sites = solar.copy()
    sites["site_id"] = range(len(sites))

    # --- Count nearby EV chargers (same BBL or within borough) ---
    ev_by_borough = ev.groupby("borough").agg(
        ev_ports_in_borough=("no_of_ports", "sum"),
        ev_stations_in_borough=("station_name", "count"),
    ).reset_index()
    sites = sites.merge(ev_by_borough, on="borough", how="left")
    sites["ev_ports_in_borough"] = sites["ev_ports_in_borough"].fillna(0)

    # --- Merge energy savings by BBL ---
    if "bbl" in savings.columns and "bbl" in sites.columns:
        savings_agg = savings.groupby("bbl").agg(
            area_total_savings=("total_savings", "sum"),
            area_electric_savings=("electric_savings", "sum"),
        ).reset_index()
        sites = sites.merge(savings_agg, on="bbl", how="left")

    # --- Engineer composite features ---
    sites["solar_score"] = (
        sites["estimated_annual_production_kwh"].fillna(0).rank(pct=True)
    )

    # Roof quality score: good=1.0, fair=0.6, poor=0.2
    roof_map = {"good": 1.0, "fair": 0.6, "poor": 0.2}
    sites["roof_score"] = (
        sites["roof_condition"].str.lower().str.strip().map(roof_map).fillna(0.4)
    )

    # Equity flag: environmental justice area
    sites["equity_flag"] = (
        sites["env_justice_area"].str.lower().str.contains("yes", na=False).astype(float)
    )

    # EV density score (percentile rank within dataset)
    sites["ev_density_score"] = sites["ev_ports_in_borough"].rank(pct=True)

    # Fill NaNs
    for col in ["area_total_savings", "area_electric_savings"]:
        if col in sites.columns:
            sites[col] = sites[col].fillna(0)

    # --- Save ---
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    out_path = os.path.join(PROCESSED_DATA_DIR, "unified_sites.csv")
    sites.to_csv(out_path, index=False)
    print(f"[SAVED] {out_path} — {len(sites)} sites, {len(sites.columns)} features")

    return sites


if __name__ == "__main__":
    df = build_site_table()
    print(f"\nSample:\n{df.head()}")
    print(f"\nColumns: {list(df.columns)}")
