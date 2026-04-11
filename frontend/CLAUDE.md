# NYC Smart City Nexus — Frontend

Vite + React dashboard for the NYC Smart City Nexus hackathon project (Spark Hack NYC 2026).
Interactive mission-control UI for city energy and waste planners.

## Commands

```bash
pnpm dev      # dev server (http://localhost:5173)
pnpm build    # production build → dist/
pnpm preview  # serve dist/ locally
pnpm lint     # ESLint
```

## Tech Stack

| Layer | Choice |
|---|---|
| Bundler | Vite 8 |
| UI | React 19 (JSX — not TypeScript) |
| Styling | Tailwind CSS v4 via `@tailwindcss/vite` — zero config file, just `@import "tailwindcss"` in `index.css` |
| Map | MapLibre GL JS 5 + react-map-gl 8 (`import Map from 'react-map-gl/maplibre'`) |
| Map tiles | CARTO Dark Matter raster tiles — **free, no API key** |
| Charts | Custom hand-rolled SVG — no recharts installed |
| State | React Context (`DashboardContext`) — no Zustand/Redux |

## Project Structure

```
src/
├── context/
│   └── DashboardContext.jsx   # all shared state (viewMode, selectedId, borough, filters, scenario)
├── hooks/
│   └── useViewMode.js         # re-exports useDashboard from context
├── data/
│   ├── top50_scored_xgboost.json  # real XGBoost-scored site data (50 sites)
│   ├── sites.js               # imports JSON, transforms → ENERGY_SITES, WASTE_SITES, NEXUS_SITES,
│   │                          #   BOROUGH_DATA, KPI arrays, score helpers
│   ├── districts.js           # borough + EJ GeoJSON polygons for MapLibre layers
│   └── chartData.js           # hourly dispatch, SOC, waste forecast, diversion gap, scenario
└── components/
    ├── Map/
    │   ├── CityMap.jsx        # MapLibre GL map — 3 layer modes (Energy/Waste/Nexus)
    │   ├── MapLegend.jsx      # dynamic legend per viewMode
    │   └── MapControls.jsx    # live geocoder search over ENERGY_SITES array
    ├── Sidebar.jsx            # view toggle pills, nav, borough/score/budget/EJ filters
    ├── Header.jsx             # breadcrumb, status pills
    ├── KPIRibbon.jsx          # 4 KPI cards, switches content with viewMode
    ├── RankingsTable.jsx      # 3-schema table (energy/waste/nexus), row click → selectSite
    ├── SiteDetail.jsx         # 3-col panel: identity / score rings / BESS + AI insight
    ├── FlowVisualization.jsx  # SVG Sankey flows (Energy + Waste side by side)
    ├── Simulation.jsx         # tabbed: BESS Dispatch / Waste Forecast / Scenario Planner
    └── BoroughComparison.jsx  # horizontal grouped bar + 5 borough summary cards
```

## Shared State (DashboardContext)

All components read from `useDashboard()`. Never use local state for cross-component concerns.

| Field | Type | Description |
|---|---|---|
| `viewMode` | `'energy' \| 'waste' \| 'nexus'` | Drives KPIs, table schema, map layers |
| `selectedId` | `number` | 0-based index into `ENERGY_SITES` |
| `borough` | `string` | Filter — `'All Boroughs'` or a borough name |
| `minScore` | `number` | Filter — hide sites below this nexus score |
| `ejPriority` | `boolean` | EJ toggle |
| `simTab` | `'bess' \| 'waste' \| 'scenario'` | Active simulation tab |
| `scenario` | `object` | Scenario Planner slider values |

Changing `viewMode` via `changeView()` also auto-switches `simTab`.

## Data

### Real site data (`top50_scored_xgboost.json`)
50 NYC municipal sites scored by XGBoost model. Fields used:
- `rank`, `site`, `address`, `borough`, `agency`
- `env_justice` — `"Yes"` / `"No"`
- `energy_score`, `waste_score`, `nexus_score` — 0–100
- `recommended_bess_kwh` — 250 / 500 / 750
- `estimated_annual_savings_usd` — number
- `top_recommendation`, `reasoning` — strings shown in SiteDetail

**lat/lng** are derived deterministically in `sites.js` using golden-ratio scatter within each borough's bounding box. They are **not** in the raw JSON.

### Score thresholds (updated for real data range 88–98)
| Range | Color | Meaning |
|---|---|---|
| ≥ 95 | `#EF4444` red | Highest priority |
| ≥ 90 | `#F59E0B` amber | High priority |
| < 90 | `#3B82F6` blue | Medium priority |

Helper functions in `sites.js`: `scoreColor(s)`, `scoreBg(s)`, `scoreText(s)`.

## Map Layers

Three modes driven by `viewMode`:

| Mode | Layers |
|---|---|
| **Energy** | Circle layer — radius + color by `nexusScore`. White ring on `selectedId`. Hover popup. |
| **Waste** | Borough fill choropleth (orange intensity by `wasteTons`) + district circles (size by refuse tonnage) |
| **Nexus** | Borough fill + EJ area fill (purple outlined) + heatmap by `nexusScore` |

Map tile style defined inline as a MapLibre style object in `CityMap.jsx` — CARTO Dark Matter raster, no external style JSON file.

## Styling Conventions

The design matches `City_Planning_Nexus.html` exactly. Use inline styles (not Tailwind classes) for component-level styling — the HTML reference uses inline CSS and the components follow the same pattern.

**Color palette:**
```
Background:   #0B1120
Card:         #131C2E  border: #1E293B
Sidebar:      #0F172A
Blue accent:  #3B82F6   text: #60A5FA / #93C5FD
Emerald:      #10B981   text: #6EE7B7
Amber:        #F59E0B   text: #FCD34D
Red:          #EF4444   text: #FCA5A5
Purple:       #8B5CF6   text: #C4B5FD
Text primary: #F1F5F9
Text muted:   #64748B
Text dim:     #475569 / #334155
```

**Card pattern:**
```jsx
style={{ background: '#131C2E', border: '1px solid #1E293B', borderRadius: 12, padding: 16 }}
```

**Section label pattern:**
```jsx
style={{ fontSize: 10, fontWeight: 600, color: '#475569', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12 }}
```

## Key Conventions

- **JSX only** — no `.tsx` files. TypeScript types are not enforced.
- **No recharts** — all charts are hand-rolled SVG inside components.
- **No API calls** — all data is static/derived from the imported JSON.
- **Do not touch** `City_Planning_Nexus.html` — it is a reference artifact only.
- Map click → `selectSite(id)` + `flyTo()` → updates SiteDetail and table highlight.
- Borough filter + minScore slider filter both the map circles and the rankings table rows.
- KPI numbers in `ENERGY_KPIS` are computed dynamically from `ENERGY_SITES` at module load time in `sites.js` — do not hardcode them.
