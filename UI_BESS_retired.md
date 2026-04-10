# BESS Predictor for NYC — UI Specification

> **Purpose:** Paste this document into Claude.ai and ask it to render a React artifact that serves as the interactive dashboard for the BESS Predictor project.

---

## Prompt for Claude Web

```
Build a single-page React dashboard based on the spec below. Use Tailwind CSS for styling. Use recharts for charts. Use a dark theme with electric blue (#3B82F6) and emerald green (#10B981) as accent colors. Make it look like a professional energy management control center. All data should be hardcoded as realistic mock data based on real NYC municipal buildings.
```

---

## App Layout

The dashboard is a single-page app with a fixed left sidebar and a scrollable main content area.

```
┌──────────────┬──────────────────────────────────────────────────┐
│              │  HEADER BAR                                      │
│   SIDEBAR    ├──────────────────────────────────────────────────┤
│              │                                                  │
│  - Logo      │  MAIN CONTENT (scrollable)                      │
│  - Nav       │                                                  │
│  - Filters   │  Section 1: KPI Cards                           │
│              │  Section 2: Map Placeholder + Rankings Table     │
│              │  Section 3: Site Detail Panel                    │
│              │  Section 4: Dispatch Simulation Chart            │
│              │  Section 5: Borough Comparison                   │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Sidebar (fixed, 240px wide, dark background #0F172A)

- **Logo area:** Text "⚡ BESS Predictor" in bold white, subtitle "NYC Energy Storage Intelligence" in gray
- **Navigation links** (vertical, icon + text):
  - 📊 Dashboard (active by default)
  - 🗺️ Site Map
  - 📋 Rankings
  - ⚙️ Settings
- **Filter controls** (below nav, in a bordered section labeled "FILTERS"):
  - **Borough dropdown:** All, Manhattan, Brooklyn, Queens, Bronx, Staten Island
  - **Min BESS Score slider:** 0–100, default 0
  - **Priority weights** — five small sliders (0–1 each, step 0.05):
    - Energy Cost Reduction (default 0.25)
    - Grid Resilience (default 0.20)
    - Solar Synergy (default 0.20)
    - Equity Impact (default 0.20)
    - EV Infrastructure (default 0.15)
  - **"Apply Filters" button** (blue)

---

### 2. Header Bar (h-16, dark #1E293B, sticky top)

- Left: Breadcrumb "Dashboard > BESS Site Analysis"
- Center: Nothing
- Right: Badge showing "Provider: Claude API" in a small blue pill, a green dot with "Pipeline: Complete", and text "Last run: Apr 10, 2026 2:34 PM"

---

### 3. Section 1 — KPI Summary Cards (4 cards in a row)

Four cards in a horizontal grid, each with an icon, big number, label, and small trend indicator.

| Card | Icon | Value | Label | Trend |
|------|------|-------|-------|-------|
| 1 | 🏢 | 4,268 | Sites Analyzed | — |
| 2 | 🔋 | 847 | High-Priority Sites (score ≥ 70) | ▲ 19.8% of total |
| 3 | 💰 | $12.4M | Estimated Annual Savings | if top 50 sites deployed |
| 4 | 🌱 | 8,240 | Tons CO₂ Offset/Year | equivalent to 1,790 cars |

Card style: rounded corners, subtle border, dark background (#1E293B), big number in white, label in gray, trend in green.

---

### 4. Section 2 — Rankings Table + Map Placeholder (two-column layout, 60/40 split)

#### Left (60%): Top Sites Ranking Table

A sortable table with the top 20 sites. Columns:

| Rank | Site Name | Borough | BESS Score | Solar Score | Equity Zone | Recommended kWh | Est. Savings/yr |
|------|-----------|---------|------------|-------------|-------------|-----------------|-----------------|

Use this mock data (10 rows minimum):

```
1  | PS 123 School Complex        | Bronx      | 94 | 0.92 | ✅ Yes | 750 kWh  | $287,000
2  | FDNY Engine 42 Station       | Bronx      | 91 | 0.88 | ✅ Yes | 500 kWh  | $243,000
3  | Brooklyn Navy Yard Bldg 77   | Brooklyn   | 89 | 0.85 | ❌ No  | 1000 kWh | $312,000
4  | Queens Central Library       | Queens     | 87 | 0.78 | ✅ Yes | 600 kWh  | $198,000
5  | Bronx County Courthouse      | Bronx      | 85 | 0.72 | ✅ Yes | 800 kWh  | $265,000
6  | Staten Island Borough Hall   | Staten Is. | 83 | 0.81 | ❌ No  | 450 kWh  | $176,000
7  | Manhattan Civic Center       | Manhattan  | 82 | 0.65 | ❌ No  | 900 kWh  | $298,000
8  | Jamaica HVAC Center          | Queens     | 80 | 0.77 | ✅ Yes | 550 kWh  | $201,000
9  | Sunset Park Recreation Ctr   | Brooklyn   | 79 | 0.83 | ✅ Yes | 400 kWh  | $167,000
10 | Harlem Hospital Center       | Manhattan  | 78 | 0.70 | ✅ Yes | 1200 kWh | $345,000
```

- BESS Score column: color-coded bar (green ≥80, yellow 60-79, red <60) behind the number
- Equity Zone: green check or red X
- Clicking a row selects it and populates the Site Detail Panel below
- Default: Row 1 is selected

#### Right (40%): Map Placeholder

A styled placeholder box representing the NYC map area:
- Dark background with a subtle grid pattern
- Title: "NYC Municipal Sites — BESS Priority Map"
- Show 5 colored dots positioned roughly where each NYC borough is (just approximate positions in the box):
  - Manhattan: center-left, cluster of 2 dots
  - Brooklyn: center-right, cluster of 3 dots
  - Queens: upper-right, cluster of 2 dots
  - Bronx: upper-left, cluster of 3 dots (some red/high priority)
  - Staten Island: bottom-left, 1 dot
- Color legend at bottom: 🔴 Score 80-100, 🟡 Score 60-79, 🔵 Score <60
- Small text: "Interactive map powered by Leaflet (connect live data to enable)"

---

### 5. Section 3 — Site Detail Panel (full width, collapsible)

When a site is selected from the table, show a detailed panel with three columns:

#### Column 1: Site Info
- **Site Name** (large, bold)
- Address: [mock address]
- Borough: [borough]
- Agency: DCAS / DOE / FDNY etc.
- BBL: [mock BBL number]
- Environmental Justice Area: Yes/No badge

#### Column 2: Energy Profile
- Avg Monthly Consumption: XXX,XXX kWh
- Peak Demand: XXX kW
- Annual Energy Cost: $XXX,XXX
- Solar Potential: XXX kWh/yr
- Roof Condition: Good/Fair/Poor (color badge)
- Nearby EV Ports: XX within borough

#### Column 3: BESS Recommendation
- **BESS Priority Score: XX/100** (large, with colored ring/gauge)
- Recommended Capacity: XXX kWh
- Estimated Annual Savings: $XXX,XXX
- Peak Reduction: XX kW (XX%)
- CO₂ Offset: XX tons/yr
- **Top Reason:** "High electricity consumption in environmental justice area with excellent solar co-location potential and growing EV charging demand nearby."

---

### 6. Section 4 — Dispatch Simulation (full width)

Title: "24-Hour BESS Dispatch Schedule — [Selected Site Name]"

Two charts side by side (50/50):

#### Left Chart: Stacked Area Chart (recharts AreaChart)
- X-axis: Hour (0–23)
- Y-axis: Power (kW)
- Three stacked areas:
  - **Building Demand** (blue, #3B82F6): follows commercial demand curve, peak ~200kW at hours 10-15
  - **Solar Generation** (yellow, #F59E0B): bell curve peaking at hour 12, ~50kW max
  - **BESS Discharge** (green, #10B981): appears during peak hours 8-17, ~60-125kW

Mock 24h data (use realistic shapes):
```
Hour 0-5:   demand 60-50kW, solar 0, BESS charging (negative, show as 0 on this chart)
Hour 6-8:   demand ramps 90→170kW, solar starts 10→70kW, BESS starts discharge 30kW
Hour 9-15:  demand 180-200kW, solar peaks 95-100kW at 12, BESS discharge 80-125kW
Hour 16-19: demand drops 170→110kW, solar drops 50→0kW, BESS discharge tapers 60→0kW
Hour 20-23: demand 80-60kW, solar 0, BESS charging
```

#### Right Chart: Battery State of Charge (recharts LineChart)
- X-axis: Hour (0–23)
- Y-axis: SOC % (0–100%)
- Single line (emerald green) showing:
```
Hour 0: 20% → charges overnight
Hour 6: 90% → starts discharging
Hour 12: 55% → continues discharging
Hour 17: 15% → minimum, starts recharging
Hour 23: 25% → ready for overnight charge
```
- Horizontal dashed lines at 10% (red, "Min SOC") and 95% (orange, "Max SOC")

Below both charts, a summary bar with 4 metrics:
- Daily Savings: $38.50
- Peak Shaved: 87.2 kW (43.6%)
- Battery Cycles: 0.85/day
- Grid Independence: 34% of peak hours

---

### 7. Section 5 — Borough Comparison (full width)

Title: "Borough-Level BESS Deployment Summary"

#### Bar Chart (recharts BarChart, horizontal)
- Y-axis: 5 boroughs
- X-axis: Number of sites
- Two grouped bars per borough:
  - Total Sites Analyzed (gray)
  - High-Priority Sites, score ≥ 70 (blue)

Mock data:
```
Bronx:         892 total, 234 high-priority
Brooklyn:      1,105 total, 198 high-priority
Manhattan:     687 total, 142 high-priority
Queens:        1,024 total, 187 high-priority
Staten Island: 560 total, 86 high-priority
```

#### Summary Cards (below the chart, 5 cards in a row, one per borough)
Each card:
- Borough name
- "If budget = $5M": X sites deployable
- Total potential savings: $X.XM/yr
- Total CO₂ offset: X,XXX tons/yr

```
Bronx:         18 sites, $4.2M savings, 1,890 tons CO₂
Brooklyn:      15 sites, $3.8M savings, 1,650 tons CO₂
Manhattan:     12 sites, $3.1M savings, 1,420 tons CO₂
Queens:        14 sites, $3.5M savings, 1,560 tons CO₂
Staten Island: 8 sites,  $1.8M savings, 720 tons CO₂
```

---

### 8. Footer (full width, slim)

- Left: "BESS Predictor v1.0 — Spark Hack NYC 2026"
- Center: "Data: NYC Open Data Portal | Model: Claude API on NVIDIA GB10"
- Right: "Team [Your Team Name]"

---

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| bg-primary | #0F172A | Sidebar, main background |
| bg-secondary | #1E293B | Cards, header, panels |
| bg-tertiary | #334155 | Hover states, borders |
| accent-blue | #3B82F6 | Primary actions, demand curves |
| accent-green | #10B981 | BESS/positive metrics |
| accent-yellow | #F59E0B | Solar, warnings |
| accent-red | #EF4444 | High-priority markers |
| text-primary | #F8FAFC | Headlines, big numbers |
| text-secondary | #94A3B8 | Labels, descriptions |

---

## Typography

- Font: Inter or system sans-serif
- KPI numbers: 2.5rem, font-weight 700
- Section titles: 1.25rem, font-weight 600, text-secondary, uppercase, letter-spacing 0.05em
- Body: 0.875rem
- Table: 0.8125rem, monospace for numbers

---

## Interaction Notes

- Table row click → updates Site Detail Panel (Section 3) and Dispatch Chart (Section 4) with that site's data
- Filter changes → re-filter the table and update KPI cards
- Weight sliders → recalculate BESS scores client-side (simple weighted sum of normalized features, no API call needed for the demo)
- All data is hardcoded mock data — no API calls in the artifact
- Make the whole thing feel like a mission control dashboard for city energy planners
