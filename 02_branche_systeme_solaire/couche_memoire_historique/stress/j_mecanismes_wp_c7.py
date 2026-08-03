"""Recherche de mécanismes nouveaux — WP-C7 du plan directeur.

« Utiliser l'échec de M2 pour localiser les résidus structurés. »

T2 et T4 ont mis au jour une dissociation : M2 est le seul modèle à produire
le rapport 100/41 ka, au bon moment, et il est le pire en RMSE. Sa signature
est bonne, son amplitude ne l'est pas. Le WP-C7 demande d'exploiter cet échec
plutôt que de le réparer par ajustements.

    C7.1  Où le résidu est-il structuré ? Spectre du résidu par fenêtre.
    C7.2  Où M2 capte-t-il la signature en ratant l'amplitude ? Régression
          glissante de l'observé sur le prédit : la pente mesure l'amplitude,
          la corrélation mesure la signature. La dissociation se lit dans
          l'écart entre les deux.
    C7.3  Le correctif manquant est-il additif, multiplicatif ou
          conditionnel ? Trois formes emboîtées, comparées à budget égal.
    C7.4  La mémoire dépend-elle du régime climatique ? Paramètres réajustés
          avant et après la transition du Pléistocène moyen.
    C7.7  Une variable lente modifie-t-elle l'opérateur de réponse ? Test du
          terme conditionnel contre le terme constant.

Ce script ne propose aucun modèle nouveau. Il localise ce qu'un modèle nouveau
devrait expliquer.

Exécution : `python j_mecanismes_wp_c7.py`
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from core import (
    OUTPUT_ROOT,
    effective_sample_size,
    fit_best_of_seeds,
    rmse,
    simulate,
)
from g_tests_reels_2 import BUDGET, GRAINES, MODELES, charger, normaliser
from i_criteres_discriminants import puissance_par_bande

OUT = OUTPUT_ROOT / "tests_reels"
LARGEUR = 200          # ka, fenêtre glissante
PAS = 25               # ka


def regression(y, x):
    """Pente, ordonnée et corrélation d'une régression simple."""
    if len(y) < 3 or np.std(x) < 1e-12:
        return np.nan, np.nan, np.nan
    pente, ordonnee = np.polyfit(x, y, 1)
    correlation = float(np.corrcoef(y, x)[0, 1])
    return float(pente), float(ordonnee), correlation


def c7_1_et_2(observe, predits, age, prediction) -> dict:
    """Résidus structurés, et dissociation amplitude / signature."""
    o = observe[prediction]
    ages = age[prediction]
    lignes = []
    for debut in range(0, len(o) - LARGEUR, PAS):
        tranche = slice(debut, debut + LARGEUR)
        ligne = {"age_centre_ka": float(ages[tranche].mean())}
        for modele in MODELES:
            p = predits[modele][prediction][tranche]
            y = o[tranche]
            pente, _, correlation = regression(y, p)
            residu = y - p
            ligne[f"pente_{modele}"] = pente
            ligne[f"correlation_{modele}"] = correlation
            ligne[f"rmse_{modele}"] = rmse(y, p)
            ligne[f"variance_residu_{modele}"] = float(np.var(residu))
        lignes.append(ligne)
    frame = pd.DataFrame(lignes)
    frame.to_csv(OUT / "j_fenetres_wp_c7.csv", index=False)

    # Dissociation : corrélation élevée et pente éloignée de 1.
    dissociation = {}
    for modele in MODELES:
        correlations = frame[f"correlation_{modele}"].to_numpy()
        pentes = frame[f"pente_{modele}"].to_numpy()
        valides = np.isfinite(correlations) & np.isfinite(pentes)
        fort = valides & (correlations > 0.5)
        dissociation[modele] = {
            "fenetres": int(valides.sum()),
            "correlation_mediane": float(np.nanmedian(correlations[valides])),
            "pente_mediane": float(np.nanmedian(pentes[valides])),
            "fenetres_a_correlation_superieure_a_0_5": int(fort.sum()),
            "pente_mediane_sur_ces_fenetres": float(
                np.nanmedian(pentes[fort])) if fort.any() else None,
            "ecart_de_pente_a_1": float(
                abs(np.nanmedian(pentes[fort]) - 1.0)) if fort.any() else None,
        }

    # Spectre du résidu de M2 : ce qu'un mécanisme manquant devrait porter.
    residus = {}
    for modele in MODELES:
        residu = o - predits[modele][prediction]
        bandes = puissance_par_bande(residu)
        residus[modele] = {
            "part_41_ka": bandes["part_41_ka"],
            "part_100_ka": bandes["part_100_ka"],
            "n_eff": float(effective_sample_size(residu)),
            "ecart_type": float(residu.std()),
            "moyenne": float(residu.mean()),
        }
    return {
        "largeur_fenetre_ka": LARGEUR,
        "pas_ka": PAS,
        "dissociation_amplitude_signature": dissociation,
        "spectre_des_residus": residus,
        "lecture": (
            "Une corrélation élevée avec une pente éloignée de 1 est la "
            "signature d'un modèle qui trouve la forme et rate le gain. "
            "C'est ce que T2 et T4 laissaient soupçonner ; ici il est mesuré "
            "fenêtre par fenêtre."
        ),
    }


def c7_3_forme_du_correctif(observe, predits, prediction) -> dict:
    """Additif, multiplicatif ou conditionnel : trois formes emboîtées."""
    o = observe[prediction]
    resultat = {}
    for modele in MODELES:
        p = predits[modele][prediction]
        n = len(o)
        # 1. brut
        formes = {"brut": (rmse(o, p), 0)}
        # 2. additif : o ≈ p + a
        a = float(np.mean(o - p))
        formes["additif"] = (rmse(o, p + a), 1)
        # 3. affine : o ≈ b p + a  (échelle et décalage)
        b, a2 = np.polyfit(p, o, 1)
        formes["affine"] = (rmse(o, b * p + a2), 2)
        # 4. multiplicatif conditionnel : le gain dépend d'un état lent.
        #    L'état lent est approché par la moyenne glissante de p.
        noyau = np.ones(150) / 150.0
        lent = np.convolve(p, noyau, mode="same")
        lent = (lent - lent.mean()) / (lent.std() + 1e-12)
        base = np.column_stack([p, p * lent, np.ones(n)])
        coefficients, *_ = np.linalg.lstsq(base, o, rcond=None)
        formes["conditionnel"] = (rmse(o, base @ coefficients), 3)

        # Comparaison à budget égal : BIC.
        scores = {}
        for nom, (valeur, k) in formes.items():
            variance = max(valeur ** 2, 1e-30)
            scores[nom] = {
                "rmse": float(valeur),
                "parametres_ajoutes": k,
                "bic": float(n * np.log(variance) + k * np.log(n)),
            }
        meilleur = min(scores, key=lambda nom: scores[nom]["bic"])
        resultat[modele] = {
            "formes": scores,
            "forme_retenue_par_bic": meilleur,
            "gain_rmse_de_la_forme_retenue": float(
                1.0 - scores[meilleur]["rmse"] / scores["brut"]["rmse"]
            ),
        }
    return {
        "par_modele": resultat,
        "lecture": (
            "Si la forme retenue est `affine`, il manque une échelle ; si "
            "elle est `conditionnel`, le gain dépend d'un état lent, ce qui "
            "est l'hypothèse du §13.4 : une variable lente modifie "
            "l'opérateur de réponse."
        ),
    }


def c7_4_dependance_au_regime(donnees) -> dict:
    """La mémoire dépend-elle du régime climatique ? Avant / après la MPT."""
    age = donnees["age"]
    regimes = {
        "avant_MPT_2600_1200": (age <= 2600) & (age >= 1200),
        "apres_MPT_1200_0": (age < 1200),
    }
    parametres = {}
    for nom, masque in regimes.items():
        observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                      masque)
        parametres[nom] = {}
        for modele in MODELES:
            meilleur, _ = fit_best_of_seeds(
                modele, forcage, observe, masque, GRAINES[:2],
                bounds_name="wide", **BUDGET,
            )
            parametres[nom][modele] = {
                "vecteur": [float(v) for v in meilleur.vector],
                "rmse_entrainement": float(meilleur.training_rmse),
            }
        print(f"     régime {nom} fait", flush=True)

    ecarts = {}
    for modele in MODELES:
        avant = np.asarray(parametres["avant_MPT_2600_1200"][modele]["vecteur"])
        apres = np.asarray(parametres["apres_MPT_1200_0"][modele]["vecteur"])
        amplitude = np.maximum(np.abs(avant), np.abs(apres))
        relative = np.abs(apres - avant) / np.where(amplitude > 0, amplitude, 1)
        ecarts[modele] = {
            "ecart_relatif_max": float(relative.max()),
            "ecart_relatif_median": float(np.median(relative)),
            "parametres_stables_entre_regimes": bool(relative.max() < 0.25),
        }
    return {
        "parametres_par_regime": parametres,
        "ecarts": ecarts,
        "lecture": (
            "Des paramètres qui changent fortement entre les deux régimes "
            "indiquent que l'opérateur de réponse n'est pas fixe — c'est "
            "l'affirmation du §13.4 du CODEBOOK, testée ici sur données "
            "réelles. Ce n'est pas un succès du modèle : c'est un constat "
            "que sa forme actuelle ne suffit pas."
        ),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    donnees = charger()
    age = donnees["age"]
    masque = age >= 1200
    prediction = ~masque
    observe, forcage = normaliser(donnees["observe"], donnees["forcage"],
                                  masque)

    print("[C7] ajustement de référence ...", flush=True)
    predits = {}
    for modele in MODELES:
        meilleur, _ = fit_best_of_seeds(
            modele, forcage, observe, masque, GRAINES,
            bounds_name="wide", **BUDGET,
        )
        predits[modele] = simulate(modele, forcage, observe[0], meilleur.vector)
        print(f"     {modele} fait", flush=True)

    rapport = {}
    print("[C7] C7.1 et C7.2 ...", flush=True)
    rapport["C7_1_2_residus_et_dissociation"] = c7_1_et_2(
        observe, predits, age, prediction)
    print("[C7] C7.3 forme du correctif ...", flush=True)
    rapport["C7_3_forme_du_correctif"] = c7_3_forme_du_correctif(
        observe, predits, prediction)
    print("[C7] C7.4 dépendance au régime ...", flush=True)
    rapport["C7_4_dependance_au_regime"] = c7_4_dependance_au_regime(donnees)

    (OUT / "j_mecanismes_wp_c7.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print("écrit :", OUT / "j_mecanismes_wp_c7.json")


if __name__ == "__main__":
    main()
