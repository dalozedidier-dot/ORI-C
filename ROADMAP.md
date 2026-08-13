# ORI-C — roadmap de fermeture scientifique

État de travail : **14 août 2026**. Cette roadmap ne crée aucun nouveau verdict et ne modifie aucune prédiction gelée. Elle réduit le programme actif aux verrous qui peuvent changer le niveau de preuve du dépôt.

Le seuil §XIV reste à **7/12**. Les conditions ouvertes sont **3, 4, 9, 10 et 11** : prédiction prospective hors échantillon, victoire contre témoin apparié, `P_acc` causal dans un système réel, réplications indépendantes strictes et transfert sans redéfinition.

## Les quatre fronts actifs

| Rang | Front | État courant | Donnée ou action manquante | Verrou visé |
|---|---|---|---|---|
| 1 | `VES-PACC-INT-01` | protocole scientifique gelé, préparation des données installée, exécution bloquée | terminer la couche administrative de préenregistrement public puis acquérir les nouvelles données exactement selon le protocole | §XIV-9, puis 3/4 si le test prospectif produit un succès qualifié |
| 2 | `H052 / HC01` — fermeture matière | fermeture stricte **46/53** ; le noyau cyclique `N029/N030/N053/N054` est localisé | preuve primaire suffisamment directe que, dans des conditions compatibles avec une croûte primitive et de l'eau disponible, le processus crée l'interface/permeabilité au lieu de l'exiger comme précondition | fermeture structurelle matière **46/53 → 53/53** si la source justifie réellement le recodage |
| 3 | `PRED-VIVANT-HISTOIRE-001` | prédiction gelée, aucun résultat prospectif | un nouveau jeu longitudinal indépendant tenu hors analyse jusqu'à l'application du protocole gelé | §XIV-3/4 et contribution future à §XIV-10 |
| 4 | `MAG-PAIR-001` | protocole matière prioritaire identifié, aucune mesure confirmatoire | laboratoire, palier AF, champ test, randomisation, aveugle, exclusions et script final gelés avant la première mesure | §XIV-9 matière et `PRED-MATIERE-ABLATION-001` |

## H052 : décision fail-closed

La fermeture 46/53 n'est pas un manque diffus de documentation. Le graphe est bloqué par une boucle de quatre nœuds. Une réparation minimale existe : recoder `H052` afin que `N051 + N028` produise `N053 + N030`, au lieu d'exiger `N030` en entrée. Cette réparation ferme mathématiquement les 53 nœuds, mais elle reste **non canonique** tant que la source ne justifie pas explicitement la direction causale nécessaire.

L'audit courant est dans `01_branche_matiere/hypergraphe_transformations/fermeture_stricte/AUDIT_H052_2026-08-14.md` et sa version machine dans `AUDIT_H052_2026-08-14.json`.

## Ce qui reste fermé et ne doit pas être relancé sous le même identifiant

- **M2** : formulation paléoclimatique actuelle fermée comme non soutenue. Une future architecture doit avoir un nouvel identifiant et un nouveau gel.
- **WP-CLIM-MEM-2026-B** : construction invalidée par contrôle négatif réel. Le contrôle reste versionné et exécuté en CI.
- **Fischer-Tropsch / C-MAT-MEM-05** : les relations partielles restent documentées, mais elles ne ferment pas la chaîne matière complète. Ajouter une nouvelle famille sans corriger le manque de trace/réponse appariée n'est pas prioritaire.
- **Santos-Lopez 2021** : benchmark externe rétrospectif utile, mais non admissible comme réussite prospective ou réplication stricte du résultat D'Onofrio.

## Industrialisation installée

La CI doit vérifier à chaque `push` et `pull_request` le socle de reproductibilité, le registre de preuves et la démonstration minimale. Les workflows spécialisés continuent à rejouer les campagnes lourdes et les contrôles négatifs sur les branches concernées.

Le site GitHub Pages dispose d'une page interactive séparée des preuves certifiées. Les visualisations interactives utilisent uniquement des sorties ou tables versionnées et affichent explicitement leur statut : donnée empirique, résultat de modèle pré-calculé ou modèle jouet pédagogique.

## Critères avant d'envisager une 1.0

Cette section est une **cible de programme**, pas une annonce de version. Une 1.0 ne devrait être envisagée qu'après des gains de preuve qui ne peuvent pas être obtenus par simple extension documentaire :

1. au moins un résultat prospectif strict réussi et battant son témoin apparié ;
2. au moins une mesure `P_acc` causale sur un système réel ;
3. au moins une réplication indépendante stricte d'un résultat positif ;
4. une présentation publique courte distinguant clairement résultats empiriques, résultats de modèle, résultats négatifs et verrous ouverts.

Le compteur §XIV reste l'autorité opérationnelle. Aucun de ces objectifs ne doit être déclaré atteint avant que les sorties machine correspondantes le permettent.
