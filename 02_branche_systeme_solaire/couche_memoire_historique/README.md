# Tests ORI-C de mémoire historique

Ce paquet implémente les deux protocoles définis pour la branche
Système solaire–Terre d’ORI-C, dans leur version corrigée.

1. Le test MPT ajuste les modèles entre 2,6 et 1,2 Ma, fige tous les
   paramètres, puis prédit la période 1,2–0 Ma.
2. Le test exoplanétaire impose deux histoires spin-orbitales différentes qui
   aboutissent exactement au même forçage final. Il compare un modèle
   classique, M2 et M2 privé de ses mémoires dynamiques.

Le paquet sépare trois statuts :

- test de code et de structure
- test empirique préliminaire
- validation physique

Une réussite structurelle du test exoplanétaire ne vaut donc pas validation
GCM. Une baisse de RMSE sur LR04 ne vaut pas reproduction de la MPT si la
bande de 100 ka et la chronologie ne sont pas retrouvées.

## Corrections apportées à la première version

La première version du protocole comportait cinq défauts qui rendaient son
verdict positif partiel non concluant. Ils sont corrigés ici.

| Défaut | Effet | Correction |
|---|---|---|
| M2 n’était comparé qu’à M1, moins complexe | Un avantage pouvait venir de la seule complexité | Ajout de M1P, témoin à complexité égale sans mémoire d’état |
| BIC calculé sur 1 200 points supposés indépendants | Résidus autocorrélés à 0,97 : la pénalité de complexité devenait négligeable | BIC sur taille d’échantillon efficace, compte brut conservé à côté |
| Quatre paramètres de M2 à l’optimum sur une borne | La boîte, non les données, fixait une partie de la solution | Bornes élargies d’au moins un ordre de grandeur |
| Palier final exoplanétaire de 10 Ma | Plus court que les mémoires de 8 et 60 Ma qu’il devait mesurer | Ajout d’un critère de persistance sur palier long |
| Une troisième symétrie exacte subsistait dans M2 | M2 n’avait que 8 degrés de liberté sur 9, et le test d’ablation carbone n’était pas défini | Décalage de l’état lent fixé à zéro par définition |

Le témoin M1P est le point central. Il possède exactement les mêmes paramètres
que M2 et une constante de temps lente supplémentaire, mais son état lent filtre
le **forçage astronomique externe** au lieu d’inscrire la **réponse passée du
système**. C’est la seule différence. Un avantage de M2 sur M1 mesure de la
flexibilité ; seul un avantage de M2 sur M1P mesurerait la mémoire historique
revendiquée par ORI-C.

## Résultat actuel

Le résultat chiffré complet est dans `REPORT.md`. La campagne de contrôles
supplémentaires est dans `STRESS_REPORT.md`.

- MPT : M2 réduit l’erreur par rapport à M1, mais perd nettement contre M1P.
  L’avantage sur M1 n’est pas distinguable d’un effet de complexité. La
  transition spectrale vers 100 ka n’est reproduite par aucun modèle ajusté.
- Exoplanète : la dépendance au chemin et son ablation sont détectées dans
  l’EMIC réduit, mais l’écart s’efface intégralement lorsque le forçage final
  commun est maintenu au-delà des constantes de temps du modèle. Il s’agit
  d’un retard de relaxation, non d’une inscription durable.

## Exécution

```bash
cd ORI-C_tests_memoire_historique
export PYTHONPATH="$PWD/src"
export MPLCONFIGDIR="${TMPDIR:-/tmp}/oric-memory-tests-matplotlib"
python3 -m oric_memory_tests --root "$PWD" run-all --config configs/primary.json
```

Test rapide :

```bash
python3 -m oric_memory_tests --root "$PWD" run-all --config configs/smoke.json
```

Tests unitaires :

```bash
PYTHONPATH="$PWD/src" python3 -m unittest discover -s tests -v
```

Campagne de contrôles supplémentaires :

```bash
cd stress && python3 verify_core.py && python3 a_mpt.py && python3 b_exo.py
```

### Note de performance

Le budget d’optimisation corrigé exige plusieurs centaines de milliers
d’évaluations par modèle. `oric_memory_tests.fastcore` fournit une
transcription de `simulate_mpt` compilée par numba, vérifiée par la suite de
tests avec une tolérance de 1e-11. Sur l'environnement de livraison l'écart est
exactement nul ; la tolérance absorbe les réordonnancements flottants d'autres
versions de bibliothèques. Sans numba le calcul reste exact mais
environ cent fois plus lent.

## Architecture des modèles MPT

| Modèle | Paramètres | États | Rôle |
|---|---:|---|---|
| M0 | 3 | glace | réponse orbitale à temps de relaxation fixe |
| M1 | 6 | glace, régolithe | témoin historique classique |
| M2 | 8 | glace, régolithe, carbone | M1 enrichi d’une mémoire ORI-C |
| M1P | 8 | glace, régolithe, filtre lent du forçage | témoin à complexité égale, sans mémoire d’état |

Les états R et C sont normalisés et le décalage de l’état lent est fixé à zéro.
Ces trois choix retirent trois symétries exactes : α/R*, β/γ, et le couple
(décalage de l’état lent, décalage du forçage). Sans eux, plusieurs paramètres
seraient mathématiquement non identifiables et le test d’ablation serait
indéterminé.

## Critères MPT

Les cinq critères sont évalués contre chacun des deux témoins.

- gain de RMSE hors échantillon d’au moins 5 %
- ΔBIC inférieur ou égal à −10, sur taille d’échantillon efficace
- rapport spectral 100/41 ka dans un facteur 2 de LR04
- corrélation d’au moins 0,4 et erreur moyenne des terminaisons inférieure à
  25 ka
- avantage bloc par bloc avec p < 0,05

Le verdict global exige la réussite de tous les critères contre les deux
témoins.

## Critères exoplanétaires

- forçage final strictement identique
- différence A–B de M2 supérieure à celle de M2 sans mémoire pour au moins
  deux variables, avec correction de Holm
- disparition d’au moins 90 % du signal lors de l’ablation
- seuils de matérialité séparés pour température, glace, CO₂ et productivité
- persistance : au moins deux variables conservent un dixième de leur écart, et
  restent au-dessus du seuil de matérialité, après un palier final trente fois
  plus long

## Limites

LR04 est une cible majeure, mais sa chronologie est orbitalement accordée à une
insolation estivale à 65°N. Ce test n’est donc pas totalement indépendant du
forçage astronomique employé.

Les trajectoires exoplanétaires sont des forçages contrôlés. Elles ne sont pas
encore produites par une intégration N-corps-spin validée, et le climat réduit
n’est pas calibré sur ROCKE-3D, WACCM6 ou GEOCLIM.

## Sources

- Lisiecki, L. E. et Raymo, M. E. (2005), LR04,
  doi:10.1029/2004PA001071, jeu NOAA doi:10.25921/k88j-0106
- Laskar et al. (2004), La2004,
  doi:10.1051/0004-6361:20041335, données IMCCE
