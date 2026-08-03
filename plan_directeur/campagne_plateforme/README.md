# Campagne plateforme — exécution du plan directeur par `oric-full`

> **État historique.** Les compteurs 175/235 ci-dessous décrivent les deux premières campagnes du plan directeur. Le bilan consolidé actuel fait autorité pour l’état présent : 211 réussites techniques, 440 blocages, 32 non-exécutions et aucun soutien confirmatoire. Voir `../../plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`.

**Statut : exécution outillée du plan. Aucun résultat ne soutient une
hypothèse ORI-C.**

Cette campagne exécute le plan directeur au moyen de la plateforme
`oric_full_research 0.2.0`, indépendante du dossier. Elle apporte deux choses
que le dossier n'avait pas : une **couverture exhaustive du plan** — 683
entrées, 51 work packages — et une **séparation stricte** entre le statut
technique et le verdict scientifique.

> `technical_outcome` — le moteur s'est-il exécuté ?
> `scientific_verdict` — le résultat satisfait-il un critère gelé avant analyse ?

Sans critère gelé, le verdict scientifique reste `undetermined`, même quand le
statut technique vaut `pass`.

## Résultats des deux campagnes

| | Campagne 1 | Campagne 2 |
|---|---:|---:|
| `pass` technique | 175 | **235** |
| `fail` | 30 | 30 |
| `error` | 430 | **0** |
| `blocked` | 0 | **370** |
| `not_run` | 48 | 48 |
| `supports` | 2 (rejetés, voir ci-dessous) | 6 dont **4 contrôles positifs** |
| `does_not_support` | 1 | **2** |
| `inconclusive` | 2 | 1 |
| `undetermined` | 630 | 626 |

**Aucun `supports` ne soutient ORI-C.** Les quatre de la campagne 2 sont des
**contrôles positifs** déclarés comme tels au gel : ils testent l'instrument
contre des valeurs publiées extérieures. Les deux restants portent sur des
quantités de procédure, pas sur une hypothèse du cadre.

## Les trois résultats réels

### Les périodes de Milankovitch, retrouvées sur La2004 brut

| Observable | Mesuré | Canonique |
|---|---:|---:|
| Excentricité | **404,77 ka** | 405 ka |
| Obliquité | **40,22 ka** | 41 ka |
| Précession | **18,79 ka** | 19–23 ka |

Contrôle positif réussi : le moteur et le mappage des données sont corrects.

Cela **complète** le résultat du WP-C6 du dossier, qui établissait que la bande
de 405 ka n'est pas résolvable sur une fenêtre de 1200 ka — un seul point de
fréquence. Sur les 51 Ma de La2004 elle est la période dominante. Les deux
constats sont vrais : la bande existe, la fenêtre climatique ne la porte pas.

### L'horizon de divergence chaotique — WP-A2.9

Dispersion relative entre les quatre solutions La2010, également admissibles :

| Fenêtre | Dispersion |
|---|---:|
| 0 – 2,6 Ma | **2,02 × 10⁻⁴** |
| 0 – 10 Ma | 5,61 × 10⁻⁴ |
| 0 – 20 Ma | 1,84 × 10⁻³ |
| 0 – 40 Ma | 3,56 × 10⁻² |
| 0 – 100 Ma | 4,65 × 10⁻¹ |

Franchissement du 1 % à **6,9 Ma**, du 50 % à 23,9 Ma. Le chiffre sur 0–2,6 Ma
recoupe le test T3 du dossier, qui donnait 5,2 × 10⁻⁴ sur une grille plus
grossière.

**Conséquence vérifiée, WP-A2.10.** En tronquant la table de référence à
l'horizon du 1 %, l'écart entre La2004 et la moyenne des La2010 passe de
**1,79 × 10⁻²** à **2,31 × 10⁻⁵** — facteur **775**, obtenu uniquement en
cessant d'interpréter au-delà de l'horizon de fiabilité.

### Confirmation indépendante sur la carte relationnelle

Le moteur `relation_graph` de la plateforme calcule une AUC de prédiction de
liens masqués de **0,4938**. L'analyse indépendante du dossier
(`00_socle/carte_relationnelle/ANALYSE_GRAPHE.md`) donnait **0,491 ± 0,032**.
Deux codes écrits séparément, même conclusion.

## Les données réellement employées

8 tables sur 31 valident, **toutes en données réelles**. Aucune donnée
synthétique n'est entrée : le gabarit de lignées prébiotiques du dossier, qui
porte le marqueur `GABARIT_SYNTHETIQUE`, a été explicitement retiré.

| Table | Source | Lignes |
|---|---|---:|
| `orbital_timeseries` | solution La2004 de Laskar | 51 001 |
| `paleoclimate_timeseries` | LR04 sur grille de 1 ka | 2 601 |
| `orbital_reference` | quatre solutions La2010, tronquées à 6,9 Ma | 1 381 |
| `relations` | carte relationnelle du socle | 47 |
| `matter_transitions` | base WP-M1 du dossier | 40 |
| `ephemerides` | Horizons DE441 | 15 |
| `orbital_initial_conditions` | Horizons DE441 avec masses | 15 |
| `states` | table d'états du protocole | 3 |

Les 370 blocages restants sont des données que le dossier ne contient pas :
chimie interstellaire, pétrologie expérimentale, lignées prébiotiques,
cultures bactériennes, ensembles climatiques.

## Deux désaccords non résolus

**Le vocabulaire des relations est incompatible.** La plateforme accepte
`{DESC, TRANS, ASSOC, INTG, CLOS, PERT, COND, HERIT}` ; le `CODEBOOK.md` du
socle en définit 13, dont **3 seulement se recoupent**. Les 16 tests S3
échouent pour cette raison. Les codes du dossier n'ont **pas** été remappés :
cela aurait fabriqué un accord qui n'existe pas. À trancher.

**Les six dimensions sont vides.** `missing_fraction = 1,0` sur les 40
transitions. Les 14 tests M1 échouent en conséquence, et c'est le bon
résultat : aucune source du dossier ne les renseigne.

## Six correctifs apportés à la plateforme

Le wheel distribué n'est pas modifié ; les correctifs portent sur la copie
extraite et sont enregistrés dans `correctifs/correctifs.json` avec les
empreintes des fichiers touchés, pour remontée à l'auteur du paquet.

| # | Défaut | Effet |
|---|---|---|
| 1 | `<` et `<=` ne lisaient que `threshold_low` | une borne supérieure déclarée dans `threshold_high` rendait le verdict `does_not_support` **quelle que soit la valeur** |
| 2 | les clés `rmse`, `cv_gain`, `oos_gain`, `holdout_fraction`, `failed_validations` n'étaient pas publiées | cinq verdicts `inconclusive` |
| 3 | des critères étaient gelés pour des tests `human_review` ou `laboratory` | couverture fictive ; le gel est désormais filtré par le mode lu dans le catalogue |
| 4 | chemins Windows absolus | scripts non déplaçables ; tout est passé en arguments |
| 5 | deux catalogues gelés coexistaient | une seule autorité, `catalogue_frozen.json` |
| 6 | une table vide levait une exception générique | 430 « pannes » qui étaient des données manquantes, désormais `blocked` |

## Trois défauts de mes propres critères, corrigés entre les deux campagnes

Tous constatés **après** la campagne 1 et corrigés par une **nouvelle
préinscription** avec de nouveaux identifiants, conformément au §XIII du plan.

| Critère | Défaut | Correction |
|---|---|---|
| `cv_gain` | mesurait la dispersion entre blocs, pas un gain contre témoin apparié ; positif dès que les blocs diffèrent | renommé `cv_dispersion_entre_blocs`, son critère retiré |
| `oos_gain > 0` | seuil vide, franchi par un gain de 0,1 % | relevé à 0,05 ; le test bascule alors en `does_not_support` |
| `holdout_fraction > 0,20` | inégalité stricte sur la valeur exacte du bord | rendue large |

Le premier fabriquait un faux `supports`. Le corriger était plus important que
tout le reste de la campagne.

## Reproduire

```bash
python -m oric_full audit --output audit/platform_audit.json
python -m oric_full bootstrap <espace>
python mapper_donnees_reelles.py --dossier <ORI-C_dossier_unique> --data-dir <espace>/data
python -m oric_full validate-data --data-dir <espace>/data
python preregistrer_campagne2.py --grille <espace>/preregistration/criteria.csv --catalogue <catalogue>/catalogue_tests.csv
python -m oric_full run --all --data-dir <espace>/data --output-dir <espace>/results/campagne2 --criteria-file <espace>/preregistration/criteria.csv
```

La plateforme exige `typer`, `pydantic`, `rich`, `jsonschema`, `scikit-learn`
et `statsmodels`, absents de l'environnement du dossier. Elle a été chargée
sans installation système, dépendances isolées dans un répertoire dédié.

## Autorité

Ce répertoire ne fixe **aucun statut**. `ETAT_DES_PREUVES.md` et
`REGISTRE_HYPOTHESES.csv` restent seuls compétents. Les 235 réussites
techniques prouvent que le code s'exécute sur des données réelles — pas que le
cadre ORI-C soit soutenu.
