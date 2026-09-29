"""Distributionszentren-Standortplanung - interaktive Fall-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Wie viele Verteilzentren sollte man eröffnen, und wo - und was passiert, wenn die Nachfrage sich über die Zeit
verschiebt? Fall-Demo auf der Themenseite Netzwerkdesign, aufbauend auf dem UFL-Kern der Standortplanungs-Linie
("Konzepte"-Reihe). Siehe README für die Einordnung.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import dcs_constants as C
from dcs_evaluation import act1_cost_curve, act2_shift, act3_rule_comparison, per_dc_gap
from dcs_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from dcs_scenario import generate_map, shift_demand
from dcs_visualization import build_cost_curve, build_map, build_rule_bars

st.set_page_config(page_title="Distributionszentren-Standortplanung – Sebastian Hanisch", layout="wide")


def _int(x):
    return "–" if x is None else f"{int(round(x)):,}".replace(",", " ")


def _pct(x, digits=1):
    return "–" if x is None else f"{x:.{digits}f} %".replace(".", ",")


def _pl(k, one, many):
    return f"{k} {one if k == 1 else many}"


@st.cache_resource(show_spinner=False, max_entries=32)
def _net(sites, customers, fixed, seed):
    return generate_map(sites, customers, fixed, seed)


@st.cache_resource(show_spinner=False, max_entries=32)
def _act1(sites, customers, fixed, seed):
    return act1_cost_curve(_net(sites, customers, fixed, seed), C.PER_DC_MARKERS)


@st.cache_resource(show_spinner=False, max_entries=64)
def _act2(sites, customers, fixed, seed, region, growth, shrink):
    return act2_shift(_net(sites, customers, fixed, seed), region, growth, shrink)


@st.cache_resource(show_spinner=False, max_entries=32)
def _act3(sites, customers, fixed, seed):
    return act3_rule_comparison(_net(sites, customers, fixed, seed))


st.title("📍 Distributionszentren-Standortplanung")
st.markdown(
    """
Wo sollte man Lager oder Verteilzentren eröffnen, wenn jeder Kunde vom nächstgelegenen offenen Standort beliefert
wird? Jeder Standort kostet **Fixkosten**, jede Belieferung Nachfrage mal Entfernung — dasselbe Modell wie in der
Standortplanungs-Linie der "Konzepte"-Reihe (**UFL**, Uncapacitated Facility Location), hier an zwei konkreten
Geschäftsfragen entlang erzählt statt an Verfahren.
"""
)
st.caption(
    "Akt 1: wie viele Standorte, und was kostet es, das zu schätzen statt zu rechnen? Akt 2: die Antwort von heute "
    "hält nicht ewig — aber anzupassen ist selbst teuer. Verwandt: die Standortplanungs-Demo (derselbe UFL-Kern, "
    "Verfahrensvergleich statt Geschäftsfall), die k-Means-Demo (Depotwahl, aber ohne Fixkosten)."
)

st.caption("🎯 Schnellstart – ein Beispiel laden:")
names = list(C.PRESETS.keys())
for row in range(0, len(names), 4):
    preset_cols = st.columns(4)
    for col, name in zip(preset_cols, names[row:row + 4]):
        with col:
            st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name) or None)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    sites = st.slider("Kandidaten-Standorte", *bounds("sites_slider"), key="sites_slider")
    customers = st.slider("Kunden", *bounds("customers_slider"), key="customers_slider")
    fixed = st.slider("Fixkosten-Faktor [%]", *bounds("fixed_slider"), key="fixed_slider", step=C.FIXED_STEP,
                      help="Skaliert die Fixkosten aller Standorte.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neues Netz generieren", width="stretch", on_click=randomize_seed)
    st.markdown("---")
    st.markdown("**Akt 1 — Faustregel**")
    per_dc = st.slider("1 Standort je N Kunden", *bounds("per_dc_slider"), key="per_dc_slider")
    st.markdown("**Akt 2 — Nachfrageverschiebung**")
    region = st.selectbox("Wachsende Region", list(C.REGIONS), key="region_select", format_func=lambda k: C.REGIONS[k])
    growth = st.slider("Wachstumsfaktor", *bounds("growth_slider"), key="growth_slider", step=C.GROWTH_STEP)
    shrink = st.slider("Schrumpfungsfaktor", *bounds("shrink_slider"), key="shrink_slider", step=C.SHRINK_STEP)

sync_query_params(sites, customers, fixed, seed, per_dc, region, growth, shrink)

with st.spinner("Rechne..."):
    a1 = _act1(int(sites), int(customers), int(fixed), int(seed))
    a2 = _act2(int(sites), int(customers), int(fixed), int(seed), region, float(growth), float(shrink))
    a3 = _act3(int(sites), int(customers), int(fixed), int(seed))
inst = _net(int(sites), int(customers), int(fixed), int(seed))

st.markdown(
    f"Das Netz hat **{inst.m} Kandidaten** und **{inst.n} Kunden**. Das freie Optimum öffnet **{_pl(a1.k_star, 'Standort', 'Standorte')}** "
    f"und kostet **{_int(a1.cost_star)}**."
)

st.markdown("---")

# --- Akt 1 ------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Akt 1 — Wie viele Standorte, und was kostet Schätzen statt Rechnen?")
st.caption("Kostenkurve über die erzwungene Standortzahl k (Stern = freies Optimum); Rauten zeigen, wo die Faustregel „1 DC je N Kunden“ landet.")
markers = list(a1.per_dc_gaps.items())
st.plotly_chart(build_cost_curve(a1.curve, a1.k_star, markers), width="stretch", key="cost_curve_chart")

k_hat, cost_hat, gap_hat = per_dc_gap(a1, inst.m, inst.n, per_dc)
c1, c2, c3 = st.columns(3)
c1.metric("Freies Optimum", _int(a1.cost_star), help=f"{a1.k_star} Standorte.")
c2.metric(f"Faustregel „1 je {per_dc}“", _int(cost_hat), delta=f"{_pct(gap_hat)} teurer" if gap_hat > 1e-9 else "trifft das Optimum",
         delta_color="off" if gap_hat <= 1e-9 else "inverse", help=f"{k_hat} Standorte statt {a1.k_star}.")
c3.metric("Standorte: Regel gegen Optimum", f"{k_hat} / {a1.k_star}")
if abs(k_hat - a1.k_star) <= 1:
    st.success(f"✅ Die Faustregel liegt nur {abs(k_hat - a1.k_star)} Standort(e) neben dem Optimum — die Kurve ist um k* herum flach, das kostet kaum etwas.")
else:
    st.warning(f"Die Faustregel liegt {abs(k_hat - a1.k_star)} Standorte neben dem Optimum ({k_hat} statt {a1.k_star}) und kostet {_pct(gap_hat)} mehr als nötig.")

st.markdown("---")

# --- Akt 2 ------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Akt 2 — Die Antwort von heute hält nicht ewig, aber Anpassen ist selbst teuer")
st.caption("Dieselben Standorte/Kunden, aber die Nachfrage verschiebt sich regional (Regler links). Verglichen wird die ALTE, bei T0 optimale Auswahl unter der neuen Nachfrage gegen die für T1 neu berechnete.")
shift_inst = shift_demand(inst, region, float(growth), float(shrink))
st.plotly_chart(build_map(shift_inst, a2.open_t1, old_open=a2.open_t0), width="stretch", key="shift_map_chart")

d1, d2, d3, d4 = st.columns(4)
d1.metric("Laufende Mehrkosten (alt unter T1)", _pct(a2.gap_pct), help=f"{_int(a2.cost_old_under_t1)} statt {_int(a2.cost_new_t1)}.")
d2.metric("Neu zu eröffnende Standorte", a2.n_newly_opened)
d3.metric("Einmalige Umbaukosten", _int(a2.rebuild_fixed_cost))
d4.metric("Umbau ÷ laufende Lücke", f"{a2.rebuild_to_gap_ratio:.1f}×" if a2.rebuild_to_gap_ratio != float("inf") else "–",
         help="Verhältnis der einmaligen Fixkosten neu eröffneter Standorte zur laufenden Mehrkosten-Lücke (eine Periode).")
if a2.n_newly_opened == 0:
    st.success("✅ Die alte Auswahl bleibt bei dieser Verschiebung optimal — nichts anzupassen.")
elif a2.rebuild_to_gap_ratio > 1:
    st.info(f"Anders als beim „starr vs. reaktiv“-Muster in diesem Portfolio ist hier das **Reagieren selbst teuer**: die einmaligen Umbaukosten ({_int(a2.rebuild_fixed_cost)}) sind das {a2.rebuild_to_gap_ratio:.1f}-Fache der laufenden Mehrkosten-Lücke — die Frage ist der Amortisationszeitraum, nicht die Lückengröße.")
else:
    st.warning(f"Hier lohnt sich der Umbau schnell: die einmaligen Kosten ({_int(a2.rebuild_fixed_cost)}) sind kleiner als eine Periode der laufenden Mehrkosten.")

st.markdown("---")

# --- Akt 3 (Panel) -----------------------------------------------------------------------------------------------

st.markdown("## 🔬 Zusatz — Und wenn man einfach nach Cluster-Schwerpunkten baut?")
st.caption("Zwei naive Standortregeln (ohne Fixkosten-/Interaktions-Rücksicht) bei gleicher Standortzahl wie das Optimum, Kundenzuordnung danach optimal.")
st.plotly_chart(build_rule_bars(a3.cost_star, a3.rules), width="stretch", key="rule_bars_chart")
st.table({"Regel": ["Optimum (gemeinsam)"] + [C.LABELS[k] for k in a3.rules],
         "Kosten": [_int(a3.cost_star)] + [_int(c) for _o, c, _g in a3.rules.values()],
         "Lücke": ["–"] + [_pct(g) for _o, _c, g in a3.rules.values()]})
st.caption("Anders als die k-Means-Demo (Depotwahl ohne Fixkosten) zählen hier Fixkosten UND die freie Zuordnung nach Eröffnung mit — die gewichtete k-Means-Regel ist ein plausibler, aber spürbar teurerer Ersatz für die gemeinsame Optimierung.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Keine Kapazitätsgrenze** | Mit Kapazitäten je Standort ist die LP-Schranke wieder schwach (siehe die kapazitierte Standortplanung-Demo, Lagrange-Relaxation). |
| **Nachfrageverschiebung als einfacher Regionsfaktor** | Echte Nachfrageprognosen sind unsicherer und feinkörniger; Akt 2 zeigt die Größenordnung des Effekts, kein Prognosemodell. |
| **Eine Verschiebung, ein Umbau** | Mehrere Zeitschritte mit rollierender Neuplanung sind nicht gebaut. |
| **Standorte einmal gebaut, nie wieder geschlossen im Vergleich** | Akt 2 vergleicht nur „alt behalten“ gegen „für T1 neu bauen“, keine Zwischenstufe (nur einzelne Standorte nachrüsten). |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Modell (wie die Standortplanungs-Demo).** Kandidaten $I$, Kunden $J$, Fixkosten $f_i$, Zuordnungskosten $c_{ij}$:
$$\min\sum_i f_iy_i+\sum_{i,j}c_{ij}x_{ij}\quad\text{u.d.N.}\quad\sum_i x_{ij}=1\ \ \forall j,\quad x_{ij}\le y_i\ \ \forall i,j,\quad y_i\in\{0,1\}.$$

**Akt 1 — erzwungene Standortzahl:** dieselbe Formulierung mit der Zusatzbedingung $\sum_i y_i=k$; die Kostenkurve
ist das Optimum dieses MILP für jedes $k=1,\dots,|I|$.

**Akt 2 — Nachfrageverschiebung:** die Kundenpositionen bleiben fest, die Nachfrage $d_j$ wird regional skaliert
($d_j\cdot g$ für Kunden in der wachsenden Region, aufgerundet, mindestens 1; $d_j\cdot s$ sonst, abgerundet,
mindestens 1), die Zuordnungskosten $c_{ij}=d_j\cdot\text{dist}(i,j)$ werden neu berechnet. Verglichen wird
$\text{Kosten}(y^{T0}, d^{T1})$ (alte Auswahl unter neuer Nachfrage) gegen $\min_y \text{Kosten}(y, d^{T1})$ (neu
optimiert); die **Umbaukosten** sind $\sum_{i\in y^{T1}\setminus y^{T0}} f_i$ — die einmalige Fixkosten-Summe der
neu eröffneten Standorte.

**Akt 3 — naive Regeln:** „größte Nachfragezentren“ wählt die $k$ Kandidaten mit dem höchsten Score
$\sum_j d_j/(1+\text{dist}(i,j))$, ohne Fixkosten oder Interaktion; „gewichtetes k-Means“ clustert die Kundenpositionen
(nachfragegewichteter Schwerpunkt, deterministische Farthest-Point-Initialisierung statt Zufallsstart) und wählt je
Zentrum den nächsten noch freien Kandidaten. Beide Regeln legen nur die Standorte fest — die Kundenzuordnung danach
ist immer optimal (nächster offener Standort).

Implementiert in `dcs_scenario.py` (Netz, Nachfrageverschiebung — Kopie/Erweiterung von `standortplanung-demo`),
`dcs_exact.py` (HiGHS-MILP mit optionalem `force_k`), `dcs_rules.py` (Faustregeln), `dcs_evaluation.py` (die drei Akte).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
