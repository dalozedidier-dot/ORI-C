# Protocole transversal de causalité architecturale X/m/A

## Statut

Ce document définit un **patron expérimental prospectif** pour les trois branches ORI-C. Il ne fixe aucun verdict scientifique et ne modifie aucun résultat déjà certifié. Chaque instanciation doit recevoir son propre critère, ses propres variables, son témoin, son seuil, son plan de puissance et son empreinte avant l'ouverture du jeu tenu à l'écart ou avant l'intervention confirmatoire.

La couche astronomique fournit la première instanciation forte de cette logique dans un modèle physique réduit. `C-AST-01` reste classé `E4_modele`. Il ne devient ni une preuve empirique du Système solaire réel ni une validation des autres branches.

## 1. Variables du protocole

Le Codebook utilise `S/m/A`. Dans les protocoles expérimentaux qui emploient la notation historique `X/m/A`, **`X` désigne le même état présent que `S` au niveau d'analyse déclaré**. Aucune quatrième variable d'état n'est introduite.

- `X_t` ou `S_t` : état présent observable au niveau `ℓ_ana` déclaré.
- `m_t` : inscription ou trace héritée de l'histoire.
- `A_t` : architecture, c'est-à-dire les composants, relations, paramètres structurels et fonctions qui rendent la réponse possible.
- `F_{t+Δ}` : réponse future ou ensemble de futurs observés à l'horizon `Δ`.
- `P^kin(T,C,ε)` : domaine accessible lorsque l'horizon, les contraintes, les ressources et le seuil sont explicitement déclarés.

Le partage `X/m/A` est relatif au niveau de description. Un protocole qui ne publie pas `ℓ_ana`, le plancher de bruit et les règles d'appariement ne peut pas attribuer causalement un effet à `m` ou à `A`.

## 2. Patron causal général

La chaîne expérimentale commune est :

```text
architecture et état définis
        ↓
intervention explicite sur le levier visé
        ↓
réponse future mesurée
        ↓
comparaison à un témoin apparié
        ↓
séparation de l'effet et du bruit
        ↓
réplication
```

Pour une causalité **architecturale**, le levier est `A` :

```text
do(A_1) ≠ do(A_2)
```

Pour une causalité de **mémoire**, le levier doit être `m`, et non l'état présent :

```text
X_1 ≈ X_2
A_1 ≈ A_2
m_1 ≠ m_2
```

puis :

```text
do(m_1) ≠ do(m_2)
```

et l'on teste si la réponse ou le domaine accessible diffère :

```text
P(F_{t+Δ} | X, A, do(m_1)) ≠ P(F_{t+Δ} | X, A, do(m_2))
```

Une manipulation qui modifie simultanément `m`, `X` et `A` au-delà des tolérances préenregistrées ne permet pas d'attribuer l'effet à `m`. Elle peut rester informative sur le système, mais son verdict causal doit être plus limité.

## 3. Étapes obligatoires d'une instanciation confirmatoire

### 3.1 Définir le niveau de description

Le protocole publie avant exécution :

- `ℓ_ana` et les variables retenues ;
- les composantes de `X`, `m` et `A` ;
- l'horizon `T` ou `Δ` ;
- les contraintes et ressources `C` ;
- le seuil `ε` lorsque `Pacc` ou `P^kin` est utilisé ;
- le plancher de bruit numérique, expérimental ou observationnel ;
- le SESOI, c'est-à-dire le plus petit effet d'intérêt scientifique.

### 3.2 Vérifier l'appariement

Avant l'intervention, les groupes ou trajectoires doivent être appariés sur `X` et sur les composantes de `A` qui ne sont pas le levier du test. Les distances, tolérances et variables d'appariement sont gelées avant analyse.

Un témoin est déclaré **non apparié** si l'une de ces tolérances est franchie. Dans ce cas, le protocole ne produit pas de verdict causal, même si l'effet brut est important.

### 3.3 Intervenir sur un seul levier causal principal

L'intervention principale est écrite sous la forme `do(A)` ou `do(m)`. Le mécanisme physique de la manipulation est documenté. Une ablation, un effacement de trace, une restauration ou une substitution peut constituer l'intervention si elle cible effectivement le levier annoncé.

Pour `m`, la comparaison minimale est :

```text
m intacte / m modifiée ou effacée
```

à état présent et architecture appariés dans les tolérances gelées.

### 3.4 Utiliser des témoins capables de falsifier le résultat

Le protocole comprend, lorsque les données le permettent :

1. un modèle ou témoin d'état présent seul ;
2. un témoin historique nul, par exemple histoire permutée ou trace neutralisée ;
3. un témoin de **complexité appariée** ;
4. un contrôle négatif réel ;
5. une ablation du mécanisme ou de la trace ;
6. pour une série temporelle, les surrogats exigés par `AUTORITE_DES_DOCUMENTS.md`, appliqués symétriquement.

Un témoin plus simple que le modèle testé peut documenter un gain prédictif, mais il ne suffit pas à établir que ce gain provient de la mémoire ou de l'architecture annoncée.

### 3.5 Mesurer la réponse future

La réponse principale doit être définie avant exécution. Elle peut porter sur :

- une variable future `Y_{t+Δ}` ;
- une distribution de trajectoires ;
- une modification de `P^kin(T,C,ε)` ou d'une mesure `Pacc` non saturée ;
- un changement du diagnostic `D-H-L` ;
- la perte, l'apparition ou le coût de chemins de récupération.

Le simple constat que deux histoires diffèrent ne suffit pas. L'effet doit apparaître dans une réponse future ou dans le domaine des futurs accessibles.

### 3.6 Séparer l'effet du bruit

Le résultat principal doit franchir simultanément :

- le SESOI ;
- le plancher de bruit déclaré ;
- le témoin de complexité appariée ;
- les contrôles négatifs applicables.

Le rapport publie l'effet brut, l'incertitude, le rapport effet/bruit lorsque cette quantité est définie et le résultat de chaque témoin. Aucun contrôle absent n'est supposé réussi.

### 3.7 Répliquer

Un résultat local ne devient pas `E5` sans réplication indépendante réelle. Les folds de validation croisée, graines numériques et permutations ne sont pas des réplications indépendantes.

Une réplication admissible utilise un autre jeu, une autre population, un autre laboratoire ou une autre publication et conserve le même noyau opérationnel. `E6` exige que ce noyau survive dans plusieurs classes de systèmes **sans redéfinir après coup la variable causale ni la règle de succès**.

## 4. Règle de décision

Une instanciation peut produire trois états locaux :

- `supports` lorsque l'intervention ciblée franchit le critère principal, le témoin apparié, le plancher de bruit et les contrôles obligatoires ;
- `does_not_support` lorsque le protocole est valide et exécutable mais que le critère principal gelé échoue ;
- `undetermined` lorsque l'appariement échoue, que la puissance est insuffisante, qu'une variable manque, qu'un contrôle négatif produit un faux positif ou que la manipulation ne permet pas d'isoler le levier annoncé.

Ces états restent attachés à l'instanciation. Ils ne deviennent jamais automatiquement un verdict de branche ou un verdict général sur ORI-C.

## 5. Position des branches au 10 août 2026

| Branche ou protocole | Ce qui est déjà établi | Ce qui manque pour le patron X/m/A |
|---|---|---|
| Astronomie `C-AST-01` | intervention explicite sur des paramètres architecturaux, réponse orbitale, effet séparé des écarts numériques, reproductibilité | résultat limité au modèle réduit, niveau `E4_modele` ; aucune transposition automatique aux autres branches |
| Vésicules `C-VES-02` / `C-VES-03` | filiation mesurable et contraste d'ablation causal dans le protocole | définir explicitement `X`, `m` et `A`, vérifier leur appariement autour de l'ablation, puis obtenir une réplication indépendante |
| D'Onofrio `C-ANT-01` | l'histoire prédit au-delà de l'état présent et d'une histoire permutée, niveau `E2` | intervention ou ablation ciblée de `m`, puis réplication indépendante avec le même critère |
| Mémoire matérielle `C-MAT-MEM-05` | plusieurs relations partielles histoire-trace-réponse | une même famille doit relier histoire, trace mesurable, intervention ou effacement de la trace, réponse future et témoin apparié |
| Paléoclimat M2 | le témoin M1P de complexité égale a correctement testé la formulation | M2 est fermé dans cette formulation ; toute nouvelle architecture de mémoire doit être définie avant analyse et survivre au témoin apparié et aux contrôles négatifs réels |

## 6. C-AST-01 comme prototype méthodologique

La valeur transversale de `C-AST-01` est **méthodologique**, pas probatoire entre domaines. Il montre qu'un système complexe peut recevoir un test causal propre lorsque quatre conditions sont réunies : une architecture explicite, une intervention contrôlée, une réponse mesurable et une séparation quantitative entre effet et bruit.

Dans la campagne astronomique courante, 13 critères sur 15 sont réussis et le plus petit rapport entre effet interventionnel et écart numérique sélectionné vaut environ 4 964. Ces nombres restent attachés au modèle physique réduit et à ses interventions. Ils servent de référence de conception pour les autres branches, pas de seuil universel.

Les sources canoniques de cette instanciation sont `plan_directeur/campagne_maximale_trois_branches/resultats/systeme_solaire_robustesse.json` pour les métriques et `plateforme/campagne_maximale_reelle/CERTIFICATIONS_SPECIALISEES.json` pour le rattachement de `C-AST-01` à `E4_modele`.

La prochaine instanciation astronomique doit distinguer deux extensions. Premièrement, la spécificité de l'architecture des géantes : Uranus et Neptune sont déjà dans le témoin, il faut donc intervenir sur elles avec des perturbations comparables à celles appliquées à Jupiter/Saturne et comparer les déplacements des modes `g_i/s_i` et la réponse terrestre. Deuxièmement, le spin terrestre : une intervention « avec/sans Lune » n'est interprétable qu'après ajout d'un modèle d'obliquité/précession validé indépendamment. Le barycentre Terre-Lune actuel ne capture pas ce couple de spin.

## 7. Fichiers à produire pour chaque nouvelle instanciation

Avant l'exécution confirmatoire, chaque instanciation doit fournir :

- un protocole lisible par humain ;
- un registre machine des variables `X/m/A`, du levier et des témoins ;
- un `POWER_PLAN.json` lorsque la puissance statistique est pertinente ;
- un critère principal et un seuil gelés ;
- les règles d'appariement ;
- le contrôle négatif prévu ;
- l'empreinte SHA-256 du protocole ;
- la séparation explicite entre données d'exploration, d'ajustement et de validation.

Après exécution, le rapport doit publier les résultats positifs, négatifs et indéterminés. La certification scientifique reste assurée par les mécanismes fail-closed du dépôt et ne peut être créée par ce document seul.
