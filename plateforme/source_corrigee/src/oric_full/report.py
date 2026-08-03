from __future__ import annotations

from pathlib import Path
import json

import pandas as pd

from .models import CampaignResult, Outcome


def write_markdown_report(campaign: CampaignResult, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Rapport d’exécution ORI-C complet",
        "",
        f"- Exécution : `{campaign.run_id}`",
        f"- Début : {campaign.started_at}",
        f"- Fin : {campaign.finished_at}",
        f"- Entrées sélectionnées : {len(campaign.results)}",
        "",
        "## Lecture obligatoire",
        "",
        "Le **statut technique** indique si le moteur informatique s’est exécuté correctement. "
        "Le **verdict scientifique** reste `undetermined` tant qu’un critère préenregistré et gelé "
        "n’est pas associé au test. Une exécution réussie ne prouve aucune hypothèse à elle seule.",
        "",
        "## Statuts techniques",
        "",
    ]
    for key, value in campaign.counts.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Verdicts scientifiques", ""])
    for key, value in campaign.scientific_counts.items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Résultats par work package", ""])
    grouped: dict[str, list] = {}
    for result in campaign.results:
        grouped.setdefault(result.wp, []).append(result)
    for wp in sorted(grouped):
        rows = grouped[wp]
        technical: dict[str, int] = {}
        scientific: dict[str, int] = {}
        for row in rows:
            technical[row.outcome.value] = technical.get(row.outcome.value, 0) + 1
            scientific[row.scientific_verdict.value] = scientific.get(row.scientific_verdict.value, 0) + 1
        lines.append(f"### WP-{wp}")
        lines.append("")
        lines.append("Technique : " + ", ".join(f"{k}={v}" for k, v in sorted(technical.items())))
        lines.append("")
        lines.append("Scientifique : " + ", ".join(f"{k}={v}" for k, v in sorted(scientific.items())))
        lines.append("")
        problems = [
            result
            for result in rows
            if result.outcome in {Outcome.FAIL, Outcome.ERROR, Outcome.BLOCKED}
        ]
        for result in problems[:20]:
            lines.append(f"- `{result.test_id}` — **{result.outcome.value}** — {result.message}")
        if len(problems) > 20:
            lines.append(f"- … {len(problems) - 20} autres entrées dans `results.json`.")
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def write_csv_report(campaign: CampaignResult, output: Path) -> None:
    rows = []
    for result in campaign.results:
        rows.append(
            {
                "test_id": result.test_id,
                "wp": result.wp,
                "technical_outcome": result.outcome.value,
                "scientific_verdict": result.scientific_verdict.value,
                "criterion_id": result.criterion_id,
                "metric": result.metric,
                "threshold": result.threshold,
                "message": result.message,
                "duration_s": result.duration_s,
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)


def render_existing_result(run_dir: Path) -> Path:
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    lines = [
        "# Rapport ORI-C",
        "",
        f"Exécution : `{payload['run_id']}`",
        "",
        "## Statuts techniques",
        "",
    ]
    for key, value in payload["counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Verdicts scientifiques", ""])
    for key, value in payload.get("scientific_counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Voir `results.json` et `results.csv` pour le détail."])
    output = run_dir / "REPORT.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output
