from __future__ import annotations

import pandas as pd

from scripts.build_max_validation_package import _top_documents


def test_top_documents_formats_mixed_acceptance_values(tmp_path):
    acceptance = pd.DataFrame(
        [
            {
                "test": "bound",
                "observed": "True",
                "operator": "==",
                "threshold": "True",
                "passed": True,
            },
            {
                "test": "energy",
                "observed": "1.3251353459634007e-11",
                "operator": "<=",
                "threshold": "1e-08",
                "passed": True,
            },
        ]
    )
    summary = {
        "acceptance_passed": 2,
        "acceptance_failed": 0,
        "long_baseline_completed_years": 20_000_000,
        "total_computation_seconds": 3600,
        "initial_eccentricity_abs_error": 2.2e-10,
        "all_job_hashes_valid": True,
    }

    _top_documents(tmp_path, "abc123", summary, acceptance)

    status = (tmp_path / "STATUT_SCIENTIFIQUE.md").read_text(encoding="utf-8")
    assert "| bound" in status
    assert "| True" in status
    assert "1.32514e-11" in status
    assert "1e-08" in status
