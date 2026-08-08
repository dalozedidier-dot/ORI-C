# Tables candidates — ce qui est mesuré, ce qui est calculé, ce qui manque encore

Trois fichiers, tous construits depuis `04_acquisitions_externes_2026-08-07/` et depuis
l'inventaire déjà sourcé du dépôt. Ce sont des **propositions**, pas des tables validées.
Aucune valeur n'est inventée ; les cellules sans valeur publiée restent vides.

---

## 1 · `late_accretion_tracers.csv`

**Schéma ORI-C :** `sample_id, tracer, final_value, uncertainty, candidate_source`

**Source :** GEOROC / DIGIS, CC BY-SA 4.0, sept compilations, 197 fichiers, 555 677 analyses
roche totale publiées.

| | |
|---|---:|
| mesures après déduplication et retrait des valeurs nulles | **122 159** |
| échantillons distincts | **56 614** |
| familles de réservoir | 45 |
| échantillons portant ≥ 2 traceurs | 29 536 |

| traceur | mesures |
|---|---:|
| Mo | 33 713 |
| W | 28 868 |
| Pd | 9 194 |
| Pt | 9 039 |
| Os | 7 980 |
| Ir | 7 515 |
| Au | 7 374 |
| Re | 7 185 |
| Ru | 6 695 |
| Rh | 4 596 |

L'ensemble Mo-Ru-W-Os-Ir-Au demandé par `AUDIT_DONNEES_DEPOT.md` est couvert.

**Transformations :** dépivotage colonne → ligne, conversion ppb → ppm, déduplication sur
le triplet échantillon-traceur-valeur, et **retrait des 16 609 valeurs nulles ou
négatives**. Dans les compilations GEOROC un zéro signale une valeur sous la limite de
détection, pas une mesure ; le moteur calcule des moyennes par famille de réservoir, ces
zéros les auraient tirées vers le bas sans qu'aucune mesure ne le justifie.

### Contrôle physique passé

Les rapports interélémentaires médians se comparent aux rapports chondritiques CI :

| rapport | mesuré | CI | échantillons |
|---|---:|---:|---:|
| Os/Ir | **1,04** | 1,07 | 4 062 |
| Ru/Ir | 2,11 | 1,50 | 6 084 |
| Rh/Ir | 1,00 | 0,29 | 4 056 |
| Pt/Pd | 1,12 | 1,67 | 8 179 |
| Pd/Ir | 6,53 | 1,22 | 6 822 |

Le couple réfractaire Os-Ir est chondritique à 3 % près, tandis que Pd, plus incompatible,
est fortement fractionné. C'est le comportement attendu de vraies données HSE mantelliques,
et c'est ce qui donne confiance dans la table.

L'osmium s'étale sur plus de deux ordres de grandeur entre familles de réservoir, de
~0,0000 ppm en marge convergente à 0,0250 ppm dans les minerais de cratons archéens.

### Ce qui manque encore

1. **`uncertainty` est vide.** GEOROC ne publie pas l'incertitude analytique par mesure
   dans ces fichiers précompilés.
2. **`candidate_source` n'est pas un pôle de mélange.** Elle contient
   `TYPE DE ROCHE | CADRE TECTONIQUE`, la famille de réservoir documentée par GEOROC.
   La demande exacte du dépôt était « compilation Mo-Ru-W-Os-Ir-Au **et modèles de mélange
   documentés** ». La compilation y est ; les modèles de mélange non.

---

## 2 · `thermochemical_phases.csv`

**Schéma ORI-C :** `phase, temperature, pressure, gibbs_energy, composition`

**Source :** base OBIGT et jeux Berman de CHNOSZ, GPL-3.

| | |
|---|---:|
| points | **64 512** |
| phases | **1 025** |
| température | 298,15 → 2 000 K |
| **pression** | **1 bar → 50 000 bar, soit 5 GPa** |

### Les équations viennent de la source, pas de la mémoire

Les formules sont reprises telles quelles de `R/cgl.R` et `R/Berman.R` de CHNOSZ. Trois
modèles de pression coexistent, chacun déclaré dans la colonne `modele_pression` :

| modèle | points | ce que c'est |
|---|---:|---|
| équation d'état Berman V(T,P) | 7 553 | V dépend de T et de P, forme Berman 1988 |
| volume constant, convention `cgl.R` | ~45 700 | ∫V dP = V·(P−1)·0,1 J |
| gaz parfait | ~17 300 | ∫V dP = RT·ln(P/P₀) |
| volume non publié | ~1 100 | limité à 1 bar |

### Un piège corrigé, et vérifié

`Berman()` de CHNOSZ renvoie `Ha − T·S`, où S est l'entropie du troisième principe. Les
blocs CGL portent une énergie de **formation**. Mélanger les deux dans un même fichier
aurait faussé toute séquence de condensation. L'écart est la constante `Tr · S_éléments`,
calculée depuis `thermo/element.csv` comme le fait la fonction `entropy()` de CHNOSZ.

Vérification sur les 77 minéraux dont la source publie `GfPrTr` :

- **écart médian 26 J/mol** sur des valeurs de l'ordre de 10⁶ J/mol ;
- écart maximal 0,55 % sur la grunérite et la ferro-actinolite, deux minéraux dont CHNOSZ
  signale lui-même l'incohérence interne.

### Contrôles thermodynamiques

- `dG/dP > 0` : **0 violation** sur 9 056 séries.
- `dG/dT < 0` : **0 violation** sur 6 502 séries, entropie déduite jamais négative.
  Les 336 lignes qui violaient ce critère — six polymorphes de glace haute pression —
  **ont été retirées**, voir `RETRAITS.json`.
- volume molaire déduit de `dG/dP` : 6,6 à 6 990 cm³/mol, médiane 128. Le maximum
  correspond aux kérogènes C292 à C515, des macromolécules réellement volumineuses.
- 75 entrées de **contribution de groupes** (`[Gly]`, `[(6)(6)>CB=]`…) ont été retirées :
  ce sont des incréments additifs, pas des phases.

### Ce qui manque encore

La borne de 5 GPa couvre la croûte et le manteau supérieur. Au-delà, la forme quadratique
V(P) de Berman et le volume constant du bloc CGL sortent de leur domaine de calibration.
La limite noyau-manteau, à 136 GPa, reste hors d'atteinte avec cette base.

---

## 3 · `volatile_inventory.csv`

**Schéma ORI-C :** `sample_id, volatile, initial_mass, core_mass, mantle_mass, atmosphere_mass, lost_mass`

**Source :** l'inventaire **déjà sourcé du dépôt lui-même**,
`01_branche_matiere/hypergraphe_transformations/inventaire_accessible.csv` et
`masses_reservoirs.csv`, dont chaque valeur renvoie à `sources.csv` (S19 à S24) avec URL et
DOI. Conversion ppm et wt% en kg par les masses de réservoir publiées.

Dix lignes : une par corps, volatil et scénario de noyau publié. `initial_mass` reçoit
l'estimation de **masse totale publiée**, indépendante de la somme des compartiments.

**Un piège d'unités corrigé.** Pour l'hydrogène, la masse totale et l'hydrosphère sont
publiées en H₂O tandis que le noyau est en H élémentaire. Tout a été ramené à la masse
d'hydrogène par le facteur 2,016/18,015. Sans cette conversion, le test de fermeture est
faux d'un facteur 9.

### Résultat : trois budgets ferment, trois non

| corps et scénario | volatil | erreur de fermeture | |
|---|---|---:|---|
| C-TER-NOY-MAX | C | **2,9 %** | ferme |
| H-TER-NOY-MAX | H | **2,9 %** | ferme |
| S-TER-NOY | S | **1,6 %** | ferme |
| H-TER-NOY-MIN | H | 61,2 % | ne ferme pas |
| C-TER-NOY-MIN | C | 83,9 % | ne ferme pas |
| C-TER-NOY-BAS | C | 90,5 % | ne ferme pas |
| N (3 scénarios) et Vénus | N | non calculable | pas de masse totale publiée |

**Lecture.** Les budgets publiés de carbone, d'hydrogène et de soufre de la Terre ne
ferment que si le noyau porte le **haut** de sa fourchette publiée. Les scénarios à noyau
pauvre laissent 61 à 90 % de la masse totale non attribuée. C'est un résultat mesurable,
pas une opinion.

Le moteur `volatile_budget` prend la médiane des erreurs, soit 0,320 contre un seuil de
0,05 : il déclare donc un **échec** sur les 10 entrées `P4`. Cet échec est le résultat, et
il confirme quantitativement ce que `AUDIT_DONNEES_DEPOT.md` affirmait sans le chiffrer.

---

## 4 · `planetary_histories.csv` — délibérément absent

**Je ne l'ai pas produit, et c'est un choix.**

Le schéma demande sept couches d'histoire par corps : composition initiale, provenance,
temps d'accrétion, histoire thermique, histoire redox, pertes, apports tardifs. Aucune
source publique harmonisée et directement téléchargeable ne fournit ces sept couches pour
un ensemble de corps. La recherche n'a rien donné, ni sur Zenodo, ni sur PANGAEA, ni dans
les soixante archives locales.

Remplir ces colonnes reviendrait à écrire de mémoire des descripteurs qualitatifs, sans
source vérifiable, pour faire passer onze entrées. Ce serait exactement ce que la règle du
dépôt interdit, et le moteur `incremental_history_value`, qui mesure à quel point
l'histoire détermine la partition finale, renverrait une valeur triviale sur trois ou
quatre lignes.

Les onze entrées restent donc bloquées, et c'est l'état honnête du dossier. Fermer ce
manque demande une compilation manuelle depuis la littérature primaire, avec une référence
par cellule.

---

## Effet sur la campagne des 683 entrées — et pourquoi ce compteur n'est pas la bonne mesure

Les chiffres ci-dessous ont été relevés **avant** le pare-feu `fail_closed_v2`. Ils sont
conservés pour la traçabilité, mais ils ne décrivent plus l'état courant :

| état du jeu de données | réussites | échecs | bloquées | non exécutables |
|---|---:|---:|---:|---:|
| chiffres publiés dans `README.md` avant erratum | 298 | 0 | 337 | 48 |
| dépôt tel quel, code d'alors | 451 | 0 | 200 | 32 |
| + climat multi-variables réel | 461 | 0 | 190 | 32 |
| + thermochimie et traceurs | 486 | 0 | 165 | 32 |
| + inventaire volatil | 486 | 10 | 155 | 32 |
| **état courant, `fail_closed_v2`** | **9** | **0** | **626** | **48** |

**La lecture que j'en donnais était fausse.** J'ai décrit les blocages comme des
« exclusions de moteurs simulant » et comme un manque de données. Le relevé réel des
`coverage_gaps` dit autre chose :

| famille | entrées | part |
|---|---:|---:|
| `test_hors_portee_mesuree` | **320** | 51,1 % |
| `non_admissible_comme_preuve_empirique` | **243** | 38,8 % |
| `aucun_jeu_empirique_declare` | 63 | 10,1 % |

La famille dominante n'est pas l'absence de données. C'est **une table réelle et
volumineuse qui ne porte pas les variables exactes du test** : GISTEMP donne une
température mais pas de forçage ni de compartiment ; les vésicules donnent turbidité et
cartes parent-descendant mais pas longueur de polymère ni fidélité de copie ; GEOROC donne
122 159 mesures mais une famille géologique là où le test attend un pôle de mélange.

La deuxième famille est un refus délibéré : `derived_benchmark` 57, `ephemeris_model_input`
47, `documentary_compilation` 32, sorties de modèle et compilations documentaires. La table
existe, elle est parfois énorme, et la politique dit qu'elle n'est pas une preuve primaire.

**Conséquence pratique.** Ajouter des tables à cette matrice ne produit pas de science. Le
chemin est l'inverse : écrire d'abord le critère et la liste des variables obligatoires,
vérifier qu'une source publique les contient toutes sans imputation, préenregistrer le
protocole avec son empreinte, et seulement ensuite intégrer la donnée dans un pipeline
ciblé. La matrice générique est un **diagnostic de couverture**, et elle a déjà fait son
travail.

Les limites propres à ces tables — pression bornée à 5 GPa, pôles de mélange absents,
incertitudes analytiques absentes — restent celles décrites plus haut.

---

## Les pôles de mélange chondritiques restent absents, délibérément

Transformer `late_accretion_tracers.csv` en véritable test de mélange demande les
compositions en éléments fortement sidérophiles des pôles candidats : CI, CM, CO, CV, EH,
EL, H, L et LL. La table actuelle ne contient que la famille de réservoir documentée par
GEOROC dans `candidate_source`, ce qui n'est pas un pôle.

**Ces compositions n'ont pas été ajoutées.** La recherche n'a produit aucun jeu public,
harmonisé et directement téléchargeable couvrant les neuf classes. Les valeurs existent
dans la littérature, notamment chez Horan et collaborateurs et chez Fischer-Gödde et
collaborateurs, mais les écrire ici sans source vérifiable reviendrait à fabriquer de la
donnée — exactement ce que la règle du dossier interdit, et ce qui a déjà motivé l'absence
volontaire de `planetary_histories.csv`.

Ce qu'il faudrait pour fermer ce manque, précisément :

- une table par classe chondritique portant Os, Ir, Ru, Pt, Pd, Re et Au en ng/g ;
- l'incertitude associée à chaque valeur ;
- une référence par ligne, avec DOI ;
- la méthode analytique, les mesures HSE anciennes n'étant pas comparables aux mesures
  par dilution isotopique modernes.

Tant que cette table n'existe pas, l'entrée `P5-001` reste un **audit de dispersion entre
familles de réservoir**, et non un test de mélange. C'est ainsi qu'elle doit être lue.
