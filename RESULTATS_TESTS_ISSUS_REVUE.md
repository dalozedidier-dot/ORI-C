# Campagne quantitative ORI-C sur données réelles

Date d'exécution : 2026-08-02. Aucun jeu synthétique ou simulé n'est utilisé comme donnée empirique. Les simulations AR(1) servent uniquement à construire l'hypothèse nulle du test spectral. Les résultats négatifs ne sont pas requalifiés en succès.

## Bilan exécutif

La campagne porte désormais sur sept confrontations quantitatives distinctes. Une propriété observationnelle du climat est nettement établie, une propriété numérique de la couche astronomique est robuste, et cinq tests limitent ou réfutent les formulations ORI-C actuelles. Aucun résultat ne valide encore ORI-C comme théorie causale générale.

| Test | Données | Résultat | Statut scientifique |
|---|---|---|---|
| Carte relationnelle hors nœud | 42 liens positifs, 673 négatifs | ΔAUC = -0,00460 ; p = 0,3387 | négatif |
| Histoire antibiotique | 358 prédictions, 148 lignées | gain MAE ≈ 1,8 % ; IC95 % traverse 0 | exploratoire, non robuste |
| LR04 contre bruit rouge | LR04, 0–2600 ka, 5 000 nulls/test | bandes 41 et 100 ka significatives sur la série complète | propriété des données, pas preuve ORI-C |
| Stabilité temporelle de 100 ka | trois fenêtres LR04 | significative seulement sur 0–1200 ka | non-stationnarité établie |
| Familles climatiques M0/M1/M2/M1P | calibration 2600–1200 ka, prédiction 1200–0 ka | M2 non identifiable et part 100 ka = 0,00284 contre 0,39393 pour LR04 | M2 abandonné |
| Six dimensions matière | 40 transitions | 0 bit propre et gain conditionnel nul | dimensions actuelles invalidées |
| Pacc observationnel commun | antibiotiques + LR04 | Pacc = 1 pour tous les états | métrique saturée, non causale |

La comparaison N-body/La2004 constitue en plus un test numérique de la couche astronomique : la corrélation de phase passe de 0,99997 à 100 ka à 0,49567 à 20 Ma, tandis que la période spectrale dominante reste appariée autour de 400–408 ka. Cela soutient la distinction phase/spectre, pas une interprétation climatique ORI-C.

## 1. Carte temporelle contre chronologie

Le benchmark laisse chaque transition cible entièrement hors apprentissage. La chronologie seule atteint une AUC de 0,91453, contre 0,90993 pour chronologie + régime ORI-C. Sur 1 000 permutations, p unilatéral = 0,3387.

Verdict : les attributs ORI-C actuels n'ajoutent pas d'information prédictive à la chronologie. La carte reste un schéma descriptif.

Résultat : `00_socle/carte_relationnelle/resultats_analyse/benchmark_hors_noeud.json`.

## 2. Résistance aux antibiotiques

Le benchmark Windels et al. (Zenodo 7550302 ; DOI `10.5281/zenodo.7550302`) sépare strictement les lignées sur 200 partitions. MAE : état courant 0,64083 ; témoin de complexité égale 0,64145 ; histoire 0,63009. L'IC95 % de `MAE(témoin) - MAE(histoire)` est [-0,03535 ; 0,05977].

Verdict : signal faible, non robuste et très inférieur au seuil confirmatoire gelé de 10 %. Il faut un jeu externe avec séquences d'exposition variées et identifiant longitudinal complet.

Résultat : `plateforme/campagne_maximale_reelle/resultats_consolides/benchmark_antibiotic_history.json`.

## 3. Climat : bandes spectrales et non-stationnarité

Chaque fenêtre LR04 est comparée à 5 000 réalisations d'un bruit rouge AR(1) ajusté sur cette fenêtre, avec correction de Bonferroni pour deux bandes. Sur 0–2600 ka, la bande 41 ka a p corrigé = 0,000400 et la bande 100 ka p corrigé = 0,000800.

La bande 100 ka est significative sur 0–1200 ka (p corrigé = 0,000400), mais pas sur 700–1900 ka (p = 1,0) ni 1400–2600 ka (p = 0,74545). La bande 41 ka reste significative dans les trois fenêtres.

Verdict : la cible climatique utile n'est pas une oscillation stationnaire à 100 ka, mais son émergence tardive. Le test ne démontre ni causalité astronomique ni mécanisme ORI-C.

Résultat : `02_branche_systeme_solaire/couche_memoire_historique/results_stress/tests_reels/n_nulls_spectraux_lr04.json`.

## 4. Climat : identifiabilité et prédiction hors échantillon

M0 et M1 sont numériquement identifiables entre quatre graines ; M2 et M1P ne le sont pas. Aucun des quatre modèles n'a des paramètres stables entre sous-fenêtres. Hors échantillon, M2 consacre 0,00284 de sa puissance à 100 ka, contre 0,39393 pour LR04 ; il n'engendre donc pas la propriété qu'il devait expliquer.

Verdict : M2 doit rester abandonné. Une nouvelle famille ne sera recevable que si elle produit explicitement l'émergence de la bande 100 ka, reste identifiable et bat un témoin sans mémoire de complexité comparable.

Résultat : `02_branche_systeme_solaire/couche_memoire_historique/results_stress/tests_reels/i_criteres_discriminants.json`.

## 5. Six dimensions de la branche matière

Sur 40 transitions, n, G, I, E et Pi ont chacune 3 bits d'entropie, entièrement expliqués par le régime : information propre = 0 bit. H est constante au niveau de base. Pour la fermeture de domaine, le gain conditionnel de chacune des six dimensions une fois le régime connu est nul.

Verdict : le remplissage formel ne constitue pas six mesures indépendantes. Les colonnes actuelles doivent être remplacées par plusieurs codeurs et des observables sourcées, et non renommées.

Résultat : `01_branche_matiere/base_transitions/information_dimensions.json`.

## 6. Pacc sur deux branches

Le même estimateur à cinq classes a été appliqué au prochain cycle observé des lignées antibiotiques et à LR04 à horizon 10 ka. Chaque classe initiale atteint les cinq classes futures dans les deux branches : Pacc observationnel = 1 partout.

Verdict : cette discrétisation sature et ne discrimine rien. En l'absence d'un ensemble d'interventions appariées, elle ne mesure pas une accessibilité contrefactuelle. Elle ne doit pas être présentée comme Pacc causal.

Résultat : `plateforme/campagne_maximale_reelle/resultats_consolides/pacc_observationnel_deux_branches.json`.

## 7. Astronomie : phase contre spectre

La corrélation entre l'intégration N-body et La2004 décroît de 0,99997 à 100 ka à 0,91248 à 6,9 Ma puis 0,49567 à 20 Ma. La période dominante reste appariée : 405,94 ka à 6,9 Ma et 408,18 ka à 20 Ma.

Verdict : la phase devient progressivement peu fiable tandis qu'une structure spectrale longue persiste. C'est un résultat numérique de robustesse de la couche astronomique, pas une validation de la mémoire climatique.

Résultat : `plateforme/campagne_maximale_reelle/degradation_phase_vs_spectre.json`.

## Décisions imposées par les résultats

1. Ne plus compter le nombre de fichiers comme niveau de preuve : un corpus volumineux peut contenir peu de contrastes identifiants.
2. Maintenir M2 abandonné et geler une nouvelle cible climat sur l'émergence non stationnaire de 100 ka.
3. Redéfinir Pacc autour d'interventions ou d'expériences naturelles appariées ; la portée observationnelle actuelle est saturée.
4. Remplacer les six dimensions matière par des codages indépendants avec accord inter-codeurs et données mesurées.
5. Étendre l'antibiotique à un jeu externe longitudinal avant toute revendication confirmatoire.
6. Maintenir la séparation stricte entre preuve disciplinaire, validation numérique et apport propre d'ORI-C.

## Campagne climatique approfondie

Une seconde campagne au budget complet a été rejouée le 2026-08-02. Le harnais principal a pris 367,7 s, T1–T4 1 161,2 s, G1 1 420 s, G2 680 s, G3 1 217,9 s et G4 3 070,8 s. Ces durées excluent les installations et les tests logiciels.

- Harnais principal : MPT ne passe qu'un critère sur dix. M2 est battu par M1P, son rapport spectral 100/41 ka vaut 0,00469 contre 2,60362 observé et l'autocorrélation de ses résidus vaut 0,97026.
- Exoplanètes : passage structurel seulement ; aucune des quatre variables n'atteint le critère matériel ou de persistance.
- T1 : le gain absolu M2/M1 ne représente que 0,3765 fois l'incertitude publiée de LR04 ; il n'est pas interprétable comme amélioration du modèle.
- T2, validation 5,3 Ma : M2 obtient RMSE 6,7566 contre 2,7674 pour M1P. Le gain relatif contre M1P est -1,4415, IC95 % [-1,7886 ; -0,8098].
- T3 : quatre solutions La2010, 2 601 points ; dispersion relative moyenne d'excentricité 5,19e-4, maximum absolu 1,06e-4.
- T4 : selon le franchissement gelé du rapport spectral 100/41 = 1, LR04 franchit vers 4 350 ka et M2 vers 1 850 ka ; M0 et M1P ne franchissent jamais.
- G1 : M2 perd contre M1P dans cinq blocs sur cinq ; gain médian -0,1215 et moyen -0,9633.
- G2 : asymétrie temporelle relative M2 0,0821, M1P 0,0842. La direction temporelle n'est donc pas spécifique à M2.
- G3 : M2 perd contre M1P sous les quatre conventions d'insolation ; déficit relatif compris entre -0,3099 et -0,3156.
- G4 : sur 12 surrogates de Fourier conservant le spectre, gain observé -0,3146, p unilatérale = 0,9231. Aucun avantage au-delà de la structure spectrale seule.

Verdict consolidé : l'échec de M2 est robuste aux blocs temporels, au sens du temps, à la convention d'insolation, au plancher d'incertitude et à une distribution nulle conservant le spectre. Une nouvelle famille climatique doit être formulée avant tout nouveau réglage de M2.
