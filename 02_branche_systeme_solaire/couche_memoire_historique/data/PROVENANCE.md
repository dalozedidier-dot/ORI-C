# Provenance des données

## LR04

- fichier : `raw/lisiecki2005-d18o-stack-noaa.txt`
- source :
  https://www.ncei.noaa.gov/pub/data/paleo/contributions_by_author/lisiecki2005/lisiecki2005-d18o-stack-noaa.txt
- jeu de données : doi:10.25921/k88j-0106
- publication : Lisiecki et Raymo, 2005, doi:10.1029/2004PA001071
- SHA-256 :
  `ec3c4af8f80c4de1d36fb0ac9fabbde28520f77f0832958caacbae4957afb412`
- accès : 29 juillet 2026

## La2004

- fichier : `raw/INSOLN.LA2004.BTL.ASC`
- source :
  https://ssp.imcce.fr/insola/earth/online/earth/La2004/INSOLN.LA2004.BTL.ASC
- documentation : `raw/La2004_README.TXT`
- publication : Laskar et al., 2004,
  doi:10.1051/0004-6361:20041335
- SHA-256 des éléments orbitaux :
  `3f13b9f8e69085baf40bc67a2669e6f6af4148fef9218ed2158772aa91e35f8c`
- SHA-256 du README :
  `7b5ab619cbc629425fd19879ca81d0b8439e134668a8f26579e9bdf613ed8b9e`
- accès : 29 juillet 2026

## Transformation

`data/processed/mpt_lr04_la2004.csv` est généré par
`oric_memory_tests.data.prepare_mpt_dataset`.

- grille : 2 600 à 0 ka BP
- pas : 1 ka
- LR04 : interpolation linéaire sur la grille
- insolation : moyenne journalière au solstice d’été, latitude 65°N,
  constante solaire 1 365 W m⁻²

