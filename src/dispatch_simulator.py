"""
Step 3b: Deterministic dispatch simulator.
Complements the LLM-based dispatch recommendations with a physics-based model
that calculates actual energy flows, savings, and CO₂ offsets.
"""
import json
import os
import numpy as np
import pandas as pd
from config import PROCESSED_DATA_DIR


# ---------------------------------------------------------------------------
# NYC Energy Constants
# ---------------------------------------------------------------------------

# Time-of-use rates ($/kWh) — ConEd commercial approximation
TOU_RATES = {
    "peak": 0.22,       # 8AM-10PM weekdays
    "off_peak": 0.08,   # 10PM-8AM + weekends
}

# NYC grid emission factor (tons CO₂ per MWh) — EPA eGRID NPCC/NYC
GRID_EMISSION_FACTOR = 0.000288  # tons CO₂ per kWh

# Typical solar generation curve (normalized, peak = 1.0)
SOLAR_CURVE = np.array([
    0.0, 0.0, 0.0, 0.0, 0.0, 0.01,  # 0-5
    0.05, 0.15, 0.35, 0.60, 0.80, 0.95,  # 6-11
    1.0, 0.95, 0.85, 0.70, 0.50, 0.25,  # 12-17
    0.08, 0.0, 0.0, 0.0, 0.0, 0.0,  # 18-23
])

# Typical commercial building demand curve (normalized, peak = 1.0)
BUILDING_DEMAND_CURVE = np.array([
    0.30, 0.28, 0.25, 0.25, 0.25, 0.30,  # 0-5
    0.45, 0.65, 0.85, 0.95, 1.00, 0.98,  # 6-11
    0.95, 0.97, 1.00, 0.95, 0.85, 0.70,  # 12-17
    0.55, 0.45, 0.40, 0.38, 0.35, 0.32,  # 18-23
])


class BESSSimulator:
    """Simulates a single BESS unit at a given site over 24 hours."""

    def __init__(
        self,
        capacity_kwh: float = 500,
        max_power_kw: float = 125,
        efficiency: float = 0.90,
        initial_soc: float = 0.2,
    ):
        self.capacity_kwh = capacity_kwh
        self.max_power_kw = max_power_kw
        self.efficiency = efficiency  # round-trip
        self.initial_soc = initial_soc

    def simulate_day(
        self,
        site_peak_kw: float = 200,
        solar_capacity_kw: float = 50,
        has_ev_chargers: bool = False,
    ) -> dict:
        """
        Simulate one representative day.
        Returns hourly schedule + summary metrics.
        """
        soc = self.initial_soc * self.capacity_kwh  # current energy in battery (kWh)
        schedule = []
        total_savings = 0
        peak_before = 0
        peak_after = 0
        total_co2_offset = 0

        for hour in range(24):
            # Determine demand and generation
            demand_kw = site_peak_kw * BUILDING_DEMAND_CURVE[hour]
            solar_kw = solar_capacity_kw * SOLAR_CURVE[hour]
            ev_extra_kw = 30 * (1 if has_ev_chargers and hour in [7, 8, 17, 18, 19] else 0)
            net_demand_kw = demand_kw + ev_extra_kw - solar_kw

            # Determine rate
            is_peak = 8 <= hour < 22
            rate = TOU_RATES["peak"] if is_peak else TOU_RATES["off_peak"]

            # Decide action: charge during off-peak/solar-surplus, discharge during peak
            action = "idle"
            power_kw = 0

            if not is_peak and soc < self.capacity_kwh * 0.95:
                # Off-peak: charge
                available = min(self.max_power_kw, (self.capacity_kwh - soc) / self.efficiency)
                power_kw = available
                soc += power_kw * self.efficiency
                action = "charge"

            elif is_peak and soc > self.capacity_kwh * 0.1 and net_demand_kw > site_peak_kw * 0.6:
                # Peak + high demand: discharge
                available = min(self.max_power_kw, soc, net_demand_kw * 0.4)
                power_kw = available
                soc -= power_kw
                action = "discharge"
                # Savings: displaced peak-rate energy
                savings = power_kw * (rate - TOU_RATES["off_peak"])
                total_savings += savings
                # CO₂: displaced grid power
                total_co2_offset += power_kw * GRID_EMISSION_FACTOR

            grid_demand_before = net_demand_kw
            grid_demand_after = net_demand_kw - (power_kw if action == "discharge" else 0)
            peak_before = max(peak_before, grid_demand_before)
            peak_after = max(peak_after, grid_demand_after)

            schedule.append({
                "hour": hour,
                "action": action,
                "power_kw": round(power_kw, 1),
                "soc_kwh": round(soc, 1),
                "soc_pct": round(soc / self.capacity_kwh * 100, 1),
                "demand_kw": round(demand_kw, 1),
                "solar_kw": round(solar_kw, 1),
                "net_demand_kw": round(net_demand_kw, 1),
                "grid_draw_kw": round(max(0, grid_demand_after), 1),
                "rate_per_kwh": rate,
            })

        # Annualize (assume ~250 weekdays + ~115 weekend days with different patterns)
        annual_factor = 365
        summary = {
            "daily_savings_usd": round(total_savings, 2),
            "annual_savings_usd": round(total_savings * annual_factor, 0),
            "peak_reduction_kw": round(peak_before - peak_after, 1),
            "peak_reduction_pct": round((peak_before - peak_after) / max(peak_before, 1) * 100, 1),
            "annual_co2_offset_tons": round(total_co2_offset * annual_factor, 2),
            "battery_utilization_pct": round(
                sum(1 for s in schedule if s["action"] != "idle") / 24 * 100, 1
            ),
        }

        return {"schedule": schedule, "summary": summary}


def simulate_top_sites(n: int = 10):
    """Run dispatch simulation for top N ranked sites."""
    ranked_path = os.path.join(PROCESSED_DATA_DIR, "ranked_sites.csv")
    if not os.path.exists(ranked_path):
        print("[ERROR] Run llm_ranker.py first to generate ranked_sites.csv")
        return

    ranked = pd.read_csv(ranked_path).head(n)
    sim = BESSSimulator(capacity_kwh=500, max_power_kw=125)

    results = []
    for _, row in ranked.iterrows():
        solar_kw = float(row.get("estimated_annual_production_kwh", 0) or 0) / 1500  # rough conversion
        has_ev = float(row.get("ev_ports_in_borough", 0) or 0) > 100

        result = sim.simulate_day(
            site_peak_kw=200,  # default estimate for municipal building
            solar_capacity_kw=min(solar_kw, 100),
            has_ev_chargers=has_ev,
        )
        result["site_id"] = int(row.get("site_id", 0))
        result["address"] = row.get("address", "N/A")
        result["borough"] = row.get("borough", "N/A")
        result["bess_score"] = int(row.get("bess_score", 0))
        results.append(result)

        print(f"  Site {row.get('address', 'N/A')[:40]:40s} | "
              f"Savings: ${result['summary']['annual_savings_usd']:,.0f}/yr | "
              f"Peak reduction: {result['summary']['peak_reduction_kw']} kW | "
              f"CO₂: {result['summary']['annual_co2_offset_tons']} tons/yr")

    # Save
    out_path = os.path.join(PROCESSED_DATA_DIR, "dispatch_simulations.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n[SAVED] {out_path}")

    return results


if __name__ == "__main__":
    print("=" * 60)
    print("BESS DISPATCH SIMULATION — TOP SITES")
    print("=" * 60)
    simulate_top_sites()
