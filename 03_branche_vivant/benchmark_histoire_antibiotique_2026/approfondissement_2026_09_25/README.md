# Robustesse du signal d'ascendance D'Onofrio

Analyse exploratoire du 25 septembre 2026 sur les données réelles déjà versionnées. Aucun crédit §XIV, aucune modification du résultat canonique ni des prédictions gelées.

Le témoin utilise l'antibiotique et l'environnement sous lequel le clone a évolué. Le modèle enrichi ajoute son ascendance. Cette comparaison ne constitue pas un contrôle de l'état physiologique et génétique complet. La définition des colonnes provient de [Dryad](https://datadryad.org/dataset/doi%3A10.5061/dryad.1zcrjdg68). Les 288 mesures correspondent à 24 clones, quatre antibiotiques et trois répétitions par couple clone-antibiotique.

| Analyse | Résultat | Limite |
|---|---|---|
| Cinq partitions groupées canoniques | Gain RMSE de 28,89 % | Ascendances déjà observées |
| 9 999 permutations par clone, au sein de l'environnement | p corrigé de 0,0001, aucun témoin aussi favorable | Échangeabilité supposée des clones, parenté à considérer |
| 500 partitions groupées aléatoires | 500 gains positifs, de 20,14 % à 33,15 % | Distribution de sensibilité, pas un intervalle de confiance |
| Transfert carbone vers azote | Gain de 19,42 %, p exact de 0,00694 | Mêmes ascendances dans les deux environnements |
| Transfert azote vers carbone | Gain de 28,01 %, p exact de 0,00694 | Mêmes ascendances dans les deux environnements |
| Retrait d'A-2 avec évaluation par clone laissé de côté | Gain de 9,57 %, contre 28,21 % sur l'ensemble | Effet hétérogène selon l'ascendance |

Chaque test de transfert énumère les 720 permutations des six étiquettes d'ascendance. La correction de Bonferroni limitée aux deux directions donne p = 0,01389. Aucun résultat ne démontre une causalité de la mémoire, une prédiction sur une nouvelle ascendance ou une réplication indépendante.

Les permutations conservent ensemble les douze mesures d'un clone et les effectifs d'ascendance par environnement. Ce contrôle complète le mélange ligne par ligne du résultat historique, qui reste conservé.

Après retrait d'une ascendance, les cinq partitions déterminées par l'ordre des identifiants isolent ici des ascendances entières. Cette procédure changerait la question en imposant la prédiction de catégories inconnues. Le script conserve ce diagnostic et utilise une évaluation laissant chaque clone successivement de côté pour mesurer la sensibilité au retrait d'une ascendance.

## Reproduction

Depuis la racine du dépôt, avec les dépendances prévues par ORI-C :

```bash
python 03_branche_vivant/benchmark_histoire_antibiotique_2026/approfondissement_2026_09_25/approfondissement_donofrio.py --repo . --output /tmp/donofrio-audit --verify-sklearn
python 03_branche_vivant/benchmark_histoire_antibiotique_2026/approfondissement_2026_09_25/verifier_approfondissement.py . /tmp/donofrio-audit
```

Sous Windows, remplacer `/tmp/donofrio-audit` par un dossier de résultats extérieur au dépôt. Le script principal fonctionne aussi avec NumPy et pandas seuls si l'option de vérification scikit-learn est omise.

Les sorties de référence figurent dans `resultats/`. La graine des permutations vaut 20260925, celle des partitions 20260926. Le script vérifie l'accord de l'erreur globale avec le résultat canonique à 0,000002 près. La résolution directe diffère de son solveur itératif d'environ 0,00000113 en RMSE. Une résolution augmentée par moindres carrés et la résolution directe de scikit-learn concordent avec le calcul à environ 10⁻¹⁴ sur les prédictions.

La prochaine étape utile consiste à mesurer un état actuel enrichi avant un test distinct sur données nouvelles. Ces analyses rétrospectives peuvent guider ce protocole, sans devenir son échantillon de confirmation.
