"""Exakte Rechnung (HiGHS über scipy): das freie Optimum, das Optimum bei erzwungener Standortzahl k (Akt 1),
und die Kosten/Zuordnung einer vorgegebenen Standort-Auswahl (für Akt 2 und Akt 3, wo die Standorte nicht vom
Löser, sondern von einer Faustregel oder der alten T0-Auswahl kommen).

Formulierung: starke Kopplung (x_ij <= y_i je Paar) wie in `standortplanung-demo` — dort gemessen: LP-Wert = Optimum
in 38 von 40 Kartennetzen, also für den exakten MILP-Aufruf hier nicht weiter relevant (wir lösen ohnehin ganzzahlig),
aber dieselbe Formulierung wie das Vorbild, damit `test_copies.py` beide vergleichen kann.
"""

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

EPS = 1e-6


def arrays(inst):
    """Fixkosten und Kostenmatrix als numpy-Ganzzahl-Felder."""
    return np.array(inst.f, dtype=np.int64), np.array(inst.c, dtype=np.int64)


def cost_of(inst, open_set, arr=None):
    """Gesamtkosten einer Auswahl (Fixkosten + je Kunde der billigste offene Standort); None, wenn nichts offen ist."""
    idx = sorted(open_set)
    if not idx:
        return None
    f, c = arr if arr is not None else arrays(inst)
    return int(f[idx].sum() + c[idx].min(axis=0).sum())


def assignment(inst, open_set):
    """Standort je Kunde (Index in `inst`); Gleichstand: der kleinste Index."""
    idx = sorted(open_set)
    _f, c = arrays(inst)
    return tuple(int(idx[k]) for k in c[idx].argmin(axis=0))


def _model(inst):
    """Starke Formulierung (x_ij <= y_i je Paar), wie `standortplanung-demo`."""
    m, n = inst.m, inst.n
    nv = m + m * n
    cost = np.concatenate([np.array(inst.f, dtype=float), np.array(inst.c, dtype=float).ravel()])
    rows, cols, vals = [], [], []
    lo, hi = [], []
    r = 0
    for j in range(n):
        for i in range(m):
            rows.append(r); cols.append(m + i * n + j); vals.append(1.0)
        lo.append(1.0); hi.append(1.0); r += 1
    for i in range(m):
        for j in range(n):
            rows += [r, r]; cols += [m + i * n + j, i]; vals += [1.0, -1.0]
            lo.append(-np.inf); hi.append(0.0); r += 1
    return cost, coo_matrix((vals, (rows, cols)), shape=(r, nv)).tocsr(), np.array(lo), np.array(hi)


def solve_mip(inst, force_k=None):
    """Optimum (ganzzahlige Kosten) und offene Standorte. `force_k`: falls gesetzt, muss genau k Standorte
    öffnen (sum(y) = k) — für die Kostenkurve in Akt 1; ohne `force_k` wählt der Löser die Anzahl frei."""
    m = inst.m
    cost, a, lo, hi = _model(inst)
    integrality = np.concatenate([np.ones(m), np.zeros(m * inst.n)])
    constraints = [LinearConstraint(a, lo, hi)]
    if force_k is not None:
        row = np.zeros(m + m * inst.n)
        row[:m] = 1.0
        constraints.append(LinearConstraint(row, force_k, force_k))
    res = milp(cost, constraints=constraints, integrality=integrality, bounds=Bounds(0, 1),
               options={"time_limit": 120, "mip_rel_gap": 0.0})
    if res.status != 0:
        raise RuntimeError(f"MILP nicht optimal gelöst (force_k={force_k}): {res.message}")
    open_set = tuple(i for i in range(m) if res.x[i] > 0.5)
    return int(round(res.fun)), open_set


def cost_curve(inst, k_max=None):
    """Kosten des Optimums bei erzwungener Standortzahl k = 1..k_max (Standard: alle Kandidaten)."""
    k_max = k_max or inst.m
    return {k: solve_mip(inst, force_k=k)[0] for k in range(1, k_max + 1)}
