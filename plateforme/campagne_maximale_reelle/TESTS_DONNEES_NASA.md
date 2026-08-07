# Deux affirmations du socle confrontées à des observations NASA

Les données de ce répertoire — GISTEMP v4 et NASA Exoplanet Archive — rendent
testables deux affirmations qui ne l'étaient pas, faute d'observations.

Aucune donnée n'est simulée. Cibles et entrées sont des valeurs mesurées.

---

## 1. Mémoire distribuée du climat — WP-CL1, sur GISTEMP

**Statut courant : analyse historique archivée.** Les résultats ci-dessous
proviennent de l'ancienne table GISTEMP zonale contenant `Glob`, `NHem`,
`SHem` et `64N-90N`. La table canonique actuelle
`data/modern_climate_timeseries.csv` contient 7 193 points globaux issus de
GISTEMP et HadCRUT5 et ne contient plus ces bandes zonales. Le script
`memoire_distribuee_gistemp.py` vérifie désormais ce contrat et retourne
`blocked` sans exécuter CL1 lorsque les régions requises sont absentes.

Aucune variable globale actuelle n'est requalifiée en compartiment zonal.
Les nombres ci-dessous sont conservés pour traçabilité historique et ne
décrivent pas une réexécution de l'état courant du dépôt.

Le §13.1 du `CODEBOOK.md` affirme deux choses distinctes. Les données
permettent de les séparer, et elles ne reçoivent pas le même verdict.

Calibration 1880-1970, prédiction 1971-2025, 146 années observées,
cible `Glob`, compartiments `NHem`, `SHem` et `64N-90N`.

### Vérifié — les compartiments ont des constantes de temps différentes

| Compartiment | Nature | τ ajusté |
|---|---|---:|
| Hémisphère nord | continental | **0,50 an** |
| **Hémisphère sud** | **océanique** | **27,78 ans** |
| 64°N–90°N | Arctique | 1,32 an |

**τ(SH) / τ(NH) = 56.** La prédiction est vérifiée dans le bon sens :
l'hémisphère océanique retient, l'hémisphère continental suit le forçage
presque instantanément. C'est le premier appui quantitatif du §13.1 sur des
mesures réelles.

### Réfuté — la structure de compartiments n'apporte rien

| Modèle | Paramètres | RMSE hors échantillon |
|---|---:|---:|
| Intégrale cumulée unique | 2 | 0,4563 |
| **Témoin de complexité égale** | 7 | **0,0997** |
| Multi-mémoires par compartiment | 7 | 0,1252 |

| Comparaison | Gain |
|---|---:|
| Multi-mémoires contre intégrale unique | **+0,726** |
| Multi-mémoires contre témoin apparié | **−0,255** |

Le §13.1 a raison sur un point : une intégrale temporelle unique ne représente
pas la mémoire climatique — elle est **trois fois pire**.

Mais le témoin apparié — mêmes sept paramètres, mêmes constantes de temps
ajustées, retards appliqués à la **moyenne** des régions au lieu de
compartiments distincts — fait **20 % mieux** que le modèle à compartiments.

Le gain de 72,6 % vient donc de la **multiplicité des échelles de temps**, pas
de leur **attachement à des compartiments spatiaux**. C'est le motif exact qui
avait réfuté M2 sur LR04, retrouvé sur un autre domaine, d'autres données et
un autre siècle : le mécanisme ORI-C perd contre un témoin apparié alors même
que sa famille bat le modèle naïf.

---

## 2. Inscription historique dans une population — vallée des rayons

**Verdict : échec du test tel que spécifié.**

La branche 2 affirme que l'histoire laisse une trace mesurable dans l'état
présent. La vallée des rayons — déficit de planètes vers 1,8 rayon terrestre,
attribué à la perte atmosphérique — en serait un cas observable hors du
Système solaire.

3 298 planètes retenues entre 1 et 4 rayons terrestres, sur 6 333 au catalogue.

| Critère, fixé avant exécution | Observé | Seuil | Verdict |
|---|---:|---:|---|
| Creux dans la fenêtre 1,5–2,2 R⊕ | position 1,502, profondeur **−0,0024** | creux réel | **échec** |
| Quantile contre 2 000 tirages nuls | **0,0005** | ≥ 0,95 | **échec** |
| Écart de position entre méthodes | 0,000 | ≤ 0,4 | sans objet |

La profondeur négative signifie qu'**il n'y a pas de minimum intérieur** : la
densité est monotone sur la fenêtre, et la position rapportée est le bord.

**Trois causes possibles, et je n'en privilégie aucune sans le vérifier.** La
largeur de lissage de 0,05 en log₁₀ peut effacer une vallée étroite. La table
`PS` par défaut mélange des rayons d'incertitudes très inégales, alors que la
vallée publiée s'obtient sur des échantillons à rayons stellaires précis. Et
une seule méthode de découverte franchit le seuil d'effectif — le transit,
3 271 planètes — ce qui prive le témoin de contraste.

**Les paramètres n'ont pas été retouchés pour faire passer le test.** Le
refaire suppose une nouvelle préinscription, avec un échantillon de qualité
déclarée et une largeur de lissage justifiée avant exécution.

---

## Un défaut de chaîne à corriger en amont

`data/prebiotic_lineages_raw.csv` — huit lignes portant le marqueur
`GABARIT_SYNTHETIQUE` — est présent dans ce paquet comme dans les deux
précédents. C'est la **troisième fois** qu'il est retiré, alors que le
`BILAN.md` de la campagne annonce « aucune donnée synthétique n'est utilisée ».

Il doit être supprimé dans le générateur qui produit ces paquets, sinon il
reviendra au suivant.

## Fidélité des données, vérifiée

| Table | Contrôle |
|---|---|
| GISTEMP zonal | **146/146** identiques au brut pour `Glob`, `NHem`, `SHem`, `24N-90N`, `64N-90N`, `90S-64S` |
| Exoplanètes | **6 333/6 333**, 16 colonnes |
| Ensemble climatique | 338 400 lignes issues des NetCDF |

La région `global` ne concorde avec `Glob` qu'à 4/146 : ce sont deux sources
distinctes — `GLB.Ts+dSST.csv` mensuel et `ZonAnn.Ts+dSST.csv` annuel — toutes
deux réelles. Elles ne doivent pas être mélangées dans une même analyse.
