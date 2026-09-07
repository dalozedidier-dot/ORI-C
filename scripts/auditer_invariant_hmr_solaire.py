#!/usr/bin/env python3
"""Synthèse de deux résultats distincts, sans nouvelle analyse des observations."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
H_SOURCE = ROOT / (
    "02_branche_systeme_solaire/couche_memoire_historique/"
    "results_stress/mpt/e_hardened_verdict.json"
)
M_SOURCE = ROOT / (
    "02_branche_systeme_solaire/couche_memoire_historique/"
    "do_m_trace/resultats/RESULTAT_DO_M.json"
)
OUT = ROOT / "02_branche_systeme_solaire/couche_memoire_historique/resultats/AUDIT_INVARIANT_HMR_SOLAIRE.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def criterion(block: dict, name: str) -> dict:
    return next(row for row in block["detail"] if row["criterion"] == name)


def build() -> dict:
    history = load(H_SOURCE)
    intervention = load(M_SOURCE)
    reference = history["reference_vs_M1P"]
    wide = history["wide_vs_M1P"]
    reference_gain = criterion(reference, "forecast_rmse_gain_at_least_5pct")
    wide_gain = criterion(wide, "forecast_rmse_gain_at_least_5pct")
    reference_block = criterion(reference, "blockwise_wilcoxon_M2_better")
    wide_block = criterion(wide, "blockwise_wilcoxon_M2_better")
    pacc = intervention["P_acc"]
    comparison_pass = all(bool(row['passed']) for block in (reference, wide) for row in block['detail'])
    matching = intervention['matching']
    model_pass = bool(
        matching['X_exact_by_construction'] and matching['same_architecture']
        and matching['same_future_forcing']
        and all(value == 0 for value in matching['max_abs_X_difference_control_vs_do_m'].values())
        and intervention['direct_INV_A_m_intervention']
        and pacc['abs_Delta_bootstrap_q025'] > pacc['epsilon_acc']
        and pacc['sham_max_abs_Delta'] == 0
    )
    return {
        "schema": "oric.hmr-two-filter-solar-audit.v1",
        "id": "HMR-SOLAR-OPEN-ARTIFACTS-01",
        "status": "synthesis_of_two_distinct_existing_results_no_XIV_credit",
        "same_dataset_two_filter_test_executed": False,
        "source_sha256": {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in (H_SOURCE, M_SOURCE)},
        "section_XIV_credit": False,
        "new_dataset_opened": False,
        "filters": {
            "H_given_rich_X": {
                "question": "Does M2 beat the equal-complexity forcing-memory model M1P?",
                "candidate": "M2",
                "matched_control": "M1P",
                "rich_X_equivalence_established": False,
                "scope": "M1P contains a slow state driven by past forcing. This is not a direct H given current rich X test.",
                "delivered_bounds": {
                    "relative_RMSE_gain": reference_gain["value"],
                    "SESOI": reference_gain["threshold"],
                    "gain_gate_pass": reference_gain["passed"],
                    "blockwise_p": reference_block["value"],
                    "blockwise_gate_pass": reference_block["passed"],
                    "criteria_passed": reference["passed"],
                    "criteria_total_reported": reference["total"],
                },
                "wide_bounds": {
                    "relative_RMSE_gain": wide_gain["value"],
                    "SESOI": wide_gain["threshold"],
                    "gain_gate_pass": wide_gain["passed"],
                    "blockwise_p": wide_block["value"],
                    "blockwise_gate_pass": wide_block["passed"],
                    "criteria_passed": wide["passed"],
                    "criteria_total_reported": wide["total"],
                },
                "passes": None,
                "equal_complexity_comparison_passes": comparison_pass,
                "verdict": "equal_complexity_gates_pass" if comparison_pass else "equal_complexity_gates_fail",
                "source": H_SOURCE.relative_to(ROOT).as_posix(),
            },
            "m_to_R": {
                "question": "Does a direct intervention on physical trace m change future response R at matched X?",
                "X_exact_by_construction": intervention["matching"]["X_exact_by_construction"],
                "same_future_forcing": intervention["matching"]["same_future_forcing"],
                "direct_intervention": intervention["direct_INV_A_m_intervention"],
                "R": "P_acc over the frozen future challenge cells",
                "control_median": pacc["control_median"],
                "do_m_median": pacc["do_m_median"],
                "signed_change": pacc["Delta_signed_median"],
                "absolute_change_95pct_interval": [
                    pacc["abs_Delta_bootstrap_q025"],
                    pacc["abs_Delta_bootstrap_q975"],
                ],
                "sham_max_absolute_change": pacc["sham_max_abs_Delta"],
                "passes_model_level": model_pass,
                "strict_empirical_P_acc": False,
                "verdict": "model_intervention_gates_pass" if model_pass else "model_intervention_gates_fail",
                "source": M_SOURCE.relative_to(ROOT).as_posix(),
            },
        },
        "combined_verdict": "No joint two-filter inference: distinct datasets and no established rich-X equivalence.",
        "rule": "No threshold is lowered and no result is promoted to section XIV credit.",
    }


def main() -> int:
    payload = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{payload['id']}: {payload['combined_verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
