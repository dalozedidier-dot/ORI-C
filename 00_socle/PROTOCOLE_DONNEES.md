# Protocole de données ORI-C

Ce document dit **quelles données récupérer** pour qu'une étude puisse tester
ce que le cadre affirme, et non seulement le décrire. Il appartient au socle :
il s'applique aux trois branches.

Les schémas des trois tables du §8 sont exécutables. `valider_donnees.py` les
vérifie ; une table qui ne passe pas n'est pas une table ORI-C.

> **Pourquoi ce document existe.** Le dossier a produit un test prospectif dont
> le témoin de complexité égale s'est révélé mal apparié : une variable motrice
> substituée occupait une plage quarante fois différente de celle qu'elle
> remplaçait. Le §6 et le §7 ci-dessous rendent ce défaut détectable avant
> exécution plutôt qu'après. Voir
> `../02_branche_systeme_solaire/couche_memoire_historique/results_stress/prospectif/RAPPORT_PROSPECTIF.md`.

## 1. Données minimales par système étudié

Une ligne par système et par instant, renseignant les six dimensions du
`CODEBOOK.md`.

| Bloc | Données | Exemple |
|---|---|---|
| **Identification** | système, échelle d'analyse `ℓ_ana`, échelles physiques pertinentes `{ℓ_phys}`, lieu, date, régime `(D_i,G_i)`, niveau de description | cellule, planète, minéral, population |
| **Composition** `n` | constituants, abondances, concentrations, isotopes | Fe, Si, eau, gènes, espèces chimiques |
| **Configuration** `G` | organisation spatiale, compartiments, topologie | noyau-manteau, réseau métabolique, orbites |
| **Interactions** `I` | liaisons, réactions, transferts, couplages | réactions, gravitation, échanges de matière |
| **Environnement** `E` | température, pression, flux, ressources, perturbations | irradiation, nutriments, état redox |
| **Persistance** `Π` | durée de maintien, stabilité, reproduction, récupération | survie, demi-vie, stabilité orbitale |
| **Histoire** `H` | états antérieurs, événements, ordre des transformations | impacts, mutations, différenciation |

## 2. Données nécessaires pour tester la chaîne

```text
Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités futures
```

| Étape | Variable à mesurer |
|---|---|
| Histoire | succession **datée** des états et événements |
| Architecture initiale | structure avant perturbation |
| Contrainte appliquée | nature, intensité, durée, **vitesse de variation** |
| Réponse immédiate | changement de structure, de fonction ou de flux |
| Seuil | valeur à laquelle le régime change |
| Inscription | modification persistante **après retrait** de la contrainte |
| État final | architecture après stabilisation |
| Possibilités futures | domaines `P^adm`, `P^att`, `P^kin`, critères `P_pers`, seuils `Π*`, règle `Q` et segment réalisé `h_i` |
| Mise à jour | état `S(t1)` produit par `U_i[t0,t1;S(t0),h_i]` |
| Changement de régime | validité de `D_i`, raccord éventuel `T(i→j)`, information conservée, abandonnée ou reconstruite |

La vitesse de variation et le retrait de la contrainte sont les deux colonnes
le plus souvent omises. Sans la première, un seuil n'est pas défini ; sans la
seconde, une inscription ne se distingue pas d'un état maintenu.

## 3. Variables centrales à calculer

### Dépendance au chemin

Comparer des systèmes ayant le même état apparent au départ, les mêmes
conditions finales, et des histoires intermédiaires différentes.

**Variable principale** : différence finale entre trajectoires sous conditions
finales identiques.

> **Contrôle obligatoire.** L'égalité des conditions finales doit être
> vérifiée, pas supposée. Le protocole de la branche 2 la teste par comparaison
> exacte des séries de forçage après la date de convergence.

### Hystérésis

Contrainte croissante puis décroissante. Mesurer le seuil d'entrée, le seuil de
retour, l'écart entre les deux, et l'état conservé au retour aux conditions
initiales.

> **Trois quantités, pas une échelle.** L'écart de seuils mesure `H`. Il ne
> mesure ni la durée `D` de la trace, ni la perte `L` de composants ou de
> chemins de récupération. Les trois sont indépendantes et doivent être
> publiées séparément : voir `CODEBOOK.md` §13.2. Un rapport qui conclut à une
> « irréversibilité » sans préciser lequel des trois a été mesuré n'est pas
> recevable.

### Inscription historique

Différence entre trois systèmes : celui qui a subi l'événement, un témoin qui ne
l'a pas subi, et un **témoin de complexité équivalente sans mémoire
historique**.

### Persistance

Durée de maintien, probabilité de survie, temps de relaxation, vitesse de
récupération, fréquence des effondrements, capacité de renouvellement.

> **Piège vérifié dans ce dossier.** Un écart mesuré sur une fenêtre plus
> courte que le temps de relaxation n'est pas une inscription. La branche 2 a
> mesuré une dépendance au chemin sur un palier de 10 Ma alors que la mémoire
> testée avait une constante de temps de 8 Ma ; l'écart s'annulait sur palier
> long. **La fenêtre d'observation doit être longue devant toutes les
> constantes de temps du système.**

La mesure doit déclarer l'échelle d'analyse `ℓ_ana`, les échelles physiques
pertinentes `{ℓ_phys}`, les composantes du vecteur
`P_pers[h]=(P_1[h],...,P_n[h])`, leurs observables, fenêtres et unités, le
vecteur de seuils `Π*` et la règle `Q`. Durée, abondance, flux transmis et
rémanence ne doivent pas être additionnés sans adimensionnalisation explicite.

La mesure historique `Π_pers,t^ℓ_ana = P_k[h_t;O,W]` est conservée pour une
composante locale `k`. Son verdict ne porte que sur cette composante. Le verdict
global de persistance porte sur `Q(P_pers[h],Π*)`, pas sur un scalaire
universel.

### Transformation des possibles

La variable la plus importante du cadre, et la moins souvent mesurée. Avant et
après chaque transition :

- nombre d'états accessibles
- diversité des trajectoires possibles
- volume du domaine de viabilité
- distance entre états accessibles
- fonctions nouvellement possibles
- **états devenus inaccessibles**
- coût énergétique d'accès à chaque état

L'avant-dernière ligne correspond au terme `ΔF` de la signature de transition.
C'est celle qui manquait à la carte relationnelle.

> **Trois filtres puis une décision vectorielle.** Distinguer les possibles
> admissibles `P^adm`, atteignables depuis l'état présent `P^att` et
> cinétiquement accessibles `P^kin(T,C,ε)`. Déclarer `ℓ_ana`, les
> `{ℓ_phys}` pertinentes, le régime `(D_i,G_i)`, l'horizon `T`, les contraintes
> `C`, le seuil de probabilité `ε`, puis `P_pers`, `Π*` et `Q`. Le segment
> réalisé `h_i` reste séparé de ces filtres et déclenche la mise à jour `U_i`.
> Voir `CODEBOOK.md` §13.3 et §13.5.

### Boucle de mise à jour et changement de régime

Toute future instanciation complète doit enregistrer :

1. l'état initial `S(t0)` et le domaine `D_i` qui le contient ;
2. la dynamique `G_i` et les trajectoires considérées dans `Ω_Gi(S(t0))` ;
3. le segment effectivement réalisé `h_i` ;
4. l'opérateur `U_i` et l'état obtenu `S(t1)` ;
5. le résultat de la réévaluation de `D_i` ;
6. si nécessaire, le raccord `T(i→j)` et sa nature : matching/continuité ou
   projection/coarse-graining ;
7. les variables conservées, abandonnées et reconstruites par ce raccord.

Ces champs sont recommandés pour les nouvelles instanciations mais ne sont pas
ajoutés rétroactivement comme exigences aux tables expérimentales existantes.

### Même état apparent, histoires différentes

Le test transversal de mémoire compare deux unités `A` et `B` telles que
`S_t,macro^A ≃ S_t,macro^B`, tout en mesurant une différence de trace à une
échelle plus fine, `m_t,micro^A ≠ m_t,micro^B`. Sous un stimulus final commun,
la prédiction ORI-C testable est que les segments réalisés ou états mis à jour
diffèrent, `h_i^A ≠ h_i^B` ou `S^A(t1) ≠ S^B(t1)`. L'appariement
macroscopique, la mesure microscopique et l'identité du stimulus doivent être
publiés séparément.

L'ablation renforce l'inférence causale : si l'opération physique met la trace
pertinente à zéro, la différence de réponse doit disparaître dans la tolérance
préenregistrée. Il faut tester les deux flèches `H_t → m_t^ℓ_ana` puis
`m_t^ℓ_ana → h_i → U_i → S(t1)`, et non une corrélation globale entre histoire
et réponse.

### Provenance épistémique

Pour chaque variable de la chaîne, enregistrer le statut `imposé`, `mesuré`,
`calculé` ou `reconstruit`, ainsi que les données `D` et le modèle `M` utilisés.
Les grandeurs reconstruites prennent un chapeau dans les rapports (`Ĥ`, `m̂`,
`P̂`). Une trajectoire physique et son estimation ne doivent jamais occuper la
même colonne sans ce qualificatif.

## 4. Données temporelles

Une mesure avant-après ne suffit pas. La série doit couvrir : état initial,
approche du seuil, franchissement, régime transitoire, nouvel état, retrait
éventuel de la contrainte, récupération ou maintien de l'inscription.

La fréquence de mesure doit être plus rapide que le phénomène. Une transition
de quelques minutes demande la seconde ; une évolution planétaire demande des
archives couvrant des millions d'années.

## 5. Données propres aux branches

### Branche 1 — Matière

Composition élémentaire et isotopique, phases, température, pression, état
d'oxydation, densité, viscosité, structure cristalline, énergie libre, vitesses
de réaction, seuils de changement de phase, temps de relaxation, et **produits
obtenus selon l'ordre des transformations**.

### Branche 2 — Système solaire et planètes

Masses et compositions, paramètres orbitaux, résonances, migrations,
chronologie des impacts, composition isotopique des météorites, abondance des
radionucléides, histoire thermique, état redox, différenciation noyau-manteau,
pertes atmosphériques, apports tardifs, archives climatiques et géologiques,
réponses aux forçages astronomiques.

Pour tout modèle numérique, conserver en outre : conditions initiales,
paramètres, pas temporel, méthode d'intégration, graine aléatoire, version du
code, **critères de réussite préenregistrés**.

### Branche 3 — Vivant

Génotype, phénotype, taux de croissance, survie, reproduction, fitness,
résistance, tolérance, persistance, flux métaboliques, expression génique,
conditions environnementales, **ordre des expositions**, lignées, mutations
successives, coûts et compromis, récupération après retrait de la contrainte.

Pour le **régime 7**, où l'hérédité est à établir et non présupposée, il faut
en outre des **données de lignées** : identifiant de compartiment, cycle,
ascendant, variante portée, transmission et fonction mesurée. Sans elles, on
observe une production chimique et non une hérédité. Schéma et validateur :
`../03_branche_vivant/programme_prebiotique/`.

## 6. Témoins obligatoires

| Groupe | Fonction |
|---|---|
| Témoin neutre | évolution sans contrainte particulière |
| Témoin instantané | dépend seulement de l'état présent |
| Témoin historique | reçoit la trajectoire complète |
| **Témoin de complexité égale** | autant de paramètres, sans mécanisme historique |
| Ablation | suppression du mécanisme supposé produire l'inscription |
| Trajectoire alternative | même arrivée, histoire différente |

Le témoin de complexité égale est celui qui empêche d'attribuer à l'histoire un
gain produit par le seul ajout de paramètres. C'est lui qui a fait basculer le
verdict de la couche mémoire, et c'est lui qui doit être **vérifié**, pas
seulement déclaré.

### Vérification d'appariement, obligatoire

Un témoin de complexité égale n'est valide que si l'on publie, pour chaque
variable motrice substituée :

| À publier | Pourquoi |
|---|---|
| nombre de paramètres libres de chaque modèle | l'égalité doit être comptée, pas affirmée |
| nombre d'états dynamiques | idem |
| **plage d'exploitation de chaque variable motrice** | une substitution peut changer l'échelle et non la nature |
| valeur de référence servant à la normalisation | elle doit être indépendante du point testé |

Sans ces quatre lignes, un résultat favorable au modèle testé n'est pas
interprétable.

## 7. Métadonnées systématiques

Chaque donnée porte : source, auteur ou laboratoire, date de récupération,
unité, méthode de mesure, précision, incertitude, limites de détection, données
manquantes, transformations appliquées, version du fichier, licence, empreinte
SHA-256, et **script ayant produit le résultat**.

## 8. Les trois tables canoniques

Schémas exécutables dans `schemas_donnees/`, vérifiés par
`valider_donnees.py`.

### `etats.csv` — un enregistrement par système et par instant

```text
system_id ; temps ; composition ; configuration ; interactions ; environnement ;
contrainte ; reponse ; seuil ; persistance ; inscription ; histoire ; possibles
```

### `evenements.csv` — un enregistrement par événement

```text
system_id ; event_id ; debut ; fin ; type_evenement ; intensite ; ordre ;
etat_avant ; etat_apres ; reversible
```

### `relations.csv` — un enregistrement par lien typé

```text
source ; relation ; cible ; date ; niveau_preuve ; reference
```

Le vocabulaire de `relation` et l'échelle de `niveau_preuve` sont ceux du
`CODEBOOK.md`. La carte relationnelle du socle est une instance de cette
troisième table.

## 9. Ordre de collecte

```text
séries temporelles → trajectoires comparables → témoins → seuils
→ état après retrait de la contrainte → domaine des états accessibles
```

Les données descriptives montrent ce qui existe. Seuls les trajectoires, les
témoins et les interventions testent ce que le cadre affirme :
**l'histoire transforme l'architecture présente et modifie les possibilités
futures.**

## 10. Utilisation

```bash
cd 00_socle
python valider_donnees.py --repertoire <dossier contenant les trois CSV>
python valider_donnees.py --exemple    # écrit un jeu minimal conforme
```
