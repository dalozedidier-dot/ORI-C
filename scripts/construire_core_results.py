#!/usr/bin/env python3
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "preuves" / "CORE_RESULTS.json"
MD = ROOT / "CORE_RESULTS.md"
HTML = ROOT / "site" / "core.html"

BRANCH_LABEL = {"matiere": "Matière", "systeme_solaire": "Système solaire", "vivant": "Vivant"}


def badge(x: dict) -> str:
    s = x["statut"]
    if s == "certifie" and x["verdict"] == "supports": return "certifié positif"
    if s == "resultat_negatif" or x["verdict"] == "does_not_support": return "résultat négatif"
    if s == "non_concluant": return "non concluant"
    if "modele" in x["portee"] or x.get("niveau_preuve") == "E4_modele": return "modèle / exploratoire"
    return s.replace("_", " ")


def build_markdown(d: dict) -> str:
    lines = [
        "# ORI-C — noyau de résultats à lire en premier", "",
        "> Vue courte dérivée de `preuves/CORE_RESULTS.json`. Elle ne remplace ni `preuves/PREUVES.json` ni les verdicts d’autorité.", "",
        f"Le noyau contient **{len(d['items'])} résultats** choisis pour couvrir les trois branches, les succès, les résultats négatifs, les limites et les verrous quantitatifs. Aucun statut n’est réécrit ici.", "",
        "| Rang | Branche | ID | Lecture | Verdict d’autorité | Pourquoi il est dans le noyau |", "|---:|---|---|---|---|---|"
    ]
    for x in d["items"]:
        lines.append(f"| {x['rank']} | {BRANCH_LABEL[x['branch']]} | `{x['id']}` | {badge(x)} | `{x['verdict']}` | {x['why_core']} |")
    lines += ["", "## Règle de lecture", "", "Un lecteur externe peut commencer par cette page, puis ouvrir l’artefact de chaque ligne. Les résultats rétrospectifs restent rétrospectifs, les résultats de modèle restent au niveau modèle, et les résultats négatifs restent visibles. Le compteur §XIV demeure l’autorité pour les verrous de confirmation.", ""]
    return "\n".join(lines)


def build_html(d: dict) -> str:
    cards=[]
    for x in d["items"]:
        cards.append(f'''<article class="card" data-branch="{x['branch']}"><div class="meta"><span>{x['rank']:02d}</span><span>{html.escape(BRANCH_LABEL[x['branch']])}</span><span>{html.escape(badge(x))}</span></div><h2><code>{html.escape(x['id'])}</code></h2><p>{html.escape(x['why_core'])}</p><p class="verdict">{html.escape(x['verdict'])}</p><a href="https://github.com/dalozedidier-dot/ORI-C/blob/main/{html.escape(x['artefact'])}">Artefact d’autorité</a></article>''')
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ORI-C — noyau de résultats</title><link rel="stylesheet" href="assets/styles.css"><style>.core{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}.card{{border:1px solid var(--line,#26384a);border-radius:14px;padding:1rem;background:var(--panel,#0e1b2a)}}.meta{{display:flex;gap:.5rem;flex-wrap:wrap;font-size:.8rem;opacity:.8}}.meta span{{border:1px solid currentColor;border-radius:999px;padding:.15rem .45rem}}.verdict{{font-family:ui-monospace,monospace;overflow-wrap:anywhere}}code{{font-size:.9em}}</style></head><body><header class="site-header"><nav><a href="index.html">Accueil</a><a href="preuves.html">État des preuves</a><a aria-current="page" href="core.html">Noyau</a><a href="methode.html">Méthode</a><a href="reproductibilite.html">Reproductibilité</a><a href="exploration.html">Explorer</a><a class="nav-repo" href="https://github.com/dalozedidier-dot/ORI-C">Dépôt GitHub</a></nav></header><main><p class="eyebrow">Lecture externe courte</p><h1>{len(d['items'])} résultats à lire en premier</h1><p>Cette vue ne crée aucun verdict. Elle expose un sous-ensemble du registre machine avec succès, résultats négatifs, limites et résultats de modèle clairement séparés.</p><section class="core">{''.join(cards)}</section></main></body></html>'''


def main() -> int:
    d=json.loads(SRC.read_text(encoding="utf-8"))
    MD.write_text(build_markdown(d),encoding="utf-8",newline="\n")
    HTML.write_text(build_html(d),encoding="utf-8",newline="\n")
    print(f"core: {len(d['items'])} résultats -> {MD.name}, site/core.html")
    return 0

if __name__ == "__main__": raise SystemExit(main())
