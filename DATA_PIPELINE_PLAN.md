# Person 1: Data Pipeline Plan — "The Plumber"

> What goes in, what comes out, and what the GB10 actually sees.

---

## Overview

25 raw datasets → cleaned → merged into **3 final tables** that feed every downstream system on the GB10:

```
  25 Raw CSVs (Socrata API)
        │
        ▼
  ┌─────────────┐
  │  CLEAN &     │   Normalize units, fix types, drop junk
  │  STANDARDIZE │
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  JOIN &      │   BBL, Community District, lat/lon proximity
  │  MERGE       │
  └──────┬──────┘
         │
         ├──→  TABLE 1: unified_sites.parquet     (4,268 rows × 48 cols)
         │     One row per municipal building. Feeds LLM scorer + dashboard.
         │
         ├──→  TABLE 2: district_waste.parquet     (59 rows × 35 cols)
         │     One row per community district. Feeds waste analysis + cuOpt.
         │
         └──→  TABLE 3: time_series.parquet        (~2.8M rows × 12 cols)
              Monthly energy readings per site. Feeds dispatch simulator.
```

---

## Part 1: Raw Dataset Inventory — What We Download

### Energy Datasets (E1–E12)

| ID | Name | Rows | Download Size | Key Raw Columns |
|----|------|------|---------------|-----------------|
| E1 `bug8-9f3g` | Energy Cost Savings | 2,363 | ~1 MB | `address`, `borough`, `total_savings`, `electric_savings`, `gas_savings`, `latitude`, `longitude`, `bbl`, `industry`, `census_tract` |
| E2 `tyv9-j3ti` | Projected Citywide Energy Cost | 290 | <1 MB | `pub_dt`, `typ`, `fisc_yr`, `amt` |
| E3 `jr24-e7cr` | Electric Consumption (NYCHA) | 553,666 | ~120 MB | `development_name`, `borough`, `consumption_kwh`, `consumption_kw`, `current_charges`, `kwh_charges`, `kw_charges`, `revenue_month`, `vendor_name`, `rate_class` |
| E4 `fc53-9hrv` | EV Fleet Stations | 1,638 | ~0.5 MB | `station_name`, `type_of_charger`, `no_of_ports`, `latitude`, `longitude`, `borough`, `bbl`, `public_charger_` |
| E5 `cfz5-6fvh` | Solar Readiness (LL24) | 4,268 | ~2 MB | `agency`, `site`, `address`, `borough`, `roof_condition`, `roof_age`, `estimated_annual_production`, `estimated_annual_energy`, `environmental_justice_area`, `upfront_project_cost`, `latitude`, `longitude`, `bbl`, `bin`, `census_tract` |
| E6 `ubdi-jgw2` | DCAS Building Energy | 55 | <1 MB | `building_name`, `building_address`, `borough`, `fy15_energy_usage_mmbtu`, `latitude`, `longitude`, `bbl` |
| E7 `fvp3-gcb2` | LL84 Monthly Energy | 2,207,184 | ~400 MB | `property_id`, `property_name`, `calendar_year`, `month`, `electricity_use_kbtu`, `natural_gas_use_kbtu`, `fuel_oil_1_use_monthly_kbtu_` through `fuel_oil_5_6_...` |
| E8 `it56-eyq4` | Heating Gas (NYCHA) | 248,915 | ~50 MB | `development_name`, `borough`, `consumption_therms`, `current_charges`, `revenue_month`, `vendor_name` |
| E9 `avhb-5jhc` | Cooking Gas (NYCHA) | 704,175 | ~130 MB | same structure as E8 |
| E10 `5zyy-y8am` | LL84 Annual Benchmarking | ~30,000 | ~15 MB | `property_id`, `bbl`, `address`, `energy_star_score`, `site_eui`, `source_eui`, `total_ghg_emissions`, `electricity_use`, `natural_gas_use`, `year_built`, `property_type`, `latitude`, `longitude` |
| E11 `uedp-fegm` | Natural Gas by ZIP | 1,015 | <1 MB | `zip_code`, `building_type`, `consumption_therms`, `consumption_gj` |
| E12 `wq7q-htne` | GHG Emissions Inventory | 85 | <1 MB | `source_units`, `consumed_qty`, `tco2e_100yr`, `calendar_year` |

### Waste Datasets (W1–W13)

| ID | Name | Rows | Download Size | Key Raw Columns |
|----|------|------|---------------|-----------------|
| W1 `ebb7-mvp5` | DSNY Monthly Tonnage | 24,883 | ~5 MB | `month`, `borough`, `communitydistrict`, `refusetonscollected`, `papertonscollected`, `mgptonscollected`, `resorganicstons`, `schoolorganictons`, `leavesorganictons` |
| W2 `erm2-nwe9` | 311 Requests (DSNY) | ~2,400,000 | ~800 MB | `complaint_type`, `descriptor`, `latitude`, `longitude`, `created_date`, `closed_date`, `borough`, `community_board`, `status` |
| W3 `8znf-7b2c` | Litter Basket Inventory | 20,413 | ~3 MB | `basketid`, `baskettype`, `streetname1`, `section`, `latitude`, `longitude` |
| W4 `rv63-53db` | DSNY Collection Frequencies | geo | ~2 MB | geometry + district + frequency schedule |
| W5 `7vgu-qbur` | DSNY Sections | geo | ~1 MB | geometry + section boundaries |
| W6 `fpv2-r9br` | Disposal Vendor Assignments | geo | ~1 MB | `district`, `vendor_refuse`, `vendor_paper`, `vendor_mgp`, `vendor_organics` |
| W7 `if26-z6xq` | Food Scrap Drop-Offs | 591 | <1 MB | `sitename`, `siteaddr`, `borough`, `latitude`, `longitude`, `day_hours`, `dsny_district` |
| W8 `ufxk-pq9j` | Disposal Facility Locations | 39 | <1 MB | `name`, `address`, `borough_city`, `state`, `type`, `latitude`, `longitude` |
| W9 `6r9j-qrwz` | Disposal Facilities by Year | 103 | <1 MB | `calendar_year`, `facility_name`, `facility_type`, `price_per_ton`, `contracted_tons_per_day`, `actual_tons_delivered_per_year` |
| W10 `99xv-he3n` | Disposal Sites by Facility | 211 | <1 MB | `calendar_year`, `facility_name`, `disposal_site_name`, `disposal_site_type`, `truck_or_rr`, `miles_to_site`, `tons_per_day` |
| W11 `867j-5pgi` | Trade Waste Haulers | 680,452 | ~150 MB | `account_name`, `trade_name`, `address`, `authorized_recycling_type`, `organic_waste_services`, `latitude`, `longitude` |
| W12 `bpea-2i5q` | Waste Characterization | 2,112 | <1 MB | `material_category`, `material_group`, `generator_type`, `refuse_percent`, `paper_percent`, `mgp_percent`, `organics_percent` |
| W13 `czei-7bxd` | Climate Emissions Forecast | ~200 | <1 MB | `forecast_year`, `sector`, `source`, `metric_tons_co2e`, `scenario` |

**Total raw download: ~1.7 GB**
**Total raw rows: ~6.8 million**

---

## Part 2: Cleaning Rules — Per Dataset

### Unit Conversions (apply globally)

```
1 kBTU    = 0.293071 kWh
1 MMBTU   = 293.071 kWh
1 therm   = 29.3071 kWh
1 GJ      = 277.778 kWh
```

All energy values normalized to **kWh**. All costs normalized to **USD**. All dates normalized to **YYYY-MM** string.

### E1: Energy Cost Savings
```
CLEAN:
  - Cast total_savings, electric_savings, gas_savings → float (coerce errors to NaN)
  - Cast latitude, longitude → float
  - Cast bbl → string (pad to 10 digits)
  - Drop rows where latitude OR longitude is null (can't geolocate)
  - Drop rows where total_savings <= 0 (invalid)
OUTPUT COLS:
  address, borough, bbl, lat, lon, total_savings_usd, electric_savings_usd,
  gas_savings_usd, industry, census_tract
ROWS EXPECTED: ~2,200 (after dropping nulls)
```

### E2: Projected Citywide Energy Cost
```
CLEAN:
  - Cast amt → float (already in $ millions)
  - Parse fisc_yr → integer
  - Keep only typ in ['Electric', 'Gas', 'Steam', 'Fuel Oil']
OUTPUT COLS:
  fiscal_year, energy_type, projected_cost_millions
ROWS EXPECTED: ~290
NOTE: This is a lookup table, not joined to sites. Used for forecasting context.
```

### E3: Electric Consumption (NYCHA)
```
CLEAN:
  - Cast consumption_kwh, consumption_kw, current_charges → float
  - Parse revenue_month → YYYY-MM (format varies: "2023-01-01" or "January 2023")
  - Drop rows where consumption_kwh is null or <= 0
  - Drop rows where revenue_month can't be parsed
  - Normalize development_name: strip whitespace, title case
AGGREGATE (for site table):
  GROUP BY development_name, borough:
    avg_monthly_kwh = mean(consumption_kwh)
    max_peak_kw = max(consumption_kw)
    avg_monthly_cost = mean(current_charges)
    months_count = count(*)
    first_month = min(revenue_month)
    last_month = max(revenue_month)
OUTPUT COLS (aggregated):
  development_name, borough, avg_monthly_kwh, max_peak_kw,
  avg_monthly_cost_usd, months_count
ROWS EXPECTED (aggregated): ~800 unique developments
KEEP RAW for time_series table: development_name, borough, revenue_month,
  consumption_kwh, consumption_kw, current_charges
```

### E4: EV Fleet Stations
```
CLEAN:
  - Cast no_of_ports → int (fill null with 1)
  - Cast latitude, longitude → float
  - Cast bbl → string
  - Normalize type_of_charger: map to ['Level 2', 'DC Fast', 'Level 1', 'Unknown']
  - Normalize public_charger_ → boolean (Yes/No → True/False)
OUTPUT COLS:
  station_name, borough, bbl, lat, lon, charger_type, num_ports, is_public
ROWS EXPECTED: ~1,600
```

### E5: Solar Readiness (LL24) — PRIMARY BASE TABLE
```
CLEAN:
  - Cast estimated_annual_production, estimated_annual_energy → float
  - Cast latitude, longitude → float
  - Cast bbl → string (pad to 10 digits)
  - Normalize roof_condition: lowercase, map to ['good', 'fair', 'poor', 'unknown']
  - Normalize roof_age: extract years if possible, else 'unknown'
  - Normalize environmental_justice_area → boolean
  - Cast upfront_project_cost → float (strip $ and commas)
  - Keep latest year_of_report per site (deduplicate on bbl)
OUTPUT COLS:
  site_id (auto-generated 0..4267), agency, site_name, address, borough,
  bbl, bin, lat, lon, roof_condition, roof_age_years,
  solar_production_kwh_yr, solar_savings_usd_yr, upfront_cost_usd,
  is_env_justice, census_tract, year_of_report
ROWS EXPECTED: 4,268 (one per building — this IS the base table)
```

### E6: DCAS Building Energy
```
CLEAN:
  - Find energy column (name varies, contains 'mmbtu')
  - Convert MMBTU → kWh: multiply by 293.071
  - Cast latitude, longitude → float
  - Cast bbl → string
OUTPUT COLS:
  building_name, address, borough, bbl, lat, lon, annual_energy_kwh
ROWS EXPECTED: 55
NOTE: Small dataset. Left-join onto site table by bbl for enrichment.
```

### E7: LL84 Monthly Energy — LARGEST DATASET
```
CLEAN:
  - Cast electricity_use_kbtu, natural_gas_use_kbtu, all fuel_oil_* → float
  - Convert all from kBTU → kWh (multiply by 0.293071)
  - Cast property_id → string
  - Parse calendar_year + month → YYYY-MM string
  - Drop rows where electricity_kwh is null AND gas_kwh is null (no data)
  - Compute total_energy_kwh = electricity_kwh + gas_kwh + sum(fuel_oil_kwh)
AGGREGATE (for site table):
  GROUP BY property_id, property_name:
    avg_monthly_elec_kwh = mean(electricity_kwh)
    avg_monthly_gas_kwh = mean(gas_kwh)
    avg_monthly_total_kwh = mean(total_energy_kwh)
    peak_monthly_elec_kwh = max(electricity_kwh)
    months_reported = count(*)
    seasonality_index = std(electricity_kwh) / mean(electricity_kwh)
OUTPUT COLS (aggregated):
  property_id, property_name, avg_monthly_elec_kwh, avg_monthly_gas_kwh,
  avg_monthly_total_kwh, peak_monthly_elec_kwh, months_reported, seasonality_index
ROWS EXPECTED (aggregated): ~18,000 unique properties
KEEP RAW for time_series table: property_id, yyyy_mm, electricity_kwh,
  gas_kwh, total_energy_kwh
```

### E8 + E9: Heating Gas + Cooking Gas (NYCHA)
```
CLEAN (same for both):
  - Cast consumption_therms → float, convert to kWh (× 29.3071)
  - Parse revenue_month → YYYY-MM
  - Drop null consumption rows
AGGREGATE:
  GROUP BY development_name, borough:
    avg_monthly_heating_kwh (E8) / avg_monthly_cooking_kwh (E9)
OUTPUT: merge onto NYCHA development profiles
```

### E10: LL84 Annual Benchmarking
```
CLEAN:
  - Cast bbl → string (pad to 10 digits)
  - Cast energy_star_score → int (0–100, null = -1)
  - Cast site_eui, source_eui → float
  - Cast total_ghg_emissions → float (metric tons CO₂e)
  - Cast year_built → int
  - Keep latest reporting year per property
OUTPUT COLS:
  property_id, bbl, address, energy_star_score, site_eui, source_eui,
  ghg_tons_co2e, year_built, property_type, lat, lon
ROWS EXPECTED: ~25,000 (deduplicated)
NOTE: Join to site table on bbl for ENERGY STAR score + GHG + building type.
```

### E11: Natural Gas by ZIP
```
CLEAN:
  - Cast consumption_therms → float → kWh
  - Group by zip_code for total gas consumption per ZIP
OUTPUT: lookup table, joined via ZIP code if needed
```

### E12: GHG Emissions Inventory
```
CLEAN:
  - Keep latest calendar_year rows
  - Pivot by sector for citywide context
OUTPUT: reference table (not joined to sites)
```

### W1: DSNY Monthly Tonnage
```
CLEAN:
  - Parse month → YYYY-MM
  - Cast all tonnage columns → float (fill null with 0)
  - Derive: total_tonnage = refuse + paper + mgp + all_organics
  - Derive: diversion_tonnage = paper + mgp + all_organics
  - Derive: diversion_rate = diversion_tonnage / total_tonnage
  - Extract community_district as integer (e.g., "BX01" → borough="Bronx", district=1)
AGGREGATE (for district table):
  GROUP BY borough, community_district:
    avg_monthly_refuse_tons = mean(refusetonscollected)
    avg_monthly_recycling_tons = mean(paper + mgp)
    avg_monthly_organics_tons = mean(all organics)
    avg_monthly_total_tons = mean(total_tonnage)
    avg_diversion_rate = mean(diversion_rate)
    trend_slope = linear regression slope of total_tonnage over time
OUTPUT COLS:
  borough, community_district, avg_monthly_refuse_tons, avg_monthly_recycling_tons,
  avg_monthly_organics_tons, avg_monthly_total_tons, avg_diversion_rate, trend_slope
ROWS EXPECTED: 59 community districts
```

### W2: 311 Requests (DSNY filter)
```
CLEAN:
  - Filter: agency == 'DSNY'
  - Cast latitude, longitude → float
  - Parse created_date → YYYY-MM
  - Categorize complaint_type into buckets:
      'Missed Collection' → 'missed_collection'
      'Dirty Conditions' → 'dirty_conditions'
      'Overflowing Litter Basket' → 'overflow'
      'Illegal Dumping' → 'illegal_dumping'
      everything else → 'other'
  - Extract community_board → community_district integer
AGGREGATE (for district table):
  GROUP BY borough, community_district:
    total_complaints = count(*)
    missed_collection_count = count where type = missed_collection
    overflow_count = count where type = overflow
    illegal_dumping_count = count where type = illegal_dumping
    avg_resolution_hours = mean(closed_date - created_date) in hours
OUTPUT COLS:
  borough, community_district, total_complaints, missed_collection_count,
  overflow_count, illegal_dumping_count, avg_resolution_hours
ROWS EXPECTED: 59 districts
NOTE: This is 2.4M rows — use cuDF for speed. Download with $where=agency='DSNY'
  to reduce download size, or paginate.
```

### W3: Litter Basket Inventory
```
CLEAN:
  - Cast latitude, longitude → float (from stateplane if needed)
  - Drop rows without valid coordinates
AGGREGATE (for district table):
  Spatial join to community districts → count baskets per district
OUTPUT COLS:
  borough, community_district, basket_count
ALSO USED: Raw lat/lon for cuOpt VRP input and spatial proximity to sites
ROWS EXPECTED: ~20,000 (raw), 59 (aggregated)
```

### W7: Food Scrap Drop-Offs
```
CLEAN:
  - Cast latitude, longitude → float
  - Extract dsny_district
OUTPUT COLS:
  site_name, address, borough, lat, lon, district
USED FOR: Count composting sites per district, proximity analysis
```

### W8: Disposal Facility Locations
```
CLEAN:
  - Cast latitude, longitude → float
  - Normalize type: ['Transfer Station', 'Marine Transfer Station', 'Rail Yard', 'Other']
OUTPUT COLS:
  facility_name, address, city, state, facility_type, lat, lon
ROWS: 39
USED FOR: cuOpt depot locations, distance calculations
```

### W9 + W10: Disposal Facilities + Sites by Year
```
CLEAN:
  - Cast price_per_ton, tons_per_day, miles_to_site → float
  - Keep latest calendar_year
  - Join W9 + W10 on facility_name to get full chain:
    facility → disposal_site → transport_mode → miles → cost
OUTPUT COLS:
  facility_name, facility_type, disposal_site, disposal_type,
  transport_mode (truck/rail), miles, price_per_ton, tons_per_day
ROWS: ~40 facility-site pairs
USED FOR: Waste flow Sankey, cost modeling, route optimization context
```

### W11: Trade Waste Haulers
```
CLEAN:
  - Cast latitude, longitude → float
  - Filter to active licenses only
  - Flag haulers with organic_waste_services = 'Yes'
AGGREGATE:
  GROUP BY borough: count haulers, count organic-capable haulers
OUTPUT: context data for commercial waste analysis
NOTE: 680K rows but we only need borough-level aggregates
```

### W12: Waste Characterization
```
CLEAN:
  - Cast all percent columns → float
  - Filter generator_type = 'Residential' (for DSNY-managed waste)
  - Average across periods for stable composition estimate
OUTPUT COLS:
  material_category, material_group, refuse_pct, paper_pct, organics_pct
ROWS: ~30 material categories
USED FOR: Multiply by district tonnage to estimate divertible organics per district
```

### W13: Climate Emissions Forecast
```
CLEAN:
  - Filter sector = 'Waste' or 'Buildings'
  - Keep relevant scenarios
OUTPUT: Reference table for emissions context
```

---

## Part 3: The Three Final Tables

### TABLE 1: `unified_sites.parquet`

**One row per municipal building. 4,268 rows × 48 columns.**
This is what the LLM scorer, dashboard, and scenario planner consume.

```
SCHEMA:
──────────────────────────────────────────────────────────────
IDENTITY (from E5 Solar Readiness — base table)
  site_id                    int       Auto-generated 0..4267
  site_name                  string    Building name
  address                    string    Street address
  borough                    string    Manhattan/Brooklyn/Queens/Bronx/Staten Island
  agency                     string    DOE, FDNY, DCAS, HPD, etc.
  bbl                        string    Borough-Block-Lot (10-digit)
  bin                        string    Building ID Number
  lat                        float     Latitude
  lon                        float     Longitude
  census_tract               string    Census tract ID
  community_district         int       Mapped from census tract or address
  is_env_justice             bool      Environmental Justice area flag

SOLAR (from E5)
  roof_condition             string    good / fair / poor / unknown
  roof_age_years             int       Years since last roof work (-1 if unknown)
  solar_production_kwh_yr    float     Estimated annual solar output
  solar_savings_usd_yr       float     Estimated annual solar savings
  upfront_solar_cost_usd     float     Estimated solar install cost

ENERGY CONSUMPTION (from E7 LL84 aggregate, joined on bbl or property_id)
  avg_monthly_elec_kwh       float     Average monthly electricity use
  avg_monthly_gas_kwh        float     Average monthly gas use
  avg_monthly_total_kwh      float     Total energy per month
  peak_monthly_elec_kwh      float     Maximum monthly electricity
  seasonality_index          float     std/mean of monthly elec (0=flat, >1=seasonal)
  months_reported            int       Data completeness indicator

ENERGY BENCHMARKING (from E10, joined on bbl)
  energy_star_score          int       0–100 ENERGY STAR rating (-1 if no data)
  site_eui                   float     Site Energy Use Intensity (kBTU/sqft)
  ghg_tons_co2e              float     Annual GHG emissions
  year_built                 int       Building construction year
  property_type              string    Office, School, Hospital, etc.

ENERGY COST (from E1, joined on bbl; from E3, joined on development_name)
  area_electric_savings_usd  float     ECSP electric savings in area
  avg_monthly_cost_usd       float     Average monthly electric bill
  annual_energy_cost_usd     float     Estimated annual cost (monthly × 12)
  max_peak_kw                float     Maximum recorded peak demand

EV INFRASTRUCTURE (from E4, spatial join: count within 500m, 1km)
  ev_ports_500m              int       EV charger ports within 500 meters
  ev_ports_1km               int       EV charger ports within 1 kilometer
  ev_stations_1km            int       EV stations within 1 kilometer
  nearest_ev_distance_m      float     Distance to closest EV station

DCAS ENRICHMENT (from E6, joined on bbl)
  dcas_annual_kwh            float     DCAS recorded annual energy (if match)

WASTE CONTEXT (from W1 district aggregates, joined on community_district)
  district_refuse_tons_mo    float     District monthly refuse tonnage
  district_recycling_tons_mo float     District monthly recycling tonnage
  district_organics_tons_mo  float     District monthly organics tonnage
  district_diversion_rate    float     District diversion rate (0–1)
  district_complaints        int       Total 311 DSNY complaints in district

COMPOSTING ACCESS (from W7, spatial join)
  compost_sites_1km          int       Food scrap drop-offs within 1 km
  nearest_compost_dist_m     float     Distance to nearest composting site

TRANSFER STATION (from W8, spatial join)
  nearest_transfer_stn       string    Name of nearest transfer station
  nearest_transfer_dist_km   float     Distance in km
  nearest_transfer_type      string    Type (Transfer Station / MTS / Rail)

COMPUTED SCORES (feature engineering)
  solar_score                float     Percentile rank of solar production (0–1)
  roof_score                 float     good=1.0, fair=0.6, poor=0.2
  equity_flag                float     1.0 if EJ area, 0.0 if not
  ev_density_score           float     Percentile rank of ev_ports_1km (0–1)
  energy_intensity_score     float     Percentile rank of avg_monthly_total_kwh (0–1)
  waste_burden_score         float     Percentile rank of district_refuse_tons (0–1)
──────────────────────────────────────────────────────────────
```

### TABLE 2: `district_waste.parquet`

**One row per community district. 59 rows × 35 columns.**
This feeds cuOpt routing, waste analysis, and the Waste view on dashboard.

```
SCHEMA:
──────────────────────────────────────────────────────────────
IDENTITY
  borough                    string
  community_district         int       1–18 depending on borough
  district_code              string    e.g., "BX01", "MN03"

WASTE VOLUME (from W1 aggregate)
  avg_monthly_refuse_tons    float
  avg_monthly_paper_tons     float
  avg_monthly_mgp_tons       float
  avg_monthly_organics_tons  float
  avg_monthly_total_tons     float
  diversion_rate             float     0–1
  tonnage_trend_slope        float     positive = growing, negative = declining

WASTE COMPOSITION (from W12, applied to district tonnage)
  est_organic_divertible_tons float    organics_pct × refuse_tons (not yet diverted)
  est_recyclable_missed_tons  float    recyclable_pct × refuse_tons
  est_energy_viable_tons      float    organic + paper with BTU value

311 COMPLAINTS (from W2 aggregate)
  total_complaints           int
  missed_collection_count    int
  overflow_count             int
  illegal_dumping_count      int
  avg_resolution_hours       float

INFRASTRUCTURE (from W3, W7, W8 spatial aggregates)
  litter_basket_count        int       Public trash cans in district
  compost_drop_off_count     int       Food scrap sites in district
  nearest_transfer_station   string    Name
  transfer_station_dist_km   float     Centroid-to-station distance

DISPOSAL CHAIN (from W6, W9, W10)
  disposal_vendor_refuse     string    Primary refuse vendor
  disposal_vendor_organics   string    Primary organics vendor
  disposal_site_type         string    Landfill / WTE / Recycling
  disposal_transport_mode    string    Truck / Rail / Barge
  disposal_miles             float     Miles to disposal site
  disposal_cost_per_ton      float

COMPUTED
  waste_intensity_score      float     Percentile rank of total_tons
  diversion_gap              float     target_rate (0.30) - actual_rate
  organic_energy_potential_kwh float   est_organic_divertible_tons × 500 kWh/ton
  collection_fuel_cost_est   float     Estimated based on truck-miles
──────────────────────────────────────────────────────────────
```

### TABLE 3: `time_series.parquet`

**Monthly energy readings for dispatch simulation. ~2.8M rows × 12 columns.**
This feeds the BESS dispatch simulator and waste forecast charts.

```
SCHEMA:
──────────────────────────────────────────────────────────────
  source                     string    'll84' or 'nycha_electric' or 'nycha_gas'
  property_id                string    LL84 property_id or NYCHA development_name
  borough                    string
  yyyy_mm                    string    '2024-01' format
  electricity_kwh            float     Monthly electricity consumption
  gas_kwh                    float     Monthly gas consumption (converted from kBTU/therms)
  total_energy_kwh           float     electricity + gas + fuel oil
  cost_usd                   float     Monthly charges (if available)
  peak_kw                    float     Peak demand kW (if available, else null)
──────────────────────────────────────────────────────────────

ROWS BREAKDOWN:
  LL84 monthly:       ~2,207,184 rows (2010-2025, ~18K properties)
  NYCHA electric:     ~553,666 rows
  NYCHA heating gas:  ~248,915 rows (deduplicated to avoid double-count)
  ─────────────────────────────
  TOTAL:              ~2,800,000 rows (after dedup)
```

---

## Part 4: Join Strategy — How Tables Connect

```
                  BUILDING LEVEL (exact match)
                  ════════════════════════════
                           BBL
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
   E5 Solar            E7/E10 LL84          E6 DCAS
   (base: 4,268)      (agg → bbl)          (55 buildings)
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    unified_sites.parquet
                            │
                   community_district
                            │
                  DISTRICT LEVEL (aggregate match)
                  ════════════════════════════════
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
   W1 Tonnage          W2 311 Complaints    W3/W7 Infra
   (59 districts)      (59 districts)       (basket/compost count)
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    district_waste.parquet
                            │
                    → also joined into unified_sites
                      via community_district


                  SPATIAL (nearest-neighbor)
                  ═════════════════════════
                        lat / lon
                            │
       ┌────────────────────┼────────────────────┐
       │                    │                    │
   E4 EV Stations      W7 Compost Sites     W8 Transfer Stns
   (within 500m/1km)   (within 1km)         (nearest)
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    → columns added to unified_sites
```

**Join order (Person 1 execution sequence):**

```python
# Step 1: Base table
sites = clean_solar_readiness()                    # 4,268 rows

# Step 2: Building-level joins (BBL)
ll84_agg = clean_ll84_monthly().groupby('bbl')     # aggregate
benchmarks = clean_ll84_benchmarking()              # latest year per bbl
dcas = clean_dcas_energy()                          # 55 rows
savings = clean_energy_savings().groupby('bbl')     # aggregate

sites = sites.merge(ll84_agg, on='bbl', how='left')
sites = sites.merge(benchmarks, on='bbl', how='left')
sites = sites.merge(dcas, on='bbl', how='left')
sites = sites.merge(savings, on='bbl', how='left')

# Step 3: Spatial joins (cuSpatial on GPU)
ev_stations = clean_ev_stations()
sites['ev_ports_500m'] = count_within_radius(sites, ev_stations, 500)
sites['ev_ports_1km'] = count_within_radius(sites, ev_stations, 1000)

compost = clean_food_scrap_dropoffs()
sites['compost_sites_1km'] = count_within_radius(sites, compost, 1000)

transfer = clean_disposal_facilities()
sites['nearest_transfer_stn'] = find_nearest(sites, transfer)

# Step 4: District-level joins
districts = build_district_waste_table()            # 59 rows
sites = sites.merge(
    districts[['community_district', 'avg_monthly_refuse_tons', ...]],
    on='community_district', how='left'
)

# Step 5: Compute scores
sites['solar_score'] = sites['solar_production_kwh_yr'].rank(pct=True)
sites['roof_score'] = sites['roof_condition'].map({'good':1, 'fair':0.6, 'poor':0.2})
# ... etc

# Step 6: Save
sites.to_parquet('data/processed/unified_sites.parquet')
districts.to_parquet('data/processed/district_waste.parquet')
time_series.to_parquet('data/processed/time_series.parquet')
```

---

## Part 5: What Each Downstream System Reads

```
┌───────────────────────────────────────────────────────────────┐
│  DOWNSTREAM CONSUMER         READS              ROWS × COLS  │
├───────────────────────────────────────────────────────────────┤
│  LLM Scorer (NIM)            unified_sites       4,268 × 48  │
│    → batches of 20 rows, subset of columns                    │
│    → sends: site_id, address, borough, all scores + features  │
│    → returns: bess_score, waste_score, nexus_score, reason    │
│                                                               │
│  Dispatch Simulator          unified_sites       top 50 sites │
│                              time_series         filtered     │
│    → reads site's avg demand, solar capacity, EV proximity    │
│    → reads monthly consumption history for demand curve shape  │
│    → returns: 24h schedule, annual savings, CO₂ offset        │
│                                                               │
│  cuOpt Route Optimizer       district_waste      59 districts │
│                              disposal_facilities  39 facilities│
│    → reads: district centroids, tonnage, station locations     │
│    → returns: optimized district→station assignments           │
│                                                               │
│  Dashboard (Streamlit)       unified_sites       4,268 × 48  │
│                              district_waste      59 × 35     │
│                              LLM scores          4,268 × 5   │
│                              dispatch results    50 sites     │
│                              cuOpt results       59 routes    │
│    → reads everything, renders map + charts + tables          │
│                                                               │
│  Scenario Planner            unified_sites (with scores)      │
│                              district_waste                   │
│    → reads scores + features, applies slider weights          │
│    → recalculates ranking + budget allocation client-side     │
└───────────────────────────────────────────────────────────────┘
```

---

## Part 6: GB10 Memory Budget

```
ON THE GB10 (128 GB UNIFIED MEMORY):

  unified_sites.parquet     4,268 × 48 cols     →  ~15 MB in cuDF
  district_waste.parquet    59 × 35 cols         →  ~0.1 MB in cuDF
  time_series.parquet       2.8M × 12 cols       →  ~800 MB in cuDF
  
  Raw datasets (kept for reference):
  - LL84 monthly (2.2M rows)                     →  ~3 GB in cuDF
  - 311 DSNY (2.4M rows)                         →  ~4 GB in cuDF
  - All others combined                          →  ~0.5 GB in cuDF
  
  TOTAL DATA IN GPU MEMORY:                      →  ~8.5 GB
  
  LLM (Llama 3.1 8B quantized):                  →  ~8–16 GB
  cuOpt solver workspace:                         →  ~2 GB
  Streamlit + plotting:                           →  ~1 GB
  ───────────────────────────────────────────────
  TOTAL:                                          →  ~20–28 GB
  REMAINING:                                      →  ~100 GB free
  
  → Plenty of headroom. No swapping needed.
```

---

## Part 7: Person 1 Execution Checklist

```
FRIDAY EVENING
  [ ] Download all 25 datasets via Socrata API (data_ingestion.py)
  [ ] Verify row counts match expected
  [ ] Load LL84 (2.2M rows) into cuDF — confirm GPU acceleration works
  [ ] Run unit conversions on E3, E7, E8, E9 (kBTU/therms/MMBTU → kWh)
  [ ] Clean E5 (solar readiness) — this is the base table, get it right
  [ ] Clean E4 (EV stations) — need clean lat/lon for spatial joins

FRIDAY NIGHT
  [ ] Clean remaining energy datasets (E1, E2, E6, E10, E11, E12)
  [ ] Clean waste datasets (W1, W2, W3, W7, W8, W9, W10, W11, W12, W13)
  [ ] Build community_district mapping for E5 sites (from census_tract or geocode)
  [ ] Aggregate E3, E7, E8 into per-site summaries
  [ ] Aggregate W1, W2 into per-district summaries

SATURDAY MORNING
  [ ] Build BBL joins: E5 + E7_agg + E10 + E6 + E1
  [ ] Build spatial joins with cuSpatial: EV proximity, compost proximity, transfer proximity
  [ ] Build district joins: site table + W1/W2 district aggregates
  [ ] Compute all derived scores (solar_score, roof_score, equity_flag, etc.)
  [ ] Save TABLE 1: unified_sites.parquet — verify 4,268 rows × 48 cols
  [ ] Save TABLE 2: district_waste.parquet — verify 59 rows × 35 cols
  [ ] Save TABLE 3: time_series.parquet — verify ~2.8M rows × 12 cols
  [ ] Run cuDF vs pandas benchmark on LL84 — record numbers

SATURDAY AFTERNOON
  [ ] Hand off parquet files to Person 2 (LLM scoring) and Person 3 (dashboard)
  [ ] Prep cuOpt input: district centroids + tonnage + station locations + capacities
  [ ] Help Person 2 debug any data issues in LLM scoring pipeline
  [ ] Spot-check: sample 10 random sites, manually verify all joined fields make sense

DONE WHEN:
  [ ] All 3 parquet files are on disk and loadable in cuDF
  [ ] Person 2 confirms LLM scorer runs without data errors
  [ ] Person 3 confirms dashboard renders data correctly
  [ ] Benchmark numbers recorded for Spark Story
```
