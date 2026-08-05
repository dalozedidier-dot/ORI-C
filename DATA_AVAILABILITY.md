# Données et provenance

Toutes les routes actives enregistrées dans les fichiers de provenance sont relatives à `plateforme/campagne_maximale_reelle`. Les fichiers de provenance donnent la date d’accès, les empreintes SHA-256 des fichiers bruts et transformés et, pour les exoplanètes, la requête TAP exacte.

- GISTEMP v4 : `plateforme/campagne_maximale_reelle/PROVENANCE_GISTEMP.json`.
- NASA Exoplanet Archive PS : `plateforme/campagne_maximale_reelle/PROVENANCE_EXOPLANET_ARCHIVE.json`.
- Antibiotiques, Windels et al. : `plateforme/campagne_maximale_reelle/PROVENANCE_WINDELS_ANTIBIOTIC.json`.
- Benchmark antibiotique externe, Card et al. 2019 : `03_branche_vivant/benchmark_externe_card2019/SOURCE.json`, Dryad `10.5061/dryad.g41hg96`, données `CC0-1.0`.
- ARN catalytique, Papastavrou, Horning et Joyce : provenance canonique dans `plateforme/campagne_maximale_reelle/PROVENANCE_PAPASTAVROU_RNA.json` et copie de travail pour le programme prébiotique dans `03_branche_vivant/programme_prebiotique/donnees_reelles/trajectoires_population/`. Le jeu Dryad `10.5061/dryad.rxwdbrvgs` est distribué sous CC0.
- Données orbitales : La2004, La2010 et JPL Horizons DE441, décrites dans `data/provenance_reelle.json`.
- Benchmark stellaire MESA : étapes et critères d’arrêt transcrits depuis la documentation officielle `1M_pre_ms_to_wd` et `12M_pre_ms_to_core_collapse`, avec références dans `01_branche_matiere/hypergraphe_transformations/calibrage_v094/benchmark_externe_stellaire/sources.csv`. Le paquet ne redistribue pas les sorties numériques complètes de MESA.

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

## Trois formes de livraison à distinguer

1. **Dépôt Git avec Git LFS hydraté.** Les fichiers volumineux sont récupérés
   par `git lfs pull` et le contrôle strict peut réussir.
2. **ZIP source automatique de GitHub.** Il contient des pointeurs Git LFS à
   la place des objets volumineux. Il permet l'inspection du code et des
   métadonnées, mais ne constitue pas une archive scientifique autonome.
3. **Archive scientifique canonique hydratée.** Elle est construite avec
   `python scripts/construire_archive_canonique.py`, contient les objets réels,
   un manifeste vérifié et son propre SHA-256.

Les fichiers transformés et leurs empreintes restent présents pour permettre
l'audit. Les données tierces conservent les conditions de leur source et ne
reçoivent aucune nouvelle licence du projet ORI-C.

Les scripts d’import reproduisent les transformations sans imputation, interpolation, simulation ni augmentation. Les trois fichiers générés artificiellement présents dans une source antérieure ne sont pas repris dans l’archive canonique.

## Données de la recherche active

Les nouveaux bancs externes utilisent trois dépôts publics enregistrés dans `plan_directeur/campagne_recherche_suivante/sources_externes.json`. Les fichiers sont téléchargés au moment de l'exécution, contrôlés par SHA-256 et accompagnés d'un `SOURCE.json`.

Les données brutes tierces ne sont pas intégrées au dossier source. Les scripts, protocoles, parseurs, règles de décision et rapports d'acquisition sont conservés. Le workflow `Recherche suivante ORI-C` réalise l'acquisition avant les analyses.


### Résilience de l'acquisition active

Depuis la correction du 5 août 2026, les fichiers Dryad requis ne dépendent plus uniquement d'identifiants enregistrés une fois. Le client résout la version publique courante depuis le DOI, vérifie le contenu téléchargé, utilise l'archive complète en repli et protège le cache antérieur par remplacement atomique. Les identifiants fixes du registre sont conservés uniquement comme solution de secours lorsque l'API de métadonnées est indisponible.
