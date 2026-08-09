# Note de supersession du gel historique

`GEL_CAMPAGNE.json` conserve la valeur historique `paires_minimum: 6`. Elle
n'est plus une règle opératoire et ne doit pas être appliquée comme un seuil
universel.

Le filtre courant appliqué par `admettre_jeu.py` utilise une règle dépendant du
plan expérimental : nombre de paires pour un plan apparié, ou tailles des
groupes pour un plan à groupes indépendants, avec vérification de
l'atteignabilité de la p-value avant admission.

Le fichier gelé et les documents scellés ne sont pas modifiés silencieusement,
afin de préserver la trace historique. Cette note constitue la supersession
explicite du seul champ `paires_minimum`, sans resceller rétroactivement la
campagne.

La qualification IODP est également précisée hors du gel : le jeu démontre
fortement `dose d'ablation → effacement de la trace`, mais ne réalise pas le
plan A/B complet exigé par C-MAT-MEM-03. Le résultat est une preuve forte
d'ablation physique ; C03 complet reste non testable avec ce jeu.
