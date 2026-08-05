# Instructions de mise à jour

## Fichiers à supprimer avant copie

**Aucun fichier à supprimer.**

Copier le contenu complet du ZIP en remplaçant les fichiers existants. Tous les fichiers ajoutés et remplacés doivent être publiés dans le même commit.

## Résultat attendu

La campagne maximale passe de 278 à **298 réussites techniques** et de 357 à **337 blocages**. Elle conserve 48 protocoles non exécutables informatiquement, 0 échec et 0 erreur. Le lot débloque 20 analyses supplémentaires sans modifier le statut scientifique confirmatoire : 0 soutien, 0 rejet et 635 résultats indéterminés.

## Corrections de reproductibilité incluses

- `partition_experiments.csv` est régénéré avec 41 expériences, dont 32 expériences de partage du carbone et 35 lignes complètes pour la méta-régression.
- Les modèles HDF5 sont parcourus dans un ordre canonique.
- Les rendements de nucléosynthèse sont calculés en pleine précision, puis sérialisés à 12 chiffres significatifs. Cette étape élimine uniquement les écarts d’octets de l’ordre de 10⁻¹³ à 10⁻¹⁵ produits par différentes configurations BLAS ; elle ne change aucun test couvert ni aucun verdict.

## Publication Git LFS obligatoire

Le fichier suivant pèse 100 443 546 octets et est suivi par Git LFS :

`donnees_externes/lot_scientifique_maximal_2026_08_05/raw/SIMPLE_CCSNe_v3p1.hdf5`

La règle `*.hdf5 filter=lfs diff=lfs merge=lfs -text` est ajoutée à `.gitattributes`. Publier la mise à jour depuis un clone Git ou GitHub Desktop avec Git LFS actif :

```bash
git lfs install
git add .
git commit -m "Intégrer le lot scientifique maximal"
git push
```

Ne pas publier cette mise à jour par simple copie de fichiers dans l’interface web : utiliser un clone Git ou GitHub Desktop afin que le filtre LFS soit appliqué.

## Fichiers ajoutés

- `donnees_externes/lot_scientifique_maximal_2026_08_05/SOURCE.json`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/210210_MurchisonSteppedHeating_ICPMSData.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/AA_abundances.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/AA_uncertainties.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/CMIP6_NASST_historical-ssp585-ssp245.zip`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Ca isotope data for analyzed lunar samples_Fu et al 2023.xlsx`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Dataset_Fig2.xlsx`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Dataset_Fig4_FigS1_FigS2_DC_1.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Dataset_Fig5_bulk_core.xlsx`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/HMM_summarized_results.zip`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/HadCRUT.5.1.0.0.analysis.ensemble_series.global.monthly.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/KeySeries.zip`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Measurement_data.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Murch-100airZn-GAS.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Murch-50airZn-GAS.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Murchison-vacc-Zn-GAS.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/Rodriguez_Supplementary_TableS1.xlsx`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/SIMPLE_CCSNe_v3p1.hdf5`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/TableS3.xlsx`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/TableS4.xlsx`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/aphid_PGN_count.csv`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/globalmean.zip`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/kida.uva.2024 (1).zip`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/original_ensembles.tar.gz`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/rate22_dipole.specs`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/rate22_final.rates`
- `donnees_externes/lot_scientifique_maximal_2026_08_05/raw/rate22_revised_CtoO_0.44.specs`
- `plateforme/campagne_maximale_reelle/LOT_SCIENTIFIQUE_2026_08_05.md`
- `plateforme/campagne_maximale_reelle/TRI_LOT_SCIENTIFIQUE_2026_08_05.json`
- `plateforme/campagne_maximale_reelle/data/aphid_pgn_gene_counts.csv`
- `plateforme/campagne_maximale_reelle/data/core_bulk_h_c_models.csv`
- `plateforme/campagne_maximale_reelle/data/endosymbiont_hmm_presence_absence.csv`
- `plateforme/campagne_maximale_reelle/data/endosymbiosis_events.csv`
- `plateforme/campagne_maximale_reelle/data/isotope_tracers.csv`
- `plateforme/campagne_maximale_reelle/data/ivuna_mn_cr_isotopes.csv`
- `plateforme/campagne_maximale_reelle/data/lunar_calcium_isotopes.csv`
- `plateforme/campagne_maximale_reelle/data/meteorite_thermal_properties.csv`
- `plateforme/campagne_maximale_reelle/data/modern_climate_ensemble.csv`
- `plateforme/campagne_maximale_reelle/data/molecular_inventory.csv`
- `plateforme/campagne_maximale_reelle/data/molecular_inventory_amino_acids_auxiliary.csv`
- `plateforme/campagne_maximale_reelle/data/murchison_degassing_profiles.csv`
- `plateforme/campagne_maximale_reelle/data/nucleosynthesis_isotope_yields.csv`
- `plateforme/campagne_maximale_reelle/data/nucleosynthesis_yields.csv`
- `plateforme/campagne_maximale_reelle/data/reaction_network.csv`
- `plateforme/campagne_maximale_reelle/integrer_lot_scientifique_2026_08_05.py`
- `plateforme/source_corrigee/tests/test_external_scientific_bundle.py`

## Fichiers remplacés

- `.gitattributes`
- `.github/workflows/analyse-donnees-reelles.yml`
- `DATA_AVAILABILITY.md`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.json`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.md`
- `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`
- `plateforme/campagne_maximale_reelle/DONNEES_UTILISEES_MAXIMUM.md`
- `plateforme/campagne_maximale_reelle/INTEGRATION_MAXIMALE_DONNEES_EXISTANTES.md`
- `plateforme/campagne_maximale_reelle/PROVENANCE_INTEGRATION_DEPOT.json`
- `plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json`
- `plateforme/campagne_maximale_reelle/data/partition_experiments.csv`
- `plateforme/campagne_maximale_reelle/integrer_donnees_existantes.py`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/REPORT.md`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/results.csv`
- `plateforme/campagne_maximale_reelle/resultats_integration_maximale/results.json`
- `plateforme/campagne_maximale_reelle/resumer_integration_maximale.py`
- `plateforme/source_corrigee/requirements-lock.txt`
- `plateforme/source_corrigee/requirements.txt`
- `plateforme/source_corrigee/src/oric_full/domains/biology.py`
- `plateforme/source_corrigee/src/oric_full/domains/climate.py`
- `plateforme/source_corrigee/src/oric_full/domains/matter.py`
- `plateforme/source_corrigee/src/oric_full/engines.py`
- `MANIFEST.sha256`
- `MANIFEST.sha256.json`
- `INSTRUCTIONS_MISE_A_JOUR.md`

## Fichiers écartés du calcul

Le lot original contenait aussi un doublon NetCDF HadCRUT, les sorties HMM brutes et un fichier d'incertitudes d'acides gras sans abondances correspondantes. Ils ne sont pas inclus dans le ZIP final. `TableS3.xlsx`, `Dataset_Fig2.xlsx` et les mesures ICP-MS brutes sont conservés pour la provenance, mais ne débloquent aucun test.

## Exécution GitHub

1. Ouvrir `Campagne maximale ORI-C - trois branches`.
2. Choisir `niveau = maximum`.
3. Vérifier l'étape `Intégrer toutes les données réelles déjà présentes`.
4. Télécharger l'artefact `analyses-donnees-reelles-*`.

Le bilan attendu est : **298 réussites, 337 blocages, 48 non exécutés, 0 échec et 0 erreur**.
