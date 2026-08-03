"""Protège ce que la généalogie annotée porte et que l'hypergraphe n'a pas."""
import csv
import json
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DOSSIER = Path(__file__).resolve().parents[3]
ANTERIEURE = DOSSIER / "01_branche_matiere" / "genealogie"

CHAMPS_PROPRES = (
    "conditions_permissives", "inventaire_accessible", "mecanisme_categorie",
    "possibilites_ouvertes", "possibilites_fermees", "epoque", "milieu",
    "preuve_experimentale", "preuve_observationnelle",
    "transformations_intermediaires", "proprietes_nouvelles",
    "conditions_necessaires", "transition_suivante",
)

# Les quatre axes de certitude remplacent la colonne unique. Ils empechent
# d'attribuer un statut eleve a une voie historique au seul motif que le
# mecanisme existe en laboratoire.
AXES_DE_CERTITUDE = (
    "preuve_du_mecanisme", "preuve_en_milieu_naturel",
    "preuve_de_la_transition_historique", "certitude_du_role_causal",
)

# Ce qui rend possible sans etre incorpore. Aucune de ces entrees ne peut
# figurer comme parent materiel.
CONDITIONS = {
    "gravité", "flux ultraviolet", "flux XUV stellaire", "chocs",
    "refroidissement par H2", "refroidissement par HD", "aucune",
    "énergie hydrothermale", "cycles humide-sec", "turbulence du disque",
    "piège à pression", "expansion cosmologique", "seuil de Roche",
    "fugacité d'oxygène", "circulation hydrothermale", "dissipation du disque",
    "rayonnement cosmique",
}


def lire(chemin):
    with Path(chemin).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def arbre():
    return lire(RACINE / "arbre_genealogique.csv")


def test_les_treize_champs_propres_sont_tous_renseignes():
    lignes = arbre()
    assert len(lignes) >= 38
    for l in lignes:
        for champ in CHAMPS_PROPRES:
            assert l[champ].strip(), f"{l['id']} : {champ} vide"


def test_les_quatre_axes_de_certitude_sont_renseignes():
    for l in arbre():
        for axe in AXES_DE_CERTITUDE:
            assert l[axe].strip(), f"{l['id']} : {axe} vide"


def test_aucune_condition_permissive_en_parent_materiel():
    """Le dihydrogene refroidit les premiers nuages ; les etoiles n'en sont
    pas faites. La gravite effondre un nuage ; rien n'est fait de gravite."""
    for l in arbre():
        for parent in (p.strip() for p in l["parents_materiels"].split("|")):
            assert parent not in CONDITIONS, f"{l['id']} : « {parent} »"


def test_aluminium_26_separe_des_actinides():
    """Les deux voies de production sont distinctes et ne doivent pas etre
    regroupees sous une capture neutronique unique."""
    par_produit = {l["produit"]: l for l in arbre()}
    assert "actinides" in par_produit
    assert "aluminium 26" in par_produit
    assert par_produit["actinides"]["mecanisme_categorie"] == "capture_neutronique"
    assert par_produit["aluminium 26"]["mecanisme_categorie"] != "capture_neutronique"


def test_cloture_genealogique_exportee():
    d = json.loads((RACINE / "cloture_arbre.json").read_text(encoding="utf-8"))
    assert d["cloture_genealogique"] is True
    assert d["anomalies"] == []
    assert d["transitions"] == len(arbre())


def test_possibilites_fermees_sont_le_terme_de_la_chaine_ORI_C():
    """Aucun autre fichier du dossier n'instancie ce champ."""
    portantes = [l for l in arbre()
                 if l["possibilites_fermees"].strip().lower() != "aucune"]
    assert len(portantes) >= 15, "trop peu de fermetures effectives"


def test_correspondance_avec_la_genealogie_anterieure_publiee():
    """La table de correspondance rend l'equivalence explicite au lieu de la
    laisser implicite."""
    m = lire(RACINE / "correspondance_GM_GA.csv")
    assert len(m) >= 20
    ids = {l["id"] for l in arbre()}
    for l in m:
        for cible in (c.strip() for c in l["id_ga"].split("|") if c.strip()):
            assert cible in ids or cible == "-", f"cible inconnue : {cible}"


def test_genealogie_anterieure_conservee_et_signalee():
    """La version anterieure traite `gravite` comme une entree externe. Elle
    est conservee pour tracabilite ; ce test verrouille le fait que le defaut
    est dans l'archive et non dans la version courante."""
    lignes = lire(ANTERIEURE / "genealogie_matiere.csv")
    produits = {l["produit"] for l in lignes}
    externes = {p.strip() for l in lignes
                for p in l["parents_materiels"].split("|")
                if p.strip() and p.strip() not in produits}
    # Le defaut est bien confine a la version anterieure. Le controle porte
    # sur le CSV et non sur le rapport, qui ne l'expose plus.
    assert externes & CONDITIONS, (
        "le defaut a disparu de l'archive : ce test doit etre retire")
    assert (ANTERIEURE / "archives_non_probantes").is_dir()
    # Et il ne doit surtout pas etre remonte dans la version courante.
    courants = {p.strip() for l in arbre()
                for p in l["parents_materiels"].split("|")}
    assert not (courants & CONDITIONS)
