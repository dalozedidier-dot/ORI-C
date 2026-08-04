import pytest
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def lire(nom):
    with (ROOT / nom).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))

def test_identifiants_et_sources():
    nodes = lire("noeuds.csv"); edges = lire("hyperaretes.csv"); sources = lire("sources.csv")
    ids = {x["node_id"] for x in nodes}; sids = {x["source_id"] for x in sources}
    assert len(ids) == len(nodes)
    assert len({x["edge_id"] for x in edges}) == len(edges)
    for e in edges:
        assert set(e["entrees"].split("|")) <= ids
        assert set(e["sorties"].split("|")) <= ids
        assert e["source_id"] in sids

def test_structure_non_lineaire_et_scenarios():
    edges = lire("hyperaretes.csv")
    assert sum(len(e["entrees"].split("|")) > 1 for e in edges) >= 20
    assert sum(len(e["sorties"].split("|")) > 1 for e in edges) >= 10
    assert any(e["type"] == "recyclage" for e in edges)
    assert sum("scenario" in e["statut_preuve"] or "hypothese" in e["statut_preuve"] for e in edges) >= 4

def test_continuite_de_la_projection_paire_a_paire():
    edges = lire("hyperaretes.csv")
    adj = {}
    for e in edges:
        for a in e["entrees"].split("|"):
            adj.setdefault(a, set()).update(e["sorties"].split("|"))
    vus={"N036"}; pile=["N036"]
    while pile:
        for b in adj.get(pile.pop(), ()):
            if b not in vus: vus.add(b); pile.append(b)
    assert "N035" in vus

def test_validation_exportee():
    d=json.loads((ROOT/"validation_hypergraphe.json").read_text(encoding="utf-8"))
    assert d["status"] == "valid_with_strict_closure_gap"
    for key in (
        "not_a_linear_tree", "all_endpoints_exist", "all_edges_sourced",
        "competing_scenarios_explicit", "four_relation_families_represented",
        "single_declared_root", "pairwise_projection_connected",
    ):
        assert d["tests"][key]
    assert d["tests"]["strict_hypergraph_closed"] is False

def test_fermeture_stricte_distinguee_de_la_projection():
    """La projection connectee ne doit plus masquer une boucle multi-entrees.

    La chaîne N029/N030/N053/N054 s'auto-entretient dans la projection, car
    chaque entrée y est traitée comme suffisante. La fermeture stricte exige
    toutes les entrées et laisse sept nœuds inatteignables.
    """
    d=json.loads((ROOT/"validation_hypergraphe.json").read_text(encoding="utf-8"))
    assert d["declared_roots"] == ["N036"]
    assert d["pairwise_projection"]["nodes_reachable_from_root"] == 53
    assert d["pairwise_projection"]["unreachable_nodes"] == []
    assert d["strict_hypergraph_closure"]["nodes_reachable_from_root"] == 46
    assert d["strict_hypergraph_closure"]["unreachable_nodes"] == [
        "N029", "N030", "N031", "N032", "N035", "N053", "N054"
    ]

def test_echelle_des_capacites_complete():
    for n in lire("noeuds.csv"):
        assert 1 <= int(n["niveau_capacite"]) <= 10, n["node_id"]

def test_role_genealogique_declare():
    roles = {"progression", "retour", "emission"}
    for e in lire("hyperaretes.csv"):
        assert e["role_genealogique"] in roles, e["edge_id"]

@pytest.mark.xfail(strict=True, reason=(
    "Monotonie refutee, et non retablissable par reetiquetage. Une production "
    "pointe toujours vers le bas : une etoile de niveau 6 produit des elements "
    "de niveau 1, un systeme hydrothermal de niveau 9 produit des especes "
    "mobiles de niveau 8. L'echelle ordonne des objets, pas des processus. "
    "Le test est conserve en echec declare : il enonce ce qui a ete refute, "
    "au lieu de le faire disparaitre. Voir test_hierarchie_execution_1_"
    "prereglee.json pour l'execution preenregistree."))
def test_monotonie_des_capacites_sur_les_aretes_de_progression():
    niveau = {n["node_id"]: int(n["niveau_capacite"]) for n in lire("noeuds.csv")}
    for e in lire("hyperaretes.csv"):
        if e["role_genealogique"] != "progression":
            continue
        ins, outs = e["entrees"].split("|"), e["sorties"].split("|")
        partage = set(ins) & set(outs)
        for a in ins:
            for b in outs:
                if a == b or a in partage or b in partage:
                    continue
                assert niveau[b] >= niveau[a], f"{e['edge_id']} {a}->{b}"

def test_echelle_porte_de_l_information_au_dela_de_la_profondeur():
    """Le resultat qui, lui, tient : le gain depasse le tirage par permutation.

    Les six dimensions portaient 0,000 bit. L'echelle en porte pres de 0,6 net
    du bruit de petit effectif, avec un rho de 0,74 : correlee a la profondeur
    sans lui etre redondante.
    """
    b = json.loads((ROOT / "test_hierarchie_resultats.json").read_text(
        encoding="utf-8"))["test_B_information"]
    assert b["gain_observe_bits"] > b["gain_moyen_sous_permutation_bits"]
    assert b["gain_net_du_bruit_bits"] > 0.3
    assert b["p_par_permutation"] < 0.001
    assert b["spearman_niveau_profondeur"] < 0.95, "sinon l echelle recopie la profondeur"

def test_inventaire_accessible_sans_imputation():
    """Aucun inventaire accessible chiffre sans ses deux facteurs.

    Ce controle avait attrape une probabilite de transfert posee a zero pour
    le noyau : « aucun mecanisme de retour connu » n'est pas un zero mesure.
    """
    sids = {s["source_id"] for s in lire("sources.csv")}
    for l in lire("inventaire_accessible.csv"):
        assert l["source"] in sids, l["record_id"]
        if l["inventaire_accessible"]:
            assert l["fraction_mobilisable"] and l["probabilite_transfert"], \
                l["record_id"]

def test_bouclage_des_budgets_publies():
    """Noyau + silicate doit reconstituer le total publie independamment."""
    d=json.loads((ROOT/"inventaire_accessible_resultats.json").read_text(
        encoding="utf-8"))
    assert d["statut"] == "valide" and not d["erreurs"]
    assert d["bouclage_integralement_verifie"]
    assert d["bouclage_ecart_maximal"] < 0.05

def test_coefficients_de_partage_sources_et_bornes_declarees():
    sids = {s["source_id"] for s in lire("sources.csv")}
    for c in lire("coefficients_partage.csv"):
        assert c["source"] in sids, c["record_id"]
        assert float(c["D_metal_sur_silicate"]) > 0, c["record_id"]
        assert c["type_de_valeur"] in {"point", "borne_inferieure",
                                       "borne_superieure"}, c["record_id"]

def test_les_coefficients_predisent_la_repartition_sauf_pour_le_soufre():
    """Epreuve independante : laboratoire d'un cote, budgets geochimiques de
    l'autre, aucune circularite.

    Trois elements sur quatre recouvrent. Le soufre est en desaccord, et ce
    desaccord n'est pas un artefact : la source des coefficients conclut
    elle-meme a un noyau pauvre en soufre, contre l'estimation classique de
    1,8 wt% tiree de la tendance de volatilite. Le controle retrouve donc une
    tension publiee sans l'avoir cherchee.
    """
    d = json.loads((ROOT / "inventaire_accessible_resultats.json").read_text(
        encoding="utf-8"))
    p = d["prediction_par_les_coefficients_de_partage"]
    assert set(d["elements_ou_la_prediction_recouvre_l_observation"]) == {
        "C", "H", "N"}
    assert d["elements_en_desaccord"] == ["S"]
    # Une borne inferieure publiee doit rester ouverte vers le haut : la
    # traiter comme un point fabriquait un desaccord inexistant sur H.
    assert p["H"]["borne_superieure_ouverte"]
    assert p["H"]["rapport_de_masses_attendu"][1] is None

def test_filtre_nc_cc_parametre():
    lignes = lire("filtre_nc_cc.csv")
    attributs = {l["attribut"] for l in lignes}
    for requis in ("debut_de_la_separation", "fin_de_la_separation",
                   "degre_de_permeabilite", "taille_franchissant_le_filtre",
                   "date_de_formation_des_corps_parents_NC"):
        assert requis in attributs, requis
    # Le mecanisme reste ouvert : plusieurs scenarios doivent coexister.
    assert sum(a.startswith("mecanisme_propose") for a in attributs) >= 3
