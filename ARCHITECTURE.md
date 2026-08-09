# Architecture du programme ORI-C

## Le principe de séparation

Le programme se laisse organiser en un socle et trois branches. Cette
séparation n'invente aucun lien : elle rend visibles des liens déjà présents
dans les documents, et surtout elle empêche deux confusions.

La première serait de prétendre qu'un même mécanisme physique explique
indistinctement les étoiles, les systèmes planétaires et les cellules. Rien
dans le dossier ne le soutient et rien ne le teste.

La seconde serait de laisser un vocabulaire commun faire circuler les niveaux
de preuve. Un calcul N-corps convergé et une preuve de concept méthodologique
ne se valent pas parce qu'ils emploient les mêmes symboles.

Une troisième confusion doit être écartée, et le socle en fait une règle :
lire cette structure comme une marche vers la complexité. La flèche
thermodynamique globale va vers l'augmentation de l'entropie ; les poches
d'organisation se maintiennent en dissipant les gradients qui les alimentent.
Voir `00_socle/CODEBOOK.md` §12. Le §13 ajoute des distinctions transversales
— mémoire distribuée, diagnostic `D-H-L`, hiérarchie
`P^adm ⊇ P^att ⊇ P^kin`, persistance vectorielle, séparation `S`/`m`/`A`,
distinction `ℓ_ana` / `{ℓ_phys}`, régimes `(D_i,G_i)`, raccords `T(i→j)`,
mise à jour `U_i`, critère d'altération architecturale et séparation entre
chaîne physique et chaîne de preuve — extraites d'une
application et valables pour les trois branches.

Ce que les trois branches partagent réellement n'est pas un mécanisme, c'est
une **structure relationnelle** :

```text
Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités futures
```

Cette lecture condensée se déploie dans la boucle canonique suivante :

```text
S(t0)
  → [ℓ_ana ; {ℓ_phys}]
  → régime (D_i,G_i)
  → Ω_Gi(S(t0))
  → P^adm → P^att → P^kin
  → stabilité + P_pers[h_i] / Π* / Q
  → h_i réalisé
  → S(t1) = U_i[t0,t1 ; S(t0),h_i]
  → réévaluation de D_i
  → T(i→j) si le régime change
  → nouveaux possibles → itération suivante
```

`ℓ_ana` est une décision de description ; `{ℓ_phys}` appartient au système.
Chaque dynamique `G_i` n'est valide que dans `D_i`. Un raccord `T(i→j)` doit
indiquer s'il conserve des variables par matching/continuité ou s'il projette
la description avec perte d'information, et préciser ce qui est conservé,
abandonné ou reconstruit. La réalisation n'est donc pas le dernier maillon
d'une chaîne : elle met à jour l'état dont seront calculés les possibles
suivants.

## Le socle n'est pas une branche

Le socle contient le langage et un résultat formel commun, jamais un
résultat empirique de branche. Il rassemble :

- la définition d'une architecture matérielle ;
- les six dimensions `n, G, I, E, Π, H` ;
- la boucle récursive ORI-C générale ;
- les échelles d'analyse et les échelles physiques ;
- les domaines de validité, dynamiques de régime et raccords ;
- le profil temporel des transitions ;
- les liens typés et leurs règles d'emploi ;
- les niveaux et les modes de preuve ;
- la carte des 40 transitions et des 47 relations.

Il contient aussi le test interventionnel du chémostat. Ce test n'appartient à
aucune branche : il vérifie la logique générale d'une intervention sur un terme
de perte, dans un modèle minimal, sans prétention à un domaine particulier.

La Chronologie des architectures de la matière fournit déjà ce langage
transversal. C'est la raison pour laquelle son article sert à la fois
d'introduction générale et de branche 1.

## Branche 1 — Matière, régimes 1 à 4

1. plasma, particules, noyaux et atomes
2. étoiles et enrichissement chimique
3. combinatoire moléculaire
4. condensation et croissance des solides cosmiques

La branche montre comment les constituants, les configurations et les
interactions ouvrent progressivement de nouveaux domaines matériels. Elle
s'achève lorsque les solides acquièrent une masse, une histoire d'accrétion et
la capacité de former des corps planétaires.

Les régimes 5 à 8 restent présents dans l'article sous forme de passages de
liaison. Leur développement complet est dans les branches 2 et 3.

**Liaison vers la branche 2** — héritage matériel et organisationnel :

```text
éléments → molécules → grains → solides → planétésimaux → planètes
```

Cette chaîne linéaire est une simplification de lecture. La représentation de
travail est un **hypergraphe**, dans
`01_branche_matiere/hypergraphe_transformations/` : 53 nœuds, 53 hyperarêtes
multi-entrées et multi-sorties, où des lignées coexistent, se mélangent, se
séparent et se rejoignent. La matière interstellaire héritée, les condensats
nébulaires nouvellement formés, les glaces et les organiques alimentent
ensemble la population de poussière ; les chondres sont à la fois précurseurs
de corps et produits de corps déjà formés ; les réservoirs NC et CC restent
séparés puis fuient l'un vers l'autre.

Trois distinctions y sont tenues, et elles ne sont pas cosmétiques.

**Parent matériel contre condition permissive.** Le dihydrogène refroidit les
premiers nuages, il n'est pas la matière dont les étoiles sont faites. Un
agent de refroidissement, un flux, la gravité ou un choc sont des conditions.
Le validateur refuse qu'une condition figure comme parent.

**Connectivité et fermeture.** Une seule racine est déclarée, `N036`,
l'inventaire baryonique net. La projection paire à paire relie les 53 nœuds,
mais elle ne suffit pas à établir la fermeture d'un hypergraphe multi-entrée.
La fermeture stricte exige toutes les entrées de chaque processus et n'atteint
que 46 nœuds sur 53. Un noyau cyclique de quatre nœuds bloque trois nœuds
en aval.
Les arêtes à point partagé, transport, survie ou recyclage, ne comptent pas
comme production, sinon tout auto-cycle se déclarerait clos. Les deux contrôles
restent publiés séparément.

**Objets contre processus.** Chaque nœud porte un niveau sur l'échelle des dix
capacités physiques, des constituants jusqu'à la matière disponible pour une
organisation active. Ce niveau **n'est pas monotone le long des arêtes**, et la
tentative de l'y contraindre a été réfutée : une production pointe toujours
vers le bas. Une étoile de niveau 6 produit des éléments de niveau 1. L'échelle
ordonne des objets ; les arêtes décrivent des processus. Les deux ne se
superposent pas.

## Branche 2 — Système solaire et Terre, régimes 5 et 6

5. systèmes planétaires couplés
6. diversification minérale et organisation terrestre

Le lien n'est pas simplement « planètes → Terre ». Il est :

```text
histoire planétaire → architecture héritée → contraintes → réponses terrestres → inscriptions géologiques
```

soit, dans la notation de la branche :

```text
H^SysSol → m^SysSol → S_astro → C_k → H_i^Terre → R_i → m^Terre
```

La branche contient **deux couches de résultats qui ne doivent jamais être
mélangées** :

| Couche | Objet | Statut |
|---|---|---|
| `couche_astronomique/` | 25 calculs N-corps, trajectoire de 20 Ma, comparaison à JPL Horizons DE441 et La2010 | validée, 13 critères sur 15 |
| `couche_memoire_historique/` | tests MPT sur LR04 et test exoplanétaire à chemins contrôlés | **négatif** après correction du protocole |

La première établit que l'architecture héritée produit un spectre calculable et
que sa modification a un effet causal interne au modèle. La seconde devait
établir que la Terre filtre ce spectre selon sa propre mémoire. Elle ne
l'établit pas.

Cette branche héberge en outre une **application séparée**,
`application_climat/`, qui n'appartient à aucune des deux couches. Elle
n'entre dans aucun verdict, n'en reçoit aucun, et ne crée pas de troisième
couche : c'est une étude de cas. Ses apports conceptuels ont été portés au
socle, `00_socle/CODEBOOK.md` §13 ; son contenu de domaine reste chez elle.

**Liaison vers la branche 3** — conditions planétaires :

```text
planète différenciée → hydrosphère, atmosphère, minéraux, gradients, cycles → voies prébiotiques accessibles
```

## Branche 3 — Vivant, régimes 7 et 8

7. voies prébiotiques candidates
8. persistance biologique active

Trois actes : la cellule eucaryote comme architecture matérielle, la
cartographie de l'endosymbiose mitochondriale, et le passage de la résistance
aux antibiotiques à un protocole expérimental.

La branche applique les mêmes six dimensions à un régime où la continuité ne
dépend plus d'une liaison ni d'un flux, mais de l'entretien, de la réparation,
de la reproduction et d'une histoire héréditaire.

**Boucle retour vers la branche 2** :

```text
vivant → transformation de l'atmosphère, des sols, des minéraux, des cycles et des sédiments → nouvelle inscription terrestre
```

La structure complète n'est donc pas une ligne. Une architecture issue d'un
domaine modifie le domaine de possibilités des architectures qui l'entourent.

## Ce qui circule entre branches, et ce qui ne circule pas

**Circule** : l'héritage matériel, la transformation des domaines accessibles,
les inscriptions laissées dans les architectures suivantes, et le vocabulaire
du socle.

**Ne circule pas** : les niveaux de preuve, les mécanismes physiques, et les
verdicts. Le résultat négatif de la couche mémoire de la branche 2 ne se
propage ni vers la couche astronomique de la même branche, ni vers les branches
1 et 3. Symétriquement, la réussite de la couche astronomique n'autorise aucune
affirmation sur les deux autres branches.

## Les fermetures, et pourquoi elles ne sont pas des arêtes

Le cadre présente la fermeture comme une propriété distinctive : la Chronologie
lui consacre une section, inscrit `ΔF` dans la signature de transition et écrit
que l'histoire ne garantit aucune croissance monotone.

La carte ne la représentait pas. Elle le fait désormais, mais **par un attribut
de nœud et non par une arête**, pour une raison qui n'est pas un choix de
commodité.

Le graphe est acyclique et ordonné par régime ; la suite de tests impose que
`FEED` soit le seul lien créant un cycle. Or la plupart des fermetures agissent
sur une architecture **antérieure**. Les représenter par une arête reviendrait
à pointer vers le passé.

| Fermeture nommée dans les documents | Arête correspondante | Représentable |
|---|---|---|
| Le code verrouille les réassignations | `TR-036 vers TR-035` | non, crée un cycle |
| La cristallisation ferme le régime fondu | `TR-022 vers TR-022` | non, boucle sur soi |
| La spécialisation réduit l'autonomie cellulaire | pas de nœud cible | non |
| L'oxygénation contracte les voies abiotiques | `TR-029 vers TR-031` | oui |

**Une fermeture qui agit vers le passé n'est pas représentable par une arête
dans un graphe acyclique ordonné par le temps.** C'est un résultat sur la
structure de la carte, pas un défaut de remplissage.

La colonne `domaine_ferme` de `noeuds_poc.csv` porte donc cinq fermetures
documentées. Les codes `CLOS` et `INTG` sont définis au codebook et attendent
la régénération des figures, décrite dans
`00_socle/carte_relationnelle/REGENERATION_REQUISE.md`.

## Le verrou de la continuité entre branches

Sept relations sur quarante-sept traversent une frontière de branche. Elles
existent, mais la connexion reste peu dense, et le graphe compte seize points
d'articulation et dix-huit ponts : de nombreuses parties de l'architecture
reposent sur une seule transition ou une seule relation.

Le passage matière vers planète est le plus solide, porté par deux relations
fortement inférées depuis l'accrétion des embryons planétaires.

La couche hypergraphe modifie ce constat pour la branche 1 vers la branche 2,
sans l'annuler ailleurs. La continuité y est désormais complète et vérifiée à
chaque validation : les 53 nœuds sont joignables depuis le socle baryonique, et
le contrôle échoue si une seule jonction disparaît. Cela ne dit rien de la
qualité des preuves attachées à chaque arête, qui restent lues une par une
dans `sources.csv`.

Le passage planète vers vivant est le point faible. La relation décisive est
`TR-035 vers TR-036`, de la catalyse ARN et de la copie dirigée par matrice
vers l'établissement du code et de la traduction. Elle est classée
**hypothétique**, et c'est la seule relation du graphe à porter ce niveau sur
un passage inter-régimes majeur.

```text
chimie prébiotique  -->  organisation vivante héréditaire
```

Tant que ce maillon reste hypothétique, la continuité affichée entre la branche
2 et la branche 3 est une continuité de vocabulaire et de conditions
matérielles, pas une continuité démontrée de mécanisme. Le renforcer suppose
des travaux expérimentaux qui n'appartiennent à aucun des documents actuels.
