# Validation finale du dépôt

Date : 29 juillet 2026

## Environnement contrôlé

- Python 3.12.13
- environnement virtuel isolé
- dépendances fixées dans `requirements.lock.txt`
- REBOUND 5.0.1

## Contrôles exécutés

```bash
python -m compileall -q src tests
python -m ruff check .
python -m pytest
python -m oric_solar_history run --config configs/smoke_surrogate.yaml --overwrite
python -m oric_solar_history run --config configs/rebound_quickcheck.yaml --overwrite
```

Résultats :

- 7 tests automatisés réussis
- contrôle statique Ruff réussi
- pipeline synthétique exécuté de bout en bout
- 4 scénarios synthétiques comparés
- sorties numériques du smoke identiques aux résultats fournis, hors manifeste d’environnement enrichi
- bande synthétique dominante retrouvée à environ 400 333 ans
- backend REBOUND exécuté sur 200 ans pour le témoin et une masse de Jupiter augmentée de 5 %
- tous les corps sont restés liés pendant le quickcheck
- dérive relative maximale d’énergie du témoin : environ 5,32 × 10⁻¹³
- dérive relative maximale de moment angulaire du témoin : environ 1,11 × 10⁻¹⁴

## Corrections issues de la validation

Le contrôle final a corrigé trois défauts avant gel du paquet :

1. un import inutilisé qui faisait échouer Ruff
2. l’ancien argument `hash` remplacé par `name` pour REBOUND 5.0.1
3. la séparation entre la grille de sortie demandée et le temps réellement atteint par l’intégrateur lorsque `exact_finish_time: false`

Le catalogue planétaire est maintenant inclus dans le paquet Python. Une
installation depuis une roue ne dépend donc plus de la présence du dossier
`data/` à la racine du dépôt.

## Limite scientifique

Le run `surrogate` vérifie uniquement la chaîne logicielle. Le quickcheck
REBOUND vérifie l’exécution technique du backend sur une courte fenêtre. Aucun
de ces deux contrôles ne valide une hypothèse astronomique ni le cadre ORI-C.
La configuration de 2 millions d’années est fournie, mais elle n’a pas été
exécutée dans cette validation finale.
