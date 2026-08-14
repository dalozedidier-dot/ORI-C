#!/usr/bin/env python3
"""Exécute demo_minimale.py et produit un rapport HTML autonome.

Le script ne recalcule rien lui-même : l'autorité reste demo_minimale.py. Il
capture sa sortie, extrait les comparaisons obtenu/publié et construit une vue
lisible destinée aux artefacts CI ou à une vérification locale.
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARE_RE = re.compile(
    r"^\s*(OK|!!)\s+(.+?)\s+([-+0-9.eE]+)\s+publié\s+([-+0-9.eE]+)\s*$"
)
INTERVENTION_RE = re.compile(r"^\s+([a-z0-9_]+)\s+([0-9.]+)\s+fois le plancher d[’\']ensemble\s*$")
BILAN_RE = re.compile(r"^\s*(\d+)\s*/\s*(\d+)\s+contrôles reproduisent")


def lire_sortie() -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "demo_minimale.py")],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    sortie = proc.stdout
    if proc.stderr:
        sortie += "\n" + proc.stderr
    return proc.returncode, sortie


def extraire(sortie: str):
    comparaisons = []
    interventions = []
    bilan = None
    for ligne in sortie.splitlines():
        m = COMPARE_RE.match(ligne)
        if m:
            statut, label, obtenu, publie = m.groups()
            comparaisons.append(
                {
                    "ok": statut == "OK",
                    "label": label.strip(),
                    "obtenu": float(obtenu),
                    "publie": float(publie),
                }
            )
            continue
        m = INTERVENTION_RE.match(ligne)
        if m:
            interventions.append((m.group(1), float(m.group(2))))
            continue
        m = BILAN_RE.match(ligne)
        if m:
            bilan = (int(m.group(1)), int(m.group(2)))
    return comparaisons, interventions, bilan


def barre_ratio(obtenu: float, publie: float) -> str:
    denom = max(abs(obtenu), abs(publie), 1e-15)
    a = max(2.0, min(100.0, 100.0 * abs(obtenu) / denom))
    b = max(2.0, min(100.0, 100.0 * abs(publie) / denom))
    return (
        '<div class="bars" aria-label="comparaison visuelle">'
        f'<span class="obt" style="width:{a:.2f}%" title="obtenu"></span>'
        f'<span class="pub" style="width:{b:.2f}%" title="publié"></span>'
        '</div>'
    )


def produire_html(sortie: str, comparaisons, interventions, bilan) -> str:
    if bilan is None:
        bilan = (sum(1 for c in comparaisons if c["ok"]), len(comparaisons))
    rows = []
    for c in comparaisons:
        ecart = c["obtenu"] - c["publie"]
        rows.append(
            "<tr>"
            f"<td><strong>{html.escape(c['label'])}</strong></td>"
            f"<td>{c['obtenu']:.12g}</td>"
            f"<td>{c['publie']:.12g}</td>"
            f"<td>{ecart:.3g}</td>"
            f"<td>{'OK' if c['ok'] else 'DIVERGE'}</td>"
            f"<td>{barre_ratio(c['obtenu'], c['publie'])}</td>"
            "</tr>"
        )
    int_rows = "".join(
        f"<li><code>{html.escape(nom)}</code><strong>{ratio:,.1f}×</strong></li>"
        for nom, ratio in interventions
    )
    safe_output = html.escape(sortie)
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ORI-C — démonstration minimale reproductible</title>
<style>
:root{{--bg:#08111d;--panel:#0e1b2a;--line:#24374b;--text:#eaf2f8;--muted:#9db0c1;--ok:#4bd3a5;--warn:#ffbf69;--accent:#78a9ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,sans-serif}}
main{{width:min(1180px,calc(100% - 2rem));margin:0 auto;padding:3rem 0}}h1{{font-size:clamp(2rem,5vw,4rem);margin:.2rem 0}}h2{{margin-top:2.4rem}}p{{color:var(--muted)}}.lead{{font-size:1.08rem;max-width:850px}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin:2rem 0}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:1rem}}.card strong{{display:block;font-size:2rem}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line)}}th,td{{padding:.75rem;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}}th{{color:var(--muted)}}
.bars{{width:180px;max-width:100%;display:grid;gap:3px}}.bars span{{height:7px;border-radius:999px;display:block}}.bars .obt{{background:var(--ok)}}.bars .pub{{background:var(--accent)}}
ul.scenarios{{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.6rem}}ul.scenarios li{{display:flex;justify-content:space-between;gap:1rem;background:var(--panel);border:1px solid var(--line);padding:.8rem;border-radius:12px}}ul.scenarios strong{{color:var(--ok)}}
pre{{white-space:pre-wrap;background:#050b12;border:1px solid var(--line);padding:1rem;border-radius:12px;overflow:auto;color:#cfe1ee}}code{{color:#b9d3ff}}
.legend{{display:flex;gap:1rem;flex-wrap:wrap;color:var(--muted)}}.dot{{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:.35rem}}.obt-dot{{background:var(--ok)}}.pub-dot{{background:var(--accent)}}
@media(max-width:760px){{table{{font-size:.82rem}}th:nth-child(4),td:nth-child(4){{display:none}}}}
</style></head><body><main>
<p>ORI-C · rapport CI reproductible</p><h1>Démonstration minimale</h1>
<p class="lead">Ce rapport est une vue de la sortie de <code>demo_minimale.py</code>. Les analyses biologiques sont réexécutées depuis les données versionnées ; la métrique astronomique certifiée est recalculée depuis les sorties numériques de robustesse. Ce fichier HTML ne remplace aucun résultat d'autorité.</p>
<div class="summary"><div class="card"><span>Contrôles</span><strong>{bilan[0]} / {bilan[1]}</strong></div><div class="card"><span>Comparaisons numériques</span><strong>{len(comparaisons)}</strong></div><div class="card"><span>Scénarios N-corps affichés</span><strong>{len(interventions)}</strong></div></div>
<h2>Valeurs recalculées vs publiées</h2><p class="legend"><span><i class="dot obt-dot"></i>obtenu</span><span><i class="dot pub-dot"></i>publié</span></p>
<table><thead><tr><th>Mesure</th><th>Obtenu</th><th>Publié</th><th>Écart</th><th>Statut</th><th>Vue</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Diagnostic astronomique secondaire</h2><p>Les valeurs ci-dessous sont les rapports <code>effect_to_ensemble_floor_ratio</code> du CSV contrefactuel. Elles sont volontairement séparées du ratio certifié <code>intervention / plus grand écart numérique sélectionné</code> affiché dans le tableau ci-dessus. Il s'agit de résultats de modèle, pas d'observations directes.</p><ul class="scenarios">{int_rows}</ul>
<h2>Sortie complète</h2><pre>{safe_output}</pre>
</main></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="demo_minimale_report.html")
    args = parser.parse_args()
    code, sortie = lire_sortie()
    print(sortie, end="" if sortie.endswith("\n") else "\n")
    comparaisons, interventions, bilan = extraire(sortie)
    cible = Path(args.output)
    if not cible.is_absolute():
        cible = (ROOT / cible).resolve()
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(produire_html(sortie, comparaisons, interventions, bilan), encoding="utf-8")
    print(f"Rapport HTML : {cible}")
    if code != 0:
        return code
    if bilan is None or bilan[0] != bilan[1]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
