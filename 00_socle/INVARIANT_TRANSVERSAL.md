# Invariant transversal candidat ORI-C

## Statut

Ce document formalise un **candidat d'invariant transversal**. Il ne constitue
ni une preuve, ni une certification générale d'ORI-C. Le verdict courant reste :
**aucun invariant transversal général n'est validé**.

Le candidat reprend l'objet `INV-A` déjà présent dans l'audit transversal :

```text
Delta m -> Delta P_acc
```

Il précise ce que cette écriture signifie, ce qu'elle ne signifie pas et les
conditions nécessaires pour la tester sans confondre information historique,
trace physique, architecture et réponse.

## 1. Domaine d'applicabilité

L'invariant n'est pas posé sur « tout système ». Il n'est testable que dans le
domaine :

```text
D_ORI = { S : X, H, m, Theta, tau, P_acc et R sont opérationnalisables }
```

avec une provenance, un niveau d'analyse, une incertitude et un témoin déclarés.
Un système hors de ce domaine est `non_testable` pour cet invariant. Un résultat
négatif dans le domaine restreint la généralité du candidat mais ne doit pas être
requalifié après coup comme un cas « hors domaine » sans critère préenregistré.

## 2. Objets

Pour une instanciation donnée :

- `X` : état présent observable au niveau d'analyse déclaré ;
- `H` : histoire ou distribution d'histoires antérieures ;
- `m` : trace ou inscription héritée, distincte de l'étiquette `H` ;
- `Theta` : contraintes effectives maintenues ou explicitement modifiées ;
- `tau` : échelle temporelle déclarée par le protocole ;
- `tau_m` : persistance propre de `m`, uniquement lorsqu'elle est mesurée sous
  forçage final commun ou par une loi physique locale explicitement reliée à la
  trace ;
- `P_acc` : mesure locale du support des états ou réponses accessibles ;
- `R` : réponse observée ou calculée à l'horizon annoncé.

`tau`, un horizon d'observation et `tau_m` ne sont pas interchangeables.

## 3. Opérateur d'accessibilité

Le cadre introduit l'écriture locale :

```text
P_acc(t) = A_acc[X(t), m(t), Theta(t) ; T, C, epsilon]
```

avec :

```text
m(t) = I[H_<=t]
```

`I` est un opérateur d'inscription propre au domaine. `A_acc` n'est pas supposé
universel dans sa forme physique. Le candidat transversal porte sur une
propriété de dépendance, pas sur une équation commune à toutes les branches.

La nullité locale à tester est :

```text
H0 : A_acc[X,m,Theta] = A0[X,Theta]
```

contre :

```text
H1 : D_acc(P_acc^ctrl, P_acc^int) > epsilon_acc
```

lorsque l'intervention cible effectivement `m` et que `X` ainsi que les parties
non visées de l'architecture restent appariées.

## 4. Invariant candidat INV-A

La forme minimale retenue est :

```text
INV-A : une modification ciblée d'une trace m peut modifier P_acc à X et
        contraintes appariés, au-delà du bruit et du plus petit effet d'intérêt.
```

Sous une instanciation confirmatoire de mémoire :

```text
X_1 ~= X_2
A_1 ~= A_2
Theta_1 ~= Theta_2
m_1 != m_2
```

puis :

```text
do(m_1) != do(m_2)
```

et :

```text
D_acc(P_acc(X,m_1,Theta), P_acc(X,m_2,Theta)) > epsilon_acc.
```

Le signe de `Delta P_acc` n'est pas imposé universellement. Une ablation peut
contracter, élargir ou ne pas modifier le support. Si un protocole annonce une
direction avant analyse, son verdict reste attaché à cette direction gelée.

## 5. Trois classes de tests qui ne doivent jamais être fusionnées

### 5.1 Permutation de l'histoire

Une permutation de `H` teste une **non-réductibilité informationnelle**. Elle
peut établir qu'une information historique améliore la prédiction ou modifie un
proxy rétrospectif. Elle ne constitue pas une intervention physique sur `m`.

### 5.2 Ablation ou modification de la trace

Une intervention `do(m)` teste la contribution fonctionnelle de la trace si
`X`, `Theta` et les composantes non visées de `A` restent appariées. C'est la
classe directement pertinente pour `INV-A`.

### 5.3 Intervention architecturale

Une intervention `do(A)` teste le patron causal architecture -> réponse ou
architecture -> domaine accessible. Elle peut servir de prototype
méthodologique sans être comptée comme réplication de `INV-A`.

## 6. Non-réductibilité informationnelle

Une relation du type :

```text
I(R ; H | X) > 0
```

ou un gain prédictif :

```text
RMSE(R | X,H) < RMSE(R | X)
```

soutient l'idée que `H` contient une information pertinente au-delà de la
représentation présente `X`. Elle ne démontre pas à elle seule :

```text
H -> m -> P_acc -> R.
```

Cette chaîne exige une opérationnalisation distincte de `m`, sa persistance et
une intervention ou ablation capable de tester sa fonction.

## 7. Contraste d'accessibilité normalisé localement

Les `P_acc` des branches n'ont pas la même partition physique. Les valeurs
brutes ne sont donc pas mises sur une échelle universelle.

Pour une instanciation disposant d'un témoin local, on définit :

```text
Delta_acc = D_acc(P_acc^ctrl, P_acc^int)
```

et, si un plancher local `B_acc > 0` est défini indépendamment :

```text
C_acc = Delta_acc / B_acc.
```

`B_acc` peut être une enveloppe numérique, une distribution nulle, une
incertitude expérimentale ou un SESOI, mais sa nature doit être déclarée. Une
valeur de `C_acc` n'est interprétable qu'avec ce dénominateur.

La comparaison transversale autorisée porte d'abord sur la proposition :

```text
l'effet franchit-il son propre témoin local ?
```

La magnitude de `C_acc` entre domaines ne devient comparable qu'après validation
d'une construction commune du dénominateur. Aucune homogénéisation a posteriori
n'est admise.

## 8. Persistance tau_m

`tau_m` est la durée caractéristique pendant laquelle une trace `m` reste
mesurable ou fonctionnellement active sous les conditions finales déclarées.

Sont distingués :

- `tau_obs` : horizon d'observation ;
- `tau_relax` : temps de relaxation local d'une différence historique ;
- `tau_decay` : échelle d'une loi physique de décroissance ;
- `tau_m` : persistance de la trace candidate visée par le test.

Un horizon de 2 Myr, une date depuis CAI ou une durée expérimentale ne devient
pas automatiquement `tau_m`. La comparabilité de `tau_m` doit être auditée
séparément.

## 9. Unité de réplication

Les claims ne sont pas des réplications indépendantes lorsqu'ils proviennent du
même système ou du même jeu de données. Le comptage transversal porte sur :

```text
N_systemes_independants
```

et, lorsque le claim se veut interbranches :

```text
N_branches_independantes.
```

Deux claims vésiculaires issus du même système comptent donc pour un seul
système dans un test de généralité.

## 10. Porte confirmatoire future

Une validation transversale ne peut être décidée à partir des résultats déjà
ouverts. Pour toute nouvelle réplication, le protocole doit être gelé avant
ouverture des données de validation.

La porte de conception retenue pour une future revendication transversale exige
au minimum :

1. trois systèmes indépendants appartenant aux trois branches du programme ;
2. au moins deux systèmes empiriques, et aucune substitution d'un claim de
   modèle à une réplication empirique ;
3. un `m` distinct de `H` ;
4. un appariement de `X`, `Theta` et des composantes non visées de `A` ;
5. une intervention `do(m)` ou un effacement physique de la trace ;
6. un contraste `P_acc` défini avant analyse avec témoin local ;
7. un `tau_m` ou une justification explicite de son absence ;
8. une réponse `R` future ou un domaine accessible mesuré ;
9. un contrôle négatif capable de produire un faux positif si le protocole est
   mal spécifié ;
10. des critères de succès et de réfutation gelés avant les données réservées.

Cette liste définit une porte de test, pas un résultat actuel.

## 11. État courant

Le benchmark actuel renseigne cinq claims à sept champs pour quatre systèmes.
Ce nombre ne signifie pas cinq réplications.

- `C-VES-03` fournit actuellement le test le plus proche de `do(m) -> Delta
  P_acc`, mais le contraste `P_acc` gelé est négatif pour la direction attendue
  et son intervalle bootstrap inclut zéro ;
- `PID-ANT-01` fournit une non-réductibilité informationnelle et un `P_acc`
  rétrospectif, mais `m` n'est pas une trace physique isolée ;
- `C-AST-01` fournit une intervention architecturale forte au niveau modèle,
  pas une ablation de mémoire ;
- `GCQ-T09` fournit une trace physique dérivée et une partition d'accessibilité,
  sans intervention sur la trace ;
- `C-VES-02` fournit un support rétrospectif et une trace parentale directe,
  sans ablation `P_acc` propre à ce claim.

Le statut correct reste donc :

```text
INV-A = candidat opérationnalisé, comparaison exploratoire possible,
        validation transversale absente.
```

## 12. Réfutation et restriction de domaine

Une instanciation valide qui échoue à son critère gelé produit
`does_not_support`. Un défaut d'appariement, une puissance insuffisante ou une
trace non isolable produit `undetermined`.

Le candidat général est progressivement affaibli si des tests indépendants et
préenregistrés de `do(m)` convergent vers :

```text
Delta P_acc ~= 0 et Delta R ~= 0
```

au-delà des planchers de détection dans les systèmes déclarés admissibles. Les
échecs ne sont pas supprimés du benchmark et le domaine de validité ne peut pas
être réécrit après connaissance des résultats.
