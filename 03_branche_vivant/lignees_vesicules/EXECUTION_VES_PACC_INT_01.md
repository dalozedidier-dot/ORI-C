# VES-PACC-INT-01 — passage laboratoire → analyse gelée

Ce document n'ajoute aucun seuil scientifique au protocole. Il décrit uniquement le format d'entrée et la chaîne logicielle qui permettent d'appliquer `PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json` sans ressaisie manuelle des décisions.

## Porte avant données

Aucune donnée prospective de test ne doit être acquise ou préparée tant que `VES-PACC-INT-01.registration.json` n'indique pas un enregistrement public avec URL et horodatage antérieur aux données. `preparer_ves_pacc_int_01.py` et `analyser_ves_pacc_int_01.py` contrôlent tous deux cette porte et vérifient les SHA-256 gelés du protocole et du script d'analyse.

Le mode `--check-schema` du préparateur est le seul mode prévu avant cette ouverture. Il contrôle le raccordement logiciel au protocole sans lire de donnée expérimentale.

## Tables de laboratoire

Le format machine est défini dans `SCHEMA_ENTREE_VES_PACC_INT_01.json` :

- `parents.csv` : une ligne par population parentale indépendante, avec les quatre ancres de réponse et les composantes de `X`
- `arms.csv` : une ligne par parent et par bras `control`, `do_m`, `sham`, avec DLS et variables nécessaires au contrôle des tolérances d'architecture
- `responses.csv` : une ligne par parent × bras × défi, avec les quatre réponses futures
- `execution_log.json` : conformité procédurale, déviations, randomisation, ordre intervention → réponse et maintien de l'aveugle

Le préparateur refuse les parents dupliqués, les bras manquants, les défis absents ou supplémentaires, les valeurs non finies et les colonnes hors schéma requises. Les douze identifiants de défi et les quatre dimensions sont lus depuis le protocole gelé.

## Production de la table d'analyse

Après ouverture publique de la porte :

```bash
python 03_branche_vivant/lignees_vesicules/preparer_ves_pacc_int_01.py \
  --raw-dir 03_branche_vivant/lignees_vesicules/ves_pacc_int_01_raw
```

Le script normalise chaque réponse future par l'ancre pré-intervention du même parent et produit :

- `ves_pacc_int_01_analysis_ready.npz`
- `ves_pacc_int_01_analysis_ready.metadata.json`

Le JSON de métadonnées conserve l'ordre des parents, l'ordre des défis, les SHA-256 des quatre entrées brutes, les drapeaux d'appariement et les tests de fidélité `do(m)`/sham. Les tolérances ne sont jamais saisies dans le préparateur : elles sont lues dans le protocole canonique.

## Analyse confirmatoire

La seule analyse confirmatoire reste :

```bash
python 03_branche_vivant/lignees_vesicules/analyser_ves_pacc_int_01.py
```

Elle relit le protocole, vérifie son empreinte, vérifie l'empreinte du script d'analyse, exige les données préparées et applique `PACC-INT-CHALLENGE-V1`. Une préparation non qualifiée reste publiable comme descriptive, mais ne peut pas fermer la qualification causale stricte.

## Ce que cette couche change

Elle ferme un risque opérationnel : auparavant, le protocole et l'analyse existaient mais aucune conversion canonique des tables de laboratoire vers les cubes `n × 12 × 4` n'était définie. Cette couche rend cette conversion vérifiable sans modifier `PRED-VIVANT-HISTOIRE-001`, les prédictions gelées, les seuils de `VES-PACC-INT-01` ni le statut actuel du §XIV.
