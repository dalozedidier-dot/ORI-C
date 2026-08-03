# Branche 2 — Système solaire, Terre et inscription géologique

**Régimes 5 et 6.**

5. systèmes planétaires couplés
6. diversification minérale et organisation terrestre

> **Erratum.** L'article de cette branche est antérieur à l'exécution des
> tests de la couche mémoire. Sur tout ce qui les concerne, `article/ERRATUM.md`
> fait foi.

## Objet

Décrire comment une histoire planétaire produit une architecture héritée,
comment cette architecture génère un spectre de sollicitations, et comment les
sous-systèmes terrestres le filtrent selon leur propre état.

```text
histoire planétaire → architecture héritée → contraintes → réponses terrestres → inscriptions géologiques
```

soit, dans la notation de la branche :

```text
H^SysSol → m^SysSol → S_astro → C_k → H_i^Terre → R_i → m^Terre
```

## Documents de la branche

| Document | Objet |
|---|---|
| `article/` | l'article de la branche, et son `ERRATUM.md` |
| `FILTRAGES_HISTORIQUES.md` | la chaîne de filtrages qui produit une architecture planétaire, et les formulations à ne pas relâcher |
| `couche_astronomique/` | 25 calculs N-corps |
| `couche_memoire_historique/` | tests MPT et exoplanétaire |
| `application_climat/` | article d'application autonome, hors chaîne de preuve de la branche |

`application_climat/` est une **étude de cas séparée**. Elle n'entre dans
aucun des verdicts de la branche, n'en reçoit aucun, et son contenu de domaine
ne remonte pas au socle. Les cinq notions transversales qui en ont été
extraites vivent désormais dans `../00_socle/CODEBOOK.md` §13, qui fait foi
sur elles. Voir `application_climat/README.md`.

`FILTRAGES_HISTORIQUES.md` occupe une place particulière : c'est le seul endroit
du programme où la dépendance au chemin est matériellement enregistrée plutôt
que modélisée. Il documente un mécanisme établi par la cosmochimie ; il ne
mesure aucun apport propre à ORI-C.

## Deux couches de résultats, à ne jamais mélanger

C'est la règle la plus importante de cette branche. Les deux couches ont des
objets, des méthodes et des verdicts différents.

| Couche | Question testée | Verdict |
|---|---|---|
| `couche_astronomique/` | le modèle réduit reproduit-il une trajectoire astronomique indépendante, et modifier l'architecture change-t-il la trajectoire terrestre ? | **13 critères réussis sur 15** |
| `couche_memoire_historique/` | une réponse dépendante de l'histoire prédit-elle mieux une archive hors échantillon qu'un modèle classique de complexité égale ? | **réfuté** |

### Couche astronomique

25 calculs N-corps, trajectoire principale de 20 Ma vers le passé, départ sur
vecteurs JPL Horizons DE441, comparaison à Horizons et à La2010.

Accord Horizons à 6 ka : r = 0,99999981, RMSE 4,83 × 10⁻⁷.
Accord La2010 à 1 Ma : r = 0,99727.
Pic de la bande de 405 ka retrouvé à 408 184 ans dans les deux solutions.
Six interventions sur Jupiter et Saturne produisent des écarts 6,27 à 13,83
millions de fois supérieurs à la dispersion d'états initiaux quasi identiques.

Deux critères échouent et sont conservés tels quels : le moment angulaire
newtonien dans le seul contrôle relativiste complet, et l'aller-retour
temporel au pas de 0,01 an, qui réussit au pas raffiné.

**Portée.** Validation astronomique et numérique du mécanisme réduit. Le modèle
ne résout ni la Lune, ni la rotation terrestre, ni le J₂ solaire, ni les marées,
ni l'obliquité dynamique. Il ne produit aucune prédiction climatique ou
géologique hors échantillon.

Voir `couche_astronomique/STATUT_SCIENTIFIQUE.md`.

### Couche mémoire historique

Deux protocoles : le test de la transition du Pléistocène moyen sur LR04, et un
test exoplanétaire à deux histoires spin-orbitales aboutissant au même forçage
final.

Le protocole initial concluait à 3 critères réussis sur 5. Cinq défauts ont été
identifiés et corrigés :

| Défaut | Correction |
|---|---|
| M2 n'était comparé qu'à M1, moins complexe | ajout de M1P, témoin à complexité égale sans mémoire d'état |
| BIC sur 1 200 points supposés indépendants, résidus autocorrélés à 0,97 | BIC sur taille d'échantillon efficace |
| quatre paramètres de M2 sur une borne à l'optimum | bornes élargies d'un ordre de grandeur |
| palier exoplanétaire de 10 Ma, plus court que les mémoires de 8 et 60 Ma | critère de persistance sur palier long |
| une troisième symétrie exacte rendait l'ablation carbone indéterminée | décalage de l'état lent fixé à zéro |

**Verdict corrigé : 1 critère sur 5 contre M1, 0 sur 5 contre M1P.**

M2 perd 31,6 % contre le témoin de complexité égale, avec un intervalle de
confiance à 95 % de [−0,389 ; −0,251]. Le gain apparent sur M1 est reproduit
dans 82 % des tirages d'un nul à forçage aléatoire.

Le test exoplanétaire réussit son volet structurel et son ablation, mais échoue
au test de persistance : l'écart décroît avec un temps caractéristique de 7,0 Ma
et s'annule sur palier long. C'est un retard de relaxation, pas une inscription.

Voir `couche_memoire_historique/RAPPORT_CORRIGE.md`.

## Ce que le résultat négatif ferme, et ce qu'il ne ferme pas

**Il ferme** cette implémentation particulière de la mémoire climatique : une
mémoire carbone lente inscrite dans le volume de glace passé, testée sur LR04
avec un forçage d'insolation du 21 juin à 65°N.

**Il ne ferme pas** la couche astronomique de la même branche, qui est validée
séparément et dont aucun critère ne dépend de la couche climatique.

**Il ne ferme pas** les branches 1 et 3, qui portent sur d'autres objets et
d'autres mécanismes, et qui n'ont pas été soumises au même test.

Deux résultats vont d'ailleurs dans l'autre sens et sont conservés : l'échec
spectral est un échec de calibration et non une incapacité structurelle, et
l'EMIC réduit possède bien une région bistable, simplement pas là où le forçage
final est placé.

## Liaison vers la branche 3

```text
planète différenciée → hydrosphère, atmosphère, minéraux, gradients, cycles → voies prébiotiques accessibles
```

## Contenu

| Dossier | Contenu |
|---|---|
| `article/` | Architecture historique du Système solaire, revue approfondie |
| `couche_astronomique/` | 25 calculs N-corps, code, données de référence, manifestes, bundle Git |
| `couche_memoire_historique/` | tests MPT et exoplanétaire, version corrigée, campagne de stress |

## Exécution

```bash
cd couche_memoire_historique
export PYTHONPATH="$PWD/src"
python -m unittest discover -s tests -v
python -m oric_memory_tests --root "$PWD" run-all --config configs/primary.json
```

La couche astronomique se reproduit selon `couche_astronomique/REPRODUCTION.md`.
