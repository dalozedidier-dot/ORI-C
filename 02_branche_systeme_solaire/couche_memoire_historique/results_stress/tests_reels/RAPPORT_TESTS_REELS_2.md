# Tests sur données réelles — seconde batterie, robustesse du verdict

Scripts : `stress/g_tests_reels_2.py`, `stress/h_g2_corrige.py`.
Sorties : `g_tests_reels_2.json`, `h_g2_corrige.json`,
`g1_validation_croisee.csv`, `g3_convention_insolation.csv`.

La première batterie mesurait des planchers d'interprétation. Celle-ci attaque
le verdict lui-même, sur quatre angles capables de le **renverser**. Aucun ne
l'a fait.

Tous comparent M2 à **M1P**, témoin de complexité égale.

---

## G1 — Validation croisée par blocs

Le verdict reposait sur un découpage unique à 1200 ka. Cinq blocs contigus
donnent une distribution au lieu d'un nombre.

| Bloc | Fenêtre | M2 | M1P | M1 | Gain / M1P |
|---|---|---:|---:|---:|---:|
| 0 | 2600–2081 ka | 3,299 | 0,615 | 0,926 | −4,361 |
| 1 | 2080–1561 ka | 0,559 | 0,518 | 0,749 | −0,080 |
| 2 | 1560–1041 ka | 0,755 | 0,703 | 0,784 | −0,073 |
| 3 | 1040–521 ka | 1,229 | 1,041 | 1,270 | −0,181 |
| 4 | 520–0 ka | 1,520 | 1,355 | 1,576 | −0,122 |

**0 bloc sur 5 favorable à M2 contre le témoin apparié.** Médiane −0,122,
étendue [−4,361 ; −0,073].

Contre M1, l'image est différente et doit être donnée : **4 blocs sur 5
favorables**, par des marges de +0,03 à +0,25, avec un effondrement dans le
bloc le plus ancien.

> **Ne pas citer la moyenne seule.** La moyenne du gain contre M1 vaut −0,441,
> entièrement portée par le bloc 0 ; la médiane vaut +0,036. Les deux chiffres
> pris isolément induisent en erreur, dans des directions opposées.

**Verdict.** Le résultat n'était pas un artefact de la coupure à 1200 ka. Il
est stable sur toute l'étendue de l'archive.

---

## G2 — Renversement temporel, et une correction de protocole

Une mémoire physique est causale, donc asymétrique dans le temps. Un modèle
dont la mémoire porte une information de direction doit ajuster la série vraie
mieux que la série retournée.

### Le défaut de la première version

Le masque d'entraînement prenait les 55 % **premiers points du tableau**. En
sens avant cela couvrait 2600–1170 ka ; après retournement, 0–1430 ka. Les deux
directions n'ajustaient pas les mêmes données : « sens du temps » se trouvait
confondu avec « quel segment ».

Version d'origine, à ne pas utiliser :

| Modèle | Asymétrie | Relative |
|---|---:|---:|
| M0 | +0,014 | 1,4 % |
| M1 | −0,015 | −1,5 % |
| M2 | +0,072 | 8,2 % |
| M1P | +0,073 | 8,4 % |

### La correction

`h_g2_corrige.py` emploie un masque **centré et exactement symétrique**,
invariant par retournement du tableau : 1431 points, 2015–585 ka, identiques
dans les deux sens. La symétrie est vérifiée par assertion à l'exécution.

Une asymétrie résiduelle subsiste et n'est pas éliminable : la condition
initiale et la mise en régime avant le masque diffèrent d'un sens à l'autre.
C'est une composante du sens du temps, pas un biais de segment, et elle
s'applique identiquement aux quatre modèles.

| Modèle | Avant | Arrière | Asymétrie | Relative |
|---|---:|---:|---:|---:|
| M0 | 0,985 | 0,998 | +0,014 | +1,4 % |
| M1 | 0,930 | 0,872 | **−0,059** | **−6,3 %** |
| M2 | 0,905 | 0,869 | −0,036 | −4,0 % |
| M1P | 0,873 | 0,863 | −0,010 | −1,2 % |

**La correction change la réponse.** Les 8 % attribués à M2 et M1P étaient
majoritairement un artefact de segment. Sur les mêmes points, l'asymétrie tombe
à 4,0 % et 1,2 %, et **change de signe**.

Trois lectures, dans l'ordre de ce qu'elles autorisent.

1. **Le signe est contraire à l'hypothèse.** Les trois modèles paramétrés
   ajustent la série **retournée** légèrement mieux que la vraie. Une mémoire
   causale prédit l'inverse. Aucun d'eux ne se comporte comme un enregistrement
   orienté du passé.
2. **L'ampleur ne suit pas la présence de mémoire ORI-C.** En valeur absolue,
   M1 (6,3 %) dépasse M2 (4,0 %), qui dépasse M1P (1,2 %). Or M1 ne contient
   aucune rétroaction de la réponse passée. La sensibilité au sens du temps ne
   trace donc pas le mécanisme testé.
3. **Le critère préenregistré était mal formulé.** Il demandait « asymétrie de
   M2 supérieure à celle de M1P », en supposant implicitement une asymétrie
   positive. Toutes les valeurs étant négatives, la réponse littérale — non —
   n'est pas la lecture substantielle. Celle-ci est donnée par le signe et
   l'ampleur ci-dessus, et elle n'appuie pas davantage M2.

> **Limite à retenir.** Aucun intervalle de confiance n'a été calculé sur ces
> asymétries. Les écarts valent 1 à 6 % ; rien n'établit qu'ils se distinguent
> du bruit d'ajustement. Ce test dit ce qu'il ne faut pas conclure, pas ce
> qu'il faut conclure.

---

## G3 — Convention d'insolation

65°N au solstice est un choix conventionnel.

| Convention | M2 | M1P | Gain / M1P | Gain / M1 |
|---|---:|---:|---:|---:|
| 60°N solstice | 2,047 | 1,563 | −0,310 | +0,035 |
| 65°N solstice | 2,042 | 1,553 | −0,315 | +0,036 |
| 70°N solstice | 2,035 | 1,547 | −0,316 | +0,037 |
| 65°N moyenne annuelle | 2,049 | 1,562 | −0,312 | +0,033 |

Écart total sur le gain : **0,006**. **0 convention sur 4 favorable à M2** face
au témoin apparié.

**Verdict.** Le résultat ne mesure ni la latitude ni la saison. Contrôle
interne : la ligne 65°N solstice redonne exactement les RMSE de T1 (2,042 et
1,553) par un chemin de code différent.

---

## G4 — Distribution nulle par surrogates de Fourier

La cible est remplacée par une série de même spectre et de phases aléatoires.

| Quantité | Valeur |
|---|---:|
| Gain observé | −0,315 |
| Nulle, moyenne | −0,046 |
| Nulle, écart-type | 0,305 |
| Nulle, étendue | [−0,958 ; +0,231] |
| **p unilatérale « gain supérieur »** | **0,923** |

Onze surrogates sur douze font mieux que la série réelle. Sur cibles à phases
aléatoires, M2 et M1P se valent — moyenne −0,046, indistinguable de zéro. Sur
la vraie cible, M2 est en retrait de 0,315.

> **Ce test ne tranche pas.** La distribution nulle est large (écart-type
> 0,305, tirée par un aberrant à −0,958) et douze surrogates donnent peu de
> puissance. L'écart observé est à 0,9 écart-type sous le centre ; dans l'autre
> sens la p unilatérale vaudrait 2/13 = 0,154, pas davantage significative.

**Verdict.** G4 exclut seulement que le gain de M2 se distingue du bruit
structurel **par le haut**. Il n'établit rien de plus.

---

## Ce que la seconde batterie établit

| | Établi |
|---|---|
| G1 | Le verdict n'est pas un artefact du découpage : 0 bloc sur 5 favorable à M2 contre le témoin apparié, sur toute l'étendue de l'archive. |
| G2 | Après correction d'un défaut de protocole, aucun modèle n'ajuste mieux le sens vrai du temps ; l'ampleur de l'asymétrie ne suit pas la présence de mémoire ORI-C. Aucun intervalle de confiance, effets de 1 à 6 %. |
| G3 | Le verdict ne dépend ni de la latitude ni de la saison : 0 convention sur 4 favorable à M2, étendue de 0,006. |
| G4 | Le gain de M2 ne se distingue pas de la distribution nulle par le haut. Puissance faible, aucune conclusion dans l'autre sens. |

## Ce que la seconde batterie ne change pas

Le verdict de la couche mémoire historique reste **négatif** : 1/5 contre M1,
0/5 contre M1P. Quatre angles conçus pour le renverser ne l'ont pas renversé,
et deux d'entre eux — G1 et G3 — le rendent plus solide qu'il ne l'était.

Deux défauts de protocole ont été trouvés et documentés : le critère de T4,
inapplicable à l'observation elle-même, et le masque de G2, confondant segment
et direction. Le second a été corrigé et **la correction a changé la réponse** ;
le premier n'a pas été converti en verdict.
