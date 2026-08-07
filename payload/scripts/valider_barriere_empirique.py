#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "plateforme/source_corrigee/src"
sys.path.insert(0, str(SRC))

from oric_full.models import Outcome, ScientificVerdict  # noqa: E402
from oric_full.registry import Registry  # noqa: E402
from oric_full.runner import RunOptions, run_campaign  # noqa: E402

DATA = ROOT / "plateforme/campagne_maximale_reelle/data"
COVERAGE = DATA / "REAL_DATA_COVERAGE.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    errors: list[str] = []
    document = json.loads(COVERAGE.read_text(encoding="utf-8"))
    if document.get("schema_version") != 2:
        errors.append("REAL_DATA_COVERAGE.json doit être en schema_version 2")
    datasets = document.get("datasets", {})
    policy_path = ROOT / "plateforme/campagne_maximale_reelle/EMPIRICAL_POLICY.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    if policy.get("schema_version") != 2:
        errors.append("EMPIRICAL_POLICY.json doit être en schema_version 2")
    policy_datasets = policy.get("datasets", {})
    for name, scope in datasets.items():
        for key in ["data_kind", "eligible_for_empirical_proof", "scope_mode", "supported_test_ids", "limitations"]:
            if key not in scope:
                errors.append(f"{name}: champ de pare-feu manquant: {key}")
        if scope.get("scope_mode") != "allow_list":
            errors.append(f"{name}: scope_mode doit rester allow_list")

    if set(datasets) != set(policy_datasets):
        errors.append("REAL_DATA_COVERAGE.json et EMPIRICAL_POLICY.json n'ont pas les mêmes datasets")
    for name, expected in policy_datasets.items():
        current = datasets.get(name, {})
        for key in ["data_kind", "eligible_for_empirical_proof", "scope_mode", "supported_test_ids", "limitations"]:
            if current.get(key) != expected.get(key):
                errors.append(f"{name}: {key} diverge de EMPIRICAL_POLICY.json")

    forbidden_as_empirical = {
        "benchmark_cases",
        "biology_cases",
        "cell_architecture",
        "modern_climate_ensemble",
        "molecular_inventory",
        "nucleosynthesis_yields",
        "reaction_network",
        "thermochemical_phases",
        "volatile_inventory",
    }
    for name in forbidden_as_empirical:
        scope = datasets.get(name, {})
        if scope.get("eligible_for_empirical_proof") is True:
            errors.append(f"{name}: ne doit pas être admissible comme preuve empirique")
        if scope.get("supported_test_ids"):
            errors.append(f"{name}: aucune allow-list empirique ne doit être active")

    exact_allowlists = {
        "late_accretion_tracers": ["P5-001"],
        "partition_experiments": ["P3-001", "P3-002"],
        "antibiotic_design": ["R1-005", "R1-009", "R1-010"],
        "prebiotic_design": ["V1-001", "V1-004"],
        "endosymbiosis_events": ["B2-003"],
        "prebiotic_lineages": [],
        "isotope_tracers": [],
        "modern_climate_timeseries": [],
    }
    for name, expected in exact_allowlists.items():
        got = datasets.get(name, {}).get("supported_test_ids")
        if got != expected:
            errors.append(f"{name}: allow-list {got!r} != {expected!r}")

    expected_hashes = {
        "late_accretion_tracers.csv": "570219a728e5df80ecc2a628c4fb79d9b67139cdf11d502660d855363141c91a",
        "thermochemical_phases.csv": "60eebfa981cb9b5d13001c65e87f0eaaf0d0221afac6f84cac39ee16c5c04d45",
        "volatile_inventory.csv": "e93d43b9d287bba0ebf6da3bef9594f5ba95120b8c5398058616d094a9da3f9f",
        "modern_climate_timeseries.csv": "e2f08d75975cdfe6ff3cd6cc0e382439588b2bcd645ac04e06575e7ea261057e",
    }
    for name, expected in expected_hashes.items():
        path = DATA / name
        if not path.exists():
            errors.append(f"donnée attendue absente: {name}")
        elif sha256(path) != expected:
            errors.append(f"empreinte inattendue: {name}")
    if (DATA / "planetary_histories.csv").exists():
        errors.append("planetary_histories.csv doit rester absent")

    paleo_dir = ROOT / "donnees_externes/donnees_reelles_2026_08_07/paleoclimat_long"
    paleo_hashes = {
        "edc-co2-2008.txt": "ae2ecff8e048c2357094c14742fb83eecc97c896707fc1f983614818427ae390",
        "edc3deuttemp2007.txt": "b801fc2e422d427524619be25b50ee86fd63b36eb440eb5044d9bec12a4d1747",
        "lisiecki2005_LR04.txt": "973a52d988da04333c98c3fc0cb51babac2fa9bb1c05d42de3d6df726d96b6fc",
        "vostok_deutnat.txt": "c69eca96499bece4b2f65d4e40240f52e0bfb4027383b3f2db68a1b3e36c75f6",
    }
    for name, expected in paleo_hashes.items():
        path = paleo_dir / name
        if not path.exists():
            errors.append(f"source paléoclimatique longue absente: {name}")
        elif sha256(path) != expected:
            errors.append(f"empreinte paléoclimatique inattendue: {name}")

    registry = Registry.load()
    sensitive_ids = {
        *(f"M4-{i:03d}" for i in range(1, 16)),
        *(f"P4-{i:03d}" for i in range(1, 11)),
        *(f"P5-{i:03d}" for i in range(1, 11)),
        *(f"P6-{i:03d}" for i in range(1, 13)),
        *(f"CL1-{i:03d}" for i in range(1, 11)),
    }
    specs = registry.select(test_ids=sensitive_ids)
    campaign = run_campaign(specs, RunOptions(data_dir=DATA, oric_root=ROOT, real_data_only=True))
    by_id = {r.test_id: r for r in campaign.results}
    for test_id, result in by_id.items():
        if test_id == "P5-001":
            if result.outcome != Outcome.PASS:
                errors.append("P5-001 doit être le seul test de ce bloc débloqué par la compilation GEOROC")
        elif test_id == "P6-012":
            if result.outcome != Outcome.NOT_RUN:
                errors.append("P6-012 doit rester un protocole humain non exécuté")
        elif result.outcome != Outcome.BLOCKED:
            errors.append(f"{test_id}: devrait rester blocked, obtenu {result.outcome.value}")
        if result.scientific_verdict == ScientificVerdict.SUPPORTS:
            errors.append(f"{test_id}: aucun verdict SUPPORTS n'est autorisé dans cet audit de ressources")

    payload = {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "coverage_datasets": len(datasets),
        "sensitive_tests_checked": len(campaign.results),
        "technical_counts": campaign.counts,
        "scientific_counts": campaign.scientific_counts,
        "rule": "Un fichier n'est jamais une preuve par présence; le pare-feu est fail-closed et test-specific.",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
