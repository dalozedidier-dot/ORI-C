# Publication stable v0.9.7-research

Cette publication est un **snapshot stable et citable du programme**, pas une validation générale d’ORI-C. Elle fige ensemble le code, les données versionnées, les résultats positifs, les résultats négatifs et leurs limites au **12 août 2026**.

## Frontière scientifique figée

- Astronomie N-corps : **13 critères préenregistrés réussis sur 15**. Les deux échecs restent publiés.
- Spin-orbite : couche séculaire exécutée jusqu’à l’obliquité et l’insolation, avec couple lunaire effectif ; Lune N-corps explicite et marées hors portée.
- Paléoclimat M2 : **1 critère sur 10**, donc formulation **non soutenue** ; le témoin M1P de même complexité reste la comparaison déterminante.
- D’Onofrio et vésicules : certifications spécialisées conservées ; les mesures locales de `P_acc` restent rétrospectives ou spécifiques à leur protocole.
- Matière : `C-MAT-MEM-05` reste `does_not_support` ; les relations partielles positives ne sont pas converties en chaîne complète.
- Généalogie cosmique quantitative : **48 sources/datasets empiriques admissibles**, **120 enregistrements empiriques historiques**, **11 467 lignes utiles** dont **11 207 grains présolaires admissibles**. L’audit impose **0 simulation, 0 donnée synthétique, 0 imputation comme preuve**.
- Benchmark transversal : **6 claims sur 21** renseignent les sept champs `X, H, m, Θ, τ, P_acc, R`, représentant **5 systèmes distincts**. Deux systèmes possèdent une intervention directe sur `m`. Le cas vésiculaire conserve son contraste local `P_acc` non soutenu dans la direction testée. `EXO-DOM-01`, au niveau `E4_modele`, maintient `X`, `Θ` et l’architecture appariés, applique `do(m)` aux traces lentes puis mesure `P_acc = 0,91` contre `0,87`, soit `|Delta P_acc| = 0,04` avec sham `= 0`. Ce résultat établit un effet causal interne au modèle, pas une réplication empirique. **Aucun invariant transversal général ORI-C n’est validé**.
- Formalismes externes et PCMCI+ : exploratoires ou méthodologiques, sans reclassement automatique des certifications.

## Autorité machine

`preuves/PREUVES.json` porte les statuts et empreintes. `preuves/CHIFFRES.json` relie les chiffres publics aux sorties machine. `ETAT_DES_PREUVES.md` est généré. Une divergence source → registre → rendu public est une erreur de publication.

## Automatisation

Le tag `v0.9.7-research` déclenche `.github/workflows/release.yml`. Le workflow hydrate Git LFS, exécute les validations, teste les couches astronomique, spin-orbite et mémoire ainsi que les formalismes légers, exécute la campagne maximale et la généalogie cosmique, reconstruit les sous-manifestes mémoire et revue systématique puis le manifeste racine en dernier, construit l’archive canonique et joint l’archive et son SHA-256 à la release GitHub.

## GitHub Pages

La page publique est construite depuis `site/`. Avant déploiement, le workflow Pages exécute `scripts/valider_publication_stable.py`, qui appelle le validateur des registres machine.

## DOI

`.zenodo.json` est synchronisé sur `0.9.7-research`. L’obtention d’un DOI exige l’activation de l’intégration GitHub dans Zenodo et la publication effective de la release. Aucun DOI n’est inscrit tant qu’il n’existe pas.

Le champ `license` Zenodo vaut `MIT` pour le logiciel. Le dépôt complet est à licences multiples ; `LICENSING.md` fait autorité pour les données, textes, figures et contenus tiers.

## Commandes locales

```bash
git lfs pull
python verifier_dossier.py
python scripts/valider_tout.py --strict-lfs
python scripts/valider_registre_preuves.py
python scripts/valider_publication_stable.py
python scripts/controle_avant_push.py
python scripts/construire_archive_canonique.py --output-dir dist
```

L’ordre de reconstruction des manifestes est obligatoire : **mémoire → revue systématique → racine**.
