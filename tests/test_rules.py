import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs_exact import cost_of
from dcs_rules import evaluate_rule, kmeans_nearest_candidate, rule_of_thumb_k, top_demand_centers
from dcs_scenario import generate_map


def test_rule_of_thumb_k_basic():
    assert rule_of_thumb_k(40, 5) == 8
    assert rule_of_thumb_k(40, 3) == 14   # ceil(40/3) = 14
    assert rule_of_thumb_k(1, 100) == 1   # mindestens 1


def test_top_demand_centers_returns_k_distinct_sites():
    inst = generate_map(18, 40, 100, 1)
    chosen = top_demand_centers(inst, 7)
    assert len(chosen) == 7
    assert len(set(chosen)) == 7
    assert all(0 <= i < inst.m for i in chosen)


def test_kmeans_nearest_candidate_returns_k_distinct_sites():
    inst = generate_map(18, 40, 100, 1)
    chosen = kmeans_nearest_candidate(inst, 7)
    assert len(chosen) == 7
    assert len(set(chosen)) == 7


def test_kmeans_nearest_candidate_deterministic_no_rng():
    inst = generate_map(18, 40, 100, 1)
    a = kmeans_nearest_candidate(inst, 7)
    b = kmeans_nearest_candidate(inst, 7)
    assert a == b


def test_evaluate_rule_matches_cost_of():
    inst = generate_map(18, 40, 100, 1)
    chosen = top_demand_centers(inst, 7)
    assert evaluate_rule(inst, chosen) == cost_of(inst, chosen)


def test_rules_never_beat_the_optimum():
    from dcs_exact import solve_mip
    inst = generate_map(18, 40, 100, 2)
    opt_cost, opt_open = solve_mip(inst)
    k = len(opt_open)
    for fn in (top_demand_centers, kmeans_nearest_candidate):
        chosen = fn(inst, k)
        assert evaluate_rule(inst, chosen) >= opt_cost
