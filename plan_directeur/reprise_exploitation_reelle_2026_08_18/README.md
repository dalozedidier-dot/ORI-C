# ORI-C — reprise de l’exploitation réelle après D’Onofrio

Date de consolidation : 18 août 2026

Ce package reprend exactement le travail qui avait été laissé en suspens après la nouvelle réanalyse D’Onofrio. Il pousse les **vésicules** et les **archives isotopiques/chronométriques** avec la même règle : données réelles, effets positifs et nuls conservés, analyses rétrospectives classées comme telles, aucun crédit §XIV ajouté rétroactivement.

## 1. D’Onofrio

La nouvelle réanalyse est conservée dans `resultats/DONOFRIO_REANALYSE_RECUPEREE.json`. Elle n’est pas recalculée ici car le résultat récupéré provenait de la conversation précédente et le jeu MIC numérique exact utilisé pour cette couche n’est pas inclus comme table autonome dans l’archive récupérée.

Résultat central récupéré : distance intra-histoire 1,248 contre inter-histoires 2,678, persistance carbone↔azote 1,280 contre 2,725, trois antibiotiques avec effet historique fort et **tobramycine comme limite** (R² partiel 0,380, p = 0,0828).

## 2. Vésicules

Entrées réelles : `prebiotic_timecourses.csv` (59 328 mesures) et `prebiotic_lineages.csv`.

### Dynamique temporelle

La réanalyse temporelle versionnée est conservée. Les 15 contrastes FR-vers-contrôle testés sur amplitude de rebond, AUC 2–6 h et pente 2–6 h sont positifs avec p unilatéral ≤ 0,004. Cela confirme une dynamique FR spécifique.

Le contraste historique P_acc d’ablation reste **-0,0375**, IC95 approximatif **[-0,145833 ; 0,0625]**. Il reste négatif et n’est pas requalifié.

### Profondeur historique

Le protocole gelé H-DEPTH-LADDER est reproduit exactement sur 1 044 lignes communes :

- profondeur 0 : RMSE 0,118860
- parent immédiat, profondeur 1 : RMSE 0,116124, gain **+2,302 %**
- profondeur 2 : gain incrémental **-0,955 %**
- profondeur 3 : **-0,495 %**
- profondeur 4 : **-0,201 %**

La profondeur effective au seuil gelé de 2 % est donc **1**. Les ancêtres plus profonds n’ajoutent pas d’information prédictive selon ce test.

### Sélection contre dérive à condition finale identique

Seize fichiers expérimentaux possèdent les deux bras au dernier nombre de générations commun. Sur 20 000 permutations par fichier :

- 7/16 contrastes sont nominaux à p < 0,05
- 6/16 restent sous FDR Benjamini-Hochberg q < 0,05
- FR : 2/6 sous FDR
- FU : 1/3
- UR : **0/3**
- UU : 3/4

L’effet de l’histoire expérimentale existe donc dans certains contextes mais **n’est ni uniforme ni universel**.

## 3. AICC2023 — incertitude chronologique

Les cinq chronologies de carottes sont recalculées depuis l’archive AICC2023 réelle.

La corrélation de Spearman entre âge et incertitude chronologique est forte dans les cinq carottes (rho ≈ 0,848 à 0,975). Le rapport entre la médiane de sigma dans la tranche la plus ancienne disponible et 0–100 ka varie cependant énormément :

- VOSTOK : ×3,47
- EDML : ×20,88
- EDC : ×35,91
- TALDICE : ×104,34
- NGRIP : ×109,61

Il existe donc un élargissement historique net de l’incertitude, mais sans loi universelle commune aux carottes.

La comparaison AICC2023–AICC2012 est conservée comme **diagnostic de révision**, jamais comme vérité terrain. Selon la carotte, 78,5 % à 94,2 % des révisions absolues se trouvent dans 2 sigma AICC2023. Le q95 de |révision|/sigma atteint néanmoins 6,84 pour EDML. Cela montre pourquoi une chronologie nominale unique ne doit pas masquer la largeur réelle de l’archive.

## 4. ^26Al — chronométrie et histoire de réservoir

La demi-vie utilisée reste 0,717 Myr. Les médianes canoniques reconstruites sont :

- angrite : 0,34528
- EC002 : 0,18598
- chondre jeune : 0,08177
- carbonate CM : 0,02305

Les rapports entre médianes successives sont ~1,86, 2,27 et 3,55. Malgré cette décroissance nette, **chaque paire adjacente possède des intervalles propagés à 95 % qui se chevauchent**.

Avec les scénarios déclarés de réservoir canonique, appauvri ×3 et appauvri ×4, le seuil 1 % reste robuste pour les trois premiers événements, tandis que le carbonate CM n’a plus aucun seuil robuste. Le seuil 10 % n’est pas robuste à l’histoire de réservoir.

Le contrôle d’hétérogénéité du dépôt montre qu’autour de 2 Myr, un CAI mesuré est ~37,87 % sous la référence de décroissance canonique, tandis qu’un second possède un déficit minimal ~84,14 %. **Le temps structure la trace, mais il ne suffit pas à déterminer l’inventaire local.**

## 5. Accrétion tardive multitraceur

La table contient 122 159 mesures, 56 614 échantillons, 45 labels `candidate_source`, 29 461 couples échantillon-source avec au moins 2 traceurs et 7 827 avec au moins 4.

Aucune des 122 159 mesures ne possède d’incertitude renseignée. Cette absence interdit toujours une inversion calibrée de mélange tardif.

Une nouvelle mesure descriptive de structuration par `candidate_source` a été calculée séparément pour chaque traceur sur log10(valeur), puis après retrait de la moyenne propre à la compilation. L’eta² conditionnel varie d’environ **0,054 à 0,175**. RE et OS conservent la plus forte structuration, W et MO la plus faible. L’archive est donc structurée, mais de façon **traceur-dépendante**, avec de vrais axes faibles qui ne doivent pas être moyennés hors du résultat.

## Statut scientifique

Aucune de ces analyses ne ferme rétroactivement §XIV. Le score reste **7/12**. Elles améliorent la description des domaines observés, des limites de persistance et des effets de contexte. `PACC-INT-CHALLENGE-V1` reste non exécuté sur les vésicules et aucune intervention `do(m)` n’est créée par ces réanalyses.

## Reproductibilité

Exécuter :

```bash
python scripts/run_all.py
python scripts/verify_package.py
```

Les entrées réelles nécessaires sont incluses dans `data/`. `MANIFEST.sha256` permet de contrôler l’intégrité du package.
