from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "resultats"
REQUIRED = ("H030", "H031", "H052", "H053")


def main() -> dict[str, object]:
    data = pd.read_csv(ROOT / "donnees/ancrages_cycle_interfaces.csv")
    cycle = data[data["edge_id"].isin(REQUIRED)].copy()
    documented = sorted(set(cycle["edge_id"]))
    missing_edges = sorted(set(REQUIRED) - set(documented))
    direct = sorted(cycle.loc[cycle["intervention_directe"].astype(bool), "edge_id"].unique())
    quantitative = sorted(cycle.loc[cycle["quantitatif"].astype(bool), "edge_id"].unique())
    by_system = {
        system: sorted(group["edge_id"].unique())
        for system, group in cycle.groupby("systeme")
    }
    closed_systems = sorted(
        system for system, edges in by_system.items() if set(REQUIRED).issubset(edges)
    )
    result = {
        "required_edges": list(REQUIRED),
        "documented_required_edges": documented,
        "missing_required_edges": missing_edges,
        "direct_intervention_edges": direct,
        "quantitative_edges": quantitative,
        "systems": by_system,
        "single_system_closed_trajectories": len(closed_systems),
        "closed_systems": closed_systems,
        "cycle_status": "empirically_closed" if closed_systems else "anchored_but_not_closed",
        "interpretation": (
            "Les quatre relations du cycle possèdent un ancrage séparé, mais aucune trajectoire "
            "unique ne relie encore quantitativement les quatre segments."
        ),
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "CYCLE_INTERFACES_RESULTAT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
