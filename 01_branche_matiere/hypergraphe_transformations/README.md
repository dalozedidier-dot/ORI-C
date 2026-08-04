# Hypergraphe mécanistique des branches 1 et 2

Cette couche corrige la représentation linéaire sans effacer `base_transitions/transitions_matiere.csv`, qui reste l'objet historique audité. Elle distingue filiation matérielle, condition d'ouverture, transformation architecturale, transformation environnementale, transport, filtrage, perte et recyclage.

## Produits

- `noeuds.csv` : architectures, réservoirs, interfaces et inventaires ;
- `hyperaretes.csv` : processus multi-entrées/multi-sorties, scénarios et portée de preuve ;
- `sources.csv` : registre portable des sources ;
- `reclassement_relations.csv` : reclassement des 47 liens historiques ;
- `validation_hypergraphe.json` : contrôles structuraux calculés ;
- `filtre_nc_cc.csv` : les huit attributs du filtrage NC–CC, scénarios inclus ;
- `inventaire_accessible.csv`, `masses_reservoirs.csv`, `analyser_inventaire.py`
  et `inventaire_accessible_resultats.json` : première campagne mesurée ;
- `tester_hierarchie.py`, `test_hierarchie_resultats.json` et
  `test_hierarchie_execution_1_prereglee.json` : épreuves de l'échelle des
  capacités, exécution préenregistrée conservée intacte.

## Clôture généalogique

`construire_et_valider.py` publie désormais deux contrôles distincts. La
projection paire à paire vérifie qu'une succession de liens relie les 53 nœuds.
La fermeture hypergraphique stricte exige que toutes les entrées d'un processus
multi-entrée soient déjà disponibles avant de produire ses sorties.

La projection avait d'abord révélé que la chaîne poussière
`N008 → N009 → N010 → N008` tournait sans alimentation matérielle.
L'hyperarête `H047` a corrigé ce défaut. Le contrôle strict a ensuite trouvé un
second verrou que la projection masquait : `N029`, `N030`, `N031`, `N032`,
`N035`, `N053` et `N054` restent enfermés dans une dépendance circulaire. La
projection atteint donc 53 nœuds sur 53, tandis que la fermeture stricte en
atteint 46 sur 53. Le dépôt conserve ce résultat négatif au lieu de déclarer
l'hypergraphe entièrement clos.

## Ce que les épreuves ont donné

La monotonie de l'échelle des dix capacités est **réfutée**, et ne peut pas être
rétablie par un réétiquetage : une production pointe toujours vers le bas. Le
test reste dans la suite en échec déclaré. Deux niveaux ont été corrigés après
lecture des violations avant l'arrêt ; ils sont consignés, et un accord obtenu
ainsi ne compterait pas comme preuve.

Ce qui tient est la non-redondance : l'échelle porte **0,595 bit net du tirage
par permutation**, p = 5·10⁻⁵, rho = 0,74 avec la profondeur dans le graphe.
Les six dimensions en portaient 0,000.

## Règles scientifiques

1. Une source peut soutenir une relation sans démontrer un mécanisme ORI-C.
2. Les scénarios concurrents sont conservés comme tels.
3. Un nœud décrit une architecture ou un réservoir ; une hyperarête décrit un processus.
4. Le partage d'un nœud entre entrée et sortie représente transport, survie ou recyclage, pas une boucle causale instantanée.
5. `Inventaire accessible` demeure une définition opérationnelle à mesurer par élément, spéciation, réservoir et horizon temporel.

Exécution : `python construire_et_valider.py`.
