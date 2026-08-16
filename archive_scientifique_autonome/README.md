# ORI-C - Correctif de livraison, exploitation des données existantes, 7 axes

Date : 16 août 2026

## Ce paquet est quoi

Ce ZIP corrige la livraison de 39 Ko produite à la fin de la conversation précédente. Il contient les données réellement récupérables de cette session, les entrées externes utilisées, les scripts à chemins relatifs, les résultats recalculés, les résultats historiques qui ne peuvent pas être honnêtement déclarés comme rerun, ainsi qu'un arbre d'intégration ORI-C.

## Ce paquet n'est pas quoi

Ce paquet n'est pas présenté comme le dépôt ORI-C complet. La base complète exacte utilisée dans la conversation précédente était `ORI-C-main-20260815T193827Z-1-001.zip`. Son nom et son rôle sont retrouvés dans l'historique, mais ses octets ne sont plus accessibles dans la bibliothèque actuelle. Aucun autre dépôt n'a été substitué à sa place.

La règle retenue est volontairement stricte : une donnée dont le SHA-256 exact n'est plus récupérable reste déclarée manquante. Une ancienne version ressemblante n'est jamais injectée silencieusement.

## Ce qui est réellement récupéré

Le précédent audit décrivait 47 fichiers de données au premier niveau et 663 433 lignes CSV. Quarante-trois des 47 payloads ont été retrouvés avec leur SHA-256 exact. Les quatre payloads exacts absents sont listés dans `data/RECOVERY_STATUS.json` :

- `REAL_DATA_COVERAGE.json`
- `nucleosynthesis_isotope_yields.csv`
- `partition_experiments.csv`
- `prebiotic_timecourse_summary.csv`

Aucun de ces quatre fichiers n'est nécessaire aux cinq recalculs principaux exécutés ici.

## Reproductions réellement exécutées dans cette réparation

- AICC2023 : résultat reproduit exactement, y compris EDC, 5 806 points et sigma médian de 2,37 ka sur 600-850 ka.
- Endosymbiose : 85 génomes, 15 810 appels HMM, résultat reproduit exactement.
- Accrétion tardive : 122 159 mesures, audit multitraceur reproduit exactement.
- Gajrani Pacc : jour 12, delta = -0,0807291667 et IC95 [-0,1145833333 ; -0,0416666667], avec JSON strict utilisant `null` lorsque les contrôles n'existent pas.
- Gajrani H -> m -> R : analyseur d'origine rerun depuis les données brutes incluses.
- Vésicules : 59 328 mesures temporelles, analyse mécanistique reproduite. Les valeurs Pacc historiques -0,0375 et [-0,1458333333 ; 0,0625] sont conservées avec leur provenance, sans prétendre les recalculer depuis un résultat source devenu inaccessible.
- Watkins : 209 essais et reconstruction des étiquettes finales reproduits. La séparation brute est exactement retrouvée, max sans bascule 0,9986572266 et min avec bascule 48,7998962402.

## Ce qui reste historique, et pourquoi

`RESULTAT_WATKINS_WAVE_HISTORY.json` est conservé dans `results/historical/`. Les métriques 26,79 % -> 30,62 %, gain +3,83 points, bootstrap et permutation ne sont pas déclarées comme fraîchement rerun, car le script exact d'extraction des 11 variables H et du classifieur utilisé dans la conversation précédente n'est plus récupérable. Les remplacer par un classifieur reconstruit après coup pour retrouver les mêmes chiffres serait méthodologiquement incorrect.

Yen-Papin est livré avec les données, l'analyseur et le résultat historique. L'analyseur complet dépasse la limite d'exécution de l'environnement actuel. Le résultat historique reste donc identifié comme tel, au lieu d'être rebaptisé « reproduit » sans exécution complète.

`VALIDATION_CIBLEE.json`, avec 51 passés, 0 échec et 1 xfail, reste également dans `results/historical/`. Il décrit la campagne de la conversation précédente. Il n'est pas transformé en nouvelle validation du paquet.

## Windels

Le protocole proposé `PRED-VIVANT-WINDELS-TRAJECTORY-001.proposed.json` est conservé. Les valeurs MIC restent fermées. La tentative de gel public avait échoué avec un 403 avant ouverture. Ce paquet ne détruit pas cet aveugle.

## Exécution

Depuis la racine du paquet :

```bash
python scripts/verify_inputs.py
python scripts/run_all.py
```

`run_all.py` exécute uniquement ce qui peut être reproduit honnêtement avec les entrées présentes. Il ne simule ni le classifieur Watkins manquant ni un rerun Yen-Papin interrompu.

Dépendances Python : `numpy`, `pandas`, `scipy`, `scikit-learn`, `openpyxl`.

## Intégration dans ORI-C

Le dossier `integration_patch/` conserve l'arborescence ORI-C pour les ajouts scientifiques disponibles. Il ne contient volontairement aucun `MANIFEST.sha256` racine prétendant représenter le dépôt complet. Les manifestes racine doivent être reconstruits uniquement après application sur la base complète exacte.

Le paquet peut donc servir immédiatement d'archive scientifique reproductible et de correctif d'intégration. Il ne doit pas être rebaptisé archive canonique complète tant que `ORI-C-main-20260815T193827Z-1-001.zip` n'a pas été réintroduit comme base exacte.
