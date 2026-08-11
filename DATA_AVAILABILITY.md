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

## Généalogie cosmique empirique — provenance de la littérature

La couche `01_branche_matiere/genealogie_cosmique_quantitative/` ne redistribue aucun PDF d'article. `SOURCES_EMPIRIQUES.csv` conserve DOI/URL, classe de source, mode de preuve, stades concernés, portion effectivement utilisée et portion explicitement exclue. Les valeurs admissibles sont isolées dans `data/MESURES_EMPIRIQUES.csv` et proviennent uniquement d'observations astronomiques ou spatiales, d'échantillons retournés, de mesures isotopiques/chronométriques, d'expériences de laboratoire, de reconstructions planétaires ancrées dans des isotopes mesurés ou d'un produit observationnel officiel.

La politique `EMPIRICAL_ONLY_POLICY.json` interdit comme preuve toute simulation, donnée synthétique ou construite, imputation, sortie numérique de modèle, table de rendement stellaire théorique, sortie thermochimique et intégration orbitale. Lorsqu'un article mélange mesures et modèles, seules les grandeurs mesurées transcrites sont admissibles ; les sorties modélisées restent documentées dans `portion_excluded`. `resultats/AUDIT_ADMISSIBILITE.json` contrôle ce pare-feu et doit rester à zéro pour simulation, synthétique et imputation. Le raccordement final atteint l'architecture présente mais laisse la trajectoire orbitale unique `undetermined_empirical_only`.

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

Les trois jeux publics enregistrés dans `plan_directeur/campagne_recherche_suivante/sources_externes.json` sont intégrés au dossier source pour rendre la campagne reproductible sans dépendre d'un téléchargement pendant GitHub Actions. Chaque jeu conserve son DOI, sa licence, ses empreintes SHA-256 et un fichier `SOURCE.json`.

Les données restent tierces. Leur intégration ne les transforme pas en productions ORI-C. Les deux jeux Dryad sont conservés avec l'archive complète fournie par le dépôt et les seuls fichiers nécessaires aux analyses. Le fichier NOAA conserve son préambule, ses métadonnées et les références originales.

### Résilience de l'acquisition active

Le workflow contrôle les données intégrées en mode hors ligne par défaut. Un rafraîchissement distant reste possible sur demande avec `telecharger_donnees`, mais un refus HTTP du fournisseur n'est plus nécessaire à l'exécution reproductible. Le client conserve la résolution par DOI, la validation de format, le repli vers l'archive complète et le remplacement atomique pour les rafraîchissements volontaires.

## Intégration maximale des données déjà présentes

Avant la campagne complète, `plateforme/campagne_maximale_reelle/integrer_donnees_existantes.py` raccorde désormais les jeux réels dispersés dans les trois branches. Il n'utilise jamais les gabarits synthétiques de `examples/data` et ne remplit aucune valeur absente.

Les tables produites, leurs volumes, leur provenance et leur portée sont documentés dans :

- `plateforme/campagne_maximale_reelle/DONNEES_UTILISEES_MAXIMUM.md`
- `plateforme/campagne_maximale_reelle/INTEGRATION_MAXIMALE_DONNEES_EXISTANTES.md`
- `plateforme/campagne_maximale_reelle/PROVENANCE_INTEGRATION_DEPOT.json`
- `plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json`
- `plateforme/campagne_maximale_reelle/AUDIT_DONNEES_DEPOT.md`

Le registre de portée empêche une table partielle de valider des protocoles qu'elle ne mesure pas. Les données GISTEMP observationnelles ne sont notamment pas requalifiées en ensemble climatique multi-modèles, et les états orbitaux ne sont pas requalifiés en histoires géochimiques planétaires.

## Lot scientifique maximal du 5 août 2026

Le lot fourni par l'utilisateur est documenté sous `donnees_externes/lot_scientifique_maximal_2026_08_05/`. Le fichier `SOURCE.json` conserve le nom d'origine, la taille, l'empreinte SHA-256 et l'adresse directe des 29 fichiers reçus. Les archives brutes volumineuses ne sont pas dupliquées dans le dépôt. Les tables canoniques dérivées et leur registre de portée sont versionnés.

La petite source brute nécessaire à la reconstruction des 32 expériences de partage du carbone est conservée séparément dans `donnees_externes/partage_carbone_2026/`. Les ensembles climatiques, réseaux KIDA et UMIST, rendements CCSN, traceurs isotopiques et proxys endosymbiotiques sont conservés dans les tables canoniques de `plateforme/campagne_maximale_reelle/data/`. Les abondances d'acides aminés, le dégazage de Murchison, les propriétés thermiques des météorites et les modèles H-C restent des tables auxiliaires lorsque leur structure ne ferme pas un contrat canonique.

Le tri complet est documenté dans :

- `plateforme/campagne_maximale_reelle/LOT_SCIENTIFIQUE_2026_08_05.md`
- `plateforme/campagne_maximale_reelle/TRI_LOT_SCIENTIFIQUE_2026_08_05.json`
- `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`

Le fichier brut `SIMPLE_CCSNe_v3p1.hdf5` n'est pas redistribué dans cette archive. Son empreinte et son lien direct sont conservés dans `SOURCE.json`, tandis que les rendements élémentaires et isotopiques dérivés restent versionnés dans les tables canoniques.


## Corpus réel du 7 août 2026

Le corpus externe `DONNEES_REELLES_ORI-C_2026-08-07(1).zip` est enregistré par son SHA-256 `619bbab8482073076aa6d68d6f6947098b584ce40a7f7c78b4d8b2d097840fb2`. La sélection intégrée, les empreintes par fichier, les licences et les usages interdits sont décrits dans `donnees_externes/donnees_reelles_2026_08_07/SOURCE_BUNDLE.json`.

La mise à jour retient une compilation GEOROC de traceurs, une grille thermodynamique calculée depuis des paramètres publiés, un inventaire volatil documentaire, un jeu climatique GISTEMP/HadCRUT5 et quatre séries paléoclimatiques longues EPICA/Vostok/LR04. Leur présence ne suffit pas à produire un verdict. `EMPIRICAL_POLICY.json` est la politique fail-closed qui décide, test par test, si une ressource peut être utilisée comme entrée empirique.

Les sources paléoclimatiques longues sont conservées pour un futur protocole préenregistré ; aucun test orbital-climat n'est débloqué automatiquement. `planetary_histories.csv` reste volontairement absent faute de provenance primaire complète par cellule.

### Généalogie cosmique — approfondissement quantitatif empirique
La branche `01_branche_matiere/genealogie_cosmique_quantitative/` conserve son autorité empirique (33 sources, 76 mesures, 16 claims) et ajoute une vue analytique 23 stades / 40 relations / 24 observations sélectionnées / 12 synthèses machine, toutes dérivées exclusivement de mesures admises. Aucune simulation, donnée synthétique, imputation, rendement théorique ou sortie thermochimique n’entre dans ces résultats.

