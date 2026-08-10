"""Vérification des documents : article, cas exoplanétaires, deux schémas PDF."""
from __future__ import annotations

import pytest
fitz = pytest.importorskip("fitz", reason="PyMuPDF requis uniquement pour les contrôles PDF")


def apostrophes_uniformes(texte: str) -> str:
    """L'article mêle apostrophes droites et typographiques ; on les unifie."""
    return texte.replace("’", "'").replace("ʼ", "'")


PHRASES_REQUISES = [
    "La bifurcation biologique correspond au passage de modes de persistance liés, métastables ou dissipatifs",
    "La rupture se situe dans l’intégration progressive de mécanismes énergétiques, organisationnels et héréditaires",
    "La sélection cumulative n’est donc pas un mécanisme interne de réparation de l’organisme",
    "Hiérarchie conceptuelle retenue",
    "6.5 Information reconstructive",
    "6.6 Information symbolique et culturelle",
    "7. Le code génétique comme stabilisateur et amplificateur de la persistance reconstructive",
    "Le code génétique consolide un régime dans lequel une mémoire nucléotidique transmissible peut orienter la synthèse protéique",
    "Les composantes reconstructive, reproductive et évolutive ne désignent pas trois degrés interchangeables",
    "Tableau synthétique des composantes du vecteur Π",
    "L’histoire matérielle de l’Univers peut être lue comme une sculpture progressive des possibles",
]
FORMULATIONS_PROSCRITES = [
    "7. Le code génétique comme rupture historiquement stabilisée",
    "Cette chronologie peut être lue comme une sculpture historique des possibles",
]


# --- Article ---------------------------------------------------------------
@pytest.mark.parametrize("phrase", PHRASES_REQUISES)
def test_correction_conceptuelle_presente(article_texte: str, phrase: str) -> None:
    assert apostrophes_uniformes(phrase) in apostrophes_uniformes(article_texte)


@pytest.mark.parametrize("formulation", FORMULATIONS_PROSCRITES)
def test_ancienne_formulation_absente(article_texte: str, formulation: str) -> None:
    assert apostrophes_uniformes(formulation) not in apostrophes_uniformes(article_texte)


def test_tableau_de_persistance_unique(article_docx) -> None:
    entetes = ("Composante", "Échelle", "Mécanismes principaux", "Effet sur la continuité")
    tableaux = [
        table for table in article_docx.tables
        if len(table.rows) == 4 and len(table.columns) == 4
        and tuple(table.cell(0, i).text.strip() for i in range(4)) == entetes
    ]
    assert len(tableaux) == 1


def test_la_divergence_planetaire_n_est_plus_nommee_polygenese(article_texte: str) -> None:
    """Le terme reste employé, mais l'article doit récuser cet usage précis.

    Le README annonce que « la divergence planétaire n'est plus appelée
    polygenèse » : c'est la dénégation explicite qui est vérifiée ici, pas
    l'absence du mot, qui reste nécessaire pour distinguer les notions.

    La comparaison neutralise les apostrophes : l'article mêle apostrophes
    droites et typographiques d'un paragraphe à l'autre.
    """
    texte = apostrophes_uniformes(article_texte)
    for enonce in (
        "La divergence de planètes appartenant à un même système n’est pas une polygenèse.",
        "divergence historique intra-système, et non une polygenèse",
        "d’éviter d’appeler polygenèse toute divergence ou toute répétition",
    ):
        assert apostrophes_uniformes(enonce) in texte, f"Dénégation absente : {enonce}"


def test_les_quatre_regimes_de_repetabilite_restent_distingues(article_texte: str) -> None:
    """Récurrence, convergence et origines multiples ne doivent pas être confondues."""
    for notion in ("récurrence physicochimique", "convergence", "origines évolutives multiples"):
        assert notion.lower() in article_texte.lower(), f"Notion absente : {notion}"


def test_l_article_ne_presente_pas_la_carte_comme_causale_demontree(article_texte: str) -> None:
    assert "graphe causal entièrement démontré" not in article_texte


def test_note_d_integration_presente(racine) -> None:
    chemin = racine / "note_integration/Note_integration_ORI-C.docx"
    assert chemin.exists() and chemin.stat().st_size > 0


# --- Cas exoplanétaires ----------------------------------------------------
def test_ordre_des_cas_exoplanetaires(exoplanetes) -> None:
    assert [ligne["cas"] for ligne in exoplanetes] == ["TRAPPIST-1d", "TRAPPIST-1e", "55 Cancri e"]


def test_trappist_1e_reste_indeterminee(exoplanetes) -> None:
    ligne = next(l for l in exoplanetes if l["cas"] == "TRAPPIST-1e")
    assert ligne["statut"] == "Indéterminé"
    assert "Aucune atmosphère secondaire" in ligne["limite"]


def test_aucune_hydrosphere_exoplanetaire_affirmee(exoplanetes) -> None:
    """Le README pose que les hydrosphères exoplanétaires restent hypothétiques."""
    for ligne in exoplanetes:
        assert "océan détecté" not in ligne["observation"].lower()
        assert "hydrosphère confirmée" not in ligne["valeur_ori_c"].lower()


def test_chaque_cas_porte_limite_et_reference(exoplanetes) -> None:
    for ligne in exoplanetes:
        assert ligne["limite"].strip(), f"Limite absente pour {ligne['cas']}"
        assert ligne["reference"].strip(), f"Référence absente pour {ligne['cas']}"
        assert ligne["mode_preuve"].strip()


# --- Les deux schémas restent séparés --------------------------------------
@pytest.fixture(scope="module")
def carte_detaillee(racine):
    document = fitz.open(racine / "carte_relationnelle/resultats/carte_relationnelle_oric_47_complete.pdf")
    yield document
    document.close()


@pytest.fixture(scope="module")
def schema_synthetique(racine):
    document = fitz.open(racine / "schema_synthetique/ORI-C_carte_relationnelle_TR001_TR040_stabilisee.pdf")
    yield document
    document.close()


def test_carte_detaillee_sept_pages(carte_detaillee) -> None:
    assert carte_detaillee.page_count == 7


def test_schema_synthetique_une_page(schema_synthetique) -> None:
    assert schema_synthetique.page_count == 1


def test_premiere_page_de_la_carte_detaillee_intacte(carte_detaillee) -> None:
    assert "Carte relationnelle de travail ORI-C" in carte_detaillee[0].get_text("text")


def test_le_schema_synthetique_n_est_pas_incorpore_a_la_carte(carte_detaillee) -> None:
    """Interdiction explicite du README : les deux schémas ne fusionnent pas."""
    texte = "\n".join(page.get_text("text") for page in carte_detaillee)
    assert "Carte relationnelle des architectures de la matière" not in texte


def test_la_carte_detaillee_n_est_pas_incorporee_au_schema(schema_synthetique) -> None:
    assert "Carte relationnelle de travail ORI-C" not in schema_synthetique[0].get_text("text")


@pytest.mark.parametrize("etiquette", [
    "Carte relationnelle des architectures de la matière",
    "R7 — Zone d’intégration progressive vers la persistance reconstructive",
    "R8 — Persistance biologique active et évolution cumulative",
])
def test_etiquettes_du_schema_synthetique(schema_synthetique, etiquette: str) -> None:
    assert etiquette in schema_synthetique[0].get_text("text")


def test_les_deux_pdf_ne_sont_pas_le_meme_fichier(racine) -> None:
    from conftest import sha256

    a = sha256(racine / "carte_relationnelle/resultats/carte_relationnelle_oric_47_complete.pdf")
    b = sha256(racine / "schema_synthetique/ORI-C_carte_relationnelle_TR001_TR040_stabilisee.pdf")
    assert a != b


def test_les_pdf_s_ouvrent_sans_page_vide(carte_detaillee, schema_synthetique) -> None:
    for document in (carte_detaillee, schema_synthetique):
        for index, page in enumerate(document):
            a_du_texte = bool(page.get_text("text").strip())
            a_du_dessin = bool(page.get_drawings()) or bool(page.get_images())
            assert a_du_texte or a_du_dessin, f"Page {index + 1} vide dans {document.name}"


def test_les_47_liens_figurent_au_registre(carte_detaillee, liens) -> None:
    """Le registre annexé doit citer chaque transition source et cible."""
    texte = "\n".join(page.get_text("text") for page in carte_detaillee)
    absents = sorted(
        {identifiant for l in liens for identifiant in (l["source"], l["target"])
         if identifiant not in texte}
    )
    assert not absents, f"Transitions absentes du document complet : {absents}"
