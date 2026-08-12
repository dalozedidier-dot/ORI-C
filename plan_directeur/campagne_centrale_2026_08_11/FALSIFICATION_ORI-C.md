# Falsification d'ORI-C

ORI-C ne doit pas être protégé par une redéfinition a posteriori de son domaine.
Les résultats négatifs valides restent attachés au benchmark et les unités de
réplication sont les **systèmes indépendants**, pas le nombre de claims.

## 1. Tests qui affaiblissent le cadre

Sur des protocoles préenregistrés et des systèmes indépendants, ORI-C est
affaibli si :

1. l'histoire n'apporte aucune information conditionnelle sur le futur après
   contrôle de l'état présent ;
2. les modèles état-seul égalent systématiquement les modèles historiques à
   complexité et validation identiques ;
3. des interventions ciblées `do(m)` sur une trace mesurée laissent
   systématiquement `P_acc` et la réponse `R` indiscernables du témoin, au-delà
   des planchers de détection ;
4. aucune définition locale non triviale de `P_acc` ne reste applicable dans
   au moins deux branches ;
5. les relations candidates `Delta m -> Delta P_acc` et
   `tau_m/tau_T -> force historique` ne se répliquent pas hors échantillon ;
6. les prédictions prospectives gelées restent au niveau des modèles nuls.

## 2. Trois classes de preuve séparées

Une permutation de `H`, une ablation de `m` et une intervention sur
l'architecture `A` ne sont pas interchangeables.

- `history_permutation` teste une dépendance informationnelle ;
- `m_ablation` teste directement `INV-A` si l'appariement est valide ;
- `architecture_intervention` teste le patron causal architectural et ne compte
  pas comme réplication de `do(m)`.

Un résultat positif dans une classe ne remplace pas un résultat négatif dans une
autre.

## 3. Résultat négatif local

Un résultat `does_not_support` provenant d'un protocole valide restreint le
candidat correspondant. Il ne réfute pas automatiquement tout ORI-C.
Inversement, il ne peut pas être retiré du domaine après connaissance du
résultat si les critères d'admission étaient satisfaits avant analyse.

Le contraste `P_acc` vésiculaire sous ablation est conservé dans cette logique :
la direction positive gelée n'est pas soutenue. Le résultat de réponse de
`C-VES-03` reste une propriété distincte et ne doit pas écraser ce résultat
négatif.

## 4. Affaiblissement transversal

Le candidat `INV-A` est fortement affaibli si plusieurs systèmes indépendants,
répartis entre les branches et testés avec `m` distinct de `H`, convergent vers :

```text
Delta P_acc ~= 0
Delta R ~= 0
```

avec une puissance suffisante et des contrôles capables de détecter le SESOI.
Le nombre de claims dérivés d'un même jeu ne multiplie jamais le nombre de
réplications.

## 5. Réfutation et domaine de validité

Une accumulation de résultats négatifs indépendants peut conduire soit au rejet
d'un invariant candidat, soit à une restriction de domaine si cette restriction
est définissable par des propriétés mesurables indépendantes des résultats.
Une restriction inventée après échec pour sauver l'hypothèse est interdite.

Aucun critère, seuil, `m`, `P_acc`, partition, contrôle ou règle de décision ne
peut être modifié après ouverture des données réservées.
