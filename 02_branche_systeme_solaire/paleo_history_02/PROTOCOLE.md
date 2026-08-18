# PALEO-HISTORY-02 — protocole préenregistré (projet non scellé)

## Statut

**Projet. Non scellé, non exécuté.** Ce document devient un protocole gelé quand
`sceller.py` écrit `GEL_PALEO_HISTORY_02.json` avec les empreintes des trois
fichiers, et pas avant. Les décisions listées en fin de document doivent être
tranchées d'abord : elles sont scientifiques, pas techniques.

## Pourquoi un nouveau numéro

PALEO-HISTORY-01 est resté `gele_avant_execution` : sa cible n'a jamais été
ouverte, aucun résultat n'en est issu. Sa règle de gel prévoit qu'une
modification exige un nouveau numéro et une justification publique ; comme il
n'existe aucun résultat antérieur, rien n'est requalifié rétroactivement.

01 est correct mais **sous-spécifié sur deux points opérationnels**, et ces deux
vides — pas une erreur de conception — l'empêchent d'être exécuté :

1. il exige que les incertitudes d'âge soient propagées sur 2 000 réalisations,
   sans dire d'où elles viennent ni comment les rattacher à chaque
   enregistrement. `AUDIT_NORMALISATION.json` montre que les neuf jeux
   normalisés ont `age_uncertainty_ka` vide sur 100 % de leurs lignes ;
2. il exige « absence de succès du même test sur le contrôle négatif réel
   préenregistré », sans nommer ce contrôle.
   `PALEO_HISTORY_02_ACQUISITION.json` a établi qu'aucune variable du produit
   PALMOD n'est *a priori* insensible à l'histoire climatique, et qu'une
   permutation ou un identifiant arbitraire ne constitue pas un contrôle
   physique.

02 hérite intégralement de la question, des modèles, des horizons, des blocs, des
nulls et du critère primaire de 01. Il ne fait que combler ces deux vides.

## Question primaire — inchangée

À état climatique et forçages astronomiques comparables, l'histoire antérieure
améliore-t-elle la prédiction de la trajectoire climatique suivante hors
échantillon ?

Quatre modèles de complexité contrôlée : état et forçages présents ; mêmes
variables plus histoire réelle ; mêmes variables plus histoire permutée dans le
bloc ; témoin de complexité égale sans ordre historique.

## Ajout 1 — chronologie et incertitude d'âge

### Source par famille d'enregistrements

| famille | source d'incertitude | statut |
|---|---|---|
| enregistrements marins de site | ensembles postérieurs PALMOD 2.0.0, 1 000 tirages âge-profondeur par site — DOI `10.1594/PANGAEA.984602`, article `10.5194/essd-18-3013-2026`, CC-BY-4.0 | **acquis : 475/475 sites, 0 échec, 475 empreintes distinctes, 1,34 Go** — voir `ACQUISITION_PALMOD_ENSEMBLES.json` et `CATALOGUE_PALMOD_ENSEMBLES.json` |

### Épinglage de version — contrainte de reproductibilité

Les 475 ensembles sont acquis en version **1.0.2**, celle que déclare la
compilation `PalMod2_0_0.zip` dont l'empreinte `10e0e21e…` est enregistrée. La
résolution par lien `current_version` est **interdite** : elle dérive dans le
temps, et un protocole préenregistré ne peut pas dépendre d'une cible mouvante.

Le témoin consigné dans `PALEO_HISTORY_02_ACQUISITION.json` avait justement été
pris ainsi, en 1.0.3. Cette version reste accessible — vérifié le 2026-08-18,
HTTP 200, 1 000 290 octets — mais elle n'est pas celle que décrit la compilation
épinglée, d'où la divergence d'empreinte documentée dans le relevé d'acquisition.
Ce n'est pas une anomalie : c'est la raison même de l'épinglage.
| carottes glaciaires EPICA et Vostok | AICC2023, σ publiés par carotte et par tranche d'âge | présent au dépôt, empreinte `a0498efb…` conforme à `AICC2023_UNCERTAINTY.json` |
| insolation | sans objet | une solution astronomique définit l'axe temporel ; elle n'a pas d'incertitude de datation. C'est la « justification explicite » prévue par l'interdiction de `SCHEMA_DONNEES.json` |

### Règle de rattachement

Les 2 000 réalisations chronologiques sont tirées ainsi :

- **marin** : chaque réalisation prend un tirage entier parmi les 1 000
  postérieurs du site, jamais un mélange de tirages. Les âges sont interpolés
  linéairement en profondeur sur les profondeurs mesurées de l'enregistrement.
  Au-delà de 1 000, les tirages sont réutilisés dans un ordre fixé par graine
  déclarée ; aucun tirage n'est synthétisé ;
- **glaciaire** : σ AICC2023 par tranche d'âge, propagé par tirage gaussien
  tronqué à ±3σ autour de l'âge publié, monotonie de l'âge en profondeur
  imposée par rejet ;
- **aucune mesure absente n'est remplacée par une sortie de modèle**, conformément
  à l'interdiction héritée.

Un enregistrement dont l'incertitude d'âge n'est pas disponible par l'une de ces
voies est **exclu du test primaire**, jamais complété par imputation.

## Ajout 2 — contrôle négatif réel

### Exigence

Une variable **mesurée sur les mêmes carottes, aux mêmes profondeurs, sous le
même plan d'échantillonnage**, dont le mécanisme générateur est *a priori*
indépendant de l'histoire climatique de surface. Elle hérite donc des mêmes
artefacts de chronologie que la cible, ce qu'une permutation ne peut pas
reproduire : la permutation détruit l'autocorrélation que le modèle d'âge
injecte, alors qu'un contrôle physique la conserve.

### Candidat retenu

La **paléointensité géomagnétique relative (RPI)**, mesurée sur les mêmes
carottes sédimentaires marines. La géodynamo est indépendante du climat de
surface aux échelles considérées ; la RPI est mesurée sur le même sédiment et
aux mêmes profondeurs que les proxys climatiques.

Le recoupement existe : PALMOD contient ODP 983, ODP 984, ODP 1089 et
IODP U1308, qui sont des carottes de référence de la littérature RPI.

### Condition d'admissibilité — corrigée le 2026-08-18

Une première rédaction exigeait que la RPI repose sur une chronologie **non
accordée** au climat. Cette exigence était mal fondée et elle est retirée. Elle
confondait deux problèmes distincts :

1. **la circularité du réglage sur la cible.** LR04 et les tiepoints marins de
   l'intervalle profond sont accordés sur l'orbite ou sur le δ¹⁸O. Cela rend la
   cible partiellement prédictible par les forçages astronomiques *par
   construction*. Ce défaut affecte le modèle de base « état et forçages », et il
   reste entier — c'est la décision 1 en fin de document ;
2. **le rôle du contrôle négatif**, qui est d'hériter des mêmes artefacts de
   chronologie que la cible afin de les rendre visibles. Pour cela il doit rouler
   sur **la même** chronologie, accordée ou non. Exiger une chronologie non
   accordée le prive justement de ce qu'on lui demande.

L'exigence correcte est double :

- la RPI est placée sur **la même chronologie postérieure PALMOD** que la cible
  du même site, artefacts compris ;
- la RPI **n'a pas servi à construire cette chronologie**. Aucun tiepoint
  magnétostratigraphique, sans quoi elle serait prédictible par construction.

Le relevé des ensembles acquis confirme que cette seconde condition est remplie
sur les carottes visées : les tiepoints PALMOD y sont de type `tuned` — donc
issus du δ¹⁸O — ou `14C`/`tephra`, jamais magnétiques. La RPI reste donc
indépendante de la construction du modèle d'âge.

### Ce que les données acquises montrent

Relevé direct des tables chronologiques PALMOD des quatre carottes recoupées :

| carotte | tiepoints | nature | couverture des tiepoints |
|---|---:|---|---|
| ODP 983 | 12 | `tuned` | 0,5–191 ka |
| ODP 1089 | 8 | `tuned` | 0,5–133,5 ka |
| IODP U1308 | 8 | `tuned` | 0,5–134 ka |
| ODP 984C | 18 | 17 `14C`, 1 `tephra` | 0,1–23,4 ka |

Aucune ne couvre 0–800 ka par ses seuls tiepoints. C'est une contrainte
structurelle de la discipline : au-delà de la portée du radiocarbone, la datation
marine passe par l'accord orbital ou isotopique. Le choix de l'intervalle
primaire doit en tenir compte — décision 1.

### Critère

Le test primaire est rejoué à l'identique sur la RPI. Un gain de RMSE de
l'histoire réelle atteignant le seuil primaire sur le contrôle négatif rend le
résultat principal **`non_testable`**, jamais `supports` : il établit que le
protocole capte un artefact de chronologie.

### Acquisition — non faite

Les séries RPI de ces quatre carottes n'ont pas été acquises. Le recoupement
établi à ce jour l'est **par nom de carotte**, pas par vérification qu'une série
RPI publiée, accessible et couvrant l'intervalle existe pour chacune. Cette
vérification est un préalable au scellement.

## Critère primaire — hérité de 01, inchangé

`supports` exige simultanément : gain de RMSE d'au moins 5 % de l'histoire réelle
sur l'état seul dans au moins trois des quatre blocs ; histoire réelle meilleure
que l'histoire permutée et que le témoin de complexité égale, p < 0,01 ; signe du
gain conservé sous les réalisations chronologiques ; réplication du signe sur une
pile benthique indépendante ; absence de succès du même test sur le contrôle
négatif réel.

Un échec rend `does_not_support`. Une donnée obligatoire absente, une p-value
inatteignable, une chronologie non propageable ou un contrôle négatif non acquis
rend `non_testable`, jamais `supports`.

## Décisions à trancher avant scellement

1. **Circularité du réglage orbital.** LR04 a un modèle d'âge accordé sur
   l'orbite. Tester si les forçages astronomiques plus l'histoire prédisent le
   climat, sur une chronologie elle-même accordée à l'orbite, est circulaire. Les
   postérieurs PALMOD de site offrent une sortie — chronologies de site non
   accordées — mais changent l'unité d'analyse : site plutôt qu'empilement.
   Faut-il basculer l'analyse primaire sur les sites PALMOD et reléguer LR04 en
   robustesse ?
2. **Série RPI de référence** pour chacune des quatre carottes, et preuve que sa
   chronologie n'est pas accordée au climat.
3. **Graine et ordre de réutilisation** des tirages au-delà de 1 000.

Tant que ces trois points ne sont pas fixés, le scellement n'a pas lieu.
