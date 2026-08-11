# Calibrage structurel de l'architecture matérielle ORI-C

## Portée

Le graphe canonique v0.9.3 est gelé. Aucun nœud ni aucune hyperarête n'est modifié par cette campagne. Le calibrage sépare la documentation, la fonction structurelle et les dimensions encore non mesurées.

Les coefficients documentaires sont des conventions explicites utilisées pour les tests de sensibilité. Les relations dont le plancher documentaire atteint 0,65 sont conservées dans tous les tirages. Seules les six relations moins documentées sont activées ou retirées. Ces coefficients ne représentent pas une probabilité de vérité et ne démontrent pas une causalité empirique.

## Résultat principal

Les **53 hyperarêtes** ont été évaluées. **40** produisent une perte mesurable lors d'une ablation dans la projection ou la fermeture stricte. **6** ont un plancher documentaire inférieur à 0,65.

Le stress paramétrique identifie **31 nœuds dans le noyau stable**, **15 nœuds sensibles**, **0 nœuds fragiles** et **7 nœuds déjà bloqués par le verrou canonique**. Cette classification décrit la dépendance au codage documentaire actuel, pas la fréquence naturelle des phénomènes.

## Tri des relations

- `P1_ablation_structurelle` : 35 hyperarêtes
- `P1_cycle_verrou` : 4 hyperarêtes
- `P1_documentation_effet_aval` : 1 hyperarêtes
- `P2_cycle_entretien` : 10 hyperarêtes
- `P3_redondante` : 3 hyperarêtes

Le cycle des interfaces `N029-N030-N053-N054` reste une priorité propre. Il n'est pas absorbé dans un score unique, car son problème est d'abord une dépendance collective et une direction causale à documenter.

## Sensibilité aux seuils documentaires

| Profil | Arêtes | Projection | Fermeture stricte |
|---|---:|---:|---:|
| complet | 53 | 53 | 46 |
| permissif | 52 | 51 | 46 |
| equilibre | 47 | 44 | 31 |
| conservateur | 36 | 5 | 5 |
| tres_strict | 5 | 2 | 2 |

La diminution du nombre de nœuds avec le seuil ne signifie pas que les processus retirés sont faux. Elle montre quelles portions de l'architecture dépendent actuellement de relations moins fortement documentées selon la convention choisie.

## Dépendance aux sources

- `S15` (revue_reference) : perte de projection 52, perte stricte 45.
- `S16` (revue) : perte de projection 49, perte stricte 42.
- `S17` (revue) : perte de projection 47, perte stricte 40.
- `S04` (mission_source) : perte de projection 42, perte stricte 36.
- `S01` (revue) : perte de projection 21, perte stricte 30.

## Test de transfert externe

Le schéma a été appliqué à deux trajectoires stellaires indépendantes documentées par MESA. Le benchmark contient **2 trajectoires**, **12 transitions** et atteint **14 nœuds sur 14** en fermeture stricte.

Ce test montre que le format de relation, le contrôle des seuils et la fermeture stricte se transfèrent à une autre architecture historique. Il ne valide pas une loi universelle de transformation et ne prouve pas que le calibrage documentaire ORI-C est optimal.

## Ce que le calibrage permet maintenant

1. Séparer les relations structurellement critiques des relations seulement faiblement documentées.
2. Repérer les sources dont dépend une grande partie de l'architecture.
3. Identifier un noyau stable et des zones sensibles sous variations explicites de seuils.
4. Conserver comme non mesurées la nécessité empirique, la suffisance, la temporalité quantitative, la réversibilité physique et l'effet d'une intervention directe.

## Limite décisive

Le calibrage affine le tri. Il ne remplace ni une expérience, ni une ablation naturelle, ni une prédiction hors échantillon. Une relation peut être structurellement indispensable dans le graphe et rester causalement insuffisamment démontrée dans la nature.
