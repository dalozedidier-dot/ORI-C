# Provenance et conventions physiques

## Forçage orbital

Les séries d'entrée sont les fichiers `earth.csv.gz` de `couche_astronomique/resultats/real_science_max`. Le témoin contient les huit planètes de Mercure à Neptune et les interventions Jupiter/Saturne déjà calculées.

## Référence indépendante

`02_branche_systeme_solaire/couche_memoire_historique/data/raw/INSOLN.LA2004.BTL.ASC` fournit, à pas de 1 kyr, l'excentricité, l'obliquité et la longitude du périhélie depuis l'équinoxe mobile de la solution La2004.

## Spin

La constante de précession actuelle `α0 = 54,93 arcsec/an` est la valeur utilisée dans la littérature de dynamique du spin terrestre (Levrard & Laskar 2003 ; Néron de Surgy & Laskar 1997). Pour l'ablation lunaire, le calcul emploie `α = 20 arcsec/an`, valeur solaire seule d'ordre actuel indiquée notamment par Saillenfest, Laskar & Boué (2019).

L'équation vectorielle intégrée est la forme séculaire du problème de Colombo : la vitesse de précession est proportionnelle à `α cos(epsilon) / (1-e²)^(3/2)` autour de la normale orbitale instantanée.

## Interprétation

Le contraste `54,93 → 20 arcsec/an` est une **ablation du couple lunaire effectif**, pas une suppression N-corps d'une particule Lune résolue. Il isole le rôle du couple lunaire sur la dynamique du spin en maintenant exactement le même forçage orbital planétaire.

Références :

- Laskar, J., Joutel, F. & Robutel, P. (1993), *Stabilization of the Earth's obliquity by the Moon*, Nature 361, 615-617.
- Néron de Surgy, O. & Laskar, J. (1997), *On the long term evolution of the spin of the Earth*, A&A 318, 975-989.
- Levrard, B. & Laskar, J. (2003), *Climate friction and the Earth's obliquity*, Geophysical Journal International 154, 970-990.
- Lissauer, J. J., Barnes, J. W. & Chambers, J. E. (2012), *Obliquity variations of a moonless Earth*, Icarus 217, 77-87.
- Saillenfest, M., Laskar, J. & Boué, G. (2019), *Secular spin-axis dynamics of exoplanets*, A&A 623, A4.
