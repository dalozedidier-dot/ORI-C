# Publication stable v0.9.8-research

Cette publication est un **snapshot stable et citable du programme**, pas une validation générale d’ORI-C. Elle fige ensemble le code, les données versionnées, les résultats positifs, les résultats négatifs et leurs limites au **15 août 2026**.

## Frontière scientifique figée

- Astronomie N-corps : **13 critères préenregistrés réussis sur 15**. Les deux échecs restent publiés.
- Spin-orbite : couche séculaire exécutée jusqu’à l’obliquité et l’insolation, avec couple lunaire effectif. Lune N-corps explicite et marées hors portée.
- Paléoclimat M2 : **1 critère sur 10**, donc formulation **non soutenue**. Le témoin M1P de même complexité reste la comparaison déterminante.
- Matière : le baseline de fermeture stricte reste **46/53**. L’extension empirique HC02-E1 atteint 53/53 sans recoder le baseline et ne reçoit aucun crédit §XIV automatique. `C-MAT-MEM-05` reste `does_not_support`.
- Généalogie cosmique quantitative : **48 sources/datasets empiriques admissibles**, **120 enregistrements empiriques historiques**, **11 467 lignes utiles** dont **11 207 grains présolaires admissibles**. L’audit impose **0 simulation, 0 donnée synthétique, 0 imputation comme preuve**.
- Données réelles vivant : Card 2019, Lamrabet 2019, Petrungaro 2026, Nader 2026, Wong & Seguin 2015 et Santos-Lopez 2021 sont conservés comme protocoles séparés. Leur qualification reste attachée à chaque analyse.
- Analyses réelles étendues : `FIT-ORIGIN-N-01` détecte une dépendance à l’origine ancestrale sous azote avec p exact **0,03069**. `MAT-NBOT-PART-01` mesure un gain RMSE hors-source de **28,27 %** avec permutation p **0,001999**, NBO/T étant classé comme état structural et non comme mémoire. `RNA-PAP-TRAJ-01` mesure une divergence maximale de **17,733 log2** entre deux trajectoires ARN et reste descriptif au niveau inter-branche.
- Benchmark transversal : **24 cas**, dont **6 cas complets** sur `X, H, m, Θ, τ, P_acc, R`, représentant **5 systèmes distincts**. Le registre machine contient **56 preuves**.
- `INV-A` : deux systèmes possèdent une intervention directe sur `m`. Un seul soutient un effet positif et ce soutien reste au niveau modèle. Aucun soutien empirique direct positif qualifié n’est acquis. Le statut reste `candidate_operationalized_exploratory_not_validated`.
- Seuil scientifique §XIV : **7/12**. Les conditions **3, 4, 9, 10 et 11** restent ouvertes. Aucune analyse rétrospective n’est convertie en prédiction prospective, réplication indépendante ou `P_acc` causal empirique.
- Formalismes externes et PCMCI+ : exploratoires ou méthodologiques, sans reclassement automatique des certifications.

## Autorité machine

`preuves/PREUVES.json` porte les statuts et empreintes. `preuves/CHIFFRES.json` relie les chiffres publics aux sorties machine. `ETAT_DES_PREUVES.md` est généré. Une divergence source → registre → rendu public est une erreur de publication.

Le snapshot de préparation du tag contient **1 847 contenus manifestés**, **56 preuves** et **90 chiffres canoniques**. Le fichier historique `preuves/SNAPSHOT_STABLE_0.9.8.json` sera ajouté après la publication effective afin d’y inscrire le commit exact du tag et le SHA-256 réel de l’archive canonique, sans valeur inventée.

## Automatisation

Le tag `v0.9.8-research` déclenche `.github/workflows/release.yml`. Le workflow hydrate Git LFS, exécute les validations de publication, teste les couches astronomique, spin-orbite et mémoire, les formalismes externes, la campagne maximale et la généalogie cosmique, reconstruit les sous-manifestes mémoire et revue systématique puis le manifeste racine en dernier, construit l’archive canonique et joint l’archive et son SHA-256 à la release GitHub. La campagne centrale et les nouveaux workflows de données réelles sont validés sur le commit de `main` avant la création du tag.

## GitHub Pages

La page publique est construite depuis `site/`. La publication 0.9.8 met à jour la version affichée, le compteur de contenus, le benchmark transversal, le registre de preuves, le §XIV et les trois nouvelles analyses sur données réelles. Avant déploiement, le workflow Pages exécute `scripts/valider_publication_stable.py`, qui appelle le validateur des registres machine.

## DOI

`.zenodo.json` est synchronisé sur `0.9.8-research`. L’obtention d’un DOI exige l’activation de l’intégration GitHub dans Zenodo et la publication effective de la release. Aucun DOI n’est inscrit tant qu’il n’existe pas.

Le champ `license` Zenodo vaut `MIT` pour le logiciel. Le dépôt complet est à licences multiples. `LICENSING.md` fait autorité pour les données, textes, figures et contenus tiers.

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
