"""Auswertungen für die drei Akte: Kostenkurve über die Standortzahl (Akt 1), alte gegen neu optimierte
Standortauswahl bei Nachfrageverschiebung (Akt 2), naive Standortregeln gegen die gemeinsame Optimierung (Akt 3)."""

from dataclasses import dataclass

from dcs_exact import assignment, cost_of, arrays, solve_mip, cost_curve
from dcs_rules import evaluate_rule, kmeans_nearest_candidate, rule_of_thumb_k, top_demand_centers
from dcs_scenario import shift_demand


@dataclass(frozen=True)
class Act1Result:
    k_star: int
    cost_star: int
    curve: dict            # k -> Kosten bei erzwungenem k
    per_dc_gaps: dict       # N (Faustregel) -> (k_hat, Kosten, Lücke in %)


def act1_cost_curve(inst, per_dc_values):
    cost_star, open_star = solve_mip(inst)
    k_star = len(open_star)
    curve = cost_curve(inst)
    gaps = {}
    for n in per_dc_values:
        k_hat = max(1, min(inst.m, rule_of_thumb_k(inst.n, n)))
        cost_hat = curve[k_hat]
        gaps[n] = (k_hat, cost_hat, 100.0 * (cost_hat - cost_star) / cost_star)
    return Act1Result(k_star, cost_star, curve, gaps)


def per_dc_gap(a1, m, n_customers, per_dc):
    """(k_hat, Kosten, Lücke) für einen BELIEBIGEN Faustregel-Wert, nicht nur die festen Marker in
    `a1.per_dc_gaps` — der Regler in der App deckt einen größeren Bereich ab als die Marker-Diamanten
    auf der Kurve, `a1.curve` deckt aber schon jedes k ab, ein neuer MILP-Lauf ist nicht nötig."""
    k_hat = max(1, min(m, rule_of_thumb_k(n_customers, per_dc)))
    cost_hat = a1.curve[k_hat]
    return k_hat, cost_hat, 100.0 * (cost_hat - a1.cost_star) / a1.cost_star


@dataclass(frozen=True)
class Act2Result:
    cost_old_t0: int
    open_t0: tuple
    cost_old_under_t1: int
    cost_new_t1: int
    open_t1: tuple
    gap_pct: float
    n_newly_opened: int
    rebuild_fixed_cost: int
    rebuild_to_gap_ratio: float          # rebuild_fixed_cost / (cost_old_under_t1 - cost_new_t1)


def act2_shift(inst, region, growth, shrink):
    cost_t0, open_t0 = solve_mip(inst)
    inst_t1 = shift_demand(inst, region, growth, shrink)
    arr_t1 = arrays(inst_t1)
    cost_old_under_t1 = cost_of(inst_t1, open_t0, arr_t1)
    cost_new_t1, open_t1 = solve_mip(inst_t1)
    gap_abs = cost_old_under_t1 - cost_new_t1
    gap_pct = 100.0 * gap_abs / cost_new_t1
    newly_opened = tuple(i for i in open_t1 if i not in open_t0)
    rebuild_cost = sum(inst_t1.f[i] for i in newly_opened)
    ratio = (rebuild_cost / gap_abs) if gap_abs > 0 else float("inf")
    return Act2Result(cost_t0, open_t0, cost_old_under_t1, cost_new_t1, open_t1, gap_pct,
                       len(newly_opened), rebuild_cost, ratio)


@dataclass(frozen=True)
class Act3Result:
    k: int
    cost_star: int
    open_star: tuple
    rules: dict           # name -> (open_set, cost, Lücke in %)


def act3_rule_comparison(inst):
    cost_star, open_star = solve_mip(inst)
    k = len(open_star)
    rules = {}
    for name, fn in (("topdemand", top_demand_centers), ("kmeans", kmeans_nearest_candidate)):
        open_set = fn(inst, k)
        cost = evaluate_rule(inst, open_set)
        rules[name] = (open_set, cost, 100.0 * (cost - cost_star) / cost_star)
    return Act3Result(k, cost_star, open_star, rules)
