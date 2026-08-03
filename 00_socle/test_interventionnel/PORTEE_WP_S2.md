# Portée du test interventionnel — WP-S2

**Statut : exploratoire.** Aucun critère n'était préenregistré. Le test
interventionnel du dossier réussit **11/11 dans son modèle réduit** ; ce banc
mesure jusqu'où le mécanisme survit hors de ce modèle.

```bash
cd 00_socle/test_interventionnel/scripts
python portee_wp_s2.py
```

## Deux exécutions

La première est conservée dans `resultats_portee/portee_wp_s2_execution_1.json`.
Elle portait **trois défauts de banc**, tous corrigés, et deux d'entre eux
changeaient les conclusions.

| Défaut | Effet | Correction |
|---|---|---|
| Bruit environnemental coloré multiplié par √pas au lieu du pas | ~35 fois trop fort ; extinction même à perte nulle, survie 0 % partout | la perturbation est un écart de taux, elle entre dans la dérive |
| Espèce 2 de la variante « compétition » plus performante que l'espèce 1 | l'espèce testée disparaissait à toute perte ; la variante ne testait rien | espèce 2 rendue moins efficace, `μ_max` 0,70 et `K_s` 1,4 |
| Critère de non-monotonie absolu à 10⁻³ | retenait 9 cas dont les remontées valaient 0,013 % à 0,17 % de l'amplitude — du bruit d'intégration | critère relatif, ≥ 1 % de l'amplitude |

## A. Six cinétiques — le mécanisme survit

| Cinétique | Seuil de lavage | `P*` décroît avec `l` | `P*` à `l = 0` |
|---|---:|---|---:|
| Monod | 0,85 | oui | 49,74 |
| Masse-action | ≥ 1,20 | oui | 49,75 |
| Haldane | 0,71 | oui | 49,74 |
| **Hill** (n = 2) | 0,94 | oui | 48,85 |
| **Contois** | 0,94 | oui | 39,58 |
| **Droop** | 0,70 | oui | 49,92 |

Les trois cinétiques absentes du dossier — Hill, Contois, Droop — conservent
les deux propriétés dont dépend l'affirmation causale : un seuil de lavage
existe, et la biomasse d'équilibre décroît strictement avec la perte.

Le seuil de la masse-action est **censuré au bord de la grille** (1,20) : il
est supérieur, non déterminé.

## B. Neuf extensions structurelles — une seule brise la monotonie

| Variante | Seuil | `P` à `l = 0` | Remontée relative | Non monotone |
|---|---:|---:|---:|---|
| base | 0,86 | 49,74 | −0,002 | non |
| seconde ressource | 0,67 | 32,76 | −0,003 | non |
| compétition | 0,36 | 49,74 | −0,004 | non |
| cross-feeding | 0,86 | 59,90 | −0,002 | non |
| prédation | 0,86 | 49,74 | −0,002 | non |
| **retard** | 0,86 | 49,74 | **+0,071** | **oui** |
| spatial | ≥ 1,20 | 49,74 | −0,001 | non |
| perte dépendante de la densité | 0,86 | 49,74 | −0,001 | non |
| perte corrélée à la ressource | 1,03 | 49,74 | −0,010 | non |

Aux paramètres de référence, **seule la variante à mémoire physiologique
retardée** produit un domaine où augmenter la perte augmente la biomasse
finale. La remontée vaut 7,1 % de l'amplitude de la courbe — bien au-dessus du
bruit d'intégration.

## C. Bruit — le seuil cesse d'être net

Fraction de survie sur 40 répétitions, intégration d'Euler-Maruyama.

| Perte `l` | 0,0 | 0,2 | 0,4 | 0,6 | 0,8 |
|---|---:|---:|---:|---:|---:|
| Bruit démographique | 1,00 | 1,00 | 1,00 | 1,00 | 0,95 |
| **Bruit environnemental coloré** | 1,00 | 1,00 | 1,00 | 0,95 | **0,40** |

Le bruit corrélé dans le temps est **nettement plus destructeur** que le bruit
démographique à amplitude égale : 40 % de survie contre 95 % au même niveau de
perte. Le test déterministe 11/11 ne dit rien de ce régime, où la survie
devient une probabilité et non un seuil.

## D. Item 14 — la prédiction contre-intuitive a un domaine de validité

C'est le seul item du WP-S2 qui teste une affirmation **propre** à ORI-C :
existe-t-il un domaine où *réduire* une perte *diminue* la persistance ?

Balayage de 200 jeux de paramètres × 3 structures = 600 configurations,
critère relatif ≥ 1 %.

| Structure | Cas non monotones |
|---|---:|
| **Compétition** | **9** sur 200 |
| Prédation | 1 sur 200 |
| Cross-feeding | 0 sur 200 |

Plus fortes remontées relatives observées : **14,5 %**, 4,6 %, 1,7 %.

**Réponse : oui, mais rarement et par effet indirect.** Le mécanisme est une
libération compétitive — réduire la perte de l'espèce 1 la laisse exclure
l'espèce 2, ce qui déstabilise l'équilibre à deux espèces et diminue la
biomasse finale. Ajouté à la variante `retard`, cela fait **deux structures
distinctes** où la prédiction contre-intuitive est vérifiée.

### Ce que cela vaut, et ce que cela ne vaut pas

**Ce que cela établit.** L'affirmation « réduire une perte peut diminuer la
persistance » n'est pas vide. Elle a un domaine de validité identifié, dans
deux structures, et ce domaine ne contient pas le chémostat à deux variables
sur lequel porte le résultat 11/11.

**Ce que cela n'établit pas.** Le résultat est **dans un modèle**, pas dans des
données. Il est **rare** : 10 configurations sur 600, soit 1,7 %. Aucun
critère n'était préenregistré, et le seuil de 1 % a été fixé après avoir
constaté que le seuil absolu retenait du bruit. Rien ici ne dit qu'un système
biologique réel se trouve dans ce domaine.

Le WP-S2 demande encore, aux items 16 à 19, de tester le seuil de lavage sur
des **données de chémostat publiées**, de concevoir une expérience à
intervention préenregistrée, et de répliquer sur deux espèces et deux milieux.
Rien de cela n'est fait, et rien de cela n'est faisable sans laboratoire ni
données externes.

## Item 20 — séparer les trois niveaux

Le plan demande de distinguer explicitement trois choses que le résultat 11/11
pouvait laisser confondre.

| Niveau | Statut |
|---|---|
| **Théorème local** — bifurcation transcritique, seuil de lavage, ralentissement critique en `1/|l − l_crit|` | **Établi** dans le modèle réduit, 11/11, et **robuste aux six cinétiques** |
| **Robustesse structurelle** — le mécanisme survit-il aux extensions ? | **Partielle.** Le seuil et la décroissance survivent à neuf extensions sur neuf. La monotonie ne survit pas au retard, ni à la compétition dans 4,5 % de l'espace des paramètres |
| **Validité biologique** | **Non testée.** Aucune donnée expérimentale, aucun laboratoire |

## Items non couverts

| Item | Obstacle |
|---|---|
| 10. biofilm et diffusion | non implémenté ; la variante spatiale en est une approximation grossière |
| 12. pertes pulsées | non implémenté |
| 15. comparaison au contrôle optimal | demande une formulation de coût qui n'est pas dans le dossier |
| 16 à 19. données publiées, expérience, réplication | données et laboratoire absents |
