"""Jede Zahl im README (und in den Preset-Hilfetexten) ist hier belegt — aus dem echten Code neu berechnet, seed 1,
18 Kandidaten, 40 Kunden, Fixkosten-Faktor 100 % (Standardnetz), soweit nicht anders angegeben."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs_constants import PER_DC_MARKERS
from dcs_evaluation import act1_cost_curve, act2_shift, act3_rule_comparison
from dcs_scenario import generate_map

STANDARD = generate_map(18, 40, 100, 1)


def test_standard_net_optimum():
    a1 = act1_cost_curve(STANDARD, PER_DC_MARKERS)
    assert a1.cost_star == 39345
    assert a1.k_star == 7


def test_akt1_faustregel_gaps():
    a1 = act1_cost_curve(STANDARD, PER_DC_MARKERS)
    expected = {3: (14, 46062, 17.072054898970645), 5: (8, 39715, 0.9403990341847757),
                8: (5, 40647, 3.3091879527258863), 12: (4, 42059, 6.897953996695895)}
    for n, (k, cost, gap) in expected.items():
        k_hat, cost_hat, gap_hat = a1.per_dc_gaps[n]
        assert (k_hat, cost_hat) == (k, cost)
        assert gap_hat == pytest.approx(gap, abs=1e-6)


def test_akt2_default_shift():
    a2 = act2_shift(STANDARD, "half", 1.8, 0.7)
    assert a2.gap_pct == pytest.approx(3.0906106235940256, abs=1e-6)
    assert a2.n_newly_opened == 3
    assert a2.rebuild_fixed_cost == 4287
    assert a2.rebuild_to_gap_ratio == pytest.approx(2.8111475409836064, abs=1e-6)


def test_akt2_strong_shift_ratio_below_one():
    """Bei stärkerer Verschiebung kippt das Verhältnis unter 1: der Umbau lohnt sich dann schon innerhalb einer Periode."""
    a2 = act2_shift(STANDARD, "half", 2.8, 0.5)
    assert a2.gap_pct == pytest.approx(8.439279943857816, abs=1e-6)
    assert a2.n_newly_opened == 3
    assert a2.rebuild_fixed_cost == 4287
    assert a2.rebuild_to_gap_ratio == pytest.approx(0.8290466060723264, abs=1e-6)


def test_akt2_quarter_region_smaller_gap_than_half():
    """Wächst nur ein Kartenviertel statt einer halben Karte (gleicher Wachstumsfaktor 3,5), bleibt die Lücke kleiner."""
    a2_quarter = act2_shift(STANDARD, "quarter", 3.5, 0.8)
    assert a2_quarter.gap_pct == pytest.approx(2.187464581208206, abs=1e-6)
    assert a2_quarter.n_newly_opened == 1
    assert a2_quarter.rebuild_fixed_cost == 1172


def test_akt3_rule_gaps():
    a3 = act3_rule_comparison(STANDARD)
    assert a3.k == 7
    assert a3.cost_star == 39345
    _open_td, cost_td, gap_td = a3.rules["topdemand"]
    _open_km, cost_km, gap_km = a3.rules["kmeans"]
    assert (cost_td, cost_km) == (48698, 43195)
    assert gap_td == pytest.approx(23.771762612784343, abs=1e-6)
    assert gap_km == pytest.approx(9.785233193544288, abs=1e-6)
    assert gap_td > gap_km  # "größte Nachfragezentren" ist die schwächere Regel
