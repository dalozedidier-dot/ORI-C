# Instructions de mise à jour

## Mise à jour du 7 août 2026 — barrière empirique et données réelles

Cette mise à jour ne doit pas être appliquée par simple copie manuelle sans reconstruire les manifestes. Utiliser le script `APPLIQUER_MISE_A_JOUR.py` fourni dans le paquet de mise à jour.

Le script :

1. vérifie que les fichiers sensibles du dépôt correspondent à l'état attendu avant remplacement ;
2. sauvegarde les fichiers qu'il va modifier ;
3. installe les nouveaux fichiers et les données sélectionnées ;
4. applique les corrections textuelles aux documents courants sans écraser les changements indépendants ;
5. exécute `python build_manifest.py build` ;
6. exécute `python build_manifest.py verify` ;
7. exécute le pare-feu empirique, l'audit des données et les tests ciblés ;
8. restaure la sauvegarde si l'une des étapes obligatoires échoue avant validation finale.

## Résultat attendu de la matrice générique en mode réel strict

- 9 réussites techniques
- 626 blocages
- 48 protocoles non exécutables informatiquement
- 0 échec
- 0 erreur
- 0 verdict scientifique `supports`
- 635 indéterminés
- 48 non applicables

Ces compteurs décrivent la matrice générique avec le pare-feu `fail_closed_v2`. Ils ne remplacent pas les verdicts des protocoles ciblés de branche.

## Données ajoutées

- `late_accretion_tracers.csv` : 122 159 mesures GEOROC ; seule l'auditabilité P5-001 est autorisée, aucun modèle de mélange n'est revendiqué.
- `thermochemical_phases.csv` : 64 512 points calculés depuis des paramètres thermodynamiques publiés ; aucune preuve empirique de condensation n'est revendiquée.
- `volatile_inventory.csv` : dix budgets documentaires incomplets ; aucune valeur absente n'est remplacée par zéro.
- `modern_climate_timeseries.csv` : 7 193 lignes GISTEMP/HadCRUT5 ; les quatre variables restent des reconstructions de température, donc CL1/CL2 ne sont pas débloqués.
- quatre sources paléoclimatiques longues NOAA/EPICA/Vostok/LR04, conservées pour un futur protocole préenregistré sans produire de verdict automatique.

`planetary_histories.csv` reste volontairement absent.

## Contrôles obligatoires après application

```bash
python build_manifest.py verify
python verifier_dossier.py --allow-lfs-pointers
python scripts/valider_barriere_empirique.py
python scripts/auditer_donnees_reelles_2026_08_07.py
python -m pytest -q plateforme/source_corrigee/tests
```

Avec un clone entièrement hydraté LFS :

```bash
git lfs pull
python verifier_dossier.py
python scripts/valider_tout.py --strict-lfs
```

Le détail scientifique de la correction se trouve dans `MISE_A_JOUR_PREUVES_EMPIRIQUES_2026-08-07.md`.
