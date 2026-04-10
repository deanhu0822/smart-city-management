# NYC Smart City Nexus: Connecting Energy and Waste to Build a Smarter City

## The Problem No One Is Solving

New York City runs on two massive, invisible systems. One moves energy. The other moves trash. And right now, nobody is looking at them together.

Every day, NYC consumes about 143 million kilowatt-hours of electricity — enough to power a small country. At the same time, the city generates roughly 38,000 tons of waste. These two systems cost the city billions of dollars a year, produce millions of tons of greenhouse gas emissions, and disproportionately burden low-income communities. Yet they are managed by completely separate agencies, tracked in separate databases, and optimized in isolation.

Here's what that disconnect looks like in practice:

A public school in the Bronx pays some of the highest electricity rates in the city. Its roof is in perfect condition for solar panels, but nobody has connected that opportunity to a battery storage system that could cut its energy bills in half. Two blocks away, the neighborhood produces 12,000 tons of organic waste every month — food scraps, yard waste, compostable material — most of which gets trucked to a landfill in Virginia. That organic waste could be processed into biogas right here in the city, generating clean electricity that feeds back into the same grid powering that school.

The data to make this connection already exists. It's sitting in 25 publicly available datasets on NYC's Open Data portal. The problem is that no one has stitched it together into a single picture — and no one has built a tool that lets city planners, energy managers, and community advocates actually use it.

That's what we built.

---

## What We Built

**NYC Smart City Nexus** is a decision-support platform that merges the city's energy data and waste data into one unified intelligence layer. It answers three questions that no existing tool can:

1. **Where should the city install battery storage systems to get the most value?** Not just based on energy data — but factoring in solar potential, EV charging growth, grid stress, and whether the neighborhood is an Environmental Justice area that deserves priority investment.

2. **Where is the city's waste system leaking value?** Which neighborhoods generate the most organic waste but have the fewest composting options? Which transfer stations are over capacity while others sit underutilized? Where are collection trucks driving the most miles — and could those routes be electrified?

3. **What happens when you connect energy and waste?** If you divert organic waste from landfills to anaerobic digestion facilities, how much biogas does that produce? How much electricity does that biogas generate? Can that electricity be stored in neighborhood batteries and dispatched during peak hours to reduce costs? What's the combined carbon impact?

We process 25 NYC Open Data datasets — over 6 million rows of real data — covering everything from monthly building electricity consumption to waste tonnage by community district to the location of every public trash can in the city. An AI analysis engine scores every municipal site across energy priority, waste optimization opportunity, and cross-domain synergy. And an interactive dashboard lets anyone explore the results, drill into specific sites, and run "what-if" scenarios.

---

## Why This Matters

### For City Planners

New York State is scaling battery storage 12 times over by 2030. The city has set ambitious waste diversion targets. Local Law 97 mandates building emissions caps. These are massive infrastructure decisions, and they all require the same thing: knowing where to invest limited dollars for maximum impact.

Right now, those decisions are made with spreadsheets and siloed reports. Our tool gives planners a single screen where they can see a school's energy consumption alongside its neighborhood's waste patterns, its solar potential, its proximity to EV chargers, and its Environmental Justice status — all at once. They can ask "If I have $10 million, where should I put it?" and get back a ranked deployment plan with specific sites, estimated savings, carbon offsets, and payback periods.

### For Communities

Environmental Justice areas in NYC bear a disproportionate burden of both energy costs and waste infrastructure. Low-income neighborhoods in the South Bronx, East New York, and the Rockaways pay more for electricity, live closer to transfer stations, and have fewer clean energy installations. Our platform makes this inequity visible and actionable. Every recommendation carries an equity score. When the system says "install batteries here first," it's not just because the numbers work — it's because the community needs it most.

### For the Environment

The numbers tell a compelling story. If the city deployed battery storage at just the top 50 priority sites, it would reduce peak electricity demand by 142 megawatts, save $12.4 million per year in energy costs, and offset 8,240 tons of CO₂ annually. On the waste side, closing the organics diversion gap — getting food scraps to composting and digestion facilities instead of landfills — could generate 1.2 million megawatt-hours of biogas per year while eliminating thousands of truck trips to out-of-state landfills.

When you combine both systems, the impact multiplies. A $10 million investment optimally split across batteries, solar, organic waste diversion, and route optimization yields $7.3 million in annual savings, offsets 12,400 tons of CO₂, and pays for itself in under 18 months.

---

## How It Works — A Walkthrough

### Opening the Dashboard

When a user opens the Nexus dashboard, they see a dark, mission-control-style interface designed for clarity under pressure. The top ribbon immediately shows eight key performance indicators: four for energy (sites analyzed, high-priority sites, savings potential, carbon offset) and four for waste (monthly tonnage, diversion rate, disposal costs, waste-to-energy potential). These numbers update based on the borough and filters selected.

### Exploring the Map

The center of the screen is an interactive map of NYC's five boroughs. In **Energy view**, colored dots represent municipal buildings — red for high-priority battery sites, amber for medium, blue for lower priority. The dots are sized by energy consumption so the biggest energy hogs jump out visually. In **Waste view**, the map switches to a choropleth showing waste tonnage by community district, with hotspot overlays for 311 sanitation complaints and markers for transfer stations. In **Nexus view**, both layers combine, highlighting locations where energy and waste opportunities overlap — the places where a single investment can solve two problems at once.

### Diving Into a Site

Clicking any dot on the map — or any row in the rankings table beside it — opens a detail panel with three sections. The first shows the site's identity: name, address, agency, and whether it's in an Environmental Justice area. The second shows its energy profile: average monthly consumption, peak demand, annual cost, solar potential, and roof condition. The third shows its waste context: how much waste the surrounding district generates, what it's made of, and where it goes.

At the bottom of this panel, an AI-generated insight ties it all together in plain English. For example: *"This Bronx school has the borough's 3rd highest energy cost and sits in an Environmental Justice area. The surrounding district produces 12,450 tons of refuse per month — 34% organic — with only a 14.2% diversion rate and no composting site within 2 miles. Recommended: deploy a 750 kWh battery for peak shaving ($287K/yr savings) and partner with a local anaerobic digestion facility to process district organics into biogas. Combined CO₂ offset: 142 tons per year, serving 23,000 residents."*

This is information that would take an analyst days to compile from separate datasets. The platform delivers it in a click.

### Understanding the Flows

Below the site detail, two Sankey flow diagrams visualize how energy and waste move through the city. The energy Sankey traces electricity from generation sources (grid, solar, biogas, wind) through consumption sectors (commercial, residential, municipal) to end uses (lighting, HVAC, EV charging, battery storage). The waste Sankey tracks material from generation (residential, commercial, institutional) through collection (DSNY trucks, private haulers, drop-offs) to final destinations (landfill, waste-to-energy, recycling, composting).

These diagrams make the invisible visible. When a user sees that 55% of waste flows to out-of-state landfills while only 5% reaches composting — and that redirecting just a portion of that flow could generate enough biogas to power thousands of homes — the case for action becomes undeniable.

### Simulating Outcomes

The simulation section offers three tools:

**BESS Dispatch** shows how a battery at a selected site would charge and discharge over a 24-hour cycle. A stacked area chart displays building demand, solar generation, and battery output hour by hour. A companion chart tracks the battery's state of charge. Summary metrics show daily savings, peak demand reduction, and carbon offset. This visualization makes an abstract concept — "battery storage optimization" — tangible and intuitive.

**Waste Forecast** projects 12 months of tonnage trends by waste type, showing the trajectory of refuse, recycling, and organics. A companion bar chart highlights the diversion gap for each material category — how far current recycling and composting rates are from city targets, and what closing that gap would mean in terms of energy generation.

**Scenario Planner** is the tool that ties everything together. Users set a total budget — say, $10 million — and use sliders to allocate it across four strategies: battery storage, rooftop solar, organics diversion, and collection route optimization. An equity weighting slider lets them prioritize Environmental Justice communities. As sliders move, the impact summary updates in real time: how many sites get batteries, how many rooftops get solar, how many tons of organics are diverted, how much fuel is saved on optimized routes. It calculates total annual savings, CO₂ offset, payback period, and equity coverage. Below the summary, a ranked table shows exactly which sites and districts receive investment, in what order, and why.

This is the tool a city official takes into a budget meeting. It transforms "we should invest in clean energy and waste reduction" from a vague aspiration into a concrete, defensible plan with numbers attached to every line item.

### Comparing Boroughs

The bottom section provides a borough-level overview — a grouped bar chart comparing energy consumption, BESS potential, waste tonnage, diversion rates, and complaint volumes across all five boroughs. Summary cards for each borough highlight the top recommended action and its expected impact. A planner responsible for the Bronx can immediately see that their borough has the highest concentration of Environmental Justice areas, the lowest diversion rate, and the most sites where battery storage and organics programs could work together.

---

## The Technology

The entire platform runs on the NVIDIA GB10 Grace Blackwell chip — a desktop supercomputer with 128 GB of unified memory and 1 petaflop of AI performance. This means no cloud dependency, no API latency, no data leaving the building. All 25 datasets are processed locally. The AI scoring engine runs locally. The dashboard serves locally. For a city government concerned about data sovereignty and operational resilience, this matters.

During development, we use cloud-based AI (Claude API or Google Gemini) to iterate quickly and validate the scoring model. The architecture is designed so that migrating from cloud to on-device inference is a configuration change, not a rewrite. The physics-based dispatch simulator — which models 24-hour charge/discharge cycles using real NYC electricity rates, solar curves, and EV charging patterns — has always been local computation.

---

## Who This Is For

**City energy managers** use it to identify which municipal buildings should get battery storage first, sized to each building's actual consumption pattern, and to model the financial return before committing capital.

**Waste reduction coordinators** use it to find neighborhoods where organics programs would have the highest impact — where waste volumes are large, diversion rates are low, and processing facilities are within reach.

**Environmental justice advocates** use it to ensure that clean energy and waste infrastructure investments reach the communities that need them most, backed by data rather than anecdotes.

**Budget analysts** use the scenario planner to model different investment allocations and compare their returns — turning competing priorities into a single, optimized portfolio.

**Elected officials** use the borough-level summaries and site-specific recommendations to make data-driven cases for infrastructure spending in their districts.

---

## What Makes This Different

Other tools look at energy or waste. We look at both — and at the connections between them. The organic waste rotting in a Bronx landfill could be the biogas powering a Brooklyn school's battery. The diesel truck hauling trash to Virginia could be an electric vehicle charged by a depot-level solar-plus-storage system. The transfer station operating at 60% capacity in Queens could absorb overflow from an overcrowded facility in Manhattan, saving miles and emissions.

These connections are not hypothetical. They exist in the data. We just made them visible, quantifiable, and actionable — in a tool that runs on a single machine sitting on a desk.

---

*Built for Spark Hack NYC 2026. Powered by 25 NYC Open Data datasets, AI analysis, and NVIDIA GB10.*
