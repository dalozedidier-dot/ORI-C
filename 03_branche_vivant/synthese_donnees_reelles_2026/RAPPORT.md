# Comparaison des études biologiques réelles — 2026-08-15

## Résultat principal

Deux résultats rétrospectifs sont robustement positifs pour l'information
incrémentale d'une histoire ou d'un fond initial : D'Onofrio et Petrungaro
sous nitrofurantoïne. Ils ne testent toutefois pas la même définition de
l'histoire et ne constituent pas ensemble une réplication confirmatoire
transversale d'ORI-C.

Petrungaro–NIT apporte le résultat nouveau le plus net : 803 populations,
RMSE `X = 0,2855`, RMSE `X+m = 0,1948`, gain `31,76 %`, intervalle bootstrap
`[27,53 ; 36,05] %`, permutation du fond conditionnée par classes de
résistance initiale `p = 0,002` (499 permutations). Les chemins mutationnels
sont également plus similaires au sein d'un même fond que parmi des fonds
différents sous MEC, NIT et TMP; ce volet reste exploratoire.

## Résultats qui doivent rester négatifs ou indéterminés

- Card Ara+5 : le modèle historique est nettement pire que l'état seul.
- Wong & Seguin : gain `−5,69 %`, intervalle traversant zéro, `p = 0,578`.
- Lamrabet : 14/15 antibiotiques divergent encore entre lignées à 50 000
  générations, mais la persistance globale des profils donne `ρ = 0,565` et
  `p = 0,0765` lorsque les 12 lignées complètes sont permutées.
- Petrungaro MEC et TMP : les gains ponctuels sont respectivement `3,79 %` et
  `0,98 %`, mais les intervalles bootstrap traversent zéro.

## Card et Nader

L'archive Card complète contient exactement la table Ara+5 déjà exploitée;
elle n'est pas réanalysée. Trois tables structurées supplémentaires sont
inventoriées et la table MIC générale reçoit seulement une synthèse
descriptive, car les répétitions de plaque ne sont pas des lignées évolutives
indépendantes. L'archive de 319 photographies (296,8 Mo) n'est pas importée :
elle n'apporte aucune nouvelle table structurée.

Nader fournit 1 558 tailles individuelles observées, médiane `374,24 nm` et
intervalle empirique 2,5–97,5 % `[204,98 ; 1 135,59] nm`, plus les
chromatogrammes quantitatifs. Ces mesures calibrent le système 2:1 acide
décanoïque:décanol; elles ne remplacent pas l'expérience
`control / do(m) / sham` et ne sont pas directement comparables à une cible
DLS Z-average après extrusion à 100 nm.

La table canonique [COMPARAISON_ETUDES_REELLES.csv](COMPARAISON_ETUDES_REELLES.csv)
contient l'unité, `X`, l'histoire ou `m`, `Θ`, `R`, l'effectif, l'effet,
l'incertitude, la permutation et le verdict de chaque analyse.
