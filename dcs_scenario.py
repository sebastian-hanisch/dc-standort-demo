"""Szenario: Distributionszentren-Standortplanung. Dieselbe Karte wie in `standortplanung-demo` (Uncapacitated
Facility Location: Kandidaten-Standorte, Kunden mit Nachfrage, Fixkosten je Standort, Belieferungskosten = Nachfrage
mal Entfernung) — hier per `shift_demand` um eine regionale Nachfrageverschiebung erweitert (Akt 2: wächst eine
Kartenhälfte oder ein Kartenviertel, während der Rest schrumpft).

Ganzzahlig, eigener Zufallsgenerator (SplitMix64 auf Python-Ints) statt `numpy.random` — numpy garantiert keine
über Versionen stabilen Zufallsströme, die CI installiert aber wöchentlich die neueste Version.
"""

import math
from dataclasses import dataclass, replace
from math import isqrt

_MASK = (1 << 64) - 1
MAP_W = 100
FIXED_BASE = 1750        # mittlere Fixkosten bei Fixkosten-Faktor 100 % (Kopie aus standortplanung-demo)


class SplitMix64:
    """Kleiner, gut gemischter 64-Bit-Zufallsgenerator (Vigna); reine Ganzzahl-Arithmetik."""

    def __init__(self, seed):
        self.state = seed & _MASK

    def next(self):
        self.state = (self.state + 0x9E3779B97F4A7C15) & _MASK
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
        return z ^ (z >> 31)

    def below(self, n):
        return self.next() % n


@dataclass(frozen=True)
class UFL:
    kind: str
    site_names: tuple
    cust_names: tuple
    site_pos: tuple
    cust_pos: tuple
    demand: tuple
    f: tuple
    c: tuple

    @property
    def m(self):
        return len(self.f)

    @property
    def n(self):
        return len(self.cust_names)

    @property
    def has_map(self):
        return bool(self.site_pos)


def distance(a, b):
    """Euklidische Entfernung in Zehntel-Einheiten, ganzzahlig (abgerundet)."""
    return isqrt(100 * ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))


def _names(prefix, count):
    return tuple(f"{prefix} {k + 1}" for k in range(count))


def generate_map(n_sites, n_customers, fixed_pct, seed):
    """Kandidaten und Kunden gleichverteilt auf einer Karte 0..99; Nachfrage 1..9; Fixkosten 60 bis 140 % von FIXED_BASE."""
    rng = SplitMix64(seed)
    sites = tuple((rng.below(MAP_W), rng.below(MAP_W)) for _ in range(n_sites))
    custs = tuple((rng.below(MAP_W), rng.below(MAP_W)) for _ in range(n_customers))
    demand = tuple(1 + rng.below(9) for _ in range(n_customers))
    f = tuple(FIXED_BASE * (60 + rng.below(81)) // 100 * fixed_pct // 100 for _ in range(n_sites))
    c = tuple(tuple(demand[j] * distance(sites[i], custs[j]) for j in range(n_customers)) for i in range(n_sites))
    return UFL("map", _names("Standort", n_sites), _names("Kunde", n_customers), sites, custs, demand, f, c)


def _in_growth_region(pos, region):
    """Ob eine Position in der wachsenden Region liegt. `region` ist 'half' (x >= 50) oder 'quarter' (x >= 50 und y >= 50)."""
    x, y = pos
    if region == "half":
        return x >= MAP_W // 2
    if region == "quarter":
        return x >= MAP_W // 2 and y >= MAP_W // 2
    raise ValueError(f"unbekannte Region: {region}")


def shift_demand(inst, region, growth, shrink):
    """Verschiebt die Nachfrage regional: Kunden in der wachsenden Region (`region`, 'half' oder 'quarter')
    werden mit `growth` multipliziert (aufgerundet, mindestens 1), alle anderen mit `shrink` (abgerundet,
    mindestens 1). Belieferungskosten `c` werden aus der neuen Nachfrage neu berechnet, Standorte/Fixkosten
    bleiben unverändert (dieselbe Netzstruktur, nur verschobene Nachfrage)."""
    # ganzzahlige Rundung: wachsend aufrunden, schrumpfend abrunden (growth/shrink sind Floats)
    new_demand = tuple(
        max(1, math.ceil(d * growth)) if _in_growth_region(pos, region) else max(1, int(d * shrink))
        for d, pos in zip(inst.demand, inst.cust_pos)
    )
    new_c = tuple(
        tuple(new_demand[j] * distance(inst.site_pos[i], inst.cust_pos[j]) for j in range(inst.n))
        for i in range(inst.m)
    )
    return replace(inst, demand=new_demand, c=new_c)
