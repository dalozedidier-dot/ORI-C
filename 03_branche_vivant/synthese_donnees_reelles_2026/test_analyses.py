import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_primary_source_hashes_are_exact():
    expected = {
        "donnees_externes/lamrabet_2019/mbio.00189-19-sd001.xls": "3af477cbe29f708e02706a496a3db4195a4db5aa6389b3c9c510cca9affb53dc",
        "donnees_externes/petrungaro_2026/41467_2026_76025_MOESM3_ESM.csv": "ba6baa558844a811ebda209689f36e5eb91e5d07919dd6e9466daf56e6815f9c",
        "donnees_externes/petrungaro_2026/41467_2026_76025_MOESM4_ESM.csv": "5d83bee91b48d7113f8bb04382c8d8bbb0379a9b9d26a8e7100607e0e1753951",
        "donnees_externes/petrungaro_2026/41467_2026_76025_MOESM7_ESM.zip": "98526cbd6b391f56ecb5bd317be45586879a618e37fa3a61f5e7f242aab208e8",
        "donnees_externes/petrungaro_2026/PRJEB103832.xml": "3d04a8d4f33b8beea045c8c4e0f35b58ee035ecb4166097e96a28976622e5dd7",
        "donnees_externes/nader_vesicules_2026/S. Nader AVT raw data.xlsx": "4df3a6ba57a1ccc0e68cabdaf7c0af7469100b1fdcf0e2abc4af168b4e4f5aab",
        "donnees_externes/card_2019_complet/Card_et_al_2019_Data_and_R_Notebook.zip": "064cc89c6907cb195e9e99e2b73ce99075afe8dff47e02d1dcfcd87d3a751165",
    }
    for path, expected_hash in expected.items():
        assert digest(path) == expected_hash


def test_all_new_analyses_use_real_data_only():
    paths = [
        "03_branche_vivant/benchmark_lamrabet_2019/resultats/RESULTAT_LAMRABET_2019.json",
        "03_branche_vivant/benchmark_petrungaro_2026/resultats/RESULTAT_PETRUNGARO_2026.json",
        "03_branche_vivant/lignees_vesicules/nader_2026/resultats/RESULTAT_NADER_2026.json",
        "03_branche_vivant/benchmark_externe_card2019/resultats/AUDIT_ARCHIVE_COMPLETE_CARD_2019.json",
    ]
    for path in paths:
        result = load(path)
        qualification = result.get("qualification", {})
        assert qualification.get("real_data") is True
        assert qualification.get("synthetic_or_simulated_scientific_data") is False


def test_lamrabet_independent_unit_and_counts():
    result = load("03_branche_vivant/benchmark_lamrabet_2019/resultats/RESULTAT_LAMRABET_2019.json")
    assert result["n_independent_units"] == 12
    assert result["n_antibiotics"] == 15
    assert result["n_raw_MIC_measurements"] == 1125


def test_petrungaro_reports_antibiotics_separately():
    result = load("03_branche_vivant/benchmark_petrungaro_2026/resultats/RESULTAT_PETRUNGARO_2026.json")
    assert set(result["phenotype_by_antibiotic"]) == {"MEC", "NIT", "TMP"}
    assert result["phenotype_by_antibiotic"]["NIT"]["bootstrap_gain_q025_percent"] > 0
    assert result["phenotype_by_antibiotic"]["MEC"]["bootstrap_gain_q025_percent"] < 0
    assert result["phenotype_by_antibiotic"]["TMP"]["bootstrap_gain_q025_percent"] < 0


def test_comparative_table_has_required_fields():
    table = pd.read_csv(ROOT / "03_branche_vivant/synthese_donnees_reelles_2026/COMPARAISON_ETUDES_REELLES.csv")
    required = {"independent_unit", "X", "H_or_m", "Theta", "future_R", "n_independent_units", "effect", "uncertainty_interval", "permutation_p", "verdict"}
    assert required <= set(table.columns)
    assert {"D'Onofrio", "Card 2019", "Wong & Seguin 2015", "Lamrabet 2019", "Petrungaro 2026", "Nader AVT"} <= set(table.study)
