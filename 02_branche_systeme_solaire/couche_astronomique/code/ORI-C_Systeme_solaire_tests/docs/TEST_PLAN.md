# Plan de test relié à la section 11

## 11.1 — Simulations dynamiques

Code : `backends/rebound_backend.py`

- intégrateur WHFast ou IAS15 ;
- témoin et architectures contrefactuelles ;
- ensembles par perturbation minuscule des angles initiaux ;
- sorties orbitales complètes ;
- dérive relative d’énergie et de moment angulaire ;
- détection simple d’éjection et d’orbite non liée.

Contrôles du protocole maximal :

- vecteurs JPL Horizons DE441 à J2000 ;
- relativité REBOUNDx `gr_potential` sur la trajectoire longue ;
- comparaison courte à IAS15 avec `gr_potential` et `gr_full` ;
- pas WHFast de 0,01, 0,005 et 0,0048828125 an ;
- aller-retour temporel sur 100 000 ans ;
- comparaison à La2010a–d ;
- modèle à huit planètes puis ajout de Pluton et cinq astéroïdes ;
- huit conditions initiales perturbées de \(10^{-10}\) radian.

Encore à ajouter avant une solution de précision La2010 : modèle Terre-Lune
résolu, J2 solaire, marées, ajustement initial complet et croisement
REBOUND/ASSIST.

## 11.2 — Extraction du spectre

Code : `spectral.py`

- périodogramme avec fenêtre de Hann ;
- détection de pics ;
- seuil ponctuel obtenu par surrogates AR(1) ;
- export fréquence, période, puissance et significativité.

Le protocole maximal ajoute un spectre multitaper DPSS, les puissances de bandes
normalisées, les pics ciblés à 95, 125, 405 kyr et 2,4 Myr, ainsi que la
stabilité glissante du pic de 405 kyr.

Restent à ajouter : ondelettes continues, cohérence de phase entre variables et
correction formelle des comparaisons multiples.

## 11.3 — Insolation et marées

Code : `insolation.py`

- insolation journalière selon latitude, longitude solaire, excentricité et longitude du périhélie ;
- canal radiatif séparé des sorties gravitationnelles.

Non inclus dans cette version : potentiel de marée, réponse océanique, nombres de Love, dissipation, obliquité dynamique et précession spin-orbite complète.

## 11.4 — Réponse terrestre

Code : `climate.py`

- inertie thermique ;
- refroidissement lié à une fraction de glace ;
- hystérésis simple gel/fonte ;
- métriques de température, glace et franchissements.

Ce modèle sert à tester la logique « même spectre, récepteur différent ». Il ne remplace pas un modèle climatique spécialisé.

## 11.5 — Comparaison aux archives

Code : `archives.py`

- archive irrégulière ;
- Lomb–Scargle ;
- comparaison des pics et corrélation après interpolation ;
- archive synthétique pour test de bout en bout.

Pour des données réelles, l’âge, la profondeur, les incertitudes et les ancrages indépendants doivent être fournis séparément.

## 11.6 — Expériences contrefactuelles

Code : `experiment.py`, configurations YAML.

Chaque scénario modifie une dimension identifiable autour du témoin. Les métriques finales comparent :

- stabilité dynamique ;
- dérives numériques ;
- périodes spectrales dominantes ;
- insolation moyenne et dispersion ;
- température et fraction glaciaire ;
- nombre de franchissements de seuil.

## 11.7 — Réussite et réfutation

Le rapport automatique ne conclut jamais à une validation générale d’ORI-C. Les
seuils numériques et astronomiques du protocole maximal sont inscrits dans
`configs/real_science_max.yaml` avant le calcul. Le rapport classe :

- pipeline exécutable ou en échec ;
- architecture viable ou instable sur la fenêtre ;
- différence détectable ou noyée dans la dispersion ;
- limites empêchant une conclusion causale.

Une réfutation utile serait obtenue si les modèles dépendants de l’état n’améliorent pas les prédictions hors échantillon, si les effets architecturaux disparaissent sous contrôle numérique, ou si un modèle plus simple explique les archives avec moins de paramètres.
