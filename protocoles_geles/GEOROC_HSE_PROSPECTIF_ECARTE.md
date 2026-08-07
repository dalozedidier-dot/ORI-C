# Protocole prospectif GEOROC sur les éléments sidérophiles — écarté

**8 août 2026 · non gelé, délibérément**

Ce document enregistre un protocole qui **n'a pas été ouvert**, et pourquoi. Il
existe pour éviter que le travail soit refait, et pour garder la trace d'une
décision prise avant de voir le moindre résultat.

## Ce qui était envisagé

Un second test prospectif préenregistré, sur le modèle de `WP-EXO-PACC-2026` :
geler une bande de rapports Os/Ir mesurée sur le millésime GEOROC 2026-06, puis
vérifier, sur les échantillons apparaissant dans un millésime ultérieur, que
leurs rapports y tombent plus souvent que sous un appariement aléatoire.

L'idée tenait : la compilation GEOROC est vivante, elle publie **deux à trois
millésimes par an** — quatorze versions publiées à ce jour — et le corpus déjà
acquis porte 122 159 mesures sidérophiles sur 61 217 échantillons, avec un
rapport Os/Ir médian de 1,04 contre 1,07 chondritique.

## Pourquoi il est écarté

La question décisive n'est pas la taille du corpus, mais **sa vitesse de
croissance dans la dimension utile**. Elle a été mesurée en comparant les
millésimes 2025-12 et 2026-06, téléchargés tous les deux.

| lithologie | couples Os+Ir en v13 (2025-12) | en v14 (2026-06) | delta |
|---|---:|---:|---:|
| Péridotite | 544 | 544 | **+0** |
| Komatiite | 419 | 419 | **+0** |
| Harzburgite | 401 | 402 | **+1** |
| **total sur ces trois** | **1 364** | **1 365** | **+1** |

Ces trois lithologies portent environ un tiers des couples Os+Ir du corpus. En
extrapolant, la compilation entière gagne de l'ordre de **trois couples par
semestre, six par an**.

Le test binomial envisagé demanderait 28 événements pour 80 % de puissance, 40
pour 90 %. Au rythme mesuré, cela représente **environ cinq ans pour le premier
seuil et sept pour le second**.

Les échantillons, eux, augmentent bien — 82 nouvelles péridotites entre v13 et
v14 — mais presque aucun ne porte à la fois l'osmium et l'iridium. La croissance
de GEOROC est une croissance en analyses majeures, pas en éléments fortement
sidérophiles, qui restent rares et coûteux à mesurer.

## La règle appliquée

Geler ce protocole aurait produit un critère non franchissable sur tout horizon
raisonnable, c'est-à-dire exactement le défaut recensé dans
`ATTEIGNABILITE_DES_CRITERES_2026-08-08.md` pour la vallée des rayons et pour les
tests de signe du benchmark antibiotique.

**Un protocole dont on sait d'avance qu'il ne pourra pas conclure ne doit pas
être ouvert.** Le préenregistrer donnerait l'apparence d'une démarche
confirmatoire sans en avoir la substance, et son échec futur serait lu à tort
comme un résultat.

## Ce qui rouvrirait la question

- Une source qui publie des mesures HSE à un rythme soutenu, plutôt qu'une
  compilation généraliste où elles sont marginales.
- Un critère portant sur une grandeur qui, elle, croît vite dans GEOROC : les
  éléments majeurs, les terres rares, les rapports isotopiques courants.
- Un horizon assumé de cinq à sept ans, avec une lecture intermédiaire déclarée
  non décisive — recevable, mais il faut alors le dire dans le protocole.

`WP-EXO-PACC-2026` reste donc le seul test prospectif gelé du dossier. Sa
puissance attendue à vingt-quatre mois est de 0,98, pour un rythme mesuré de
trente-cinq événements par an.
