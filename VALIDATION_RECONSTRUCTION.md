# Validation de la reconstruction

Contrôles exécutés le 3 août 2026 après le tri, les corrections de chemins, l’intégration de l’inventaire et la régénération du manifeste.

## Intégrité

- manifeste SHA-256 valide ;
- aucune entrée absente, modifiée ou non listée ;
- structure canonique complète ;
- archive ZIP testée sans erreur ;
- noms Unicode normalisés.

## Suites de tests

| Suite | Résultat |
|---|---:|
| Socle | 152 réussis, 1 ignoré, 1 échec attendu |
| Hypergraphe de la matière | 13 réussis, 1 échec attendu |
| Inventaire hiérarchique | 19 réussis |
| Mémoire historique | 32 réussis |
| Couche astronomique | 10 réussis, 2 ignorés faute de dépendances optionnelles |
| Plateforme | 13 réussis |
| **Total réussi** | **239 tests** |

## Écarts conservés volontairement

- l’analyse exhaustive du test interventionnel n’est pas relancée automatiquement ;
- deux relations de la carte conservent une référence générique non datable et restent marquées comme échec attendu ;
- les architectures et liens nouvellement repérés demeurent candidats jusqu’à validation des quatre axes de preuve.
