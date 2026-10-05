"""Orakel-Test: Optimum, erzwungenes k, Akt 2 und Standortregeln gegen Brute Force über alle Teilmengen und exakte Brüche (Fraction) für die Nachfrageverschiebung, die Score-Regel und das gewichtete k-Means."""

import math
import random
from fractions import Fraction as Fr
from itertools import combinations

import pytest

import dcs_evaluation as ev
import dcs_exact as ex
import dcs_rules as ru
import dcs_scenario as sc


def _cost(inst, s):
    return sum(inst.f[i] for i in s) + sum(min(inst.c[i][j] for i in s) for j in range(inst.n))


def _by_k(inst):
    return {k: min(_cost(inst, s) for s in combinations(range(inst.m), k)) for k in range(1, inst.m + 1)}


def _inst(seed):
    rng = random.Random(seed)
    return sc.generate_map(rng.randint(3, 8), rng.randint(4, 12), rng.choice([25, 100, 400]), rng.randint(0, 10 ** 6))


@pytest.mark.parametrize("seed", range(12))
def test_exact_and_act2_equal_brute_force(seed):
    inst = _inst(seed)
    curve = _by_k(inst)
    assert ex.cost_curve(inst) == curve and ex.solve_mip(inst)[0] == min(curve.values())
    a1 = ev.act1_cost_curve(inst, (3, 5))
    assert a1.cost_star == min(curve.values())
    for per in range(2, 15):
        k = max(1, min(inst.m, -(-inst.n // per)))
        assert ev.per_dc_gap(a1, inst.m, inst.n, per)[:2] == (k, curve[k])
    rng = random.Random(seed)
    region, g, s = rng.choice(["half", "quarter"]), rng.choice([1.0, 1.8, 2.8, 3.5]), rng.choice([0.5, 0.7, 1.0])
    a2 = ev.act2_shift(inst, region, g, s)
    t1 = sc.shift_demand(inst, region, g, s)
    best1 = min(_by_k(t1).values())
    assert a2.cost_new_t1 == best1 and a2.cost_old_under_t1 == _cost(t1, a2.open_t0)
    assert a2.rebuild_fixed_cost == sum(t1.f[i] for i in a2.open_t1 if i not in a2.open_t0)


@pytest.mark.parametrize("seed", range(12))
def test_shift_demand_and_rules_equal_exact_fractions(seed):
    inst = _inst(seed)
    for region, g, s in (("half", 1.8, 0.7), ("quarter", 2.8, 0.5), ("half", 5.0, 0.2)):
        t1 = sc.shift_demand(inst, region, g, s)
        for j, (d, (x, y)) in enumerate(zip(inst.demand, inst.cust_pos)):
            grow = x >= 50 if region == "half" else (x >= 50 and y >= 50)
            exp = max(1, math.ceil(d * Fr(str(g)))) if grow else max(1, math.floor(d * Fr(str(s))))
            assert t1.demand[j] == exp
    k = max(1, inst.m // 2)

    def score(i):
        return sum(Fr(inst.demand[j], 1 + sc.distance(inst.site_pos[i], inst.cust_pos[j])) for j in range(inst.n))

    assert ru.top_demand_centers(inst, k) == tuple(sorted(sorted(range(inst.m), key=lambda i: (-score(i), i))[:k]))
    if k <= inst.n:
        pts = [tuple(Fr(v) for v in p) for p in inst.cust_pos]
        cs = [pts[0]]
        while len(cs) < k:
            cs.append(pts[max(range(len(pts)), key=lambda j: min((pts[j][0] - c[0]) ** 2 + (pts[j][1] - c[1]) ** 2 for c in cs))])
        for _ in range(50):
            asg = [min(range(k), key=lambda c: (pts[j][0] - cs[c][0]) ** 2 + (pts[j][1] - cs[c][1]) ** 2) for j in range(len(pts))]
            new = []
            for c in range(k):
                mem = [j for j in range(len(pts)) if asg[j] == c]
                ws = sum(inst.demand[j] for j in mem)
                new.append(cs[c] if not mem else (sum(pts[j][0] * inst.demand[j] for j in mem) / ws, sum(pts[j][1] * inst.demand[j] for j in mem) / ws))
            if new == cs:
                break
            cs = new
        chosen = []
        for cx, cy in cs:
            chosen.append(min((i for i in range(inst.m) if i not in chosen), key=lambda i: ((inst.site_pos[i][0] - cx) ** 2 + (inst.site_pos[i][1] - cy) ** 2, i)))
        assert ru.kmeans_nearest_candidate(inst, k) == tuple(sorted(chosen))
