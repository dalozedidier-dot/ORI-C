# ORI-C v0.9.7-research

Publication stable du snapshot scientifique du **12 août 2026**, postérieur à `v0.9.6-research`. Cette version publie l’opérationnalisation exécutable de l’invariant candidat `INV-A` et un second système avec intervention directe sur la trace `m`, sans reclasser les résultats antérieurs.

## Invariant transversal `INV-A`

Le benchmark transversal compte désormais **21 cas**. **6 claims** renseignent les sept champs `X, H, m, Θ, τ, P_acc, R`, pour **5 systèmes distincts**. La complétude des champs reste séparée du niveau de preuve.

Deux systèmes possèdent maintenant une intervention directe sur `m` :

- **Vésicules** : intervention empirique existante ; son contraste local `P_acc` reste publié tel quel et ne soutient pas la direction positive initialement testée.
- **EXO-DOM-01** : intervention causale interne au modèle climatique exoplanétaire réduit, classée `E4_modele`. `X`, `Θ` et l’architecture sont appariés par construction ; seules les traces lentes `regolith_fraction` et `carbon_memory` sont modifiées avant l’application des mêmes forçages futurs.

Pour `EXO-DOM-01` :

- `P_acc` contrôle : **0,91** ;
- `P_acc` sous `do(m)` : **0,87** ;
- `Delta P_acc` signé : **−0,04** ;
- `|Delta P_acc|` : **0,04** pour `epsilon_acc = 0,01` ;
- sham : **0** ;
- `tau_m` local : environ **7,89 Myr** pour la trace régolithe et **7,01 Myr** pour la mémoire carbone.

Le signe est une contraction et n’est pas universalisé. Le résultat soutient localement `do(m) -> Delta P_acc` **dans le modèle**, sans constituer une intervention sur le Système solaire réel ni une réplication empirique indépendante.

Le statut machine d’`INV-A` reste :

`candidate_operationalized_exploratory_not_validated`

Aucun invariant transversal général ORI-C n’est déclaré validé.

## Résultats antérieurs conservés

La publication ne réécrit aucun verdict de `v0.9.6-research` :

- astronomie N-corps : **13 / 15** ;
- paléoclimat M2 : **1 / 10**, non soutenu ;
- D’Onofrio : gain prédictif de l’histoire conservé sans conversion en `do(m)` physique ;
- vésicules : résultats spécialisés et contraste local `P_acc` conservés ;
- généalogie cosmique quantitative : pare-feu empirique maintenu avec **0 simulation**, **0 donnée synthétique** et **0 imputation comme preuve** ;
- PCMCI+ : reste exploratoire et ne modifie pas M2.

## Reproductibilité et intégrité

La campagne centrale possède désormais un workflow GitHub Actions dédié qui recalcule le test `EXO-DOM-01`, vérifie sa reproductibilité, exécute la campagne transversale et publie les résultats audités. Le manifeste interne de la couche mémoire inclut explicitement le bloc `do_m_trace/`.

Le snapshot `v0.9.7-research` contient **1 669 contenus manifestés**. Le registre de publication conserve **53 preuves** et **83 chiffres canoniques**. Le workflow de release reconstruit les sous-manifestes puis le manifeste racine en dernier avant de construire l’archive canonique et son SHA-256.
