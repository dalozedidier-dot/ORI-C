# Régénération requise

Les figures de `resultats/` ont été produites à partir de l'état antérieur des
données. Elles restent **exactes pour ce qu'elles montrent** : ni la topologie
du graphe, ni les codes portés par les arêtes n'ont été modifiés depuis. Deux
enrichissements sont en revanche en attente d'être rendus visibles.

## 1. Recodage en attente

| Relation | Code affiché | Code cible | Raison |
|---|---|---|---|
| `TR-037 → TR-039` | `DESC` | `INTG` | l'endosymbiose est une intégration de deux lignées, non une simple ascendance |

## 2. Attribut de fermeture

La colonne `domaine_ferme` de `data/noeuds_poc.csv` est renseignée pour cinq
transitions. Aucune figure ne la représente encore.

| Transition | Domaine fermé |
|---|---|
| TR-005 Recombinaison | régime opaque couplé matière-rayonnement |
| TR-022 Océans magmatiques | réseaux de réactions du liquide silicaté de haute température |
| TR-029 Oxygénation | habitats de surface strictement anaérobies, synthèse abiotique réductrice |
| TR-036 Code et traduction | réassignations majeures, architectures de traduction alternatives |
| TR-040 Multicellularités | autonomie des cellules devenues somatiques |

## 3. Comment régénérer

Graphviz doit être présent sur le `PATH`.

```bash
cd 00_socle
python carte_relationnelle/scripts/generer_carte_relationnelle_oric.py
python -m pytest -q
```

Le générateur devra d'abord recevoir `CLOS` et `INTG` dans son dictionnaire
`REL`, et `EXPECTED_COUNTS` devra être ajusté. Tant que ce n'est pas fait, le
test `test_repartition_des_codes` gèle volontairement la répartition actuelle.

## 4. Contrôle automatique

`tests/test_carte_relationnelle.py` vérifie que tout écart entre `relation` et
`code_cible` est accompagné d'une `note_codage`, et que chaque valeur de
`domaine_ferme` est non vide lorsqu'elle est déclarée. Le dossier ne peut donc
pas accumuler d'écarts silencieux.
