from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def condition_key(ab: object, nutrient: object) -> str:
    return f"AMK{ab}_N{nutrient}".replace(".", "p")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import reel Windels et al. 2024, sans simulation ni imputation")
    parser.add_argument("evolution_csv", type=Path)
    parser.add_argument("phenotypes_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("provenance_json", type=Path)
    args = parser.parse_args()

    evol = pd.read_csv(args.evolution_csv)
    phen = pd.read_csv(args.phenotypes_csv)
    if set(evol.columns) != {"AB_conc", "nutrient_conc", "population", "time", "surv_frac"}:
        raise ValueError(f"Colonnes longitudinales inattendues: {list(evol.columns)}")
    if set(phen.columns) != {"AB_conc", "nutrient_conc", "MIC", "pers_frac"}:
        raise ValueError(f"Colonnes phenotypiques inattendues: {list(phen.columns)}")

    evol["lineage_id"] = [f"W_{condition_key(a, n)}_P{int(p):02d}" for a, n, p in zip(evol.AB_conc, evol.nutrient_conc, evol.population)]
    cycles = pd.DataFrame({
        "lineage_id": evol["lineage_id"], "cycle": evol["time"], "antibiotic": "amikacin",
        "dose": evol["AB_conc"], "duration": 5.0, "recovery_duration": 19.0,
    }).drop_duplicates(["lineage_id", "cycle"])

    longitudinal = pd.DataFrame({
        "lineage_id": evol["lineage_id"], "cycle": evol["time"], "mic": pd.NA,
        "lag_time": pd.NA, "growth_rate": pd.NA, "survival": evol["surv_frac"],
        "persister_fraction": pd.NA, "fitness": pd.NA,
    })
    # Le depot ne fournit pas l'identifiant population pour les phenotypes finaux.
    # Ils restent donc des replicats independants et ne sont jamais joints aux trajectoires.
    phen = phen.copy()
    phen["replicate"] = phen.groupby(["AB_conc", "nutrient_conc"]).cumcount() + 1
    endpoint = pd.DataFrame({
        "lineage_id": [f"W_ENDPOINT_{condition_key(a, n)}_R{int(r):02d}" for a, n, r in zip(phen.AB_conc, phen.nutrient_conc, phen.replicate)],
        "cycle": pd.NA, "mic": phen["MIC"], "lag_time": pd.NA, "growth_rate": pd.NA,
        "survival": pd.NA, "persister_fraction": phen["pers_frac"], "fitness": pd.NA,
    })
    measurements = pd.concat([longitudinal, endpoint], ignore_index=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cycle_path = args.output_dir / "antibiotic_cycles.csv"
    measurement_path = args.output_dir / "antibiotic_measurements.csv"
    cycles.to_csv(cycle_path, index=False)
    measurements.to_csv(measurement_path, index=False)
    provenance = {
        "source": "Windels et al., Antibiotic dose and nutrient availability differentially drive the evolution of antibiotic resistance and persistence",
        "repository": "Zenodo 7550302", "dataset_doi": "10.5281/zenodo.7550302",
        "article": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11102087/",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "raw_files": {str(p.resolve()): sha256(p) for p in [args.evolution_csv, args.phenotypes_csv]},
        "outputs": {str(p.resolve()): {"sha256": sha256(p), "rows": int(sum(1 for _ in p.open(encoding='utf-8')) - 1)} for p in [cycle_path, measurement_path]},
        "experimental_context": {"organism": "Escherichia coli", "antibiotic": "amikacin", "treatment_hours": 5, "recovery_hours": 19, "reported_cycles": "11-16", "parallel_populations_per_condition": 24},
        "rules": ["aucune imputation, interpolation, simulation ou augmentation", "survie longitudinale conservee telle que publiee", "phenotypes finaux non joints aux trajectoires faute d'identifiant population dans le depot", "cellules non mesurees conservees vides"],
    }
    args.provenance_json.parent.mkdir(parents=True, exist_ok=True)
    args.provenance_json.write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"cycles": len(cycles), "measurements": len(measurements)}))


if __name__ == "__main__":
    main()
