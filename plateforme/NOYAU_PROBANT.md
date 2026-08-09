# Noyau probant actif

Le catalogue canonique conserve **683 tests** pour préserver l’historique, les identifiants et la traçabilité. Une politique séparée classe chaque entrée sans modifier ce registre :

- **366 GARDER** : cibles du noyau probant actif ;
- **317 VIRER** : sorties du noyau probant et conservées uniquement en QA/exploration si elles restent utiles ;
- **27/27 tests confirmatoires conservés**.

`VIRER` ne signifie pas supprimer le code. Les simulations, contrôles de reproductibilité, inventaires, balayages paramétriques et métriques secondaires peuvent rester indispensables à la qualité de la plateforme, mais ils ne sont plus traités comme des preuves scientifiques autonomes.

La politique est dans `POLITIQUE_NOYAU_PROBANT.csv`. `valider_noyau_probant.py` vérifie en mode fail-closed que les 683 IDs sont classés exactement une fois, que les compteurs restent 366/317 et qu’aucun test confirmatoire n’est exclu. Il peut matérialiser un catalogue dérivé de 366 lignes pour les campagnes de recherche sans altérer `catalogue_tests.csv`.

Ce tri est une décision d’organisation du programme de preuve. Il **ne constitue pas un verdict scientifique** et ne modifie pas les compteurs de l’audit empirique strict ni les certifications spécialisées.
