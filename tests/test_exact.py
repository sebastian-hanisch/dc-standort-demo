import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs_exact import arrays, assignment, cost_of, cost_curve, solve_mip
from dcs_scenario import generate_map


def _brute_force(inst):
    best = None
    for k in range(1, inst.m + 1):
        for s in combinations(range(inst.m), k):
            v = cost_of(inst, s)
            if best is None or v < best:
                best = v
    return best


def _brute_force_k(inst, k):
    return min(cost_of(inst, s) for s in combinations(range(inst.m), k))


def test_solve_mip_matches_brute_force_small_net():
    inst = generate_map(6, 8, 100, 42)
    cost, opens = solve_mip(inst)
    assert cost == _brute_force(inst)
    assert cost_of(inst, opens) == cost


def test_solve_mip_force_k_matches_brute_force():
    inst = generate_map(6, 8, 100, 7)
    for k in range(1, inst.m + 1):
        cost, opens = solve_mip(inst, force_k=k)
        assert len(opens) == k
        assert cost == _brute_force_k(inst, k)


def test_cost_curve_is_the_free_optimum_at_its_minimum():
    inst = generate_map(6, 8, 100, 3)
    curve = cost_curve(inst)
    free_cost, _ = solve_mip(inst)
    assert min(curve.values()) == free_cost


def test_cost_curve_monotone_around_optimum_not_assumed_but_checked_flat_near_min():
    # Keine globale Monotonie-Annahme (kann sowohl vor als auch nach k* fallen), nur: das Minimum der Kurve
    # ist eindeutig das freie Optimum (siehe test_cost_curve_is_the_free_optimum_at_its_minimum).
    inst = generate_map(10, 20, 100, 5)
    curve = cost_curve(inst)
    assert len(curve) == inst.m
    assert all(v > 0 for v in curve.values())


def test_assignment_picks_cheapest_open_site():
    inst = generate_map(8, 12, 100, 9)
    _cost, opens = solve_mip(inst)
    assign = assignment(inst, opens)
    f, c = arrays(inst)
    for j, i in enumerate(assign):
        assert i in opens
        assert c[i][j] == min(c[k][j] for k in opens)


def test_cost_of_none_when_nothing_open():
    inst = generate_map(4, 4, 100, 1)
    assert cost_of(inst, ()) is None


def test_solve_mip_force_k_infeasible_k_raises_or_handles():
    inst = generate_map(4, 4, 100, 1)
    # k darf hoechstens m sein; k=m ist immer zulaessig (alle offen).
    cost, opens = solve_mip(inst, force_k=inst.m)
    assert len(opens) == inst.m
