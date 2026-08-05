# Données utilisées au maximum dans la campagne réelle

La campagne raccorde automatiquement les données réelles compatibles avec les schémas ORI-C. Les tables d'exemple synthétiques restent exclues.

## Matière et astro-chimie

- 40 transitions matérielles
- 41 expériences de partage métal-silicate, dont 35 lignes complètes pour P-T-redox-logD
- 16 434 réactions issues de KIDA 2024 et UMIST Rate22
- 19 conditions initiales Rate22
- 1 383 rendements élémentaires et 56 507 rendements isotopiques CCSN
- 84 éléments, 18 modèles, trois masses et six familles CCSN

## Système solaire, isotopes et climat

- La2004 et La2010
- JPL Horizons DE441
- LR04
- GISTEMP observationnel
- 63 600 lignes d'incertitude observationnelle NASA GISTEMP et HadCRUT5
- trajectoires CMIP6 historiques et SSP1-2.6, SSP2-4.5 et SSP5-8.5
- expériences idéalisées 4xCO2, +2 K et +4 K
- 142 745 lignes climatiques consolidées
- 362 mesures D/H et tables auxiliaires Ca lunaire et Mn-Cr Ivuna
- NASA Exoplanet Archive

## Vivant et prébiotique

- Papastavrou, Horning et Joyce : évolution d'ARN catalytique
- Windels et Donofrio : cycles, MIC, survie, persistance et fitness
- Sokolskyi et Baum : seize expériences de transfert, séries temporelles et mesures auxiliaires
- 85 génomes endosymbiotiques et 15 810 résultats HMM
- 253 comptages de familles géniques de pucerons, conservés en table auxiliaire

## Autres données auxiliaires conservées

- 1 387 mesures d'acides aminés dans 69 environnements
- 3 648 mesures de dégazage de Murchison dans trois conditions
- 61 propriétés thermiques de météorites
- modèles H-C noyau et inventaire global

## Tables canoniques nouvellement produites

- `modern_climate_ensemble.csv`
- `reaction_network.csv`
- `molecular_inventory.csv`
- `nucleosynthesis_yields.csv`
- `isotope_tracers.csv`
- `endosymbiosis_events.csv`
- extension de `partition_experiments.csv`

Les tables auxiliaires conservent les mesures qui ne satisfont pas un contrat canonique complet. Elles ne débloquent aucun test par leur seule existence.
