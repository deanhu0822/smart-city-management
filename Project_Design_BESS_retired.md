# BESS Predictor for NYS & NYC — Project Steps

> **Hackathon:** [The Spark Hack Series — New York](https://luma.com/spark-hack-nyc?tk=s5GaSK)
> **Dates:** April 10–12, 2026 (Fri 6 PM → Sun 5 PM)
> **Track:** Environmental Impact
> **Hardware:** Acer Veriton GN100 w/ NVIDIA GB10 Grace Blackwell Superchip (128 GB unified memory, 1 PFLOP FP4)
> **Team Size:** 3–5 members

---

## Project Summary

Build a **local decision engine** that uses NYC Open Data to determine where Battery Energy Storage Systems (BESS) should be installed across municipal sites — and how they should be dispatched once operational. The model runs entirely on-device (GB10), with no cloud dependency.

**Why it matters:** New York State is scaling battery storage ~12x by 2030. The hardest question isn't building batteries — it's deciding which city sites should get them first and how to operate them to maximize public benefit.

---

## Data Sources (NYC Open Data)

| # | Dataset | ID | Rows | Key Fields | Last Updated |
|---|---------|-----|------|------------|--------------|
| 1 | [Value of Energy Cost Savings Program Savings for Businesses](https://data.cityofnewyork.us/City-Government/Value-of-Energy-Cost-Savings-Program-Savings-for-B/bug8-9f3g) | `bug8-9f3g` | 2,363 | address, borough, total_savings, electric_savings, gas_savings, lat/lon, industry | Jun 2023 |
| 2 | [Projected Citywide Energy Cost](https://data.cityofnewyork.us/City-Government/Projected-Citywide-Energy-Cost/tyv9-j3ti) | `tyv9-j3ti` | 290 | pub_dt, typ, fisc_yr, amt ($ millions) | Jan 2025 |
| 3 | [Electric Consumption And Cost (2010–Sep 2025)](https://data.cityofnewyork.us/Housing-Development/Electric-Consumption-And-Cost-2010-Sep-2025-jr/jr24-e7cr) | `jr24-e7cr` | 553,666 | development_name, borough, consumption_kwh, kwh_charges, consumption_kw, revenue_month | Jul 2024 |
| 4 | [NYC EV Fleet Station Network](https://data.cityofnewyork.us/City-Government/NYC-EV-Fleet-Station-Network/fc53-9hrv) | `fc53-9hrv` | 1,638 | agency, station_name, type_of_charger, no_of_ports, lat/lon, public_charger | Jan 2026 |
| 5 | [Municipal Solar-Readiness Assessment (LL24)](https://data.cityofnewyork.us/City-Government/City-of-New-York-Municipal-Solar-Readiness-Assessm/cfz5-6fvh) | `cfz5-6fvh` | 4,268 | agency, address, borough, roof_condition, roof_age, estimated_annual_production, upfront_project_cost, environmental_justice_area, lat/lon | Dec 2022 |
| 6 | [DCAS Managed Building Energy Usage](https://data.cityofnewyork.us/City-Government/DCAS-Managed-Building-Energy-Usage/ubdi-jgw2) | `ubdi-jgw2` | 55 | building_name, address, borough, fy15_energy_usage_mmbtu, lat/lon | May 2017 |
| 7 | [Local Law 84 Monthly Data (Calendar Year)](https://data.cityofnewyork.us/Environment/Local-Law-84-Monthly-Data-Calendar-Year-/fvp3-gcb2) | `fvp3-gcb2` | 2,207,184 | property_name, calendar_year, month, electricity_use_kbtu, natural_gas_use_kbtu, fuel_oil_use | Jan 2025 |

---

## Step-by-Step Plan

### Phase 1: Data Acquisition & Cleaning (Fri evening — ~3 hrs)

**Step 1.1 — Download all datasets**
- Pull CSVs via Socrata API: `https://data.cityofnewyork.us/resource/{id}.csv?$limit=50000`
- For LL84 (2.2M rows), paginate with `$offset` parameter
- Store raw files in `data/raw/`

**Step 1.2 — Standardize geo-references**
- Normalize address fields across all 7 datasets
- Ensure all records have `latitude`, `longitude`, `borough`, `bbl` (Borough-Block-Lot), and `census_tract`
- Use BBL as the primary join key for building-level merges; fall back to lat/lon proximity matching

**Step 1.3 — Clean & validate**
- Handle nulls, duplicates, and unit mismatches (kWh vs kBTU vs MMBTU)
- Convert all energy units to a common base (kWh recommended)
- Parse date fields into consistent `YYYY-MM` format
- Flag and remove obvious outliers (negative consumption, zero-area buildings)

**Step 1.4 — Build unified site table**
- Join datasets on BBL/address to create one row per municipal site
- Columns: `site_id`, `address`, `borough`, `lat`, `lon`, `avg_monthly_kwh`, `peak_kw`, `solar_potential_kwh`, `roof_condition`, `ev_charger_count`, `energy_cost_savings`, `environmental_justice_area`

---

### Phase 2: Feature Engineering (Sat morning — ~3 hrs)

**Step 2.1 — Energy demand features**
- Monthly consumption time series from LL84 + Electric Consumption datasets
- Peak-to-average demand ratio per site
- Year-over-year consumption trend (growing vs declining)
- Seasonal variability index

**Step 2.2 — Solar co-location features**
- Solar readiness score (roof condition + age + estimated production)
- Solar-BESS synergy score: sites with solar potential but high evening demand = ideal for storage

**Step 2.3 — Grid stress & resilience features**
- EV charger density within 500m radius (future load growth proxy)
- Environmental justice area flag (equity weighting)
- Projected energy cost trajectory from citywide projections

**Step 2.4 — Cost & feasibility features**
- Current energy cost per kWh at site level
- Estimated BESS payback period using energy savings data
- Upfront cost estimate based on solar-readiness assessment data

---

### Phase 3: Model Training on GB10 (Sat afternoon — ~4 hrs)

**Step 3.1 — Define the ranking objective**
- **BESS Priority Score**: composite metric reflecting public value
- Components: energy cost reduction potential, grid resilience contribution, solar synergy, equity impact, EV infrastructure support
- Weights tunable by user (default: equal weighting)

**Step 3.2 — Train local ranking model**
- Use the GB10's 128 GB unified memory for in-memory processing
- Approach options (pick based on time):
  - **Option A (Fast):** Gradient-boosted trees (XGBoost/LightGBM) — train a ranking model with features from Phase 2
  - **Option B (Advanced):** Fine-tune a small LLM (≤7B params) to act as a reasoning dispatch agent that explains *why* a site should get BESS
- Train/val split: 80/20 by borough to test geographic generalization

**Step 3.3 — Build dispatch simulator**
- Given a BESS installation at site X, simulate hourly charge/discharge cycles
- Inputs: site consumption profile, solar generation curve, time-of-use electricity rates
- Outputs: annual savings ($), peak demand reduction (kW), CO₂ offset (tons)
- Decision logic: charge during solar peak / off-peak hours, discharge during evening peak / EV charging surge

**Step 3.4 — Validate results**
- Compare top-ranked sites against known DCAS energy projects
- Sanity-check dispatch recommendations against NYSERDA BESS siting guidelines (250-ft setbacks, fire code compliance)
- Cross-validate priority scores across boroughs

---

### Phase 4: Interactive Dashboard & Visualization (Sat evening → Sun morning — ~6 hrs)

**Step 4.1 — Map-based site explorer**
- Interactive NYC map (Leaflet / Mapbox) showing all candidate sites
- Color-coded by BESS Priority Score (red = high priority, blue = low)
- Click a site → show detail card: energy profile, solar potential, EV proximity, estimated savings

**Step 4.2 — Scenario comparison tool**
- Slider controls: budget constraint, equity weighting, solar-preference toggle
- Real-time re-ranking as user adjusts parameters
- "If you have $X million, install BESS at these N sites first"

**Step 4.3 — Dispatch simulation view**
- For any selected site, show 24-hour charge/discharge cycle
- Overlay: solar generation, grid demand, EV charging load
- Summary metrics: annual $ saved, peak kW shaved, tons CO₂ avoided

**Step 4.4 — Borough-level summary**
- Aggregated stats per borough: total sites, total potential savings, equity coverage
- Exportable report (PDF/CSV) for municipal decision-makers

---

### Phase 5: Demo Prep & Submission (Sun — ~4 hrs)

**Step 5.1 — End-to-end test**
- Run full pipeline: data download → cleaning → feature engineering → model inference → dashboard
- Verify everything runs locally on the Acer Veriton GN100 with no cloud calls
- Benchmark: total inference time < 30 seconds for full site ranking

**Step 5.2 — Prepare demo narrative**
- **Problem:** NYC needs to deploy BESS at scale but lacks a data-driven siting tool
- **Solution:** Fully local AI engine that ranks 4,000+ municipal sites by public value
- **Demo flow:** Show map → pick a borough → drill into top site → run dispatch simulation → show savings
- **Impact:** Every dollar of BESS investment goes where it creates the most value

**Step 5.3 — Hack Fair presentation (Sun 4 PM)**
- 3-minute live demo on the GB10 hardware
- Emphasize: local-first AI, no cloud dependency, real NYC data, actionable output
- Have backup screenshots/video in case of hardware issues

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Hardware | Acer Veriton GN100 / NVIDIA GB10 | Hackathon-provided, 128 GB unified memory, 1 PFLOP FP4 |
| Data Processing | Python + Pandas/Polars | Fast tabular processing, fits in GB10 memory |
| ML Model | XGBoost or LightGBM (ranking mode) | Fast training, interpretable feature importance |
| LLM (optional) | Llama 3 8B (quantized, local) | Natural language explanations for site recommendations |
| Visualization | Streamlit + Folium/Leaflet | Rapid prototyping, interactive maps |
| Dispatch Sim | NumPy / custom Python | Hourly charge/discharge optimization |

---

## Judging Alignment

| Hackathon Criteria | How We Address It |
|--------------------|-------------------|
| On-device / local-first | 100% local — all data processing, model training, and inference on GB10 |
| Environmental Impact track | Direct tool for optimizing clean energy storage deployment |
| Uses NYC Open Data | 7 official datasets merged into unified decision engine |
| Practical public value | Helps city officials allocate BESS budgets where impact is highest |

---

## Key References

- [NYSERDA Battery Energy Storage System Guidebook](https://www.nyserda.ny.gov/All-Programs/Clean-Energy-Siting-Resources/Battery-Energy-Storage-Guidebook)
- [NYSERDA BESS Guidebook PDF (Nov 2024)](https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Clean-Energy-Siting/battery-storage-guidebook.pdf)
- [NYC Fire Code — BESS Rules](https://coderedconsultants.com/insights/new-rules-for-battery-energy-storage-systems-in-new-york-city/)
- [NVIDIA DGX Spark / GB10 Specs](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)
- [NYC Open Data Portal](https://data.cityofnewyork.us/)
