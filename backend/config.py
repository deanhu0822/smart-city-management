"""
Configuration for BESS Predictor — Cloud Solution
Switch between Claude API and Gemini API by setting LLM_PROVIDER.
"""
import os

# --- LLM Provider ---
# Options: "claude" or "gemini"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "claude")

# API Keys (set via environment variables)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model IDs
CLAUDE_MODEL = "claude-sonnet-4-20250514"
GEMINI_MODEL = "gemini-2.0-flash"

# --- NYC Open Data ---
SOCRATA_BASE = "https://data.cityofnewyork.us/resource"
DATASETS = {
    "energy_savings":    {"id": "bug8-9f3g", "label": "Energy Cost Savings Program"},
    "projected_cost":    {"id": "tyv9-j3ti", "label": "Projected Citywide Energy Cost"},
    "electric_consumption": {"id": "jr24-e7cr", "label": "Electric Consumption & Cost"},
    "ev_stations":       {"id": "fc53-9hrv", "label": "NYC EV Fleet Station Network"},
    "solar_readiness":   {"id": "cfz5-6fvh", "label": "Municipal Solar-Readiness Assessment"},
    "dcas_energy":       {"id": "ubdi-jgw2", "label": "DCAS Managed Building Energy Usage"},
    "ll84_monthly":      {"id": "fvp3-gcb2", "label": "Local Law 84 Monthly Data"},
}

# --- Scoring Weights (tunable) ---
DEFAULT_WEIGHTS = {
    "energy_cost_reduction": 0.25,
    "grid_resilience":       0.20,
    "solar_synergy":         0.20,
    "equity_impact":         0.20,
    "ev_infrastructure":     0.15,
}

# --- Paths ---
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
