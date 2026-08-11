"""Carte causale des architectures, des transitions et des lacunes.

L'inventaire cesse d'etre une liste des que chaque entree est lue sous le cadre.
Ce script produit quatre analyses qui n'existaient pas :

    A  Contrastes a composition constante. Ce sont les seuls cas experimentaux
       ou l'on tient la composition fixe et fait varier l'architecture ou
       l'histoire. Ils testent la proposition centrale au lieu de l'illustrer.

    B  Liens causaux candidats types. Un lien n'est plus « A est associe a B »
       mais une relation qualifiee : transmission materielle, condition
       permissive, stabilisation, catalyse, contrainte, inscription,
       retroaction, fermeture, integration, dependance.

    C  Familles d'architectures sous-representees dans la genealogie.
       L'inventaire recense des regimes de matiere organisee que les trente-neuf
       transitions ne couvrent pas.

    D  Motifs structurels transversaux. Des transformations architecturales
       identiques par leur grammaire reapparaissent a des echelles physiques
       sans rapport. Ce n'est pas une identite de mecanisme, c'est une identite
       de forme, et elle rend des domaines comparables sans les confondre.

Les liens de B restent hors du graphe canonique tant que leur mecanisme, leur
occurrence naturelle, leur trajectoire historique et leur role causal ne sont
pas sources separement. Ils sont candidats, pas acquis.

    python carte_causale.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ICI = Path(__file__).resolve().parent
TABLES = ICI / "tables"
ARBRE = ICI.parents[1] / "00_socle" / "genealogie" / "arbre_genealogique.csv"

# --- A. Contrastes a composition constante --------------------------------
# Chaque paire tient X constant et fait varier A ou m. La colonne `teste`
# indique la proposition que le contraste met a l'epreuve.
CONTRASTES = [
 ("C", "Diamant", "Graphite", "architecture",
  "reseau covalent tridimensionnel contre feuillets empiles",
  "durete, conductivite, transparence, domaine de stabilite",
  "la composition seule ne determine pas les proprietes"),
 ("CaCO3", "Calcite", "Aragonite", "architecture",
  "trigonal contre orthorhombique, meme formule",
  "solubilite, stabilite relative, temperature de transformation",
  "la composition seule ne determine pas la persistance"),
 ("MgSiO3", "Enstatite", "Post-perovskite", "architecture",
  "chaines simples contre structure lamellaire dense",
  "densite, vitesses sismiques, domaine de pression",
  "une meme composition change de regime sous contrainte"),
 ("H2O", "Glace Ih", "Glace amorphe", "histoire",
  "reseau hexagonal contre reseau desordonne",
  "densite, chaleur de transition, capacite d'archivage",
  "la vitesse de refroidissement reste inscrite dans la structure"),
 ("H2O", "Glace Ih", "Glace VII", "conditions",
  "hexagonal basse pression contre cubique haute pression",
  "densite, domaine de stabilite, reversibilite",
  "le domaine accessible depend de la pression maintenue"),
 ("SiO2", "Quartz", "Verre de silice", "histoire",
  "reseau ordonne contre reseau fige hors equilibre",
  "point de fusion net ou absent, vieillissement structural",
  "la trempe inscrit une histoire que le recuit efface lentement"),
 ("Fe-C", "Acier trempe", "Acier recuit", "histoire",
  "martensite contre ferrite et perlite, composition identique",
  "durete, limite elastique, tenacite",
  "l'histoire thermique et mecanique est physiquement incorporee"),
 ("Fe3O4", "Magnetite sous le point de Curie", "Magnetite au-dessus", "histoire",
  "aimantation remanente presente ou effacee",
  "direction et intensite du champ enregistre",
  "une inscription possede un seuil d'effacement thermique"),
 ("Especes minerales", "Mineral primaire", "Mineral d'alteration", "histoire",
  "assemblage igne contre assemblage hydrate",
  "composition en volatils, surface reactive",
  "l'alteration ouvre des surfaces et ferme des retours"),
]

# --- B. Liens causaux candidats types --------------------------------------
TYPES = {
 "MATR": "transmission materielle", "ENBL": "condition permissive",
 "STAB": "stabilisation", "CATL": "catalyse", "CNST": "contrainte",
 "INCO": "inscription historique", "FEED": "retroaction",
 "CLOS": "fermeture", "INTG": "integration", "DEPG": "dependance fonctionnelle",
}
LIENS = [
 ("Ionisation", "ENBL", "Plasma thermique", "l'ionisation ouvre le regime plasma"),
 ("Ionisation", "CLOS", "Liaison chimique neutre", "au-dela d'un seuil, la chimie neutre cesse"),
 ("Transition vitreuse", "STAB", "Verre", "fige un liquide hors equilibre"),
 ("Transition vitreuse", "CLOS", "Rearrangement liquide", "ferme les reorganisations a longue portee"),
 ("Depot", "INCO", "Sediment stratifie", "inscrit une sequence temporelle lisible"),
 ("Metamorphisme", "INCO", "Assemblage mineral", "inscrit un chemin pression-temperature"),
 ("Metamorphisme", "CLOS", "Texture sedimentaire initiale", "efface la texture anterieure"),
 ("Cristallisation", "STAB", "Solide cristallin", "abaisse l'energie et fixe l'ordre"),
 ("Refroidissement sous le point de Curie", "INCO", "Magnetite", "inscrit la direction du champ ambiant"),
 ("Chauffage au-dela du point de Curie", "CLOS", "Aimantation remanente", "efface irreversiblement l'inscription"),
 ("Adsorption de surface", "CATL", "Reaction heterogene", "concentre et oriente les reactifs"),
 ("Serpentinisation", "CATL", "Synthese organique", "fournit H2 et surfaces reductrices"),
 ("Frontiere de phase", "ENBL", "Gradient", "une interface permet un gradient durable"),
 ("Gradient", "ENBL", "Flux", "un gradient entretenu autorise un flux"),
 ("Flux entretenu", "STAB", "Structure dissipative", "maintient une organisation hors equilibre"),
 ("Segregation metal-silicate", "CLOS", "Inventaire siderophile de surface", "sequestre sans retour etabli"),
 ("Echappement atmospherique", "CLOS", "Composition primitive", "fractionne de maniere irreversible"),
 ("Encapsulation", "ENBL", "Selection sur compartiment", "rend la variation heritable a l'echelle du compartiment"),
 ("Endosymbiose", "INTG", "Cellule eucaryote", "integration avec perte d'autonomie du partenaire"),
 ("Transfert de genes", "DEPG", "Endosymbiote", "le partenaire devient dependant de l'hote"),
 ("Architecture virale", "DEPG", "Machinerie de l'hote", "aucune reproduction autonome"),
 ("Conformation prion", "INCO", "Proteine hote", "l'information est portee par la conformation, pas la sequence"),
 ("Biofilm", "FEED", "Microenvironnement local", "modifie le milieu qui le favorise"),
 ("Biomineralisation", "INCO", "Coquille et os", "inscrit une histoire de croissance et de milieu"),
 ("Ordre de bande electronique", "ENBL", "Conduction ou isolation", "fixe le regime de transport"),
 ("Appariement supraconducteur", "STAB", "Coherence macroscopique", "protege par un gap d'excitation"),
 ("Ordre topologique", "STAB", "Etat de bord protege", "robustesse aux perturbations locales"),
 ("Piege a pression", "CNST", "Derive radiale des galets", "borne la perte vers l'etoile"),
 ("Barriere de rebond", "CNST", "Croissance collisionnelle", "borne la taille atteignable"),
 ("Instabilite de streaming", "FEED", "Concentration de solides", "la concentration renforce la concentration"),
]

# --- C. Familles sous-representees ----------------------------------------
FAMILLES = [
 ("architectures vitreuses et amorphes", "inscrivent la vitesse de trempe et vieillissent"),
 ("colloides, gels, mousses, emulsions", "interfaces massives et transport modifie"),
 ("architectures electroniques de bande", "fixent le regime de transport sans changer la composition"),
 ("ordres magnetiques et memoires remanentes", "inscription lisible avec seuil d'effacement"),
 ("coherences quantiques collectives", "persistance par gap, non par barriere chimique"),
 ("phases topologiques", "robustesse d'origine globale et non locale"),
 ("disques d'accretion et jets", "transport de moment cinetique et redistribution de matiere"),
 ("architectures virales dependantes", "reproduction sans autonomie metabolique"),
 ("prions, replicateurs conformationnels", "heredite portee par la conformation"),
 ("biofilms, microbiomes, ecosystemes, biosphere", "entretien collectif du domaine de viabilite"),
]

# --- D. Motifs structurels transversaux -----------------------------------
MOTIFS = [
 ("confinement vers unite persistante",
  ["confinement des quarks en hadrons", "liaison nucleaire",
   "encapsulation membranaire", "effondrement gravitationnel en corps lie"]),
 ("frontiere vers reservoirs vers gradient",
  ["segregation metal-silicate", "interface eau-roche", "membrane plasmique",
   "stratification atmospherique"]),
 ("barriere vers metastabilite",
  ["diamant a pression ambiante", "verre sous la transition vitreuse",
   "martensite avant revenu", "glace VII en inclusion scellee"]),
 ("architecture vers inscription vers seuil d'effacement",
  ["traces de fission dans le zircon", "aimantation sous le point de Curie",
   "bulles d'air dans la glace", "ADN et sa temperature de denaturation"]),
 ("flux vers persistance dissipative",
  ["structure hydrothermale entretenue", "cellule vivante",
   "disque d'accretion", "convection mantellique"]),
 ("sequestration vers fermeture du domaine accessible",
  ["azote du noyau planetaire", "carbone en phase insoluble",
   "echappement atmospherique irreversible", "delaminage d'un composite"]),
 ("polymorphisme a composition constante",
  ["diamant et graphite", "calcite et aragonite",
   "enstatite et post-perovskite", "glaces I a XIX"]),
 ("catalyse par les surfaces",
  ["chimie sur grains interstellaires", "serpentinisation",
   "argiles et polymerisation", "site actif enzymatique"]),
 ("integration avec perte d'autonomie",
  ["endosymbiose mitochondriale", "transfert de genes vers le noyau",
   "accretion d'un corps dans un plus gros", "alliage et solution solide"]),
 ("reconstruction a partir d'une inscription lue",
  ["replication de l'ADN par polymerase", "traduction par le ribosome",
   "recristallisation depuis un germe", "repliement guide par chaperon"]),
]


def lire(chemin):
    with Path(chemin).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def main() -> int:
    index = lire(TABLES / "01_Index_maitre.csv")
    arbre = lire(ARBRE)
    corpus = " ".join(x["produit"] + " " + x["mecanisme"] + " " +
                      x["proprietes_nouvelles"] for x in arbre).lower()

    # C : quelles familles la genealogie couvre-t-elle ?
    familles = []
    for nom, pourquoi in FAMILLES:
        mots = [m for m in nom.replace(",", " ").split() if len(m) > 6]
        couverte = any(m[:8] in corpus for m in mots)
        familles.append({"famille": nom, "pourquoi_elle_compte": pourquoi,
                         "couverte_par_la_genealogie": couverte})

    # Lacunes : une entree est lacunaire si un champ decisif est generique.
    GENERIQUES = {"non quantifié", "non déterminé", "non applicable", ""}
    lacunaires = [r for r in index
                  if (r["Mobilisabilité"] or "").strip().lower() in GENERIQUES
                  or (r["Stabilité ou durée"] or "").strip().lower() in GENERIQUES]

    liens = [{"source": s, "type": t, "libelle_type": TYPES[t],
              "cible": c, "justification": j} for s, t, c, j in LIENS]

    rapport = {
        "A_contrastes_a_composition_constante": {
            "nombre": len(CONTRASTES),
            "par_variable_controlee": dict(Counter(c[3] for c in CONTRASTES)),
            "contrastes": [
                {"composition": c[0], "cas_1": c[1], "cas_2": c[2],
                 "ce_qui_varie": c[3], "difference_architecturale": c[4],
                 "observables_discriminants": c[5], "proposition_testee": c[6]}
                for c in CONTRASTES],
            "portee": ("ces contrastes soutiennent trois propositions : la "
                       "composition seule ne determine pas les proprietes ; une "
                       "histoire peut rester inscrite ; le retour depend de "
                       "barrieres, de pertes et de l'horizon. Ils ne prouvent "
                       "ni une loi universelle ni une superiorite predictive."),
        },
        "B_liens_causaux_candidats": {
            "nombre": len(liens),
            "par_type": dict(Counter(l["type"] for l in liens)),
            "vocabulaire": TYPES,
            "liens": liens,
            "statut": ("candidats, hors graphe canonique tant que mecanisme, "
                       "occurrence naturelle, trajectoire historique et role "
                       "causal ne sont pas sources separement"),
        },
        "C_familles_sous_representees": {
            "nombre": len(familles),
            "non_couvertes": sum(1 for f in familles
                                 if not f["couverte_par_la_genealogie"]),
            "familles": familles,
            "lecture": ("la genealogie couvre la grande chaine matiere, "
                        "planete, vivant. Elle couvre moins bien les regimes "
                        "intermediaires de la matiere organisee."),
        },
        "D_motifs_transversaux": {
            "nombre": len(MOTIFS),
            "motifs": [{"motif": m, "occurrences": o} for m, o in MOTIFS],
            "avertissement": ("identite de grammaire, pas identite de "
                              "mecanisme. Ces motifs rendent des domaines "
                              "comparables sans les confondre physiquement."),
        },
        "E_lacunes": {
            "entrees_totales": len(index),
            "entrees_avec_au_moins_une_lacune": len(lacunaires),
            "part": round(len(lacunaires) / len(index), 4),
            "principales": ["premiere occurrence individuelle",
                            "origine des nuclides isotope par isotope",
                            "interactions et contraintes precises",
                            "mecanismes de maintien et de transmission",
                            "mobilisabilite reelle",
                            "preuves historiques des liens",
                            "transitions manquantes"],
        },
    }
    (ICI / "carte_causale.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"A  contrastes a composition constante : {len(CONTRASTES)}")
    print(f"   variables controlees : "
          f"{dict(Counter(c[3] for c in CONTRASTES))}")
    print(f"B  liens causaux types               : {len(liens)}")
    print(f"   {dict(Counter(l['type'] for l in liens))}")
    nc = rapport["C_familles_sous_representees"]["non_couvertes"]
    print(f"C  familles sous-representees        : {nc} sur {len(familles)}")
    for f in familles:
        if not f["couverte_par_la_genealogie"]:
            print(f"      {f['famille']}")
    print(f"D  motifs transversaux               : {len(MOTIFS)}")
    e = rapport["E_lacunes"]
    print(f"E  entrees lacunaires                : "
          f"{e['entrees_avec_au_moins_une_lacune']}/{e['entrees_totales']} "
          f"= {e['part']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
