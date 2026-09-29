"""Konstanten, Regler-Grenzen und feste Seed-Mengen der Demo "Distributionszentren-Standortplanung"."""

# --- Regler (Netz) ---------------------------------------------------------------------------------------------
SITES_MIN, SITES_MAX, DEFAULT_SITES = 6, 24, 18
CUSTOMERS_MIN, CUSTOMERS_MAX, DEFAULT_CUSTOMERS = 15, 60, 40
FIXED_MIN, FIXED_MAX, DEFAULT_FIXED, FIXED_STEP = 25, 400, 100, 25
DEFAULT_SEED = 1
SEED_MAX = 2_000_000_000

# --- Akt 1: Faustregel "1 DC je N Kunden" ----------------------------------------------------------------------
PER_DC_MIN, PER_DC_MAX, DEFAULT_PER_DC = 2, 14, 5
PER_DC_MARKERS = (3, 5, 8, 12)          # in der Vorab-Messreihe gemessene Faustregeln, als Marker auf der Kurve

# --- Akt 2: Nachfrageverschiebung T0 -> T1 ---------------------------------------------------------------------
REGIONS = {"half": "halbe Karte", "quarter": "ein Kartenviertel"}
DEFAULT_REGION = "half"
GROWTH_MIN, GROWTH_MAX, DEFAULT_GROWTH, GROWTH_STEP = 1.0, 5.0, 1.8, 0.1
SHRINK_MIN, SHRINK_MAX, DEFAULT_SHRINK, SHRINK_STEP = 0.2, 1.0, 0.7, 0.05

# --- feste Seed-Mengen (unabhängig vom Nutzer-Seed) ------------------------------------------------------------
DIST_SEEDS = tuple(range(500001, 500041))
SWEEP_SEEDS = DIST_SEEDS[:20]

COLORS = {"open": "#2ca02c", "closed": "#9aa0a6", "old_open": "#1f77b4", "new_open": "#2ca02c",
          "kept_open": "#6a3d9a", "customer": "#7f8c8d", "line": "#9aa0a6", "opt": "#111111",
          "rule": "#d62728", "kmeans": "#ff7f0e", "topdemand": "#8c564b"}
LABELS = {"opt": "Optimum (k frei)", "rule": "Faustregel", "kmeans": "gewichtetes k-Means", "topdemand": "größte Nachfragezentren"}

# --- Presets -----------------------------------------------------------------------------------------------------
_BASE = dict(sites=DEFAULT_SITES, customers=DEFAULT_CUSTOMERS, fixed=DEFAULT_FIXED, seed=DEFAULT_SEED,
             per_dc=DEFAULT_PER_DC, region=DEFAULT_REGION, growth=DEFAULT_GROWTH, shrink=DEFAULT_SHRINK)
PRESETS = {
    "🗺️ Standardnetz": {**_BASE},
    "📏 Grobe Faustregel": {**_BASE, "per_dc": 3},
    "🚀 Starke Verschiebung": {**_BASE, "growth": 2.8, "shrink": 0.5},
    "🧭 Konzentriertes Wachstum": {**_BASE, "region": "quarter", "growth": 3.5, "shrink": 0.8},
}
# Jede Zahl in diesen Texten ist in tests/test_claims.py belegt (aus dem echten Code neu berechnet).
PRESET_HELP = {
    "🗺️ Standardnetz": "18 Kandidaten, 40 Kunden, Fixkosten-Faktor 100 %: das Optimum öffnet 7 Standorte und kostet 39 345. Faustregel „1 je 5“ trifft mit 8 Standorten fast daneben (0,9 % teurer). Verschiebt sich die Nachfrage (Wachstum ×1,8 / Schrumpfung ×0,7), kostet das Festhalten an der alten Auswahl 3,1 % mehr; der Umbau (3 neue Standorte, 4 287) ist das 2,8-Fache dieser laufenden Lücke.",
    "📏 Grobe Faustregel": "Faustregel „1 Standort je 3 Kunden“ (statt je 5) öffnet 14 statt 7 Standorte und kostet 17,1 % mehr als das Optimum — die Kurve ist um k* herum flach, aber weit daneben wird es teuer.",
    "🚀 Starke Verschiebung": "Wachstum ×2,8 / Schrumpfung ×0,5: die laufende Lücke wächst auf 8,4 %, dieselben 3 Standorte werden neu gebraucht (4 287) — hier ist der Umbau schon günstiger als eine Periode der Mehrkosten (Verhältnis 0,8).",
    "🧭 Konzentriertes Wachstum": "Wächst nur ein Kartenviertel (×3,5) statt einer halben Karte, bleibt die laufende Lücke mit 2,2 % kleiner: eine konzentrierte Verschiebung trifft weniger Standorte gleichzeitig.",
}
