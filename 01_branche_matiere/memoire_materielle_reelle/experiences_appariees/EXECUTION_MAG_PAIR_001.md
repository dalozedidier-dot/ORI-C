# MAG-PAIR-001 — paquet d’exécution

`MAG-PAIR-001` est le front matière prioritaire pour `PRED-MATIERE-ABLATION-001`. Le présent paquet ne crée aucune mesure et ne modifie pas la prédiction gelée du 11 août.

## Ce qui est déjà fixé

Le protocole canonique impose au moins 48 unités indépendantes, deux histoires IRM opposées, une trace vectorielle mesurée avant le stimulus final, une persistance à 7 jours avec 10 lectures non destructives, une démagnétisation AF réelle, un sham AF nul, un champ test identique, un aveugle opérateur/analyste et la règle `A >= 0,50` avec interaction bilatérale `p <= 0,05`.

Le script `preparer_mag_pair_001.py` transforme les deux tables brutes gelées par `SCHEMA_ENTREE_MAG_PAIR_001.json` en une table par unité. Il vérifie notamment la complétude des étapes, les 10 lectures de persistance, les champs AF/test et les tolérances de température fixées dans la fiche d’exécution.

`analyser_mag_pair_001.py` applique ensuite la définition gelée de `A` et un test de permutation bloqué de l’interaction `histoire × ablation` sur le changement pré→post. Le sham entre dans ce contraste et est publié séparément. Le script refuse d’inventer un seuil supplémentaire pour le sham.

## Ce qui manque encore et ne peut pas être inventé dans le dépôt

La fiche `MAG-PAIR-001.execution.json` laisse volontairement `null` le laboratoire, le palier AF exact, le champ test, la température et sa tolérance, les graines de randomisation/permutation, la clé d’aveugle et la règle d’exclusion opérationnelle. Ces valeurs doivent être fixées avec le laboratoire **avant la première mesure confirmatoire**.

Tant que ces champs ne sont pas gelés et que l’enregistrement public préalable n’est pas attesté, `valider_gate_mag_pair_001.py` exige l’absence des fichiers de mesures et l’analyse reste fermée.
