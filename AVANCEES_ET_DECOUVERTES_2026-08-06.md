# ORI-C, avancées et découvertes après la campagne maximale

Date : 6 août 2026

## Conclusion générale

La campagne maximale ne valide pas ORI-C comme théorie générale. Elle produit cependant une avancée conceptuelle et expérimentale nette : **l’architecture d’un système peut modifier causalement ses trajectoires futures, tandis qu’une simple dépendance au chemin ne suffit pas à établir une mémoire durable**.

Le résultat le plus solide se trouve dans la branche astronomique. Les branches matière, climat et vivant permettent surtout de localiser avec précision ce qui fonctionne, ce qui reste descriptif et ce qui échoue face à des témoins plus exigeants.

## 1. Une causalité architecturale solidement établie dans le modèle astronomique réduit

La couche astronomique réussit **13 critères préenregistrés sur 15**. L’intégration de référence couvre 20 millions d’années. À 1 million d’années, la corrélation de l’excentricité terrestre avec La2010a atteint **0,9973**. Le pic de la bande de 405 000 ans est retrouvé à **408 184 ans**, exactement comme dans la comparaison La2010a utilisée par le rapport.

Les interventions sur l’architecture de Jupiter et de Saturne produisent des effets au moins **4 964 fois plus grands** que les écarts numériques sélectionnés. Cela sépare clairement l’effet causal de l’intervention des erreurs liées au pas de temps, à l’intégrateur ou aux conditions initiales proches.

Les deux critères échoués restent localisés. Le diagnostic du moment angulaire exporte une grandeur newtonienne qui n’est pas l’invariant canonique relativiste complet. L’aller-retour à un pas de 0,01 an dépasse le seuil, alors que le pas de 0,005 an le respecte. Le modèle reste également beaucoup moins précis qu’une solution astronomique de référence à long horizon. Il valide donc un mécanisme causal dans un modèle réduit, pas une nouvelle éphéméride de référence.

## 2. Une distinction nouvelle entre histoire, relaxation et mémoire

Les trajectoires exoplanétaires présentent d’abord des différences liées à leur chemin. Lorsque le même forçage final est maintenu pendant 600 millions d’années, les écarts de température, de glace et de CO₂ deviennent nuls, et l’écart de productivité devient négligeable.

Le temps de décroissance caractéristique est proche de 7 millions d’années, soit l’échelle de temps du mécanisme de mémoire introduit dans le modèle. Le signal initial correspond donc à un **retard de relaxation**, pas à une inscription durable.

Cette distinction resserre fortement le cadre ORI-C :

> Une histoire différente ne constitue une mémoire persistante que si son effet survit à la relaxation sous un même forçage final.

Le modèle climatique réduit possède plusieurs attracteurs dans quatre régions testées, autour de 12° et e = 0,30, 23,5° et e = 0,18, 30° et e = 0,10, puis 40° et e = 0. Mais les deux trajectoires étudiées retombent dans le même bassin. La capacité de produire une dépendance durable existe dans le modèle, sans être démontrée pour les trajectoires testées.

## 3. La branche matière devient plus précise sur ses verrous

La fermeture hypergraphique stricte atteint **46 nœuds sur 53**. Les sept nœuds inaccessibles sont liés à un noyau cyclique formé par `N029`, `N030`, `N053` et `N054`, avec trois nœuds supplémentaires bloqués en aval.

Déclarer disponible un seul des quatre nœuds du noyau suffit à restaurer 53 nœuds sur 53. Ce résultat diagnostique une dépendance circulaire dans l’encodage actuel. Il ne démontre pas l’existence d’un apport naturel extérieur.

Deux comptages auparavant présentés comme contradictoires décrivent en réalité deux tests différents :

- **34 hyperarêtes** sont critiques pour la fermeture stricte sous suppression unitaire ;
- **40 hyperarêtes** produisent une perte mesurable dans au moins une métrique de projection ou de fermeture stricte.

L’échelle des dix capacités porte une information propre, avec un gain net de **0,595 bit**, une permutation à **p = 0,00005** et une corrélation d’environ **0,74** avec la profondeur du graphe. Sa monotonie le long des transformations est toutefois réfutée. Elle classe utilement les architectures, mais ne représente pas une progression obligatoire des processus.

Le benchmark hors nœud donne une autre limite importante. La chronologie seule atteint une AUC de **0,9145**, tandis que chronologie plus régime ORI-C atteint **0,9099**. L’ajout du régime ne fournit donc aucun gain prédictif démontré dans ce test.

## 4. La mémoire paléoclimatique actuelle est testée et non soutenue

Le modèle M2 améliore la RMSE d’environ **3,6 %** face au modèle classique M1, sous le seuil préenregistré de 5 %. Face au témoin M1P de même complexité, il perd environ **31,6 %**, avec un intervalle de confiance de **−38,9 % à −25,1 %**.

Après retrait d’une symétrie exacte, M2 possède huit paramètres identifiables. Le couplage carbone dégrade la prédiction hors échantillon de **0,232**. Les paramètres de mémoire restent mal identifiés et la bande de 100 000 ans n’est pratiquement pas reproduite par le modèle calibré.

La famille de modèles peut produire cette bande dans certaines configurations. L’échec concerne donc la calibration et la formulation actuelle, pas une impossibilité mathématique générale.

## 5. Le vivant fournit un signal exploratoire, pas une confirmation robuste

Dans la validation croisée groupée sur l’amikacine, le modèle historique obtient une MAE de **0,6240**, contre **0,6335** pour le témoin de même complexité. L’écart reste faible et le test apparié donne **p = 0,2266**.

Le modèle sans pente historique fait légèrement mieux que le modèle historique complet, avec une MAE de **0,6221**. Sur la dernière transition, le modèle état seul obtient **0,7767**, contre **0,8687** pour le modèle historique. La permutation détruisant l’ordre temporel donne **p = 0,0649**.

La conclusion soutenue par les données est donc prudente : certains résumés du passé contiennent une information prédictive faible, mais l’avantage ne dépend pas clairement de l’ordre historique et ne résiste pas à tous les tests hors échantillon.

Les données ARN montrent une dynamique de composition sur huit cycles. Elles ne contiennent pas de filiation parent-descendant entre compartiments et ne testent donc pas encore une continuité héréditaire prébiotique.

## 6. Résultat strict des 683 entrées

Après correction du registre de portée et reconstruction reproductible des 41 expériences de partage :

| Statut | Nombre |
|---|---:|
| Réussites techniques | **298** |
| Blocages | **337** |
| Protocoles non exécutables informatiquement | **48** |
| Échecs | **0** |
| Erreurs | **0** |

Les verdicts scientifiques restent : 0 soutien confirmatoire, 0 rejet confirmatoire, 635 indéterminés et 48 non applicables. Une réussite technique signifie qu’un moteur a exécuté une analyse couverte par les données. Elle ne vaut pas automatiquement confirmation scientifique.

## Ce que le programme permet maintenant d’affirmer

> L’architecture matérielle d’un système peut modifier causalement son domaine de trajectoires, résultat solidement établi dans le modèle astronomique réduit. L’histoire améliore certaines descriptions ou prédictions exploratoires, mais son effet n’est ni automatique ni universel. Une mémoire durable exige une inscription qui persiste après relaxation sous un même forçage, ce qui suppose généralement plusieurs attracteurs accessibles ou des frontières de bassin effectivement franchies.

Cette formulation est plus étroite que l’ambition initiale, mais elle est aussi beaucoup plus solide. La campagne a séparé un résultat causal robuste, des signaux exploratoires, des représentations encore descriptives et deux résultats négatifs localisés qui orientent directement les prochains protocoles.
