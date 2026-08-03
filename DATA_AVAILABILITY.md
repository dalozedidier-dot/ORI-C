# Données et provenance

Toutes les routes actives enregistrées dans les fichiers de provenance sont relatives à `plateforme/campagne_maximale_reelle`. Les fichiers de provenance donnent la date d’accès, les empreintes SHA-256 des fichiers bruts et transformés et, pour les exoplanètes, la requête TAP exacte.

- GISTEMP v4 : `plateforme/campagne_maximale_reelle/PROVENANCE_GISTEMP.json`.
- NASA Exoplanet Archive PS : `plateforme/campagne_maximale_reelle/PROVENANCE_EXOPLANET_ARCHIVE.json`.
- Antibiotiques, Windels et al. : `plateforme/campagne_maximale_reelle/PROVENANCE_WINDELS_ANTIBIOTIC.json`.
- ARN catalytique, Papastavrou, Horning et Joyce : `plateforme/campagne_maximale_reelle/PROVENANCE_PAPASTAVROU_RNA.json`.
- Données orbitales : La2004, La2010 et JPL Horizons DE441, décrites dans `data/provenance_reelle.json`.

La campagne d'inventaire accessible de la branche 1 ne consomme aucun fichier
brut : elle transcrit des valeurs publiées, chacune rattachée à une entrée du
registre `01_branche_matiere/hypergraphe_transformations/sources.csv`, qui
porte l'URL, le DOI quand il existe et la date d'accès.

- Budget azote par réservoir, Terre et Vénus : `S19`, Johnson et Goldblatt,
  *Earth-Science Reviews* 148, doi 10.1016/j.earscirev.2015.05.006.
- Azote du noyau par calcul ab initio, estimation concurrente : `S20`.
- Masses planetétaires et masse des océans : `S21`, NASA Planetary Fact Sheet.
- Carbone de la Terre silicatée et du noyau : `S22`, arXiv:2202.06809.
- Hydrogène et carbone du noyau et de la Terre globale : `S23`, arXiv:2508.17740.
- Soufre : `S24`, arXiv:2505.02641.
- Apport tardif : `S25`, Willbold, Elliott et Moorbath, *Nature* 477,
  doi 10.1038/nature10399, et `S27`, arXiv:1609.01785.
- Échantillon de Bennu : `S26`, NASA.

Les unités sont celles de la source — ppm, wt%, kg. La conversion en masse est
faite par `analyser_inventaire.py` à partir de masses de réservoir déclarées
dans `masses_reservoirs.csv`, jamais dans la saisie. Les colonnes non
contraintes restent vides : le validateur refuse tout inventaire accessible
chiffré dont les deux facteurs ne sont pas renseignés.

Les fichiers bruts volumineux sont inclus dans cette archive canonique mais exclus d’un futur dépôt Git par `.gitignore`. Les fichiers transformés et leurs empreintes restent présents pour permettre l’audit.

Les scripts d’import reproduisent les transformations sans imputation, interpolation, simulation ni augmentation. Les trois fichiers générés artificiellement présents dans une source antérieure ne sont pas repris dans l’archive canonique.
