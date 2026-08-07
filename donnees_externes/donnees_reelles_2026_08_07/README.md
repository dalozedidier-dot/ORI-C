# Corpus réel du 7 août 2026

Cette entrée documente uniquement les fichiers du bundle externe qui ont été retenus dans le dépôt. Le bundle complet n'est pas recopié ici : il contient plusieurs centaines de mégaoctets et des licences hétérogènes.

Le fichier `SOURCE_BUNDLE.json` fixe l'empreinte SHA-256 du bundle et de chaque table retenue. `scripts/importer_bundle_donnees_reelles.py` permet de les réimporter après vérification des empreintes.

Règle scientifique : **présence d'un fichier ≠ preuve**. La portée empirique est contrôlée par `plateforme/campagne_maximale_reelle/data/REAL_DATA_COVERAGE.json`. Les tables thermochimiques et volatiles sont conservées comme ressources utiles mais ne débloquent aucun test de la matrice 683 dans l'état actuel. La compilation GEOROC ne débloque que `P5-001`, qui demande explicitement de compiler les traceurs.

`planetary_histories.csv` reste volontairement absent.
