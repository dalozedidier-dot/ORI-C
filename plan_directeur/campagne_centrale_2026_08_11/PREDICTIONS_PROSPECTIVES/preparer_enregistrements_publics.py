#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "ENREGISTREMENTS_PUBLICS"


def main() -> int:
    OUT.mkdir(exist_ok=True)
    predictions = sorted(HERE.glob("PRED-*.json"))
    index = []
    for path in predictions:
        raw = path.read_bytes()
        pred = json.loads(raw)
        package = {
            "schema": "oric.public-blind-registration-package.v1",
            "prediction_id": pred["id"], "source_file": path.name,
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "frozen_on": pred["date_gel"], "hypothesis": pred["hypothese"],
            "seen_data": pred["donnees_vues"],
            "forbidden_or_hidden_data": pred["donnees_interdites"],
            "predicted_variable": pred["variable_predite"],
            "prediction": pred["valeur_ou_intervalle"],
            "competitor": pred["modele_concurrent"],
            "success": pred["critere_succes"], "failure": pred["critere_echec"],
            "registration_service": "OSF Registries", "public_url": None,
            "registered_at": None, "status": "package_ready_external_account_required",
            "blindness_rule": "aucune donnée interdite ne doit être ouverte entre publication et scellement de l'analyse"
        }
        output = OUT / f"{pred['id']}.registration.json"
        output.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        index.append({"id": pred["id"], "package": output.name, "status": package["status"]})
    (OUT / "INDEX.json").write_text(json.dumps({"registrations": index}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(index)} paquets prêts; 0 publication revendiquée")
    return 0 if index and len(index) == len(predictions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
