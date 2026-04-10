# NYC Smart City Nexus — Full Dashboard UI

Build a single-page interactive React dashboard as an artifact. Use Tailwind CSS for all styling. Use recharts for all charts. Dark theme — this should look like a **mission control center for city energy and waste planners**. All data is hardcoded realistic mock data based on real NYC municipal buildings and waste districts.

---

## Global Style

- Background: #0B1120 (deep navy)
- Cards/panels: #131C2E with border #1E293B
- Accent blue: #3B82F6 (energy)
- Accent emerald: #10B981 (positive/savings)
- Accent amber: #F59E0B (solar/waste)
- Accent orange: #F97316 (waste)
- Accent red: #EF4444 (alerts)
- Accent purple: #8B5CF6 (nexus)
- Text primary: #F1F5F9
- Text secondary: #64748B
- Font: system sans-serif, monospace for numbers
- All cards: rounded-xl, subtle ring-1 ring-white/5, shadow-lg
- Transitions: smooth 200ms on hover states

---

## Layout Structure

```
┌─────────(240px)──────┬────────────────────────────────────────────────┐
│                      │  HEADER (h-14, sticky)                         │
│      SIDEBAR         ├────────────────────────────────────────────────┤
│                      │                                                │
│  (fixed, full-height)│  SCROLLABLE MAIN CONTENT                      │
│                      │                                                │
│                      │  [KPI Ribbon]                                  │
│                      │  [Map + Rankings]                              │
│                      │  [Site Detail]                                 │
│                      │  [Sankey / Flow]                               │
│                      │  [Simulation]                                  │
│                      │  [Borough Comparison]                          │
│                      │                                                │
└──────────────────────┴────────────────────────────────────────────────┘
```

---

## SIDEBAR (fixed left, 240px, bg #0F172A, border-r border-white/5)

### Logo Section (top, px-5 py-6)
- Line 1: "⚡ NYC Nexus" — text-xl font-bold text-white
- Line 2: "Energy · Waste · Intelligence" — text-xs text-slate-500 tracking-widest uppercase

### View Mode Selector (px-4 py-2)
Three pill buttons in a row (acts as the main view toggle). Use React state to switch the active view. The active pill has bg-blue-600 text-white; inactive pills have bg-slate-800 text-slate-400.
- **Energy** (default active)
- **Waste**
- **Nexus**

Switching view mode changes: KPI cards, ranking table columns, map layer description, and simulation tab content. Implement this with a single `viewMode` state variable.

### Navigation (px-3 mt-4, vertical list)
Each item: icon + text, rounded-lg px-3 py-2, hover:bg-slate-800. Active item has bg-slate-800/60 text-blue-400.
- 📊 Dashboard (active)
- 🗺️ Site Map
- 📋 Rankings
- 📈 Analytics
- ⚙️ Settings

### Filters Section (px-4 mt-6, border-t border-white/10 pt-4)
Label: "FILTERS" in text-[10px] uppercase tracking-widest text-slate-600 mb-3

**Borough dropdown** (select element, bg-slate-800 text-sm rounded-lg):
Options: All Boroughs, Manhattan, Brooklyn, Queens, Bronx, Staten Island

**Min Score slider** (range input):
Label: "Min Priority Score" — show current value
Range: 0–100, default 0, step 5

**Budget slider** (range input):
Label: "Budget ($M)" — show current value as "$X.XM"
Range: 1–50, default 10, step 1

**Equity Priority toggle** (small toggle switch):
Label: "Prioritize EJ Areas"
Default: ON (checked)

Small blue button at bottom: "Apply Filters" — full width, rounded-lg, bg-blue-600 hover:bg-blue-500, text-sm font-medium

---

## HEADER BAR (sticky top, h-14, bg-#0F172A/80 backdrop-blur-xl, border-b border-white/5, z-50)

- Left side: "Dashboard" in text-sm font-medium text-slate-300, then " / " text-slate-600, then the active view mode name in text-blue-400
- Right side (flex items-center gap-4):
  - Small pill badge: "Claude API" with a small blue dot before it — bg-blue-500/10 text-blue-400 text-xs px-2.5 py-0.5 rounded-full
  - Small pill badge: green dot + "Pipeline Complete" — bg-emerald-500/10 text-emerald-400 text-xs
  - Text: "Apr 10, 2026 2:34 PM" in text-xs text-slate-500

---

## SECTION 1: KPI RIBBON (grid grid-cols-4 gap-4 for energy, then grid-cols-4 for waste — show 8 cards in 2 rows of 4, or 1 row of 4 based on active view mode)

### Energy View — 4 cards:

Card 1:
- Icon area: small rounded square bg-blue-500/10 with 🏢 inside
- Big number: "4,268" — text-3xl font-bold text-white tabular-nums
- Label: "Sites Analyzed" — text-sm text-slate-400
- Sublabel: "Municipal buildings across 5 boroughs" — text-xs text-slate-600

Card 2:
- Icon area: bg-emerald-500/10 with 🔋
- Big number: "847"
- Label: "High-Priority Sites"
- Sublabel: "BESS score ≥ 70"
- Small green tag: "▲ 19.8% of total"

Card 3:
- Icon area: bg-amber-500/10 with 💰
- Big number: "$12.4M"
- Label: "Annual Savings Potential"
- Sublabel: "If top 50 sites deploy BESS"

Card 4:
- Icon area: bg-emerald-500/10 with 🌱
- Big number: "8,240"
- Label: "Tons CO₂ Offset/yr"
- Sublabel: "≈ 1,790 cars removed"

### Waste View — 4 cards:

Card 1:
- Icon: bg-orange-500/10 with 🗑️
- Big number: "295K"
- Label: "Monthly Refuse (tons)"
- Sublabel: "Latest month, citywide"

Card 2:
- Icon: bg-teal-500/10 with ♻️
- Big number: "21.3%"
- Label: "Diversion Rate"
- Sublabel: "Target: 30%"
- Small red tag: "▼ 8.7% below target"

Card 3:
- Icon: bg-red-500/10 with 🚛
- Big number: "$418"
- Label: "Avg Disposal Cost/ton"
- Sublabel: "Across all facilities"

Card 4:
- Icon: bg-purple-500/10 with 🔥
- Big number: "1.2M"
- Label: "MWh WTE Potential/yr"
- Sublabel: "If 50% organics → AD"

### Nexus View — 4 cards:
Show combined highlights:

Card 1: "25" — "Datasets Integrated" — "12 energy + 13 waste"
Card 2: "$19.7M" — "Combined Savings/yr" — "Energy + waste optimization"
Card 3: "12,400" — "Total CO₂ Offset (tons/yr)" — "Energy + waste combined"
Card 4: "68%" — "EJ Area Coverage" — "Equity-weighted deployment"

---

## SECTION 2: MAP + RANKINGS (grid grid-cols-5 gap-4 — map gets 3 cols, table gets 2 cols)

### Left: Map Area (col-span-3, aspect-[4/3], bg-#131C2E rounded-xl overflow-hidden)

Since we can't use a real map library in a React artifact, create a **stylized SVG visualization** of NYC's five boroughs as simplified shapes. This is the most important visual element.

Draw 5 simplified borough polygons (abstract/geometric shapes, not geographically precise — just recognizable):
- Manhattan: tall narrow rectangle, center-left
- Brooklyn: large irregular shape, center-bottom-right
- Queens: large shape, right side
- Bronx: shape at top
- Staten Island: small shape, bottom-left

Fill each borough shape with a semi-transparent color based on the active view:
- Energy view: blue gradient intensity based on energy consumption
- Waste view: orange gradient intensity based on waste tonnage
- Nexus view: purple gradient intensity based on combined score

Scatter colored dots inside each borough (representing sites):
Mock dot data (generate 30-40 dots with randomized positions within each borough shape):

```javascript
const sites = [
  // Bronx (top area) — high priority cluster
  { x: 185, y: 55, score: 94, name: "PS 123 School", borough: "Bronx" },
  { x: 200, y: 70, score: 91, name: "FDNY Engine 42", borough: "Bronx" },
  { x: 170, y: 80, score: 85, name: "Bronx Courthouse", borough: "Bronx" },
  { x: 210, y: 45, score: 72, name: "Bronx Library", borough: "Bronx" },
  { x: 190, y: 90, score: 68, name: "Bronx Health Ctr", borough: "Bronx" },
  { x: 175, y: 65, score: 55, name: "Bronx Park Bldg", borough: "Bronx" },
  // Manhattan (center-left, tall narrow)
  { x: 135, y: 120, score: 82, name: "Civic Center", borough: "Manhattan" },
  { x: 130, y: 155, score: 78, name: "Harlem Hospital", borough: "Manhattan" },
  { x: 140, y: 180, score: 65, name: "DSNY Garage M7", borough: "Manhattan" },
  { x: 128, y: 140, score: 59, name: "Public Library", borough: "Manhattan" },
  { x: 138, y: 200, score: 48, name: "Tribeca Annex", borough: "Manhattan" },
  // Brooklyn (center-right, large)
  { x: 200, y: 230, score: 89, name: "Navy Yard Bldg 77", borough: "Brooklyn" },
  { x: 230, y: 250, score: 79, name: "Sunset Park Rec", borough: "Brooklyn" },
  { x: 250, y: 220, score: 73, name: "BK Central Lib", borough: "Brooklyn" },
  { x: 215, y: 260, score: 66, name: "Prospect Depot", borough: "Brooklyn" },
  { x: 270, y: 240, score: 52, name: "Canarsie Yard", borough: "Brooklyn" },
  { x: 190, y: 245, score: 61, name: "Red Hook Ctr", borough: "Brooklyn" },
  // Queens (right)
  { x: 300, y: 140, score: 87, name: "Queens Central Lib", borough: "Queens" },
  { x: 320, y: 170, score: 80, name: "Jamaica HVAC Ctr", borough: "Queens" },
  { x: 280, y: 160, score: 71, name: "Flushing Depot", borough: "Queens" },
  { x: 340, y: 150, score: 58, name: "Rockaway Stn", borough: "Queens" },
  { x: 310, y: 190, score: 44, name: "Ozone Park Sch", borough: "Queens" },
  // Staten Island (bottom-left, small)
  { x: 80, y: 290, score: 83, name: "Borough Hall SI", borough: "Staten Island" },
  { x: 95, y: 310, score: 56, name: "SI Landfill Site", borough: "Staten Island" },
  { x: 70, y: 305, score: 41, name: "Tottenville Sch", borough: "Staten Island" },
]
```

Dot styling:
- Size: 6-10px diameter, larger for higher scores
- Color: score ≥ 80 → #EF4444 (red), 60-79 → #F59E0B (amber), <60 → #3B82F6 (blue)
- On hover: enlarge to 14px, show tooltip with site name + score
- Clicking a dot selects it (adds a white ring) and updates the Site Detail panel and Simulation section

**Map title:** "NYC Municipal Sites — Priority Map" in text-sm font-medium text-slate-300 at top-left of map with a subtle bg-black/40 backdrop px-3 py-1.5 rounded-lg

**Legend** at bottom-right inside map: three small circles with labels:
- 🔴 Score 80–100 (High Priority)
- 🟡 Score 60–79 (Medium)
- 🔵 Score <60 (Low)

**Borough labels:** faint text labels positioned in the center of each borough shape, text-[11px] text-slate-500/50 font-medium uppercase

---

### Right: Rankings Table (col-span-2)

Card with header "Top Sites" + a small pill showing "{count} results".

Table header row: bg-slate-800/40, text-[11px] uppercase tracking-wider text-slate-500.

Scrollable table body (max height ~400px, overflow-y-auto with custom thin scrollbar).

**Energy View columns & data:**

| Rank | Site Name | Borough | Score | Solar | EJ | Savings/yr |
|------|-----------|---------|-------|-------|----|------------|
| 1 | PS 123 School Complex | Bronx | 94 | 0.92 | ✅ | $287K |
| 2 | FDNY Engine 42 Station | Bronx | 91 | 0.88 | ✅ | $243K |
| 3 | Brooklyn Navy Yard Bldg 77 | Brooklyn | 89 | 0.85 | — | $312K |
| 4 | Queens Central Library | Queens | 87 | 0.78 | ✅ | $198K |
| 5 | Bronx County Courthouse | Bronx | 85 | 0.72 | ✅ | $265K |
| 6 | Staten Island Borough Hall | S.I. | 83 | 0.81 | — | $176K |
| 7 | Manhattan Civic Center | Manhattan | 82 | 0.65 | — | $298K |
| 8 | Jamaica HVAC Center | Queens | 80 | 0.77 | ✅ | $201K |
| 9 | Sunset Park Recreation Ctr | Brooklyn | 79 | 0.83 | ✅ | $167K |
| 10 | Harlem Hospital Center | Manhattan | 78 | 0.70 | ✅ | $345K |
| 11 | Flushing Depot | Queens | 71 | 0.62 | — | $142K |
| 12 | Prospect Park Depot | Brooklyn | 66 | 0.58 | ✅ | $118K |
| 13 | Red Hook Community Ctr | Brooklyn | 61 | 0.55 | ✅ | $95K |
| 14 | Rockaway Station | Queens | 58 | 0.49 | ✅ | $89K |
| 15 | Bronx Park Building | Bronx | 55 | 0.44 | — | $76K |

Score column: render a small horizontal bar behind the number. Bar width = score%, color follows the red/amber/blue scale.

EJ column: ✅ = small green dot, — = small gray dot

**Row interaction:** clicking a row highlights it (bg-blue-500/10 border-l-2 border-blue-500) and updates selected site state.

**Waste View columns & data:**

| Rank | District | Borough | Refuse t/mo | Diversion % | 311 Complaints | Organic Potential |
|------|----------|---------|-------------|-------------|----------------|-------------------|
| 1 | District 7 | Bronx | 12,450 | 14.2% | 1,847 | High |
| 2 | District 1 | Brooklyn | 11,820 | 16.8% | 1,623 | High |
| 3 | District 12 | Queens | 10,950 | 18.1% | 1,204 | Medium |
| 4 | District 9 | Manhattan | 9,870 | 22.4% | 2,156 | Medium |
| 5 | District 3 | Bronx | 9,540 | 13.7% | 1,932 | High |
| 6 | District 14 | Brooklyn | 9,120 | 19.3% | 987 | Medium |
| 7 | District 7 | Queens | 8,760 | 20.1% | 876 | Medium |
| 8 | District 1 | S.I. | 8,340 | 17.5% | 654 | Low |
| 9 | District 4 | Manhattan | 7,890 | 25.6% | 1,543 | Low |
| 10 | District 5 | Brooklyn | 7,650 | 21.2% | 1,098 | Medium |

**Nexus View columns & data:**

| Rank | Location | Borough | Energy | Waste | Nexus | CO₂ Impact |
|------|----------|---------|--------|-------|-------|------------|
| 1 | Dist 7 + PS 123 | Bronx | 94 | 88 | 96 | 142 t/yr |
| 2 | Dist 1 + Navy Yard | Brooklyn | 89 | 82 | 91 | 128 t/yr |
| 3 | Dist 12 + Queens Lib | Queens | 87 | 79 | 88 | 115 t/yr |
| 4 | Dist 3 + Courthouse | Bronx | 85 | 85 | 87 | 134 t/yr |
| 5 | Dist 9 + Harlem Hosp | Manhattan | 78 | 76 | 84 | 98 t/yr |

---

## SECTION 3: SITE DETAIL PANEL (full width, shows when a site is selected — default: first row selected)

Card with three columns inside:

### Column 1: Identity
- **Site name** in text-xl font-bold text-white
- Address: "1250 E 172nd St, Bronx, NY 10472" — text-sm text-slate-400
- Agency: "DOE (Dept of Education)" — text-sm
- BBL: "2-02831-0045" — text-xs text-slate-500 font-mono
- Environmental Justice Area: green badge "EJ Area" if yes, gray badge "Non-EJ" if no

### Column 2: Energy Profile
Render as a mini grid of key-value pairs, each in its own small card:
- Avg Monthly: **184,500 kWh**
- Peak Demand: **342 kW**
- Annual Cost: **$487,200**
- Solar Potential: **285,000 kWh/yr**
- Roof: green badge **"Good"**
- EV Ports Nearby: **47**

### Column 3: Waste & BESS Recommendation
Top half — BESS recommendation:
- Large circular gauge/ring showing the score (94/100). Use an SVG circle with stroke-dasharray to create a progress ring. Color: red for 80+, amber 60-79, blue <60.
- Below: "Recommended: **750 kWh BESS**"
- "Est. Savings: **$287,000/yr**"
- "Peak Reduction: **87 kW (25.4%)**"
- "CO₂ Offset: **42 tons/yr**"

Bottom half — Waste context for this district:
- District refuse: **12,450 t/mo**
- Organic fraction: **34%** → **4,233 t/mo divertible**
- If diverted to AD: **~18,500 MWh/yr biogas**

### LLM Insight Bar (full width below the 3 columns, bg-purple-500/5 border border-purple-500/20 rounded-lg px-4 py-3)
- Small purple "🤖 AI Insight" badge
- Text: "This Bronx school sits in an Environmental Justice area with the borough's 3rd highest energy cost. The surrounding District 7 produces 12,450 tons/month of refuse — 34% organic — with only 14.2% diversion rate. Recommended: deploy 750 kWh BESS for peak shaving ($287K/yr savings), and partner with Newtown Creek AD facility to process district organics into biogas. Combined CO₂ offset: 142 tons/yr, serving 23,000 residents in an underserved community."

---

## SECTION 4: FLOW VISUALIZATION — Sankey-Style (full width, two panels side by side)

Since recharts doesn't have a Sankey chart, build a **custom SVG flow diagram** with animated gradients.

### Left Panel: Energy Flow (col-span-1)
Title: "Energy Flow — Citywide" in text-sm font-medium

Draw a simplified Sankey with these nodes and flows using SVG paths with curved bezier lines:

**Left column (Sources):**
- Grid (ConEd): 44,200 GWh — thick gray flow
- Solar: 2,800 GWh — amber flow
- Biogas: 680 GWh — green flow
- Wind: 4,320 GWh — light blue flow

**Middle column (Sectors):**
- Commercial: 22,400 GWh
- Residential: 18,900 GWh
- Municipal: 6,200 GWh
- Industrial: 4,500 GWh

**Right column (End Use):**
- Direct Use: 42,000 GWh
- EV Charging: 3,200 GWh
- BESS Storage: 2,800 GWh
- Losses: 4,000 GWh

Each flow: SVG path with a gradient matching source color, opacity 0.3, stroke matching source color at opacity 0.6. Width proportional to GWh value.

Add subtle CSS animation: the gradient offset shifts slowly to create a "flowing" effect.

### Right Panel: Waste Flow
Title: "Waste Flow — Citywide"

**Left column (Sources):**
- Residential: 3.1M tons — blue flow
- Commercial: 5.2M tons — slate flow
- Institutional: 1.4M tons — teal flow
- Construction: 4.3M tons — gray flow

**Middle column (Collection):**
- DSNY Trucks: 3.5M tons
- Private Carters: 8.8M tons
- Drop-off: 0.7M tons
- Self-haul: 1.0M tons

**Right column (Destination):**
- Landfill: 7.7M tons — red flow (55%)
- WTE Plants: 3.1M tons — orange flow (22%)
- Recycling: 2.5M tons — blue flow (18%)
- Composting: 0.7M tons — green flow (5%)

Same animated gradient style. Show percentage labels at the right side.

---

## SECTION 5: SIMULATION (full width, tabbed interface)

Three tabs styled as pills: "⚡ BESS Dispatch" | "🗑️ Waste Forecast" | "🎯 Scenario Planner"

### Tab 1: BESS Dispatch (default for Energy view)

Two recharts side-by-side in a grid-cols-2:

**Left: Stacked Area Chart — "24h Energy Profile"**
- X axis: Hours 0–23 (labels: "12AM", "3AM", "6AM", "9AM", "12PM", "3PM", "6PM", "9PM")
- Y axis: Power (kW), range 0–300
- Three areas stacked:

```javascript
const hourlyData = [
  { hour: 0, demand: 62, solar: 0, bess: 0 },
  { hour: 1, demand: 58, solar: 0, bess: 0 },
  { hour: 2, demand: 52, solar: 0, bess: 0 },
  { hour: 3, demand: 50, solar: 0, bess: 0 },
  { hour: 4, demand: 52, solar: 0, bess: 0 },
  { hour: 5, demand: 60, solar: 2, bess: 0 },
  { hour: 6, demand: 95, solar: 10, bess: 0 },
  { hour: 7, demand: 140, solar: 30, bess: 15 },
  { hour: 8, demand: 185, solar: 70, bess: 45 },
  { hour: 9, demand: 220, solar: 120, bess: 80 },
  { hour: 10, demand: 260, solar: 160, bess: 105 },
  { hour: 11, demand: 285, solar: 190, bess: 120 },
  { hour: 12, demand: 295, solar: 200, bess: 125 },
  { hour: 13, demand: 290, solar: 190, bess: 120 },
  { hour: 14, demand: 280, solar: 170, bess: 110 },
  { hour: 15, demand: 265, solar: 140, bess: 95 },
  { hour: 16, demand: 240, solar: 100, bess: 70 },
  { hour: 17, demand: 200, solar: 50, bess: 40 },
  { hour: 18, demand: 160, solar: 15, bess: 15 },
  { hour: 19, demand: 130, solar: 0, bess: 0 },
  { hour: 20, demand: 105, solar: 0, bess: 0 },
  { hour: 21, demand: 88, solar: 0, bess: 0 },
  { hour: 22, demand: 75, solar: 0, bess: 0 },
  { hour: 23, demand: 68, solar: 0, bess: 0 },
];
```

- demand: fill #3B82F6 opacity 0.3, stroke #3B82F6
- solar: fill #F59E0B opacity 0.3, stroke #F59E0B
- bess: fill #10B981 opacity 0.3, stroke #10B981
- Add a recharts Tooltip and Legend

**Right: Line Chart — "Battery State of Charge"**
```javascript
const socData = [
  { hour: 0, soc: 20 }, { hour: 1, soc: 32 }, { hour: 2, soc: 45 },
  { hour: 3, soc: 58 }, { hour: 4, soc: 72 }, { hour: 5, soc: 85 },
  { hour: 6, soc: 92 }, { hour: 7, soc: 88 }, { hour: 8, soc: 78 },
  { hour: 9, soc: 65 }, { hour: 10, soc: 52 }, { hour: 11, soc: 40 },
  { hour: 12, soc: 30 }, { hour: 13, soc: 25 }, { hour: 14, soc: 22 },
  { hour: 15, soc: 18 }, { hour: 16, soc: 15 }, { hour: 17, soc: 14 },
  { hour: 18, soc: 16 }, { hour: 19, soc: 20 }, { hour: 20, soc: 22 },
  { hour: 21, soc: 18 }, { hour: 22, soc: 15 }, { hour: 23, soc: 18 },
];
```
- Line: stroke #10B981, strokeWidth 2, dot false
- Add two horizontal ReferenceLine components: y=10 stroke="#EF4444" strokeDasharray="5 5" label="Min 10%", y=95 stroke="#F59E0B" strokeDasharray="5 5" label="Max 95%"
- Area fill below line: fill #10B981 opacity 0.1

**Summary bar below both charts** (flex justify-around, bg-slate-800/40 rounded-lg py-3):
- Daily Savings: **$38.50**
- Peak Shaved: **87.2 kW (25.4%)**
- Battery Cycles: **0.85/day**
- Grid Independence: **34% of peak hours**

### Tab 2: Waste Forecast (default for Waste view)

Two recharts side-by-side:

**Left: Multi-line Chart — "12-Month Waste Forecast"**
```javascript
const wasteForcast = [
  { month: "May", refuse: 285, recycling: 52, organics: 15, total: 352 },
  { month: "Jun", refuse: 278, recycling: 54, organics: 18, total: 350 },
  { month: "Jul", refuse: 290, recycling: 53, organics: 20, total: 363 },
  { month: "Aug", refuse: 282, recycling: 55, organics: 22, total: 359 },
  { month: "Sep", refuse: 275, recycling: 56, organics: 25, total: 356 },
  { month: "Oct", refuse: 268, recycling: 58, organics: 28, total: 354 },
  { month: "Nov", refuse: 260, recycling: 59, organics: 31, total: 350 },
  { month: "Dec", refuse: 255, recycling: 60, organics: 33, total: 348 },
  { month: "Jan", refuse: 248, recycling: 62, organics: 36, total: 346 },
  { month: "Feb", refuse: 242, recycling: 63, organics: 38, total: 343 },
  { month: "Mar", refuse: 235, recycling: 65, organics: 41, total: 341 },
  { month: "Apr", refuse: 230, recycling: 66, organics: 44, total: 340 },
];
```
Units: thousands of tons. Lines: refuse=#EF4444, recycling=#3B82F6, organics=#10B981, total=#94A3B8 dashed.

**Right: Grouped Bar Chart — "Diversion Gap by Material"**
```javascript
const diversionGap = [
  { material: "Organics", current: 14, target: 45, gap: 31 },
  { material: "Paper", current: 52, target: 70, gap: 18 },
  { material: "Plastic", current: 18, target: 40, gap: 22 },
  { material: "Metal", current: 65, target: 80, gap: 15 },
  { material: "Glass", current: 42, target: 65, gap: 23 },
];
```
Two bars per material: "Current %" in slate, "Target %" in emerald. Show the gap as a red annotation or dashed outline on top of the current bar.

Annotation below chart in a callout box: "Closing the organics diversion gap alone = **45,000 MWh/yr** of biogas potential — enough to power **4,100 homes**."

### Tab 3: Scenario Planner (default for Nexus view) — THE CROWN JEWEL

Full width interactive section.

**Top: Slider Controls** (grid grid-cols-2 gap-x-8 gap-y-3, bg-slate-800/30 rounded-xl p-5)

Left column sliders:
- "Total Budget" — range 1–50, default 10, show "$10M", step 1
- "BESS Allocation" — range 0–100%, default 40%, step 5
- "Solar Allocation" — range 0–100%, default 25%, step 5

Right column sliders:
- "Organics Diversion" — range 0–100%, default 20%, step 5
- "Route Optimization" — range 0–100%, default 15%, step 5
- "Equity Weighting" — range 0–1, default 0.3, step 0.05

(Note: BESS + Solar + Organics + Route should sum to ~100% — show a small warning text in red if they don't. This is a demo, so just show the warning, don't enforce it.)

**Middle: Impact Summary** (bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-emerald-500/5, border border-white/5, rounded-xl p-6 mt-4)

Title: "PROJECTED IMPACT — $10M Budget" (updates with slider)

Four big metric boxes in a row:
- 🔋 BESS: "Deploy at **32 sites** → save **$4.8M/yr**, shave **89 MW**"
- ☀️ Solar: "Install on **18 rooftops** → **12.4 GWh/yr** generation"
- 🌱 Organics: "Divert **45K tons** → **22K MWh** biogas + **3,200 t CO₂**"
- 🚛 Routes: "Optimize **14 districts** → save **$1.1M/yr** fuel"

Divider line, then aggregate totals:
- "Annual Savings: **$7.3M**" in large green text
- "CO₂ Offset: **12,400 tons/yr**" in emerald
- "Payback: **1.4 years**" in blue
- "EJ Coverage: **68%**" in purple

**Bottom: Ranked Deployment Table** (scrollable, max 8 rows shown)

| Priority | Action | Location | Investment | Annual Return | CO₂ | Payback | Equity |
|----------|--------|----------|------------|---------------|-----|---------|--------|
| 1 | BESS 750kWh | PS 123 School, Bronx | $340K | $287K/yr | 42t | 1.2yr | ✅ EJ |
| 2 | Solar 200kW | Navy Yard Bldg 77, Brooklyn | $480K | $198K/yr | 67t | 2.4yr | — |
| 3 | Organics AD | District 7, Bronx | $220K | $165K/yr | 38t | 1.3yr | ✅ EJ |
| 4 | BESS 500kWh | FDNY Engine 42, Bronx | $290K | $243K/yr | 35t | 1.2yr | ✅ EJ |
| 5 | Solar 150kW | Queens Central Lib | $360K | $156K/yr | 52t | 2.3yr | ✅ EJ |
| 6 | Route Opt | Districts 3+7, Bronx | $180K | $142K/yr | 28t | 1.3yr | ✅ EJ |
| 7 | BESS 600kWh | Bronx Courthouse | $320K | $265K/yr | 39t | 1.2yr | ✅ EJ |
| 8 | Organics AD | District 1, Brooklyn | $195K | $134K/yr | 31t | 1.5yr | — |

---

## SECTION 6: BOROUGH COMPARISON (full width)

Title: "Borough-Level Overview"

### Horizontal Grouped Bar Chart (recharts BarChart, layout="vertical")

```javascript
const boroughData = [
  { borough: "Bronx", sites: 892, highPriority: 234, wasteTons: 48200, diversion: 15.8 },
  { borough: "Brooklyn", sites: 1105, highPriority: 198, wasteTons: 62400, diversion: 19.2 },
  { borough: "Manhattan", sites: 687, highPriority: 142, wasteTons: 38900, diversion: 24.1 },
  { borough: "Queens", sites: 1024, highPriority: 187, wasteTons: 55100, diversion: 20.5 },
  { borough: "Staten Island", sites: 560, highPriority: 86, wasteTons: 28300, diversion: 17.5 },
];
```

Two grouped bars per borough:
- "Total Sites" — #334155 (slate)
- "High Priority (≥70)" — #3B82F6 (blue)

### Borough Summary Cards (grid grid-cols-5 gap-3 mt-4)

Five cards, one per borough. Each card:

**Bronx:**
- Title: "Bronx" with a small colored dot
- "If $5M budget:" text-xs text-slate-500
- "18 sites deployable" — text-lg font-bold
- "$4.2M savings/yr" — text-emerald-400
- "1,890 tons CO₂" — text-blue-400
- "Top action: BESS + Organics AD" — text-xs text-purple-400

**Brooklyn:**
- "15 sites · $3.8M · 1,650t CO₂"
- "Top action: Solar + BESS"

**Manhattan:**
- "12 sites · $3.1M · 1,420t CO₂"
- "Top action: BESS + Route Opt"

**Queens:**
- "14 sites · $3.5M · 1,560t CO₂"
- "Top action: Solar + Organics"

**Staten Island:**
- "8 sites · $1.8M · 720t CO₂"
- "Top action: BESS + Composting"

---

## FOOTER (full width, h-12, border-t border-white/5, flex items-center justify-between px-6)

- Left: "NYC Smart City Nexus v2.0 — Spark Hack NYC 2026" — text-xs text-slate-600
- Center: "Data: NYC Open Data (25 datasets) · Model: Claude API · Hardware: NVIDIA GB10" — text-xs text-slate-600
- Right: "Built with ⚡ by Team Nexus" — text-xs text-slate-600

---

## Key Interactions Summary

1. **View Mode toggle** (Energy / Waste / Nexus) in sidebar → changes KPI cards, table columns, map layer colors, default simulation tab
2. **Map dot click** → selects site → updates Site Detail panel + BESS Dispatch chart
3. **Table row click** → same as map dot click
4. **Borough filter** in sidebar → filters table + map dots + KPI recalculation
5. **Scenario sliders** → real-time update of impact summary numbers and deployment table (use simple multiplication formulas — no API calls)
6. **Score slider** → filters which dots/rows are visible

All state management via React useState hooks. No external API calls. Everything is self-contained mock data.
