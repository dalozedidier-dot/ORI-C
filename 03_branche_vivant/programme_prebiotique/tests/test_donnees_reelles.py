from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parents[1]


def test_audit_ne_confond_pas_gabarit_et_donnee():
    result = subprocess.run(
        [sys.executable, str(HERE / "auditer_donnees_reelles.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = json.loads((HERE / "resultats/audit_donnees_reelles.json").read_text())
    assert verdict["status"] in {
        "aucune_donnee_reelle",
        "trajectoires_population_reelles_sans_lignees",
        "donnees_de_lignees_presentes_a_valider",
    }
    assert not any(
        item.get("file") == "lignees.csv" for item in verdict["accepted_lineages"]
    )


def test_trajectoire_reelle_reste_distincte_d_une_lignee():
    verdict = json.loads((HERE / "resultats/audit_donnees_reelles.json").read_text())
    assert verdict["real_population_trajectory_files"] == 1
    assert verdict["population_trajectory_available"] is True
    assert verdict["real_lineage_files"] == 0
    assert verdict["criterion_testable"] is False
    trajectory = verdict["accepted_population_trajectories"][0]
    assert trajectory["branches"] == ["52-2", "71-89"]
    assert trajectory["rounds"] == list(range(1, 9))
