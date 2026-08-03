from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import json

from .environment import sha256_file
from .models import TestSpec


def write_protocols(specs: list[TestSpec], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[TestSpec]] = defaultdict(list)
    for spec in specs:
        grouped[spec.wp].append(spec)
    paths = []
    for wp, items in sorted(grouped.items()):
        lines = [f"# Protocole WP-{wp}", "", "## Règles", "", "- Geler les données confirmatoires avant analyse.", "- Déclarer le modèle nul et le témoin de complexité égale.", "- Conserver les échecs et analyses non concluantes.", "- Ne jamais transformer un contrôle technique réussi en validation scientifique.", "", "## Registre", ""]
        for item in items:
            lines.extend(
                [
                    f"### {item.test_id}",
                    "",
                    item.description,
                    "",
                    f"- Mode : `{item.mode.value}`",
                    f"- Moteur : `{item.engine}`",
                    f"- Priorité : {item.priority}",
                    f"- Confirmatoire : {'oui' if item.confirmatory else 'non'}",
                    f"- Données : {', '.join(item.required_datasets) if item.required_datasets else 'aucune donnée externe obligatoire'}",
                    "- Prédiction ORI-C : À renseigner avant exécution confirmatoire.",
                    "- Modèle nul : À renseigner.",
                    "- Témoin de complexité égale : À renseigner.",
                    "- Métrique principale : À renseigner.",
                    "- Seuil : À renseigner.",
                    "- Conditions d’arrêt : À renseigner.",
                    "",
                ]
            )
        path = output_dir / f"WP-{wp}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        paths.append(path)
    return paths


def preregister(specs: list[TestSpec], output: Path, metadata: dict | None = None) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": metadata or {},
        "frozen_tests": [s.to_dict() for s in specs],
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    digest_path = output.with_suffix(output.suffix + ".sha256")
    digest_path.write_text(f"{sha256_file(output)}  {output.name}\n", encoding="utf-8")
    return output
