# État des tests

**Fichier généré par `etat_des_tests.py`. Ne pas modifier à la main.**

Ce fichier est l'unique compteur courant. Des instantanés historiques
conservent leurs anciens nombres pour la traçabilité, mais ils ne font
pas autorité.

Dernière exécution : 2026-08-04

Environnement : Python 3.13.5, numpy 2.3.5, scipy 1.17.0, numba 0.65.1, pandas 2.2.3

Les compteurs dépendent de l'environnement. Un écart entre ce fichier et une exécution locale n'est pas nécessairement un fichier périmé : comparez d'abord les versions ci-dessus.

## Suites exécutables

| Suite | Réussis | Échecs | Ignorés | Xfail attendus |
|---|---:|---:|---:|---:|
| Socle, `00_socle/tests` | 153 | 0 | 1 | 1 |
| Couche mémoire historique | 32 | 0 | 0 | 0 |
| Campagne maximale, trois branches | 21 | 0 | 0 | 0 |
| Priorités v0.9.3 | 11 | 0 | 0 | 0 |
| Couche astronomique | 10 | 0 | 2 | 0 |

Le `xfail` attendu du socle concerne deux relations dont la référence est encore trop générique pour être datée : `TR-021 → TR-028` et `TR-024 → TR-023`. Il passera au vert dès qu'une source datable leur sera attachée. Il ne compte pas comme un échec réel.

## Analyse exhaustive du test interventionnel

Rapport archivé, **lu sans réexécution**. Le relevé d'état ne réécrit aucun résultat : la régénération appartient à la construction du dossier, avec `--rejouer-analyse`.

**11 sections réussies sur 11.**

## Portabilité de la couche mémoire

**Choix arrêté : reproductibilité numérique tolérée.** Les comparaisons au modèle de référence exigent un écart sous `1e-11` au lieu d'une égalité binaire.

Le noyau compilé exécute la même suite d'opérations flottantes que le modèle de référence, et l'écart est exactement nul sur l'environnement de livraison. Cette égalité n'est pas portable : numpy, scipy et numba peuvent réordonner ou vectoriser les opérations d'une version à l'autre, ce qui déplace le dernier bit. Des exécutions sur d'autres versions ont produit des écarts de 10⁻¹⁴ à 10⁻¹⁸.

La reproductibilité binaire exigerait aussi de figer le système, BLAS, LAPACK et les options de compilation. Le verrou Python exact ne suffit pas à garantir cette identité. La tolérance retenue reste très inférieure aux échelles numériques pertinentes pour les résultats rapportés : elle absorbe les écarts d'arrondi entre environnements et détecte les divergences dépassant le seuil fixé. Le test `test_la_tolerance_detecte_une_divergence_algorithmique` en donne la preuve automatisée.

## Reproduire

```bash
python etat_des_tests.py
```

Le mode `--verifier` échoue si le fichier ne correspond plus aux exécutions réelles ; il convient à un contrôle avant livraison.
