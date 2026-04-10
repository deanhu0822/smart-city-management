"""
Step 3: LLM-powered BESS site ranking and dispatch recommendations.
Supports both Claude API and Google Gemini API — switch via LLM_PROVIDER in config.
"""
import json
import os
import pandas as pd
from config import (
    LLM_PROVIDER, ANTHROPIC_API_KEY, GEMINI_API_KEY,
    CLAUDE_MODEL, GEMINI_MODEL, DEFAULT_WEIGHTS, PROCESSED_DATA_DIR,
)


# ---------------------------------------------------------------------------
# LLM Client Abstraction
# ---------------------------------------------------------------------------

def _call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """Call Claude API and return the text response."""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_gemini(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """Call Google Gemini API and return the text response."""
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=f"{system_prompt}\n\n{user_prompt}",
        config={"max_output_tokens": max_tokens},
    )
    return response.text


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """Route to the configured LLM provider."""
    if LLM_PROVIDER == "claude":
        return _call_claude(system_prompt, user_prompt, max_tokens)
    elif LLM_PROVIDER == "gemini":
        return _call_gemini(system_prompt, user_prompt, max_tokens)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


# ---------------------------------------------------------------------------
# BESS Priority Scoring
# ---------------------------------------------------------------------------

RANKING_SYSTEM_PROMPT = """You are an expert energy analyst specializing in Battery Energy Storage System (BESS) deployment for municipal buildings in New York City.

Your task: Given a batch of municipal site profiles, score each site from 0-100 on its suitability for BESS installation. Consider these factors and their weights:

- Energy Cost Reduction Potential (weight: {w_energy}): Sites with high electricity consumption and costs benefit most from peak-shaving with BESS.
- Grid Resilience (weight: {w_resilience}): Sites in areas with high demand variability or aging infrastructure need backup storage.
- Solar Synergy (weight: {w_solar}): Sites with high solar potential but mismatched demand curves (high evening use) benefit from solar+storage pairing.
- Equity Impact (weight: {w_equity}): Sites in Environmental Justice areas should be prioritized for clean energy investment.
- EV Infrastructure Support (weight: {w_ev}): Sites near EV charging clusters face growing demand that BESS can buffer.

Return ONLY a valid JSON array. Each element must have:
- "site_id": integer
- "bess_score": integer 0-100
- "top_reason": string (1 sentence — the #1 reason this site should or shouldn't get BESS)
- "recommended_capacity_kwh": integer (estimated BESS size in kWh)
- "estimated_annual_savings_usd": integer

No markdown, no explanation outside the JSON."""


def score_sites_batch(sites_df: pd.DataFrame, batch_size: int = 20) -> pd.DataFrame:
    """
    Score all sites using the LLM in batches.
    Returns DataFrame with bess_score, top_reason, recommended_capacity_kwh, estimated_annual_savings_usd.
    """
    weights = DEFAULT_WEIGHTS
    system = RANKING_SYSTEM_PROMPT.format(
        w_energy=weights["energy_cost_reduction"],
        w_resilience=weights["grid_resilience"],
        w_solar=weights["solar_synergy"],
        w_equity=weights["equity_impact"],
        w_ev=weights["ev_infrastructure"],
    )

    # Select columns to send to LLM (avoid sending raw lat/lon for token efficiency)
    feature_cols = [
        "site_id", "agency", "address", "borough",
        "estimated_annual_production_kwh", "solar_score", "roof_score",
        "equity_flag", "ev_ports_in_borough", "ev_density_score",
        "area_total_savings", "area_electric_savings",
    ]
    available_cols = [c for c in feature_cols if c in sites_df.columns]

    all_results = []
    total = len(sites_df)

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = sites_df.iloc[start:end]
        print(f"[SCORING] Sites {start+1}–{end} of {total}...")

        # Build the user prompt with site data
        batch_data = batch[available_cols].to_dict(orient="records")
        user_prompt = (
            f"Score these {len(batch_data)} NYC municipal sites for BESS installation.\n\n"
            f"Site data:\n{json.dumps(batch_data, indent=2, default=str)}"
        )

        try:
            response_text = call_llm(system, user_prompt)
            # Parse JSON from response (strip any accidental markdown fencing)
            clean = response_text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
            results = json.loads(clean)
            all_results.extend(results)
        except Exception as e:
            print(f"  [ERROR] Batch {start}-{end}: {e}")
            # Fallback: assign neutral scores
            for _, row in batch.iterrows():
                all_results.append({
                    "site_id": row["site_id"],
                    "bess_score": 50,
                    "top_reason": "Scoring failed — manual review needed",
                    "recommended_capacity_kwh": 0,
                    "estimated_annual_savings_usd": 0,
                })

    scores_df = pd.DataFrame(all_results)
    return scores_df


# ---------------------------------------------------------------------------
# Dispatch Recommendation
# ---------------------------------------------------------------------------

DISPATCH_SYSTEM_PROMPT = """You are a BESS dispatch optimization expert. Given a site's energy profile, recommend an optimal daily charge/discharge schedule.

Consider:
- Time-of-use electricity rates in NYC (peak: 8AM-10PM summer, 8AM-10PM winter; off-peak otherwise)
- Solar generation curve (if solar potential exists): peaks 10AM-3PM
- EV charging patterns (if EV stations nearby): peaks 7-9AM and 5-8PM
- Building demand patterns: office buildings peak during business hours, residential peaks morning/evening

Return ONLY valid JSON with:
- "strategy": string (1-2 sentence summary)
- "schedule": array of 24 objects, one per hour (0-23), each with:
  - "hour": integer
  - "action": "charge" | "discharge" | "idle"
  - "kw": number (power in kW, positive for both charge and discharge)
  - "reason": string (brief)
- "projected_annual_savings_usd": integer
- "peak_reduction_kw": number
- "co2_offset_tons": number (annual)

No markdown outside the JSON."""


def get_dispatch_recommendation(site: dict) -> dict:
    """Get a dispatch schedule recommendation for a single site."""
    user_prompt = (
        f"Recommend a BESS dispatch schedule for this NYC municipal site:\n\n"
        f"{json.dumps(site, indent=2, default=str)}"
    )

    try:
        response_text = call_llm(DISPATCH_SYSTEM_PROMPT, user_prompt)
        clean = response_text.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(clean)
    except Exception as e:
        print(f"[ERROR] Dispatch recommendation failed: {e}")
        return {"strategy": "Error generating recommendation", "schedule": []}


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def run_ranking_pipeline():
    """Full Phase 3 pipeline: load features → score with LLM → save results."""
    # Load unified site table
    sites_path = os.path.join(PROCESSED_DATA_DIR, "unified_sites.csv")
    if not os.path.exists(sites_path):
        print("[ERROR] Run feature_engineering.py first to generate unified_sites.csv")
        return

    sites = pd.read_csv(sites_path)
    print(f"[PIPELINE] Loaded {len(sites)} sites from {sites_path}\n")

    # Score all sites
    scores = score_sites_batch(sites)

    # Merge scores back
    ranked = sites.merge(scores, on="site_id", how="left")
    ranked = ranked.sort_values("bess_score", ascending=False).reset_index(drop=True)
    ranked["rank"] = range(1, len(ranked) + 1)

    # Save ranked results
    ranked_path = os.path.join(PROCESSED_DATA_DIR, "ranked_sites.csv")
    ranked.to_csv(ranked_path, index=False)
    print(f"\n[SAVED] {ranked_path}")

    # Get dispatch recommendations for top 10 sites
    print("\n[DISPATCH] Generating schedules for top 10 sites...")
    top_10 = ranked.head(10)
    dispatch_results = []

    for _, row in top_10.iterrows():
        site_info = row.to_dict()
        dispatch = get_dispatch_recommendation(site_info)
        dispatch["site_id"] = row["site_id"]
        dispatch["address"] = row.get("address", "")
        dispatch_results.append(dispatch)
        print(f"  Site #{int(row['rank'])}: {row.get('address', 'N/A')} — {dispatch.get('strategy', 'N/A')}")

    # Save dispatch recommendations
    dispatch_path = os.path.join(PROCESSED_DATA_DIR, "dispatch_recommendations.json")
    with open(dispatch_path, "w") as f:
        json.dump(dispatch_results, f, indent=2, default=str)
    print(f"\n[SAVED] {dispatch_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("BESS PRIORITY RANKING — TOP 10 SITES")
    print("=" * 60)
    for _, row in top_10.iterrows():
        print(f"  #{int(row['rank']):>3}  Score: {row.get('bess_score', 'N/A'):>3}  "
              f"{row.get('borough', ''):>10}  {row.get('address', 'N/A')}")
        print(f"        → {row.get('top_reason', '')}")
    print("=" * 60)

    return ranked, dispatch_results


if __name__ == "__main__":
    run_ranking_pipeline()
