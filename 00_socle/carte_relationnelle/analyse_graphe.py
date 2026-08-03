"""Carte relationnelle — WP-S3.12 à S3.19 du plan directeur.

Les 33 tests de `00_socle/tests/test_carte_relationnelle.py` vérifient déjà
l'intégrité, les cycles, la connexité et les niveaux de preuve. Ils ne
répondent pas à la question du plan directeur :

    la structure de la carte porte-t-elle une information, ou reflète-t-elle
    seulement le choix manuel des nœuds et leur ordre chronologique ?

Trois analyses, toutes exécutables sur les données présentes.

    A. Métriques de graphe : centralité, modularité, chemins, goulets.
    B. Graphes nuls conservant le degré. Une propriété qui n'excède pas ce que
       produit un rebranchement aléatoire à degrés fixés n'est pas une
       propriété de la carte.
    C. Prédiction de liens masqués, comparée à deux témoins : la proximité
       chronologique simple, et le hasard. C'est le test décisif du §S3.16 :
       si la structure ne bat pas « les transitions voisines sont liées », la
       carte n'ajoute rien à une chronologie.

Exécution : `python analyse_graphe.py [--tirages 2000] [--repetitions 200]`
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import networkx as nx
import numpy as np

RACINE = Path(__file__).resolve().parent
DONNEES = RACINE / "data"
SORTIE = RACINE / "resultats_analyse"
SEPARATEUR = ";"


def charger() -> tuple[nx.DiGraph, dict]:
    with (DONNEES / "noeuds_poc.csv").open(encoding="utf-8-sig",
                                           newline="") as flux:
        noeuds = {l["id"]: l for l in csv.DictReader(flux, delimiter=SEPARATEUR)}
    with (DONNEES / "relations_oric_47_provisoires.csv").open(
            encoding="utf-8-sig", newline="") as flux:
        liens = list(csv.DictReader(flux, delimiter=SEPARATEUR))
    graphe = nx.DiGraph()
    for identifiant, ligne in noeuds.items():
        graphe.add_node(identifiant, **ligne)
    for lien in liens:
        graphe.add_edge(lien["source"], lien["target"],
                        relation=lien["relation"])
    return graphe, noeuds


def rang(identifiant: str) -> int:
    """Ordre chronologique porté par l'identifiant TR-0xx."""
    return int(identifiant.split("-")[1])


# ==========================================================================
# A. Métriques

def metriques(graphe: nx.DiGraph) -> dict:
    sans_direction = graphe.to_undirected()
    intermediarite = nx.betweenness_centrality(graphe)
    communautes = list(
        nx.algorithms.community.greedy_modularity_communities(sans_direction)
    )
    modularite = nx.algorithms.community.modularity(sans_direction, communautes)
    acyclique = nx.DiGraph(
        (u, v) for u, v, d in graphe.edges(data=True)
        if d["relation"] != "FEED"
    )
    plus_long = nx.dag_longest_path(acyclique) if nx.is_directed_acyclic_graph(
        acyclique) else []
    articulation = list(nx.articulation_points(sans_direction))
    return {
        "noeuds": graphe.number_of_nodes(),
        "liens": graphe.number_of_edges(),
        "densite": nx.density(graphe),
        "modularite": float(modularite),
        "nombre_de_communautes": len(communautes),
        "longueur_du_plus_long_chemin": len(plus_long),
        "plus_long_chemin": plus_long,
        "points_d_articulation": sorted(articulation),
        "cinq_plus_intermediaires": sorted(
            intermediarite.items(), key=lambda x: -x[1]
        )[:5],
        "degre_entrant_max": max(dict(graphe.in_degree()).values()),
        "degre_sortant_max": max(dict(graphe.out_degree()).values()),
    }


# ==========================================================================
# B. Graphes nuls à degrés conservés

def _echange_respectant_l_ordre(graphe, rng, passes=3):
    """Double échange conservant les degrés **et** l'acyclicité.

    Le rebranchement libre de `directed_edge_swap` détruit l'ordre
    chronologique : tous les tirages deviennent cycliques et la longueur du
    plus long chemin y vaut zéro par convention. La comparaison n'a alors
    aucun sens. Ce nul-ci n'échange deux arêtes que si les deux arêtes
    produites vont encore d'un rang inférieur vers un rang supérieur, ce qui
    garantit un graphe orienté acyclique à degrés entrants et sortants
    inchangés.
    """
    copie = graphe.copy()
    aretes = list(copie.edges())
    for _ in range(passes * len(aretes)):
        i, j = rng.integers(0, len(aretes), 2)
        if i == j:
            continue
        (u1, v1), (u2, v2) = aretes[i], aretes[j]
        if len({u1, v1, u2, v2}) < 4:
            continue
        if rang(v2) <= rang(u1) or rang(v1) <= rang(u2):
            continue
        if copie.has_edge(u1, v2) or copie.has_edge(u2, v1):
            continue
        relation1 = copie[u1][v1]["relation"]
        relation2 = copie[u2][v2]["relation"]
        copie.remove_edge(u1, v1)
        copie.remove_edge(u2, v2)
        copie.add_edge(u1, v2, relation=relation1)
        copie.add_edge(u2, v1, relation=relation2)
        aretes[i], aretes[j] = (u1, v2), (u2, v1)
    return copie


def graphes_nuls(graphe: nx.DiGraph, tirages: int, rng) -> dict:
    """Rebranchement par double échange, degrés entrants et sortants fixés."""
    observees = metriques(graphe)
    modularites, chemins, communautes = [], [], []

    for _ in range(tirages):
        copie = graphe.copy()
        try:
            nx.directed_edge_swap(
                copie, nswap=3 * copie.number_of_edges(),
                max_tries=200 * copie.number_of_edges(),
                seed=int(rng.integers(0, 2 ** 31 - 1)),
            )
        except (nx.NetworkXError, nx.NetworkXAlgorithmError):
            continue
        sans_direction = copie.to_undirected()
        parties = list(
            nx.algorithms.community.greedy_modularity_communities(sans_direction)
        )
        modularites.append(
            nx.algorithms.community.modularity(sans_direction, parties)
        )
        communautes.append(len(parties))
        acyclique = nx.DiGraph(
            (u, v) for u, v, d in copie.edges(data=True)
            if d["relation"] != "FEED"
        )
        chemins.append(
            len(nx.dag_longest_path(acyclique))
            if nx.is_directed_acyclic_graph(acyclique) else 0
        )

    def situer(valeur, echantillon, nom):
        echantillon = np.asarray(echantillon, dtype=float)
        if len(echantillon) < 2:
            return {"observe": valeur, "nulle_indisponible": True}
        ecart = echantillon.std(ddof=1)
        return {
            "observe": float(valeur),
            "nulle_moyenne": float(echantillon.mean()),
            "nulle_ecart_type": float(ecart),
            "z": float((valeur - echantillon.mean()) / ecart) if ecart else None,
            "p_bilaterale": float(
                (np.sum(np.abs(echantillon - echantillon.mean())
                        >= abs(valeur - echantillon.mean())) + 1)
                / (len(echantillon) + 1)
            ),
            "quantite": nom,
        }

    # Seconde famille : degrés conservés ET acyclicité préservée.
    mod_ordre, chem_ordre, com_ordre = [], [], []
    for _ in range(tirages):
        copie = _echange_respectant_l_ordre(graphe, rng)
        sans_direction = copie.to_undirected()
        parties = list(
            nx.algorithms.community.greedy_modularity_communities(sans_direction)
        )
        mod_ordre.append(
            nx.algorithms.community.modularity(sans_direction, parties)
        )
        com_ordre.append(len(parties))
        acyclique = nx.DiGraph(
            (u, v) for u, v, d in copie.edges(data=True)
            if d["relation"] != "FEED"
        )
        chem_ordre.append(
            len(nx.dag_longest_path(acyclique))
            if nx.is_directed_acyclic_graph(acyclique) else 0
        )

    return {
        "tirages_reussis": len(modularites),
        "nul_respectant_l_ordre": {
            "tirages": len(mod_ordre),
            "modularite": situer(observees["modularite"], mod_ordre,
                                 "modularité"),
            "longueur_du_plus_long_chemin": situer(
                observees["longueur_du_plus_long_chemin"], chem_ordre,
                "longueur du plus long chemin"),
            "nombre_de_communautes": situer(
                observees["nombre_de_communautes"], com_ordre,
                "nombre de communautés"),
        },
        "modularite": situer(observees["modularite"], modularites,
                             "modularité"),
        "longueur_du_plus_long_chemin": situer(
            observees["longueur_du_plus_long_chemin"], chemins,
            "longueur du plus long chemin"),
        "nombre_de_communautes": situer(
            observees["nombre_de_communautes"], communautes,
            "nombre de communautés"),
        "lecture": (
            "Le rebranchement conserve les degrés entrants et sortants de "
            "chaque nœud. Une quantité dont le z est faible ne distingue pas "
            "la carte d'un graphe aléatoire de mêmes degrés : elle vient du "
            "choix des nœuds, pas du codage des liens."
        ),
    }


# ==========================================================================
# C. Prédiction de liens masqués

def _candidats(graphe):
    """Toutes les paires orientées admissibles, hors FEED, sans boucle."""
    noeuds = sorted(graphe.nodes(), key=rang)
    for u in noeuds:
        for v in noeuds:
            if u != v and rang(v) > rang(u):
                yield (u, v)


def _score_structurel(entrainement, paires):
    """Adamic-Adar sur la projection non orientée, prédicteur standard."""
    sans_direction = entrainement.to_undirected()
    scores = {}
    for u, v in paires:
        if u not in sans_direction or v not in sans_direction:
            scores[(u, v)] = 0.0
            continue
        communs = set(sans_direction[u]) & set(sans_direction[v])
        scores[(u, v)] = float(sum(
            1.0 / np.log(max(sans_direction.degree(w), 2))
            for w in communs
        ))
    return scores


def _score_proximite(paires):
    """Témoin : les transitions chronologiquement voisines sont liées."""
    return {(u, v): -float(rang(v) - rang(u)) for u, v in paires}


def _auc(verite, scores) -> float:
    """Aire sous la courbe ROC, par somme de rangs.

    Implémentée ici plutôt qu'importée : le dossier n'a pas scikit-learn en
    dépendance et n'a pas besoin de l'acquérir pour une statistique de rang.
    Les ex aequo reçoivent le rang moyen, ce qui est le traitement correct
    pour un prédicteur qui renvoie beaucoup de zéros.
    """
    verite = np.asarray(verite, dtype=float)
    scores = np.asarray(scores, dtype=float)
    positifs = verite == 1
    n1, n0 = int(positifs.sum()), int((~positifs).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    ordre = np.argsort(scores, kind="mergesort")
    rangs = np.empty(len(scores), dtype=float)
    rangs[ordre] = np.arange(1, len(scores) + 1, dtype=float)
    # Rang moyen sur chaque groupe d'ex aequo.
    tries = scores[ordre]
    debut = 0
    for indice in range(1, len(tries) + 1):
        if indice == len(tries) or tries[indice] != tries[debut]:
            if indice - debut > 1:
                moyen = rangs[ordre[debut:indice]].mean()
                rangs[ordre[debut:indice]] = moyen
            debut = indice
    return float((rangs[positifs].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def prediction_de_liens(graphe, repetitions, masques, rng) -> dict:

    reels = [(u, v) for u, v, d in graphe.edges(data=True)
             if d["relation"] != "FEED"]
    toutes = list(_candidats(graphe))
    ensemble_reel = set(reels)

    resultats = {"structurel": [], "proximite": [], "hasard": []}
    for _ in range(repetitions):
        caches = [reels[i] for i in rng.choice(len(reels), masques,
                                               replace=False)]
        entrainement = graphe.copy()
        entrainement.remove_edges_from(caches)

        # Les négatifs sont les paires admissibles qui ne sont liées nulle part.
        negatifs_possibles = [p for p in toutes if p not in ensemble_reel]
        negatifs = [negatifs_possibles[i] for i in rng.choice(
            len(negatifs_possibles), masques * 10, replace=False)]
        evaluees = caches + negatifs
        verite = [1] * len(caches) + [0] * len(negatifs)

        structurels = _score_structurel(entrainement, evaluees)
        proximites = _score_proximite(evaluees)
        resultats["structurel"].append(
            _auc(verite, [structurels[p] for p in evaluees])
        )
        resultats["proximite"].append(
            _auc(verite, [proximites[p] for p in evaluees])
        )
        resultats["hasard"].append(_auc(verite, rng.random(len(evaluees))))

    resume = {
        nom: {
            "auc_moyenne": float(np.mean(valeurs)),
            "auc_ecart_type": float(np.std(valeurs, ddof=1)),
            "auc_ic_2.5": float(np.percentile(valeurs, 2.5)),
            "auc_ic_97.5": float(np.percentile(valeurs, 97.5)),
        }
        for nom, valeurs in resultats.items()
    }
    ecart = np.asarray(resultats["structurel"]) - np.asarray(
        resultats["proximite"])
    resume["structurel_moins_proximite"] = {
        "moyenne": float(ecart.mean()),
        "ic_2.5": float(np.percentile(ecart, 2.5)),
        "ic_97.5": float(np.percentile(ecart, 97.5)),
        "fraction_de_tirages_favorables_au_structurel": float(
            np.mean(ecart > 0)
        ),
    }
    resume["repetitions"] = repetitions
    resume["liens_masques_par_tirage"] = masques
    resume["lecture"] = (
        "Le témoin de proximité prédit qu'une transition est liée à celles qui "
        "la suivent immédiatement. Si le prédicteur structurel ne le bat pas, "
        "la carte n'ajoute rien à une chronologie ordonnée."
    )
    return resume


# ==========================================================================

def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--tirages", type=int, default=2000)
    parseur.add_argument("--repetitions", type=int, default=200)
    parseur.add_argument("--masques", type=int, default=8)
    parseur.add_argument("--graine", type=int, default=20260801)
    arguments = parseur.parse_args()

    SORTIE.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(arguments.graine)
    graphe, _ = charger()

    print("[carte] métriques ...", flush=True)
    rapport = {"graine": arguments.graine, "A_metriques": metriques(graphe)}
    print("[carte] graphes nuls ...", flush=True)
    rapport["B_graphes_nuls"] = graphes_nuls(graphe, arguments.tirages, rng)
    print("[carte] prédiction de liens ...", flush=True)
    rapport["C_prediction_de_liens"] = prediction_de_liens(
        graphe, arguments.repetitions, arguments.masques, rng)

    (SORTIE / "analyse_graphe.json").write_text(
        json.dumps(rapport, indent=2, ensure_ascii=False, default=float),
        encoding="utf-8",
    )
    print(json.dumps(rapport, indent=2, ensure_ascii=False, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
