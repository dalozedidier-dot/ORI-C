# Carte relationnelle — analyse de graphe, WP-S3.12 à S3.19

**Statut : exploratoire.** Aucun critère n'avait été préenregistré pour ces
quantités. Les résultats ci-dessous sont des mesures, pas des verdicts.

```bash
cd 00_socle/carte_relationnelle
python analyse_graphe.py
```

Les 33 tests de `00_socle/tests/test_carte_relationnelle.py` couvrent déjà
l'intégrité, les cycles, la connexité et les niveaux de preuve. Ils ne
répondaient pas à la question du plan directeur : **la structure de la carte
porte-t-elle une information, ou reflète-t-elle le choix des nœuds et leur
ordre chronologique ?**

## A. Métriques

| Quantité | Valeur |
|---|---:|
| Nœuds | 40 |
| Liens | 47 |
| Densité | 0,030 |
| Modularité | 0,659 |
| Communautés | 5 |
| Plus long chemin | 24 |
| Degré entrant max | 4 |
| Degré sortant max | 4 |

Cinq nœuds les plus intermédiaires : `TR-020` (0,189), `TR-019` (0,184),
`TR-016`, `TR-022`, `TR-023` (0,162).

Seize points d'articulation sur quarante nœuds : la carte est **une chaîne
principale à embranchements courts**, pas un réseau dense. Retirer l'un de ces
seize nœuds la scinde.

## B. Graphes nuls — et un modèle nul défectueux

### Le premier nul ne convenait pas

Le rebranchement libre à degrés conservés (`directed_edge_swap`) **détruit
l'ordre chronologique**. Tous les tirages deviennent cycliques, la longueur du
plus long chemin y vaut zéro par convention, et la comparaison affichait
`p = 0,0005` — un résultat qui ne dit rien d'autre que « rebrancher au hasard
crée des cycles ».

Un second nul a donc été construit : double échange conservant les degrés
entrants et sortants **et** n'acceptant l'échange que si les deux arêtes
produites vont encore d'un rang inférieur vers un rang supérieur. Il préserve
l'acyclicité et l'ordre. C'est lui qui fait foi.

### Résultats contre le nul respectant l'ordre, 2000 tirages

| Quantité | Observé | Nulle | z | p |
|---|---:|---:|---:|---:|
| Modularité | 0,659 | 0,668 ± 0,021 | **−0,43** | 0,693 |
| Plus long chemin | 24 | 6,07 ± 9,95 | **+1,80** | 0,090 |
| Nombre de communautés | 5 | 5,81 ± 0,65 | **−1,26** | 0,382 |

**Aucune des trois quantités ne distingue la carte d'un graphe aléatoire de
mêmes degrés et de même ordre chronologique.**

La modularité de 0,659, qui semble élevée dans l'absolu, est **inférieure** à
la moyenne des graphes nuls. Elle vient de la séquence de degrés et de la
contrainte d'ordre, pas du codage des liens.

Le plus long chemin, à 24, est le seul à s'écarter — mais avec `p = 0,090` et
un nul d'écart-type 9,95, il ne franchit aucun seuil usuel.

## C. Prédiction de liens masqués — le test décisif

Huit liens masqués par tirage, 200 tirages, dix négatifs par positif. Aire sous
la courbe ROC, calculée par somme de rangs avec traitement des ex aequo.

| Prédicteur | AUC | IC 95 % |
|---|---:|---|
| Structurel (Adamic-Adar) | **0,491 ± 0,032** | [0,444 ; 0,542] |
| **Proximité chronologique** | **0,922 ± 0,038** | [0,836 ; 0,978] |
| Hasard | 0,510 ± 0,112 | [0,309 ; 0,721] |

Écart structurel moins proximité : **−0,430**, IC [−0,508 ; −0,323].
**0 tirage sur 200 favorable au prédicteur structurel.**

**Lecture.** Le prédicteur structurel est au niveau du hasard. Le témoin
chronologique — « une transition est liée à celles qui la suivent
immédiatement » — atteint 0,92.

Autrement dit : **connaître la structure de la carte n'aide pas à retrouver un
lien masqué ; connaître l'ordre des transitions suffit presque.** Les 47
relations sont, pour l'essentiel, la chronologie.

### Deux réserves qui limitent la portée de ce résultat

1. **Adamic-Adar mesure la fermeture triadique.** Sur 47 liens répartis sur 40
   nœuds en quasi-chaîne, les voisins communs sont rares par construction. Un
   prédicteur inadapté au type de graphe échouerait ici même sur une carte
   informative. Le résultat dit qu'*un prédicteur structurel standard ne trouve
   pas de signal exploitable*, pas que la carte n'en contient aucun.
2. **Le témoin chronologique est avantagé par la construction du problème.**
   Les candidats sont restreints aux paires orientées vers l'avant, et les
   liens réels sont majoritairement à courte portée. Une part de son AUC de
   0,92 vient de là.

Ces réserves n'annulent pas la convergence entre B et C : les deux analyses,
indépendantes, pointent dans la même direction.

## Ce que l'analyse établit

La valeur de la carte, en l'état, est **documentaire et non structurelle**.
Elle consigne 47 relations typées, sourcées et datées, chacune avec son niveau
de preuve — c'est son apport réel, et les 33 tests le vérifient. Mais sa
topologie n'ajoute rien de mesurable à l'ordre chronologique des transitions.

Cela ne réfute rien du cadre ORI-C. Cela dit où la carte n'est pas encore un
instrument : elle ne prédit pas, elle enregistre.

## Ce que cela implique pour le plan directeur

- **WP-S3.15 et S3.16** sont exécutés. Résultat négatif.
- **WP-S3.13** — « vérifier que les propriétés de graphe ne proviennent pas du
  choix manuel des nœuds » — est exécuté et la réponse est qu'elles en
  proviennent.
- **WP-S3.18**, proposer des relations nouvelles ensuite validées par la
  littérature, ne peut pas s'appuyer sur le prédicteur structurel testé ici.
- Le préalable reste **WP-S3.5 à S3.7** : faire coder les 47 relations par des
  experts indépendants et publier les désaccords. Aucune analyse de graphe ne
  remplace cette mesure.
