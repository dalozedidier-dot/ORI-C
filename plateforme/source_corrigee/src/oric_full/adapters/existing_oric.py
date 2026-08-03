from __future__ import annotations

from pathlib import Path
import json
import shutil
import pandas as pd


class ImportReport(dict):
    pass


def _copy_csv(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def import_existing_data(oric_root: Path, data_dir: Path) -> ImportReport:
    oric_root = Path(oric_root)
    data_dir = Path(data_dir)
    report: ImportReport = ImportReport(imported=[], skipped=[], errors=[])

    mappings = [
        (
            oric_root / "02_branche_systeme_solaire" / "couche_astronomique" / "code" / "ORI-C_Systeme_solaire_tests" / "data" / "horizons_j2000_de441.csv",
            data_dir / "ephemerides.csv",
        ),
        (
            oric_root / "03_branche_vivant" / "programme_prebiotique" / "schema_lignees" / "gabarit" / "lignees.csv",
            data_dir / "prebiotic_lineages_raw.csv",
        ),
    ]
    for source, destination in mappings:
        try:
            if source.exists():
                _copy_csv(source, destination)
                report["imported"].append(str(destination))
            else:
                report["skipped"].append(str(source))
        except Exception as exc:
            report["errors"].append({"source": str(source), "error": str(exc)})

    # Carte relationnelle : la source est séparée par des points-virgules et
    # nomme la relation `relation`; le schéma exécutable exige `relation_type`.
    relations = oric_root / "00_socle" / "carte_relationnelle" / "data" / "relations_oric_47_provisoires.csv"
    if relations.exists():
        try:
            frame = pd.read_csv(relations, sep=";")
            frame[["source", "target", "relation"]].rename(columns={"relation": "relation_type"}).to_csv(
                data_dir / "relations.csv", index=False
            )
            report["imported"].append(str(data_dir / "relations.csv"))
        except Exception as exc:
            report["errors"].append({"source": str(relations), "error": str(exc)})

    # Tables astronomiques déjà préparées à partir des solutions de référence.
    campaign_data = oric_root / "plan_directeur" / "campagne_plateforme" / "donnees"
    for name in ("orbital_initial_conditions.csv", "orbital_reference.csv"):
        source = campaign_data / name
        if source.exists():
            _copy_csv(source, data_dir / name)
            report["imported"].append(str(data_dir / name))
    reference = data_dir / "orbital_reference.csv"
    if reference.exists():
        try:
            frame = pd.read_csv(reference)
            wide = frame.pivot_table(index="time", columns="observable", values="value", aggfunc="mean").reset_index()
            expected = [column for column in ("time", "eccentricity", "obliquity", "precession") if column in wide]
            wide[expected].to_csv(data_dir / "orbital_timeseries.csv", index=False)
            report["imported"].append(str(data_dir / "orbital_timeseries.csv"))
        except Exception as exc:
            report["errors"].append({"source": str(reference), "error": str(exc)})

    # Base matière codée et sourcée dans la branche matière.
    matter = oric_root / "plateforme" / "donnees" / "matter_transitions.csv"
    if matter.exists():
        _copy_csv(matter, data_dir / "matter_transitions.csv")
        report["imported"].append(str(data_dir / "matter_transitions.csv"))

    # Adapter le paléoclimat déjà présent au schéma commun.
    mpt = oric_root / "02_branche_systeme_solaire" / "couche_memoire_historique" / "data" / "processed" / "mpt_lr04_la2004.csv"
    if mpt.exists():
        try:
            frame = pd.read_csv(mpt)
            cols = {c.casefold(): c for c in frame.columns}
            time_col = next((c for c in frame.columns if "time" in c.casefold() or "age" in c.casefold() or "kyr" in c.casefold()), frame.columns[0])
            target_col = next((c for c in frame.columns if "lr04" in c.casefold() or "d18" in c.casefold() or "target" in c.casefold()), frame.columns[1])
            forcing_candidates = [c for c in frame.columns if c not in {time_col, target_col}]
            forcing_1 = forcing_candidates[0] if forcing_candidates else target_col
            forcing_2 = forcing_candidates[1] if len(forcing_candidates) > 1 else forcing_1
            out = pd.DataFrame({
                "time_kyr": frame[time_col],
                "target": frame[target_col],
                "forcing_1": frame[forcing_1],
                "forcing_2": frame[forcing_2],
            })
            out.to_csv(data_dir / "paleoclimate_timeseries.csv", index=False)
            report["imported"].append(str(data_dir / "paleoclimate_timeseries.csv"))
        except Exception as exc:
            report["errors"].append({"source": str(mpt), "error": str(exc)})

    (data_dir / "import_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
