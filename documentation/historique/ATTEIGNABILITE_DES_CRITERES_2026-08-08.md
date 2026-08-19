# Atteignabilité des critères de décision — 8 août 2026

Un critère de décision peut échouer pour deux raisons très différentes : parce
que l'effet cherché n'existe pas, ou parce que le test employé ne peut pas le
détecter. Les deux produisent le même mot dans un rapport, et ils n'ont pas la
même valeur scientifique.

Ce document sépare les deux cas pour l'ensemble du dossier. Il ne rend aucun
verdict scientifique : il dit, critère par critère, si la question posée peut
recevoir une réponse.

Reproduction :

```bash
python scripts/auditer_atteignabilite_criteres.py
python plateforme/campagne_maximale_reelle/analyser_puissance_vallee.py
python plan_directeur/campagne_maximale_trois_branches/analyser_puissance_vivant.py
```

Résultats machine : `ATTEIGNABILITE_CRITERES.json`,
`plateforme/campagne_maximale_reelle/resultats_consolides/PUISSANCE_VALLEE_DES_RAYONS.json`,
`plan_directeur/campagne_maximale_trois_branches/resultats/POWER_VIVANT_LONGITUDINAL.json`.

---

## 1 · Balayage des tests discrets — rassurant

Un test à statistique discrète ne produit qu'un nombre fini de valeurs de `p`.
Un test de signe sur dix unités n'en produit que onze ; un test de permutation à
deux cents tirages ne descend pas sous 1/201. Si le seuil est plus exigeant que
la plus petite valeur atteignable, le critère est vide.

**22 critères discrets audités, alpha = 0,05 :**

| classe | nombre |
|---|---:|
| atteignable | **20** |
| atteignable mais fragile | 2 |
| inatteignable | **0** |

Aucun critère discret du dépôt n'est vicié par construction. C'est le résultat
important de ce balayage, et il vaut d'être dit : les tests de permutation à
2 000 et 40 320 tirages, les bootstrap à 20 000 tirages, tous ont la résolution
nécessaire.

### Les deux exceptions

Les deux tests de signe du benchmark antibiotique longitudinal, sur dix plis :

```
p minimal atteignable          0,00195
plis favorables requis         9 sur 10
```

Aucun résultat inférieur à 9/10 ne peut franchir 0,05. Le protocole exige donc
la quasi-unanimité, ce qui n'est pas une exigence de puissance mais un effet de
la taille choisie. Voir `PUISSANCE_VIVANT_2026-08-07.md` pour la puissance
correspondante, mesurée à 0,109 et 0,212. Ces deux valeurs sont des diagnostics de séparabilité entre plis corrélés, non des puissances expérimentales sur lignées : voir la correction en tête de `PUISSANCE_VIVANT_2026-08-07.md`.

---

## 2 · La vallée des rayons — critère inatteignable

Ce cas ne relève pas du balayage précédent : son atteignabilité dépend de la
distribution des données, pas de la discrétisation du test. Il fallait donc le
mesurer.

La mesure sous-échantillonne le catalogue réel et applique **les fonctions de
détection du script d'origine, importées telles quelles**, jamais réécrites.

| taille | tirages | succès | puissance |
|---:|---:|---:|---:|
| 200 | 40 | 0 | **0,00** |
| 400 | 40 | 0 | **0,00** |
| 800 | 40 | 0 | **0,00** |
| 1 600 | 40 | 0 | **0,00** |

Le critère « profondeur du creux au-delà de 95 % des permutations » n'est franchi
à **aucune taille disponible**.

### Pourquoi, précisément

Sur les 3 298 planètes retenues, la profondeur du creux dans la fenêtre
1,5–2,2 R⊕ vaut **−0,002420**. Elle est **négative** : dans cette fenêtre, la
densité au minimum local dépasse le plus faible de ses deux pics encadrants. Il
n'y a pas de creux à mesurer. Un critère qui exige qu'une profondeur négative
dépasse 95 % des permutations ne peut pas être satisfait.

### Conséquence

`plateforme/campagne_maximale_reelle/vallee_des_rayons.json` porte `reussi:
false`. **Ce verdict ne mesure pas l'absence de vallée des rayons.** Il constate
qu'un seuil inatteignable n'a pas été atteint. Il ne peut donc être cité ni comme
un résultat négatif sur l'inscription historique dans une population, ni comme
une réfutation de quoi que ce soit.

Le témoin méthodologique du même test, lui, reste valide et informatif : la
position du minimum ne dépend pas de la méthode de découverte, avec un écart de
0,0. Ce contrôle-là a bien fonctionné.

---

## 3 · Ce qu'il faut en faire

Trois critères du dossier sont concernés, tous dans la même situation : leur
échec n'est pas un résultat.

| critère | classe | ce qu'il faut |
|---|---|---|
| benchmark antibiotique, comparaison principale | fragile, 9/10 requis | redéfinir le nombre de plis avant toute nouvelle exécution |
| benchmark antibiotique, ablation de pente | fragile, 9/10 requis | idem |
| vallée des rayons | inatteignable | redéfinir la fenêtre et le seuil, ou abandonner le critère |

Dans les trois cas, la règle est la même et elle est déjà écrite dans
`protocoles_geles/` : **un seuil ne se redéfinit pas après lecture du résultat**.
Modifier ces critères impose donc d'ouvrir de nouveaux protocoles, avec de
nouveaux identifiants, et de laisser les anciens en l'état avec la mention
« critère inatteignable, résultat sans portée ».

## 4 · Portée de ce document

Le balayage couvre les tests discrets dont la taille figure dans les résultats.
Il ne couvre pas les critères dont l'atteignabilité dépend de la distribution,
qui demandent une mesure empirique au cas par cas — la vallée des rayons en est
l'exemple, et elle a été traitée séparément.

Il ne dit rien de la justesse des résultats qui, eux, franchissent leur seuil.
Le résultat D'Onofrio (p = 0,004975 sur 200 permutations) et les lignées de
vésicules (p = 0,00050 sur 2 000 permutations) sont dans la classe
« atteignable » : leur seuil était franchissable, et il a été franchi.
