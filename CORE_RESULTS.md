# ORI-C — noyau de résultats à lire en premier

> Vue courte dérivée de `preuves/CORE_RESULTS.json`. Elle ne remplace ni `preuves/PREUVES.json` ni les verdicts d’autorité.

Le noyau contient **16 résultats** choisis pour couvrir les trois branches, les succès, les résultats négatifs, les limites et les verrous quantitatifs. Aucun statut n’est réécrit ici.

| Rang | Branche | ID | Lecture | Verdict d’autorité | Pourquoi il est dans le noyau |
|---:|---|---|---|---|---|
| 1 | Système solaire | `C-AST-01` | certifié positif | `supports` | Intervention architecturale la plus forte du dépôt, avec contrôle numérique explicite. |
| 2 | Système solaire | `SPIN-ORB-EXE` | modèle / exploratoire | `executed_model` | Propage l’architecture orbitale jusqu’au spin et à l’insolation, sans surclasser le niveau modèle. |
| 3 | Système solaire | `MPT-M2-01` | résultat négatif | `does_not_support` | Falsification locale importante : la formulation M2 testée ne bat pas son témoin apparié. |
| 4 | Système solaire | `EXO-DOM-01` | modèle / exploratoire | `supports_local_nonzero_delta_Pacc_under_direct_m_reset` | Test direct do(m) au niveau modèle avec P_acc causal local, utile comme patron expérimental. |
| 5 | Vivant | `C-ANT-01` | certifié positif | `supports` | Gain prédictif rétrospectif de l’histoire face à l’état seul et à une histoire permutée de même complexité. |
| 6 | Vivant | `C-VES-02` | certifié positif | `supports` | Signal parent-descendant supérieur au témoin permuté sur les lignées de vésicules. |
| 7 | Vivant | `C-VES-03` | certifié positif | `supports` | Ablation mécanistique sur données réelles, distincte du futur test prospectif VES-PACC-INT-01. |
| 8 | Vivant | `PACC-VES-ABL-01` | résultat négatif | `does_not_support_positive_Pacc_ablation_contrast` | Contraste P_acc exploratoire négatif pour la direction attendue ; limite conservée comme résultat. |
| 9 | Matière | `C-MAT-MEM-05` | résultat négatif | `does_not_support` | La transversalité complète histoire→trace→réponse n’est soutenue par aucune des familles exigées. |
| 10 | Matière | `M-26AL-01` | exploratoire | `derived_physical_history_trace_from_empirical_ages` | Quantifie une trace radiogénique d’histoire à partir d’âges empiriques. |
| 11 | Matière | `GCQ-T11` | extension quantitative empirique non preregistered | `supports_persistent_isotopic_architecture_across_large_inventory_change` | Quantifie la persistance de l’architecture isotopique NC/CC pendant une forte variation d’inventaire 26Al. |
| 12 | Matière | `GCQ-T12` | extension quantitative empirique non preregistered | `supports_gigayear_material_memory_carrier` | Borne la persistance de porteurs matériels présolaires sur des échelles gigannuelles. |
| 13 | Matière | `GCQ-T16` | extension quantitative empirique non preregistered | `strict_stellar_to_endpoint_chain_exists_but_primordial_end_to_end_closure_open` | Documente la chaîne stricte produits stellaires→endpoint tout en laissant ouverte la fermeture primordiale→endpoint. |
| 14 | Matière | `GCQ-T18` | extension quantitative empirique donnees massives non preregistered | `supports_multisystem_NC_CC_isotopic_separation` | Séparation isotopique NC/CC multivariée sur données massives réelles sans imputation. |
| 15 | Matière | `GCQ-T21` | extension quantitative empirique donnees massives non preregistered | `supports_returned_sample_multiscale_isotopic_heterogeneity` | Hétérogénéité isotopique multi-échelle dans des échantillons retournés, sans surinterprétation historique unique. |
| 16 | Matière | `GCQ-INTERSTAGE-01` | non concluant | `no_conservation_claim_after_publication_control` | Contrôle de publication qui empêche de transformer une association même-grain en claim de conservation. |

## Règle de lecture

Un lecteur externe peut commencer par cette page, puis ouvrir l’artefact de chaque ligne. Les résultats rétrospectifs restent rétrospectifs, les résultats de modèle restent au niveau modèle, et les résultats négatifs restent visibles. Le compteur §XIV demeure l’autorité pour les verrous de confirmation.
