# Couche spin-orbite Terre-Lune

Cette couche prolonge les sorties N-corps déjà certifiées jusqu'au **spin terrestre, à l'obliquité et à l'insolation**.

Elle est exécutée sur les sorties de `couche_astronomique/resultats/real_science_max` et comparée directement à la solution publiée **La2004** déjà figée dans le dépôt.

Le modèle est séculaire et réduit. La Lune est représentée par sa contribution effective à la constante de précession du spin :

- Terre actuelle : `α = 54,93 arcsec/an` ;
- ablation lunaire : `α ≈ 20 arcsec/an`, couple solaire seul.

La normale orbitale `n(t)` et l'excentricité viennent de l'intégration N-corps à huit planètes. L'axe de spin est intégré dynamiquement. L'équinoxe mobile est reconstruit géométriquement, puis la longitude du périhélie et l'insolation journalière à `65°N` au solstice d'été sont calculées.

## Exécution

```bash
cd 02_branche_systeme_solaire/couche_spin_orbite
python run_spin_orbit.py --overwrite
pytest -q tests
python - <<'PY'
from pathlib import Path
from spin_orbit import verify_results_manifest
verify_results_manifest(Path('resultats'))
print('résultats conformes')
PY
```

## Portée

Cette couche calcule effectivement :

`architecture N-corps → spin → obliquité → insolation`.

Elle ne résout pas explicitement l'orbite mensuelle de la Lune, les marées ni l'évolution de la distance Terre-Lune. Ces éléments restent une extension physique de long terme et ne sont pas nécessaires pour tester ici l'effet stabilisateur du couple lunaire sur le spin séculaire.

## Reproductibilité numérique

Le contrôle CI distingue deux régimes au lieu d'imposer une identité point par point artificielle sur toute la fenêtre :

- avec couple lunaire effectif, la trajectoire est comparée point par point sur 20 Ma à `rel=1e-10`, `abs=1e-10` ;
- pour l'ablation lunaire, la comparaison point par point est conservée jusqu'à 2 Ma ; au-delà, la sensibilité chaotique aux derniers bits rend une identité trajectorielle de 20 Ma inappropriée, donc les statistiques canoniques de `summary.json` sont comparées avec une tolérance locale de `2e-6` relative et `2e-5` absolue ;
- les rapports effet/plancher utilisent la même tolérance locale, car leur dénominateur est une dispersion d'ensemble de l'ordre de `1e-9` ;
- `resultats/viabilite/` est recalculé et contrôlé séparément par le workflow des formalismes externes, car ce sous-dossier n'est pas produit par `run_spin_orbit.py`.

Le script d'autorité est `scripts/verifier_reproductibilite_spin_orbite.py`. Cette séparation ne modifie aucun résultat scientifique ni aucun critère de validation La2004.
