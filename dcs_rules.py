"""Praktiker-Regeln, die ohne den exakten Löser auskommen — Gegenstück zu den Faustregeln aus der Vorab-Messreihe.

Akt 1: Standortzahl aus einer Faustregel ("1 DC je N Kunden") statt aus dem MILP.
Akt 3: zwei naive Standortregeln (keine Fixkosten-/Interaktions-Rücksicht) statt der gemeinsamen Optimierung;
die Kundenzuordnung ist danach immer optimal (nächster offener Standort, `dcs_exact.assignment`).
"""

import math

from dcs_exact import cost_of, arrays
from dcs_scenario import distance


def rule_of_thumb_k(n_customers, per_dc):
    """Faustregel "1 DC je N Kunden": k = ceil(n_customers / per_dc), mindestens 1."""
    return max(1, math.ceil(n_customers / per_dc))


def _demand_weighted_score(inst, site_idx):
    """Score eines Kandidaten für die Regel "größte Nachfragezentren": Summe Nachfrage/(1+Entfernung) über alle
    Kunden — ohne jede Rücksicht auf Fixkosten oder Interaktion mit anderen Standorten."""
    pos = inst.site_pos[site_idx]
    return sum(d / (1 + distance(pos, cp)) for d, cp in zip(inst.demand, inst.cust_pos))


def top_demand_centers(inst, k):
    """Regel "größte Nachfragezentren": die k Kandidaten mit dem höchsten Score, ohne Interaktion."""
    scored = sorted(range(inst.m), key=lambda i: (-_demand_weighted_score(inst, i), i))
    return tuple(sorted(scored[:k]))


def _weighted_kmeans(points, weights, k, iters=50):
    """Nachfragegewichtetes k-Means auf Kundenpositionen. Deterministische Initialisierung per Farthest-Point-
    Sampling (kein Zufallsgenerator, damit das Ergebnis plattformstabil bleibt) statt zufälliger Startpunkte."""
    pts = [tuple(p) for p in points]
    n = len(pts)
    centers = [pts[0]]
    while len(centers) < k:
        far = max(range(n), key=lambda j: min((pts[j][0] - c[0]) ** 2 + (pts[j][1] - c[1]) ** 2 for c in centers))
        centers.append(pts[far])
    for _ in range(iters):
        assign = [min(range(k), key=lambda c: (pts[j][0] - centers[c][0]) ** 2 + (pts[j][1] - centers[c][1]) ** 2) for j in range(n)]
        new_centers = []
        changed = False
        for c in range(k):
            members = [j for j in range(n) if assign[j] == c]
            if not members:
                new_centers.append(centers[c])
                continue
            wsum = sum(weights[j] for j in members)
            cx = sum(pts[j][0] * weights[j] for j in members) / wsum
            cy = sum(pts[j][1] * weights[j] for j in members) / wsum
            new_centers.append((cx, cy))
        if new_centers != centers:
            changed = True
        centers = new_centers
        if not changed:
            break
    return centers


def kmeans_nearest_candidate(inst, k):
    """Regel "nachfragegewichtetes k-Means + nächster freier Kandidat": Zentren aus gewichtetem k-Means, je
    Zentrum der nächste noch nicht gewählte Kandidat-Standort (kein Kandidat wird doppelt gewählt)."""
    centers = _weighted_kmeans(inst.cust_pos, inst.demand, k)
    chosen = []
    for cx, cy in centers:
        cand = min((i for i in range(inst.m) if i not in chosen),
                   key=lambda i: (inst.site_pos[i][0] - cx) ** 2 + (inst.site_pos[i][1] - cy) ** 2)
        chosen.append(cand)
    return tuple(sorted(chosen))


def evaluate_rule(inst, open_set):
    """Kosten einer per Regel gewählten Auswahl bei optimaler (nächster offener Standort) Zuordnung."""
    return cost_of(inst, open_set, arrays(inst))
