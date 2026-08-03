# Ce qui a été délibérément exclu

La règle de la campagne est : **aucune donnée simulée, inventée ou imputée.**
Quatre exclusions ont été appliquées, chacune vérifiée.

## 1. Gabarit de lignées prébiotiques

`data/prebiotic_lineages_raw.csv`, huit lignes portant le marqueur
`GABARIT_SYNTHETIQUE`. Retiré. Il était présent dans **quatre paquets
successifs** — campagne initiale, extension GISTEMP et campagne étendue — alors que leurs bilans
annonçaient « aucune donnée synthétique n'est utilisée ».

**À supprimer dans le générateur en amont**, sinon il reviendra.

## 2. Trois jeux fabriqués par la plateforme

| Fichier | Contenu réel | Donnée réelle correspondante |
|---|---|---|
| `antibiotic_cycles_generated.csv` | `L001_R00`, antibiotique « A », dose 0,25 | Windels : `W_AMK12p5`, amikacine, 12,5 |
| `antibiotic_design_generated.csv` | plan fabriqué | — |
| `prebiotic_design_generated.csv` | plan fabriqué | — |

Ces fichiers étaient produits par les moteurs de la plateforme quand la table
réelle manquait. Les données réelles Windels et Papastavrou les remplacent
désormais ; les versions fabriquées sont écartées.

## 3. Résultats partiels d'une intégration inachevée

`02_branche_systeme_solaire/couche_astronomique/integration_reelle/` est
conservé **pour la traçabilité seulement**, avec son `AVERTISSEMENT.md` :
l'essai porte sur 20 ka au lieu des 2 Ma visés, et sa dérive d'énergie dépasse
de quatre ordres de grandeur celle de l'intégration N-corps du dossier.

## 4. Caches d'exécution

`__pycache__`, `.pytest_cache`, `.mplconfig` sont exclus de l'archive et du
manifeste. Ce sont des artefacts, pas du contenu.

## Ce qui est conservé, et pourquoi

Les **bancs synthétiques du socle** — `00_socle/banc_synthetique/` — sont
conservés. Ils ne prétendent pas mesurer le monde : ils testent si les
définitions du `CODEBOOK.md` produisent une décision reproductible quand la
réponse est connue par construction. Leur statut est déclaré *exploratoire*
dans `AUTORITE_DES_DOCUMENTS.md`, et aucun verdict scientifique n'en découle.

L'**intégration N-corps** du dossier est également conservée. Ce n'est pas une
donnée simulée au sens de la règle : ce sont les positions mesurées de quinze
corps par JPL Horizons DE441, propagées par les lois de la gravitation, et
confrontées à une solution publiée indépendante. Elle est validée par 13 tests
d'acceptation sur 15 et par l'égalité de son spectre avec celui de La2004.
