# Rapport de validation de la plateforme ORI-C complète

Date : 1 août 2026

## Couverture

- 683 entrées de test
- 51 work packages
- 59 moteurs analytiques
- 33 schémas de données
- 51 protocoles de campagne
- 683 lignes dans la grille de critères préenregistrables

## Contrôles exécutés après fusion

- Compilation et import des modules : réussis
- Tests logiciels `pytest` : 13 réussis
- Construction de la roue Python : réussie
- Installation de la roue dans `pkg/` : réussie
- Concordance `src/`, `build/lib/` et `pkg/` : 42 fichiers communs identiques
- Validation des 11 jeux centraux de la campagne réelle : réussie
- Campagne réelle consolidée : 213 réussites techniques, 438 blocages explicites, 32 protocoles non exécutés, 0 échec et 0 erreur
- Verdict scientifique : 0 soutien, 0 réfutation, 651 indéterminés et 32 non applicables

## Interprétation

Ces contrôles valident le fonctionnement du logiciel, la cohérence des schémas et la portée prudente de la campagne réelle. Une réussite technique ne valide aucune hypothèse scientifique ORI-C. Les membres d’incertitude GISTEMP ne sont pas traités comme des modèles climatiques indépendants.

## Limites

Le code ne peut pas exécuter physiquement une culture bactérienne, une expérience prébiotique, une mesure isotopique, une expérience à haute pression ou une réplication externe. Pour ces cas, il prépare les protocoles et bloque l’interprétation lorsque les données nécessaires manquent.
