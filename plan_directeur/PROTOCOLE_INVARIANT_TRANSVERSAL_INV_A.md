# Protocole transversal candidat INV-A

## Statut

Protocole cadre de conception. Il est destiné à être gelé avant toute nouvelle
réplication confirmatoire. Il ne transforme pas les analyses rétrospectives
déjà ouvertes en préenregistrement.

Source conceptuelle : `00_socle/INVARIANT_TRANSVERSAL.md`.
Spécification machine :
`plan_directeur/campagne_centrale_2026_08_11/INVARIANT_TRANSVERSAL_INV_A.json`.

## Hypothèse

`INV-A` teste si une trace historique opérationnalisée `m` contribue à la
reconfiguration d'un domaine accessible :

```text
Delta m -> Delta P_acc
```

à état présent, contraintes et architecture non visée appariés.

## Nullité locale

```text
H0 : D_acc(P_acc^ctrl, P_acc^do(m)) <= epsilon_acc
```

La forme alternative, le sens unilatéral ou bilatéral et `epsilon_acc` doivent
être gelés avant ouverture des données de validation.

## Variables obligatoires

Chaque instanciation déclare :

```text
X, H, m, Theta, A_non_visee, tau_obs, tau_m, P_acc, R
```

ainsi que `l_ana`, l'horizon, le bruit, le SESOI, la provenance et la partition
de `P_acc`.

## Appariement

Une attribution à `m` exige :

```text
D_X(X_ctrl, X_int) <= delta_X
D_A(A_ctrl, A_int) <= delta_A
D_Theta(Theta_ctrl, Theta_int) <= delta_Theta
```

hors composante explicitement ciblée. Les distances et tolérances sont gelées.
Si l'une échoue, le verdict est `undetermined` pour `INV-A`.

## Classes de contrôle

Les classes suivantes sont enregistrées séparément :

1. `history_permutation` : test informationnel, jamais compté comme `do(m)` ;
2. `m_ablation` : intervention directe sur la trace candidate ;
3. `architecture_intervention` : test de `A`, jamais compté comme réplication
   de `INV-A` ;
4. `retrospective_physical_history` : mesure historique physique sans
   intervention ;
5. `negative_real_control` : contrôle négatif réel du protocole.

## Mesure locale

Le protocole définit une divergence locale `D_acc`. Si un plancher de référence
`B_acc` est disponible indépendamment :

```text
C_acc = D_acc / B_acc
```

Le rapport est utilisé pour savoir si l'effet dépasse son propre niveau de
référence. Les magnitudes de `C_acc` ne sont pas comparées entre domaines tant
que les dénominateurs n'ont pas une définition validée commune.

## Persistance

`tau_m` est mesuré séparément de `tau_obs`. Un protocole peut utiliser une loi de
décroissance ou un maintien à forçage final identique, mais il doit publier la
règle utilisée. Une date, une génération ou un horizon de simulation ne suffit
pas à déclarer `tau_m`.

## Critère local

Une instanciation est `supports` uniquement si :

- l'appariement est valide ;
- l'intervention cible `m` ;
- `P_acc` est non saturé ou possède une mesure de divergence informative ;
- l'effet franchit le SESOI et le bruit ;
- le contrôle négatif applicable ne donne pas le même effet ;
- la réponse `R` ou le domaine accessible change selon le critère gelé.

Elle est `does_not_support` si le protocole est valide mais le critère échoue.
Elle est `undetermined` si un maillon nécessaire n'est pas identifiable.

## Critère transversal futur

Aucune revendication transversale n'est autorisée tant que la porte suivante
n'est pas satisfaite sur des données de validation non utilisées pour concevoir
la règle :

- au moins trois systèmes indépendants ;
- les trois branches représentées ;
- au moins deux systèmes empiriques ;
- chaque système compté une seule fois, même s'il porte plusieurs claims ;
- même règle de décision et mêmes classes de contrôle ;
- aucune redéfinition a posteriori de `m`, `P_acc`, `D_acc`, `B_acc` ou du SESOI.

Le niveau de preuve final reste déterminé par les règles générales du dépôt.
