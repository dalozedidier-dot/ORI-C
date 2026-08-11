# État des preuves

> **Fichier généré. Ne pas modifier à la main.** Source : `preuves/PREUVES.json`.

Les certifications historiques restent inchangées. Les nouvelles analyses importées sont explicitement séparées en exploratoire, non concluant ou modèle.

## Résultats certifiés

| ID | Verdict | Niveau | Portée | Artefact |
|---|---|---|---|---|
| `C-ANT-01` | **supports** | E2 | empirique_externe | `03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/RESULTAT.json` |
| `C-VES-02` | **supports** | E2 | empirique_externe | `03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json` |
| `C-VES-03` | **supports** | E4 | empirique_externe | `03_branche_vivant/lignees_vesicules/resultats/RESULTAT.json` |
| `C-MAT-MEM-05` | **does_not_support** | — | campagne_empirique_partielle_sans_admission_complete | `01_branche_matiere/memoire_materielle_reelle/derive/SYNTHESE_CAMPAGNE.json` |
| `C-AST-01` | **supports** | E4_modele | modele_physique_reduit_valide | `plan_directeur/campagne_maximale_trois_branches/resultats/systeme_solaire_robustesse.json` |

## Extensions exécutées sans reclassement des certifications

| ID | Statut | Verdict technique | Portée |
|---|---|---|---|
| `SPIN-ORB-EXE` | exploratoire | executed_model | modele_reduit |
| `VIAB-SPIN-01` | exploratoire | executed_not_kernel | modele_reduit |
| `PID-ANT-01` | exploratoire | executed | empirique_externe_secondaire |
| `CSTATE-01` | exploratoire | executed_finite_proxy | methodologique |
| `TOPO-MAT-01` | exploratoire | executed | structure_documentaire |
| `COT-MAT-01` | non_concluant | not_evaluable_missing_stoichiometry | structure_documentaire |
| `POWER-MAT-01` | exploratoire | prospective_simulation | dimensionnement |
| `MPT-M2-01` | resultat_negatif | does_not_support | modele_paleoclimatique_orbitally_tuned |
| `CCM-CLIM-01` | exploratoire | executed | observational_orbitally_tuned |
| `PCMCI-CLIM-01` | exploratoire | executed_raw_p | observational_orbitally_tuned |
| `LTEE-REPLAY-01` | exploratoire | secondary_reanalysis | empirique_externe_table_transcription |
| `ASSEMBLY-BRIDGE-01` | non_concluant | not_evaluable_missing_paired_observables | comparaison_formelle |
| `C-GC-01` | extension_genealogique | supports_narrow | mixte — Le dépôt quantifie la couverture des éléments par 6 familles de rendements; cela teste l’élargissement de l’inventaire modèle, pas une trajectoire galactique unique. |
| `C-GC-02` | extension_genealogique | supports_direct_material_inheritance | directe sur la matière conservée — Démontre une continuité matérielle pour des grains particuliers. |
| `C-GC-03` | extension_genealogique | supports_external_analogue | directe dans un autre système — V883 Ori fournit un test observationnel de l’héritage eau nuage→disque. |
| `C-GC-04` | extension_genealogique | supports_history_dependent_disk_structure | archive historique reconstruite — Les hétérogénéités isotopiques sont réelles; leur mécanisme exact n’est pas unique. |
| `C-GC-05` | extension_genealogique | supports_model | modèle mécanistique contraint — Le cadre de condensation relie inventaire et état global aux phases solides possibles. |
| `C-GC-06` | extension_genealogique | supports_historical_record | directe sur archives solides — Les solides primitifs enregistrent des événements distincts dans le temps. |
| `C-GC-07` | extension_genealogique | supports_model | modèle causal — Cohérent avec H011 du dépôt, ratio de seuil 3,33 entre conditions comparées. |
| `C-GC-08` | extension_genealogique | supports_history_changes_future_fate | archive + mécanisme physique — Exemple fort de variable historique qui change l’accès à fusion/différenciation. |
| `C-GC-09` | extension_genealogique | supports_reconstruction | reconstruction — Mars est cohérent avec une croissance rapide et un statut d’embryon préservé. |
| `C-GC-10` | ouvert | open_multiple_models | indirecte — Plusieurs mécanismes reproduisent des sous-ensembles des contraintes. |
| `C-GC-11` | liaison_certification_existante | linked_to_C_AST_13_of_15_E4_model | modèle causal aval — Le résultat certifié C-AST reste inchangé et sert de point aval. |
| `C-GC-12` | ouvert | open_not_certified | n/a — La branche documente et quantifie plusieurs maillons mais refuse le saut vers une preuve end-to-end. |

## Règle de lecture

Un calcul exploratoire ne devient pas une preuve certifiée par sa simple présence dans ce registre. `C-MAT-MEM-05` reste négatif, M2 reste non réussi, et `C-AST-01` reste limité au niveau modèle. Les ponts vers la théorie de la viabilité, la PID, la mécanique computationnelle, COT, CCM, LTEE et Assembly Theory sont des extensions méthodologiques ou des analyses supplémentaires. La généalogie cosmique quantitative enregistre séparément ses claims locaux et conserve son handoff vers C-AST ouvert tant que les conditions initiales orbitales ne sont pas dérivées avec leurs incertitudes.
