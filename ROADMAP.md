# ORI-C — roadmap de fermeture scientifique

État de travail : **25 septembre 2026**, réconcilié avec `plan_directeur/VERROUS_ACTIFS.json`. Cette roadmap ne crée aucun nouveau verdict et ne modifie aucune prédiction gelée. Elle réduit le programme actif aux verrous qui peuvent changer le niveau de preuve du dépôt.

Le fichier machine `plan_directeur/VERROUS_ACTIFS.json` est reconstruit en CI à partir des sorties d’autorité afin d’empêcher la roadmap de dériver. Le seuil §XIV reste à **7/12**. Les conditions ouvertes sont **3, 4, 9, 10 et 11** : prédiction prospective hors échantillon, victoire contre témoin apparié, `P_acc` causal dans un système réel, réplications indépendantes strictes et transfert sans redéfinition.

## Les cinq fronts actifs

| Rang | Front | État courant | Donnée ou action manquante | Verrou visé |
|---|---|---|---|---|
| 1 | `PRED-PALEO-HISTORY-03-AGE-ENSEMBLE` | provenance et conception incomplètes, exécution fermée | résoudre l'historique d'accès et préciser le protocole sous une nouvelle version avant toute exécution | test histoire/état et propagation de l'incertitude chronologique, aucun crédit acquis |
| 2 | `VES-PACC-INT-01` | protocole scientifique gelé, laboratoire et matériel non confirmés, enregistrement public manquant | confirmer l'accès expérimental, achever l'enregistrement public préalable et acquérir les nouvelles données selon le protocole | §XIV-9, puis 3/4 si le test prospectif produit un succès qualifié |
| 3 | `MAG-PAIR-001` | pilote installé, six champs de gel laboratoire manquants, minimum de 48 unités indépendantes | confirmer le laboratoire, exécuter le pilote, figer champs, seuils et clé aveugle, puis préenregistrer les analyses | §XIV-9 matière et §XIV-11 avec VES sous `PACC-INT-CHALLENGE-V1` |
| 4 | `PRED-VIVANT-HISTOIRE-001` | aucune réussite prospective stricte, contrôles Windels et Yen-Papin non soutenants à ce jour | poursuivre les nouvelles MIC selon les deux routes LTEE prévues, en distinguant réplication stricte et généralisation | §XIV-3/4, puis §XIV-10 pour la route de réplication stricte |
| 5 | `H052 / HC01 / HC02`, fermeture matière | baseline scellé **46/53**, extension `HC02-E1` **53/53**, matrice sémantique 4/4 | faire relire indépendamment la qualification des sources, conserver le baseline en cas d'objection | consolider l'extension empirique sans promotion du candidat dans le canon |

La route Watkins `PRED-MATIERE-WAVE-HISTORY-001` a été exécutée et reste négative selon son seuil gelé : gain de 3,83 points pour 10 points exigés, sans crédit §XIV. Son résultat demeure visible dans le registre. L'[audit de la route paléoclimatique](plan_directeur/AUDIT_PALEO_ENSEMBLE_03.json) précise les raisons de son blocage. Une chronologie non ajustée constitue une comparaison de robustesse dont le rôle de contrôle négatif reste à justifier.

## H052 : décision fail-closed

La fermeture canonique 46/53 est bloquée par une boucle de quatre nœuds. Deux réparations minimales ferment 53/53 en sensibilité. `HC01` recode H052. `HC02` suit la voie `N051 + N028 → N030`, puis H052 reste strictement canonique. Hao & Li 2018 et Ueda et al. 2021 donnent un support expérimental direct pour l'interface et sa chimie. Zhong et al. 2026 complète la composante « catalyse ». HC02-E1 est qualifiée en extension et atteint 53/53, tandis que le baseline gelé reste 46/53. Le registre courant ne désigne plus HC02 comme prochain audit prioritaire.

L'audit courant est dans `01_branche_matiere/hypergraphe_transformations/fermeture_stricte/AUDIT_H052_2026-08-14.md`, avec matrice sémantique et registre de sources dédiés. Le prochain verrou HC02 n'est plus la recherche d'une quatrième source : c'est une **revue indépendante de la qualification 4/4**. Toute contestation d'une composante doit faire retomber l'extension en fail-closed sans toucher au baseline 46/53.

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

1. au moins un résultat prospectif strict réussi et battant son témoin apparié,
2. au moins une mesure `P_acc` causale sur un système réel,
3. au moins une réplication indépendante stricte d'un résultat positif,
4. une présentation publique courte distinguant clairement résultats empiriques, résultats de modèle, résultats négatifs et verrous ouverts.

Le compteur §XIV reste l'autorité opérationnelle. Aucun de ces objectifs ne doit être déclaré atteint avant que les sorties machine correspondantes le permettent.
