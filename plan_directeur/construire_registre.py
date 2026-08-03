"""Construit `REGISTRE_HYPOTHESES.csv` à partir de l'état réel du dossier.

Le plan directeur demande ce registre en tête de ses priorités — Niveau 1
item 1, Bloc A item 1. Il l'exige avec les seize champs de son Étape 1, plus
la distinction exploratoire / confirmatoire de son Étape 0.4.

Le registre n'est **pas** initialisé vide. Il est amorcé avec les hypothèses
que le dossier a déjà instruites, chacune avec son statut réel, y compris les
réfutations et les non-concluants. Un registre qui ne contiendrait que des
hypothèses à venir cacherait précisément ce que le plan demande de garder
visible : les résultats négatifs.

    python construire_registre.py            # écrit le registre
    python construire_registre.py --verifier # échoue si le fichier a divergé
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
CIBLE = RACINE / "REGISTRE_HYPOTHESES.csv"
SEPARATEUR = ";"

COLONNES = [
    "identifiant", "formulation", "domaine", "type", "variables_observables",
    "prediction_oric", "modele_nul", "modele_concurrent",
    "temoin_complexite_egale", "intervention_ou_contraste",
    "metrique_principale", "seuil_de_reussite", "fenetre_temporelle",
    "conditions_arret", "donnees_apprentissage", "donnees_validation",
    "statut_final", "ou",
]

TYPES = {"confirmatoire", "exploratoire"}
STATUTS = {
    "Réfuté", "Non concluant", "Non évalué", "Non testé",
    "Validé dans le modèle réduit", "Établi", "Sans verdict",
}

# ---------------------------------------------------------------------------
# Amorce : ce que le dossier a réellement instruit.
# Chaque ligne est vérifiable dans les rapports cités en dernière colonne.

E = [
    # -- Socle -------------------------------------------------------------
    dict(
        identifiant="H-S-001",
        formulation="Réduire une perte peut diminuer la persistance globale ; "
                    "l'intervention sur la perte a un effet causal sur le "
                    "régime du chémostat.",
        domaine="socle", type="confirmatoire",
        variables_observables="S, P, seuil de lavage l_crit, temps de relaxation",
        prediction_oric="bifurcation transcritique en l_crit, ralentissement "
                        "critique en 1/|l-l_crit|",
        modele_nul="équilibre sans perte",
        modele_concurrent="modèle de contrôle optimal",
        temoin_complexite_egale="sans objet, test analytique et numérique",
        intervention_ou_contraste="intervention directe sur le taux de perte l",
        metrique_principale="11 contrôles analytiques et numériques",
        seuil_de_reussite="11/11",
        fenetre_temporelle="jusqu'à convergence, écarts 1e-2 à 1e-5 du seuil",
        conditions_arret="échec d'un contrôle asymptotique",
        donnees_apprentissage="aucune, modèle analytique",
        donnees_validation="régénération indépendante du script",
        statut_final="Validé dans le modèle réduit",
        ou="00_socle/test_interventionnel/resultats_exhaustifs/rapport_exhaustif.txt",
    ),
    dict(
        identifiant="H-S-002",
        formulation="Les six dimensions n, G, I, E, Pi, H se codent sans "
                    "chevauchement complet sur des systèmes des trois branches.",
        domaine="socle", type="exploratoire",
        variables_observables="codage des 40 transitions, 47 relations",
        prediction_oric="codage stable et séparable entre codeurs",
        modele_nul="chronologie descriptive simple",
        modele_concurrent="graphe causal standard",
        temoin_complexite_egale="graphe nul conservant le degré",
        intervention_ou_contraste="retrait du nom du domaine avant codage",
        metrique_principale="accord inter-codeurs",
        seuil_de_reussite="à préenregistrer, WP-S1.1",
        fenetre_temporelle="sans objet",
        conditions_arret="accord inter-codeurs non mesurable",
        donnees_apprentissage="carte relationnelle",
        donnees_validation="relations masquées",
        statut_final="Non testé",
        ou="plan_directeur/PLAN_DIRECTEUR_TESTS.md WP-S1.1",
    ),
    # -- Branche 1 ---------------------------------------------------------
    dict(
        identifiant="H-M-001",
        formulation="Les dimensions ORI-C améliorent la reconstruction des "
                    "transitions de la matière par rapport à une chronologie "
                    "descriptive.",
        domaine="branche 1 matière", type="confirmatoire",
        variables_observables="40 transitions, états antérieur et postérieur",
        prediction_oric="reconstruction de transitions masquées supérieure au "
                        "témoin",
        modele_nul="chronologie descriptive",
        modele_concurrent="graphe causal standard, réseau sans histoire",
        temoin_complexite_egale="modèle de même nombre de paramètres sans "
                                "variable d'histoire",
        intervention_ou_contraste="masquage de 20 % des transitions",
        metrique_principale="taux de reconstruction correcte, calibration",
        seuil_de_reussite="à préenregistrer, WP-M5",
        fenetre_temporelle="sans objet",
        conditions_arret="aucun gain contre le témoin apparié",
        donnees_apprentissage="80 % des transitions",
        donnees_validation="20 % masquées",
        statut_final="Non testé",
        ou="ETAT_DES_PREUVES.md, branche 1",
    ),
    # -- Couche astronomique ----------------------------------------------
    dict(
        identifiant="H-A-001",
        formulation="Le modèle réduit reproduit une trajectoire astronomique "
                    "indépendante, et modifier l'architecture change la "
                    "trajectoire terrestre.",
        domaine="branche 2 couche astronomique", type="confirmatoire",
        variables_observables="excentricité, obliquité, spectre orbital",
        prediction_oric="reproduction des solutions de référence, effet causal "
                        "de l'architecture",
        modele_nul="solution de référence La2004",
        modele_concurrent="intégrateurs alternatifs",
        temoin_complexite_egale="sans objet, comparaison à référence externe",
        intervention_ou_contraste="perturbation des masses et demi-grands axes",
        metrique_principale="15 critères préenregistrés",
        seuil_de_reussite="critères préenregistrés par observable",
        fenetre_temporelle="horizons croissants jusqu'à divergence chaotique",
        conditions_arret="non-reproductibilité entre intégrateurs",
        donnees_apprentissage="conditions initiales JPL",
        donnees_validation="solutions La2004 et La2010",
        statut_final="Établi",
        ou="02_branche_systeme_solaire/couche_astronomique/STATUT_SCIENTIFIQUE.md",
    ),
    # -- Couche mémoire historique ----------------------------------------
    dict(
        identifiant="H-C-001",
        formulation="Une mémoire de la réponse passée (M2) prédit LR04 hors "
                    "échantillon mieux qu'un modèle sans cette mémoire (M1).",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="d18O benthique LR04, insolation 65N",
        prediction_oric="RMSE hors échantillon inférieure à M1",
        modele_nul="M0, réponse instantanée",
        modele_concurrent="M1, 6 paramètres",
        temoin_complexite_egale="M1P, 8 paramètres, état lent piloté par "
                                "forçage externe",
        intervention_ou_contraste="ablation de la rétroaction de réponse passée",
        metrique_principale="RMSE hors échantillon",
        seuil_de_reussite="5 critères préenregistrés",
        fenetre_temporelle="calibration 2600-1200 ka, prédiction 1200-0 ka",
        conditions_arret="échec sur deux jeux confirmatoires indépendants",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="LR04 1200-0 ka",
        statut_final="Réfuté",
        ou="02_.../couche_memoire_historique/RAPPORT_CORRIGE.md, 1/5",
    ),
    dict(
        identifiant="H-C-002",
        formulation="Le gain de M2 subsiste contre un témoin de complexité "
                    "égale (M1P).",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="d18O benthique LR04, insolation 65N",
        prediction_oric="RMSE inférieure à M1P",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="substitution de la variable motrice de "
                                  "l'état lent",
        metrique_principale="gain relatif de RMSE",
        seuil_de_reussite="5 critères préenregistrés",
        fenetre_temporelle="calibration 2600-1200 ka, prédiction 1200-0 ka",
        conditions_arret="gain négatif",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="LR04 1200-0 ka",
        statut_final="Réfuté",
        ou="02_.../RAPPORT_CORRIGE.md, 0/5 ; gain -0,316 IC [-0,389 ; -0,251]",
    ),
    dict(
        identifiant="H-C-003",
        formulation="Le gain de M2 dépasse l'incertitude publiée de l'archive.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="RMSE, colonne d18O_error de LR04",
        prediction_oric="gain supérieur à l'erreur publiée",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="comparaison du gain au plancher de l'archive",
        metrique_principale="rapport gain sur incertitude",
        seuil_de_reussite="rapport > 1",
        fenetre_temporelle="prédiction 1200-0 ka",
        conditions_arret="rapport < 1",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="LR04 1200-0 ka",
        statut_final="Réfuté",
        ou="02_.../results_stress/tests_reels/RAPPORT_TESTS_REELS.md T1, rapport 0,377",
    ),
    dict(
        identifiant="H-C-004",
        formulation="M2 prédit la transition du Pléistocène moyen lorsqu'elle "
                    "est entièrement hors échantillon.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="d18O LR04 sur 5,32 Ma, rapport 100/41 ka",
        prediction_oric="RMSE inférieure au témoin apparié",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="calibration antérieure à la transition",
        metrique_principale="RMSE hors échantillon, bootstrap par blocs",
        seuil_de_reussite="gain positif, IC excluant zéro",
        fenetre_temporelle="calibration 5320-2600 ka, prédiction 2600-0 ka",
        conditions_arret="gain négatif avec IC excluant zéro",
        donnees_apprentissage="LR04 5320-2600 ka",
        donnees_validation="LR04 2600-0 ka",
        statut_final="Réfuté",
        ou="…/RAPPORT_TESTS_REELS.md T2, gain -1,442 IC [-1,789 ; -0,810]",
    ),
    dict(
        identifiant="H-C-005",
        formulation="M2 place la transition du Pléistocène moyen à la bonne "
                    "date, mesurée par le franchissement du rapport 100/41.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="rapport de puissance 100/41 en fenêtre glissante",
        prediction_oric="date de franchissement proche de l'observation",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="comparaison de chronologie spectrale",
        metrique_principale="date de premier franchissement du rapport 1",
        seuil_de_reussite="écart à la date observée",
        fenetre_temporelle="fenêtre glissante 800 ka sur 5,32 Ma",
        conditions_arret="critère inapplicable",
        donnees_apprentissage="LR04 5320-2600 ka",
        donnees_validation="LR04 2600-0 ka",
        statut_final="Sans verdict",
        ou="…/RAPPORT_TESTS_REELS.md T4 : LR04 franchit 1 six fois, "
           "critère non défini sur l'observation",
    ),
    dict(
        identifiant="H-C-006",
        formulation="Le verdict négatif ne dépend pas du découpage "
                    "calibration / prédiction.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="RMSE par bloc",
        prediction_oric="au moins un bloc favorable à M2 contre M1P",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="validation croisée en cinq blocs contigus",
        metrique_principale="nombre de blocs favorables",
        seuil_de_reussite="majorité de blocs favorables",
        fenetre_temporelle="cinq blocs de 520 ka sur 2,6 Ma",
        conditions_arret="zéro bloc favorable",
        donnees_apprentissage="quatre blocs sur cinq, en rotation",
        donnees_validation="bloc restant",
        statut_final="Réfuté",
        ou="…/RAPPORT_TESTS_REELS_2.md G1, 0 bloc sur 5",
    ),
    dict(
        identifiant="H-C-007",
        formulation="La mémoire de M2 porte une information de sens du temps "
                    "que le témoin apparié n'a pas.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="RMSE d'ajustement en sens direct et retourné",
        prediction_oric="asymétrie de M2 supérieure à celle de M1P",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="retournement temporel sur masque centré "
                                  "symétrique",
        metrique_principale="asymétrie RMSE arrière moins avant",
        seuil_de_reussite="asymétrie M2 > asymétrie M1P",
        fenetre_temporelle="masque centré 2015-585 ka, 1431 points",
        conditions_arret="aucun intervalle de confiance calculable",
        donnees_apprentissage="masque centré",
        donnees_validation="même masque, sens inversé",
        statut_final="Non concluant",
        ou="…/RAPPORT_TESTS_REELS_2.md G2 corrigé, aucun IC, effets 1 à 6 %",
    ),
    dict(
        identifiant="H-C-008",
        formulation="Le verdict négatif ne dépend pas de la convention "
                    "d'insolation.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="RMSE sous quatre conventions",
        prediction_oric="au moins une convention favorable à M2",
        modele_nul="M0",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="60N, 65N, 70N au solstice et moyenne annuelle",
        metrique_principale="signe du gain contre M1P",
        seuil_de_reussite="au moins une convention favorable",
        fenetre_temporelle="calibration 2600-1200 ka, prédiction 1200-0 ka",
        conditions_arret="zéro convention favorable",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="LR04 1200-0 ka",
        statut_final="Réfuté",
        ou="…/RAPPORT_TESTS_REELS_2.md G3, 0 sur 4, étendue 0,006",
    ),
    dict(
        identifiant="H-C-009",
        formulation="Le gain de M2 se distingue d'une distribution nulle de "
                    "même spectre et de phases aléatoires.",
        domaine="branche 2 couche mémoire", type="confirmatoire",
        variables_observables="gain relatif sur cibles surrogates",
        prediction_oric="gain observé au-dessus de la distribution nulle",
        modele_nul="surrogates de Fourier",
        modele_concurrent="M1",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="randomisation des phases de la cible",
        metrique_principale="p unilatérale",
        seuil_de_reussite="p < 0,05",
        fenetre_temporelle="calibration 2600-1200 ka, prédiction 1200-0 ka",
        conditions_arret="puissance insuffisante",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="12 surrogates",
        statut_final="Non concluant",
        ou="…/RAPPORT_TESTS_REELS_2.md G4, p = 0,923, nulle large",
    ),
    dict(
        identifiant="H-C-010",
        formulation="L'indétermination des solutions orbitales limite "
                    "l'interprétation des résultats climatiques.",
        domaine="branche 2 couche mémoire", type="exploratoire",
        variables_observables="excentricité des quatre solutions La2010",
        prediction_oric="dispersion comparable aux effets discutés",
        modele_nul="solution unique",
        modele_concurrent="sans objet",
        temoin_complexite_egale="sans objet",
        intervention_ou_contraste="comparaison des quatre solutions admissibles",
        metrique_principale="dispersion relative moyenne",
        seuil_de_reussite="sans objet, mesure de plancher",
        fenetre_temporelle="0-2600 ka",
        conditions_arret="sans objet",
        donnees_apprentissage="aucune",
        donnees_validation="La2010 a, b, c, d",
        statut_final="Établi",
        ou="…/RAPPORT_TESTS_REELS.md T3, 5,2e-4 ; l'objection est fermée",
    ),
    dict(
        identifiant="H-C-011",
        formulation="La bistabilité de l'EMIC réduit suffit à produire une "
                    "dépendance au chemin permanente.",
        domaine="branche 2 test prospectif", type="confirmatoire",
        variables_observables="étendue de la fraction de glace finale",
        prediction_oric="attracteurs multiples sans états lents",
        modele_nul="mode classic",
        modele_concurrent="mode ablated",
        temoin_complexite_egale="M2P",
        intervention_ou_contraste="balayage de 150 états initiaux sur 400 Ma",
        metrique_principale="étendue de la fraction de glace",
        seuil_de_reussite="étendue non nulle",
        fenetre_temporelle="400 Ma",
        conditions_arret="monostabilité aux points testés",
        donnees_apprentissage="aucune, modèle",
        donnees_validation="quatre points de forçage",
        statut_final="Réfuté",
        ou="…/results_stress/prospectif/RAPPORT_PROSPECTIF.md H1",
    ),
    dict(
        identifiant="H-C-012",
        formulation="La mémoire ORI-C ajoute quelque chose à bistabilité égale.",
        domaine="branche 2 test prospectif", type="confirmatoire",
        variables_observables="monostabilité de M2P",
        prediction_oric="M2 multistable, M2P monostable",
        modele_nul="mode classic",
        modele_concurrent="mode ablated",
        temoin_complexite_egale="M2P, mal apparié sur le canal régolithe",
        intervention_ou_contraste="substitution des entrées des états lents",
        metrique_principale="étendue de la fraction de glace",
        seuil_de_reussite="préenregistré",
        fenetre_temporelle="400 Ma",
        conditions_arret="témoin non apparié",
        donnees_apprentissage="aucune, modèle",
        donnees_validation="quatre points de forçage",
        statut_final="Non concluant",
        ou="…/RAPPORT_PROSPECTIF.md H2 ; à repréenregistrer, WP-C2",
    ),
    dict(
        identifiant="H-C-013",
        formulation="Les bassins d'attraction sont asymétriques.",
        domaine="branche 2 test prospectif", type="confirmatoire",
        variables_observables="frontière de bassin",
        prediction_oric="asymétrie mesurable",
        modele_nul="mode classic",
        modele_concurrent="mode ablated",
        temoin_complexite_egale="M2P",
        intervention_ou_contraste="bissection de la frontière de bassin",
        metrique_principale="asymétrie de bassin",
        seuil_de_reussite="préenregistré",
        fenetre_temporelle="400 Ma",
        conditions_arret="frontière indéterminable au sens du protocole",
        donnees_apprentissage="aucune, modèle",
        donnees_validation="quatre points de forçage",
        statut_final="Non évalué",
        ou="…/RAPPORT_PROSPECTIF.md H3 ; frontière indéterminable",
    ),
    # -- Application climatique -------------------------------------------
    dict(
        identifiant="H-CL-001",
        formulation="Un modèle multi-mémoires bat une intégrale temporelle "
                    "unique du forçage cumulé.",
        domaine="application climatique", type="confirmatoire",
        variables_observables="noyaux de mémoire par compartiment",
        prediction_oric="gain prédictif du modèle multi-mémoires",
        modele_nul="intégrale unique des émissions cumulées",
        modele_concurrent="modèle à noyau fixe unique",
        temoin_complexite_egale="modèle de même nombre de paramètres, "
                                "mémoires découplées",
        intervention_ou_contraste="expériences d'arrêt des émissions",
        metrique_principale="à préenregistrer, WP-CL1",
        seuil_de_reussite="à préenregistrer",
        fenetre_temporelle="longue devant toutes les constantes de temps",
        conditions_arret="aucun gain contre le témoin apparié",
        donnees_apprentissage="simulations historiques",
        donnees_validation="scénarios réservés",
        statut_final="Non testé",
        ou="02_.../application_climat/, hors chaîne de preuve",
    ),
    # -- Branche 3 ---------------------------------------------------------
    dict(
        identifiant="H-V-001",
        formulation="Un système protocellulaire franchit les six conditions "
                    "du critère minimal de transition matière-hérédité.",
        domaine="branche 3 régime 7", type="confirmatoire",
        variables_observables="lignées, copies, variantes, division, fonction",
        prediction_oric="six conditions atteintes simultanément",
        modele_nul="chimie sans compartiment",
        modele_concurrent="compartiment sans matrice",
        temoin_complexite_egale="polymère non copiable apparié en longueur, "
                                "charge, concentration, encombrement",
        intervention_ou_contraste="ablations membrane, matrice, énergie, "
                                  "variation ; permutation des environnements",
        metrique_principale="proportion de descendants conservant information "
                            "héritée et différence fonctionnelle",
        seuil_de_reussite="6/6 conditions, plus avantage sur témoin apparié",
        fenetre_temporelle="longue devant toutes les mémoires du système",
        conditions_arret="échec sur deux réplications indépendantes",
        donnees_apprentissage="aucune, expérience à mener",
        donnees_validation="second laboratoire",
        statut_final="Non testé",
        ou="03_branche_vivant/programme_prebiotique/PROGRAMME_PREBIOTIQUE.md",
    ),
    dict(
        identifiant="H-V-002",
        formulation="L'histoire d'exposition modifie l'architecture de "
                    "résistance à MIC finale égale.",
        domaine="branche 3 régime 8", type="confirmatoire",
        variables_observables="MIC, fitness, mutations, expression génique",
        prediction_oric="dépendance au chemin à état final vérifié identique",
        modele_nul="modèle de population classique",
        modele_concurrent="fitness landscape, chaînes de Markov",
        temoin_complexite_egale="modèle prédictif de même complexité sans "
                                "variable d'histoire",
        intervention_ou_contraste="même dose cumulée, ordres différents",
        metrique_principale="à préenregistrer, WP-R4",
        seuil_de_reussite="avantage hors échantillon",
        fenetre_temporelle="plusieurs cycles, au-delà du retrait",
        conditions_arret="avantage nul contre témoin apparié",
        donnees_apprentissage="lignées d'apprentissage",
        donnees_validation="lignées masquées",
        statut_final="Non testé",
        ou="03_branche_vivant/README.md, acte 3",
    ),
    # -- Ajouts de la campagne du plan directeur --------------------------
    dict(
        identifiant="H-S-003",
        formulation="Il existe un domaine ou reduire une perte diminue la "
                    "persistance globale par effet indirect.",
        domaine="socle", type="exploratoire",
        variables_observables="biomasse finale en fonction du taux de perte",
        prediction_oric="non-monotonie de P* en fonction de l",
        modele_nul="chemostat a deux variables",
        modele_concurrent="neuf extensions structurelles",
        temoin_complexite_egale="structures appariees en nombre d especes",
        intervention_ou_contraste="balayage de 200 jeux de parametres",
        metrique_principale="remontee relative de la biomasse finale",
        seuil_de_reussite="remontee >= 1 % de l amplitude",
        fenetre_temporelle="4000 unites, au-dela de tous les transitoires",
        conditions_arret="aucune remontee au-dessus du bruit d integration",
        donnees_apprentissage="aucune, modele",
        donnees_validation="600 configurations",
        statut_final="Établi",
        ou="00_socle/test_interventionnel/PORTEE_WP_S2.md : 10 cas sur 600, "
           "competition et retard",
    ),
    dict(
        identifiant="H-C-014",
        formulation="M2 bat des familles de modeles entierement differentes, "
                    "a budget et donnees egaux.",
        domaine="branche 2 couche memoire", type="confirmatoire",
        variables_observables="RMSE hors echantillon de onze modeles",
        prediction_oric="M2 en tete du classement",
        modele_nul="persistance, zero parametre",
        modele_concurrent="six familles concurrentes",
        temoin_complexite_egale="M1P",
        intervention_ou_contraste="meme fenetre, meme budget, roue libre",
        metrique_principale="RMSE hors echantillon, BIC",
        seuil_de_reussite="premier rang",
        fenetre_temporelle="calibration 2600-1200 ka, prediction 1200-0 ka",
        conditions_arret="un modele plus simple fait aussi bien",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="LR04 1200-0 ka",
        statut_final="Réfuté",
        ou="RAPPORT_WP_C4.md : rang 4 sur 11 ; persistance a 0 parametre est "
           "2e et bat M2 de 16 %",
    ),
    dict(
        identifiant="H-C-015",
        formulation="Les parametres de M2 sont identifiables sur LR04.",
        domaine="branche 2 couche memoire", type="confirmatoire",
        variables_observables="vecteurs de parametres sur quatre graines",
        prediction_oric="dispersion relative faible",
        modele_nul="M0, 3 parametres",
        modele_concurrent="M1, 6 parametres",
        temoin_complexite_egale="M1P, 8 parametres",
        intervention_ou_contraste="quatre graines d optimisation",
        metrique_principale="dispersion relative maximale des parametres",
        seuil_de_reussite="< 0,10",
        fenetre_temporelle="calibration 2600-1200 ka",
        conditions_arret="dispersion superieure a 1",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="sans objet",
        statut_final="Réfuté",
        ou="RAPPORT_WP_C6.md : dispersion 1,233 pour M2 et 1,680 pour M1P, "
           "contre 0,003 pour M0",
    ),
    dict(
        identifiant="H-C-016",
        formulation="Avec un temoin correctement apparie, M2 conserve une "
                    "multistabilite que le temoin n a pas.",
        domaine="branche 2 test prospectif", type="confirmatoire",
        variables_observables="etendue de la fraction de glace finale",
        prediction_oric="M2 multistable, temoin monostable",
        modele_nul="mode classic",
        modele_concurrent="mode ablated",
        temoin_complexite_egale="M2P corrige, deux entrees externes distinctes",
        intervention_ou_contraste="24 etats initiaux, deux points discriminants",
        metrique_principale="etendue de la glace finale",
        seuil_de_reussite="0,05, preenregistre",
        fenetre_temporelle="400 Ma, soit 6600 fois tau_max",
        conditions_arret="appariement des plages non tenu",
        donnees_apprentissage="aucune, modele",
        donnees_validation="deux points discriminants",
        statut_final="Non concluant",
        ou="prospectif_c2/RAPPORT_WP_C2.md : temoin multistable lui aussi, et "
           "appariement echoue, rapports 6,5 et 3,4 pour un seuil de 2",
    ),
    dict(
        identifiant="H-C-017",
        formulation="Le mecanisme manquant a M2 est conditionnel : une "
                    "variable lente modifie l operateur de reponse.",
        domaine="branche 2 couche memoire", type="exploratoire",
        variables_observables="RMSE de quatre formes emboitees",
        prediction_oric="la forme conditionnelle est retenue",
        modele_nul="forme brute",
        modele_concurrent="formes additive et affine",
        temoin_complexite_egale="penalisation BIC a parametres comptes",
        intervention_ou_contraste="comparaison de quatre formes emboitees",
        metrique_principale="BIC",
        seuil_de_reussite="forme conditionnelle retenue",
        fenetre_temporelle="prediction 1200-0 ka",
        conditions_arret="une forme plus simple est retenue",
        donnees_apprentissage="LR04 2600-1200 ka",
        donnees_validation="LR04 1200-0 ka",
        statut_final="Réfuté",
        ou="RAPPORT_WP_C7.md : le BIC retient la forme affine, gain +27,7 %",
    ),
    dict(
        identifiant="H-S-004",
        formulation="La structure de la carte relationnelle porte une "
                    "information que l ordre chronologique ne contient pas.",
        domaine="socle", type="confirmatoire",
        variables_observables="AUC de prediction de liens et de regimes",
        prediction_oric="le predicteur structurel bat la proximite",
        modele_nul="hasard",
        modele_concurrent="proximite chronologique",
        temoin_complexite_egale="graphes nuls a degres et ordre conserves",
        intervention_ou_contraste="masquage de liens et de transitions",
        metrique_principale="AUC, erreur absolue de regime",
        seuil_de_reussite="AUC structurelle superieure a la proximite",
        fenetre_temporelle="sans objet",
        conditions_arret="AUC au niveau du hasard",
        donnees_apprentissage="carte privee des elements masques",
        donnees_validation="elements masques",
        statut_final="Réfuté",
        ou="00_socle/carte_relationnelle/ANALYSE_GRAPHE.md : AUC 0,491 contre "
           "0,922 ; WP-M5 : EAM 0,618 contre 0,206",
    ),
    dict(
        identifiant="H-T-002",
        formulation="Les notions du socle produisent une mesure dans "
                    "plusieurs branches.",
        domaine="transversal", type="exploratoire",
        variables_observables="presence d une mesure par notion et par branche",
        prediction_oric="notions invariantes entre branches",
        modele_nul="notion employee sans mesure",
        modele_concurrent="descriptions disciplinaires separees",
        temoin_complexite_egale="sans objet",
        intervention_ou_contraste="recherche dans les fichiers generes seuls",
        metrique_principale="nombre de branches par notion",
        seuil_de_reussite="au moins deux branches",
        fenetre_temporelle="sans objet",
        conditions_arret="notion sans aucune mesure",
        donnees_apprentissage="sans objet",
        donnees_validation="dossier complet",
        statut_final="Non concluant",
        ou="plan_directeur/AUDIT_TRANSVERSAL.md : 8 notions sur 15 traversent "
           "deux branches ; la chaine ORI-C n en mesure aucune",
    ),
    # -- Transversal -------------------------------------------------------
    dict(
        identifiant="H-T-001",
        formulation="Une même définition ORI-C produit une mesure dans les "
                    "trois branches sans modification.",
        domaine="transversal", type="confirmatoire",
        variables_observables="D, H, L, Pacc, séparation X/m/A",
        prediction_oric="portabilité sans adaptation des définitions",
        modele_nul="descriptions disciplinaires séparées",
        modele_concurrent="cadres de résilience classiques",
        temoin_complexite_egale="à définir par domaine",
        intervention_ou_contraste="benchmark multi-domaines",
        metrique_principale="performance et calibration comparées",
        seuil_de_reussite="à préenregistrer, WP-T2",
        fenetre_temporelle="par domaine",
        conditions_arret="définition non applicable sans adaptation",
        donnees_apprentissage="cas du benchmark",
        donnees_validation="cas réservés",
        statut_final="Non testé",
        ou="plan_directeur/PLAN_DIRECTEUR_TESTS.md WP-T1 et WP-T2",
    ),
]


def ecrire() -> int:
    with CIBLE.open("w", encoding="utf-8-sig", newline="") as flux:
        redacteur = csv.DictWriter(flux, fieldnames=COLONNES,
                                   delimiter=SEPARATEUR)
        redacteur.writeheader()
        for entree in E:
            manquantes = set(COLONNES) - set(entree)
            if manquantes:
                raise SystemExit(
                    f"{entree['identifiant']} : champs absents {sorted(manquantes)}"
                )
            redacteur.writerow(entree)
    return len(E)


def verifier() -> int:
    if not CIBLE.exists():
        print(f"{CIBLE.name} absent.")
        return 1
    with CIBLE.open(encoding="utf-8-sig", newline="") as flux:
        lignes = list(csv.DictReader(flux, delimiter=SEPARATEUR))
    anomalies = []
    identifiants = set()
    for index, ligne in enumerate(lignes, start=2):
        identifiant = ligne["identifiant"]
        if identifiant in identifiants:
            anomalies.append(f"ligne {index} : identifiant `{identifiant}` "
                             "en double")
        identifiants.add(identifiant)
        if ligne["type"] not in TYPES:
            anomalies.append(f"{identifiant} : type `{ligne['type']}` hors "
                             f"vocabulaire {sorted(TYPES)}")
        if ligne["statut_final"] not in STATUTS:
            anomalies.append(f"{identifiant} : statut "
                             f"`{ligne['statut_final']}` hors échelle")
        for colonne in COLONNES:
            if not (ligne.get(colonne) or "").strip():
                anomalies.append(f"{identifiant} : `{colonne}` vide")
        # Étape 0.5 : un confirmatoire doit porter son témoin apparié.
        if ligne["type"] == "confirmatoire" \
                and not ligne["temoin_complexite_egale"].strip():
            anomalies.append(f"{identifiant} : confirmatoire sans témoin de "
                             "complexité égale")
    for anomalie in anomalies:
        print(f"  {anomalie}")
    if anomalies:
        print(f"\n{len(anomalies)} anomalie(s).")
        return 1

    compte: dict[str, int] = {}
    for ligne in lignes:
        compte[ligne["statut_final"]] = compte.get(ligne["statut_final"], 0) + 1
    print(f"{CIBLE.name} : {len(lignes)} hypothèses, registre conforme.")
    for statut, nombre in sorted(compte.items(), key=lambda x: -x[1]):
        print(f"  {nombre:2d}  {statut}")
    return 0


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--verifier", action="store_true")
    arguments = parseur.parse_args()
    if arguments.verifier:
        return verifier()
    nombre = ecrire()
    print(f"{CIBLE.name} écrit : {nombre} hypothèses")
    return verifier()


if __name__ == "__main__":
    sys.exit(main())
