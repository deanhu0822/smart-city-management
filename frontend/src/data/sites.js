/**
 * All site data extracted directly from City_Planning_Nexus.html
 * Real NYC lat/lng coordinates added for MapLibre GL rendering
 */

export const ENERGY_SITES = [
  { id: 0, name: "PS 123 School Complex",      borough: "Bronx",         score: 94, solar: 0.92, ej: true,  savings: "$287K", mx: 185, my: 55,  lng: -73.871, lat: 40.844, addr: "1250 E 172nd St, Bronx, NY 10472",           agency: "DOE",   bbl: "2-02831-0045", cons: "184,500", peak: 342, cost: "$487,200", solPot: "285,000", roof: "Good", ev: 47, pkRed: 87,  pkPct: 25.4, co2: 42, wasteRef: "12,450", wasteOrg: "34%", wasteDivert: "4,233", wasteMWh: "18,500", bessKwh: 750 },
  { id: 1, name: "FDNY Engine 42 Station",      borough: "Bronx",         score: 91, solar: 0.88, ej: true,  savings: "$243K", mx: 200, my: 70,  lng: -73.889, lat: 40.848, addr: "445 E 174th St, Bronx, NY 10457",            agency: "FDNY",  bbl: "2-03156-0028", cons: "118,000", peak: 165, cost: "$212,000", solPot: "74,000",  roof: "Good", ev: 8,  pkRed: 73,  pkPct: 44,   co2: 35, wasteRef: "9,540",  wasteOrg: "28%", wasteDivert: "2,671", wasteMWh: "11,200", bessKwh: 500 },
  { id: 2, name: "Brooklyn Navy Yard Bldg 77",  borough: "Brooklyn",      score: 89, solar: 0.85, ej: false, savings: "$312K", mx: 200, my: 230, lng: -73.971, lat: 40.700, addr: "63 Flushing Ave, Brooklyn, NY 11205",         agency: "DCAS",  bbl: "3-02023-0001", cons: "198,000", peak: 245, cost: "$318,000", solPot: "112,000", roof: "Good", ev: 18, pkRed: 105, pkPct: 43,   co2: 67, wasteRef: "11,820", wasteOrg: "22%", wasteDivert: "2,600", wasteMWh: "10,800", bessKwh: 800 },
  { id: 3, name: "Queens Central Library",      borough: "Queens",        score: 87, solar: 0.78, ej: true,  savings: "$198K", mx: 300, my: 140, lng: -73.794, lat: 40.701, addr: "89-11 Merrick Blvd, Jamaica, NY 11432",      agency: "NYPL",  bbl: "4-09580-0001", cons: "108,000", peak: 142, cost: "$187,000", solPot: "68,000",  roof: "Fair", ev: 10, pkRed: 61,  pkPct: 43,   co2: 52, wasteRef: "10,950", wasteOrg: "25%", wasteDivert: "2,738", wasteMWh: "11,500", bessKwh: 600 },
  { id: 4, name: "Bronx County Courthouse",     borough: "Bronx",         score: 85, solar: 0.72, ej: true,  savings: "$265K", mx: 170, my: 80,  lng: -73.924, lat: 40.829, addr: "851 Grand Concourse, Bronx, NY 10451",       agency: "Courts",bbl: "2-02385-0001", cons: "162,000", peak: 198, cost: "$271,000", solPot: "79,000",  roof: "Fair", ev: 6,  pkRed: 95,  pkPct: 48,   co2: 39, wasteRef: "9,540",  wasteOrg: "30%", wasteDivert: "2,862", wasteMWh: "12,000", bessKwh: 600 },
  { id: 5, name: "Staten Island Borough Hall",  borough: "Staten Island", score: 83, solar: 0.81, ej: false, savings: "$176K", mx: 80,  my: 290, lng: -74.076, lat: 40.643, addr: "10 Richmond Terrace, SI, NY 10301",           agency: "DCAS",  bbl: "5-00001-0001", cons: "92,000",  peak: 128, cost: "$162,000", solPot: "61,000",  roof: "Good", ev: 7,  pkRed: 58,  pkPct: 45,   co2: 28, wasteRef: "8,340",  wasteOrg: "20%", wasteDivert: "1,668", wasteMWh: "7,000",  bessKwh: 400 },
  { id: 6, name: "Manhattan Civic Center",      borough: "Manhattan",     score: 82, solar: 0.65, ej: false, savings: "$298K", mx: 135, my: 120, lng: -74.004, lat: 40.713, addr: "1 Centre St, New York, NY 10007",             agency: "DCAS",  bbl: "1-00164-0001", cons: "178,000", peak: 228, cost: "$302,000", solPot: "58,000",  roof: "Fair", ev: 22, pkRed: 112, pkPct: 49,   co2: 45, wasteRef: "9,870",  wasteOrg: "18%", wasteDivert: "1,777", wasteMWh: "7,400",  bessKwh: 700 },
  { id: 7, name: "Jamaica HVAC Center",         borough: "Queens",        score: 80, solar: 0.77, ej: true,  savings: "$201K", mx: 320, my: 170, lng: -73.780, lat: 40.699, addr: "168-11 Liberty Ave, Jamaica, NY 11433",      agency: "DOT",   bbl: "4-12345-0002", cons: "112,000", peak: 148, cost: "$194,000", solPot: "72,000",  roof: "Good", ev: 9,  pkRed: 65,  pkPct: 44,   co2: 33, wasteRef: "8,760",  wasteOrg: "22%", wasteDivert: "1,927", wasteMWh: "8,100",  bessKwh: 500 },
  { id: 8, name: "Sunset Park Recreation Ctr",  borough: "Brooklyn",      score: 79, solar: 0.83, ej: true,  savings: "$167K", mx: 230, my: 250, lng: -73.998, lat: 40.650, addr: "7th Ave & 43rd St, Brooklyn, NY 11232",      agency: "Parks", bbl: "3-07001-0001", cons: "87,000",  peak: 112, cost: "$148,000", solPot: "65,000",  roof: "Good", ev: 5,  pkRed: 48,  pkPct: 43,   co2: 29, wasteRef: "7,650",  wasteOrg: "24%", wasteDivert: "1,836", wasteMWh: "7,700",  bessKwh: 350 },
  { id: 9, name: "Harlem Hospital Center",      borough: "Manhattan",     score: 78, solar: 0.70, ej: true,  savings: "$345K", mx: 130, my: 155, lng: -73.939, lat: 40.810, addr: "506 Lenox Ave, New York, NY 10037",           agency: "HHC",   bbl: "1-01808-0001", cons: "218,000", peak: 275, cost: "$348,000", solPot: "82,000",  roof: "Poor", ev: 14, pkRed: 128, pkPct: 47,   co2: 58, wasteRef: "9,870",  wasteOrg: "20%", wasteDivert: "1,974", wasteMWh: "8,300",  bessKwh: 900 },
  { id: 10,name: "Flushing Depot",              borough: "Queens",        score: 71, solar: 0.62, ej: false, savings: "$142K", mx: 280, my: 160, lng: -73.832, lat: 40.767, addr: "133-01 Northern Blvd, Flushing, NY 11354",   agency: "DSNY",  bbl: "4-05280-0001", cons: "74,000",  peak: 98,  cost: "$128,000", solPot: "48,000",  roof: "Fair", ev: 4,  pkRed: 42,  pkPct: 43,   co2: 22, wasteRef: "7,890",  wasteOrg: "18%", wasteDivert: "1,420", wasteMWh: "6,000",  bessKwh: 300 },
  { id: 11,name: "Prospect Park Depot",         borough: "Brooklyn",      score: 66, solar: 0.58, ej: true,  savings: "$118K", mx: 250, my: 220, lng: -73.973, lat: 40.663, addr: "95 Prospect Park W, Brooklyn, NY 11215",     agency: "Parks", bbl: "3-05120-0001", cons: "62,000",  peak: 82,  cost: "$108,000", solPot: "42,000",  roof: "Fair", ev: 3,  pkRed: 35,  pkPct: 43,   co2: 18, wasteRef: "6,200",  wasteOrg: "16%", wasteDivert: "992",   wasteMWh: "4,200",  bessKwh: 250 },
  { id: 12,name: "Red Hook Community Ctr",      borough: "Brooklyn",      score: 61, solar: 0.55, ej: true,  savings: "$95K",  mx: 190, my: 245, lng: -73.997, lat: 40.677, addr: "399 Atlantic Ave, Brooklyn, NY 11217",       agency: "DCAS",  bbl: "3-03200-0001", cons: "52,000",  peak: 68,  cost: "$92,000",  solPot: "38,000",  roof: "Poor", ev: 2,  pkRed: 28,  pkPct: 41,   co2: 15, wasteRef: "5,400",  wasteOrg: "15%", wasteDivert: "810",   wasteMWh: "3,400",  bessKwh: 200 },
  { id: 13,name: "Rockaway Station",            borough: "Queens",        score: 58, solar: 0.49, ej: true,  savings: "$89K",  mx: 340, my: 150, lng: -73.800, lat: 40.605, addr: "Rockaway Beach Blvd, Queens, NY 11694",      agency: "MTA",   bbl: "4-16200-0001", cons: "48,000",  peak: 64,  cost: "$86,000",  solPot: "35,000",  roof: "Fair", ev: 2,  pkRed: 26,  pkPct: 41,   co2: 14, wasteRef: "4,800",  wasteOrg: "14%", wasteDivert: "672",   wasteMWh: "2,800",  bessKwh: 150 },
  { id: 14,name: "Bronx Park Building",         borough: "Bronx",         score: 55, solar: 0.44, ej: false, savings: "$76K",  mx: 175, my: 65,  lng: -73.868, lat: 40.858, addr: "2900 Southern Blvd, Bronx, NY 10458",        agency: "Parks", bbl: "2-05840-0001", cons: "41,000",  peak: 54,  cost: "$74,000",  solPot: "28,000",  roof: "Poor", ev: 2,  pkRed: 22,  pkPct: 41,   co2: 12, wasteRef: "4,200",  wasteOrg: "12%", wasteDivert: "504",   wasteMWh: "2,100",  bessKwh: 120 },
];

export const WASTE_SITES = [
  { id: 0, name: "District 7",  borough: "Bronx",         score: 88, ref: 12450, diversion: "14.2%", complaints: 1847, organic: "High",   lng: -73.900, lat: 40.838 },
  { id: 1, name: "District 1",  borough: "Brooklyn",      score: 82, ref: 11820, diversion: "16.8%", complaints: 1623, organic: "High",   lng: -73.985, lat: 40.695 },
  { id: 2, name: "District 12", borough: "Queens",        score: 79, ref: 10950, diversion: "18.1%", complaints: 1204, organic: "Medium", lng: -73.825, lat: 40.755 },
  { id: 3, name: "District 9",  borough: "Manhattan",     score: 76, ref:  9870, diversion: "22.4%", complaints: 2156, organic: "Medium", lng: -73.945, lat: 40.805 },
  { id: 4, name: "District 3",  borough: "Bronx",         score: 85, ref:  9540, diversion: "13.7%", complaints: 1932, organic: "High",   lng: -73.915, lat: 40.825 },
  { id: 5, name: "District 14", borough: "Brooklyn",      score: 73, ref:  9120, diversion: "19.3%", complaints:  987, organic: "Medium", lng: -73.960, lat: 40.638 },
  { id: 6, name: "District 7",  borough: "Queens",        score: 70, ref:  8760, diversion: "20.1%", complaints:  876, organic: "Medium", lng: -73.792, lat: 40.710 },
  { id: 7, name: "District 1",  borough: "Staten Island", score: 68, ref:  8340, diversion: "17.5%", complaints:  654, organic: "Low",    lng: -74.060, lat: 40.645 },
  { id: 8, name: "District 4",  borough: "Manhattan",     score: 64, ref:  7890, diversion: "25.6%", complaints: 1543, organic: "Low",    lng: -73.978, lat: 40.745 },
  { id: 9, name: "District 5",  borough: "Brooklyn",      score: 61, ref:  7650, diversion: "21.2%", complaints: 1098, organic: "Medium", lng: -73.944, lat: 40.658 },
];

export const NEXUS_SITES = [
  { id: 0, name: "Dist 7 + PS 123",       borough: "Bronx",     eScore: 94, wScore: 88, nScore: 96, co2: "142 t/yr", lng: -73.880, lat: 40.840 },
  { id: 1, name: "Dist 1 + Navy Yard",    borough: "Brooklyn",  eScore: 89, wScore: 82, nScore: 91, co2: "128 t/yr", lng: -73.978, lat: 40.698 },
  { id: 2, name: "Dist 12 + Queens Lib",  borough: "Queens",    eScore: 87, wScore: 79, nScore: 88, co2: "115 t/yr", lng: -73.810, lat: 40.728 },
  { id: 3, name: "Dist 3 + Courthouse",   borough: "Bronx",     eScore: 85, wScore: 85, nScore: 87, co2: "134 t/yr", lng: -73.920, lat: 40.830 },
  { id: 4, name: "Dist 9 + Harlem Hosp",  borough: "Manhattan", eScore: 78, wScore: 76, nScore: 84, co2: "98 t/yr",  lng: -73.942, lat: 40.808 },
];

export const BOROUGH_DATA = [
  { name: "Bronx",         sites: 892,  hp: 234, savings: "$4.2M", co2: "1,890", sites5: "18", action: "BESS + Organics AD", wasteTons: 48200, diversion: 15.8, color: "#3B82F6" },
  { name: "Brooklyn",      sites: 1105, hp: 198, savings: "$3.8M", co2: "1,650", sites5: "15", action: "Solar + BESS",       wasteTons: 62400, diversion: 19.2, color: "#10B981" },
  { name: "Manhattan",     sites: 687,  hp: 142, savings: "$3.1M", co2: "1,420", sites5: "12", action: "BESS + Route Opt",   wasteTons: 38900, diversion: 24.1, color: "#F59E0B" },
  { name: "Queens",        sites: 1024, hp: 187, savings: "$3.5M", co2: "1,560", sites5: "14", action: "Solar + Organics",   wasteTons: 55100, diversion: 20.5, color: "#8B5CF6" },
  { name: "Staten Island", sites: 560,  hp: 86,  savings: "$1.8M", co2: "720",   sites5: "8",  action: "BESS + Composting",  wasteTons: 28300, diversion: 17.5, color: "#F97316" },
];

export const ENERGY_KPIS = [
  { icon: "🏢", iconBg: "rgba(59,130,246,.12)",   num: "4,268",  label: "Sites Analyzed",          sub: "Municipal buildings across 5 boroughs",  tag: null },
  { icon: "🔋", iconBg: "rgba(16,185,129,.12)",   num: "847",    label: "High-Priority Sites",     sub: "BESS score ≥ 70",                        tag: { txt: "▲ 19.8% of total", cls: "green" } },
  { icon: "💰", iconBg: "rgba(245,158,11,.12)",   num: "$12.4M", label: "Annual Savings Potential",sub: "If top 50 sites deploy BESS",            tag: null },
  { icon: "🌱", iconBg: "rgba(16,185,129,.12)",   num: "8,240",  label: "Tons CO₂ Offset/yr",      sub: "≈ 1,790 cars removed",                  tag: null },
];

export const WASTE_KPIS = [
  { icon: "🗑️", iconBg: "rgba(249,115,22,.12)",  num: "295K",   label: "Monthly Refuse (tons)",   sub: "Latest month, citywide",                tag: null },
  { icon: "♻️", iconBg: "rgba(20,184,166,.12)",  num: "21.3%",  label: "Diversion Rate",          sub: "Target: 30%",                           tag: { txt: "▼ 8.7% below target", cls: "red" } },
  { icon: "🚛", iconBg: "rgba(239,68,68,.12)",   num: "$418",   label: "Avg Disposal Cost/ton",   sub: "Across all facilities",                 tag: null },
  { icon: "🔥", iconBg: "rgba(139,92,246,.12)",  num: "1.2M",   label: "MWh WTE Potential/yr",    sub: "If 50% organics → AD",                  tag: null },
];

export const NEXUS_KPIS = [
  { icon: "📊", iconBg: "rgba(59,130,246,.12)",   num: "25",     label: "Datasets Integrated",     sub: "12 energy + 13 waste",                  tag: null },
  { icon: "💰", iconBg: "rgba(16,185,129,.12)",   num: "$19.7M", label: "Combined Savings/yr",     sub: "Energy + waste optimization",           tag: null },
  { icon: "🌱", iconBg: "rgba(16,185,129,.12)",   num: "12,400", label: "Total CO₂ Offset (tons/yr)", sub: "Energy + waste combined",            tag: null },
  { icon: "🏘️", iconBg: "rgba(139,92,246,.12)", num: "68%",    label: "EJ Area Coverage",         sub: "Equity-weighted deployment",            tag: null },
];

/** Helpers */
export function scoreColor(s) { return s >= 80 ? '#EF4444' : s >= 60 ? '#F59E0B' : '#3B82F6'; }
export function scoreBg(s)    { return s >= 80 ? 'rgba(239,68,68,.15)'  : s >= 60 ? 'rgba(245,158,11,.15)' : 'rgba(59,130,246,.15)'; }
export function scoreText(s)  { return s >= 80 ? '#FCA5A5' : s >= 60 ? '#FCD34D' : '#93C5FD'; }
export function dotR(s)       { return s >= 80 ? 6 : s >= 60 ? 5 : 4; }
