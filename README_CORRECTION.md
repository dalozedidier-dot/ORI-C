# Correction de l'intégration du tri 366/317

Ce paquet **n'est pas destiné à être copié tel quel dans le dépôt**. Le script `CORRIGER_DEPOT.py` est un outil de livraison externe.

Il corrige quatre fautes d'intégration constatées dans les logs CI :

1. retrait de `APPLIQUER.md` et des deux copies racine `TRI_COMPLET_683_ORIC.*`, qui sont des artefacts de livraison/redondance et non des documents canoniques du repo ;
2. restauration du test CI `Tester la couche de certification fail-closed`, supprimé par erreur lors de l'intégration du tri ;
3. remplacement de la colonne ambiguë `priorite` par `rang_action` et de raisons libres par des `motif_code` contrôlés ;
4. reconstruction de `MANIFEST.sha256` et `MANIFEST.sha256.json` **après toutes les modifications**, via `python build_manifest.py build`.

Le script ajoute aussi un test fail-closed dédié au tri et enregistre la politique dans `AUTORITE_DES_DOCUMENTS.md` comme document d'organisation qui ne fixe aucun verdict scientifique.

Exécution depuis n'importe où :

```bash
python CORRIGER_DEPOT.py /chemin/vers/ORI-C
```

Le script s'arrête au premier échec et lance les contrôles officiels du dépôt, y compris `controle_avant_push.py` et `valider_tout.py --strict-lfs`.
