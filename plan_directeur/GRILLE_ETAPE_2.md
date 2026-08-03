# Grille universelle de l'Étape 2, appliquée mécanisme par mécanisme

Le plan directeur impose trente familles de tests à **chaque** mécanisme. Le
dossier en possède deux qui soient assez développés pour subir la grille
entière :

- **CHM** — le test interventionnel du chémostat, socle
- **MEM** — la couche mémoire historique, M2 et sa famille, branche 2

Chaque case porte un état et, quand elle est faite, la référence du fichier
généré qui l'atteste. Les cases vides ne sont pas des oublis : elles sont
comptées.

Légende : **fait** · *partiel* · — non fait · **N/A** sans objet ici

| # | Famille de tests | CHM | MEM |
|---:|---|---|---|
| 1 | cohérence mathématique | **fait** — théorèmes symboliques, `rapport_exhaustif.txt` C1-C2 | *partiel* — pas de preuve formelle, modèle numérique |
| 2 | cohérence dimensionnelle | **fait** — grandeurs homogènes vérifiées analytiquement | *partiel* — séries standardisées, unités absorbées |
| 3 | identifiabilité | **N/A** — paramètres imposés, non ajustés | **fait** — WP-C6.8 : M2 **non identifiable**, dispersion 1,233 |
| 4 | sensibilité aux paramètres | **fait** — WP-S2 D, 200 jeux × 3 structures | *partiel* — bornes larges, pas de balayage systématique |
| 5 | robustesse aux conditions initiales | **fait** — bassin global, `rapport_exhaustif.txt` D02 | **fait** — 150 états initiaux, `RAPPORT_PROSPECTIF.md` §1 |
| 6 | convergence numérique | **fait** — certification par intervalles, F01 | **fait** — vérification bit à bit du noyau compilé |
| 7 | comparaison à plusieurs algorithmes | *partiel* — LSODA et intégration directe | *partiel* — évolution différentielle, quatre graines |
| 8 | contrôle positif | **fait** — cas où l'effet doit apparaître | **fait** — M2 sur données synthétiques du modèle |
| 9 | contrôle négatif | **fait** — ablation `beta = 0` | **fait** — M0, réponse instantanée |
| 10 | témoin instantané | **fait** — équilibre sans perte | **fait** — M0 |
| 11 | témoin historique | **fait** — trajectoire complète | **fait** — M2 |
| 12 | **témoin de complexité égale** | **fait** — WP-S2, structures appariées | **fait** — M1P ; verdict 0/5 |
| 13 | ablation du mécanisme | **fait** — WP-S2 B, neuf variantes | **fait** — WP-C3, ablation par mécanisme |
| 14 | permutation de l'ordre des événements | **fait** — WP-S2, pertes pulsées et corrélées | **fait** — G2, renversement temporel |
| 15 | même état final par histoires différentes | **fait** — `rapport_exhaustif.txt` D01 | **fait** — test exoplanétaire à histoires contrôlées |
| 16 | retrait de la contrainte | **fait** — retour à `l = 0` | *partiel* — palier long, `RAPPORT_CORRIGE.md` |
| 17 | durée de relaxation | **fait** — E01, ralentissement critique | **fait** — `n_eff` et constantes de temps publiées |
| 18 | hystérésis aller-retour | *partiel* — monotonie mesurée, pas de cycle complet | — |
| 19 | perte de composants ou de chemins | — | — |
| 20 | estimation de `Pth` | — | — |
| 21 | estimation de `Pacc(T, C, ε)` | — | — |
| 22 | prédiction hors échantillon | **N/A** — modèle analytique | **fait** — T1, T2, G1, G3, WP-C4 |
| 23 | réplication sur une autre base | — données absentes | *partiel* — LR04 seule ; T2 sur l'étendue complète |
| 24 | réplication par un autre code | *partiel* — script régénéré indépendamment | — |
| 25 | réplication par une autre équipe | — humain | — humain |
| 26 | test adversarial | **fait** — WP-S2 D cherche la non-monotonie | **fait** — G1 à G4 conçus pour renverser le verdict |
| 27 | cas où ORI-C et le concurrent concordent | — | **fait** — WP-C4 : neuf familles sur onze à 5 % près |
| 28 | cas où ils divergent | — | **fait** — WP-C4 : `persistance` bat M2 de 16 % |
| 29 | correction pour comparaisons multiples | — | — **non faite**, voir ci-dessous |
| 30 | publication des positifs, négatifs et non concluants | **fait** | **fait** — sept réfutations publiées |

## Compte

| | CHM | MEM | Total |
|---|---:|---:|---:|
| **fait** | 15 | 15 | **30** |
| *partiel* | 4 | 6 | 10 |
| non fait | 8 | 8 | 16 |
| **N/A** | 2 | 1 | 3 |
| | 29 | 30 | 59 |

**Trente cases sur cinquante-neuf sont faites, dix partielles, seize vides.**

## Les quatre trous qui comptent

**Lignes 19, 20 et 21 — `Pth`, `Pacc` et les pertes de chemins — sont vides
pour les deux mécanismes.** Ce sont pourtant les notions les plus propres à
ORI-C, celles que le §13.3 déclare centrales. Le banc synthétique du socle les
mesure sur des systèmes construits pour cela, mais **aucun mécanisme réel du
dossier n'en porte d'estimation**. C'est le manque le plus significatif de la
grille.

**Ligne 29 — correction pour comparaisons multiples — n'est faite nulle part,
et cela affaiblit des conclusions déjà publiées.** La couche mémoire a subi
neuf tests réels, quinze critères discriminants, onze familles de modèles. Les
p-values et intervalles cités ne portent aucune correction. Le verdict global
reste négatif et une correction ne peut que le renforcer — mais les résultats
individuels marginaux, comme le `p = 0,090` du plus long chemin de la carte ou
le `p = 0,154` de G4, ne survivraient probablement pas à une correction.

**Ligne 25 — réplication par une autre équipe — est vide pour les deux.** Le
plan en fait une condition de son seuil scientifique, §XIV.10.

**Ligne 18 — hystérésis aller-retour — n'est complète nulle part.** Le WP-S2
mesure la monotonie de `P*` en fonction de la perte, ce qui n'est pas un cycle
aller-retour. Pour la couche mémoire, rien.

## Ce que la grille apprend sur le dossier

Le dossier est **fort sur les témoins et les ablations** — lignes 8 à 15, où
les deux mécanismes sont complets. C'est le résultat de la correction du
verdict de la couche mémoire, qui a imposé le témoin de complexité égale
partout.

Il est **faible sur les domaines de possibles** — lignes 19 à 21 — c'est-à-dire
précisément là où ORI-C prétend apporter quelque chose que les cadres existants
n'ont pas.

Et il est **muet sur la réplication externe** — lignes 23 à 25 — ce qui est
attendu pour un dossier produit par une seule personne sur une seule machine,
mais qui plafonne définitivement le statut atteignable.
