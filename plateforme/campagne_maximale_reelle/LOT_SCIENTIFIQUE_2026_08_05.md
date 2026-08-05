# Tri du lot scientifique reçu le 5 août 2026

## Intégré dans les tables canoniques

- `KeySeries.zip`, HadCRUT5 CSV, CMIP6 NASST, ensembles CMIP6 globaux et `globalmean.zip`
- KIDA 2024 et UMIST Rate22
- `SIMPLE_CCSNe_v3p1.hdf5`
- compilation D/H, Ca lunaire et Mn-Cr Ivuna
- expériences de partage du carbone
- matrice HMM résumée des endosymbiotes

## Conservé comme donnée auxiliaire

- abondances et incertitudes d'acides aminés
- profils de dégazage de Murchison
- propriétés thermiques de météorites
- modèles H-C noyau et inventaire global
- comptages PGN des pucerons

## Écarté des calculs canoniques

- HadCRUT NetCDF : doublon du CSV utilisé
- sorties HMM brutes : la matrice résumée contient les variables retenues
- incertitudes d'acides gras : fichier d'abondances correspondant absent
- `TableS3.xlsx` : standards et calibration SIMS
- `Dataset_Fig2.xlsx` : métadonnées insuffisantes pour nommer les variables sans interprétation externe
- mesures ICP-MS brutes de Murchison : protocole de normalisation insuffisant pour fermer un bilan volatil

Le détail machine est dans `TRI_LOT_SCIENTIFIQUE_2026_08_05.json`. Aucun fichier écarté n'est utilisé pour débloquer un test.
