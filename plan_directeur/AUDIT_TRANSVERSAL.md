# Audit transversal — WP-T2 et WP-T4

Script : `audit_transversal.py`. Sortie : `audit_transversal.json`.

L'audit se calcule sur le dossier lui-même. Il cherche chaque notion du socle
dans les **fichiers générés** — JSON, CSV, sorties de test — et non dans les
documents rédigés. C'est la différence entre employer un mot et mesurer une
quantité.

## WP-T2 — Généralité réelle

| Notion | Branches où une mesure existe |
|---|---:|
| vecteur de persistance `Π` | **3** |
| liens typés de la carte | **3** |
| six dimensions `n G I E Π H` | 2 |
| niveaux de preuve | 2 |
| mémoire distribuée `m(t)` | 2 |
| témoin de complexité égale | 2 |
| dépendance au chemin | 2 |
| fenêtre longue devant les constantes de temps | 2 |
| signature de transition `S` | 1 |
| diagnostic `D-H-L` | 1 |
| `Pth` et `Pacc(T, C, ε)` | 1 |
| séparation `X` / `m` / `A` | 1 |
| critère d'altération architecturale | 1 |
| seuil et bifurcation | 1 |
| **chaîne ORI-C** | **0** |

**Huit notions sur quinze traversent au moins deux branches.** C'est la
mesure de généralité demandée au WP-T2.3, et elle est modeste : la moitié des
notions du socle n'a été instanciée que dans un seul domaine et reste
**analogique** au sens du WP-T2.4.

### Le résultat qu'il faut regarder en face

**La chaîne ORI-C ne produit aucune mesure, dans aucune branche.**

```text
Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités futures
```

C'est l'énoncé central du cadre — celui qui figure au §3 du CODEBOOK, dans les
trois articles et dans le document principal. Aucun fichier généré du dossier
ne contient de quantité qui l'instancie. Elle organise le discours ; elle ne
mesure rien.

Le WP-T2.5 demande de « retirer les notions qui ne produisent aucune mesure ».
Je ne propose pas de la retirer : une chaîne d'articulation peut être utile
sans être une métrique. Mais elle doit être **déclarée comme telle** — un
schéma d'organisation, pas un résultat — et le CODEBOOK doit cesser de la
présenter au même niveau que les notions mesurées.

Les cinq notions apportées par le §13 — mémoire distribuée, `D-H-L`,
`Pth`/`Pacc`, `X`/`m`/`A`, altération architecturale — sont toutes mesurées,
mais quatre le sont uniquement dans le banc synthétique du socle. Leur
généralité reste à établir hors de ce banc.

## WP-T4 — Compression explicative

| Quantité | Valeur |
|---|---:|
| Sections du CODEBOOK | 15 |
| Sous-sections | 15 |
| Codes de relation | 13 |
| Hypothèses enregistrées | 28 |
| Hypothèses à statut positif | **4** |
| **Concepts par résultat positif** | **3,75** |

Les quatre statuts positifs comprennent un résultat *Validé dans le modèle
réduit* et trois résultats *Établi*. Ce compteur décrit les statuts du registre
et ne doit pas être confondu avec le nombre de validations scientifiques
indépendantes d'ORI-C.

**Le cadre introduit 3,75 concepts par résultat positif obtenu.** Onze
hypothèses sont réfutées, cinq non concluantes, six non testées ; une est sans
verdict et une n'est pas évaluée.

C'est la réponse au WP-T4.3 — « vérifier si ORI-C réduit la complexité sans
perdre de précision ». En l'état, **non** : le cadre coûte davantage en
vocabulaire qu'il ne rend en résultats établis.

Deux nuances, qui ne renversent pas le constat.

Le rapport est une mesure d'**avancement**, pas de valeur intrinsèque. Un cadre
jeune a par construction plus de concepts que de résultats. Le chiffre sera
significatif lorsqu'il aura cessé de baisser ou de monter sur plusieurs
campagnes ; il vaut aujourd'hui comme point de départ.

Les résultats **négatifs ont une valeur** que ce rapport ne compte pas. Établir
que M2 est réfuté sur cinq critères indépendants, que ses paramètres ne sont
pas identifiables et qu'un modèle à zéro paramètre le bat, c'est un acquis —
mais c'est un acquis *contre* le cadre, pas *pour* lui.

## Items non couverts

| Item | Obstacle |
|---|---|
| T2.2, adaptations nécessaires par branche | demande un codage manuel comparé |
| T2.8, accord de codage entre disciplines | demande des codeurs |
| T2.9, audit du langage par experts externes | humain |
| T4.5, évaluation de clarté par lecteurs indépendants | humain |
| T4.6, distinguer utilité pédagogique et valeur scientifique | jugement, non calculable |

**T2.10, réviser le Codebook à partir des échecs**, est en revanche engagé : le
§13.4 a été complété après le banc synthétique pour exiger la déclaration du
plancher de bruit, et le présent audit demande que la chaîne ORI-C soit
requalifiée.
