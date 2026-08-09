# Échelle de preuve E0–E6

Cette échelle complète les verdicts `supports`, `does_not_support` et
`undetermined`. Elle décrit la force du dispositif ayant produit le verdict ;
elle ne transforme jamais un succès technique en soutien scientifique.

| Niveau | Exigence minimale |
|---|---|
| E0 | reproductibilité informatique de l'artefact |
| E1 | association empirique sur données réelles |
| E2 | l'histoire prédit au-delà de l'état présent et d'un témoin de complexité égale |
| E3 | états présents comparables, histoires différentes, futurs différents |
| E4 | intervention ou ablation causale de la trace ou du mécanisme |
| E5 | réplication indépendante sur un autre jeu, laboratoire ou publication |
| E6 | réplication du même noyau opérationnel dans plusieurs classes de systèmes |

## Pare-feu de montée de niveau

Un résultat ne monte que s'il survit aux contrôles applicables, dans cet ordre :

A. état seul ;
B. histoire permutée ;
C. variables confondantes ;
D. paramètres alternatifs préenregistrés ;
E. autre période ou population ;
F. autre dataset indépendant ;
G. autre laboratoire ou publication ;
H. intervention ou ablation.

Un contrôle absent est indiqué `non_testable`; il n'est jamais supposé réussi.
E5 exige une réplication indépendante réelle. E6 exige plusieurs classes de
systèmes avec le même critère opérationnel, pas une analogie verbale.

## Position actuelle des résultats certifiés

- D'Onofrio `C-ANT-01` : E2 ;
- vésicules `C-VES-02` : E2 ;
- vésicules `C-VES-03` : E4 dans ce protocole, sans réplication indépendante ;
- astronomie `C-AST-01` : E4 **dans le modèle physique réduit** ;
- matière `C-MAT-MEM-05` : verdict `does_not_support`, niveau non attribué comme
  résultat positif.

Ces niveaux sont des plafonds documentaires courants. Ils devront être
recalculés si une source, un contrôle ou un verdict change.
