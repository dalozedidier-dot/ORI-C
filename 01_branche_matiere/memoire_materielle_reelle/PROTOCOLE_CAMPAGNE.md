# Campagne « mémoire matérielle réelle » — protocole gelé

**Gelé le 8 août 2026, avant inspection du moindre jeu de données.** Cet ordre
n'est pas une formalité. Écrire les critères après avoir regardé ce que les
données permettent produit des critères taillés sur mesure, donc non
confirmatoires. Les empreintes SHA-256 de ce document, du schéma d'extraction et
du filtre d'admission sont scellées dans `GEL_CAMPAGNE.json`.

## Ce que cette campagne apporte que les autres ne peuvent pas

La couche mémoire historique plafonne au **niveau 4** de la hiérarchie des
témoins : un surrogat IAAFT reste un artefact statistique, et la journée du
8 août 2026 a montré qu'un témoin de niveau 4 sur une statistique inadéquate ne
produit rien. Aucun raffinement de surrogat ne changera cela.

Une campagne matière atteint le **niveau 6**. Démagnétiser un échantillon,
recuire un acier écroui, effacer une histoire thermique : ce sont des ablations
**physiques**, pas des permutations. Le témoin n'est pas une série calculée, c'est
un autre échantillon réel ayant subi un traitement réel. `C-MAT-MEM-03` est donc
structurellement plus fort que tout ce que la branche Système solaire pourra
produire, quel que soit son raffinement statistique.

Le second apport est la **transversalité**. Un résultat unique sur un acier reste
un résultat sur un acier. Le même schéma relationnel soutenu indépendamment sur
le magnétisme, la plasticité et une transition de phase, avec des mécanismes
matériels sans rapport, est un fait d'un autre ordre.

## Schéma relationnel testé

Un seul, identique pour toutes les familles physiques :

> **histoire appliquée → trace physique persistante mesurée → réponse ultérieure
> modifiée sous stimulus identique**

| étape | magnétisme | plasticité | verre | métastabilité |
|---|---|---|---|---|
| histoire | champ et cycles antérieurs | déformation antérieure | recuit sous `Tg` | traitement thermique |
| trace | aimantation, domaines | dislocations, écrouissage | structure figée, enthalpie | fractions de phase, paramètres de maille |
| état persistant | rémanence, coercivité | seuil d'écoulement | état structural | phase métastable |
| réponse | boucle B-H suivante, pertes | courbe σ-ε, ratcheting | cinétique de relaxation | transformation ultérieure |

## Filtre d'admission

Non négociable, et vérifié par `admettre_jeu.py` avant toute extraction. Un jeu
n'entre dans la campagne que s'il remplit **les cinq** conditions :

1. **au moins deux histoires distinctes**, documentées par leurs paramètres, pas
   déduites ;
2. **une trace physique persistante mesurée**, distincte de la réponse ;
3. **une réponse ultérieure mesurée sous condition finale comparable** entre les
   histoires ;
4. **des unités expérimentales indépendantes identifiables** — des échantillons,
   pas des points d'une même courbe ;
5. **un témoin réel disponible** — histoire nulle, échantillon de référence, ou
   ablation.

Un jeu qui ne contient qu'une courbe d'hystérésis isolée, aussi propre soit-elle,
sans possibilité de reconstruire les trois étapes, est conservé comme **source
documentaire** et n'entre dans aucun compteur de preuve.

**Aucune imputation.** Si un champ obligatoire du schéma d'extraction manque, le
jeu est écarté ou le critère concerné est déclaré non testable. On ne comble pas.

## Les cinq critères

### C-MAT-MEM-01 — Existence de mémoire matérielle

Sous stimulus final identique, deux systèmes ayant subi des histoires différentes
présentent une **réponse ultérieure différente**, accompagnée d'une **trace
physique persistante mesurée et cohérente avec cette différence de réponse**.

La cohérence entre trace et réponse est exigée, pas seulement leur coexistence.
Deux quantités qui diffèrent toutes deux entre histoires sans lien établi ne
démontrent rien : il faut que la trace ordonne les réponses.

*Témoin.* Échantillons appariés, histoires assignées expérimentalement, stimulus
final identique. **Niveau 6.**

*Statistique.* Différence de réponse entre histoires, testée par sign-flip exact
sur les paires ou permutation des étiquettes d'histoire. Cohérence trace-réponse
testée par corrélation de rang entre l'ordre de la trace et l'ordre de la réponse,
contre permutation des appariements.

### C-MAT-MEM-02 — Persistance

La différence de réponse reste détectable après un délai, un nombre de cycles ou
une relaxation contrôlée, **fixés avant exécution**.

*Témoin.* Niveau 6 si le délai est expérimentalement imposé. Si la persistance
n'est lisible que sur une série temporelle continue, le témoin descend au
**niveau 4** et un surrogat IAAFT devient obligatoire, appliqué de façon
**symétrique** — statistique recalculée entièrement sur le surrogat.

### C-MAT-MEM-03 — Ablation de l'histoire

Lorsque l'histoire est effacée par une opération physique — démagnétisation,
recuit de restauration, remise en solution — la différence de réponse disparaît ou
chute sous un seuil préenregistré.

*Témoin.* **Niveau 6, le plus fort de la hiérarchie.** C'est le critère central de
la campagne : il ne se contourne par aucun artifice statistique et ne se simule
pas.

### C-MAT-MEM-04 — Spécificité

Le même stimulus appliqué **sans** l'histoire préalable ne produit pas la même
modification persistante. La trace est attribuable à l'histoire, non au stimulus
de mesure.

*Témoin.* Niveau 6, bras sans histoire du même jeu.

### C-MAT-MEM-05 — Transversalité, critère de campagne

Le schéma `histoire → trace physique persistante → réponse ultérieure modifiée`
est soutenu **indépendamment dans au moins trois familles physiques distinctes,
avec des mécanismes matériels différents**.

Ce critère ne s'applique à aucun jeu pris isolément. Il ne se calcule qu'après
verdicts locaux, et deux jeux relevant du même mécanisme — deux aciers écrouis,
par exemple — comptent pour une seule famille.

## États de verdict autorisés

Par jeu et par critère, quatre états et pas un de plus :

| état | signification |
|---|---|
| `soutient` | critère atteint contre son témoin déclaré |
| `ne_soutient_pas` | critère exécuté, non atteint |
| `non_testable_avec_ce_jeu` | le jeu ne contient pas le bras nécessaire |
| `indetermine_par_atteignabilite` | le critère ne peut pas descendre sous alpha avec les unités disponibles |

**Un jeu n'a pas besoin de réussir les quatre critères locaux pour être utile.**
Un jeu magnétique sans expérience de démagnétisation donne légitimement :

```
C-MAT-MEM-01 : soutient
C-MAT-MEM-02 : soutient
C-MAT-MEM-03 : non_testable_avec_ce_jeu
C-MAT-MEM-04 : soutient
```

Aucun remplissage, aucune simulation en substitution d'une expérience absente.
`non_testable_avec_ce_jeu` est un état honorable ; une valeur inventée ne l'est
pas.

## Atteignabilité, déclarée avant exécution

Le nombre d'unités expérimentales indépendantes borne ce qui est démontrable.
Pour un sign-flip exact sur *n* paires, la plus petite valeur de p vaut 2/2ⁿ ; pour
une permutation à *N* tirages, 1/(N+1). L'estimateur de p est **(1 + k)/(1 + N)** :
une valeur exactement nulle est impossible avec un tirage fini.

| paires *n* | p minimal | verdict à alpha = 0,05 |
|---:|---:|---|
| 4 | 0,125 | inatteignable |
| 5 | 0,0625 | inatteignable |
| 6 | 0,03125 | atteignable |
| 8 | 7,8 × 10⁻³ | atteignable |
| 10 | 2,0 × 10⁻³ | atteignable |

**Un jeu offrant moins de six paires indépendantes ne peut pas produire de verdict
positif à alpha = 0,05.** Ce constat se fait à l'admission, pas après l'analyse.

## Contrôle négatif obligatoire

Hérité de la rétractation de `WP-CLIM-MEM-2026-B`. Avant tout verdict, la même
statistique est appliquée à une grandeur du **même jeu** dont on sait par la
physique qu'elle ne porte pas l'histoire testée — une lecture d'instrument
indépendante de l'échantillon, une propriété connue pour être insensible au
traitement, une grandeur de calibration. Si ce contrôle négatif obtient un verdict
positif, la statistique est inadéquate et aucun verdict n'est rendu.

C'est ce contrôle qui a révélé qu'un test accordait `soutient` à l'obliquité
terrestre avec un gain supérieur à celui de la cible. Il n'est pas optionnel.

## Ordre d'exécution contraignant

1. geler ce protocole et son schéma — **fait, ce document** ;
2. inspecter chaque jeu candidat contre le filtre d'admission, sans rien extraire ;
3. pour les jeux admis, extraire les champs du schéma sans imputation ;
4. déclarer l'atteignabilité et le contrôle négatif de chaque critère ;
5. exécuter, puis inscrire les verdicts dans un registre unique.

Intégrer d'abord et chercher ensuite ce que la donnée permet de tester produit des
résultats non préenregistrés, donc non confirmatoires.

## Statut épistémique

Les jeux visés sont **expérimentaux et primaires** : des mesures d'instrument sur
des échantillons réels. C'est la différence essentielle avec la couche mémoire
historique, dont les sources sont des reconstructions de modèle. Un verdict rendu
ici, s'il est rendu, sera une preuve empirique primaire — statut qu'aucun résultat
paléoclimatique du dossier ne peut atteindre.

Aucun calcul DFT, aucune sortie de simulation n'entre dans les tests. Lorsqu'un
jeu mêle mesures et calculs, les seconds sont séparés et exclus, conformément à
`EMPIRICAL_POLICY.json`.
