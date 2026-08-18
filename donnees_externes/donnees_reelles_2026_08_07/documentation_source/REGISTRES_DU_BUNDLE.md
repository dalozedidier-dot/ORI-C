# Registres du bundle `DONNEES_REELLES_ORI-C_2026-08-07(1).zip`

Le bundle et son arborescence décompressée vivaient hors du dépôt, à côté de lui.
Ils ont été supprimés le 18 août 2026 après vérification : sur 406 fichiers,
106 étaient déjà dans le dépôt à l'octet près, 12 y existaient en version égale
ou plus récente, et les 287 restants (713 Mo) provenaient tous de fournisseurs
publics identifiés — GEOROC/DIGIS, NASA GISS, Met Office, Zenodo, UMIST, KIDA,
CHNOSZ, NOAA GML, SILSO, AMDC. Aucune production originale ORI-C n'a été perdue.

Ce qui ne se reconstruit pas, en revanche, c'est la trace de l'acquisition :
quels fichiers ont été tirés, d'où, quand, sous quelle licence, et avec quelle
empreinte. Ce sont ces registres, et eux seuls, qui sont conservés ici. Ils
pèsent 600 Ko et rendent les 713 Mo re-téléchargeables un par un, avec
vérification d'empreinte.

## Contenu

| fichier | rôle |
|---|---|
| `ACQUISITION_GEOROC.json` | 185 fichiers GEOROC (427,7 Mo), chacun avec son DOI, son URL et son SHA-256 ; 6 DOI de compilation distincts |
| `ACQUISITION_bundle.json` | 40 entrées d'acquisition du 7 août 2026, empreintes comprises, dont un échec enregistré |
| `MANIFESTE_bundle.csv` | inventaire des 402 fichiers du bundle : chemin, octets, SHA-256, type, domaine, jeu, fournisseur, identifiant, licence, description, origine |
| `MANIFESTE_bundle.json` | même inventaire, forme structurée |
| `LISEZ_MOI_bundle.md` | mode d'emploi du corpus tel qu'il était livré |

`RETRAITS.json` et `NOTICE_TABLES_CANDIDATES.md`, déjà présents dans ce dossier,
complètent l'ensemble : le premier motive les fichiers écartés, le second
documente les tables candidates non validées. La `NOTICE.md` du bundle n'a pas
été reprise : `NOTICE_TABLES_CANDIDATES.md` la supersède, en conservant son
tableau d'origine annoté « avant erratum » et en y ajoutant l'état courant sous
`fail_closed_v2`.

Le sous-ensemble effectivement retenu pour le dépôt — 8 fichiers, 20,6 Mo — est
décrit par `../SOURCE_BUNDLE.json`, qui porte aussi le SHA-256 du zip d'origine,
`619bbab8482073076aa6d68d6f6947098b584ce40a7f7c78b4d8b2d097840fb2`.

## Fins de ligne

Ces cinq fichiers arrivaient en CRLF. Le dépôt impose `eol=lf` (voir
`.gitattributes`), et un fichier CRLF versionné fait diverger le manifeste de ce
qu'un clonage restitue. Ils ont donc été convertis en LF, à contenu identique.
Leurs empreintes d'origine, avant conversion, sont consignées ici pour qui
voudrait les rapprocher du zip :

| fichier | SHA-256 du fichier CRLF d'origine |
|---|---|
| `MANIFESTE.csv` | `1ba4b7500862c84d0b9d8748885f7e54dbc5ef19912367242e359f57a5e91636` |
| `MANIFESTE.json` | `ca6237937740ba7bf26fc663aeb2c94054264c35077e95166b17851c170bd610` |
| `LISEZ_MOI.md` | `5558c164eeae746335b823532b8058a7fe37a7f333314639677f0f65ee3de3fc` |
| `ACQUISITION.json` | `40162ff4647459b79bf6adb3b31c4dfa72de46566dd726df99acb230f528d19b` |
| `ACQUISITION_GEOROC.json` | `de5b86a6e6c114a382a378d0f7d6c49bce05236233a7ea560f1b1c15905ff08f` |

Les empreintes internes à `MANIFESTE_bundle.csv` et aux journaux d'acquisition
décrivent les fichiers de données eux-mêmes et restent valables telles quelles.

## Le second dossier, `DONNEES_MATIERE_ORI-C`

Il servait de `racine_locale` à la campagne « mémoire matérielle réelle » et
pesait 6,2 Go. Il a été supprimé le même jour, sans rien conserver : les 52
sources de `01_branche_matiere/memoire_materielle_reelle/SOURCES.json` portent
toutes un identifiant de record Zenodo, et `telecharger_toutes_sources.py` les
retire par ce record. Le dossier n'était qu'un cache.

Sa provenance locale couvrait 52 sources contre 46 dans
`01_branche_matiere/memoire_materielle_reelle/donnees/PROVENANCE.json`. Les six
sources téléchargées le 9 août sans jamais être exploitées par la campagne
restent déclarées dans `SOURCES.json`, donc re-téléchargeables :
`carbures_matrice_acier` (19334962), `fluage_fatigue_grade` (7198219),
`fluage_relaxation_martensitique` (14051050), `nanoindentation_stem` (21296200),
`shkh15_traitement` (19557697), `synchrotron_in_situ_effets` (8387004).
