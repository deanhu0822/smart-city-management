"""
BESS Predictor — Full Pipeline Runner
Run this to execute the entire cloud-based pipeline end-to-end.

Usage:
    # With Claude API (default)
    export ANTHROPIC_API_KEY="sk-ant-..."
    export LLM_PROVIDER="claude"
    python run_pipeline.py

    # With Gemini API
    export GEMINI_API_KEY="AIza..."
    export LLM_PROVIDER="gemini"
    python run_pipeline.py
"""
import sys
import time


def main():
    print("=" * 60)
    print("  BESS PREDICTOR FOR NYC — CLOUD PIPELINE")
    print("  Smart City Management: Energy Storage & Distribution")
    print("=" * 60)

    start = time.time()

    # --- Phase 1: Data Ingestion ---
    print("\n" + "─" * 60)
    print("  PHASE 1: DATA ACQUISITION")
    print("─" * 60)
    from data_ingestion import download_all
    download_all()

    # --- Phase 2: Feature Engineering ---
    print("\n" + "─" * 60)
    print("  PHASE 2: FEATURE ENGINEERING")
    print("─" * 60)
    from feature_engineering import build_site_table
    sites = build_site_table()
    print(f"  → {len(sites)} sites with {len(sites.columns)} features")

    # --- Phase 3a: LLM-Powered Ranking ---
    print("\n" + "─" * 60)
    print("  PHASE 3a: LLM-POWERED BESS SITE RANKING")
    print("─" * 60)
    from config import LLM_PROVIDER
    print(f"  Provider: {LLM_PROVIDER.upper()}")
    from llm_ranker import run_ranking_pipeline
    ranked, dispatch_recs = run_ranking_pipeline()

    # --- Phase 3b: Physics-Based Dispatch Simulation ---
    print("\n" + "─" * 60)
    print("  PHASE 3b: DISPATCH SIMULATION")
    print("─" * 60)
    from dispatch_simulator import simulate_top_sites
    simulate_top_sites(n=10)

    # --- Done ---
    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s total")
    print(f"  Results in: data/processed/")
    print(f"    • ranked_sites.csv          — All sites ranked by BESS priority")
    print(f"    • dispatch_recommendations.json — LLM dispatch strategies (top 10)")
    print(f"    • dispatch_simulations.json — Physics-based simulations (top 10)")
    print("=" * 60)


if __name__ == "__main__":
    main()
