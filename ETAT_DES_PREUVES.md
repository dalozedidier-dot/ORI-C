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

## Règle de lecture

Un calcul exploratoire ne devient pas une preuve certifiée par sa simple présence dans ce registre. `C-MAT-MEM-05` reste négatif, M2 reste non réussi, et `C-AST-01` reste limité au niveau modèle. Les ponts vers la théorie de la viabilité, la PID, la mécanique computationnelle, COT, CCM, LTEE et Assembly Theory sont des extensions méthodologiques ou des analyses supplémentaires.
