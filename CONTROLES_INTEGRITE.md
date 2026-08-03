# Contrôles d’intégrité et de reproductibilité

Date : 2026-08-01

## Contrôles rejoués depuis une extraction isolée

- manifeste initial : valide ;
- socle : 121 tests réussis, 1 xfail documenté ;
- mémoire historique : 32 tests réussis ;
- astronomie : 11 tests collectés, 10 réussis et 1 ignoré ;
- plateforme : 13 tests réussis ;
- généalogie annotée : 8 tests réussis ;
- hypergraphe : 13 tests réussis, 1 xfail déclaré ;
- **total rejoué : 196 collectés, 192 réussis, 2 xfail, 2 ignorés, aucun échec**.

Deux causes de plateforme faisaient paraître cassées les suites de la plateforme
et de la couche astronomique. Elles ne l'étaient pas. `scikit-learn` et
`statsmodels` manquaient, et le chemin de base du répertoire temporaire de
`pytest` dépassait la limite Windows de 260 caractères, ce qui produisait des
`PermissionError` puis des `FileNotFoundError` trompeuses. Un chemin court
suffit :

```bash
PYTHONPATH=src python -m pytest tests -q --basetemp=C:/oric_tmp/pf
```

Le second xfail est une réfutation, pas une lacune : la monotonie de l'échelle
des dix capacités a échoué sur son critère préenregistré et n'est pas
rétablissable par réétiquetage. Le test est conservé en échec déclaré pour
énoncer ce qui a été réfuté au lieu de le faire disparaître.

Le xfail concerne deux relations dont la référence reste générique et non datable. Il ne doit pas être présenté comme une validation. Le test astronomique ignoré reste explicitement signalé.

## Nettoyage appliqué

- retrait des anciens bancs et schémas synthétiques livrés comme données ;
- retrait des miroirs et constructions `build`, `dist`, `pkg` et `egg-info` ;
- retrait des caches pytest, `__pycache__` et fichiers `.pyc` ;
- conservation du code synthétique uniquement comme utilitaire interne permettant de tester que le mode `real-data-only` bloque bien les générateurs ;
- correction du verrou vers `numpy==2.3.5`, `pandas==2.3.3` et `pytest==8.4.2`, compatibles avec les contraintes des sous-projets ;
- reconstruction des manifestes après nettoyage.

## Couche hypergraphe de la branche 1, ajout du 2026-08-02

- hypergraphe : 53 nœuds, 53 hyperarêtes, clôture généalogique vérifiée,
  racine unique `N036`, 53/53 nœuds joignables ;
- inventaire accessible : 31 enregistrements sourcés, 4 éléments, 2 corps,
  bouclage des budgets publiés à 2,88 % au pire ;
- suite hypergraphe : 13 tests réussis, 1 xfail déclaré ;
- socle : 121 tests réussis, 1 xfail ;
- mémoire historique : 32 tests réussis ;
- couche astronomique : 10 réussis, 2 ignorés ;
- plateforme : 13 tests réussis ;
- **total rejoué : 193 collectés, 189 réussis, 2 xfail, 2 ignorés, 0 échec** ;
- manifestes reconstruits : 0 modifié, 0 absent, 0 non listé.

Les suites de la plateforme et de la couche astronomique étaient apparemment
cassées. Elles ne l'étaient pas. Deux causes distinctes, toutes deux de
plateforme : `scikit-learn` et `statsmodels` manquaient, et le chemin de base
du répertoire temporaire de `pytest` dépassait la limite Windows de 260
caractères, ce qui produisait des `PermissionError` puis des
`FileNotFoundError` trompeuses. Les deux conditions sont maintenant écrites
dans `ENVIRONNEMENT.md` avec la commande exacte.

Trois défauts d'intégration ont été corrigés à cette occasion. Les exclusions
de `build_manifest.py`, `construire_dossier.py` et `verifier_dossier.py`
divergeaient : le cache `.mplconfig` était inscrit au manifeste sans être
balayé par le vérificateur, et `MANIFEST.sha256.json` était empreinté puis
réécrit à chaque régénération, donc perpétuellement obsolète. Les trois listes
sont alignées.

Le second xfail est une réfutation, pas une lacune : la monotonie de l'échelle
des dix capacités a échoué sur son critère préenregistré et n'est pas
rétablissable par réétiquetage. Le test est conservé en échec déclaré pour
énoncer ce qui a été réfuté au lieu de le faire disparaître.

La campagne consolidée reste scientifiquement prudente : une réussite technique n'est pas une validation d'une hypothèse ORI-C.
