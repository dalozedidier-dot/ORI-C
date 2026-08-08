# Recherche d'un jeu de vésicules indépendant — 8 août 2026

Objectif : trouver un jeu expérimental **indépendant** de Sokolskyi & Baum
permettant de répliquer les quatre composantes préenregistrées déjà soutenues sur
11 760 couples parent-descendant.

**Résultat : aucun jeu qualifiant trouvé.** Ce document consigne la recherche pour
qu'elle ne soit pas refaite à l'identique.

---

## Critère de rétention, fixé avant la recherche

Un jeu n'est retenu que s'il porte **simultanément** :

1. identifiant de lignée ou de population ;
2. génération ou cycle ;
3. relation parent → descendant explicite, carte de transfert ou identifiant parent ;
4. phénotype sélectionnable mesuré — turbidité, taille, fluorescence, fitness, survie ;
5. condition de sélection **et** son témoin de dérive ;
6. au moins une variable d'architecture — composition amphiphile, taille, nombre de cycles, alimentation ;
7. réplicats indépendants.

Un jeu qui n'a pas la relation parent-descendant explicite est rejeté d'emblée :
c'est la variable qui distingue une réponse de population d'une transmission.

## Candidats examinés et motifs de rejet

| candidat | motif de rejet |
|---|---|
| Dryad `10.5061/dryad.866t1g1qs` — *Evolution towards increasing complexity through functional diversification in a protocell model of the RNA world*, 2021 | **Données de simulation.** Le champ « methods » du dépôt le dit explicitement : « The data was collected through computer simulations using Python ». Aucune mesure. |
| Préprint bioRxiv — *Simple case of prebiotic evolution: vesicle populations can respond to selection for greater turbidity via emergent cooperative dynamics* | Selon toute vraisemblance le préprint de **Sokolskyi & Baum**, dont le jeu Dryad `10.5061/dryad.fbg79cp99` est déjà intégré. Ce n'est donc pas une réplication indépendante. |
| Dryad `10.5061/dryad.q83bk3jt7`, `10.5061/dryad.7wm37pvzf`, `10.5061/dryad.478t9` | Hors sujet : traits de paires de lignées, complexité multicellulaire, traçage de lignée par édition génomique. Aucun compartiment abiotique. |

## Cibles restant à vérifier

Elles n'ont pas encore donné de jeu de données accessible et vérifié :

- **Abil & Danelon**, évolution darwinienne d'ADN autoréplicatif en protocellule
  de synthèse — données NGS et liposomes. Vérifier si une filiation de
  compartiments est publiée, et non seulement une évolution de séquences.
- **Zambrano et al. 2024**, *JACS*, division pilotée chimiquement par bourgeonnement
  membranaire. Vérifier s'il existe une table par vésicule mère et fille.
- Coacervats et ARN, lignée Szostak et suivants, avec mesure de rétention sur
  plusieurs jours.

## Ce que cette recherche apprend

Le point dur n'est pas la rareté des expériences de protocellules : il y en a
beaucoup. C'est que **presque aucune ne publie la carte parent-descendant**. La
plupart mesurent une réponse de population — turbidité moyenne, taux de division,
survie agrégée — sans conserver quelle vésicule descend de laquelle.

Or c'est exactement cette carte qui fait la valeur du jeu Sokolskyi & Baum, et
c'est elle qui permet de distinguer une réponse à la sélection d'une transmission
héréditaire. Une recherche future gagnera à filtrer d'emblée sur la présence
d'une table de transfert, plutôt que sur les mots-clés « vesicle » ou « selection ».

## Conséquence pour la branche

Le résultat des vésicules reste **un résultat unique, non répliqué de manière
indépendante**. Il ne peut pas être présenté autrement tant qu'un second jeu
qualifiant n'a pas été trouvé. C'est aussi ce que dit `ETAT_DES_PREUVES.md`.
