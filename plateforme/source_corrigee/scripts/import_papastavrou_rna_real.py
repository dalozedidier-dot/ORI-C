from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def load_frequency(path: Path, sheet: str, branch: str) -> pd.DataFrame:
    f = pd.read_excel(path, sheet_name=sheet)
    required = {"Name", "Cluster", "Round", "frequency", "rel. frequency"}
    if not required.issubset(f.columns): raise ValueError(f"Colonnes absentes dans {path.name}/{sheet}: {sorted(required-set(f.columns))}")
    return pd.DataFrame({"branch": branch, "round": f["Round"], "sequence_id": f["Name"], "cluster": f["Cluster"], "frequency": f["frequency"], "relative_frequency": f["rel. frequency"], "source_table": f"{path.name}:{sheet}"})

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("fig3", type=Path); p.add_argument("figs3", type=Path); p.add_argument("output_csv", type=Path); p.add_argument("provenance_json", type=Path); args = p.parse_args()
    out = pd.concat([load_frequency(args.fig3, "Fig 3B Frequency Data", "71-89"), load_frequency(args.figs3, "Fig S3B Frequency Data", "52-2")], ignore_index=True).dropna(subset=["round", "sequence_id", "frequency"])
    if out.duplicated(["branch", "round", "sequence_id"]).any(): raise ValueError("Grain branche-cycle-séquence dupliqué")
    args.output_csv.parent.mkdir(parents=True, exist_ok=True); out.to_csv(args.output_csv, index=False)
    prov = {"source": "Papastavrou, Horning & Joyce, RNA-Catalyzed Evolution of Catalytic RNA", "repository": "Zenodo 10714366", "dataset_doi": "10.5061/dryad.rxwdbrvgs", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "raw_files": {str(x.resolve()): sha256(x) for x in [args.fig3,args.figs3]}, "output": {"path": str(args.output_csv.resolve()), "sha256": sha256(args.output_csv), "rows": len(out)}, "rules": ["fréquences de figures publiées uniquement", "aucune imputation, simulation ou reconstruction généalogique", "deux branches conservées séparément"]}
    args.provenance_json.write_text(json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8"); print(json.dumps({"rows": len(out), "branches": int(out.branch.nunique()), "rounds": int(out['round'].nunique())}))

if __name__ == "__main__": main()
