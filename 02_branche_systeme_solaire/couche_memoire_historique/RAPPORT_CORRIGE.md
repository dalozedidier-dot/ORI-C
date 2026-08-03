# Branche paléoclimatique et exoplanétaire d’ORI-C — protocole corrigé et résultats

Didier Daloze | ORI-C
Version corrigée du 31 juillet 2026

---

## 0. Objet et portée

Ce document corrige la branche empirique du cadre ORI-C : le test de la
transition du Pléistocène moyen sur LR04 et le test exoplanétaire à chemins
contrôlés. Il remplace `REPORT.md` dans son rôle de conclusion et s’appuie sur
`STRESS_REPORT.md` pour le détail chiffré.

**Ce document ne touche pas à la couche astronomique.** Les vingt-cinq calculs
N-corps, l’accord avec JPL Horizons DE441 et La2010, le spectre multitaper sur
20 Ma et les six interventions architecturales restent tels quels. Rien dans ce
qui suit ne les remet en cause, et rien dans ce qui suit ne s’en autorise.

Ce qui est corrigé est ce que la synthèse ORI-C appelait « l’étape décisive
ouverte » : la démonstration qu’un modèle dépendant de l’histoire surpasse,
hors échantillon, un modèle classique soumis aux mêmes contraintes.

---

## 1. Les cinq défauts du protocole initial

La première version du paquet concluait à un verdict MPT de 3 réussites sur 5
et à une réussite structurelle du test exoplanétaire. Ces deux résultats
reposaient sur cinq décisions de protocole qui les rendent non concluants.

| # | Défaut | Pourquoi il invalide la conclusion | Correction appliquée |
|---|---|---|---|
| 1 | M2 (9 paramètres nominaux) n’était comparé qu’à M1 (6 paramètres) | Un avantage peut venir des degrés de liberté supplémentaires, pas d’une mémoire | Ajout de M1P, témoin à complexité égale sans mémoire d’état |
| 2 | BIC calculé sur 1 200 points supposés indépendants | Les résidus ont ρ₁ = 0,971 : la pénalité de complexité devient négligeable | BIC sur taille d’échantillon efficace (n_eff ≈ 18) |
| 3 | Quatre paramètres de M2 sur une borne à l’optimum | La boîte, non les données, fixait une partie de la solution | Bornes élargies d’au moins un ordre de grandeur |
| 4 | Palier final exoplanétaire de 10 Ma | Plus court que les mémoires de 8 Ma et 60 Ma qu’il devait mesurer | Critère de persistance sur palier long |
| 5 | Une troisième symétrie exacte subsistait dans M2 | M2 n’avait que 8 degrés de liberté sur 9, et **le test d’ablation carbone était indéterminé** | Décalage de l’état lent fixé à zéro par définition |

Le défaut 1 est le plus lourd. C’est aussi celui que la synthèse ORI-C
inscrivait dans sa propre condition de réfutation. Le défaut 5, découvert en
cours de campagne, est décrit en §3.6 : il invalidait le seul critère que le
protocole initial réussissait de façon non ambiguë.

La synthèse ORI-C écrivait : « ORI-C gagnerait un appui spécifique seulement si
M2 améliore de manière stable les prédictions hors échantillon **face à M1**,
malgré la pénalité liée à ses paramètres supplémentaires. » Formuler la pénalité
comme un correctif statistique, alors que le témoin lui-même est moins complexe,
ne suffit pas. Un témoin de complexité égale est nécessaire.

### Le témoin manquant, M1P

M1P reprend M1 et lui ajoute un état lent de structure strictement identique à
celui de M2 : un gain et une constante de temps. Il possède donc exactement le
même nombre de paramètres que M2 et la même seconde échelle de temps.

Une seule chose diffère.

- Dans **M2**, l’état lent suit le **volume de glace passé**. C’est une
  inscription de la réponse du système : la mémoire au sens d’ORI-C.
- Dans **M1P**, l’état lent suit le **forçage astronomique**. C’est un filtre
  passe-bas de l’entrée, sans aucune mémoire de la réponse.

Un test unitaire vérifie que M1P privé de son couplage lent redevient
exactement M1, et qu’à l’inverse son état lent est insensible à la condition
initiale de glace alors que celui de M2 ne l’est pas. La comparaison est donc
propre : elle isole la seule chose qu’ORI-C revendique.

---

## 2. Contrôle du harnais

Le budget d’optimisation corrigé exige des centaines de milliers d’évaluations
par modèle, hors de portée du simulateur livré. Une transcription compilée a
donc été écrite, puis vérifiée.

| Contrôle | Résultat |
|---|---|
| Noyau MPT compilé contre `simulate_mpt` | écart maximal **exactement 0,0** sur l'environnement de livraison ; exigé sous 1e-11 ailleurs |
| EMIC compilé contre `simulate_reduced_climate` | écart relatif maximal **1,1 × 10⁻¹⁶** |
| Gain de vitesse | **129 ×** |
| Suite de tests unitaires | **31 sur 31** |

Sans ce contrôle, aucun résultat qui suit n’aurait de valeur. Il est exécuté
par la suite de tests à chaque exécution.

---

## 3. Résultat MPT

### 3.1 Les cinq critères préenregistrés, recalculés

Aucun seuil n’a été modifié. Seuls changent la qualité de l’optimisation, la
correction d’autocorrélation et le témoin.

| Configuration | Critères réussis |
|---|---:|
| Témoin M1, bornes livrées (protocole initial, optimiseur convergé) | **2 / 5** |
| Témoin M1, bornes élargies | **1 / 5** |
| Témoin M1P, bornes livrées | **0 / 5** |
| Témoin M1P, bornes élargies | **0 / 5** |
| **Protocole corrigé complet** (bornes élargies, symétrie retirée, 4 redémarrages, tous convergés) | **1 / 5 contre M1, 0 / 5 contre M1P** |

Le rapport initial annonçait 3 sur 5. Deux critères basculent sans qu’aucun
seuil ne bouge.

- Le BIC : sur le compte brut ΔBIC = −73, sur la taille d’échantillon efficace
  ΔBIC = **+5,5**.
- Le gain de RMSE : 6,0 % avec les bornes livrées, **3,6 %** avec des bornes
  qui ne retiennent plus l’optimum, sous le seuil préenregistré de 5 %.

Le troisième critère encore réussi, le test de Wilcoxon par blocs, l’est
uniquement contre M1 : contre M1P il vaut p = 1,000.

### 3.2 Le résultat central

| Témoin | Paramètres | Gain de RMSE hors échantillon | IC 95 % (blocs mobiles) | P(gain < 5 %) |
|---|---:|---:|---:|---:|
| M0 | 3 | +0,025 | [0,017 ; 0,036] | 0,9999 |
| M1 | 6 | +0,036 | [0,027 ; 0,046] | 0,9952 |
| **M1P** | **8** | **−0,316** | **[−0,389 ; −0,251]** | **1,0000** |

(M2 possède 8 paramètres identifiables après retrait de la symétrie du §3.6 ;
M1P en possède 8 également, par construction.)

M2 bat M1 de 3,6 %, en dessous du seuil préenregistré de 5 %, et le bootstrap
par blocs place cette conclusion à 99,5 % de certitude. Face à un témoin de
complexité égale, M2 ne bat rien : il perd de 32 %, avec un intervalle de
confiance qui ne s’approche pas de zéro.

**Un filtre lent du forçage externe prédit LR04 nettement mieux qu’une mémoire
de la réponse passée, à nombre de paramètres identique.**

> **Note sur les chiffres.** Les sections 3.3 à 3.10 proviennent de la campagne
> de contrôles, exécutée avant que la symétrie du §3.6 ne soit retirée. Ce
> retrait ne change aucune trajectoire ni aucune RMSE : il fixe un point sur une
> orbite d’équivalence exacte. Le calcul final le confirme, gain sur M1
> +0,03574 dans les deux cas. Seuls changent le nombre de paramètres pénalisés
> par le BIC, 9 avant et 8 après, et le résultat de l’ablation, qui devient
> défini.

### 3.3 Ce n’est pas un artefact d’optimisation

Le gain a été mesuré sur dix configurations, de 30 à 1 500 générations, pour
deux jeux de bornes, à données et graines identiques.

- Bornes livrées : le gain M2/M1 vaut 0,060 à **tous** les budgets.
- Bornes élargies : il vaut 0,036 à **tous** les budgets.
- Le gain M2/M1P est négatif dans les **dix** configurations, de −0,18 à −0,32.

Le budget d’optimisation n’est donc pas la variable explicative : la largeur
des bornes l’est. Avec des bornes plus larges, M2 trouve un meilleur optimum
d’apprentissage (RMSE 0,855 contre 0,902) et une **moins bonne** prédiction
(2,042 contre 1,969). C’est du surajustement, et il est propre à M2.

### 3.4 Ce n’est pas un artefact de fenêtre

Neuf séparations calibration/prédiction, de 0,8 à 1,6 Ma :

- gain M2/M1 : de +0,034 à +0,137, médiane +0,042, **4 fenêtres sur 9** au-dessus du seuil de 5 % ;
- gain M2/M1P : de −0,170 à −0,392, **0 fenêtre sur 9** au-dessus du seuil.

La condition de réfutation inscrite dans la synthèse ORI-C — « si le gain
disparaît selon le bassin ou la fenêtre choisis, cette déclinaison d’ORI-C ne
serait pas soutenue » — est remplie contre le témoin apparié, et n’est même pas
stable contre le témoin non apparié.

### 3.5 Distribution nulle : le gain sur M1 n’est pas informatif

Deux nuls ont été construits, 60 tirages chacun, avec des surrogates à phases
aléatoires préservant exactement le spectre de puissance.

| Nul | Gain moyen M2/M1 | Fraction ≥ 5 % | Fraction ≥ 5 % contre M1P |
|---|---:|---:|---:|
| Forçage La2004 aléatoirisé | **+0,124** | **81,7 %** | 3,3 % |
| Cible LR04 aléatoirisée | −0,378 | 10,0 % | 35,0 % |

Lorsqu’on détruit toute relation de phase entre l’insolation et LR04, M2 bat
encore M1 de plus de 5 % dans quatre tirages sur cinq, et d’un gain moyen
(12,4 %) **supérieur au gain réellement observé** (3,6 %). Le gain de M2 sur M1
n’est donc pas distinguable de ce que produit une architecture à trois
paramètres de plus face à une architecture qui en a trois de moins. Contre
M1P, le même nul ne produit un faux positif que dans 3,3 % des cas.

### 3.6 L’ablation : un critère qui n’était pas défini

Le test d’ablation carbone était le seul critère que le protocole initial
réussissait de façon non ambiguë. La campagne a montré qu’il n’était pas bien
posé.

Deux ajustements indépendants de M2, avec des graines différentes, ont convergé
vers des optima qui ne diffèrent que sur deux paramètres :

| Paramètre | Ajustement A | Ajustement B |
|---|---:|---:|
| `forcing_offset` | −0,996 | +1,886 |
| `carbon_offset` | −0,074 | +0,070 |
| tous les autres | identiques à 4 décimales | identiques à 4 décimales |

Ce n’est pas un hasard. Le décalage de l’état lent, `carbon_offset`, déplace
l’équilibre de C d’une constante δ ; comme C n’agit sur la glace qu’à travers
`carbon_feedback_gain × C`, tout δ est **exactement** compensé par un décalage
`−gain × δ` de `forcing_offset`. Vérification directe : δ = 0,144 et
gain = −20 donnent bien l’écart observé de 2,88 sur `forcing_offset`. Les deux
trajectoires de glace sont identiques à 3 × 10⁻¹⁶ près.

C’est une **troisième symétrie exacte**, en plus des deux que le protocole
déclarait avoir retirées (α/R* et β/γ). M2 n’avait donc que huit degrés de
liberté identifiables sur neuf.

La conséquence n’est pas cosmétique. Annuler le couplage carbone supprime un
terme dont la moyenne est absorbée différemment en chaque point de l’orbite de
symétrie. Les deux ajustements, qui prédisent identiquement, donnent des
ablations qui diffèrent de 2,8 unités de RMSE : dans un cas l’ablation dégrade
massivement la prédiction, dans l’autre elle l’améliore. **Le résultat du test
d’ablation dépendait donc d’un choix arbitraire, invisible dans les métriques.**

Correction appliquée : le décalage de l’état lent est fixé à zéro par
définition, comme l’étaient déjà les échelles de R et de C, et `forcing_offset`
porte seul le niveau. Le même traitement est appliqué à M1P pour garder les deux
modèles appariés. Un test unitaire vérifie d’abord que la symétrie existe bien
dans le simulateur, puis qu’elle n’est plus atteignable par l’ajustement.

Après correction, le test d’ablation redevient interprétable, et son résultat
est net.

| Variante | Paramètres | RMSE de prédiction |
|---|---:|---:|
| M1 | 6 | 2,118 |
| M2 complet | 8 | 2,042 |
| **M2, couplage carbone annulé** | **7** | **1,810** |

Le couplage carbone **dégrade** la prédiction hors échantillon de 0,232 en
RMSE. Le petit avantage de M2 sur M1 ne vient donc pas de la mémoire : il vient
des valeurs auxquelles les six paramètres de type M1 ont atterri pendant que le
couplage était actif. Une fois les paramètres figés, la mémoire coûte.

C’est cohérent avec le reste du diagnostic. Le couplage reste collé à sa borne,
sa constante de temps n’est pas identifiée, et il produit un gain
d’apprentissage qui ne se transporte pas hors échantillon : la signature
ordinaire du surajustement.

### 3.7 Les paramètres de mémoire ne sont pas identifiés

Cinq fenêtres × quatre graines :

| Paramètre | Minimum | Médiane | Maximum | Ordres de grandeur |
|---|---:|---:|---:|---:|
| `carbon_feedback_gain` | −20,000 | −20,000 | −19,922 | 0,00 |
| `tau_carbon_kyr` | 22,2 | 10 845 | 12 649 | **2,76** |
| `carbon_offset` | −0,855 | −0,334 | +0,149 | change de signe |

Le couplage carbone reste collé à la borne basse **après élargissement d’un
facteur 10** : l’ajustement en demande toujours davantage, ce qui signale une
non-identifiabilité et non un optimum. La constante de temps de la mémoire
varie de trois ordres de grandeur selon la fenêtre. Le décalage change de
signe. Le profil de vraisemblance confirme que quatre paramètres sur neuf sont
plats à 1 % sur plus de la moitié de leur domaine.

La « stabilité des paramètres », que la synthèse ORI-C nomme parmi les critères
décisifs, n’est pas atteinte.

### 3.8 La dépendance à la chronologie accordée

LR04 est datée par accordage sur l’insolation du 21 juin à 65°N. Onze
définitions du forçage ont été recalculées depuis le même fichier La2004.

| Forçage | Gain M2/M1 | Gain M2/M1P | Corrélation de chronologie |
|---|---:|---:|---:|
| juin 65°N (prescrit) | +0,036 | −0,315 | 0,260 |
| juin 65°S (nuit polaire) | +0,173 | −0,135 | **0,424** |
| décembre 65°N (nuit polaire) | +0,172 | −0,110 | **0,410** |
| obliquité seule | +0,170 | −0,161 | **0,422** |
| excentricité seule | +0,166 | −0,148 | **0,402** |

Trois constats.

1. Le gain de M2 sur M1 dépasse 5 % pour **8 des 11 forçages**, y compris ceux
   qui n’ont aucun sens physique comme moteur d’une déglaciation nordique.
   C’est encore un signe qu’il mesure de la flexibilité.
2. Le gain contre M1P est négatif pour **les 11 forçages**.
3. Le seul critère de chronologie qui puisse être franchi (corrélation ≥ 0,4)
   l’est par des forçages en nuit polaire ou par des composantes orbitales
   nues, jamais par l’insolation prescrite. Un critère qu’on ne passe qu’avec
   un prédicteur physiquement inapproprié ne mesure pas ce qu’il prétend
   mesurer.

### 3.9 L’échec spectral : une nuance importante

Le rapport de puissance 100/41 ka observé vaut 2,604 sur la fenêtre de
prédiction. M2 ajusté produit 0,0047, soit 550 fois trop peu. C’est le résultat
négatif le plus massif du test, et il ne dépend ni du témoin ni de
l’optimisation.

Mais il ne s’agit **pas** d’une impossibilité structurelle. En optimisant
directement le rapport spectral, avec un plafond de RMSE imposé :

| Modèle | Rapport atteignable | RMSE hors échantillon à ce point | RMSE de l’ajustement honnête |
|---|---:|---:|---:|
| M1 | 2,604 | 1,66 | 2,118 |
| M2 | 2,604 | 1,84 | 2,042 |
| M1P | 2,604 | 1,60 | 1,560 |

Il existe donc, pour les trois classes, des paramètres qui reproduisent
simultanément le régime de 100 ka **et** une meilleure erreur de prédiction que
l’ajustement calibré. Ces solutions ne sont simplement pas trouvées en
minimisant la RMSE sur la fenêtre 2,6–1,2 Ma.

Deux réserves. Ce test utilise délibérément la fenêtre de prédiction comme
oracle : il établit une capacité, jamais une validation. Et il vaut pour les
trois modèles indifféremment, donc il ne distingue pas ORI-C. Sa conclusion
utile est méthodologique : **l’échec spectral est un échec de calibration et
d’identifiabilité, non une réfutation de la famille de modèles.** Le choix du
forçage y contribue directement — avec un indice de précession climatique
(e·sin ϖ), M2 atteint 1,03 au lieu de 0,0047, soit 220 fois mieux.

### 3.10 L’avantage ne survit pas au renversement du sens

Ajustement sur 1,2–0 Ma, prédiction sur 2,6–1,2 Ma : M2 perd 18,9 % contre M1,
et M0, le modèle à trois paramètres, est le meilleur des quatre. L’avantage
n’est donc pas une propriété du modèle mais de la direction particulière du
test.

---

## 4. Résultat exoplanétaire

### 4.1 Ce qui tient

Trois contrôles sont favorables et doivent être portés au crédit du protocole.

| Contrôle | Résultat |
|---|---|
| Convergence numérique | Δ varie de 0,6 à 1,5 % entre le pas livré (0,02 Ma) et un pas huit fois plus fin |
| Marge sur le bruit | Δ de M2 vaut 2 × 10⁵ à 7 × 10⁵ fois le résidu du modèle classique |
| Stabilité d’échantillonnage | Réussite structurelle dans 100 % des cas, pour n = 20, 60 et 200 et cinq graines, p de Holm ≤ 2,9 × 10⁻³⁴ |

La dépendance au chemin détectée est donc un fait réel du modèle, pas une
erreur d’intégration ni un accident d’échantillonnage. Le test d’ablation
fonctionne aussi comme prévu.

### 4.2 Le test décisif : la persistance

Les constantes de temps lentes du modèle valent 8 Ma pour la mémoire carbone et
60 Ma pour la récupération du régolithe. Le protocole livré maintient le
forçage final commun pendant 10 Ma — c’est-à-dire moins longtemps que la
mémoire qu’il prétend mesurer. Les deux histoires y sont encore en train de
converger.

En prolongeant le palier :

| Variable | Δ à 10 Ma | Δ à 600 Ma | Temps d’e-folding |
|---|---:|---:|---:|
| température | 2,52 × 10⁻³ K | **0** | 7,02 Ma |
| fraction de glace | 3,53 × 10⁻⁵ | **0** | 7,80 Ma |
| CO₂ | 0,687 ppm | **0** | 7,28 Ma |
| productivité | 3,76 × 10⁻⁴ | 5,6 × 10⁻¹⁷ | 17,66 Ma |

L’écart décroît exponentiellement avec un temps caractéristique de 7 Ma, c’est-
à-dire exactement la constante de temps de la mémoire carbone du modèle, et
atteint zéro. **Ce que le protocole livré détecte n’est pas une inscription
durable, c’est un retard de relaxation.**

### 4.3 Pourquoi c’était inévitable : un attracteur unique

Une dépendance au chemin permanente exige au minimum deux attracteurs sous le
forçage final. Mille états initiaux très dispersés ont été intégrés 800 Ma sous
le seul forçage final prescrit.

| Variable | Dispersion initiale | Dispersion finale |
|---|---:|---:|
| température | 11,98 K | 3,0 × 10⁻¹⁴ K |
| fraction de glace | 0,998 | 2,2 × 10⁻¹⁵ |
| CO₂ | 780 ppm | 6,7 × 10⁻¹² ppm |

Sous obliquité 23,5° et excentricité 0,05, l’EMIC réduit possède **un seul
attracteur**, et cet attracteur est une planète quasi totalement englacée
(fraction de glace 0,9998). Aucune dépendance au chemin permanente n’y est
possible, par construction. Les deux histoires sont comparées entre deux états
presque saturés contre la borne supérieure de la variable de glace, sur le
chemin d’un même état final.

### 4.4 La matérialité est une question de rapport entre durées

1 521 combinaisons de paramètres de mémoire ont été balayées.

| Variable | Fraction matérielle, palier 10 Ma | Fraction matérielle, palier 200 Ma |
|---|---:|---:|
| température | 19,2 % | **0 %** |
| fraction de glace | 0 % | 0 % |
| CO₂ | 72,2 % | 33,1 % |
| productivité | 35,3 % | **0 %** |

La meilleure configuration atteint 0,236 K à 10 Ma — bien au-dessus du seuil de
0,1 K — mais 0,00035 K à 200 Ma, soit un effondrement d’un facteur 680. La
matérialité observée à un palier donné est entièrement gouvernée par le rapport
entre la durée du palier et la constante de temps de la mémoire. Les 33 % qui
subsistent pour le CO₂ correspondent aux cas où le balayage impose une mémoire
plus longue (jusqu’à 400 Ma) que le palier de test lui-même.

### 4.5 Une piste constructive : la bistabilité existe, ailleurs

Cinquante-quatre couples (obliquité finale, excentricité finale) ont été
balayés, avec pour chacun une sonde de 150 états initiaux intégrés 400 Ma.

**Quatre points présentent bien plusieurs attracteurs**, avec une dispersion
finale de 2,4 à 2,7 K en température et de 0,87 à 0,92 en fraction de glace :

| Obliquité finale | Excentricité finale | Glace de l’attracteur |
|---:|---:|---:|
| 12° | 0,30 | 0,193 |
| 23,5° | 0,18 | 0,344 |
| 30° | 0,10 | 0,422 |
| 40° | 0,00 | 0,272 |

Ces points bordent la transition entre régime englacé et régime libre de glace.
Le modèle possède donc la capacité d’une dépendance au chemin permanente. Mais
le forçage final prescrit (23,5°, e = 0,05) se situe **loin** de cette bande,
en plein régime boule de neige. Et même aux quatre points bistables, les deux
histoires A et B retombent dans le **même** bassin : 0 point sur 54 conserve un
écart matériel après un palier de 200 Ma.

Ce n’est donc pas le modèle qui interdit le résultat recherché, c’est le choix
du forçage final et le dessin des deux trajectoires.

---

## 5. Ce qui est établi et ce qui ne l’est pas

| Proposition | Statut après correction |
|---|---|
| L’implémentation est complète, reproductible, et son noyau d’optimisation est exactement le modèle de référence | **Établi** |
| La dépendance au chemin de l’EMIC réduit est réelle, convergée numériquement et statistiquement robuste | **Établi dans le modèle réduit** |
| Le test d’ablation carbone du protocole initial était bien posé | **Réfuté** : une symétrie exacte non retirée rendait son résultat indéterminé (écart de 2,8 en RMSE entre deux ajustements équivalents) |
| Une fois la symétrie retirée, la mémoire carbone améliore la prédiction | **Réfuté** : le couplage dégrade la RMSE hors échantillon de 0,232 |
| M2 réduit l’erreur de prédiction par rapport à M1 | Établi, mais **non informatif** : un nul à forçage aléatoire produit le même effet dans 82 % des tirages |
| M2 surpasse un modèle historique classique de complexité égale | **Réfuté** : M2 perd de 32 %, sur 10 configurations, 9 fenêtres et 11 forçages |
| Les paramètres de la mémoire ORI-C sont identifiés et stables | **Réfuté** : couplage à la borne, constante de temps sur 2,8 ordres de grandeur |
| M2 reproduit l’émergence de la bande de 100 ka | **Réfuté pour le modèle calibré** (0,0047 contre 2,604) |
| La famille de modèles est structurellement incapable de la bande de 100 ka | **Réfuté** : capacité démontrée, l’échec est de calibration |
| La dépendance au chemin exoplanétaire est une inscription durable | **Réfuté** : décroissance exponentielle à 7 Ma, écart nul à 600 Ma |
| L’EMIC réduit possède plusieurs équilibres sous le forçage final prescrit | **Réfuté** : attracteur unique, dispersion finale 3 × 10⁻¹⁴ K |
| L’EMIC réduit possède plusieurs équilibres quelque part | **Établi** : 4 points sur 54 dans le balayage du régime final |
| La couche astronomique N-corps du cadre ORI-C | **Non touchée par ce travail** |

---

## 6. Corrections à porter dans la synthèse ORI-C

Les formulations suivantes remplacent celles du document de synthèse.

**§10.1, ligne « Réponse terrestre ».** Remplacer « Non testé ici / Étape
ouverte » par : *testé et non soutenu. Face à un témoin de complexité égale, le
modèle à mémoire explicite ne surpasse pas le modèle classique sur LR04 hors
échantillon.*

**§11.11, condition de consolidation ou de réfutation.** La condition écrite —
« si M2 améliore de manière stable les prédictions hors échantillon face à M1 »
— est mal spécifiée : M1 possède six paramètres et M2 neuf. Elle doit être
remplacée par : *face à un témoin possédant le même nombre de paramètres et la
même structure de constantes de temps, mais dont l’état lent filtre le forçage
externe au lieu d’enregistrer la réponse passée.* Sous cette condition
corrigée, le résultat est négatif.

**§12.5, test exoplanétaire propre à ORI-C.** La condition écrite — « si la
variable ORI-C améliore la prédiction de cette dépendance au chemin face au
même modèle sans cette variable » — est nécessaire mais insuffisante. Deux
conditions doivent y être ajoutées : *(a) l’écart doit survivre à un palier
final long devant toutes les constantes de temps du modèle ; (b) le forçage
final doit se situer dans une région où le modèle possède plus d’un
attracteur.* Sous ces conditions, le résultat actuel est négatif, et la cause
est identifiée : le palier est trois fois plus court que la mémoire testée et
le forçage final tombe dans un régime à attracteur unique.

**§10.5 et §14, conclusion de statut.** La phrase « La démonstration proprement
spécifique à ORI-C apparaîtra si un modèle dépendant de l’histoire produit des
prédictions géologiques fixées à l’avance et surpasse, hors échantillon, un
modèle historique classique » reste exacte comme programme. Il faut y ajouter
que ce test a maintenant été conduit dans sa version réduite, et qu’il est
négatif : *une première exécution de ce test, sur LR04 et avec un témoin de
complexité égale, ne soutient pas la déclinaison paléoclimatique du cadre.*

---

## 7. Programme corrigé

Les cinq points suivants sont ceux qu’un prochain tour doit traiter, dans
l’ordre.

1. **Ne jamais publier un écart contre un témoin moins complexe.** Tout témoin
   doit égaler le nombre de paramètres et la structure temporelle du modèle
   testé. C’est la correction la moins coûteuse et la plus décisive.
2. **Rendre la mémoire identifiable avant de la tester.** Le couplage carbone
   reste sur sa borne après élargissement d’un facteur 10 et sa constante de
   temps varie de trois ordres de grandeur. Une reparamétrisation, ou une
   contrainte physique externe sur ces deux quantités, est un préalable. Toute
   symétrie doit par ailleurs être recherchée activement : celle qui rendait
   l’ablation indéterminée n’est apparue qu’en comparant deux ajustements
   indépendants qui prédisaient à l’identique. Comparer les **paramètres**, et
   pas seulement les métriques, de plusieurs redémarrages doit être un contrôle
   systématique.
3. **Changer le forçage, pas seulement le modèle.** L’insolation du 21 juin à
   65°N ne porte presque pas de puissance à 100 ka ; c’est une cause directe de
   l’échec spectral. L’énergie estivale intégrée et l’indice de précession
   climatique doivent être préenregistrés comme forçages alternatifs, avec la
   chronologie tenue à l’écart de l’accordage.
4. **Dimensionner le palier exoplanétaire sur les constantes de temps.** Un
   palier final doit valoir au moins dix fois la plus lente des mémoires du
   modèle, et le rapport palier/mémoire doit être rapporté.
5. **Placer le forçage final dans la bande bistable.** Les quatre points
   identifiés — notamment (30°, e = 0,10) et (23,5°, e = 0,18) — sont les seuls
   où une dépendance au chemin permanente est possible. Les deux histoires
   doivent en outre être dessinées pour encadrer la frontière de bassin, ce que
   les trajectoires A et B actuelles ne font pas.

---

## 8. Reproduction

```bash
cd ORI-C_tests_memoire_historique
export PYTHONPATH="$PWD/src"
export MPLCONFIGDIR="${TMPDIR:-/tmp}/oric-memory-tests-matplotlib"

python3 -m unittest discover -s tests -v
python3 -m oric_memory_tests --root "$PWD" run-all --config configs/primary.json

cd stress
python3 verify_core.py
python3 a_mpt.py && python3 b_exo.py && python3 b2_regime.py
python3 c_indep.py && python3 d_budget_ladder.py && python3 verdict.py
python3 figures.py && python3 make_report.py
```

| Document | Contenu |
|---|---|
| `RAPPORT_CORRIGE.md` | ce document |
| `REPORT.md` | verdict du protocole corrigé, généré à chaque exécution |
| `STRESS_REPORT.md` | tous les tableaux de la campagne de contrôles, générés |
| `METHODS.md` | décisions de préenregistrement corrigées |
| `VALIDATION.md` | contrôles de livraison |
| `results_stress/figures/` | six figures |
| `MANIFEST.sha256` | empreintes de l’ensemble du paquet |

## Sources primaires

- Lisiecki, L. E. et Raymo, M. E. (2005), LR04, doi:10.1029/2004PA001071, jeu
  NOAA doi:10.25921/k88j-0106
- Laskar, J. et collaborateurs (2004), La2004, doi:10.1051/0004-6361:20041335,
  données IMCCE
