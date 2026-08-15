"""Construit la comparaison unique des etudes biologiques reelles."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    don = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json")
    card = load("03_branche_vivant/benchmark_externe_card2019/resultats/verdict_externe.json")
    wong = load("03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT_WONG_SEGUIN_2015.json")
    lam = load("03_branche_vivant/benchmark_lamrabet_2019/resultats/RESULTAT_LAMRABET_2019.json")
    pet = load("03_branche_vivant/benchmark_petrungaro_2026/resultats/RESULTAT_PETRUNGARO_2026.json")
    nad = load("03_branche_vivant/lignees_vesicules/nader_2026/resultats/RESULTAT_NADER_2026.json")
    rows = [
        {
            "study": "D'Onofrio", "stratum": "all", "independent_unit": "strain/lineage group", "X": "present limitation", "H_or_m": "ancestral limitation history", "Theta": "antibiotic assay", "future_R": "MIC", "n_independent_units": don["group_count"], "effect": don["history_gain_percent"], "effect_unit": "RMSE gain percent X vs X+H", "uncertainty_low": None, "uncertainty_high": None, "uncertainty_type": "not reported in legacy artifact", "permutation_p": don["permutation_p_history_better_than_shuffled"], "verdict": "positive_real_retrospective"
        },
        {
            "study": "Card 2019", "stratum": "Ara+5 tetracycline", "independent_unit": "held-out strain block", "X": "present parent MIC", "H_or_m": "temporal strain identity", "Theta": "tetracycline assay", "future_R": "daughter MIC", "n_independent_units": 4, "effect": card["history_gain_vs_state_percent"], "effect_unit": "RMSE gain percent X vs X+H", "uncertainty_low": card["group_bootstrap"]["difference_history_minus_state_rmse_ci95"][0], "uncertainty_high": card["group_bootstrap"]["difference_history_minus_state_rmse_ci95"][1], "uncertainty_type": "95% group-bootstrap CI for history-minus-state RMSE", "permutation_p": None, "verdict": "negative_history_model_worse"
        },
        {
            "study": "Wong & Seguin 2015", "stratum": "ciprofloxacin", "independent_unit": "evolved population", "X": "progenitor MIC and target gene", "H_or_m": "founding resistance mutation", "Theta": "ciprofloxacin evolution", "future_R": "endpoint MIC", "n_independent_units": wong["mapping"]["n_independent_units"], "effect": wong["results"]["history_gain_percent"], "effect_unit": "RMSE gain percent X vs X+m", "uncertainty_low": wong["results"]["bootstrap_gain_q025_percent"], "uncertainty_high": wong["results"]["bootstrap_gain_q975_percent"], "uncertainty_type": "95% population-bootstrap CI", "permutation_p": wong["results"]["permutation_p_one_sided"], "verdict": "negative_no_incremental_information"
        },
        {
            "study": "Lamrabet 2019", "stratum": "15 antibiotics", "independent_unit": "LTEE lineage", "X": "MIC profile at generation 2000", "H_or_m": "lineage realized history", "Theta": "antibiotic-specific MIC assay", "future_R": "MIC profile at generation 50000", "n_independent_units": lam["n_independent_units"], "effect": lam["global"]["spearman_profile_persistence"], "effect_unit": "Spearman persistence", "uncertainty_low": lam["global"]["bootstrap_q025"], "uncertainty_high": lam["global"]["bootstrap_q975"], "uncertainty_type": "95% lineage-bootstrap CI", "permutation_p": lam["global"]["permutation_p_two_sided"], "verdict": "divergence_real_persistence_not_significant_at_0.05"
        },
    ]
    for antibiotic, value in pet["phenotype_by_antibiotic"].items():
        robust = value["bootstrap_gain_q025_percent"] > 0 and value["background_permutation_p_one_sided"] <= 0.05
        rows.append({
            "study": "Petrungaro 2026", "stratum": antibiotic, "independent_unit": "evolved plate-well population", "X": "initial IC50", "H_or_m": "initial gene-deletion background", "Theta": antibiotic, "future_R": "endpoint IC50", "n_independent_units": value["n_populations"], "effect": value["relative_gain_percent"], "effect_unit": "RMSE gain percent X vs X+m", "uncertainty_low": value["bootstrap_gain_q025_percent"], "uncertainty_high": value["bootstrap_gain_q975_percent"], "uncertainty_type": "95% population-bootstrap CI", "permutation_p": value["background_permutation_p_one_sided"], "verdict": "positive_robust_real_retrospective" if robust else "not_robust_bootstrap_crosses_zero"
        })
    rows.append({
        "study": "Nader AVT", "stratum": "2:1 decanoic acid:decanol", "independent_unit": "independent batch unavailable; particles are nested", "X": "physical formulation", "H_or_m": "not manipulated", "Theta": "aerosol-to-landing transformation", "future_R": "chromatography and particle size", "n_independent_units": None, "effect": nad["observed_particle_sizes"]["median_nm"], "effect_unit": "observed median particle size nm", "uncertainty_low": nad["observed_particle_sizes"]["q025_nm"], "uncertainty_high": nad["observed_particle_sizes"]["q975_nm"], "uncertainty_type": "empirical 2.5%-97.5% particle-size interval", "permutation_p": None, "verdict": "physical_characterisation_not_history_test"
    })
    table = pd.DataFrame(rows)
    table.to_csv(HERE / "COMPARAISON_ETUDES_REELLES.csv", index=False, lineterminator="\n")
    summary = {
        "schema": "oric.real-biological-studies-comparison.v1",
        "row_count": len(table),
        "robust_positive_incremental_history_or_background": ["D'Onofrio", "Petrungaro 2026 / NIT"],
        "negative_or_non_robust": ["Card 2019", "Wong & Seguin 2015", "Lamrabet 2019 persistence at alpha=0.05", "Petrungaro 2026 / MEC", "Petrungaro 2026 / TMP"],
        "physical_characterisation_only": ["Nader AVT"],
        "cross_dataset_reproducibility": "Multiple real datasets show history/background dependence, but constructs and interventions differ; this is not yet a common confirmatory ORI-C test.",
        "synthetic_or_simulated_scientific_data": False,
    }
    (HERE / "SYNTHESE.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
