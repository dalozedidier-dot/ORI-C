#!/usr/bin/env python3
"""Rejoue les deux filtres H|X riche et m vers R sur des artefacts déjà ouverts."""
from __future__ import annotations

import json
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
    return {
        "schema": "oric.hmr-two-filter-solar-audit.v1",
        "id": "HMR-SOLAR-OPEN-ARTIFACTS-01",
        "status": "executed_on_already_open_versioned_artifacts",
        "section_XIV_credit": False,
        "new_dataset_opened": False,
        "filters": {
            "H_given_rich_X": {
                "question": "Does ordered history survive the equal-complexity rich-X control?",
                "candidate": "M2",
                "rich_X_matched_control": "M1P",
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
                "passes": False,
                "verdict": "ordered history does not survive the equal-complexity rich-X control",
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
                "passes_model_level": bool(intervention["direct_INV_A_support"]),
                "strict_empirical_P_acc": False,
                "verdict": "m changes R inside the already-open reduced model, without strict empirical P_acc qualification",
                "source": M_SOURCE.relative_to(ROOT).as_posix(),
            },
        },
        "combined_verdict": "solar invariance is split: H fails after rich-X matching, while m changes R only at retrospective model level",
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
