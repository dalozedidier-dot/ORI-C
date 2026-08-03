"""Test prospectif réparé — WP-C2 du plan directeur.

Le test prospectif d'origine n'a pas pu conclure. Deux défauts, tous deux dans
le protocole : une frontière de bassin indéterminable au sens de la clause qui
la définissait, et un témoin de complexité égale **mal apparié** — une seule
entrée externe normalisée contre la productivité, employée pour les deux états
lents, alors que dans M2 l'un suit la productivité (≈ 0,91) et l'autre la
fraction de glace (≈ 0,02). Facteur d'écart ≈ 40.

Ce script exécute les dix items du WP-C2.

    1. Cartographie complète des régions mono et multistables
    2. Choix de points réellement discriminants, sur la carte
    3. **Deux entrées externes distinctes**, une par état lent
    4. Publication des plages d'exploitation des quatre variables motrices
    5. Normalisation calibrée au forçage de référence (23,5°, e = 0,05),
       donc indépendante du point testé
    6. Simulation de puissance avant préenregistrement
    7. Seuils de matérialité fixés
    8. Durée d'observation au-delà de toutes les constantes de temps
    9. Protocole gelé — empreinte écrite avant toute lecture de résultat
   10. Exécution unique

Le noyau est réécrit ici en numpy plutôt que modifié dans `e_prospectif.py` :
le code vérifié du dossier n'est pas touché.

Exécution : `python m_prospectif_wp_c2.py`
"""

from __future__ import annotations

import hashlib
import json
import math
import time

import numpy as np

from core import OUTPUT_ROOT, exo_parameter_vector, polar_summer_insolation

OUT = OUTPUT_ROOT / "prospectif_c2"

# Forçage de référence : sert à calibrer les entrées du témoin. Il ne fait
# partie d'aucun point testé, ce qui satisfait l'item 5.
REFERENCE = (23.5, 0.05)

# Item 8 : la plus grande constante de temps du modèle est tau_regolithe = 60.
# On observe 400 Ma, soit plus de six mille fois cette valeur.
DUREE_MA = 400.0
PAS_MA = 0.02

# Item 7 : seuils de matérialité, fixés avant exécution.
SEUIL_MULTISTABILITE = 0.05     # étendue de la fraction de glace finale
SEUIL_APPARIEMENT = 2.0         # rapport max toléré entre plages


def _pas(etat, polar, flux, mode, p, entree_regolithe, entree_memoire):
    """Un sous-pas du modèle. `mode` : 0 classic, 2 M2, 4 M2P corrigé."""
    temperature, ice, co2, regolith, memoire = etat
    co2_borne = max(co2, 50.0)
    productivite = (
        math.exp(-((temperature - 0.5) / 4.0) ** 2)
        * (co2_borne / 280.0) ** 0.2 * (1.0 - 0.45 * ice)
    )
    if mode in (2, 4):
        bedrock = 1.0 - regolith
        effet = memoire - 0.5
    else:
        bedrock = 0.0
        effet = 0.0

    cible_t = p[3] * flux + p[4] * math.log(co2_borne / 280.0) - p[5] * ice
    argument = -(temperature + p[6] * polar - p[7] - p[9] * bedrock) / p[8]
    argument = max(-30.0, min(30.0, argument))
    cible_glace = 1.0 / (1.0 + math.exp(-argument))
    cible_co2 = 280.0 * math.exp(-p[15] * temperature - p[13] * effet)
    tau_glace = p[1] * (1.0 + p[10] * bedrock)

    temperature += PAS_MA * (cible_t - temperature) / p[0]
    ice = min(1.0, max(0.0, ice + PAS_MA * (cible_glace - ice) / tau_glace))
    co2 = min(1200.0, max(80.0, co2 + PAS_MA * (cible_co2 - co2) / p[2]))

    if mode == 2:
        # Les états lents suivent la RÉPONSE.
        regolith += PAS_MA * (-p[11] * ice * regolith + (1.0 - regolith) / p[12])
        memoire += PAS_MA * (productivite - memoire) / p[14]
    elif mode == 4:
        # Témoin corrigé : DEUX entrées externes distinctes, chacune calibrée
        # sur la valeur de la variable motrice qu'elle remplace, au forçage de
        # référence. C'est le correctif du §3 du rapport prospectif.
        regolith += PAS_MA * (-p[11] * entree_regolithe * regolith
                              + (1.0 - regolith) / p[12])
        memoire += PAS_MA * (entree_memoire - memoire) / p[14]

    if mode in (2, 4):
        regolith = min(1.0, max(0.0, regolith))
        memoire = min(2.0, max(0.0, memoire))
    return (temperature, ice, co2, regolith, memoire), productivite


def simuler(obliquite, excentricite, mode, etat_initial, p,
            calibration=None, duree=DUREE_MA):
    """Renvoie (état final, plages d'exploitation des variables motrices)."""
    polar = float(polar_summer_insolation(obliquite, excentricite))
    reference = float(polar_summer_insolation(*REFERENCE))
    anomalie = (polar - reference) / 100.0
    flux = (1.0 / math.sqrt(1.0 - excentricite ** 2)
            - 1.0 / math.sqrt(1.0 - 0.05 ** 2)) / 0.05

    entree_r, entree_m = (calibration if calibration else (0.0, 0.0))
    etat = tuple(etat_initial)
    n = int(duree / PAS_MA)
    suivi = {"ice": [], "productivite": [], "regolith": [], "memoire": []}
    for i in range(n):
        etat, productivite = _pas(etat, anomalie, flux, mode, p,
                                  entree_r, entree_m)
        if i % 200 == 0:
            suivi["ice"].append(etat[1])
            suivi["productivite"].append(productivite)
            suivi["regolith"].append(etat[3])
            suivi["memoire"].append(etat[4])
    plages = {k: (float(np.median(v)), float(np.ptp(v)))
              for k, v in suivi.items()}
    return etat, plages


def calibrer(p, initiaux):
    """Item 5 : valeurs des variables motrices au forçage de référence.

    Calibrée sur **l'ensemble** des états initiaux, pas sur un seul : si le
    point de référence est lui-même multistable, une calibration sur un état
    unique dépendrait du bassin atteint, ce que l'item 5 interdit. La
    dispersion est renvoyée pour que ce cas soit visible.
    """
    ices, productivites = [], []
    for etat in initiaux:
        _, plages = simuler(REFERENCE[0], REFERENCE[1], 2, etat, p)
        ices.append(plages["ice"][0])
        productivites.append(plages["productivite"][0])
    return {
        "entree_du_regolithe": float(np.median(ices)),
        "entree_de_la_memoire": float(np.median(productivites)),
        "dispersion_ice": float(np.ptp(ices)),
        "dispersion_productivite": float(np.ptp(productivites)),
        "reference_monostable": bool(np.ptp(ices) <= SEUIL_MULTISTABILITE),
    }


def etats_initiaux(nombre, graine):
    rng = np.random.default_rng(graine)
    return [
        (float(rng.uniform(-8.0, 8.0)), float(rng.uniform(0.0, 1.0)),
         float(rng.uniform(150.0, 600.0)), float(rng.uniform(0.0, 1.0)),
         float(rng.uniform(0.0, 1.5)))
        for _ in range(nombre)
    ]


def cartographier(p, initiaux, obliquites, excentricites) -> dict:
    """Item 1 : régions mono et multistables, mode par mode."""
    carte = {}
    for mode, nom in ((0, "classic"), (2, "M2")):
        grille = []
        for obliquite in obliquites:
            for excentricite in excentricites:
                finaux = [
                    simuler(obliquite, excentricite, mode, etat, p,
                            duree=120.0)[0][1]
                    for etat in initiaux
                ]
                etendue = float(np.ptp(finaux))
                grille.append({
                    "obliquite": float(obliquite),
                    "excentricite": float(excentricite),
                    "etendue_glace_finale": etendue,
                    "multistable": bool(etendue > SEUIL_MULTISTABILITE),
                })
        carte[nom] = {
            "points": grille,
            "points_multistables": sum(1 for g in grille if g["multistable"]),
            "sur": len(grille),
        }
    return carte


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    p = exo_parameter_vector()
    initiaux = etats_initiaux(24, 20260801)

    # --- Items 1 et 2 : cartographie, puis choix des points discriminants ---
    print("[C2] cartographie ...", flush=True)
    depart = time.perf_counter()
    obliquites = [12.0, 18.0, 23.5, 30.0, 40.0]
    excentricites = [0.0, 0.10, 0.20, 0.30]
    carte = cartographier(p, initiaux[:8], obliquites, excentricites)
    print(f"[C2] cartographie en {time.perf_counter() - depart:.0f} s",
          flush=True)

    multistables = [g for g in carte["M2"]["points"] if g["multistable"]]
    discriminants = sorted(multistables,
                           key=lambda g: -g["etendue_glace_finale"])[:3]
    if not discriminants:
        discriminants = sorted(carte["M2"]["points"],
                               key=lambda g: -g["etendue_glace_finale"])[:3]

    # --- Items 3, 4, 5 : témoin corrigé et plages publiées ---
    calibration_mesuree = calibrer(p, initiaux)
    entree_r = calibration_mesuree["entree_du_regolithe"]
    entree_m = calibration_mesuree["entree_de_la_memoire"]
    print(f"[C2] calibration : regolithe←{entree_r:.4f} "
          f"(dispersion {calibration_mesuree['dispersion_ice']:.4f}), "
          f"memoire←{entree_m:.4f} ; référence monostable : "
          f"{calibration_mesuree['reference_monostable']}", flush=True)

    # --- Item 6 : puissance, avant de figer le protocole ---
    # Combien d'états initiaux faut-il pour distinguer une étendue de 0,05 ?
    tirages = [4, 8, 16, 24]
    puissance = {}
    point = discriminants[0]
    for nombre in tirages:
        finaux = [
            simuler(point["obliquite"], point["excentricite"], 2, etat, p,
                    duree=120.0)[0][1]
            for etat in initiaux[:nombre]
        ]
        puissance[str(nombre)] = float(np.ptp(finaux))

    protocole = {
        "hypothese": (
            "Avec un témoin correctement apparié, M2 conserve une "
            "multistabilité que M2P n'a pas, aux points discriminants."
        ),
        "points_discriminants": discriminants,
        "calibration_des_entrees": {
            "forcage_de_reference": {"obliquite": REFERENCE[0],
                                     "excentricite": REFERENCE[1]},
            "entree_du_regolithe": entree_r,
            "entree_de_la_memoire": entree_m,
            "mesure": calibration_mesuree,
        },
        "seuil_de_multistabilite": SEUIL_MULTISTABILITE,
        "seuil_d_appariement": SEUIL_APPARIEMENT,
        "duree_Ma": DUREE_MA,
        "etats_initiaux": len(initiaux),
        "puissance_par_nombre_d_etats": puissance,
    }
    empreinte = hashlib.sha256(
        json.dumps(protocole, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()
    protocole["empreinte_sha256"] = empreinte
    (OUT / "PROTOCOLE_C2.json").write_text(
        json.dumps(protocole, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[C2] protocole gelé, empreinte {empreinte[:16]}...", flush=True)

    # --- Item 10 : exécution unique ---
    print("[C2] exécution ...", flush=True)
    resultats = {}
    for point in discriminants:
        clef = f"obl{point['obliquite']:.1f}_e{point['excentricite']:.2f}"
        resultats[clef] = {}
        for mode, nom in ((0, "classic"), (2, "M2"), (4, "M2P_corrige")):
            calibration = (entree_r, entree_m) if mode == 4 else None
            finaux, plages = [], []
            for etat in initiaux:
                final, plage = simuler(point["obliquite"],
                                       point["excentricite"], mode, etat, p,
                                       calibration=calibration)
                finaux.append(final[1])
                plages.append(plage)
            resultats[clef][nom] = {
                "etendue_glace_finale": float(np.ptp(finaux)),
                "mediane_glace_finale": float(np.median(finaux)),
                "multistable": bool(np.ptp(finaux) > SEUIL_MULTISTABILITE),
                "plages_d_exploitation": {
                    variable: {
                        "mediane": float(np.median([pl[variable][0]
                                                    for pl in plages])),
                        "etendue": float(np.median([pl[variable][1]
                                                    for pl in plages])),
                    }
                    for variable in ("ice", "productivite", "regolith",
                                     "memoire")
                },
            }
        print(f"[C2] point {clef} fait", flush=True)

    # --- Item 4 : vérification chiffrée de l'appariement ---
    appariement = {}
    for clef, par_mode in resultats.items():
        m2 = par_mode["M2"]["plages_d_exploitation"]
        temoin = par_mode["M2P_corrige"]["plages_d_exploitation"]
        rapports = {}
        for canal, variable in (("regolithe", "regolith"),
                                ("memoire", "memoire")):
            a = abs(m2[variable]["mediane"])
            b = abs(temoin[variable]["mediane"])
            rapports[canal] = float(max(a, b) / max(min(a, b), 1e-9))
        appariement[clef] = {
            "rapports": rapports,
            "apparie": bool(all(r <= SEUIL_APPARIEMENT
                                for r in rapports.values())),
        }

    rapport = {
        "protocole": protocole,
        "cartographie": {
            nom: {"points_multistables": v["points_multistables"],
                  "sur": v["sur"]}
            for nom, v in carte.items()
        },
        "cartographie_detaillee": carte,
        "resultats": resultats,
        "verification_d_appariement": appariement,
        "lecture": (
            "Le témoin n'est recevable que si `apparie` vaut vrai. Sinon le "
            "résultat n'est pas interprétable, exactement comme dans la "
            "version d'origine."
        ),
    }
    (OUT / "prospectif_c2.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8")
    print("écrit :", OUT / "prospectif_c2.json")


if __name__ == "__main__":
    main()
