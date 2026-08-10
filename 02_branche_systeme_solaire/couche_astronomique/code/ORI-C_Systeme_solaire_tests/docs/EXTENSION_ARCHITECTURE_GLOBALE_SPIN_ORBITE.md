# Extension de la causalité architecturale : architecture globale, fréquences séculaires et spin-orbite

## Statut

Ce document est **prospectif**. Il organise les extensions nécessaires de la couche astronomique sans modifier les verdicts actuels. `C-AST-01` reste `E4_modele` et reste attaché au modèle physique réduit déjà exécuté et certifié.

L'objectif est de prolonger le patron causal déjà réussi :

```text
architecture planétaire
→ intervention contrôlée
→ réponse orbitale terrestre
→ effet supérieur au bruit
→ reproductibilité
```

vers une chaîne plus complète :

```text
architecture planétaire globale
→ modes séculaires g_i et s_i
→ orbite terrestre
→ spin terrestre (précession + obliquité)
→ insolation
```

Aucune étape nouvelle ne doit être interprétée comme acquise avant exécution de son protocole propre et de ses contrôles.

## 1. État réel du modèle au 10 août 2026

Le témoin `real_science_max` **inclut déjà les huit planètes**, de Mercure à Neptune. Uranus et Neptune ne sont donc pas une extension à ajouter au modèle courant : elles font partie du témoin de référence.

Un contrôle séparé ajoute déjà Pluton et cinq astéroïdes : **Cérès, Pallas, Vesta, Iris et Bamberga**. Sur 2 Ma, la comparaison publiée entre le témoin à huit planètes et cette configuration à quatorze corps donne une corrélation d'environ `0,999999924` et une RMSE `5,28 × 10^-6` sur l'excentricité terrestre. Ce contrôle montre que l'ajout de ces petits corps modifie peu la série sur cette fenêtre ; il ne prouve pas leur négligeabilité à toute échelle de temps.

Le modèle reste réduit sur trois points essentiels :

- la Terre est représentée par le **barycentre Terre-Lune**, la Lune n'est pas un corps résolu ;
- l'obliquité et la précession de l'axe terrestre ne sont pas intégrées dynamiquement ;
- les marées séculaires et l'évolution de la distance Terre-Lune ne sont pas incluses.

## 2. Référence séculaire La2010a

Les fréquences fondamentales `g_i` décrivent principalement la précession séculaire des périhélies ; les `s_i` décrivent les modes nodaux et deviennent indispensables dès que l'on veut traiter l'inclinaison orbitale et le spin terrestre.

Les valeurs de référence sont stockées dans :

- `data/reference/la2010/La2010a_secular_frequencies.csv`
- `data/reference/la2010/La2010a_eccentricity_combinations.csv`

Elles reprennent la Table 6 de Laskar, Fienga, Gastineau & Manche (2011, A&A 532, A89). Les quatre modes internes sont déterminés sur 20 Ma et les modes externes sur 50 Ma dans cette table.

### 2.1 Modes `g_i` La2010a

| Mode | La2010a (arcsec/an) | Période tabulée | Association dominante |
|---|---:|---:|---|
| `g1` | 5,59 | 231 843 ans | Mercure |
| `g2` | 7,453 | 173 913 ans | Vénus |
| `g3` | 17,368 | 74 620 ans | Terre |
| `g4` | 17,916 | 72 338 ans | Mars |
| `g5` | 4,257482 | 304 407 ans | Jupiter |
| `g6` | 28,2449 | 45 884 ans | Saturne |
| `g7` | 3,087946 | 419 696 ans | Uranus |
| `g8` | 0,673019 | 1 925 646 ans | Neptune |

Ces valeurs sont les **valeurs tabulées** de La2010a, et non des constantes exactes au sens mathématique. `g1` à `g4` sont notamment publiés avec une précision plus faible que `g5` à `g8`. Les colonnes `Δ100` de la source montrent aussi une variation des fréquences sur 100 Ma. Il est donc incorrect de présenter toutes les combinaisons dérivées comme des périodes exactes et invariantes.

Dans cette table, `g5` est particulièrement stable (`Δ100 = 0,000030 arcsec/an`) et `g6` varie d'environ `0,0010 arcsec/an`, alors que `g2` varie davantage (`0,019 arcsec/an`). Cette hiérarchie justifie l'intérêt des modes associés aux géantes, mais elle ne transforme aucune fréquence en constante immuable.

### 2.2 Combinaisons liées aux principales bandes d'excentricité

À partir des valeurs tabulées :

| Combinaison | Différence (arcsec/an) | Période dérivée | Bande |
|---|---:|---:|---|
| `g4 - g5` | 13,658518 | 94 886 ans | ~95 ka |
| `g3 - g5` | 13,110518 | 98 852 ans | ~99 ka |
| `g4 - g2` | 10,463000 | 123 865 ans | ~124-125 ka |
| `g3 - g2` | 9,915000 | 130 711 ans | ~131 ka |
| `g2 - g5` | 3,195518 | 405 568 ans | ~405 ka |
| `g4 - g3` | 0,548000 | 2 364 964 ans | ~2,4 Ma |

La bande de ~405 ka est classiquement associée à `g2 - g5`. Le calcul ORI-C de référence place son pic à `408 184 ans`, exactement au même emplacement que le pic extrait de la série La2010a utilisée par le pipeline. Cette concordance est une validation spectrale du modèle réduit sur cette bande ; elle ne signifie pas que `408 184 ans` est la période théorique universelle de `g2 - g5`.

## 3. Extension utile maintenant : tester la spécificité des géantes

Puisque Uranus et Neptune sont déjà présentes, la prochaine question n'est pas « que se passe-t-il si on les ajoute ? », mais :

> les effets causaux produits par les interventions sur Jupiter et Saturne restent-ils dominants lorsqu'on applique des interventions comparables à Uranus et Neptune ?

La prochaine campagne doit donc conserver le témoin huit planètes et ajouter des interventions **symétriques** sur les quatre géantes, par exemple même variation relative de masse et de demi-grand axe. Les amplitudes, métriques et seuils doivent être fixés avant calcul.

Mesures minimales :

1. déplacement de `g5`, `g6`, `g7`, `g8` ;
2. déplacement des combinaisons `g4-g5`, `g3-g5`, `g2-g5`, `g4-g3` ;
3. réponse de l'excentricité terrestre ;
4. rapport intervention / dispersion d'ensemble ;
5. stabilité au pas de temps et à l'intégrateur ;
6. comparaison huit planètes / quatorze corps maintenue comme contrôle physique.

L'hypothèse de « dominance Jupiter/Saturne » ne doit pas être promue avant ce test. Le dépôt actuel démontre un effet de leurs interventions, pas encore leur dominance causale par comparaison expérimentale symétrique avec Uranus et Neptune.

## 4. Horizons plus longs : ce qu'il faut changer

Le témoin actuel couvre 20 Ma et l'ensemble chaotique huit réalisations couvre 10 Ma. Étendre une trajectoire unique à 50 ou 100 Ma ne constitue pas automatiquement une amélioration de précision : la corrélation de phase avec une solution de référence décroît avec l'horizon dans un système chaotique.

Au-delà de quelques dizaines de Ma, le protocole doit privilégier :

- des **ensembles** de conditions initiales proches ;
- les distributions de fréquences et d'amplitudes plutôt qu'une phase point par point ;
- la présence, la dérive et l'intermittence des bandes ;
- les transitions de résonance ;
- des comparaisons entre familles de solutions indépendantes.

La bande ~2,4 Ma est déjà détectée dans le témoin 20 Ma. Les interventions actuelles limitées à 2 Ma ne peuvent cependant pas résoudre proprement sa réponse contrefactuelle. Une extension des interventions, pas seulement du témoin, est donc nécessaire.

## 5. Lune et obliquité : ce qui est établi et ce qui ne l'est pas

### 5.1 Terre actuelle

Laskar, Joutel & Robutel (1993) trouvent, pour la configuration actuelle, une obliquité essentiellement stable autour de `23,3°`, avec des variations d'environ `±1,3°`. La période dominante est de l'ordre de 40-41 ka.

La présence de la Lune augmente fortement la précession effective de l'axe terrestre. Dans les formulations modernes de dynamique du spin, une Terre solaire seule a une constante de précession de l'ordre de `20 arcsec/an`, alors que l'effet additionnel de la Lune porte la valeur effective vers `50 arcsec/an`. Il est donc préférable d'écrire que **la Lune fournit une contribution majeure au couple de précession**, plutôt que « exactement la moitié ».

Dans les intégrations prospectives illustrées par Laskar, l'évolution tidale lente du système Terre-Lune diminue cette fréquence au cours du futur ; un croisement avec des fréquences orbitales devient possible à l'échelle du milliard d'années, autour de 1,5 Ga dans l'exemple publié par l'auteur. Ce nombre est un résultat de modèle de très long terme, **pas un seuil à incorporer dans le protocole ORI-C actuel**.

Cette augmentation déplace la dynamique du spin à l'écart d'un large recouvrement de résonances avec les fréquences nodales orbitales `s_i`.

### 5.2 Terre sans Lune

Le résultat classique de Laskar et al. (1993) est une **carte de fréquences** dans laquelle la zone chaotique s'étend presque de `0°` à `85°` lorsque le couple lunaire est supprimé. Cette plage décrit un domaine dynamique accessible dans cette analyse et ne doit pas être présentée comme la trajectoire typique obligatoire d'une Terre sans Lune.

Les intégrations de Lissauer, Barnes & Chambers (2012), menées jusqu'à 4 Ga selon les cas, montrent une image plus nuancée : l'obliquité d'une Terre sans Lune varie davantage que celle de la Terre actuelle, mais reste souvent confinée dans une plage totale d'environ `20-25°` pendant des centaines de millions d'années. Le comportement dépend notamment des conditions initiales et de la vitesse de rotation.

Conséquence pour ORI-C : le test « avec Lune / sans Lune » est intéressant comme **intervention architecturale sur le spin**, mais son critère ne doit pas être « atteindre 0-85° ». Il doit mesurer des quantités robustes : amplitude de l'obliquité, diffusion, temps de résidence, franchissement de zones résonantes et effet sur l'insolation.

### 5.3 Portée climatique

Des variations d'obliquité plus grandes modifient fortement la distribution latitudinale et saisonnière de l'insolation. Cela ne suffit toutefois pas à conclure directement à une « instabilité climatique majeure » ou à une perte d'habitabilité. Cette étape exige un modèle climatique ou au minimum une fonction de réponse physique explicitement validée.

La chaîne à tester est donc :

```text
architecture planétaire + architecture Terre-Lune
→ g_i et s_i
→ précession / obliquité
→ insolation
→ réponse climatique
```

La causalité peut être testée jusqu'à l'insolation sans GCM ; l'habitabilité ne doit pas être déclarée à partir de l'obliquité seule.

## 6. Référence La2010 / La2004 pour le spin

Le dépôt utilise correctement La2010 comme référence orbitale. Pour l'étape spin-orbite, il faut respecter une distinction importante indiquée par l'IMCCE :

- **La2010** : référence pour les éléments orbitaux de la Terre ;
- **La2004** : référence à utiliser pour l'obliquité et l'insolation dans les produits officiels IMCCE associés.

Il serait donc incorrect d'écrire que « La2010 complète » fournit déjà une solution d'obliquité équivalente à La2004.

## 7. Plan expérimental progressif

### Étape A — déjà réalisée

Témoin à huit planètes, de Mercure à Neptune, avec conditions initiales Horizons DE441, relativité `gr_potential`, validation Horizons et La2010, intégration 20 Ma et ensemble 10 Ma.

### Étape B — déjà réalisée comme contrôle

Configuration à quatorze corps : huit planètes + Pluton + Cérès + Pallas + Vesta + Iris + Bamberga. Ce contrôle reste un contrôle de fidélité, pas la configuration obligatoire de toutes les interventions.

### Étape C — prochaine campagne causale

Interventions appariées sur Jupiter, Saturne, Uranus et Neptune ; extraction explicite des `g_i`; comparaison des déplacements de bandes et de la réponse terrestre. Cette étape teste la spécificité de l'architecture des géantes.

### Étape D — spin-orbite Terre-Lune

Ajouter un module de spin validé indépendamment :

- précession de l'axe ;
- obliquité dynamique ;
- fonctions orbitales `p(t), q(t)` ou équivalent à partir de l'intégration ;
- couple solaire et lunaire ;
- scénario avec Lune et scénario d'ablation lunaire ;
- évolution tidale séparée dans une extension longue durée ;
- validation contre La2004 pour l'obliquité/insolation.

Une simple représentation du barycentre Terre-Lune ne suffit pas à produire l'effet stabilisateur de la Lune sur l'axe terrestre.

### Étape E — chaîne radiative

Calculer l'insolation, notamment à 65°N lorsque le protocole climatique le justifie, puis tester si les interventions architecturales modifient la distribution d'insolation au-delà du bruit numérique et des variations internes de l'ensemble.

## 8. Critères de prudence

- Ne pas reclasser `C-AST-01` à partir de ces extensions non exécutées.
- Ne pas présenter le domaine chaotique `0-85°` comme une trajectoire typique d'une Terre sans Lune.
- Ne pas convertir une variation d'insolation en verdict d'habitabilité sans modèle de réponse climatique.
- Ne pas appeler « exactes » les fréquences séculaires tabulées lorsque leur précision est limitée et qu'elles varient sur le temps long.
- Ne pas considérer une trajectoire unique à 50-100 Ma comme plus probante qu'un ensemble correctement contrôlé.
- Ne pas attribuer à Uranus et Neptune une « faible influence » avant intervention comparative : leur rôle peut être secondaire sur certaines métriques tout en étant important dans la structure séculaire globale.

## 9. Références principales

- Laskar, J., Fienga, A., Gastineau, M. & Manche, H. (2011), *La2010: a new orbital solution for the long-term motion of the Earth*, Astronomy & Astrophysics 532, A89.
- IMCCE, *Astronomical Solutions for Earth Paleoclimates*, jeux La2010 et La2004.
- Laskar, J., Joutel, F. & Robutel, P. (1993), *Stabilization of the Earth's obliquity by the Moon*, Nature 361, 615-617, doi:10.1038/361615a0.
- Lissauer, J. J., Barnes, J. W. & Chambers, J. E. (2012), *Obliquity variations of a moonless Earth*, Icarus 217, 77-87, doi:10.1016/j.icarus.2011.10.013.
- Saillenfest, M., Laskar, J. & Boué, G. (2019), *Secular spin-axis dynamics of exoplanets*, Astronomy & Astrophysics 623, A4.
