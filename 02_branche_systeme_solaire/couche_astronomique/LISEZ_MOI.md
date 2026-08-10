# ORI-C — validation scientifique maximale du Système solaire

Ce paquet contient 25 calculs N-corps et contrôles numériques issus du commit `969edb2e5262d3160313ce8e42c0f38e47409725`.

Le protocole préenregistré est **partiellement réussi** : 13 critères réussis et 2 échoués.

Commencez par :

```bash
python scripts/verifier_paquet.py
```

Le rapport scientifique complet se trouve dans :

`resultats/real_science_max/analysis/SCIENTIFIC_VALIDATION_REPORT.md`

La procédure de recalcul se trouve dans `REPRODUCTION.md`.

Les sorties incluent la trajectoire terrestre, les invariants, les échantillons de tous les corps, les comparaisons JPL Horizons et La2010, les spectres multitaper, les contrefactuels et l’ensemble de sensibilité.

La feuille de route prospective pour les fréquences séculaires, les quatre géantes et le futur couplage spin-orbite Terre-Lune est documentée dans `code/ORI-C_Systeme_solaire_tests/docs/EXTENSION_ARCHITECTURE_GLOBALE_SPIN_ORBITE.md`. Elle ne modifie pas le verdict de l'exécution publiée.
