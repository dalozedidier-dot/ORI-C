# Méthodes et décisions de préenregistrement

## Question MPT

La mémoire carbone explicite de M2 améliore-t-elle une prévision réellement
figée de la transition du Pléistocène moyen, par rapport à un témoin soumis aux
mêmes contraintes ?

La comparaison décisive n’est pas M1 contre M2. M1 possède six paramètres et M2
huit : un avantage de M2 peut provenir de deux degrés de liberté
supplémentaires plutôt que d’une mémoire. La comparaison décisive est **M1P
contre M2**.

## Le témoin à complexité égale

M1P reprend M1 et lui ajoute un état lent supplémentaire de structure
identique à celui de M2 : un gain et une constante de temps. Il possède donc
exactement huit paramètres, comme M2.

La seule différence est la variable qui alimente l’état lent.

- Dans M2, l’état lent suit le volume de glace passé. C’est une inscription de
  la réponse du système, au sens d’ORI-C.
- Dans M1P, l’état lent suit le forçage astronomique. C’est un simple filtre
  passe-bas de l’entrée, sans mémoire de la réponse.

Cette construction rend le test réfutable. Si M2 ne bat pas M1P, alors ce qui
améliore la prévision est la présence d’une seconde échelle de temps, non le
fait qu’elle enregistre l’histoire du système.

M0 reste un contrôle de faible complexité.

## Séparation temporelle

- calibration : 2 600 à 1 200 ka BP
- prédiction : 1 200 à 0 ka BP
- grille commune : 1 ka

Les moyennes et écarts-types utilisés pour normaliser LR04 et l’insolation sont
calculés uniquement sur la calibration.

## Optimisation

Chaque modèle est ajusté par évolution différentielle. La fonction objectif est
la RMSE sur la calibration. Le nombre de paramètres libres est 3 pour M0, 6 pour
M1, 8 pour M2 et 8 pour M1P.

Trois décisions encadrent l’ajustement.

1. **Redémarrages multiples.** Quatre départs indépendants par modèle, avec
   initialisation de Sobol. Un témoin mal ajusté crée un avantage artificiel
   pour le modèle testé ; la dispersion entre redémarrages est journalisée.
2. **Budget suffisant.** 800 générations et une population de 18 par paramètre,
   tolérance 10⁻⁸. La première version employait 30 générations et une
   population de 6, et son propre journal indiquait la limite d’itérations
   atteinte pour M1 et M2.
3. **Bornes non contraignantes.** Les bornes sont élargies d’au moins un ordre
   de grandeur par rapport à la première version, où quatre paramètres de M2 se
   trouvaient sur une borne à l’optimum. Les paramètres restant sur une borne
   après élargissement sont signalés dans `summary.json` : ils indiquent une
   non-identifiabilité, non un optimum.

## Symétries retirées

Trois symétries exactes rendent des paramètres non identifiables. Toutes trois
sont retirées par définition.

1. Le changement d’échelle de R peut être absorbé simultanément dans α et R*.
   L’échelle de R est fixée à 1.
2. Le changement d’échelle de C peut être absorbé dans β et γ. L’échelle de C
   est fixée à 1.
3. Le décalage de l’état lent, `carbon_offset` dans M2, déplace l’équilibre de
   C d’une constante δ. Comme C n’agit sur la glace qu’à travers
   `carbon_feedback_gain × C`, tout δ est exactement compensé par un décalage
   `−gain × δ` de `forcing_offset`. Le décalage est fixé à zéro et
   `forcing_offset` porte seul le niveau. Le même traitement s’applique à
   `slow_forcing_offset` dans M1P.

La troisième symétrie n’avait pas été retirée dans la première version. Elle
n’est pas seulement redondante : elle rendait le test d’ablation carbone
indéterminé. Annuler le couplage supprime un terme dont la moyenne est absorbée
différemment en chaque point de l’orbite de symétrie, si bien que deux
ajustements donnant exactement la même prédiction donnaient des ablations
séparées de plusieurs unités de RMSE. Un test unitaire vérifie que la symétrie
existe dans le simulateur et qu’elle n’est plus atteignable par l’ajustement.

## Évaluation

Les paramètres ne sont jamais réajustés après 1,2 Ma. Les mesures sont :

- RMSE et corrélation
- corrélation maximale avec décalage limité à ±30 ka
- rapport de puissance 80–120 ka sur 39–43 ka
- chronologie des fortes déglaciations
- AIC, AICc et BIC
- RMSE sur blocs contigus de 50 ka et test de Wilcoxon apparié
- intervalle de confiance du gain par bootstrap sur blocs mobiles

## Traitement de l’autocorrélation

Sur une grille de 1 ka, les résidus de prédiction ont une autocorrélation de
rang 1 supérieure à 0,97, soit un temps de décorrélation de l’ordre de 34 ka.
La fenêtre de prédiction contient 1 200 points de grille mais moins de vingt
points indépendants.

Deux conséquences sont traitées explicitement.

- Le BIC rapporté utilise la taille d’échantillon efficace
  n_eff = n (1 − ρ) / (1 + ρ). Le compte brut est conservé sous
  `bic_naive` à titre de comparaison, mais il ne sert pas au verdict : avec
  n = 1 200, le terme de pénalité devient négligeable devant la vraisemblance
  et les paramètres supplémentaires paraissent toujours justifiés.
- L’intervalle de confiance du gain de RMSE provient d’un bootstrap par blocs
  mobiles, dont la longueur de bloc est calée sur le temps de décorrélation
  mesuré. Un rééchantillonnage point par point supposerait l’indépendance.

## Question exoplanétaire

Deux histoires orbitales différentes laissent-elles des états finaux
différents lorsque le forçage final est exactement identique, ce signal
disparaît-il lorsque les variables de mémoire sont figées, et **subsiste-t-il
lorsque le forçage final est maintenu bien au-delà des constantes de temps du
modèle** ?

Les deux chemins sont prescrits. Cette décision isole le test climatique de la
difficulté distincte de construire deux trajectoires N-corps-spin possédant la
même frontière finale.

## Trois modèles exoplanétaires

- `classic` : température, glace et CO₂ avec coefficients fixes
- `M2` : même noyau avec régolithe et mémoire du carbone dynamiques
- `ablated` : mêmes couplages que M2, avec régolithe et carbone figés à une
  référence commune

Les ensembles sont appariés. Chaque répétition reçoit les mêmes conditions
initiales pour les trajectoires A et B et pour les trois modèles.

## Statistiques exoplanétaires

La moyenne des deux derniers millions d’années du palier définit l’état final.
Pour chaque répétition et variable, le score est |A − B|. M2 est comparé à sa
version ablatée par Wilcoxon apparié avec correction de Holm.

Trois notions sont séparées.

1. **Significativité.** L’écart de M2 dépasse-t-il celui de sa version ablatée
   de façon statistiquement fiable ?
2. **Matérialité.** L’écart dépasse-t-il un seuil physique fixé avant le
   calcul : 0,1 K, 0,01 de fraction glaciaire, 1 ppm de CO₂ et 0,01 de
   productivité normalisée ?
3. **Persistance.** L’écart survit-il à un palier final beaucoup plus long ?

Le critère de persistance a été ajouté parce que le palier de 10 Ma de la
première version est plus court que les mémoires qu’il prétend mesurer : la
mémoire carbone du modèle a une constante de temps de 8 Ma et la récupération du
régolithe de 60 Ma. Sur un palier de 10 Ma, deux histoires différentes sont
encore en train de converger, et tout écart mesuré peut n’être qu’un retard de
relaxation. Le protocole corrigé rejoue donc le test avec un palier trente fois
plus long et exige qu’au moins deux variables conservent un dixième de leur
écart tout en restant au-dessus du seuil de matérialité.

Une dépendance au chemin permanente exige au minimum deux attracteurs sous le
forçage final. Cette condition nécessaire est vérifiée séparément dans
`stress/b_exo.py` et `stress/b2_regime.py`.
