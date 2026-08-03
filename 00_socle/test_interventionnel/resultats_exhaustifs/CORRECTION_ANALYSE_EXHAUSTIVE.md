# Correction de l'analyse exhaustive

## Portée

Cette correction concerne uniquement le test interventionnel du socle ORI-C.
Elle ne modifie aucune branche, aucune carte relationnelle et aucun article.

## Défaut A01

La sortie publiée était antérieure au script présent dans le dossier. Après
régénération, le cas dégénéré `m = delta + l = 0` réussit le contrôle prévu :
`P` croît sans borne, sa pente tend vers `D S_in` et `S` tend vers zéro. Ce cas
reste exclu du domaine non dégénéré par la condition `m > 0`.

## Défaut E01

Le test du ralentissement critique incluait le point situé à un écart relatif
de `10^-1` du seuil dans un critère censé vérifier une loi asymptotique. Ce
point est encore hors du régime asymptotique et provoquait un faux échec.

Le verdict utilise désormais les quatre points les plus proches du seuil,
entre `10^-2` et `10^-5`, avec deux contrôles complémentaires :

- pente log-log de `tau` en fonction de l'écart proche de `-1`
- stabilité du produit `tau × écart`

Résultats :

- pente log-log : `-1,015951`
- rapport maximal/minimal de `tau × écart` : `1,126199`
- échange de stabilité : confirmé
- décroissance au seuil en `1/t` : confirmée

## Verdict

Les 11 sections sur 11 réussissent. Cette exhaustivité porte sur le système
d'équations défini et son domaine admissible. Elle ne constitue pas une preuve
sur toutes les structures mathématiques possibles ni une validation empirique
dans le vivant.
