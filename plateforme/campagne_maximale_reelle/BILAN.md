# Campagne maximale, données réelles uniquement

> **Instantané historique du 1er août 2026.** Ce bilan décrit la campagne au
> moment où le catalogue comptait 56 moteurs. L'état courant en compte 59 et
> est décrit par `BILAN_CANONIQUE.md`, `ETAT_DES_PREUVES.md` et les résultats
> machine lisibles. Les nombres ci-dessous sont conservés pour la traçabilité
> de cette exécution et ne doivent pas être utilisés comme compteurs actuels.

Date d'exécution : 2026-08-01. Catalogue de cet instantané : 683 entrées, 56 moteurs.

## Règle de la campagne

Aucune donnée synthétique n'est utilisée. Les moteurs qui génèrent un banc,
une expérience, un plan ou une trajectoire numérique sont bloqués. Les
protocoles humains, de laboratoire et de réplication externe restent
`not_run`. Aucun critère scientifique n'est appliqué lorsque sa comparabilité
ou son gel ne sont pas établis.

## Données validées

| Jeu | Lignes |
|---|---:|
| Relations typées | 47 |
| Transitions matérielles | 40 |
| Conditions initiales orbitales JPL | 15 |
| Référence orbitale | 1 381 |
| Paléoclimat LR04/La2004 | 2 601 |

La série orbitale exploitable ne contient que l'excentricité. Les colonnes
obliquité et précession ne sont pas imputées.

## Résultats

| Statut technique | Nombre |
|---|---:|
| Réussites | 147 |
| Échecs | 0 |
| Erreurs | 0 |
| Bloqués | 504 |
| Humain/laboratoire/externe non exécuté | 32 |

Les 147 réussites proviennent de 17 moteurs alimentés par les données réelles :
carte relationnelle, matière, audit des conditions initiales, spectres
orbitaux, chronologie climatique, proxys, hystérésis, identifiabilité,
spectres climatiques, dépendance au chemin, modèles et familles de mémoire.

**Verdict scientifique : 0 soutien, 0 réfutation, 651 indéterminés et 32 non
applicables.** Une réussite indique seulement que le moteur concerné a pu
traiter son jeu réel.

## Blocages principaux

- 144 entrées exclues parce qu'elles exigent génération ou simulation ;
- 96 attendent de vraies lignées prébiotiques ;
- 70 attendent les cycles et mesures d'antibiotiques ;
- 48 attendent des cas de benchmark multi-domaines ;
- le reste attend des données de nucléosynthèse, astro-chimie, phases,
  isotopes, partitionnement, volatils, climat moderne ou biologie.

Les sorties détaillées sont dans `resultats/results.json`, `results.csv` et
`REPORT.md`.
# Extension exoplanetes observationnelles — 2026-08-01

- Source primaire : NASA Exoplanet Archive, table Planetary Systems (`ps`), solutions `default_flag=1`, DOI `10.26133/NEA2`.
- 6 333 planetes confirmees et 6 333 noms uniques au moment de l'extraction.
- Import sans imputation, interpolation, simulation, reechantillonnage ni augmentation.
- Couverture publiee : periode orbitale 94,35 %, rayon 74,64 %, masse 49,46 %, densite 19,45 %, temperature d'equilibre 27,43 %.
- 1 212 objets possedent simultanement masse, rayon et densite publies (19,14 %).
- Ecart median du controle dimensionnel densite contre masse/rayon : 0,90 %.
- 11 methodes de decouverte; le moteur publie leurs effectifs pour rendre visible le biais de selection.
- P4-010 utilise maintenant le moteur `exoplanet_observations`. P3-014 et P6-011, explicitement fondes sur des populations simulees/synthetiques, restent bloques en mode reel strict.
- Campagne : 186 `pass`, 0 `fail`, 0 `error`, 144 `blocked`, 321 `skip`, 32 `not_run`.
- Verdict scientifique de P4-010 : `undetermined` tant qu'un critere confirmatoire preregistre reliant ces observables a ORI-C n'est pas defini.

# Extension antibiotiques et ARN expérimental — 2026-08-01

- Antibiotiques : Windels et al. 2024, Zenodo `10.5281/zenodo.7550302`, *E. coli* exposé quotidiennement à l'amikacine.
- Importés sans imputation : 942 enregistrements de cycles et 1 068 mesures, dont survies longitudinales, MIC et fractions persistantes finales.
- Les phénotypes finaux ne sont pas joints aux trajectoires lorsque le dépôt ne fournit pas l'identifiant de population.
- Gain antibiotique : 52 tests supplémentaires exécutés.
- ARN prébiotique : Papastavrou, Horning & Joyce, Zenodo 10714366 / DOI données `10.5061/dryad.rxwdbrvgs`.
- Importés : 80 enregistrements de fréquences, deux branches de polymérase ribozyme et huit cycles.
- Nouveau moteur `prebiotic_rna_evolution`; 11 questions réellement couvertes ont été spécialisées. Les questions sur membranes, vésicules, compartiments ou cycles géochimiques restent en attente.
- Campagne antérieure étendue : 249 `pass`, 0 `fail`, 0 `error`, 258 `skip`, 144 `blocked`, 32 `not_run`.
- Gain cumulé de cette extension : +63 tests réussis par rapport à la campagne précédente (186 → 249).
- Les 144 blocages de génération/simulation restent intentionnels en mode données réelles strict.
