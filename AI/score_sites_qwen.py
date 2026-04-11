"""
Job A: Score municipal sites using Qwen 3 80B locally on GB10.

OPTIMIZED VERSION:
  - Thinking disabled (no <think> chain — 5-10x faster)
  - Parallel batches (4 concurrent requests)
  - Smart filtering (skip sites with no useful data)
  - Batch size 50

Reads:  data/gold/unified_sites.parquet + dispatch/site_profiles.parquet
Writes: data/gold/ranked_sites.parquet + top50_scored.json

Usage (on GB10):
    python AI/score_sites_qwen.py

    # Adjust concurrency and batch size:
    BATCH_SIZE=50 WORKERS=4 python AI/score_sites_qwen.py
"""
import json
import os
import sys
import time
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
QWEN_URL = os.getenv("QWEN_URL", "http://localhost:8000/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen3-80b")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
WORKERS = int(os.getenv("WORKERS", "4"))  # parallel requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

# ---------------------------------------------------------------------------
# Compact System Prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Score NYC sites for BESS (battery) + waste optimization. Return JSON array only.

Input fields: site, borough, ej (Environmental Justice), roof, solar_kwh, kwh_mo, ev_1km, compost_1km.

Score 0-100:
- energy_score: BESS priority. High solar+consumption+EJ = high.
- waste_score: Waste opportunity. EJ + no compost nearby = high.
- nexus_score: Combined synergy. EJ + solar + EV + waste = highest.

Return ONLY JSON array. Each element:
{"site":"name","energy_score":N,"waste_score":N,"nexus_score":N,"recommended_bess_kwh":N,"estimated_annual_savings_usd":N,"top_recommendation":"one sentence","reasoning":"1-2 sentences"}"""


# ---------------------------------------------------------------------------
# Build features
# ---------------------------------------------------------------------------
def build_site_features(sites_df, profiles_df):
    """Build compact feature dicts — 8 fields per site."""
    profile_map = {}
    for _, p in profiles_df.iterrows():
        profile_map[str(p["site_id"])] = p

    features = []
    for _, row in sites_df.iterrows():
        site_name = str(row.get("Site", "Unknown"))
        p = profile_map.get(site_name, {})
        solar_prod = p.get("solar_production_kwh_yr", row.get("Estimated Annual Production", 0))

        features.append({
            "site": site_name,
            "borough": str(row.get("Borough", "")),
            "ej": str(row.get("Environmental Justice Area", "No")),
            "roof": str(row.get("Roof Condition", "?"))[:4],
            "solar_kwh": _safe_num(solar_prod),
            "kwh_mo": round(float(p.get("avg_monthly_total_kwh", 0) or 0), 0),
            "ev_1km": bool(row.get("ev_within_1km", False)),
            "compost_1km": bool(row.get("compost_within_1km", False)),
        })
    return features


def _safe_num(val):
    try:
        v = float(str(val).replace(",", "").replace("$", ""))
        return 0 if np.isnan(v) or np.isinf(v) else round(v, 1)
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------------------
# Filter: only score sites worth scoring
# ---------------------------------------------------------------------------
def filter_scorable(features):
    """Split into sites worth LLM-scoring vs. heuristic-only."""
    to_score = []
    to_fallback = []

    for f in features:
        has_data = (
            f["solar_kwh"] > 0 or
            f["kwh_mo"] > 0 or
            f["ej"] == "Yes" or
            f["roof"] in ["Good", "good", "Fair", "fair"]
        )
        if has_data:
            to_score.append(f)
        else:
            to_fallback.append(f)

    return to_score, to_fallback


# ---------------------------------------------------------------------------
# Score a single batch (called by worker threads)
# ---------------------------------------------------------------------------
def score_batch(client, batch_features, batch_id):
    """Send one batch to Qwen. Returns (batch_id, results)."""
    user_msg = (
        f"Score these {len(batch_features)} NYC sites.\n\n"
        f"{json.dumps(batch_features, default=str)}"
    )

    try:
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.1,
            max_tokens=4096,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )

        text = response.choices[0].message.content.strip()

        # Safety: strip any leftover think tags
        if "</think>" in text:
            text = text.split("</think>")[-1].strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        results = json.loads(text)
        if not isinstance(results, list):
            raise ValueError(f"Expected list, got {type(results)}")

        return batch_id, results, "LLM"

    except Exception as e:
        return batch_id, _fallback_scores(batch_features), f"FALLBACK({e})"


def _fallback_scores(batch_features):
    """Fast heuristic scoring."""
    results = []
    for f in batch_features:
        is_ej = f.get("ej", "No") == "Yes"
        has_solar = f.get("solar_kwh", 0) > 0
        good_roof = f.get("roof", "?").lower() in ["good", "fair"]
        has_ev = f.get("ev_1km", False)
        has_compost = f.get("compost_1km", False)

        e = 40 + (15 if has_solar else 0) + (10 if good_roof else 0) + (10 if is_ej else 0) + (5 if has_ev else 0)
        w = 40 + (10 if not has_compost else 0) + (15 if is_ej else 0)
        n = int((e + w) / 2) + (10 if is_ej and has_solar else 0)

        results.append({
            "site": f["site"],
            "energy_score": min(100, e),
            "waste_score": min(100, w),
            "nexus_score": min(100, n),
            "recommended_bess_kwh": 250 if has_solar else 100,
            "estimated_annual_savings_usd": 10000 if has_solar else 3000,
            "top_recommendation": "Install BESS with solar" if has_solar else "Evaluate solar-readiness",
            "reasoning": "Heuristic score.",
        })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 65)
    print("  JOB A: SITE SCORING — Qwen 3 80B (Local on GB10)")
    print(f"  Endpoint:   {QWEN_URL}")
    print(f"  Model:      {QWEN_MODEL}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Workers:    {WORKERS} parallel")
    print(f"  Thinking:   DISABLED (fast mode)")
    print("=" * 65)

    # Load data
    sites_path = os.path.join(GOLD_DIR, "unified_sites.parquet")
    profiles_path = os.path.join(GOLD_DIR, "dispatch", "site_profiles.parquet")

    if not os.path.exists(sites_path):
        print(f"\n[ERROR] {sites_path} not found.")
        sys.exit(1)

    sites = pd.read_parquet(sites_path)
    profiles = pd.read_parquet(profiles_path) if os.path.exists(profiles_path) else pd.DataFrame()
    print(f"\n[LOADED] {len(sites)} sites, {len(profiles)} profiles")

    # Build features
    all_features = build_site_features(sites, profiles)

    # Filter: LLM-score only sites with useful data
    to_score, to_fallback = filter_scorable(all_features)
    print(f"[FILTER] {len(to_score)} sites for LLM scoring, {len(to_fallback)} for heuristic")

    # Heuristic score the low-data sites immediately
    fallback_results = _fallback_scores(to_fallback)

    # Connect to Qwen
    client = OpenAI(base_url=QWEN_URL, api_key="not-needed")

    print(f"\n[TEST] Pinging {QWEN_URL}...")
    try:
        models = client.models.list()
        print(f"  → Connected. Models: {[m.id for m in models.data]}")
    except Exception as e:
        print(f"  → Connection failed: {e}")
        print(f"  → FULL FALLBACK mode")
        all_results = _fallback_scores(to_score) + fallback_results
        _save_results(sites, all_results)
        return

    # Build batches
    batches = []
    for i in range(0, len(to_score), BATCH_SIZE):
        batches.append(to_score[i:i + BATCH_SIZE])

    total_batches = len(batches)
    print(f"\n[SCORING] {len(to_score)} sites in {total_batches} batches, {WORKERS} workers parallel\n")

    # Run parallel
    llm_results = []
    start_time = time.time()
    completed = 0
    llm_count = 0
    fb_count = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(score_batch, client, batch, idx): idx
            for idx, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            batch_id, results, method = future.result()
            completed += 1
            llm_results.extend(results)

            if "FALLBACK" in method:
                fb_count += len(results)
            else:
                llm_count += len(results)

            elapsed = time.time() - start_time
            rate = completed / elapsed if elapsed > 0 else 0
            eta = (total_batches - completed) / rate / 60 if rate > 0 else 0

            print(f"  [{completed}/{total_batches}] batch {batch_id} → "
                  f"{len(results)} sites ({method}) "
                  f"[{elapsed:.0f}s, ~{eta:.1f}min left]")

    # Combine LLM + fallback results
    all_results = llm_results + fallback_results

    total_time = time.time() - start_time
    _save_results(sites, all_results)

    print(f"\n{'=' * 65}")
    print(f"  SCORING COMPLETE")
    print(f"  Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"  LLM scored:      {llm_count} sites")
    print(f"  Heuristic:       {len(fallback_results) + fb_count} sites")
    print(f"  Throughput:      {len(all_results) / total_time:.1f} sites/sec")
    print(f"{'=' * 65}")


def _save_results(sites, all_results):
    """Merge scores onto sites and save."""
    scores_df = pd.DataFrame(all_results)

    site_col = "Site" if "Site" in sites.columns else "site"
    sites_copy = sites.copy()
    sites_copy["_merge_key"] = sites_copy[site_col].astype(str)
    scores_df["_merge_key"] = scores_df["site"].astype(str)

    scores_dedup = scores_df.drop_duplicates(subset=["_merge_key"], keep="first")

    ranked = sites_copy.merge(
        scores_dedup[["_merge_key", "energy_score", "waste_score", "nexus_score",
                       "recommended_bess_kwh", "estimated_annual_savings_usd",
                       "top_recommendation", "reasoning"]],
        on="_merge_key", how="left"
    ).drop(columns=["_merge_key"])

    for col in ["energy_score", "waste_score", "nexus_score"]:
        ranked[col] = ranked[col].fillna(50).astype(int)
    ranked["recommended_bess_kwh"] = ranked["recommended_bess_kwh"].fillna(100).astype(int)
    ranked["estimated_annual_savings_usd"] = ranked["estimated_annual_savings_usd"].fillna(0).astype(int)
    ranked["top_recommendation"] = ranked["top_recommendation"].fillna("Review needed")
    ranked["reasoning"] = ranked["reasoning"].fillna("")

    ranked = ranked.sort_values("nexus_score", ascending=False).reset_index(drop=True)
    ranked["rank"] = range(1, len(ranked) + 1)

    out_path = os.path.join(GOLD_DIR, "ranked_sites.parquet")
    ranked.to_parquet(out_path, index=False)
    print(f"\n[SAVED] {out_path} — {len(ranked)} sites ranked")

    # Top 50 JSON for dashboard
    top50 = ranked.head(50)
    top50_records = []
    for _, row in top50.iterrows():
        top50_records.append({
            "rank": int(row["rank"]),
            "site": str(row.get("Site", row.get("site", ""))),
            "address": str(row.get("Address", "")),
            "borough": str(row.get("Borough", "")),
            "agency": str(row.get("Agency", "")),
            "env_justice": str(row.get("Environmental Justice Area", "")),
            "energy_score": int(row.get("energy_score", 50)),
            "waste_score": int(row.get("waste_score", 50)),
            "nexus_score": int(row.get("nexus_score", 50)),
            "recommended_bess_kwh": int(row.get("recommended_bess_kwh", 0)),
            "estimated_annual_savings_usd": int(row.get("estimated_annual_savings_usd", 0)),
            "top_recommendation": str(row.get("top_recommendation", "")),
            "reasoning": str(row.get("reasoning", "")),
        })

    top50_path = os.path.join(GOLD_DIR, "top50_scored.json")
    with open(top50_path, "w") as f:
        json.dump(top50_records, f, indent=2, default=str)
    print(f"[SAVED] {top50_path}")

    print(f"\n  TOP 10 (by Nexus Score):")
    print("  " + "─" * 60)
    for _, row in ranked.head(10).iterrows():
        print(f"  #{int(row['rank']):>3}  "
              f"E:{int(row.get('energy_score',0)):>3}  "
              f"W:{int(row.get('waste_score',0)):>3}  "
              f"N:{int(row.get('nexus_score',0)):>3}  "
              f"{str(row.get('Borough','')):>12}  "
              f"{str(row.get('Site', row.get('site','')))[:35]}")
    print("  " + "─" * 60)


if __name__ == "__main__":
    main()
