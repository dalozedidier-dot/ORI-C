# ORI-C — Architecture historique du Système solaire

Dépôt expérimental pour transformer la section 11 du document **« Le Système solaire comme architecture historique de contraintes »** en une chaîne quantitative reproductible.

## Ce que le dépôt teste

La chaîne calculée est :

```text
architecture planétaire
→ séries orbitales
→ spectres et stabilité des bandes
→ insolation saisonnière
→ réponse climatique réduite
→ inscription synthétique / comparaison à une archive
→ métriques contrefactuelles
```

Le dépôt sépare volontairement deux usages :

- `surrogate` : signaux synthétiques déterministes servant uniquement à valider le code, les formats et les tests automatisés ;
- `rebound` : intégration gravitationnelle N-corps destinée aux expériences physiques.

**Une réussite du pipeline `surrogate` ne valide aucune hypothèse astronomique ni ORI-C.** Elle prouve seulement que la chaîne logicielle fonctionne. Les conclusions scientifiques doivent reposer sur les sorties du backend N-corps, des contrôles numériques, des ensembles de conditions initiales et des archives indépendantes.

## État scientifique de cette version

Cette version implémente :

1. un témoin et des contrefactuels sur la masse, le demi-grand axe et l’excentricité des planètes ;
2. l’extraction de `a`, `e`, `i`, `Ω`, `ω`, `ϖ` et de la longitude moyenne ;
3. les diagnostics d’énergie et de moment angulaire ;
4. un périodogramme, la recherche de pics et un seuil par surrogates AR(1) ;
5. une insolation journalière au sommet de l’atmosphère à latitude et saison choisies ;
6. un modèle climatique réduit avec inertie et état glaciaire ;
7. une comparaison Lomb–Scargle avec une archive irrégulièrement échantillonnée ;
8. un manifeste d’exécution, les empreintes SHA-256 et un rapport automatique.

Le protocole renforcé `configs/real_science_max.yaml` ajoute :

1. des vecteurs cartésiens J2000 tirés de JPL Horizons DE441 ;
2. la relativité générale par REBOUNDx ;
3. une intégration rétrospective de 20 millions d’années ;
4. des contrôles de convergence du pas et un croisement WHFast–IAS15 ;
5. un modèle enrichi avec Pluton, Cérès, Pallas, Vesta, Iris et Bamberga ;
6. huit trajectoires à conditions initiales quasi identiques ;
7. six interventions architecturales N-corps ;
8. une comparaison directe et spectrale aux solutions indépendantes La2010a–d ;
9. des seuils d’acceptation fixés dans le YAML avant le calcul.

Limites importantes :

- l’obliquité terrestre est prescrite dans cette version ; le couplage complet rotation-orbite n’est pas encore intégré ;
- la Lune est représentée par le barycentre Terre-Lune dans les conditions initiales ;
- la relativité générale est optionnelle et les marées séculaires ne sont pas intégrées ;
- le modèle climatique est un modèle de réponse réduit, pas un GCM ;
- les éléments J2000 historiques restent disponibles pour contrôle, mais les tests longs utilisent les vecteurs Horizons ;
- `gr_potential` préserve la structure symplectique et reproduit la précession, sans remplacer le modèle relativiste complet de La2010.

Ces limites sont affichées dans chaque rapport afin d’éviter toute surinterprétation.

## Installation rapide

Python 3.11 ou 3.12 est recommandé.

### Test complet de la chaîne logicielle

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.lock.txt
python -m pip install --no-build-isolation --no-deps -e .
python -m compileall -q src tests
python -m ruff check .
python -m pytest
python -m oric_solar_history run --config configs/smoke_surrogate.yaml
python -m oric_solar_history run --config configs/rebound_quickcheck.yaml
```

Les résultats sont écrits dans `runs/smoke_surrogate/` et
`runs/rebound_quickcheck/`. Le fichier `requirements.lock.txt` fixe
l’environnement utilisé pour la validation finale.

### Backend N-corps

```bash
python -m oric_solar_history doctor
python -m oric_solar_history run --config configs/rebound_quickcheck.yaml
```

Le fichier `configs/rebound_science_2myr.yaml` fournit une base pour une intégration séculaire. Il est volontairement séparé du test rapide.

### Validation scientifique maximale

Cette exécution utilise plusieurs cœurs et peut durer de plusieurs dizaines de
minutes à quelques heures selon la machine.

```bash
python -m venv .venv-science
# Linux/macOS
# source .venv-science/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.science.lock.txt
python -m pip install --no-build-isolation --no-deps -e .

python scripts/run_real_science_suite.py \
  --config configs/real_science_max.yaml \
  --overwrite

python scripts/analyze_real_science_suite.py \
  --config configs/real_science_max.yaml
```

Les calculs interrompus peuvent être repris sans refaire les jobs intacts :

```bash
python scripts/run_real_science_suite.py \
  --config configs/real_science_max.yaml \
  --resume
```

Le rapport final est écrit dans
`runs/real_science_max/analysis/SCIENTIFIC_VALIDATION_REPORT.md`.

### Résultat de l’exécution de référence

L’exécution du 29 juillet 2026 a terminé les 25 jobs et 20 millions d’années
du témoin. Treize critères préenregistrés sur quinze sont réussis. Les résultats
principaux sont :

- corrélation avec JPL Horizons DE441 sur 6 000 ans : `0,9999998095`
- corrélation avec La2010a à 1 Myr : `0,9972696754`
- corrélation avec La2010a à 2 Myr : `0,9914236522`
- pic de 405 kyr calculé : `408 184 ans`, identique au pic extrait de La2010a
- convergence du pas 0,01 contre 0,005 an : RMSE `8,43 × 10⁻⁷`
- WHFast contre IAS15 : RMSE `3,13 × 10⁻⁷`
- six effets contrefactuels supérieurs de plus de six millions de fois au
  plancher de l’ensemble sur 2 Myr

Les deux échecs restent publiés : l’aller-retour au pas 0,01 an dépasse son
seuil alors que le pas 0,005 le réussit, et le diagnostic newtonien de moment
angulaire dépasse son seuil pour le contrôle 1PN `gr_full`. Les résultats et
leurs limites sont résumés dans `docs/REAL_SCIENCE_RESULTS.md`.

## Commandes principales

```bash
python -m oric_solar_history doctor
python -m oric_solar_history check-config --config configs/smoke_surrogate.yaml
python -m oric_solar_history run --config configs/smoke_surrogate.yaml
python -m oric_solar_history make-demo-archive --output data/demo_archive.csv
python -m oric_solar_history compare-archive \
  --forcing runs/smoke_surrogate/baseline/insolation.csv \
  --archive data/demo_archive.csv \
  --output runs/archive_comparison
```

## Organisation

```text
configs/                    configurations reproductibles
src/oric_solar_history/     code scientifique
src/.../backends/           surrogate et REBOUND
src/.../spectral.py         analyses fréquentielles et bruit rouge
src/.../real_validation.py  comparaison La2010 et multitaper
src/.../insolation.py       traduction orbitale-radiative
src/.../climate.py          réponse terrestre réduite
src/.../archives.py         archives irrégulières et Lomb–Scargle
scripts/                    acquisition, calcul parallèle et analyse
tests/                      tests unitaires et test de bout en bout
docs/TEST_PLAN.md           correspondance avec la section 11
data/planetary_j2000.csv    conditions initiales et masses
data/horizons_*.csv         vecteurs JPL DE441 figés
data/reference/la2010/      solutions orbitales indépendantes
docs/source/                document source fourni par Didier Daloze
```

## Données initiales

Les éléments orbitaux J2000 proviennent de la table « Approximate Positions of the Planets » du JPL Solar System Dynamics. Le JPL précise que ces éléments ajustés sont destinés à des positions approximatives et ne remplacent pas Horizons pour la haute précision. Les masses sont dérivées des paramètres physiques planétaires du JPL et exprimées en masses solaires.

Le catalogue Horizons est conservé à la racine du dépôt et dans les données du
paquet Python. Les réponses brutes, les requêtes, les sources de masses et les
empreintes sont conservées dans `data/HORIZONS_PROVENANCE.md`. Un contrôle
automatisé vérifie que le catalogue installé reste accessible hors d’un dépôt
Git.

Sources :

- JPL Solar System Dynamics, Approximate Positions of the Planets: https://ssd.jpl.nasa.gov/planets/approx_pos.html
- JPL Horizons API: https://ssd-api.jpl.nasa.gov/doc/horizons.html
- JPL Solar System Dynamics, Planetary Physical Parameters: https://ssd.jpl.nasa.gov/planets/phys_par.html
- REBOUND: https://github.com/hannorein/rebound
- REBOUNDx: https://reboundx.readthedocs.io/en/latest/effects.html
- La2010, données IMCCE: https://ssp.imcce.fr/insola/earth/online/earth/La2010/
- SciPy spectral analysis: https://docs.scipy.org/doc/scipy/reference/signal.html

## Critères minimaux avant interprétation scientifique

Une expérience N-corps ne doit être interprétée que si :

- le témoin reproduit qualitativement les bandes attendues sur une fenêtre assez longue ;
- la dérive relative d’énergie et de moment angulaire reste documentée et acceptable pour la question posée ;
- les résultats sont stables face au pas de temps, à l’intégrateur et aux conditions initiales ;
- une architecture instable est classée séparément ;
- les pics sont comparés à des processus nuls rouges et à plusieurs fenêtres d’analyse ;
- les effets contrefactuels dépassent la dispersion entre réalisations ;
- les archives utilisées disposent d’un modèle âge-profondeur indépendant de la bande recherchée.

## Licence

Code du dépôt : MIT. Les dépendances conservent leurs licences propres. REBOUND est distribué sous GPL-3.0 et n’est pas inclus dans cette archive ; il est installé séparément. Ne soumettez pas ce code comme contribution automatique au projet REBOUND.

## Auteur et cadre

Didier Daloze — ORI-C — juillet 2026.
