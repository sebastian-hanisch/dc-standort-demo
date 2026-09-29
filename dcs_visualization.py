"""Plotly-Abbildungen: Karte mit offenen Standorten (Kopie des Kartenbausteins aus `standortplanung-demo`), die
Kostenkurve über die Standortzahl (Akt 1), die Karte mit alter/neuer Auswahl bei Nachfrageverschiebung (Akt 2) und
der Vergleich der naiven Standortregeln (Akt 3). Achsen sind gesperrt (fixedrange), Karten mit gleichem Maßstab
(scaleanchor), damit Touch-Geräte beim Scrollen nicht zoomen."""

import plotly.graph_objects as go

import dcs_constants as C
from dcs_exact import assignment


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.22), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_map(inst, open_set=(), old_open=None, height=520):
    """Karte: Kunden (Größe = Nachfrage), Standorte eingefärbt nach Status. Ohne `old_open`: offen = grün, zu = grau.
    Mit `old_open` (Akt 2): weiterhin offen = lila, neu eröffnet = grün, alt aber jetzt zu = blau, nie offen = grau."""
    fig = go.Figure()
    open_set = tuple(sorted(open_set))
    if open_set:
        assign = assignment(inst, open_set)
        xs, ys = [], []
        for j, i in enumerate(assign):
            xs += [inst.cust_pos[j][0], inst.site_pos[i][0], None]
            ys += [inst.cust_pos[j][1], inst.site_pos[i][1], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLORS["line"], width=1), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[p[0] for p in inst.cust_pos], y=[p[1] for p in inst.cust_pos], mode="markers", name="Kunde",
                             marker=dict(color=C.COLORS["customer"], size=[5 + 1.4 * d for d in inst.demand], opacity=0.7),
                             text=[f"{nm}: Nachfrage {d}" for nm, d in zip(inst.cust_names, inst.demand)], hoverinfo="text"))
    if old_open is None:
        groups = [("Standort offen", list(open_set), C.COLORS["open"]),
                  ("Standort zu", [i for i in range(inst.m) if i not in open_set], C.COLORS["closed"])]
    else:
        old_set, new_set = set(old_open), set(open_set)
        groups = [("weiterhin offen", sorted(old_set & new_set), C.COLORS["kept_open"]),
                  ("neu eröffnet", sorted(new_set - old_set), C.COLORS["new_open"]),
                  ("alt, jetzt zu", sorted(old_set - new_set), C.COLORS["old_open"]),
                  ("nie offen", sorted(set(range(inst.m)) - old_set - new_set), C.COLORS["closed"])]
    for name, idx, color in groups:
        if not idx:
            continue
        fig.add_trace(go.Scatter(x=[inst.site_pos[i][0] for i in idx], y=[inst.site_pos[i][1] for i in idx], mode="markers+text", name=name,
                                 marker=dict(symbol="square", color=color, size=15, line=dict(color="#111111", width=1)),
                                 text=[inst.site_names[i].replace("Standort ", "S") for i in idx], textposition="top center", textfont=dict(size=10),
                                 customdata=[[inst.f[i]] for i in idx], hovertemplate="%{text}: Fixkosten %{customdata[0]}<extra></extra>"))
    pts = list(inst.site_pos) + list(inst.cust_pos)
    xs = [p[0] for p in pts]
    ys_ = [p[1] for p in pts]
    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False)
    fig.add_trace(go.Scatter(x=[min(xs) - 6, max(xs) + 6], y=[min(ys_) - 6, max(ys_) + 6], mode="markers", marker=dict(opacity=0), hoverinfo="skip", showlegend=False))
    return _base(fig, height)


def build_cost_curve(curve, k_star, markers=(), height=420):
    """Kostenkurve über die erzwungene Standortzahl k; k* markiert, Faustregel-Treffer (N -> (k_hat, Kosten, Lücke)) als Punkte."""
    ks = sorted(curve)
    fig = go.Figure(go.Scatter(x=ks, y=[curve[k] for k in ks], mode="lines+markers", name="Kosten bei k Standorten",
                               line=dict(color=C.COLORS["opt"], width=2)))
    fig.add_trace(go.Scatter(x=[k_star], y=[curve[k_star]], mode="markers", marker=dict(color=C.COLORS["open"], size=16, symbol="star"), name="k* (Optimum)"))
    if markers:
        fig.add_trace(go.Scatter(x=[k_hat for _n, (k_hat, _c, _g) in markers], y=[c for _n, (_k, c, _g) in markers],
                                 mode="markers+text", marker=dict(color=C.COLORS["rule"], size=12, symbol="diamond"),
                                 text=[f"1 je {n}" for n, _ in markers], textposition="top center", name="Faustregel"))
    fig.update_xaxes(title="Erzwungene Standortzahl k", dtick=1)
    fig.update_yaxes(title="Gesamtkosten")
    return _base(fig, height)


def build_rule_bars(cost_star, rules, height=340):
    """Balken: Optimum gegen die naiven Standortregeln, Beschriftung mit Lücke in %."""
    names = ["Optimum (gemeinsam)"] + [C.LABELS[k] for k in rules]
    costs = [cost_star] + [c for _o, c, _g in rules.values()]
    gaps = [0.0] + [g for _o, _c, g in rules.values()]
    colors = [C.COLORS["open"]] + [C.COLORS.get(k, C.COLORS["rule"]) for k in rules]
    fig = go.Figure(go.Bar(x=names, y=costs, marker=dict(color=colors),
                           text=[f"+{g:.1f} %".replace(".", ",") if g > 0 else "Optimum" for g in gaps], textposition="outside"))
    fig.update_yaxes(title="Gesamtkosten")
    return _base(fig, height)
