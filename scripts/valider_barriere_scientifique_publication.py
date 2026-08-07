from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "plateforme/source_corrigee"
CATALOGUE = PLATFORM / "src/oric_full/resources/catalogue_tests.csv"
COVERAGE = ROOT / "plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json"

QUARANTINED_ENGINES = {"condensation", "volatile_budget", "late_accretion", "planetary_value"}
SOURCE_REGISTRY = ROOT / "donnees_externes/SOURCES_EMPIRIQUES_PRIORITAIRES_2026-08-07.json"


def load_catalogue() -> dict[str, dict[str, str]]:
    with CATALOGUE.open(encoding="utf-8", newline="") as handle:
        return {row["test_id"]: row for row in csv.DictReader(handle)}


def check_coverage(catalogue: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    if not COVERAGE.exists():
        errors.append("REAL_DATA_COVERAGE.json absent: le mode données réelles ne peut pas être publié.")
        return errors
    payload = json.loads(COVERAGE.read_text(encoding="utf-8"))
    datasets = payload.get("datasets", {})
    if not isinstance(datasets, dict):
        return ["REAL_DATA_COVERAGE.json: datasets invalide"]
    for dataset, scope in datasets.items():
        if scope.get("scope_mode") != "allow_list":
            errors.append(f"{dataset}: scope_mode doit être allow_list")
            continue
        for test_id in scope.get("supported_test_ids", []):
            spec = catalogue.get(test_id)
            if spec is None:
                errors.append(f"{dataset}: test inconnu dans la allow-list: {test_id}")
                continue
            if spec.get("engine") in QUARANTINED_ENGINES:
                errors.append(
                    f"{dataset}: {test_id} utilise le moteur en quarantaine {spec.get('engine')} et ne peut pas être déclaré couvert empiriquement"
                )
    return errors



def check_source_registry() -> list[str]:
    if not SOURCE_REGISTRY.exists():
        return ["registre des sources empiriques prioritaires absent"]
    payload = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    sources = payload.get("sources", [])
    if not isinstance(sources, list) or not sources:
        return ["registre des sources empiriques prioritaires vide ou invalide"]
    errors: list[str] = []
    by_id = {item.get("source_id"): item for item in sources if isinstance(item, dict)}
    decision = by_id.get("PLANETARY_HISTORIES_SCHEMA_DECISION")
    if not decision or decision.get("kind") != "invalid_as_direct_empirical_dataset":
        errors.append("planetary_histories doit rester explicitement interdit comme dataset empirique direct")
    for item in sources:
        if not isinstance(item, dict):
            errors.append("entrée source non objet")
            continue
        if item.get("empirical_evidence") is True and not (item.get("article_doi") or item.get("dataset_doi") or item.get("doi")):
            errors.append(f"{item.get('source_id')}: source empirique sans DOI")
    return errors

def iter_results() -> list[Path]:
    roots = [
        ROOT / "plateforme/campagne_maximale_reelle",
        ROOT / "plan_directeur",
    ]
    paths: list[Path] = []
    for base in roots:
        if base.exists():
            paths.extend(base.rglob("results.json"))
    return sorted(set(paths))


def check_existing_results(catalogue: dict[str, dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for path in iter_results():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not payload.get("metadata", {}).get("real_data_only"):
            continue
        for result in payload.get("results", []):
            if result.get("outcome") != "pass":
                continue
            test_id = result.get("test_id", "")
            engine = result.get("details", {}).get("engine") or catalogue.get(test_id, {}).get("engine")
            if engine in QUARANTINED_ENGINES:
                errors.append(
                    f"{path.relative_to(ROOT)}: {test_id} est PASS en mode réel avec moteur en quarantaine {engine}"
                )
    return errors


def check_source_regressions() -> list[str]:
    errors: list[str] = []
    planetary = (PLATFORM / "src/oric_full/domains/planetary.py").read_text(encoding="utf-8")
    matter = (PLATFORM / "src/oric_full/domains/matter.py").read_text(encoding="utf-8")
    runner = (PLATFORM / "src/oric_full/runner.py").read_text(encoding="utf-8")
    climate = (PLATFORM / "src/oric_full/domains/climate.py").read_text(encoding="utf-8")
    publication = (ROOT / "scripts/valider_publication_stable.py").read_text(encoding="utf-8")
    integrator = (ROOT / "plateforme/campagne_maximale_reelle/integrer_donnees_existantes.py").read_text(encoding="utf-8")
    if 'errors="coerce").fillna(0.0)' in planetary and "def volatile_closure" in planetary:
        errors.append("volatile_closure contient encore une imputation zéro interdite")
    if 'g.loc[g["gibbs_energy"].idxmin()' in matter:
        errors.append("analyze_condensation contient encore le faux minimum Gibbs global")
    if 'if not scope or scope.get("scope_mode") != "allow_list":\n                        continue' in runner:
        errors.append("runner réel encore fail-open pour les datasets non enregistrés")
    if 'to_numpy(dtype=float)' in climate.split('def compare_memory_families', 1)[1].split('def blocked_cross_validation', 1)[0] and '_numeric_time_axis' not in climate:
        errors.append("compare_memory_families force encore les dates ISO en float")
    if ".read_text()" in publication:
        errors.append("valider_publication_stable.py contient encore des read_text sans UTF-8 explicite")
    if 'for sheet in pd.ExcelFile(path).sheet_names' in integrator or 'excel = pd.ExcelFile(path)' in integrator:
        errors.append("integrer_donnees_existantes.py laisse encore des ExcelFile sans fermeture explicite")
    return errors


def main() -> int:
    catalogue = load_catalogue()
    errors = check_coverage(catalogue) + check_source_registry() + check_existing_results(catalogue) + check_source_regressions()
    if errors:
        print("BARRIERE SCIENTIFIQUE PUBLICATION: ECHEC")
        for error in errors:
            print(f"- {error}")
        return 1
    print("BARRIERE SCIENTIFIQUE PUBLICATION: OK")
    print("- registre de portée réel fail-closed")
    print("- aucun moteur en quarantaine déclaré comme preuve empirique")
    print("- registre des sources réelles explicite et planetary_histories interdit comme pseudo-donnée")
    print("- aucune imputation zéro dans le bilan volatil")
    print("- aucun minimum Gibbs global présenté comme équilibre")
    print("- dates climatiques ISO converties explicitement")
    print("- lectures de publication figées en UTF-8")
    print("- classeurs Excel ouverts avec fermeture explicite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
