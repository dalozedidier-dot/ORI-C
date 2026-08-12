# VES-PACC-INT-01 — Pacc causal prospectif sur vésicules

Statut : **design prêt à être complété et préenregistré, non exécuté**.

Objectif : produire le premier test vésiculaire qui puisse instancier strictement
`PACC-INT-CHALLENGE-V1` dans un système empirique réel. Les 11 760 couples
parent-descendant déjà analysés servent uniquement à la calibration et à la
conception. Ils ne peuvent pas être requalifiés a posteriori comme test
prospectif de la condition 9 du §XIV.

## Patron expérimental obligatoire

Trois bras appariés sont requis : contrôle, `do(m)` ciblé et sham. L'état présent
non ciblé `X`, les contraintes futures `Theta` et l'architecture expérimentale
restent appariés. `m` doit être une trace matérielle mesurée, distincte de `X`,
et l'intervention doit viser `m` sans modifier volontairement les autres
variables.

Le candidat déjà visible dans le cas historique est la composition parentale
mesurée avant transfert. Ce candidat n'est **pas encore** un opérateur causal :
la manipulation physique ou quasi-physique qui permettrait `do(m)` doit être
spécifiée, testée techniquement et gelée avant l'ouverture d'un nouveau jeu de
données.

## Défis, réponse et accessibilité

Le jeu de défis futurs, les dimensions de réponse `R`, les seuils de matérialité,
les poids et les fenêtres de lecture sont déclarés avant acquisition ou avant
ouverture d'une tranche tenue à l'écart. `P_acc` est ensuite calculé par
`PACC-INT-CHALLENGE-V1`, avec bootstrap des unités indépendantes.

Une mesure empirique causalement qualifiée peut fermer localement la partie
vivant de la condition 9 même si `Delta P_acc` est nul ou négatif. Le soutien à
`INV-A` exige en plus que la règle d'effet non nul préenregistrée soit satisfaite.
Un résultat nul ou de signe opposé reste publié comme non-soutien.

## Porte avant préenregistrement

Le protocole ne doit pas être soumis comme protocole final tant que les champs
suivants ne sont pas remplis : opérateur et niveaux de `m`, défis `Theta`,
dimensions `R`, seuils de matérialité, tolérances d'appariement, définition et
nombre d'unités indépendantes, SESOI, puissance et règle finale de décision.

Le fichier machine compagnon est
`PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json`.
