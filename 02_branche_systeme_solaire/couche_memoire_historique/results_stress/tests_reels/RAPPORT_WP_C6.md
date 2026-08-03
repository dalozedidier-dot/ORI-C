# Critères discriminants de la couche mémoire — WP-C6

Script : `stress/i_criteres_discriminants.py`. Sortie :
`i_criteres_discriminants.json`, `i_criteres_discriminants.csv`.

Le verdict de la couche mémoire reposait sur **une** métrique : la RMSE hors
échantillon. Le WP-C6 en demande quinze. Sept sont exécutables sur les données
présentes et n'avaient jamais été calculées.

Calibration 2600–1200 ka, prédiction 1200–0 ka.

---

## C6.2 à C6.4 — vraisemblance, calibration, corrélation, phase

| Modèle | RMSE | Corrélation | log-vraisemblance | Couverture à 90 % | Décalage de phase |
|---|---:|---:|---:|---:|---:|
| M0 | 2,094 | +0,086 | −32,5 | 0,728 | **+82 ka** |
| M1 | 2,118 | +0,086 | −32,5 | 0,724 | **+81 ka** |
| M2 | 2,042 | **+0,260** | −32,8 | 0,729 | **+82 ka** |
| **M1P** | **1,553** | +0,175 | −33,9 | **0,885** | **+81 ka** |

Quatre lectures, dont deux inattendues.

**La calibration sépare mieux que la RMSE.** M1P couvre 88,5 % des
observations dans son intervalle nominal à 90 % — presque exact. Les trois
autres plafonnent à 72–73 %, c'est-à-dire qu'ils **sous-estiment leur propre
incertitude d'environ 18 points**. Un modèle mal calibré donne des intervalles
trop étroits, ce qui est plus grave qu'une RMSE médiocre pour un usage
prédictif.

**La log-vraisemblance renverse le classement.** M1P a la meilleure RMSE et la
**pire** log-vraisemblance (−33,9 contre −32,5). Ce n'est pas une
contradiction : la vraisemblance est pénalisée par la taille efficace, et les
résidus de M1P sont plus autocorrélés. Les deux métriques mesurent des choses
différentes, et le plan avait raison de les demander séparément.

**Les quatre modèles ont le même décalage de phase, +81 à +82 ka.** Aucun ne
retarde moins que les autres. Un biais partagé par toute la famille n'est pas
une propriété de M2 : c'est une propriété de la structure commune, ou du
forçage employé. C'est le genre de chose qu'une comparaison interne à la
famille ne peut pas révéler.

**M2 garde le meilleur coefficient de corrélation** (+0,260 contre +0,175 pour
M1P), tout en ayant une RMSE nettement moins bonne. C'est la même dissociation
forme/amplitude que T2 et T4 avaient laissée entrevoir.

---

## C6.5 — Trois bandes spectrales, et une bande non résolvable

### La bande de 405 ka n'est pas mesurable ici

| Fenêtre | Points de fréquence dans 360–450 ka | Résolue |
|---|---:|---|
| 1200 ka, prédiction | **1** | non |
| 2600 ka, série complète | **2** | non |
| 5320 ka, archive entière | 3 | oui, marginalement |

Le plan demande cette bande au WP-C6.5 et au WP-A5.4. **La réponse est que la
fenêtre de prédiction ne la porte pas.** Un pic à 405 ka calculé sur 1200 ka
est un artefact de résolution, pas une mesure. Seule l'archive complète peut
l'accueillir, et encore de justesse.

Le script le signale désormais explicitement plutôt que de renvoyer une
puissance qui n'en est pas une.

### Ce que portent les bandes résolues

Part de la puissance totale, fenêtre de prédiction :

| Série | 41 ka | 100 ka |
|---|---:|---:|
| **LR04** | 0,151 | **0,394** |
| M0 | 0,244 | 0,004 |
| M1 | 0,275 | 0,006 |
| **M2** | **0,602** | 0,003 |
| M1P | 0,257 | 0,006 |

**Aucun des quatre modèles ne produit la bande de 100 ka sur cette fenêtre.**
L'observation y met 39 % de sa puissance ; les modèles, entre 0,3 et 0,6 %.

Et M2 est le plus déséquilibré des quatre : 60 % de sa puissance dans la bande
de 41 ka, quatre fois la part observée.

**Ceci nuance T4.** En T4, calibré sur 5320–2600 ka, M2 produisait un rapport
100/41 supérieur à 1. Ici, calibré sur 2600–1200 ka, il est massivement
dominé par l'obliquité. La capacité de M2 à produire la signature de 100 ka
**dépend de la fenêtre de calibration**, ce qui est exactement le motif d'arrêt
n° 7 du plan : « la prédiction dépend d'un choix de fenêtre non préenregistré ».

---

## C6.6 — Chronologie des terminaisons

Huit terminaisons les plus fortes, appariement à 20 ka près.

| Modèle | Appariées | Écart médian |
|---|---:|---:|
| M0 | 3 / 8 | 58,5 ka |
| M1 | 2 / 8 | 81,5 ka |
| **M2** | **4 / 8** | **21,5 ka** |
| M1P | 3 / 8 | 52,5 ka |

**C'est le seul critère sur lequel M2 arrive premier.** Il apparie la moitié
des terminaisons et son écart médian est deux à quatre fois plus faible que
celui des autres.

À tempérer : 4 sur 8 reste un échec en valeur absolue, l'écart médian de
21,5 ka dépasse la tolérance de 20 ka, et aucun intervalle de confiance n'a été
calculé sur ce comptage.

---

## C6.7 et C6.8 — Stabilité et identifiabilité

### Dérive des paramètres entre quatre sous-fenêtres de 350 ka

| Modèle | Dérive relative max | Stable (< 0,25) |
|---|---:|---|
| M0 | 1,711 | **non** |
| M1 | 0,997 | **non** |
| M2 | 1,000 | **non** |
| M1P | 1,308 | **non** |

**Aucun des quatre modèles n'a de paramètres stables.** Réajustés sur des
sous-fenêtres successives, ils varient de 100 % à 171 %. La forme fonctionnelle
ne décrit pas un mécanisme constant sur 2,6 Ma — pour aucun des quatre.

### Dispersion entre graines d'optimisation

| Modèle | Dispersion relative max | Identifiable (< 0,10) |
|---|---:|---|
| M0 | 0,003 | **oui** |
| M1 | 0,001 | **oui** |
| **M2** | **1,233** | **non** |
| **M1P** | **1,680** | **non** |

**Voici le résultat le plus décisif de la campagne.** Quatre graines
d'optimisation différentes donnent à M2 des jeux de paramètres qui diffèrent de
plus de 100 %, pour des qualités d'ajustement voisines. Les paramètres de M2
**ne sont pas identifiables** sur ces données.

M0 et M1, avec 3 et 6 paramètres, le sont parfaitement — dispersion de 0,1 à
0,3 %. La non-identifiabilité apparaît exactement avec le huitième paramètre et
le second état lent, et elle frappe **aussi bien M2 que son témoin apparié
M1P**. C'est donc une propriété de la structure à deux états lents, pas du
mécanisme ORI-C en particulier.

---

## Conséquence au regard des règles d'arrêt du plan

Le §XIII du plan directeur énumère huit motifs d'arrêt ou de reformulation.
**Trois sont atteints** par la forme actuelle de M2 :

| Motif | Constat |
|---|---|
| **2. son avantage disparaît contre un témoin de complexité égale** | atteint : 0/5 critères, gain −0,316 ; confirmé par G1 (0 bloc sur 5) et G3 (0 convention sur 4) |
| **3. ses paramètres restent non identifiables malgré des données suffisantes** | **atteint** : dispersion relative de 1,233 entre graines, contre 0,003 pour M0 |
| **7. la prédiction dépend d'un choix de fenêtre non préenregistré** | atteint : la production de la bande de 100 ka bascule selon la fenêtre de calibration |

Le §XIII prévoit qu'une piste **reste ouverte** lorsque l'échec révèle un
défaut précis de protocole avant consultation du résultat confirmatoire. Ce
n'est pas le cas ici : les trois motifs portent sur le modèle, pas sur le
protocole.

**La forme actuelle de M2 doit être abandonnée ou reformulée**, et le WP-C7
indique où chercher : la dissociation forme/amplitude, le décalage de phase
commun de 82 ka, et la chronologie des terminaisons — le seul point où M2
devance les trois autres.

## Ce que ce rapport ne fait pas

Il ne teste pas les items C6.10 à C6.12 — hystérésis, pertes de régimes,
valeur de `Pacc` — qui demandent des interventions sur le modèle et non des
métriques sur ses sorties. Ni le C6.14, qui demande un second jeu de proxys
absent du dossier.
