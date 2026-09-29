import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs_scenario import SplitMix64, distance, generate_map, shift_demand


def test_splitmix64_deterministic():
    a = SplitMix64(1)
    b = SplitMix64(1)
    assert [a.next() for _ in range(5)] == [b.next() for _ in range(5)]


def test_splitmix64_below_range():
    rng = SplitMix64(42)
    vals = [rng.below(7) for _ in range(200)]
    assert all(0 <= v < 7 for v in vals)
    assert len(set(vals)) > 1


def test_generate_map_shapes():
    inst = generate_map(10, 25, 100, 1)
    assert inst.m == 10
    assert inst.n == 25
    assert len(inst.demand) == 25
    assert all(1 <= d <= 9 for d in inst.demand)
    assert len(inst.c) == 10 and all(len(row) == 25 for row in inst.c)


def test_generate_map_reproducible():
    a = generate_map(10, 25, 100, 7)
    b = generate_map(10, 25, 100, 7)
    assert a == b


def test_distance_matches_manual():
    assert distance((0, 0), (3, 4)) == 50  # isqrt(100 * 25) = isqrt(2500) = 50 (Zehntel-Einheiten)
    assert distance((0, 0), (0, 0)) == 0


def test_shift_demand_growth_and_shrink_by_hand():
    # 2 Standorte, 2 Kunden: einer in der wachsenden Hälfte (x>=50), einer nicht.
    from dcs_scenario import UFL
    inst = UFL("map", ("S1", "S2"), ("K1", "K2"), ((10, 10), (90, 90)), ((10, 10), (90, 90)),
               (4, 6), (100, 100), ((0, 1000), (1000, 0)))
    shifted = shift_demand(inst, "half", growth=2.0, shrink=0.5)
    # K1 bei x=10 (nicht wachsend) -> 4 * 0.5 = 2; K2 bei x=90 (wachsend) -> ceil(6*2.0) = 12
    assert shifted.demand == (2, 12)
    assert shifted.f == inst.f
    assert shifted.site_pos == inst.site_pos


def test_shift_demand_minimum_one_unit():
    from dcs_scenario import UFL
    inst = UFL("map", ("S1",), ("K1",), ((10, 10),), ((10, 10),), (1,), (100,), ((0,),))
    shifted = shift_demand(inst, "half", growth=1.5, shrink=0.1)
    assert shifted.demand == (1,)  # shrink darf nicht auf 0 fallen


def test_shift_demand_quarter_region():
    from dcs_scenario import UFL
    # Nur x>=50 UND y>=50 zaehlt als "quarter".
    inst = UFL("map", ("S1",), ("K1", "K2"), ((0, 0),), ((60, 60), (60, 10)),
               (2, 2), (100,), ((0, 0),))
    shifted = shift_demand(inst, "quarter", growth=3.0, shrink=1.0)
    assert shifted.demand == (math.ceil(2 * 3.0), 2)
