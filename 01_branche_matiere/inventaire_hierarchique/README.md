# Inventaire hiérarchique de la matière connue

Registre de ce qui existe, classé par niveau d'organisation, du constituant
fondamental au réservoir astronomique. Il répond à une question distincte de
celle de la généalogie : celle-ci demande *d'où vient* une architecture,
celui-ci demande *ce qui est disponible* à un niveau donné.

## Contenu

| Niveau | Entrées | Couverture |
|---|---:|---|
| Constituants fondamentaux | 18 | exhaustif, Modèle standard confirmé |
| Particules composites | 56 | sélection structurante, registre détaillé externe |
| Nuclides et états nucléaires | 5 843 | **import complet d'une évaluation fermée** |
| Éléments chimiques | 118 | exhaustif |
| Molécules et macromolécules | 70 | sélection structurante, catalogue dynamique externe |
| États et phases | 53 | familles principales, ouvert |
| Matériaux et minéraux | 77 | structurant, registre minéralogique externe |
| Réservoirs astronomiques | 46 | grands réservoirs |
| Matière biologique | 43 | hiérarchique, les espèces ne sont pas énumérées |
| Inconnus et hypothèses | 16 | **séparés des entités confirmées** |
| Transformations | 52 | processus structurants |
| **Total détaillé** | **6 392** | hors index maître et hiérarchie |

L'index maître donne 550 entrées filtrables pointant vers les feuilles
détaillées. Dix sources institutionnelles sont enregistrées avec URL et date de
consultation.

## Ce qui est exhaustif et ce qui ne l'est pas

La distinction est portée par le fichier lui-même et ne doit pas être effacée.
L'inventaire est **exhaustif là où un registre fermé ou évalué existe** —
constituants fondamentaux, nuclides, éléments chimiques. Il est **hiérarchique
et ouvert** partout ailleurs : molécules, matériaux, organismes, architectures.
Aucun de ces derniers ensembles n'est fini, et le fichier ne prétend pas les
clore.

Aucune hypothèse n'est présentée comme une découverte. La feuille des inconnus
ne porte aucun statut « confirmé » : ses entrées sont non détectées,
hypothétiques ou inférées, et le disent.

## Rapport avec l'inventaire accessible

Le fichier introduit une chaîne à quatre degrés qui raffine la notion employée
dans `../hypergraphe_transformations/inventaire_accessible.csv` :

| Degré | Définition |
|---|---|
| **Présence** | la matière existe dans le système ou le réservoir considéré |
| **Accessibilité** | une interaction, un flux ou une interface peut l'atteindre |
| **Mobilisabilité** | elle peut être déplacée, dissoute, transportée ou transformée dans les conditions du milieu |
| **Opérativité** | elle est incorporée dans une architecture et contribue à sa persistance ou à sa transformation |

Cette chaîne éclaire pourquoi vingt-huit des trente et un enregistrements de
l'inventaire accessible n'ont pas de valeur chiffrée. Ils mesurent une
**présence** par réservoir. Le passage à la mobilisabilité exige des flux et des
horizons, que les coefficients de partage à l'équilibre ne fournissent pas.

## Vérification

`tables/` contient l'export CSV de chaque feuille, pour que le contenu soit
diffable et vérifiable au manifeste sans ouvrir un binaire. Le classeur reste la
source. Les tests de `tests/` verrouillent les effectifs annoncés, la clôture de
la hiérarchie, le sourçage et la séparation entre confirmé et hypothétique.
