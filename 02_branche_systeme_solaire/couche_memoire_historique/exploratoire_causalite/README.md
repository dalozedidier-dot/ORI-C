# Causalité exploratoire paléoclimatique

Cette couche ajoute deux instruments **exploratoires** sans rouvrir le verdict négatif de M2 :

- `run_ccm.py` : cross-mapping convergent minimal et reproductible sur les séries déjà versionnées ;
- `run_pcmci_plus.py` : adaptateur PCMCI+ via Tigramite, dépendance isolée du socle.

LR04 est orbitally tuned. Aucun résultat de cette couche ne constitue donc une validation indépendante d'un mécanisme orbital-climatique.

## Reproductibilité de CCM

Le générateur fixe explicitement la graine, mais CCM repose sur un classement de voisins dans un espace reconstruit. Des distances quasi ex aequo peuvent changer d'ordre entre bibliothèques numériques compatibles et déplacer les moyennes de `rho` d'environ `1e-4` sans changer le diagnostic. Le vérificateur des formalismes conserve `1e-10` pour toutes les autres sorties et applique **uniquement à `CCM_RESULTAT.json`** une tolérance locale `rel=5e-3`, `abs=2e-4`.

Cette tolérance est un contrôle de reproductibilité numérique de l'estimateur exploratoire. Elle ne transforme pas CCM en preuve confirmatoire et ne modifie pas le verdict négatif de M2.
