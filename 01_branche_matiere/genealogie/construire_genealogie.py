from __future__ import annotations
import argparse, csv, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CERTITUDES = {"établi", "fortement inféré", "plausible", "hypothétique", "non documenté"}


def lire(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def produits_et_ordre(rows):
    produits, ordre = {}, {}
    for i, r in enumerate(rows):
        ordre[r["id"]] = i
        for p in r["produit"].split("|"):
            p = p.strip()
            if p:
                produits.setdefault(p, r["id"])
    return produits, ordre

CSV_PATH = ROOT / "genealogie_matiere.csv"
REPORT = ROOT / "cloture_genealogie.json"
EXTERNES = {"quarks", "gluons", "électrons", "electrons", "photons", "neutrinos",
            "gravité", "rayonnement cosmique", "flux ultraviolet", "chocs"}


def valider(rows):
    produits, ordre = produits_et_ordre(rows)
    anomalies = []
    required = ["id", "parents_materiels", "produit", "mecanisme", "degre_de_certitude",
                "preuve_du_mecanisme", "preuve_en_milieu_naturel",
                "preuve_de_la_transition_historique", "certitude_du_role_causal"]
    for r in rows:
        for field in required:
            if not (r.get(field) or "").strip():
                anomalies.append(f"{r.get('id','?')} : champ {field} vide")
        for parent in [x.strip() for x in r["parents_materiels"].split("|") if x.strip()]:
            if parent in EXTERNES:
                continue
            if parent not in produits:
                anomalies.append(f"{r['id']} : parent sans producteur ni déclaration externe : {parent}")
            elif ordre[produits[parent]] >= ordre[r["id"]]:
                anomalies.append(f"{r['id']} : parent produit trop tard : {parent}")
        for field in ["degre_de_certitude", "preuve_du_mecanisme", "preuve_en_milieu_naturel",
                      "preuve_de_la_transition_historique", "certitude_du_role_causal"]:
            if r.get(field) not in CERTITUDES:
                anomalies.append(f"{r['id']} : statut invalide dans {field}: {r.get(field)}")
        nxt = (r.get("transition_suivante") or "").strip()
        if nxt.startswith("GM-") and nxt not in ordre:
            anomalies.append(f"{r['id']} : transition suivante inexistante : {nxt}")
    edges = sum(1 for r in rows for p in r["parents_materiels"].split("|")
                if p.strip() and p.strip() not in EXTERNES)
    report = {
        "transitions": len(rows), "produits_distincts": len(produits),
        "relations_parent_produit": edges,
        "cloture_genealogique": not anomalies, "anomalies": anomalies,
        "certitudes_synthetiques": dict(Counter(r["degre_de_certitude"] for r in rows)),
        "possibilites_fermees_declarees": sum(1 for r in rows if r["possibilites_fermees"].strip().lower() not in ("", "aucune")),
    }
    return report


def main():
    argparse.ArgumentParser(description="Vérifie la généalogie détaillée de la matière").parse_args()
    report = valider(lire(CSV_PATH))
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["cloture_genealogique"] else 1

if __name__ == "__main__":
    sys.exit(main())
