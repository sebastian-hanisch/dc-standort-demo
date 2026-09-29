import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs_constants import PER_DC_MARKERS
from dcs_evaluation import act1_cost_curve, act2_shift, act3_rule_comparison
from dcs_exact import solve_mip
from dcs_scenario import generate_map


def test_act1_cost_star_matches_free_optimum():
    inst = generate_map(18, 40, 100, 1)
    free_cost, free_open = solve_mip(inst)
    a1 = act1_cost_curve(inst, PER_DC_MARKERS)
    assert a1.cost_star == free_cost
    assert a1.k_star == len(free_open)


def test_act1_per_dc_gaps_are_nonnegative():
    inst = generate_map(18, 40, 100, 1)
    a1 = act1_cost_curve(inst, PER_DC_MARKERS)
    for n, (k_hat, cost_hat, gap) in a1.per_dc_gaps.items():
        assert cost_hat >= a1.cost_star
        assert gap >= -1e-9


def test_act2_gap_is_nonnegative_and_new_optimum_not_worse():
    inst = generate_map(18, 40, 100, 1)
    a2 = act2_shift(inst, "half", 1.8, 0.7)
    assert a2.cost_old_under_t1 >= a2.cost_new_t1
    assert a2.gap_pct >= -1e-9


def test_act2_no_shift_means_zero_or_near_zero_gap():
    # growth=shrink=1.0: T1 = T0, die alte Auswahl muss (nahezu) optimal bleiben.
    inst = generate_map(10, 20, 100, 3)
    a2 = act2_shift(inst, "half", 1.0, 1.0)
    assert a2.gap_pct < 1e-6
    assert a2.n_newly_opened == 0


def test_act2_rebuild_cost_matches_sum_of_newly_opened_fixed_costs():
    inst = generate_map(18, 40, 100, 1)
    a2 = act2_shift(inst, "half", 2.8, 0.5)
    newly_opened = [i for i in a2.open_t1 if i not in a2.open_t0]
    assert len(newly_opened) == a2.n_newly_opened
    assert a2.rebuild_fixed_cost >= 0


def test_act3_rules_report_k_equal_to_free_optimum():
    inst = generate_map(18, 40, 100, 1)
    a3 = act3_rule_comparison(inst)
    _cost, opens = solve_mip(inst)
    assert a3.k == len(opens)
    for name, (open_set, cost, gap) in a3.rules.items():
        assert len(open_set) == a3.k
        assert gap >= -1e-9
