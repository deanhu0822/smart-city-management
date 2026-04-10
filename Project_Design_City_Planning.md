# NYC Smart City Nexus — Energy, Utility, Waste: A Holistic System

> **Hackathon:** [The Spark Hack NYC 2026](https://luma.com/spark-hack-nyc?tk=s5GaSK) · April 10–12
> **Track:** Environmental Impact
> **Hardware:** Acer Veriton GN100 / NVIDIA GB10 (128 GB, 1 PFLOP FP4)
> **Evolution:** Expands BESS Predictor (v1) into a full urban energy–waste intelligence platform

---

## 1. Vision

NYC generates **14M tons of waste/year** and consumes **~52 TWh of electricity/year**. These two systems are treated as separate problems — but they're deeply connected:

- **Waste → Energy:** Organic waste (3.5M tons/yr) can be anaerobically digested into biogas. Waste-to-energy plants already process ~20% of NYC's residential waste.
- **Energy → Waste cost:** Energy prices drive collection truck fuel costs, transfer station operations, and refrigerated waste transport.
- **Storage bridges both:** BESS smooths renewable generation; waste-derived biogas can be stored and dispatched like any fuel.

**This project models the full loop:** generation → consumption → fluctuation → storage → retail optimization → waste tracking → waste-to-energy recovery → back to generation.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NYC SMART CITY NEXUS                         │
├──────────────────┬──────────────────┬───────────────────────────────┤
│   ENERGY LAYER   │   WASTE LAYER    │      NEXUS (crossover)       │
│                  │                  │                               │
│ • Generation     │ • Collection     │ • Waste-to-Energy potential   │
│ • Grid demand    │ • Transfer       │ • Biogas → grid injection     │
│ • Solar/DER      │ • Disposal flow  │ • Collection route × energy   │
│ • BESS storage   │ • Recycling rate │ • Organic diversion → AD      │
│ • Retail pricing │ • Composition    │ • Carbon accounting (unified) │
│ • EV charging    │ • Complaints     │ • Equity overlay              │
└──────────────────┴──────────────────┴───────────────────────────────┘
         │                    │                      │
         ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM ANALYSIS ENGINE                             │
│         (Claude API / Gemini API → migrate to GB10 local)           │
│                                                                     │
│  • Site scoring & ranking    • Dispatch optimization                │
│  • Waste flow prediction     • Natural language insights            │
│  • Scenario simulation       • Cross-domain recommendations        │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     INTERACTIVE DASHBOARD                           │
│            (Streamlit + React artifact for demo)                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Sources — Complete Inventory

### 3A. Energy Layer (7 original + 5 new)

| # | Dataset | ID | Rows | What It Tells You |
|---|---------|-----|------|-------------------|
| E1 | Energy Cost Savings Program | `bug8-9f3g` | 2,363 | Where businesses save on energy — cost burden geography |
| E2 | Projected Citywide Energy Cost | `tyv9-j3ti` | 290 | Where energy prices are headed by fiscal year |
| E3 | Electric Consumption & Cost (NYCHA) | `jr24-e7cr` | 553,666 | Monthly kWh + peak kW per housing development |
| E4 | NYC EV Fleet Station Network | `fc53-9hrv` | 1,638 | EV charger locations, types, port counts — future load growth |
| E5 | Municipal Solar-Readiness (LL24) | `cfz5-6fvh` | 4,268 | Solar potential per city building — roof condition, production est. |
| E6 | DCAS Building Energy Usage | `ubdi-jgw2` | 55 | Baseline energy for city-managed facilities |
| E7 | LL84 Monthly Energy Data | `fvp3-gcb2` | 2,207,184 | Monthly electricity + gas for all large buildings |
| **E8** | **Heating Gas (NYCHA)** | `it56-eyq4` | 248,915 | Monthly gas therms — seasonal heating demand |
| **E9** | **Cooking Gas (NYCHA)** | `avhb-5jhc` | 704,175 | Cooking gas demand — baseline load profile |
| **E10** | **LL84 Annual Benchmarking** | `5zyy-y8am` | large | ENERGY STAR score, EUI, GHG per building with BBL |
| **E11** | **Natural Gas by ZIP** | `uedp-fegm` | 1,015 | ZIP-level gas consumption by building type |
| **E12** | **GHG Emissions Inventory** | `wq7q-htne` | 85 | Citywide emissions by sector including waste + energy |

### 3B. Waste Layer (13 datasets — all new)

| # | Dataset | ID | Rows | What It Tells You |
|---|---------|-----|------|-------------------|
| W1 | DSNY Monthly Tonnage | `ebb7-mvp5` | 24,883 | Refuse + recycling + organics tons by community district by month |
| W2 | 311 Requests (DSNY filter) | `erm2-nwe9` | ~2.4M | Missed pickups, overflowing bins, illegal dumping — geocoded |
| W3 | Litter Basket Inventory | `8znf-7b2c` | 20,413 | Every public trash can — location, type, section |
| W4 | DSNY Collection Frequencies | `rv63-53db` | geo | Collection zone boundaries + pickup schedules |
| W5 | DSNY Sections (Boundaries) | `7vgu-qbur` | geo | District section shapefiles for spatial joins |
| W6 | Disposal Vendor Assignments | `fpv2-r9br` | geo | Which vendor handles each waste stream per district |
| W7 | Food Scrap Drop-Off Locations | `if26-z6xq` | 591 | Community composting sites — location, hours, host |
| W8 | Disposal Facility Locations | `ufxk-pq9j` | 39 | Transfer stations, marine terminals, rail yards — geolocated |
| W9 | Disposal Facilities by Year | `6r9j-qrwz` | 103 | Cost/ton, capacity, actual tonnage delivered per year |
| W10 | Disposal Sites by Facility | `99xv-he3n` | 211 | Full chain: facility → disposal site, transport mode, miles |
| W11 | Trade Waste Haulers | `867j-5pgi` | 680,452 | Licensed private haulers — recycling + organics capability |
| W12 | Waste Characterization (Main) | `bpea-2i5q` | 2,112 | What's in the trash — material composition percentages |
| W13 | Climate Budget Emissions Forecast | `czei-7bxd` | — | Future emissions by sector including waste |

---

## 4. Analysis Pipeline — How Data Becomes Insight

### 4A. Energy Analysis

```
Raw Data (E1–E12)
    │
    ▼
┌─────────────────────────────────┐
│ STAGE 1: Demand Profiling       │
│                                 │
│ • Merge LL84 monthly (E7) +     │
│   NYCHA electric (E3) + gas     │
│   (E8, E9) by BBL/address      │
│ • Build 24h load curves per     │
│   building type (office,        │
│   school, hospital, housing)    │
│ • Identify peak/off-peak        │
│   demand ratios + seasonality   │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ STAGE 2: Supply Modeling        │
│                                 │
│ • Solar generation curves from  │
│   LL24 solar readiness (E5)     │
│ • EV charging load overlay      │
│   from station network (E4)     │
│ • Grid price forecast from      │
│   projected cost (E2)           │
│ • Retail rate structure          │
│   (ConEd TOU + ESCO rates)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ STAGE 3: Storage Optimization   │
│                                 │
│ • BESS sizing per site          │
│   (capacity kWh, power kW)     │
│ • Charge/discharge scheduling   │
│   (peak shaving + solar shift)  │
│ • Payback period estimation     │
│ • Fleet-level portfolio:        │
│   "If $10M budget, where?"     │
└─────────────────────────────────┘
```

### 4B. Waste Analysis

```
Raw Data (W1–W13)
    │
    ▼
┌─────────────────────────────────┐
│ STAGE 1: Volume & Flow Mapping  │
│                                 │
│ • Monthly tonnage (W1) by       │
│   community district → time     │
│   series per borough            │
│ • 311 complaints (W2) →         │
│   hotspot heatmap of service    │
│   failures + illegal dumping    │
│ • Litter baskets (W3) →         │
│   coverage density analysis     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ STAGE 2: Disposal Chain         │
│                                 │
│ • Facility locations (W8) +     │
│   vendor assignments (W6) →     │
│   origin-destination matrix     │
│ • Disposal sites (W10) →        │
│   transport mode (truck/rail/   │
│   barge), distance, cost/ton    │
│ • Waste composition (W12) →     │
│   what % is recyclable,         │
│   compostable, energy-viable    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ STAGE 3: Optimization           │
│                                 │
│ • Route optimization: minimize  │
│   truck-miles using tonnage +   │
│   311 patterns + frequencies    │
│ • Diversion targeting: which    │
│   districts have highest        │
│   organic waste + lowest        │
│   composting participation?     │
│ • Transfer station load         │
│   balancing across the city     │
└─────────────────────────────────┘
```

### 4C. Nexus Analysis (Energy × Waste Crossover)

```
Energy Stage 3 output + Waste Stage 3 output
    │
    ▼
┌──────────────────────────────────────────┐
│ NEXUS STAGE: Cross-Domain Intelligence   │
│                                          │
│ 1. WASTE-TO-ENERGY POTENTIAL             │
│    • Waste composition (W12): organic    │
│      fraction × BTU content → estimated  │
│      energy yield per ton                │
│    • Map organic waste volume (W1) to    │
│      nearest AD facility or biogas       │
│      injection point                     │
│    • Model: if X% more organics diverted │
│      to AD → Y MWh of biogas generated   │
│                                          │
│ 2. CARBON ACCOUNTING                     │
│    • Energy GHG (E12) + waste GHG (W13)  │
│      → unified carbon budget per         │
│      community district                  │
│    • BESS + solar offsets vs. waste       │
│      diversion offsets → combined CO₂    │
│      reduction per dollar invested       │
│                                          │
│ 3. COLLECTION ENERGY COST                │
│    • DSNY truck routes × fuel cost ×     │
│      distance to disposal sites (W10)    │
│    • Electrification opportunity: which  │
│      DSNY depots + routes could switch   │
│      to electric trucks, supported by    │
│      depot-level BESS?                   │
│                                          │
│ 4. EQUITY OVERLAY                        │
│    • Environmental justice areas (E5)    │
│      cross-referenced with:              │
│      - Waste complaint density (W2)      │
│      - Energy cost burden (E1)           │
│      - Proximity to transfer stations    │
│    • "Equity Score" per district         │
│                                          │
│ 5. SCENARIO SIMULATOR                    │
│    • Input: budget, policy levers        │
│    • Output: optimal allocation across   │
│      BESS, solar, organics diversion,    │
│      route optimization                  │
└──────────────────────────────────────────┘
```

### 4D. LLM Analysis Engine

The LLM (Claude API / Gemini → later local on GB10) performs three roles:

| Role | Input | Output | Why LLM? |
|------|-------|--------|-----------|
| **Scorer** | Site features (energy + waste + equity) | Priority score 0–100 + natural language justification | Weighs multi-dimensional tradeoffs that simple formulas can't capture |
| **Advisor** | Selected site profile + scenario params | Dispatch schedule, diversion strategy, implementation roadmap | Generates actionable, human-readable recommendations |
| **Narrator** | Dashboard state + user query | Plain-English insight ("Bronx District 7 has 3x the organics waste of Manhattan District 1 but zero composting sites within 2 miles") | Makes data accessible to non-technical city planners |

**Batch scoring prompt structure:**
```
System: You are an urban sustainability analyst for NYC. Score each site
        on BESS priority AND waste-to-energy opportunity. Consider energy
        demand, solar potential, organic waste volume, equity impact, and
        EV infrastructure. Return JSON with scores and reasoning.

User:   [batch of 20 site profiles with merged energy + waste features]
```

---

## 5. Dashboard UI — Detailed Design

### 5.1 Overall Layout

```
┌──────────────┬──────────────────────────────────────────────────────┐
│              │  ┌─ HEADER ─────────────────────────────────────┐    │
│   SIDEBAR    │  │ NYC Smart City Nexus    [Energy][Waste][Nexus]│   │
│              │  └──────────────────────────────────────────────┘    │
│  Navigation  │                                                      │
│  Filters     │  ┌─ KPI RIBBON ────────────────────────────────┐    │
│  Layer       │  │  [4 energy KPIs]  |  [4 waste KPIs]         │    │
│  Toggles     │  └──────────────────────────────────────────────┘    │
│              │                                                      │
│              │  ┌─ MAP ──────────┬─ RANKINGS TABLE ───────────┐    │
│              │  │                │                             │    │
│              │  │  NYC 5-borough │  Sortable ranked list       │    │
│              │  │  map with      │  of sites with scores       │    │
│              │  │  dual layers   │                             │    │
│              │  └────────────────┴─────────────────────────────┘    │
│              │                                                      │
│              │  ┌─ SITE DETAIL ───────────────────────────────┐    │
│              │  │  Energy profile | Waste profile | BESS rec   │    │
│              │  └──────────────────────────────────────────────┘    │
│              │                                                      │
│              │  ┌─ FLOW DIAGRAMS ─────────────────────────────┐    │
│              │  │  Energy Sankey | Waste Sankey | Carbon view  │    │
│              │  └──────────────────────────────────────────────┘    │
│              │                                                      │
│              │  ┌─ SIMULATION ────────────────────────────────┐    │
│              │  │  Dispatch chart | Waste forecast | Scenario  │    │
│              │  └──────────────────────────────────────────────┘    │
└──────────────┴──────────────────────────────────────────────────────┘
```

### 5.2 Three View Modes (Tab Switcher in Header)

Users toggle between **Energy**, **Waste**, and **Nexus** views. Each view reshapes the same layout with different data:

---

### 5.3 KPI Ribbon — 8 Cards (4 Energy + 4 Waste)

#### Energy KPIs

| Card | Value | Subtitle |
|------|-------|----------|
| 🔋 BESS High-Priority Sites | **847** | Score ≥ 70 out of 4,268 analyzed |
| ⚡ Peak Demand Reducible | **142 MW** | If top 50 sites deploy BESS |
| 💰 Annual Savings Potential | **$12.4M** | Across top 50 BESS deployments |
| 🌱 CO₂ Offset (Energy) | **8,240 tons/yr** | ≈ 1,790 cars removed |

#### Waste KPIs

| Card | Value | Subtitle |
|------|-------|----------|
| 🗑️ Monthly Refuse Collected | **295K tons** | Citywide, latest month |
| ♻️ Diversion Rate | **21.3%** | Recycling + organics (target: 30%) |
| 🚛 Disposal Cost | **$418/ton avg** | Across all facilities |
| 🔥 Waste-to-Energy Potential | **1.2M MWh/yr** | If 50% organics → AD |

---

### 5.4 Interactive Map — Dual Layer

The map is the centerpiece. Two toggleable layers on the same NYC map:

**Layer 1: Energy (blue palette)**
- Dots for each municipal site, sized by energy consumption, colored by BESS priority score
- Solar potential overlay (yellow heat patches)
- EV station markers (green lightning bolts)

**Layer 2: Waste (orange palette)**
- Community districts shaded by monthly tonnage (choropleth)
- Transfer station locations (large squares)
- 311 complaint hotspots (red heat overlay)
- Litter basket density (small dots)
- Waste flow arrows: district → transfer station → disposal site (animated Sankey on map)

**Layer 3: Nexus (purple overlay, shown in Nexus tab)**
- Environmental justice areas highlighted
- Sites where energy + waste opportunity overlap (e.g., high energy building near organic waste hotspot = AD + BESS combo candidate)
- Carbon intensity per district (unified energy + waste GHG)

**Map interactions:**
- Click a district → filter all panels below to that district
- Click a site → open Site Detail Panel
- Hover a waste flow arrow → show tons/month, transport mode, cost, miles

---

### 5.5 Rankings Table (Right of Map)

Columns change by view mode:

**Energy view:**
| Rank | Site | Borough | BESS Score | Solar | Equity | Savings/yr |
|------|------|---------|------------|-------|--------|------------|

**Waste view:**
| Rank | District | Borough | Refuse tons/mo | Diversion % | Complaints | Organic Potential |
|------|----------|---------|----------------|-------------|------------|-------------------|

**Nexus view:**
| Rank | Site/District | Borough | Energy Score | Waste Score | Combined | CO₂ Impact |
|------|---------------|---------|--------------|-------------|----------|------------|

---

### 5.6 Site Detail Panel (Expands on Row Click)

Three-column layout:

```
┌─────────────────┬──────────────────┬──────────────────────────┐
│  IDENTITY       │  ENERGY PROFILE  │  WASTE PROFILE           │
│                 │                  │                          │
│  Name           │  Avg kWh/month   │  District tonnage/month  │
│  Address        │  Peak kW         │  Waste composition pie   │
│  Agency         │  Annual cost     │  Recycling rate          │
│  Borough        │  Solar potential  │  311 complaints nearby   │
│  Equity zone    │  Roof condition   │  Nearest transfer stn    │
│  BBL            │  EV ports nearby  │  Disposal vendor         │
│                 │                  │                          │
├─────────────────┴──────────────────┴──────────────────────────┤
│  LLM INSIGHT (natural language)                               │
│                                                               │
│  "This Bronx school site has the 3rd highest energy cost in   │
│   the borough, sits in an Environmental Justice area, and is  │
│   2 blocks from a district producing 1,200 tons/month of      │
│   organic waste with no nearby composting site. Recommended:  │
│   500 kWh BESS + partnership with local AD facility for       │
│   biogas generation. Combined CO₂ offset: 89 tons/yr."       │
└───────────────────────────────────────────────────────────────┘
```

---

### 5.7 Flow Diagrams — Sankey Charts (Full Width Section)

Two side-by-side Sankey diagrams:

#### Energy Sankey (left)
```
Generation Sources          Consumption Sectors         End Use
─────────────────          ────────────────────        ────────
Grid (ConEd) ─────────┬──→ Commercial ──────────┬──→ Lighting
Solar (rooftop) ──────┤                         ├──→ HVAC
Biogas (AD) ──────────┤   Residential ──────────┤   Appliances
Wind (imported) ──────┤                         ├──→ EV Charging
                      ├──→ Municipal ───────────┤
                      │                         └──→ BESS Storage
                      └──→ Industrial
```
- Width of each flow = MWh
- Color: source-coded (grid=gray, solar=yellow, biogas=green)
- Interactive: hover to see exact MWh + % of total

#### Waste Sankey (right)
```
Generation              Collection          Processing         Destination
──────────             ──────────          ──────────         ───────────
Residential ──────┬──→ DSNY Trucks ──┬──→ Transfer Stn ──┬──→ Landfill (55%)
Commercial ───────┤                  │                    ├──→ WTE Plant (22%)
Institutional ────┤   Private Carters┤   MTS (Marine) ───┤   Recycling (18%)
                  │                  │                    └──→ Composting (5%)
                  └──→ Drop-off ─────┘
```
- Width = tons/month
- Color: destination-coded (landfill=red, WTE=orange, recycling=blue, compost=green)
- Animated flow particles showing direction

---

### 5.8 Simulation Section (Full Width, Tabbed)

Three tabs:

#### Tab 1: BESS Dispatch (from v1)
- 24-hour stacked area chart: building demand + solar + BESS discharge
- Battery SOC line chart
- Summary metrics: daily savings, peak shaved, CO₂ offset

#### Tab 2: Waste Flow Forecast
```
┌─────────────────────────────────┬─────────────────────────────────┐
│  TONNAGE FORECAST (Line Chart)  │  DIVERSION SCENARIO (Bar Chart) │
│                                 │                                 │
│  X: Month (12-month forecast)   │  X: Waste type (organic, paper, │
│  Y: Tons/month                  │     plastic, metal, glass)      │
│  Lines:                         │  Bars:                          │
│   - Refuse (declining trend)    │   - Current diversion %         │
│   - Recycling (growing)         │   - Target diversion %          │
│   - Organics (growing fast)     │   - Gap (red highlight)         │
│   - Total (stable)              │                                 │
│                                 │  Annotation: "Closing the       │
│                                 │  organics gap = 45K MWh/yr      │
│                                 │  of biogas potential"           │
└─────────────────────────────────┴─────────────────────────────────┘
```

#### Tab 3: Scenario Planner (the crown jewel)
Interactive "what-if" simulator with sliders and real-time output:

**Input sliders:**
| Slider | Range | Default |
|--------|-------|---------|
| Total budget ($M) | 1–50 | 10 |
| % allocated to BESS | 0–100% | 40% |
| % allocated to solar | 0–100% | 25% |
| % allocated to organics diversion | 0–100% | 20% |
| % allocated to route optimization | 0–100% | 15% |
| Equity weighting | 0–1 | 0.3 |

**Output (updates in real-time as sliders move):**
```
┌──────────────────────────────────────────────────────────────┐
│  WITH $10M BUDGET (40% BESS / 25% Solar / 20% Organics):   │
│                                                              │
│  🔋 BESS: Deploy at 32 sites → save $4.8M/yr, shave 89 MW  │
│  ☀️ Solar: Install on 18 rooftops → 12.4 GWh/yr generation  │
│  🌱 Organics: Divert 45K tons → 22K MWh biogas + 3.2K t CO₂│
│  🚛 Routes: Optimize 14 districts → save $1.1M/yr fuel     │
│                                                              │
│  ═══════════════════════════════════════════════════════      │
│  TOTAL IMPACT:                                               │
│  • Annual savings: $7.3M    • CO₂ offset: 12,400 tons/yr   │
│  • Payback period: 1.4 years • Equity coverage: 68% of EJ  │
│  ═══════════════════════════════════════════════════════      │
│                                                              │
│  [📊 View site-by-site breakdown]  [📄 Export report (PDF)]  │
└──────────────────────────────────────────────────────────────┘
```

Below the summary, a **ranked allocation table** shows exactly which sites/districts get investment:

| Priority | Action | Location | Investment | Annual Return | CO₂ | Equity |
|----------|--------|----------|------------|---------------|-----|--------|
| 1 | BESS 750kWh | PS 123, Bronx | $340K | $287K/yr | 42t | ✅ EJ |
| 2 | Solar 200kW | Navy Yard, BK | $480K | $198K/yr | 67t | — |
| 3 | Organics AD | District 7, BX | $220K | $165K/yr | 38t | ✅ EJ |
| ... | ... | ... | ... | ... | ... | ... |

---

### 5.9 Borough Comparison (Bottom Section)

Horizontal grouped bar chart — each borough gets a cluster of bars:

| Metric | Bar Color |
|--------|-----------|
| Energy consumption (MWh/yr) | Blue |
| BESS savings potential ($/yr) | Green |
| Waste tonnage (tons/month) | Orange |
| Diversion rate (%) | Teal |
| 311 complaints (count/month) | Red |

Below: 5 borough summary cards (one per borough), each showing:
- Top recommended action (BESS site / organics program / route change)
- Estimated impact
- Equity score

---

## 6. Data Model — Key Joins

```
                    ┌──────────────┐
                    │   BBL / BIN  │  (Building-level key)
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │ Solar (E5) │  │ LL84 (E7)   │  │ Benchmrk    │
    │ 4,268 bldg │  │ 2.2M rows   │  │ (E10)       │
    └────────────┘  └─────────────┘  └─────────────┘

                    ┌──────────────┐
                    │ Comm District│  (District-level key)
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │ Tonnage    │  │ 311 (W2)    │  │ Collection  │
    │ (W1)       │  │ complaints  │  │ Freq (W4)   │
    └────────────┘  └─────────────┘  └─────────────┘

                    ┌──────────────┐
                    │  Lat / Lon   │  (Spatial proximity join)
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
    │ EV Stations│  │ Litter      │  │ Transfer    │
    │ (E4)       │  │ Baskets(W3) │  │ Stns (W8)   │
    └────────────┘  └─────────────┘  └─────────────┘
```

Three join strategies:
1. **BBL (Borough-Block-Lot):** Exact building match for energy datasets
2. **Community District:** Aggregate match for waste tonnage + 311 + collection data
3. **Spatial proximity (lat/lon):** Nearest-neighbor for EV stations, litter baskets, transfer stations (radius-based: 500m / 1km / 2km)

---

## 7. LLM Prompt Templates

### 7.1 Unified Site Scoring
```
System: You are a NYC urban sustainability analyst. For each site, produce:
  1. energy_score (0-100): BESS deployment priority
  2. waste_score (0-100): waste optimization opportunity
  3. nexus_score (0-100): cross-domain synergy potential
  4. top_recommendation: single best action for this site
  5. reasoning: 2-3 sentences explaining the scores

Weigh: energy cost reduction ({w1}), grid resilience ({w2}),
solar synergy ({w3}), equity ({w4}), EV support ({w5}),
waste diversion potential ({w6}), WTE opportunity ({w7}).
```

### 7.2 District Waste Narrative
```
System: You are a waste management consultant for NYC. Given a community
district's waste data (tonnage trends, composition, complaints, disposal
chain), write a 100-word insight paragraph explaining:
  - Key trends (improving or worsening?)
  - Biggest opportunity (recycling, organics, route optimization?)
  - Estimated impact if opportunity is captured
  - Any equity concerns
```

### 7.3 Scenario Evaluation
```
System: Given a budget allocation scenario across BESS, solar, organics
diversion, and route optimization, calculate:
  - Site-by-site deployment plan (ranked by ROI)
  - Aggregate annual savings, CO₂ offset, equity coverage
  - Payback period
  - Risk factors and dependencies
Return as structured JSON + 3-sentence executive summary.
```

---

## 8. Implementation Timeline (48-Hour Hackathon)

| Time Block | Duration | Deliverable |
|------------|----------|-------------|
| Fri 6–10 PM | 4h | Download all 25 datasets, clean, establish join keys |
| Fri 10 PM–Sat 2 AM | 4h | Feature engineering: unified site table + district waste table |
| Sat 8 AM–12 PM | 4h | LLM scoring pipeline (cloud): score all sites energy + waste + nexus |
| Sat 12–4 PM | 4h | Dispatch simulator + waste flow model + scenario engine |
| Sat 4–10 PM | 6h | Dashboard: map, KPIs, rankings, site detail, Sankey charts |
| Sat 10 PM–Sun 8 AM | buffer | Polish, fix bugs, edge cases |
| Sun 8 AM–12 PM | 4h | Simulation tab, scenario planner, borough comparison |
| Sun 12–3 PM | 3h | Demo prep, narrative, backup screenshots |
| **Sun 4 PM** | — | **Hack Fair presentation** |

---

## 9. Key Differentiators for Judging

| Criteria | How We Win |
|----------|-----------|
| **On-device** | Full pipeline runs on GB10 — data processing, model inference, dashboard serving |
| **Environmental Impact** | Unified energy + waste system, not just one silo |
| **NYC Open Data** | 25 official datasets merged — deepest data integration in the competition |
| **Actionable** | Scenario planner outputs a specific deployment plan with dollar amounts |
| **Equity** | Environmental Justice overlay on every recommendation |
| **Novel insight** | Waste-to-energy nexus: connecting organic waste to biogas to grid to BESS — nobody else will model this full loop |
