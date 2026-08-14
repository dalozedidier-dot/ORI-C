# ORI-C en 10 minutes

Cette page vise un lecteur extérieur qui veut vérifier le dépôt sans parcourir l’ensemble du catalogue. Elle ne remplace pas la documentation scientifique.

## 1. Installation

```bash
git clone https://github.com/dalozedidier-dot/ORI-C.git
cd ORI-C
git lfs pull
python -m pip install -r plateforme/source_corrigee/requirements-lock.txt
```

## 2. Reproduire les trois résultats phares

```bash
python demo_minimale.py
```

La partie biologique réexécute les analyses D’Onofrio et vésicules depuis les données versionnées. La partie astronomique recalcule la métrique certifiée `C-AST-01` depuis les sorties numériques de robustesse et distingue explicitement cette métrique du diagnostic `effect_to_ensemble_floor_ratio`.

Pour obtenir le rapport HTML autonome :

```bash
python scripts/demo_minimale_html.py --output demo_minimale_report.html
```

## 3. Vérifier l’intégrité et les verdicts

```bash
python verifier_dossier.py
python scripts/verifier_fins_de_ligne.py
python scripts/valider_registre_preuves.py
python scripts/valider_core_results.py
python scripts/controle_avant_push.py
```

## 4. Lire seulement le noyau

Commencer par `CORE_RESULTS.md`, puis `ETAT_DES_PREUVES.md`. Le premier contient 16 résultats à fort levier, volontairement mélangés entre succès, résultats négatifs, limites et résultats de modèle. Le second est le registre complet généré.

## 5. Comprendre ce qui manque encore

`ROADMAP.md` présente les quatre fronts actifs. Le fichier machine `plan_directeur/VERROUS_ACTIFS.json` est généré à partir des sorties d’autorité afin d’éviter qu’une roadmap narrative dérive du dépôt.

Le seuil §XIV se lit dans :

```text
plan_directeur/campagne_centrale_2026_08_11/resultats/SEUIL_XIV.json
```

## 6. Notebooks courts

- `notebooks/branche_matiere_26Al.ipynb` : inventaire radiogénique dérivé des événements datés.
- `notebooks/branche_systeme_solaire_interventions.ipynb` : séparation interventions / écarts numériques de `C-AST-01`.
- `notebooks/branche_vivant_histoire.ipynb` : réexécution du benchmark D’Onofrio.

Ces notebooks sont des portes d’entrée. Les artefacts JSON/CSV et scripts de campagne restent les autorités.
