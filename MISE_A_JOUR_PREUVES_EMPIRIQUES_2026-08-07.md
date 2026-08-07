# ORI-C — mise à jour des preuves empiriques du 7 août 2026

Cette mise à jour corrige la frontière entre quatre objets qui étaient insuffisamment séparés dans la plateforme générale : données mesurées, données dérivées, sorties de modèles et fixtures synthétiques.

## Correction principale

Le mode `--real-data-only` est désormais **fail-closed**. La présence physique d'un fichier ne suffit plus à exécuter un protocole comme test empirique. Pour être admis, le jeu doit être déclaré dans `EMPIRICAL_POLICY.json`, porter `eligible_for_empirical_proof = true` et autoriser explicitement le `test_id` concerné. `REAL_DATA_COVERAGE.json` est l'état d'exécution de cette politique et ne peut pas élargir la portée automatiquement.

Cette correction invalide l'usage des anciens compteurs `298/337/48` comme état courant de la matrice empirique stricte. Ces nombres étaient des statuts techniques de plateforme et certains moteurs pouvaient encore s'exécuter sur des tables qui n'étaient pas suffisantes pour le protocole demandé.

Après durcissement, la matrice générique de 683 entrées donne :

- 9 réussites techniques
- 626 blocages explicites
- 48 protocoles non exécutables informatiquement
- 0 échec
- 0 erreur
- 0 verdict `supports`
- 635 verdicts `undetermined`
- 48 `not_applicable`

Les neuf réussites techniques sont `P3-001`, `P3-002`, `P5-001`, `V1-001`, `V1-004`, `B2-003`, `R1-005`, `R1-009` et `R1-010`. Elles signifient seulement que ces protocoles disposent d'une ressource réelle explicitement autorisée pour leur exécution technique. Elles ne remplacent pas les analyses confirmatoires dédiées.

## Données récupérées du corpus `DONNEES_REELLES_ORI-C_2026-08-07`

Le corpus source est identifié par SHA-256 :

`619bbab8482073076aa6d68d6f6947098b584ce40a7f7c78b4d8b2d097840fb2`

Les actifs retenus sont inscrits dans `donnees_externes/donnees_reelles_2026_08_07/SOURCE_BUNDLE.json` avec leur empreinte, leur nature et les usages interdits.

### Traceurs d'accrétion tardive

`late_accretion_tracers.csv` contient 122 159 mesures GEOROC sur 56 614 échantillons. Mo, Ru, W, Os, Ir et Au sont tous présents. La table est une vraie compilation observationnelle, mais `candidate_source` décrit une famille géologique et non un pôle de mélange planétaire, et l'incertitude analytique par mesure n'est pas fournie dans ces exports.

Conséquence : `P5-001` peut auditer la disponibilité et la couverture des traceurs. `P5-002` à `P5-010` restent bloqués tant qu'un modèle de mélange documenté avec pôles, unités et incertitudes n'est pas défini.

### Thermochimie

`thermochemical_phases.csv` contient 64 512 points et 1 025 phases, calculés depuis des paramètres thermodynamiques publiés de CHNOSZ/OBIGT/Berman. Les contrôles directionnels T-P sont conservés comme audit de cohérence numérique.

Cette grille est **une sortie calculée depuis des paramètres publiés**, pas une observation directe d'une séquence de condensation. Le moteur ne choisit plus arbitrairement un minimum global de Gibbs entre compositions différentes. Aucun test M4 n'est débloqué sans composition globale, bilans élémentaires, activités/fugacités et solveur d'équilibre approprié.

### Inventaire volatil

`volatile_inventory.csv` conserve les valeurs publiées et laisse les compartiments inconnus vides. Le moteur ne remplace plus ces absences par `0.0`.

Sur les dix lignes actuelles, aucune ne publie simultanément la masse initiale, le noyau, le manteau, l'atmosphère et la masse perdue. Une somme des compartiments connus est donc seulement une borne partielle, pas une fermeture exacte. Les tests P4 restent bloqués.

### Climat moderne

`modern_climate_timeseries.csv` contient 7 193 lignes issues de GISTEMP v4 et HadCRUT5. Les quatre variables sont des reconstructions de température. Elles ne sont plus interprétées comme quatre compartiments de mémoire ou comme un forçage externe. Les protocoles CL1/CL2 restent bloqués.

### Paléoclimat long

Quatre sources longues sont conservées avec leurs empreintes : EPICA Dome C CO2 jusqu'à environ 799 ka, EPICA dD/température jusqu'à environ 802 ka, Vostok jusqu'à environ 423 ka et LR04 jusqu'à 5,32 Ma.

Elles lèvent le problème de durée du seul fichier 0–22 ka, mais **aucun nouveau verdict orbital-climat n'est produit par leur simple ajout**. Un protocole long doit d'abord geler l'indépendance chronologique, la cible, les bandes, les contrôles, le SESOI et le traitement des incertitudes.

### Histoires planétaires

`planetary_histories.csv` reste délibérément absent. Aucun des fichiers disponibles ne fournit les sept couches historiques demandées avec une provenance primaire vérifiable par cellule. Le fabriquer à partir de descriptions qualitatives produirait un pseudo-jeu de données et est explicitement interdit.

## Moteurs corrigés

- `volatile_budget` : aucune imputation des masses manquantes à zéro.
- `late_accretion` : audit des traceurs, unités et couvertures, sans moyenne brute Mo/Ru/W/Os/Ir/Au présentée comme modèle de mélange.
- `condensation` : audit de la grille thermodynamique, sans faux calcul d'équilibre fermé.
- `modern_climate_memory` : support portable des dates ISO, mais aucune autorisation empirique tant que les variables nécessaires ne sont pas disponibles.
- `runner` : pare-feu empirique fail-closed et test-specific.

## Reproductibilité et publication

`scripts/valider_barriere_empirique.py` vérifie la politique, les empreintes, les autorisations et un ensemble sensible de 57 protocoles. `.github/workflows/audit-empirique-strict.yml` exécute la barrière, les tests spécifiques, l'audit des données et la matrice complète des 683 entrées en mode strict.

`scripts/valider_tout.py` appelle désormais cette barrière. Une publication stable ne peut donc plus être construite si la portée empirique régresse silencieusement.

Les manifestes `MANIFEST.sha256` et `MANIFEST.sha256.json` doivent être reconstruits **après** application des fichiers avec `python build_manifest.py build`, puis vérifiés avec `python build_manifest.py verify`.

## Ce que cette mise à jour ne change pas

Les campagnes ciblées possèdent leurs propres protocoles et restent séparées de la matrice générique. Les résultats dédiés sur données réelles ne doivent ni être promus ni être annulés par un compteur de plateforme. Cette mise à jour corrige précisément ce mélange de niveaux.
