from __future__ import annotations

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("admission", HERE / "admettre_jeu.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def fiches() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted((HERE / "fiches").glob("*.json"))]


def test_six_jeux_existants_sont_enfin_inspectes() -> None:
    assert len(fiches()) == 6


def test_aucun_jeu_incomplet_n_est_force_dans_la_campagne() -> None:
    rapports = [MOD.examiner(fiche) for fiche in fiches()]
    assert not any(rapport["admis"] for rapport in rapports)
    assert any("trace physique persistante" in condition["condition"] and not condition["satisfaite"]
               for rapport in rapports for condition in rapport["conditions"])
    assert any("réponse ultérieure" in condition["condition"] and not condition["satisfaite"]
               for rapport in rapports for condition in rapport["conditions"])
