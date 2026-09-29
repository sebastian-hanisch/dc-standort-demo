# Distributionszentren-Standortplanung – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-dc-standort-demo.streamlit.app/)**

Fall-Demo auf der Themenseite **Netzwerkdesign** für die Website "Sebastian Hanisch – Operations Research und
Machine Learning": wie viele Verteilzentren sollte ein Unternehmen eröffnen, und wo — und was passiert, wenn sich
die Nachfrage über die Zeit verschiebt? Anders als die Standortplanungs-Demo der "Konzepte"-Reihe (dieselbe
Standortwahl ohne Kapazitätsgrenze, **UFL**, aber als reiner Verfahrensvergleich: Add/Drop/Interchange, LP-Schranken,
Dual Ascent) erzählt diese Demo denselben Modellkern entlang zweier konkreter Geschäftsfragen.

## Zwei Akte, ein Netz

**Akt 1 — Wie viele Standorte, und was kostet Schätzen statt Rechnen?** Die Kostenkurve über eine erzwungene
Standortzahl $k$ ist um das freie Optimum $k^*$ herum flach: ein Standort daneben kostet kaum etwas. Aber eine
Faustregel ("1 Standort je $N$ Kunden"), die nicht zufällig nahe an $k^*$ trifft, kostet real zweistellige Prozent
mehr — nicht wenig.

**Akt 2 — Die Antwort von heute hält nicht ewig, aber Anpassen ist selbst teuer.** Dieselben Standorte und Kunden,
aber die Nachfrage verschiebt sich regional über die Zeit (eine Kartenregion wächst, eine andere schrumpft).
Verglichen wird die Kosten der alten, bei T0 optimalen Standortauswahl unter der neuen Nachfrage gegen das für T1
neu berechnete Optimum — und die einmalige Fixkosten-Summe der dafür neu zu eröffnenden Standorte.

**Anders als die vier "starr vs. reaktiv"-Fall-Demos in diesem Portfolio** (`fahrzeugflotte-demo`,
`robuste-kaiplatz-demo`, `blockzuweisung-demo`, `hofrobust-demo`): dort ist Reagieren auf eine Störung operativ und
billig, der Sieger hängt nur davon ab, wie schnell reagiert wird. Hier ist die Standortentscheidung eine
**Kapitalbindung**: Reagieren bedeutet neue Fixkosten, und ob sich das lohnt, hängt vom Verhältnis der
Umbaukosten zur laufenden Mehrkosten-Lücke ab — nicht davon, wie schnell man reagiert.

## Ergebnis (Zahlen aus den Tests)

Jede hier genannte Zahl ist in `tests/test_claims.py` belegt: Standardnetz 18 Kandidaten, 40 Kunden, Fixkosten-
Faktor 100 %, Seed 1 (SplitMix64, ganzzahlig, plattformstabil, derselbe Zufallsstrom wie in `standortplanung-demo`).

**Akt 1.** Das Optimum öffnet **7 Standorte** und kostet **39 345**. Die Faustregel "1 je 5" trifft mit 8 Standorten
fast daneben (**0,9 %** teurer) — die Kurve ist um $k^*$ herum flach. Weiter daneben wird es teuer: "1 je 8" (5
Standorte statt 7) kostet **3,3 %** mehr, "1 je 12" (4 Standorte) **6,9 %**, "1 je 3" (14 Standorte, weit zu viel)
**17,1 %**. Die Botschaft: ein bisschen daneben ist billig, eine unreflektierte Faustregel nicht.

**Akt 2.** Bei moderater Verschiebung (halbe Karte wächst ×1,8, schrumpft ×0,7): Festhalten an der alten Auswahl
kostet **3,1 %** mehr als nötig; 3 neue Standorte werden gebraucht, ihre Fixkosten (4 287) sind das **2,8-Fache**
der laufenden Lücke — der Umbau lohnt sich noch nicht sofort. Bei stärkerer Verschiebung (×2,8 / ×0,5) wächst die
Lücke auf **8,4 %**; dieselben 3 Standorte werden gebraucht, aber jetzt ist das Verhältnis **0,8** — der Umbau ist
günstiger als eine Periode der Mehrkosten, das Amortisations-Argument kippt. Bei gleichem Wachstumsfaktor, aber auf
ein Kartenviertel statt eine halbe Karte konzentriert, bleibt die Lücke mit **2,2 %** kleiner (nur 1 statt 3 neue
Standorte) — eine konzentrierte Verschiebung trifft weniger Standorte gleichzeitig als eine breite.

**Zusatz-Panel.** Zwei naive Standortregeln bei gleicher Standortzahl wie das Optimum: "größte Nachfragezentren"
(Score ohne Fixkosten-/Interaktions-Rücksicht) liegt **23,8 %** über dem Optimum, das plausiblere nachfragegewichtete
k-Means (+ nächster freier Kandidat) **9,8 %** — real, aber deutlich schwächer als eine gemeinsame Optimierung.
Anders als die k-Means-Demo (Depotwahl ohne Fixkosten) zählen hier Fixkosten und die freie Zuordnung nach
Eröffnung mit.

## Was nicht funktioniert hat / Vorab-Hypothesen

Eine Vorab-Messreihe hat drei Kandidaten-Hooks geprüft, bevor diese Demo gebaut wurde:

- **"Sequenziell (Cluster-Regel) statt gemeinsam optimieren" ist ein eigenständiger, tragender Hook — widerlegt
  als Hauptsäule.** Der Effekt ist real (9,8 % / 23,8 %), aber konzeptionell zu nah an der k-Means-Demo (dieselbe
  Depotwahl-Idee, nur jetzt mit Fixkosten) und die schlechtere Regel wirkt wie ein Strohmann. Als Zusatz-Panel
  aufgenommen, nicht als Akt.
- **"Reagieren ist bei Nachfrageverschiebung immer teurer als Festhalten" — nicht monoton in der erwarteten
  Richtung.** Die laufende Lücke wächst zwar mit der Verschiebungsstärke, aber das Verhältnis Umbaukosten zu
  Lücke **fällt** dabei tendenziell (der Umbau ist ein Sprung, sobald ein neuer Standort nötig wird; die Lücke
  wächst dagegen stetig) — bei starker Verschiebung kann der Umbau schon lohnen. Die Demo zeigt deshalb bewusst
  beide Fälle (Standardnetz: Verhältnis 2,8; starke Verschiebung: Verhältnis 0,8), statt nur die eine Richtung zu
  behaupten.

## Grenzen (was die Demo nicht zeigt)

Unkapazitiert (mit Kapazitäten ist die LP-Schranke wieder schwach, siehe die kapazitierte Standortplanung-Demo),
eine einzelne, einmalige Nachfrageverschiebung (kein rollierender Planungshorizont mit mehreren Zeitschritten),
regionale Verschiebung als einfacher Faktor statt eines Prognosemodells, kein Zwischenschritt zwischen "alt
behalten" und "vollständig neu bauen" (z. B. nur einen einzelnen Standort nachrüsten).

## Dateien

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: Akt 1, Akt 2, Zusatz-Panel, 📐-Abschnitt |
| `dcs_scenario.py` | Netz (Kopie aus `standortplanung-demo`), Nachfrageverschiebung `shift_demand` |
| `dcs_exact.py` | HiGHS-MILP: freies Optimum, Optimum bei erzwungenem $k$, Kosten/Zuordnung einer Auswahl |
| `dcs_rules.py` | Faustregel "1 je N", zwei naive Standortregeln (größte Nachfragezentren, gewichtetes k-Means) |
| `dcs_evaluation.py` | Die drei Akte: Kostenkurve, Verschiebungsvergleich, Regelvergleich |
| `dcs_visualization.py` | Karte, Kostenkurve, Regel-Balken |
| `dcs_presets.py`, `dcs_constants.py` | Presets, Permalink, Regler-Grenzen |
| `tests/` | Szenario, Exakt (gegen Brute-Force), Regeln, Auswertung, Presets, App, `test_claims.py` (jede README-Zahl), `test_copies.py` (Wache gegen Drift vom UFL-Kern in `standortplanung-demo`) |

Lokal starten: `pip install -r requirements.txt`, dann `streamlit run app.py`; Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests`.
