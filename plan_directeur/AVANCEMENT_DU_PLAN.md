# Avancement du plan directeur

Le plan porte **804 items numérotés** répartis en 58 groupes de travail. Ce
document dit lesquels sont exécutés, lesquels sont bloqués et pourquoi.

Il ne fixe aucun statut : `ETAT_DES_PREUVES.md` et
`REGISTRE_HYPOTHESES.csv` s'en chargent. **Cocher un item ne valide rien** —
sur 35 hypothèses enregistrées, les résultats réfutés et non concluants restent explicitement conservés.

## Niveau 1 du plan — immédiat, faible coût, forte valeur

| Item | État | Où |
|---|---|---|
| 1. registre complet des hypothèses | **fait**, 35 hypothèses | `REGISTRE_HYPOTHESES.csv` |
| 2. base de données des 40 transitions | **fait** comme schéma, 8 champs sur 23 remplis | `01_branche_matiere/base_transitions/` |
| 3. tests synthétiques du socle | **fait**, 4 volets | `00_socle/banc_synthetique/` |
| 4. régénération et audit de la carte | **partiel** — audit fait, figures bloquées | `…/carte_relationnelle/ANALYSE_GRAPHE.md` |
| 5. benchmark de valeur ajoutée | **fait** pour la carte et la couche mémoire | `ANALYSE_GRAPHE.md`, `RAPPORT_WP_C4.md` |
| 6. réplication du résultat négatif climatique | **fait**, 9 tests réels | `…/results_stress/tests_reels/` |
| 7. réparation du protocole prospectif | **fait**, 10 items sur 10 | `…/prospectif_c2/RAPPORT_WP_C2.md` |
| 8. extension astronomique par ablations | **fait**, 25 calculs, 13 critères sur 15 | `02_branche_systeme_solaire/couche_astronomique/` |
| 9. méta-analyse des filtrages planétaires | **bloqué** — données absentes | — |
| 10. préparation confirmatoire antibiotique | **partiel** — benchmark exploratoire, aucun jeu final intact | `plateforme/campagne_maximale_reelle/resultats_consolides/benchmark_antibiotic_history.json` |
| 11. durcissement du schéma de lignées | **fait** | `03_.../programme_prebiotique/` |
| 12. préenregistrement public | **partiel**, deux protocoles scellés | `PREENREGISTREMENT_PROSPECTIF.md`, `PROTOCOLE_C2.json` |

**8 faits, 3 partiels, 1 bloqué.**

## Groupes de travail ouverts

| Groupe | Items | Traités | Résultat principal |
|---|---:|---:|---|
| Étape 0 | 10 | 8 | environnement enregistré ; `rebound` installé et campagne astronomique exécutée |
| Étape 1 | — | **fait** | 35 hypothèses, 18 champs |
| Étape 2, grille universelle | 30 | **30/59 cases** | `GRILLE_ETAPE_2.md` |
| S1.2 à S1.5 | 42 | ~12 | banc synthétique, 4 volets sur 4 |
| WP-S2 | 20 | 14 | **item 14 positif** : 10 cas sur 600 |
| WP-S3 | 20 | 9 | carte non distinguable d'un graphe nul |
| WP-M1 | 15 | 15 | base construite, complétude mesurée |
| WP-M5 | 10 | 2 | graphe pire que la chronologie |
| WP-C1 | 10 | 6 | verdict négatif répliqué |
| WP-C2 | 10 | **10** | non concluant, contradiction dans le protocole |
| WP-C3 | 22 | en cours | 7 mécanismes sur 16 |
| WP-C4 | 15 | 7 | **`persistance` à 0 paramètre bat M2** |
| WP-C6 | 15 | 10 | **M2 non identifiable** |
| WP-C7 | 10 | 5 | le signal manquant est la bande de 100 ka |
| WP-T2 | 10 | 5 | 8 notions sur 15 traversent 2 branches |
| WP-T4 | 6 | 3 | 3,00 concepts par résultat positif |
| WP-V1 | 10 | 4 | validateur de lignées vérifié |

## Les huit résultats qui comptent

1. **`persistance`, zéro paramètre, se classe 2e sur 11 familles** et bat M2 de
   16 %. Neuf modèles sur onze tiennent dans un intervalle de 5 %.
2. **Les paramètres de M2 ne sont pas identifiables** : dispersion relative de
   1,233 entre graines, contre 0,003 pour M0.
3. **La bande de 100 ka est entièrement dans le résidu** des quatre modèles,
   à 38–41 %. C'est là que se trouve le mécanisme manquant.
4. **La bande de 405 ka n'est pas résolvable** sur la fenêtre de prédiction :
   1 point de fréquence sur 1200 ka.
5. **La carte relationnelle ne se distingue pas d'un graphe nul** à degrés et
   ordre conservés, et son prédicteur structurel est au niveau du hasard.
6. **La chaîne ORI-C ne produit aucune mesure** dans aucune branche.
7. **L'item 14 du WP-S2 a un domaine de validité** : réduire une perte diminue
   la persistance dans 10 configurations sur 600, par libération compétitive et
   par retard.
8. **Le WP-C2 est contradictoire dans ses propres termes** : l'item 5 impose
   une calibration au point de référence, ce qui rend l'appariement des items 3
   et 4 impossible quand référence et points testés sont dans des régimes
   différents.

## Résultats ajoutés par les workflows d’analyse

1. **Astronomie** : 25 calculs, 13 critères sur 15, accord avec JPL et La2010, et effets des interventions sur Jupiter et Saturne supérieurs de plusieurs millions de fois à la dispersion du témoin. Le résultat reste une causalité dans le modèle réduit.
2. **Azote terrestre** : présence, accessibilité et mobilisabilité sont calculées dans un modèle de premier ordre. L'opérativité reste sans donnée.
3. **GISTEMP** : le modèle multi-mémoires améliore l'intégrale simple, mais perd contre le témoin de complexité égale. La structure proposée n'est pas validée.
4. **Vallée des rayons exoplanétaires** : le critère préenregistré échoue nettement dans cette implémentation.
5. **Antibiotiques** : le modèle historique présente un faible avantage moyen, mais son intervalle de confiance traverse zéro. Le résultat est exploratoire et non concluant.
6. **Proxy `Pacc`** : toutes les classes atteignent toutes les classes futures, soit `Pacc = 1`. L'estimateur est saturé et ne mesure pas une accessibilité causale.
7. **Campagne réelle consolidée** : 211 réussites techniques, 440 blocages et 32 non-exécutions, avec zéro soutien confirmatoire à ORI-C.
8. **Robustesse de la branche matière** : la projection paire à paire atteint 53 nœuds, mais la fermeture hypergraphique stricte n'en atteint que 46. Sur cet ensemble accessible, 34 hyperarêtes sur 53 sont critiques. Le recouvrement du carbone résiste aux retraits unitaires, celui de l'azote dépend d'une mesure publiée, l'hydrogène reste non évaluable et le désaccord du soufre est robuste.
9. **Séparation astronomique** : le plus petit effet des six interventions reste 4 964 fois supérieur au plus grand écart numérique sélectionné. Les perturbations appariées montrent une réponse souvent asymétrique et parfois non antisymétrique.
10. **Verrou des 100 ka** : selon le modèle, environ 98,6 à 99,3 % de la part observée de la bande de 100 ka reste descriptivement inexpliquée sur la fenêtre de prédiction.
11. **Robustesse du benchmark longitudinal amikacine** : ce bloc est distinct de D’Onofrio. Le modèle historique gagne légèrement en validation groupée, mais la version sans pente fait mieux et le test de dernière transition inverse le classement. Le gain face au témoin n’est pas significatif dans le test apparié exact, p = 0,2266. Retirer la pente améliore le résultat, p = 0,0078, et la distribution nulle à 1 000 permutations donne p = 0,0649. **Ces trois p-values ne portent pas sur D’Onofrio**, dont le benchmark séparé conserve RMSE 1,1309 contre 0,8042 et permutation p = 0,004975, tout en restant rétrospectif et non répliqué indépendamment.
12. **ARN catalytique** : la branche 71-89 montre une hausse de diversité du sous-ensemble suivi, p exact = 0,0117. Les données décrivent une composition au fil des cycles, pas une filiation prébiotique.
13. **Campagne maximale trois branches** : 21 tests de régression verrouillent les calculs, les ablations et leurs limites dans `plan_directeur/campagne_maximale_trois_branches/`.

## Défauts de mes propres bancs, trouvés et corrigés

Tous sont documentés avec leur première exécution conservée.

| Banc | Défaut | Effet |
|---|---|---|
| Banc synthétique S1.5 | estimateur saturé | **réussissait en ne testant rien** |
| Banc synthétique S1.2 | pas de bruit d'observation | 0 % des cas « état » reconnus |
| Banc synthétique S1.3 | grille de constantes fixe | identification à 0,000 |
| Analyse de graphe | nul détruisant l'acyclicité | `p = 0,0005` sans signification |
| WP-S2 | bruit coloré 35× trop fort | extinction même à perte nulle |
| WP-S2 | critère de non-monotonie absolu | retenait du bruit d'intégration |
| WP-C3 | rétroaction accumulée au lieu d'un taux | 4 mécanismes sur 7 divergeaient |
| G2 | masque confondant segment et direction | **changeait la conclusion** |

## Ce qui reste, par cause de blocage

**Données absentes du dossier** — WP-M2 à M4, WP-P1 à P6, WP-C1.4-6, WP-C5,
WP-CL1 à CL4, WP-B2. Environ **190 items**.

**Environnement** — le verrou `rebound` est levé. Les calculs astronomiques sont exécutables sur GitHub Actions. Les blocages résiduels concernent désormais les données, le coût des campagnes longues ou des dépendances propres à d’autres WP et doivent être recomptés séparément.

**Humains ou laboratoires** — WP-S3.5-7, WP-V2 à V6, WP-R1 à R6, WP-B1, WP-B3,
WP-T5, Niveaux 3 et 4. Environ **250 items**.

**Exécutable et non fait** — WP-C3 reste partiellement en cours, WP-T1 et
WP-T3 demandent encore des extensions qui ne sont pas couvertes par la campagne
maximale actuelle, et S1.1 reste ouvert. Le précédent ordre de grandeur de 70
items doit être recompté après intégration des nouveaux contrôles, plutôt que
conservé artificiellement.

## Sur le seuil scientifique du §XIV

Le plan fixe douze conditions. État :

| Condition | État |
|---|---|
| 1. identifiant et statut pour chaque affirmation majeure | **fait**, 35 |
| 2. base de données de la branche matière | **fait** comme schéma, à remplir |
| 3. une prédiction propre réussissant hors échantillon par branche | **aucune** |
| 4. chaque réussite bat un témoin apparié | sans objet, aucune réussite |
| 5. chaque mécanisme soutenu par une ablation | **fait** pour CHM, MEM et les interventions astronomiques |
| 6. dépendance au chemin à conditions finales vérifiées | **fait** |
| 7. persistance au-delà des constantes de temps | **fait** |
| 8. `D`, `H`, `L` publiés séparément | **fait** dans le banc synthétique |
| 9. `Pacc` mesuré dans un système réel par branche | **non** — plusieurs mesures locales existent, mais aucune définition causale empirique qualifiée n’est instanciée dans les trois branches : le proxy observationnel historique est saturé, le support vésiculaire est rétrospectif et EXO-DOM-01 reste un modèle |
| 10. deux résultats reproduits par des équipes indépendantes | **non** |
| 11. un résultat traversant deux branches sans redéfinition | **non** |
| 12. résultats négatifs visibles et versionnés | **fait** |

**Sept conditions sur douze sont remplies.** Les cinq manquantes — 3, 4, 9, 10,
11 — sont précisément celles qui exigent un résultat **positif hors échantillon**, un témoin apparié battu, une mesure causale de `Pacc` sur système réel, une réplication externe et un transfert sans redéfinition. L’état est désormais aussi généré par `campagne_centrale_2026_08_11/evaluer_seuil_xiv.py`; cette porte machine doit rester fail-closed.

Le programme n'a franchi ni le premier seuil ni, a fortiori, le seuil fort.
## Phase v0.9.4 - calibrage de la branche matière

- [x] geler le graphe v0.9.3 par empreintes
- [x] séparer documentation et criticité structurelle
- [x] exécuter 53 ablations unitaires
- [x] exécuter 31 ablations de sources
- [x] tester cinq seuils documentaires
- [x] exécuter 4 000 tirages de stress paramétrique déterministes
- [x] identifier le noyau stable, les nœuds sensibles et le verrou canonique
- [x] transférer le schéma à deux trajectoires stellaires MESA
- [ ] obtenir une évaluation indépendante de la nécessité et de la suffisance des relations prioritaires
- [ ] tester une intervention ou un contrefactuel naturel sur `H011` et sur le cycle `H030-H031-H052-H053`

## Campagne de recherche suivante

| Axe | État | Résultat ou verrou |
|---|---|---|
| `H011` sous variation de turbulence | **exécuté** | seuil critique monotone, rapport 3,33 dans les simulations publiées ; intervention naturelle non mesurée |
| cycle `H030-H031-H052-H053` | **exécuté** | quatre segments documentés, aucune trajectoire quantitative unique |
| `Pacc` astronomique interventionnel | **exécuté** | 6 interventions sur 6 dépassent l'enveloppe sur au moins deux métriques ; 17 dimensions sur 18 dépassent l'enveloppe |
| `WP-C2b` | **protocole gelé** | quatre points non saturés, trois classes de régime, huit graines de validation |
| spéléothèmes NOAA | **acquisition automatisée** | audit de chronologie et de proxy ; portée limitée à 0-22 ka |
| lignées de vésicules | **acquisition et analyse automatisées** | trois répétitions par régime, filiation reconstruite par cartes donneur-receveur |
| histoire antibiotique 2026 | **acquisition et analyse automatisées** | souche exclue de l'apprentissage, témoin d'état et histoire permutée de même complexité |

Les trois derniers blocs restent en attente lors d'une exécution sans accès aux jeux externes. Le workflow `Recherche suivante ORI-C` télécharge les sources, écrit leur provenance et exécute les analyses complètes.

## Mise à jour exécutable — Pacc causal et OSF (13 août 2026)

- **Test de sanité Pacc : fait.** `PACC-INT-CHALLENGE-V1` restitue sur `EXO-DOM-01` `0,91 -> 0,87`, `Delta=-0,04`, sham nul. Le résultat est enregistré dans `do_m_trace/resultats/VALIDATION_PACC_INTERVENTIONNEL_V1.json` et reste un contrôle d'outil au niveau modèle.
- **Vésicules : protocole causal prospectif scientifiquement gelé, non exécuté.** `VES-PACC-INT-01` fixe `do(m)` à 11 passages sur membrane 100 nm, sham 5 µm, 48 populations parentales indépendantes, 12 défis, 4 dimensions, les seuils `[0,10, 0,10, 0,05, 0,10]`, SESOI `0,08` et l’analyse confirmatoire. Les 11 760 couples déjà vus restent calibration/conception. Aucune nouvelle donnée avant préenregistrement public des SHA-256.
- **Prédictions prospectives : paquets OSF prêts.** Les quatre fiches restent `package_ready_external_account_required` jusqu'à dépôt public. L'audit §XIV exige maintenant une registration publique antérieure aux données pour compter une réussite prospective.
- **Benchmark Santos-Lopez 2021 : exécuté, rétrospectif.** RMSE état seul `0,937482`, état + histoire `0,732492`, gain `21,866 %`, bootstrap 95 % `[7,235 % ; 33,967 %]`, permutation `p≈0,00020`. La règle numérique de référence est satisfaite, mais la spécification propre au jeu a été fixée après ouverture : le résultat ne compte ni pour §XIV-3 ni pour §XIV-10.
- **Matière : `MAG-PAIR-001` retenu pour l’exécution physique.** Le protocole reste un plan, sans mesure confirmatoire. Le laboratoire, le palier AF, le champ test, la randomisation, l’aveugle et l’analyse doivent être gelés avant la première mesure.
- **Cosmos et paléo : portes inchangées.** `PRED-COSMOS-NCCC-001` attend un nouveau cohort météoritique indépendant. `PRED-PALEO-HISTORY-02` reste fermé tant que les incertitudes chronologiques ponctuelles et le vrai contrôle négatif manquants ne sont pas acquis.
- **Seuil scientifique : inchangé.** **7/12**, verrous `3, 4, 9, 10, 11`.
- **VES-PACC-INT-01 — chaîne laboratoire → analyse prête.** Le schéma `SCHEMA_ENTREE_VES_PACC_INT_01.json` et `preparer_ves_pacc_int_01.py` imposent la structure parent/bras/défi, calculent la normalisation vers les cubes `n×12×4`, dérivent les contrôles de fidélité et d’appariement depuis le protocole gelé et restent bloqués pour toute donnée réelle tant que l’enregistrement public n’est pas attesté. Aucun seuil scientifique ni verdict §XIV n’est modifié.


## Mise à jour d'industrialisation et de fermeture — 14 août 2026

- **Roadmap courte installée.** `ROADMAP.md` limite les priorités actives à `VES-PACC-INT-01`, `H052/HC01`, `PRED-VIVANT-HISTOIRE-001` et `MAG-PAIR-001`.
- **H052 audité sans promotion.** `AUDIT_H052_2026-08-14.md/.json` conserve la fermeture canonique à **46/53** et précise la preuve discriminante encore nécessaire pour justifier `HC01`.
- **Démonstration reproductible renforcée.** `scripts/demo_minimale_html.py` transforme la sortie de `demo_minimale.py` en rapport HTML autonome sans changer l'analyse d'autorité.
- **Contrôle négatif industrialisé.** `controle_negatif_reel_surrogats.py` accepte un chemin `--sortie` afin que la CI rejoue le contrôle sans modifier l'artefact versionné.
- **Exploration GitHub Pages installée.** `scripts/construire_exploration_site.py` dérive une vue interactive déterministe de la généalogie cosmique, des mesures NC/CC, des scénarios N-corps pré-calculés et de l'état §XIV. Un modèle jouet séparé illustre le patron `Histoire → Architecture → Possibles` sans compter comme preuve.
- **Notebook de démonstration ajouté.** `notebooks/ORI-C_demo_colab.ipynb` rejoue la démonstration minimale depuis un clonage propre avec Git LFS.
- **Seuil scientifique inchangé.** §XIV reste **7/12**, verrous `3, 4, 9, 10, 11`.

### 14 août 2026 — noyau externe, portes de données et préparation MAG

Le dépôt dispose désormais d’un noyau externe de 16 résultats (`preuves/CORE_RESULTS.json` / `CORE_RESULTS.md`) validé contre `preuves/PREUVES.json`, d’un état machine des quatre verrous actifs (`plan_directeur/VERROUS_ACTIFS.json`) et d’un registre fail-closed des jeux biologiques déjà vus afin qu’aucun benchmark rétrospectif ne puisse être réutilisé comme test prospectif strict.

`MAG-PAIR-001` possède maintenant un schéma de tables brutes, un préparateur, un script d’analyse et une gate d’exécution. La gate reste volontairement fermée : neuf paramètres de laboratoire sont encore `null` et aucun fichier de mesure prospectif n’est présent. Le script d’analyse ne s’ouvre qu’après gel de ces paramètres et attestation d’un enregistrement public préalable.

Le verrou H052 reste à 46/53. Lawal et al. 2026 (`doi:10.1029/2025GL120883`) renforce toutefois la composante expérimentale en montrant une initiation/propagation de microfissures induite par serpentinisation dans une dunite riche en olivine. Le manque est désormais plus étroit : raccord exact à la croûte primitive `N051` et à l’auto-initiation de la circulation `H052`.
