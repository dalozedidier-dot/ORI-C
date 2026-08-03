# Erratum — article de la branche 2

**Ce document prime sur le PDF qu'il accompagne.**

L'article `Architecture_historique_du_Systeme_solaire_ORI-C.pdf` a été rédigé
avant l'exécution des tests de la couche mémoire historique. Il présente donc
encore ces tests comme ouverts, futurs ou prioritaires. Ils ont depuis été
exécutés, puis corrigés, et le résultat est négatif.

Tant que le PDF n'est pas régénéré, deux lecteurs peuvent tirer des conclusions
opposées selon le fichier consulté. Cet erratum lève l'ambiguïté.

## Passages à corriger

### §10.1, ligne « Réponse terrestre »

Le tableau des plans de preuve porte « Non testé ici / Étape ouverte ».

**Remplacer par :** *testé et non soutenu. Face à un témoin de complexité
égale, le modèle à mémoire explicite ne surpasse pas le modèle classique sur
LR04 hors échantillon.*

### §11.11, condition de consolidation ou de réfutation

L'article écrit : « ORI-C gagnerait un appui spécifique seulement si M2
améliore de manière stable les prédictions hors échantillon **face à M1** ».

Cette condition est mal spécifiée : M1 possède six paramètres et M2 huit. Un
avantage peut venir des degrés de liberté supplémentaires plutôt que d'une
mémoire.

**Remplacer par :** *face à un témoin possédant le même nombre de paramètres et
la même structure de constantes de temps, mais dont l'état lent filtre le
forçage externe au lieu d'enregistrer la réponse passée.*

Sous cette condition corrigée, le résultat est négatif.

### §12.5, test exoplanétaire propre à ORI-C

La condition écrite — « si la variable ORI-C améliore la prédiction de cette
dépendance au chemin face au même modèle sans cette variable » — est nécessaire
mais insuffisante.

**Ajouter :** *(a) l'écart doit survivre à un palier final long devant toutes
les constantes de temps du modèle ; (b) le forçage final doit se situer dans
une région où le modèle possède plus d'un attracteur.*

Sous ces conditions, le résultat actuel est négatif, et la cause est
identifiée : le palier est plus court que la mémoire testée et le forçage final
tombe dans un régime à attracteur unique.

### §10.5 et §14, conclusion de statut

La phrase sur la démonstration à venir reste exacte comme programme.

**Ajouter :** *une première exécution de ce test, sur LR04 et avec un témoin de
complexité égale, ne soutient pas la déclinaison paléoclimatique du cadre.*

## Formulation de remplacement, en un paragraphe

> La réponse climatique dépendante de l'histoire a été testée dans deux modèles
> réduits. La déclinaison paléoclimatique ne surpasse pas un modèle de
> complexité équivalente et subit une perte hors échantillon importante. La
> dépendance au chemin exoplanétaire est retrouvée transitoirement, mais
> s'efface sur un plateau commun suffisamment long.

## Chiffres à jour

| Quantité | Valeur |
|---|---:|
| Critères préenregistrés réussis, contre M1 | 1 / 5 |
| Critères préenregistrés réussis, contre M1P | 0 / 5 |
| Gain de RMSE hors échantillon, contre M1P | −0,316 |
| Intervalle de confiance à 95 % | [−0,389 ; −0,251] |
| Temps d'e-folding de l'écart exoplanétaire | 7,0 Ma |

## Ce que l'erratum ne touche pas

**La couche astronomique n'est pas concernée.** Les 25 calculs N-corps, l'accord
avec JPL Horizons DE441 et La2010, le spectre sur 20 Ma et les six
interventions architecturales restent tels quels, avec 13 critères réussis sur
15. Aucun de ces critères ne dépend de la couche climatique.

**Les branches 1 et 3 ne sont pas concernées.** Elles portent sur d'autres
objets et n'ont pas subi ce test.

## Sources

- `../couche_memoire_historique/RAPPORT_CORRIGE.md` — document maître
- `../couche_memoire_historique/STRESS_REPORT.md` — tableaux complets
- `../couche_memoire_historique/REPORT.md` — verdict régénéré à chaque exécution
- `../../ETAT_DES_PREUVES.md` — tableau transversal
