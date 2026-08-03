"""Vérification de la carte relationnelle : inventaire, typage, graphe, preuves.

Reprend les assertions de `verifier_dossier.py` en les rendant indépendantes
les unes des autres — un échec ne masque plus les suivants — et y ajoute les
contrôles d'intégrité référentielle qui manquaient.
"""
from __future__ import annotations

import collections
import re

import networkx as nx
import pytest

from conftest import lire_csv

REPARTITION_ATTENDUE = {
    "ENBL": 19, "MATR": 13, "ENVR": 4, "STAB": 2, "CATL": 1,
    "CNST": 2, "CONT": 1, "DEPG": 1, "INCO": 1, "DESC": 2, "FEED": 1,
}
NIVEAUX_AUTORISES = {"Établi", "Fortement inféré", "Plausible", "Hypothétique"}
CHAMPS_OBLIGATOIRES = [
    "portee_du_lien", "niveau_preuve", "mode_preuve",
    "justification", "limite_interpretative", "reference_cle",
]
REGIMES_ATTENDUS = {
    1: "Physique fondamentale", 2: "Atomes et étoiles", 3: "Molécules",
    4: "Solides cosmiques", 5: "Architectures planétaires",
    6: "Diversification minérale", 7: "Voies prébiotiques", 8: "Vivant",
}


# --- Inventaire ------------------------------------------------------------
# Colonnes renseignées seulement quand elles s'appliquent.
CHAMPS_FACULTATIFS = {"domaine_ferme", "note_codage"}


def test_quarante_transitions(noeuds) -> None:
    assert len(noeuds) == 40


def test_identifiants_contigus_de_tr001_a_tr040(noeuds) -> None:
    assert [ligne["id"] for ligne in noeuds] == [f"TR-{i:03d}" for i in range(1, 41)]


def test_aucun_champ_de_transition_vide(noeuds) -> None:
    vides = [
        (ligne["id"], champ)
        for ligne in noeuds
        for champ, valeur in ligne.items()
        if not (valeur or "").strip()
    ]
    vides = [couple for couple in vides if couple[1] not in CHAMPS_FACULTATIFS]
    assert not vides, f"Champs vides dans l'inventaire : {vides}"


def test_les_huit_regimes_sont_couverts_et_nommes(noeuds) -> None:
    observes = {int(ligne["regime_num"]): ligne["regime_nom"] for ligne in noeuds}
    assert observes == REGIMES_ATTENDUS


def test_les_regimes_ne_reculent_pas_le_long_de_l_inventaire(noeuds) -> None:
    """TR-001 à TR-040 est un ordre de lecture : les régimes y sont croissants."""
    numeros = [int(ligne["regime_num"]) for ligne in noeuds]
    assert numeros == sorted(numeros)


# --- Liens -----------------------------------------------------------------
def test_quarante_sept_liens(liens) -> None:
    assert len(liens) == 47


def test_repartition_des_codes(liens) -> None:
    comptes = collections.Counter(ligne["relation"] for ligne in liens)
    assert dict(comptes) == REPARTITION_ATTENDUE


def test_aucun_lien_duplique(liens) -> None:
    cles = [(l["source"], l["target"], l["relation"]) for l in liens]
    doublons = [cle for cle, n in collections.Counter(cles).items() if n > 1]
    assert not doublons, f"Liens dupliqués : {doublons}"


def test_aucune_paire_source_cible_repetee(liens) -> None:
    """Deux relations différentes entre les deux mêmes nœuds seraient ambiguës."""
    paires = [(l["source"], l["target"]) for l in liens]
    doublons = [paire for paire, n in collections.Counter(paires).items() if n > 1]
    assert not doublons, f"Paires répétées sous des codes différents : {doublons}"


def test_integrite_referentielle(liens, noeuds) -> None:
    identifiants = {ligne["id"] for ligne in noeuds}
    orphelins = {l["source"] for l in liens} | {l["target"] for l in liens}
    assert not (orphelins - identifiants), f"Extrémités hors inventaire : {orphelins - identifiants}"


def test_aucune_boucle_sur_soi(liens) -> None:
    assert not [l for l in liens if l["source"] == l["target"]]


def test_tous_les_champs_documentaires_sont_renseignes(liens) -> None:
    manquants = [
        (l["source"], l["target"], champ)
        for l in liens for champ in CHAMPS_OBLIGATOIRES
        if not l[champ].strip()
    ]
    manquants = [
        couple for couple in manquants if couple[-1] not in CHAMPS_FACULTATIFS
    ]
    assert not manquants, f"Champs documentaires vides : {manquants}"


LACUNES_DE_REFERENCE_CONNUES = {("TR-021", "TR-028"), ("TR-024", "TR-023")}


@pytest.mark.xfail(
    reason="Deux liens portent une référence générique, sans année, DOI ni arXiv : "
           "TR-021 -> TR-028 (« Observations minéralogiques naturelles et expériences "
           "de haute pression. ») et TR-024 -> TR-023 (« Modèles climatiques "
           "planétaires; aucune hydrosphère détectée sur TRAPPIST-1e. »). "
           "Le test passera au vert dès qu'une source datable leur sera attachée.",
    strict=False,
)
def test_chaque_reference_cle_est_datable(liens) -> None:
    """Une référence sans année ni DOI n'est pas vérifiable par un lecteur."""
    sans_ancrage = [
        (l["source"], l["target"])
        for l in liens
        if not re.search(r"(19|20)\d{2}|doi:|arXiv:", l["reference_cle"], re.IGNORECASE)
    ]
    assert not sans_ancrage, f"Références non datables : {sans_ancrage}"


def test_aucune_lacune_de_reference_nouvelle(liens) -> None:
    """Verrou de non-régression : les lacunes connues ne doivent pas se multiplier."""
    sans_ancrage = {
        (l["source"], l["target"])
        for l in liens
        if not re.search(r"(19|20)\d{2}|doi:|arXiv:", l["reference_cle"], re.IGNORECASE)
    }
    nouvelles = sans_ancrage - LACUNES_DE_REFERENCE_CONNUES
    assert not nouvelles, f"Nouvelles références non datables : {nouvelles}"


def test_chaque_reference_cle_est_substantielle(liens) -> None:
    maigres = [
        (l["source"], l["target"], l["reference_cle"])
        for l in liens if len(l["reference_cle"].strip()) < 25
    ]
    assert not maigres, f"Références trop courtes pour être identifiables : {maigres}"


# --- Structure du graphe ---------------------------------------------------
@pytest.fixture(scope="module")
def graphe(liens, noeuds) -> nx.DiGraph:
    g = nx.DiGraph()
    g.add_nodes_from(ligne["id"] for ligne in noeuds)
    for l in liens:
        g.add_edge(l["source"], l["target"], relation=l["relation"])
    return g


def test_graphe_faiblement_connexe(graphe: nx.DiGraph) -> None:
    assert nx.is_weakly_connected(graphe)


def test_aucun_noeud_isole(graphe: nx.DiGraph) -> None:
    isoles = [n for n in graphe.nodes if graphe.degree(n) == 0]
    assert not isoles, f"Transitions non reliées : {isoles}"


def test_acyclique_hors_feed(liens, noeuds) -> None:
    dag = nx.DiGraph()
    dag.add_nodes_from(ligne["id"] for ligne in noeuds)
    dag.add_edges_from((l["source"], l["target"]) for l in liens if l["relation"] != "FEED")
    assert nx.is_directed_acyclic_graph(dag)


def test_feed_est_le_seul_lien_retroactif(graphe: nx.DiGraph, liens) -> None:
    """Le cycle unique de la carte doit être porté par FEED, et par lui seul."""
    cycles = list(nx.simple_cycles(graphe))
    assert len(cycles) == 1, f"Nombre de cycles inattendu : {len(cycles)}"
    aretes_du_cycle = set(zip(cycles[0], cycles[0][1:] + cycles[0][:1]))
    codes = {graphe.edges[a]["relation"] for a in aretes_du_cycle}
    assert "FEED" in codes


# --- Statuts de preuve -----------------------------------------------------
def test_statuts_normalises(liens) -> None:
    statuts = {l["niveau_preuve"] for l in liens}
    assert not (statuts - NIVEAUX_AUTORISES), f"Statuts hors nomenclature : {statuts - NIVEAUX_AUTORISES}"


def test_contextuel_reste_un_type_de_lien_pas_un_niveau(liens) -> None:
    assert "contextuel" not in {l["niveau_preuve"].lower() for l in liens}


@pytest.mark.parametrize(
    "source,cible,niveau_attendu,motif",
    [
        ("TR-036", "TR-030", "Établi",
         "dépendance générale code-biominéralisation, sans causalité historique directe"),
        ("TR-039", "TR-040", "Plausible",
         "endosymbiose vers multicellularité"),
        ("TR-017", "TR-018", "Établi",
         "incorporation CAI-chondres établie comme trace, non comme causalité"),
        ("TR-036", "TR-037", "Fortement inféré",
         "code avant LUCA, reconstruit"),
        ("TR-023", "TR-025", "Hypothétique",
         "hydrosphère vers tectonique"),
    ],
)
def test_niveaux_de_preuve_verrouilles(liens, source, cible, niveau_attendu, motif) -> None:
    par_paire = {(l["source"], l["target"]): l for l in liens}
    assert (source, cible) in par_paire, f"Lien absent : {source} -> {cible} ({motif})"
    assert par_paire[(source, cible)]["niveau_preuve"] == niveau_attendu, motif


@pytest.mark.parametrize("triplet", [
    ("TR-002", "TR-004", "CNST"),
    ("TR-017", "TR-018", "INCO"),
    ("TR-023", "TR-025", "CONT"),
    ("TR-036", "TR-030", "DEPG"),
    ("TR-037", "TR-038", "DESC"),
    ("TR-037", "TR-039", "DESC"),
    ("TR-029", "TR-038", "FEED"),
])
def test_liens_revises_presents(liens, triplet) -> None:
    assert triplet in {(l["source"], l["target"], l["relation"]) for l in liens}


@pytest.mark.parametrize("paire", [("TR-002", "TR-003"), ("TR-017", "TR-020")])
def test_liens_supprimes_ne_reapparaissent_pas(liens, paire) -> None:
    assert paire not in {(l["source"], l["target"]) for l in liens}


def test_les_codes_non_causaux_portent_une_limite_explicite(liens) -> None:
    """INCO, DESC et DEPG ne décrivent pas une causalité historique."""
    non_causaux = [l for l in liens if l["relation"] in {"INCO", "DESC", "DEPG"}]
    assert len(non_causaux) == 4
    for l in non_causaux:
        assert len(l["limite_interpretative"].strip()) > 30, (
            f"Limite interprétative trop maigre pour {l['source']} -> {l['target']}"
        )


def test_les_liens_hypothetiques_restent_marginaux(liens) -> None:
    """Une carte majoritairement hypothétique ne serait pas présentable."""
    hypothetiques = sum(1 for l in liens if l["niveau_preuve"] == "Hypothétique")
    assert hypothetiques == 2
    etablis = sum(1 for l in liens if l["niveau_preuve"] == "Établi")
    assert etablis >= hypothetiques * 4


# --- Matrice dérivée -------------------------------------------------------
def test_matrice_coherente_avec_les_liens(racine, liens, noeuds) -> None:
    chemin = racine / "carte_relationnelle/resultats/matrice_relations_oric_47.csv"
    lignes = lire_csv(chemin)
    identifiants = [n["id"] for n in noeuds]
    assert len(lignes) == 40
    entetes = [c for c in lignes[0] if c != "source\\target"]
    assert entetes == identifiants
    attendu = {(l["source"], l["target"]): l["relation"] for l in liens}
    trouve = {
        (ligne["source\\target"], cible): valeur
        for ligne in lignes
        for cible, valeur in ligne.items()
        if cible != "source\\target" and (valeur or "").strip()
    }
    assert trouve == attendu


# --- Audit dérivé ----------------------------------------------------------
def test_audit_reprend_les_comptes_reels(racine, liens, noeuds) -> None:
    texte = (racine / "carte_relationnelle/resultats/audit_carte_relationnelle_oric_47.txt").read_text(
        encoding="utf-8"
    )
    assert f"Transitions : {len(noeuds)}" in texte
    assert f"Liens typés : {len(liens)}" in texte
    assert "Cycles hors FEED : 0" in texte
    assert f"Liens avec référence clé jointe : {len(liens)}/{len(liens)}" in texte
    for code, compte in REPARTITION_ATTENDUE.items():
        assert f"{code}: {compte}" in texte, f"Répartition {code} absente de l'audit."


# ---------------------------------------------------------------------------
# Fermetures et recodages en attente
# ---------------------------------------------------------------------------

def test_les_fermetures_declarees_sont_substantielles(noeuds) -> None:
    """`domaine_ferme` est facultatif, mais jamais bâclé quand il est rempli."""
    maigres = [
        ligne["id"] for ligne in noeuds
        if ligne["domaine_ferme"] and len(ligne["domaine_ferme"]) < 25
    ]
    assert not maigres, f"Fermetures trop vagues : {maigres}"


def test_au_moins_une_fermeture_est_documentee(noeuds) -> None:
    """Le cadre inscrit ΔF dans sa signature ; la carte doit en porter la trace."""
    renseignees = [ligne["id"] for ligne in noeuds if ligne["domaine_ferme"]]
    assert renseignees, (
        "Aucune fermeture documentée alors que le codebook définit ΔF."
    )


def test_tout_recodage_est_justifie(liens) -> None:
    """Un écart entre `relation` et `code_cible` exige une note."""
    sans_note = [
        (ligne["source"], ligne["target"])
        for ligne in liens
        if ligne["code_cible"] != ligne["relation"] and not ligne["note_codage"]
    ]
    assert not sans_note, f"Recodages sans justification : {sans_note}"


def test_les_codes_cibles_appartiennent_au_vocabulaire(liens) -> None:
    vocabulaire = {
        "ENBL", "MATR", "ENVR", "STAB", "CATL", "CNST",
        "CONT", "DEPG", "INCO", "DESC", "FEED", "CLOS", "INTG",
    }
    inconnus = sorted(
        {ligne["code_cible"] for ligne in liens} - vocabulaire
    )
    assert not inconnus, f"Codes cibles hors vocabulaire : {inconnus}"


def test_la_note_de_regeneration_liste_les_ecarts(liens, racine) -> None:
    """Aucun écart ne doit rester silencieux."""
    note = (racine / "carte_relationnelle" / "REGENERATION_REQUISE.md").read_text(
        encoding="utf-8"
    )
    for ligne in liens:
        if ligne["code_cible"] != ligne["relation"]:
            couple = f"{ligne['source']} → {ligne['target']}"
            assert couple in note, f"Écart non listé dans la note : {couple}"
