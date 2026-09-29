"""Die aus `standortplanung-demo` kopierten Bausteine (SplitMix64-Strom, `generate_map`, starke MILP-Formulierung)
sind bewacht: dieselben Zahlen wie im Vorgänger, damit ein künftiger Umbau hier nicht unbemerkt vom UFL-Kern der
Konzepte-Linie abweicht."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dcs_scenario import SplitMix64, generate_map
from dcs_exact import solve_mip


def test_splitmix64_stream_is_the_portfolio_standard():
    rng = SplitMix64(1)
    assert [rng.next() for _ in range(3)] == [10451216379200822465, 13757245211066428519, 17911839290282890590]


def test_generate_map_matches_standortplanung_demo_reference_values():
    """Seed 1, 18 Standorte, 40 Kunden, Fixkosten 100 %: Referenzwerte aus `standortplanung-demo/ufl_scenario.py`
    mit denselben Parametern erzeugt (dieselbe Formel, unabhängig gegengerechnet)."""
    inst = generate_map(18, 40, 100, 1)
    assert inst.f[:5] == (1085, 2030, 1855, 2205, 1977)
    assert inst.demand[:5] == (3, 3, 5, 1, 9)
    assert inst.site_pos[:3] == ((65, 19), (90, 35), (61, 48))


def test_solve_mip_reproduces_standortplanung_demo_style_optimum():
    """Dieselbe starke Formulierung wie `standortplanung-demo/ufl_exact.py`: Optimum für Seed 1 (18/40/100%)."""
    inst = generate_map(18, 40, 100, 1)
    cost, opens = solve_mip(inst)
    assert cost == 39345
    assert opens == (2, 5, 7, 9, 11, 15, 16)
