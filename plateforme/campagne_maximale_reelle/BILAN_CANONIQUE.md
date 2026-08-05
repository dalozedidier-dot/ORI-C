# Campagne réelle consolidée - bilan canonique

Date de réexécution : 5 août 2026. Catalogue : 683 entrées.

## Méthode

La campagne commence par `integrer_donnees_existantes.py`. Cette étape raccorde les données réelles déjà réparties dans le dépôt, puis le lot scientifique reçu le 5 août 2026. Aucune valeur absente n'est inventée. Une table partielle ne débloque que les identifiants inscrits dans `REAL_DATA_COVERAGE.json`.

Les gabarits de `plateforme/source_corrigee/examples/data/` restent exclus.

## Apport du nouveau lot scientifique

| Bloc | Volume intégré | Portée réelle |
|---|---:|---|
| Ensembles climatiques | 142 745 lignes, 83 modèles ou sources, 8 scénarios | observations et incertitudes, CMIP6 multi-modèles, scénarios SSP, expériences idéalisées |
| Réseaux réactionnels | 16 434 réactions, 2 réseaux | construction versionnée, incertitudes de taux, réplication KIDA/UMIST |
| Conditions initiales astro-chimiques | 19 espèces | inventaire initial Rate22, distinct d'un inventaire radioastronomique |
| Nucléosynthèse CCSN | 1 383 rendements élémentaires et 56 507 isotopiques | effet de trois masses stellaires dans six familles CCSN |
| Traceurs isotopiques | 362 mesures D/H, 13 Ca lunaires et 9 Mn-Cr auxiliaires | compilation de traceurs disponibles, sans prétendre tester la dichotomie complète CC/NC |
| Partage métal-silicate | 41 expériences, dont 35 complètes | compilation, harmonisation et méta-régression exploratoire |
| Endosymbiotes | 85 génomes et 15 810 résultats HMM | réduction génomique uniquement |
| Dégazage de Murchison | 3 648 mesures | table auxiliaire, sans bilan volatil fermé |
| Propriétés thermiques de météorites | 61 échantillons | table auxiliaire |

La compilation d'acides aminés comprend 1 387 mesures dans 69 environnements. Elle est conservée séparément et n'est pas présentée comme un inventaire interstellaire observé.

## Résultat des 683 entrées

| Statut technique | Avant toute intégration | Après données du dépôt | Après nouveau lot |
|---|---:|---:|---:|
| Réussites | 211 | 278 | **298** |
| Blocages | 440 | 357 | **337** |
| Protocoles non exécutés informatiquement | 32 | 48 | **48** |
| Échecs | 0 | 0 | **0** |
| Erreurs | 0 | 0 | **0** |

Le nouveau lot débloque **20 analyses supplémentaires**. Aucune entrée n'est reclassée en réussite par la seule présence d'un fichier.

## Analyses nouvellement exécutées

- M2-004 : effet des masses stellaires sur les rendements CCSN, avec trois masses et six familles de modèles
- M3-001, M3-011 et M3-015 : réseau astro-chimique versionné, couverture des incertitudes et réplication par un second réseau
- P1-001 : compilation et analyse exploratoire des traceurs isotopiques disponibles
- P3-003 à P3-005 : méta-régression, interactions et comparaison de lois de partage sur la compilation étendue
- CL3-001 à CL3-003, CL3-006 et CL3-007 : domaine accessible et trajectoires climatiques multi-scénarios
- CL4-001 à CL4-003, CL4-005 à CL4-007 : observations, ensembles multi-modèles, expériences idéalisées et robustesse
- B2-003 : réduction génomique de 85 endosymbiotes

## Résultats exploratoires du nouveau lot

Les rendements CCSN couvrent 84 éléments valides. La variation relative médiane entre les trois masses est de 0,457. Ce résultat décrit les modèles fournis et ne compare ni AGB, ni BBN, ni fusions compactes.

Les réseaux KIDA 2024 et UMIST Rate22 totalisent 16 434 réactions et 642 espèces dans le graphe. Les deux réseaux sont distingués et 46,7 % des lignes possèdent un facteur d'incertitude exploitable. Les 19 conditions initiales Rate22 recouvrent entièrement les espèces correspondantes du réseau. Aucun inventaire radioastronomique n'est revendiqué.

La méta-régression métal-silicate utilise 35 lignes complètes et produit un R² exploratoire de 0,632. Ce nombre ne valide pas encore des trajectoires d'accrétion ou des histoires planétaires.

Les 85 génomes endosymbiotiques présentent une rétention génomique médiane de 0,817, avec une étendue de 0,640. Il s'agit de proxys HMM de réduction génomique, pas de mesures directes du transfert nucléaire ou de la dépendance à l'hôte.

## Statut scientifique

| Verdict scientifique | Nombre |
|---|---:|
| Soutient | 0 |
| Ne soutient pas | 0 |
| Indéterminé | 635 |
| Non applicable | 48 |

Les 298 réussites restent techniques ou exploratoires. Aucun critère confirmatoire gelé n'autorise encore un verdict global de soutien ou de rejet.

## Blocages restants

Les causes détaillées sont dans `AUDIT_DONNEES_DEPOT.md` et `AUDIT_DONNEES_DEPOT.json`. Les quatre tables quantitatives encore entièrement absentes sont :

- `thermochemical_phases.csv`
- `planetary_histories.csv`
- `late_accretion_tracers.csv`
- `volatile_inventory.csv`

Les autres blocages viennent de la portée partielle des données, de simulations interdites en mode réel strict ou de protocoles humains et expérimentaux non exécutables par le logiciel.
