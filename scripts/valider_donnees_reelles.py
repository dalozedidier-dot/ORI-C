#!/usr/bin/env python3
"""Valide les trois jeux réels intégrés et les résultats qu'ils produisent."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "donnees_externes"
OUT = ROOT / "plan_directeur/campagne_recherche_suivante/resultats"

EXPECTED_DATASETS = {
    "vesicules_sokolskyi_baum_2026": 12,
    "histoire_antibiotique_donofrio_2026": 3,
    "speleothemes_noaa_0_22ka": 1,
}


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path.relative_to(ROOT))
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_dataset(dataset_id: str, expected_count: int, errors: list[str]) -> dict[str, Any]:
    folder = EXTERNAL / dataset_id
    try:
        source = load_json(folder / "SOURCE.json")
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"{dataset_id}: SOURCE.json illisible ou absent ({exc})")
        return {"id": dataset_id, "status": "invalid_source"}

    provenance = source.get("file_provenance", [])
    if len(provenance) != expected_count:
        errors.append(
            f"{dataset_id}: {len(provenance)} fichiers inscrits, {expected_count} attendus"
        )
    if source.get("missing_expected"):
        errors.append(f"{dataset_id}: fichiers attendus manquants {source['missing_expected']}")

    checked_files: list[dict[str, Any]] = []
    for item in provenance:
        relative = Path(str(item.get("local_path", "")))
        path = folder / relative
        name = str(item.get("name", relative.name))
        if not path.is_file():
            errors.append(f"{dataset_id}: fichier absent {relative.as_posix()}")
            continue
        current_size = path.stat().st_size
        current_hash = sha256(path)
        if current_size != item.get("size_bytes"):
            errors.append(f"{dataset_id}: taille modifiée pour {name}")
        if current_hash != item.get("sha256"):
            errors.append(f"{dataset_id}: empreinte modifiée pour {name}")
        checked_files.append(
            {"name": name, "size_bytes": current_size, "sha256": current_hash}
        )

    return {
        "id": dataset_id,
        "status": "verified" if len(checked_files) == expected_count else "incomplete",
        "files_verified": len(checked_files),
        "dataset_sha256": source.get("sha256"),
        "acquisition_method": source.get("acquisition_method"),
    }


def validate_results(errors: list[str]) -> dict[str, Any]:
    vesicles = load_json(ROOT / "03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json")
    antibiotic = load_json(
        ROOT / "03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json"
    )
    speleothems = load_json(
        ROOT / "02_branche_systeme_solaire/tests_suivants/resultats/AUDIT_SPELEOTHEMES.json"
    )
    synthesis = load_json(OUT / "SYNTHESE.json")

    checks = {
        "vesicules": {
            "status": vesicles.get("status"),
            "pairs": vesicles.get("pairs"),
            "verdict": vesicles.get("global_verdict"),
        },
        "antibiotique": {
            "status": antibiotic.get("status"),
            "rows": antibiotic.get("rows"),
            "verdict": antibiotic.get("verdict"),
        },
        "speleothemes_noaa": {
            "status": speleothems.get("status"),
            "rows_age_isotope": speleothems.get("rows_age_isotope"),
            "sites": speleothems.get("independent_site_count"),
            "schema": speleothems.get("source_schema"),
        },
        "campagne": {
            "execution_errors": synthesis.get("execution_errors"),
            "waiting_for_external_data": synthesis.get("waiting_for_external_data"),
        },
    }

    expected = [
        (vesicles.get("status") == "analysed", "vésicules: analyse non exécutée"),
        (vesicles.get("pairs") == 11760, "vésicules: 11 760 paires attendues"),
        (
            vesicles.get("global_verdict") == "all_pre_registered_components_supported",
            "vésicules: verdict attendu absent",
        ),
        (antibiotic.get("status") == "analysed", "antibiotique: analyse non exécutée"),
        (antibiotic.get("rows") == 288, "antibiotique: 288 lignes attendues"),
        (
            antibiotic.get("verdict") == "history_supported_against_both_controls",
            "antibiotique: verdict attendu absent",
        ),
        (speleothems.get("status") == "audited", "NOAA: audit non exécuté"),
        (speleothems.get("rows_age_isotope") == 27721, "NOAA: 27 721 mesures attendues"),
        (speleothems.get("independent_site_count") == 36, "NOAA: 36 sites attendus"),
        (
            speleothems.get("source_schema") == "noaa_two_table_compilation",
            "NOAA: schéma à deux tables non reconnu",
        ),
        (synthesis.get("execution_errors") == 0, "campagne: erreurs d'exécution"),
        (
            synthesis.get("waiting_for_external_data") == 0,
            "campagne: bloc encore en attente de données",
        ),
    ]
    errors.extend(message for passed, message in expected if not passed)
    return checks


def main() -> int:
    errors: list[str] = []

    acquisition_report = load_json(EXTERNAL / "ACQUISITION_REPORT.json")
    acquisition_by_id = {item.get("id"): item for item in acquisition_report}
    for dataset_id in EXPECTED_DATASETS:
        item = acquisition_by_id.get(dataset_id)
        if item is None:
            errors.append(f"rapport d'acquisition: jeu absent {dataset_id}")
        elif item.get("status") != "ok":
            errors.append(
                f"rapport d'acquisition: {dataset_id} a le statut {item.get('status')}"
            )

    datasets = [
        validate_dataset(dataset_id, count, errors)
        for dataset_id, count in EXPECTED_DATASETS.items()
    ]
    try:
        results = validate_results(errors)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors.append(f"résultat scientifique illisible ou absent ({exc})")
        results = {}

    report = {
        "schema": 1,
        "status": "validated" if not errors else "failed",
        "datasets": datasets,
        "results": results,
        "errors": errors,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "VALIDATION_DONNEES_REELLES.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    lines = [
        "# Validation des données réelles intégrées",
        "",
        f"Statut : **{report['status']}**.",
        "",
        "## Jeux contrôlés",
        "",
    ]
    for item in datasets:
        noun = "fichier vérifié" if item["files_verified"] == 1 else "fichiers vérifiés"
        lines.append(f"- `{item['id']}` : {item['files_verified']} {noun}.")
    lines.extend(
        [
            "",
            "## Analyses contrôlées",
            "",
            "- Vésicules : 11 760 paires.",
            "- Antibiotique : 288 lignes.",
            "- NOAA : 27 721 mesures âge–δ18O sur 36 sites.",
        ]
    )
    if errors:
        lines.extend(["", "## Erreurs", ""])
        lines.extend(f"- {error}" for error in errors)
    (OUT / "VALIDATION_DONNEES_REELLES.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    if errors:
        print("ÉCHEC DU TEST DES DONNÉES RÉELLES")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Test des données réelles réussi :")
    print("- 12 classeurs de vésicules vérifiés et analysés")
    print("- 3 CSV antibiotiques vérifiés ; analyse sur 288 lignes")
    print("- CSV NOAA vérifié ; 27 721 mesures sur 36 sites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
