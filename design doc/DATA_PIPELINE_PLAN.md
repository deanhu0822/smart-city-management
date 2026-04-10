# Person 1: Data Pipeline Plan — "The Plumber"

> 12 datasets. 3 output tables. Zero fluff.

---

## Dataset Selection: 25 → 12

### What We Cut and Why

| Cut | Dataset | Rows | Why It's Out |
|-----|---------|------|-------------|
| ~~E2~~ | Projected Citywide Energy Cost | 290 | Reference-only. Hardcode the 3 numbers we need. |
| ~~E6~~ | DCAS Building Energy | 55 | Only 55 rows, last updated 2017. Stale and tiny. |
| ~~E8~~ | Heating Gas (NYCHA) | 248,915 | Overlaps with E3 (same developments). Gas adds marginal value vs. electric for BESS sizing. |
| ~~E9~~ | Cooking Gas (NYCHA) | 704,175 | Same overlap. 700K rows for cooking gas we don't use in battery dispatch. |
| ~~E11~~ | Natural Gas by ZIP | 1,015 | Single-year snapshot (2010). Too stale. |
| ~~E12~~ | GHG Emissions Inventory | 85 | Citywide totals only. Hardcode the waste/energy sector numbers. |
| ~~W4~~ | DSNY Collection Frequencies | geo | Collection schedule boundaries — useful in theory but not for our scoring or cuOpt. |
| ~~W5~~ | DSNY Sections | geo | Can derive district boundaries from community_district field in W1. |
| ~~W6~~ | Disposal Vendor Assignments | geo | Vendor names don't affect our optimization. |
| ~~W9~~ | Disposal Facilities by Year | 103 | Merge the key fields (cost/ton) directly into W8. |
| ~~W11~~ | Trade Waste Haulers | 680,452 | Massive dataset, we only need a borough-level count. Not worth 150 MB download. |
| ~~W13~~ | Climate Emissions Forecast | ~200 | Reference-only. Hardcode projections. |

**Saved:** ~1.7 GB download → ~1.0 GB. Eliminated 1.6M rows of marginal data. Freed ~2 hours of cleaning time.

---

## The Final 12 Datasets

### Energy (5 datasets)

| # | ID | Name | Rows | Size | Role in System |
|---|-----|------|------|------|---------------|
| **E1** | `bug8-9f3g` | Energy Cost Savings Program | 2,363 | ~1 MB | Cost burden geography — which areas pay most for energy |
| **E3** | `jr24-e7cr` | Electric Consumption & Cost (NYCHA) | 553,666 | ~120 MB | Monthly kWh + peak kW demand profiles per development |
| **E4** | `fc53-9hrv` | NYC EV Fleet Station Network | 1,638 | ~0.5 MB | EV charger locations — future load growth for BESS sizing |
| **E5** | `cfz5-6fvh` | Municipal Solar Readiness (LL24) | 4,268 | ~2 MB | **BASE TABLE** — every city building with solar potential, roof, EJ flag |
| **E7** | `fvp3-gcb2` | LL84 Monthly Energy Data | 2,207,184 | ~400 MB | Monthly electricity + gas for all large buildings — demand curves |

### Waste (5 datasets)

| # | ID | Name | Rows | Size | Role in System |
|---|-----|------|------|------|---------------|
| **W1** | `ebb7-mvp5` | DSNY Monthly Tonnage | 24,883 | ~5 MB | Refuse + recycling + organics by community district by month |
| **W2** | `erm2-nwe9` | 311 Requests (DSNY filter) | ~2,400,000 | ~800 MB | Missed pickups, overflows, illegal dumping — geocoded complaints |
| **W3** | `8znf-7b2c` | Litter Basket Inventory | 20,413 | ~3 MB | Every public trash can — density analysis + cuOpt input |
| **W7** | `if26-z6xq` | Food Scrap Drop-Off Locations | 591 | <1 MB | Composting access — gap analysis for organics diversion |
| **W8** | `ufxk-pq9j` | Disposal Facility Locations | 39 | <1 MB | Transfer stations + marine terminals — cuOpt depot locations |

### Nexus (2 datasets)

| # | ID | Name | Rows | Size | Role in System |
|---|-----|------|------|------|---------------|
| **E10** | `5zyy-y8am` | LL84 Annual Benchmarking | ~30,000 | ~15 MB | ENERGY STAR score, GHG emissions, building type per BBL |
| **W12** | `bpea-2i5q` | Waste Characterization | 2,112 | <1 MB | What's in the trash — % organic, recyclable, energy-viable |

```
TOTAL: 12 datasets
TOTAL ROWS: ~5.2 million
TOTAL DOWNLOAD: ~1.0 GB
```

---

## How the 12 Connect

```
                     ┌──────────────────────┐
                     │   E5 Solar Readiness  │
                     │   4,268 buildings     │
                     │   (BASE TABLE)        │
                     └──────────┬───────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
    BBL JOIN               SPATIAL JOIN         DISTRICT JOIN
          │                     │                     │
    ┌─────▼──────┐       ┌──────▼──────┐       ┌─────▼──────┐
    │ E7  LL84   │       │ E4  EV Stns │       │ W1 Tonnage │
    │ monthly    │       │ (1,638 pts) │       │ (59 dists) │
    │ (2.2M rows)│       │             │       │            │
    │            │       │ W3 Baskets  │       │ W2 311     │
    │ E10 Bench  │       │ (20K pts)   │       │ complaints │
    │ mark       │       │             │       │            │
    │            │       │ W7 Compost  │       │ W12 Waste  │
    │ E1 Savings │       │ (591 pts)   │       │ composition│
    │            │       │             │       │            │
    └────────────┘       │ W8 Transfer │       └────────────┘
                         │ (39 depots) │
                         └─────────────┘
```

---

## Raw → Clean: Per-Dataset Rules

### Unit Conversions (global)

```
1 kBTU  = 0.293071 kWh
1 therm = 29.3071 kWh
1 MMBTU = 293.071 kWh
→ ALL energy values normalized to kWh
→ ALL costs normalized to USD
→ ALL dates normalized to YYYY-MM
```

---

### E1: Energy Cost Savings Program (`bug8-9f3g`)

**Purpose:** Identify areas with high energy cost burden.

```
RAW COLUMNS USED:
  address, borough, bbl, latitude, longitude,
  total_savings, electric_savings, gas_savings, industry, census_tract

CLEAN:
  - Cast total_savings, electric_savings, gas_savings → float (coerce NaN)
  - Cast lat, lon → float; drop rows where both null
  - Cast bbl → string, zero-pad to 10 digits
  - Drop rows where total_savings <= 0

OUTPUT COLUMNS:
  address        string
  borough        string
  bbl            string
  lat            float
  lon            float
  total_savings  float    (USD)
  elec_savings   float    (USD)
  gas_savings    float    (USD)
  industry       string

ROWS OUT: ~2,200
JOIN KEY: bbl → aggregate by bbl, merge into unified_sites
```

---

### E3: Electric Consumption & Cost — NYCHA (`jr24-e7cr`)

**Purpose:** Monthly demand profiles — consumption curves, peak demand, costs.

```
RAW COLUMNS USED:
  development_name, borough, consumption_kwh, consumption_kw,
  current_charges, kwh_charges, kw_charges, revenue_month, rate_class

CLEAN:
  - Cast consumption_kwh, consumption_kw, current_charges → float
  - Parse revenue_month → YYYY-MM
      (formats vary: "2023-01-01T00:00:00" or "January 2023")
  - Drop rows where consumption_kwh is null or <= 0
  - Strip whitespace, title-case development_name

AGGREGATE → for unified_sites:
  GROUP BY development_name, borough:
    avg_monthly_kwh     = mean(consumption_kwh)
    max_peak_kw         = max(consumption_kw)
    avg_monthly_cost    = mean(current_charges)
    months_of_data      = count(*)

KEEP RAW → for time_series table:
    development_name, borough, yyyy_mm,
    consumption_kwh, consumption_kw, current_charges

OUTPUT (aggregated): ~800 unique developments
OUTPUT (time series): ~553,000 rows
```

---

### E4: EV Fleet Station Network (`fc53-9hrv`)

**Purpose:** EV charger proximity — future load growth for BESS sizing.

```
RAW COLUMNS USED:
  station_name, type_of_charger, no_of_ports, latitude, longitude,
  borough, bbl, public_charger_

CLEAN:
  - Cast no_of_ports → int (null → 1)
  - Cast lat, lon → float; drop rows where both null
  - Normalize charger type → ['Level 2', 'DC Fast', 'Level 1', 'Unknown']
  - Normalize public_charger_ → boolean

OUTPUT COLUMNS:
  station_name    string
  borough         string
  bbl             string
  lat             float
  lon             float
  charger_type    string
  num_ports       int
  is_public       bool

ROWS OUT: ~1,600
JOIN: Spatial — count ports within 500m and 1km of each site
```

---

### E5: Municipal Solar Readiness — LL24 (`cfz5-6fvh`) ⭐ BASE TABLE

**Purpose:** Complete inventory of 4,268 city buildings. This IS the site list.

```
RAW COLUMNS USED:
  agency, site, address, borough, bbl, bin, latitude, longitude,
  roof_condition, roof_age, estimated_annual_production,
  estimated_annual_energy, upfront_project_cost,
  environmental_justice_area, census_tract, year_of_report

CLEAN:
  - Cast estimated_annual_production, estimated_annual_energy → float
  - Cast upfront_project_cost → float (strip "$" and commas)
  - Cast lat, lon → float
  - Cast bbl → string, zero-pad to 10 digits
  - Normalize roof_condition → lowercase: good / fair / poor / unknown
  - Extract roof_age → integer years where possible, else -1
  - Normalize environmental_justice_area → boolean (Yes/No → True/False)
  - Deduplicate: keep latest year_of_report per bbl
  - Auto-generate site_id: 0..4267

OUTPUT COLUMNS:
  site_id                  int       (0..4267)
  agency                   string    (DOE, FDNY, DCAS, etc.)
  site_name                string
  address                  string
  borough                  string
  bbl                      string
  bin                      string
  lat                      float
  lon                      float
  roof_condition           string    (good/fair/poor/unknown)
  roof_age_years           int       (-1 if unknown)
  solar_production_kwh_yr  float
  solar_savings_usd_yr     float
  upfront_solar_cost_usd   float
  is_env_justice           bool
  census_tract             string
  community_district       int       (derived from census_tract or address)

ROWS OUT: 4,268
THIS TABLE SEEDS unified_sites — everything else joins onto it.
```

---

### E7: LL84 Monthly Energy Data (`fvp3-gcb2`) ⭐ LARGEST

**Purpose:** Monthly electricity + gas for all large buildings. Demand curve shapes.

```
RAW COLUMNS USED:
  property_id, property_name, calendar_year, month,
  electricity_use_kbtu, natural_gas_use_kbtu,
  fuel_oil_1_use_monthly_kbtu_ ... fuel_oil_5_6_...

CLEAN:
  - Cast all _kbtu columns → float, then convert to kWh (× 0.293071)
  - Cast property_id → string
  - Build yyyy_mm from calendar_year + month
  - Drop rows where electricity_kwh AND gas_kwh are both null
  - Compute total_kwh = electricity_kwh + gas_kwh + sum(fuel_oils_kwh)

AGGREGATE → for unified_sites:
  GROUP BY property_id:
    avg_monthly_elec_kwh    = mean(electricity_kwh)
    avg_monthly_gas_kwh     = mean(gas_kwh)
    avg_monthly_total_kwh   = mean(total_kwh)
    peak_monthly_elec_kwh   = max(electricity_kwh)
    months_reported         = count(*)
    seasonality_index       = std(electricity_kwh) / mean(electricity_kwh)

KEEP RAW → for time_series table:
    property_id, yyyy_mm, electricity_kwh, gas_kwh, total_kwh

OUTPUT (aggregated): ~18,000 unique properties
OUTPUT (time series): ~2,207,000 rows

NOTE: Download with $limit=50000 and paginate. This takes ~5 min.
      Use cuDF for processing — pandas will choke.
```

---

### E10: LL84 Annual Benchmarking (`5zyy-y8am`)

**Purpose:** ENERGY STAR score, GHG emissions, building type — enriches site profiles.

```
RAW COLUMNS USED:
  property_id, bbl, address, energy_star_score, site_eui, source_eui,
  total_ghg_emissions, year_built, property_type, latitude, longitude

CLEAN:
  - Cast bbl → string, zero-pad to 10 digits
  - Cast energy_star_score → int (null → -1)
  - Cast site_eui, source_eui, total_ghg_emissions → float
  - Cast year_built → int
  - Deduplicate: keep latest reporting year per bbl

OUTPUT COLUMNS:
  bbl                 string
  energy_star_score   int       (0–100, -1 if missing)
  site_eui            float     (kBTU/sqft)
  ghg_tons_co2e       float
  year_built          int
  property_type       string    (Office, School, Hospital, etc.)

ROWS OUT: ~25,000
JOIN KEY: bbl → merge into unified_sites
```

---

### W1: DSNY Monthly Tonnage (`ebb7-mvp5`)

**Purpose:** How much waste each community district generates, by type, by month.

```
RAW COLUMNS USED:
  month, borough, communitydistrict,
  refusetonscollected, papertonscollected, mgptonscollected,
  resorganicstons, schoolorganictons, leavesorganictons, xmastreetons

CLEAN:
  - Parse month → YYYY-MM
  - Cast all tonnage columns → float (null → 0)
  - Derive: all_organics = resorganics + schoolorganics + leaves + xmastree
  - Derive: total_tons = refuse + paper + mgp + all_organics
  - Derive: diversion_tons = paper + mgp + all_organics
  - Derive: diversion_rate = diversion_tons / total_tons
  - Parse communitydistrict → borough (string) + district_num (int)

AGGREGATE → for district_waste table:
  GROUP BY borough, district_num:
    avg_refuse_tons      = mean(refuse)
    avg_recycling_tons   = mean(paper + mgp)
    avg_organics_tons    = mean(all_organics)
    avg_total_tons       = mean(total_tons)
    avg_diversion_rate   = mean(diversion_rate)
    trend_slope          = linregress slope of total_tons over time

OUTPUT COLUMNS:
  borough              string
  community_district   int
  avg_refuse_tons_mo   float
  avg_recycling_tons_mo float
  avg_organics_tons_mo float
  avg_total_tons_mo    float
  diversion_rate       float    (0–1)
  trend_slope          float    (positive = growing)

ROWS OUT: 59 community districts
```

---

### W2: 311 Requests — DSNY (`erm2-nwe9`)

**Purpose:** Where waste service is failing — complaints, illegal dumping, overflows.

```
DOWNLOAD FILTER: $where=agency='DSNY' (reduces from 30M to ~2.4M)

RAW COLUMNS USED:
  complaint_type, descriptor, latitude, longitude,
  created_date, closed_date, borough, community_board

CLEAN:
  - Cast lat, lon → float
  - Parse created_date, closed_date → datetime
  - Categorize complaint_type:
      'Missed Collection'         → missed
      'Dirty Conditions'          → dirty
      'Overflowing Litter Basket' → overflow
      'Illegal Dumping'           → dumping
      everything else             → other
  - Extract community_district from community_board field

AGGREGATE → for district_waste table:
  GROUP BY borough, community_district:
    total_complaints      = count(*)
    missed_count          = count(type=missed)
    overflow_count        = count(type=overflow)
    dumping_count         = count(type=dumping)
    avg_resolution_hrs    = mean(closed - created) in hours

OUTPUT COLUMNS:
  borough              string
  community_district   int
  total_complaints     int
  missed_count         int
  overflow_count       int
  dumping_count        int
  avg_resolution_hrs   float

ROWS OUT: 59 districts (aggregated from ~2.4M rows)

NOTE: This is the biggest download (~800 MB).
      Filter server-side with $where clause to reduce.
      Process with cuDF — pandas will be slow.
```

---

### W3: Litter Basket Inventory (`8znf-7b2c`)

**Purpose:** Public trash can locations — density analysis + cuOpt routing input.

```
RAW COLUMNS USED:
  basketid, baskettype, streetname1, section,
  latitude, longitude (or point geometry)

CLEAN:
  - Extract lat, lon from point geometry if needed
  - Cast lat, lon → float; drop rows without valid coords

OUTPUT COLUMNS:
  basket_id       string
  basket_type     string
  lat             float
  lon             float
  section         string

ROWS OUT: ~20,000

AGGREGATE → for district_waste:
  Spatial join to community districts → basket_count per district

ALSO: Raw points used as input for cuOpt VRP (optional demand nodes)
```

---

### W7: Food Scrap Drop-Off Locations (`if26-z6xq`)

**Purpose:** Where composting access exists — gap analysis for organics diversion.

```
RAW COLUMNS USED:
  sitename, siteaddr, borough, latitude, longitude, day_hours, dsny_district

CLEAN:
  - Cast lat, lon → float
  - Extract district number from dsny_district

OUTPUT COLUMNS:
  site_name       string
  address         string
  borough         string
  lat             float
  lon             float
  district        int

ROWS OUT: ~591

JOIN: Spatial — count composting sites within 1km of each building
      Also aggregate per district for district_waste table
```

---

### W8: Disposal Facility Locations (`ufxk-pq9j`)

**Purpose:** Transfer stations and marine terminals — depot locations for cuOpt.

```
RAW COLUMNS USED:
  name, street_address, borough_city, state, type, latitude, longitude

CLEAN:
  - Cast lat, lon → float
  - Normalize type → ['Transfer Station', 'Marine Transfer Station',
                       'Rail Yard', 'Other']

OUTPUT COLUMNS:
  facility_name    string
  address          string
  city             string
  state            string
  facility_type    string
  lat              float
  lon              float

ROWS OUT: 39

USAGE:
  - cuOpt: these are the depots in the Vehicle Routing Problem
  - Dashboard: map markers for transfer stations
  - unified_sites: nearest transfer station per building (spatial join)
```

---

### W12: Waste Characterization (`bpea-2i5q`)

**Purpose:** What's actually in the trash — % organic, recyclable, energy-viable.

```
RAW COLUMNS USED:
  material_category, material_group, generator_type,
  refuse_percent, paper_percent, organics_percent

CLEAN:
  - Cast all percent columns → float
  - Filter: generator_type = 'Residential' (matches DSNY-managed waste)
  - Average across time periods for stable composition estimate
  - Compute energy_viable_pct = organics_pct + paper_pct (combustible)

OUTPUT COLUMNS:
  material_category    string
  material_group       string
  refuse_pct           float
  recyclable_pct       float
  organics_pct         float
  energy_viable_pct    float

ROWS OUT: ~30 material categories

USAGE: Multiply by district tonnage (W1) to estimate:
  - Divertible organic tons per district
  - Waste-to-energy potential (organic tons × ~500 kWh/ton biogas yield)
```

---

## The 3 Output Tables

### TABLE 1: `unified_sites.parquet` — 4,268 rows × 38 columns

One row per municipal building. Feeds LLM scorer, dashboard, scenario planner.

```
COLUMN                        TYPE     SOURCE    DESCRIPTION
─────────────────────────────────────────────────────────────
site_id                       int      E5        Auto 0..4267
site_name                     str      E5        Building name
address                       str      E5        Street address
borough                       str      E5        Borough name
agency                        str      E5        DOE, FDNY, etc.
bbl                           str      E5        Borough-Block-Lot
lat                           float    E5        Latitude
lon                           float    E5        Longitude
community_district            int      E5→derive District number
is_env_justice                bool     E5        Environmental Justice flag

roof_condition                str      E5        good/fair/poor
roof_age_years                int      E5        Years (-1=unknown)
solar_production_kwh_yr       float    E5        Annual solar output
solar_savings_usd_yr          float    E5        Annual solar savings

avg_monthly_elec_kwh          float    E7        Avg monthly electricity
avg_monthly_gas_kwh           float    E7        Avg monthly gas
avg_monthly_total_kwh         float    E7        Avg monthly total
peak_monthly_elec_kwh         float    E7        Max month electricity
seasonality_index             float    E7        Demand variability
energy_star_score             int      E10       0–100 rating
ghg_tons_co2e                 float    E10       Annual GHG
property_type                 str      E10       Office/School/etc
annual_energy_cost_usd        float    E3/E7     Estimated annual cost
max_peak_kw                   float    E3        Max peak demand

ev_ports_500m                 int      E4→spatial EV ports within 500m
ev_ports_1km                  int      E4→spatial EV ports within 1km
nearest_ev_dist_m             float    E4→spatial Distance to nearest

district_refuse_tons_mo       float    W1        District refuse/month
district_organics_tons_mo     float    W1        District organics/month
district_diversion_rate       float    W1        District diversion rate
district_complaints           int      W2        311 complaints in district
compost_sites_1km             int      W7→spatial Composting sites nearby
nearest_transfer_km           float    W8→spatial Nearest transfer station

solar_score                   float    computed  Percentile rank (0–1)
roof_score                    float    computed  good=1, fair=0.6, poor=0.2
equity_flag                   float    computed  1.0 if EJ, 0.0 if not
ev_density_score              float    computed  Percentile rank (0–1)
energy_intensity_score        float    computed  Percentile rank (0–1)
waste_burden_score            float    computed  Percentile rank (0–1)
```

### TABLE 2: `district_waste.parquet` — 59 rows × 22 columns

One row per community district. Feeds cuOpt, waste analysis, dashboard.

```
COLUMN                        TYPE     SOURCE    DESCRIPTION
─────────────────────────────────────────────────────────────
borough                       str      W1        Borough name
community_district            int      W1        District number
district_code                 str      derived   "BX01", "MN03"

avg_refuse_tons_mo            float    W1        Monthly refuse
avg_recycling_tons_mo         float    W1        Monthly recycling
avg_organics_tons_mo          float    W1        Monthly organics
avg_total_tons_mo             float    W1        Monthly total
diversion_rate                float    W1        0–1
trend_slope                   float    W1        Tonnage trend

est_divertible_organics_tons  float    W1×W12    Organics in refuse stream
est_energy_potential_kwh      float    W1×W12    Organic tons × 500 kWh/ton

total_complaints              int      W2        Total 311 complaints
missed_count                  int      W2        Missed pickups
overflow_count                int      W2        Overflowing bins
dumping_count                 int      W2        Illegal dumping
avg_resolution_hrs            float    W2        Avg response time

basket_count                  int      W3        Public trash cans
compost_sites                 int      W7        Drop-off composting sites
nearest_transfer_station      str      W8        Name
nearest_transfer_km           float    W8        Distance

diversion_gap                 float    computed  0.30 - actual_rate
waste_intensity_score         float    computed  Percentile rank (0–1)
```

### TABLE 3: `time_series.parquet` — ~2.76M rows × 8 columns

Monthly energy readings. Feeds dispatch simulator + forecast charts.

```
COLUMN                        TYPE     SOURCE    DESCRIPTION
─────────────────────────────────────────────────────────────
source                        str      —         'll84' or 'nycha'
property_id                   str      E7/E3     Property or dev name
borough                       str      E7/E3     Borough
yyyy_mm                       str      E7/E3     '2024-01' format
electricity_kwh               float    E7/E3     Monthly electricity
gas_kwh                       float    E7/E3     Monthly gas
total_kwh                     float    E7/E3     Electricity + gas
cost_usd                      float    E3        Monthly cost (if avail)

ROWS: ~2,207,000 (LL84) + ~553,000 (NYCHA) = ~2,760,000
```

---

## GB10 Memory Budget (Revised)

```
unified_sites.parquet    4,268 × 38      →    ~12 MB in cuDF
district_waste.parquet   59 × 22         →    ~0.05 MB in cuDF
time_series.parquet      2.76M × 8       →    ~600 MB in cuDF

Raw intermediates during cleaning:
  E7 LL84 (2.2M rows)                   →    ~2.5 GB in cuDF
  W2 311 (2.4M rows)                    →    ~3.5 GB in cuDF
  All others                            →    ~0.3 GB in cuDF

PEAK DATA MEMORY (during cleaning):     →    ~7 GB
AFTER CLEANUP (only final tables):      →    ~0.6 GB

LLM (Llama 3.1 8B quantized via NIM):  →    ~8–16 GB
cuOpt solver:                           →    ~2 GB
Streamlit + dashboard:                  →    ~1 GB
────────────────────────────────────────────────────
TOTAL PEAK:                              →    ~26 GB
REMAINING:                               →    ~102 GB free
```

---

## Join Execution Order (copy-paste ready)

```python
import cudf
import cuspatial

# ── STEP 1: Load & clean base table ──────────────────────
sites = clean_e5_solar_readiness()              # 4,268 rows

# ── STEP 2: BBL joins (building-level) ───────────────────
e7_agg  = clean_e7_ll84().groupby('bbl').agg(...)
e10     = clean_e10_benchmarking()              # deduped by bbl
e1_agg  = clean_e1_savings().groupby('bbl').agg(...)

sites = sites.merge(e7_agg,  on='bbl', how='left')
sites = sites.merge(e10,     on='bbl', how='left')
sites = sites.merge(e1_agg,  on='bbl', how='left')

# E3 NYCHA: join on development_name for public housing sites
e3_agg = clean_e3_nycha().groupby('development_name').agg(...)
# (fuzzy match or manual mapping to site_name where possible)

# ── STEP 3: Spatial joins (GPU via cuSpatial) ────────────
ev   = clean_e4_ev_stations()
comp = clean_w7_food_scrap()
xfer = clean_w8_disposal_facilities()

sites['ev_ports_500m']       = spatial_count(sites, ev, radius=500)
sites['ev_ports_1km']        = spatial_count(sites, ev, radius=1000)
sites['nearest_ev_dist_m']   = spatial_nearest(sites, ev)
sites['compost_sites_1km']   = spatial_count(sites, comp, radius=1000)
sites['nearest_transfer_km'] = spatial_nearest(sites, xfer) / 1000

# ── STEP 4: District joins ──────────────────────────────
districts = build_district_table(w1, w2, w3, w7, w8, w12)   # 59 rows

sites = sites.merge(
    districts[['community_district', 'avg_refuse_tons_mo',
               'avg_organics_tons_mo', 'diversion_rate',
               'total_complaints']],
    on='community_district', how='left'
)

# ── STEP 5: Compute scores ──────────────────────────────
sites['solar_score']     = sites['solar_production_kwh_yr'].rank(pct=True)
sites['roof_score']      = sites['roof_condition'].map(
                             {'good':1.0, 'fair':0.6, 'poor':0.2}).fillna(0.4)
sites['equity_flag']     = sites['is_env_justice'].astype(float)
sites['ev_density_score'] = sites['ev_ports_1km'].rank(pct=True)
sites['energy_intensity_score'] = sites['avg_monthly_total_kwh'].rank(pct=True)
sites['waste_burden_score'] = sites['district_refuse_tons_mo'].rank(pct=True)

# ── STEP 6: Save ────────────────────────────────────────
sites.to_parquet('data/processed/unified_sites.parquet')
districts.to_parquet('data/processed/district_waste.parquet')
time_series.to_parquet('data/processed/time_series.parquet')
```

---

## Person 1 Checklist (Revised)

```
FRIDAY EVENING (6–11 PM) — Download & Clean
  [ ] Download 12 datasets via Socrata API
      Priority order: E5, E7, W2, E3 (big ones first)
  [ ] Verify row counts match expected
  [ ] Test cuDF: load E7 (2.2M rows), confirm GPU acceleration
  [ ] Clean E5 (base table) — get this perfect
  [ ] Clean E7 (unit conversion kBTU→kWh, date parsing)
  [ ] Clean E3, E4, E1, E10

FRIDAY NIGHT (11 PM–2 AM) — Clean Waste + Start Joins
  [ ] Clean W1, W2, W3, W7, W8, W12
  [ ] Aggregate W1→district tonnage, W2→district complaints
  [ ] Build district_waste table (59 rows)
  [ ] Start BBL joins: E5 + E7_agg + E10

SATURDAY MORNING (8 AM–12 PM) — Spatial Joins + Scores
  [ ] cuSpatial: EV proximity, compost proximity, transfer proximity
  [ ] District join: sites + waste district data
  [ ] Compute all derived scores
  [ ] Build time_series table from E7 + E3 raw
  [ ] Save all 3 parquet files
  [ ] Run cuDF vs pandas benchmark — record numbers

SATURDAY AFTERNOON (12–3 PM) — Handoff
  [ ] Hand off parquets to Person 2 + Person 3
  [ ] Prep cuOpt input from district_waste + W8
  [ ] Spot-check 10 random sites for data quality
  [ ] Fix any issues Person 2/3 find

DONE WHEN:
  [ ] 3 parquet files on disk, loadable in cuDF
  [ ] Person 2 confirms LLM scorer runs clean
  [ ] Person 3 confirms dashboard renders correctly
  [ ] Benchmark numbers documented
```
