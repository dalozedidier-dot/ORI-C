"""Verrouille ce que l'inventaire hierarchique annonce.

Les effectifs sont ecrits dans la note de lecture du classeur. S'ils divergent
des feuilles, l'annonce est fausse : c'est le premier controle. Les suivants
portent sur la cloture de la hierarchie, le sourcage, et la separation entre
entites confirmees et hypotheses.
"""
import csv
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
TABLES = RACINE / "tables"

# Effectifs annonces par la note de lecture du classeur.
ANNONCES = {
    "03_Particules_fond": 18, "04_Composites": 56, "05_Nuclides_NUBASE": 5843,
    "06_Elements_118": 118, "07_Molecules": 70, "08_Phases": 53,
    "09_Materiaux": 77, "10_Reservoirs": 46, "11_Biologique": 43,
    "12_Inconnus": 16, "13_Transformations": 52, "01_Index_maitre": 550,
    "14_Sources": 10, "02_Hierarchie": 25,
}
TOTAL_DETAILLE = 6392


def lire(nom):
    with (TABLES / f"{nom}.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def test_les_effectifs_annonces_correspondent_aux_feuilles():
    for nom, attendu in ANNONCES.items():
        assert len(lire(nom)) == attendu, nom


def test_le_total_detaille_est_exact():
    detail = [n for n in ANNONCES
              if n not in ("01_Index_maitre", "02_Hierarchie", "14_Sources")]
    assert sum(len(lire(n)) for n in detail) == TOTAL_DETAILLE


def test_la_hierarchie_est_close():
    """Tout parent declare doit exister comme noeud, sauf la racine."""
    lignes = lire("02_Hierarchie")
    ids = {l["ID"] for l in lignes if l["ID"]}
    for l in lignes:
        parent = (l.get("Parent ID") or "").strip()
        if parent and parent in ids:
            continue
        # La racine porte un libelle et non un identifiant de parent.
        assert not parent or parent not in ids or l["ID"] == "U00", l["ID"]
    racines = [l["ID"] for l in lignes if (l.get("Parent ID") or "") not in ids]
    assert len(racines) == 1, f"racines multiples : {racines}"


def test_chaque_entree_porte_une_source():
    for nom in ("03_Particules_fond", "07_Molecules", "09_Materiaux",
                "13_Transformations"):
        lignes = lire(nom)
        colonne = next(c for c in lignes[0] if "url" in c.lower())
        vides = [l for l in lignes if not (l[colonne] or "").strip()]
        assert not vides, f"{nom} : {len(vides)} lignes sans source"


def test_aucun_candidat_presente_comme_confirme():
    """Aucun candidat ni aucune entite exotique ne doit porter « confirme ».

    La feuille contient deux lignes de reference legitimement confirmees, la
    matiere baryonique ordinaire et la matiere noire inferee, qui servent de
    comparaison. Le controle porte sur les categories de candidats, pas sur la
    feuille entiere : c'est la que la confusion serait grave.
    """
    lignes = lire("12_Inconnus")
    cat = next(iter(lignes[0]))
    colonne = next(c for c in lignes[0] if c.lower().startswith("statut"))
    candidats = [l for l in lignes
                 if "candidat" in (l[cat] or "").lower()
                 or "exotique" in (l[cat] or "").lower()
                 or "sombre" in (l[cat] or "").lower()]
    assert len(candidats) >= 12, "la feuille ne contient plus de candidats"
    for l in candidats:
        statut = (l[colonne] or "").lower()
        assert not statut.startswith("confirm"), l["Nom"]


def test_la_matiere_noire_reste_inferee_et_non_identifiee():
    """Sa distribution est etablie, sa composition microscopique ne l'est pas.
    Confondre les deux serait l'erreur exacte que la feuille evite."""
    lignes = lire("12_Inconnus")
    colonne = next(c for c in lignes[0] if c.lower().startswith("statut"))
    noire = next(l for l in lignes if l["Nom"].strip() == "Matière noire")
    assert "infér" in (noire[colonne] or "").lower()


def test_les_sources_sont_datees_et_adressables():
    for s in lire("14_Sources"):
        assert (s["URL"] or "").startswith("http"), s["ID"]
        assert (s["Date de consultation"] or "").startswith("2026"), s["ID"]


def test_les_niveaux_exhaustifs_sont_declares_comme_tels():
    """Trois niveaux seulement s'appuient sur un registre ferme ou evalue.
    Les autres sont ouverts, et le fichier ne doit pas pretendre les clore."""
    lecture = " ".join(
        " ".join(v or "" for v in l.values()) for l in lire("00_Lecture"))
    assert "Exhaustif" in lecture or "exhaustif" in lecture
    assert "ouvert" in lecture.lower()


def test_le_detecteur_de_manques_produit_un_rapport_exploitable():
    """L'inventaire sert a reperer ce que la genealogie ne sait pas produire.

    L'appariement transformation -> mecanisme est declare a la main. Toute
    transformation non appariee est une erreur de saisie, pas un manque : le
    test l'interdit pour que les deux ne soient jamais confondus.
    """
    import json
    d = json.loads((RACINE / "manques_detectes.json").read_text(encoding="utf-8"))
    assert d["B_transformations"]["transformations_non_appariees"] == []
    assert d["B_transformations"]["transformations_recensees"] == 52
    # Les quatre transformations propres au programme restent a instancier.
    oric = d["B_transformations"]["transformations_sans_mecanisme"].get(
        "Échelle ORI-C", [])
    assert len(oric) == 4, "si elles sont instanciees, mettre ce test a jour"


# --- Couche transversale d'analyse et registres canoniques -----------------

def test_la_couche_analyse_relie_a_l_index_maitre():
    """Chaque fiche doit pointer vers une entree reelle de l'index."""
    fiches = lire("15_Analyse_ORI-C")
    ids = {l["ID"] for l in lire("01_Index_maitre")}
    assert len(fiches) >= 20
    for f in fiches:
        assert f["ID_index"] in ids, f["ID_analyse"]


def test_la_profondeur_du_cadre_est_declaree_et_non_supposee():
    """Pour une particule fondamentale, m et A ne sont pas definis dans le
    modele courant. La colonne le dit, au lieu de laisser des cases vides."""
    fiches = lire("15_Analyse_ORI-C")
    valides = {"nulle", "partielle", "complete"}
    for f in fiches:
        assert f["Profondeur"] in valides, f["ID_analyse"]
    assert any(f["Profondeur"] == "nulle" for f in fiches)
    assert sum(1 for f in fiches if f["Profondeur"] == "complete") >= 12


def test_les_champs_Z_sont_tous_renseignes():
    for f in lire("15_Analyse_ORI-C"):
        for champ in ("Y observe", "X etat courant", "A organisation",
                      "Persistance", "Z accessible", "Verrous",
                      "Intervention", "Certitude"):
            assert f[champ].strip(), f"{f['ID_analyse']} : {champ}"
        # m peut etre declare absent, mais jamais laisse vide.
        assert f["m histoire incorporee"].strip(), f["ID_analyse"]


def test_un_identifiant_designe_une_seule_chose():
    """Une relation, une condition ou une transformation ne doit jamais etre
    encodee comme si elle etait une matiere."""
    index = lire("01_Index_maitre")
    assert all(r["type_registre"] for r in index)
    prefixes = {"ENT", "NUC", "PHA", "MAT", "RES", "BIO", "UNK", "TRF"}
    assert {r["type_registre"] for r in index} <= prefixes
    for r in lire("17_Relations_REL"):
        assert r["relation_id"].startswith("REL-")
    for c in lire("16_Conditions_CON"):
        assert c["condition_id"].startswith("CON-")


def test_les_registres_sont_peuples_et_non_des_schemas_vides():
    assert len(lire("16_Conditions_CON")) >= 50
    assert len(lire("17_Relations_REL")) >= 100
    assert len(lire("18_Preuves_PRV")) >= 150


def test_chaque_transition_porte_ses_quatre_axes_de_preuve():
    preuves = lire("18_Preuves_PRV")
    from collections import Counter
    par_cible = Counter(p["cible_id"] for p in preuves)
    assert par_cible and set(par_cible.values()) == {4}


# --- Carte causale ---------------------------------------------------------

def test_les_contrastes_controlent_bien_une_variable():
    """Un contraste utile tient la composition fixe et fait varier une seule
    chose : l'architecture, l'histoire ou les conditions."""
    import json
    d = json.loads((RACINE / "carte_causale.json").read_text(encoding="utf-8"))
    a = d["A_contrastes_a_composition_constante"]
    assert a["nombre"] >= 8
    for c in a["contrastes"]:
        assert c["ce_qui_varie"] in {"architecture", "histoire", "conditions"}
        assert c["observables_discriminants"].strip()
        assert c["proposition_testee"].strip()
        assert c["cas_1"] != c["cas_2"]


def test_chaque_lien_candidat_est_type_et_justifie():
    import json
    d = json.loads((RACINE / "carte_causale.json").read_text(encoding="utf-8"))
    b = d["B_liens_causaux_candidats"]
    for l in b["liens"]:
        assert l["type"] in b["vocabulaire"], l
        assert l["justification"].strip()
    # Le typage doit rester varie : un vocabulaire employe a un seul code
    # ne distingue rien.
    assert len(b["par_type"]) >= 8


def test_les_liens_candidats_restent_hors_du_graphe_canonique():
    """Ils ne doivent pas etre confondus avec les relations sourcees."""
    import json
    d = json.loads((RACINE / "carte_causale.json").read_text(encoding="utf-8"))
    assert "candidats" in d["B_liens_causaux_candidats"]["statut"]
    canon = lire("17_Relations_REL")
    candidats = {l["source"] for l in d["B_liens_causaux_candidats"]["liens"]}
    assert not candidats & {r["source_libelle"] for r in canon}


def test_les_motifs_transversaux_traversent_plusieurs_echelles():
    import json
    d = json.loads((RACINE / "carte_causale.json").read_text(encoding="utf-8"))
    for m in d["D_motifs_transversaux"]["motifs"]:
        assert len(m["occurrences"]) >= 3, m["motif"]
    assert "pas identite de mecanisme" in d["D_motifs_transversaux"]["avertissement"]
