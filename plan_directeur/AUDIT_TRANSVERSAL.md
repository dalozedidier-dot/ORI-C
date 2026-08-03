# Audit transversal — WP-T2 et WP-T4

Script : `audit_transversal.py`. Sortie : `audit_transversal.json`.

L'audit se calcule sur le dossier lui-même. Il cherche chaque notion du socle dans les **fichiers générés** des trois branches et du socle, et non dans les documents rédigés. Employer un terme ne signifie pas qu'une quantité correspondante a été mesurée.

## WP-T2 — Généralité réelle

| Notion | Branches où une mesure existe |
|---|---:|
| vecteur de persistance `Π` | **3** |
| liens typés de la carte | **3** |
| mémoire distribuée `m(t)` | **3** |
| dépendance au chemin | **3** |
| fenêtre longue devant les constantes de temps | **3** |
| témoin de complexité égale | **4** |
| six dimensions `n G I E Π H` | 2 |
| niveaux de preuve | 2 |
| signature de transition `S` | 1 |
| seuil et bifurcation | 1 |
| diagnostic `D-H-L` | **0** |
| `Pth` et `Pacc(T, C, ε)` | **0** |
| séparation `X` / `m` / `A` | **0** |
| critère d'altération architecturale | **0** |
| **chaîne ORI-C** | **0** |

**Huit notions sur quinze traversent au moins deux branches.** Cinq notions ne produisent aucune mesure dans les sorties générées examinées : la chaîne ORI-C, `D-H-L`, `Pth/Pacc`, la séparation `X/m/A` et le critère d'altération architecturale.

### Portée exacte du résultat

```text
Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités futures
```

Cette chaîne reste un schéma d'organisation. Elle ordonne l'analyse, mais aucun fichier généré des branches ne l'instancie encore de bout en bout par une suite de quantités mesurées.

Le proxy observationnel de `Pacc` calculé par la campagne plateforme n'invalide pas ce constat. Il se trouve hors du périmètre des sorties de branche auditées et, surtout, il est saturé à 1 pour toutes les classes. Sans interventions appariées, il mesure seulement la diversité des transitions observées et ne constitue pas une accessibilité contrefactuelle causale.

La chaîne présence → accessibilité → mobilisabilité possède désormais une première instanciation partielle pour l'azote terrestre. Elle ne va pas jusqu'à l'opérativité, qui reste sans donnée. Cette avancée ne transforme donc pas encore la chaîne ORI-C complète en mesure transversale.

## WP-T4 — Compression explicative

| Quantité | Valeur |
|---|---:|
| Sections du CODEBOOK | 15 |
| Sous-sections | 15 |
| Codes de relation | 13 |
| Hypothèses enregistrées | 28 |
| Hypothèses à statut positif | **4** |
| **Concepts par résultat positif** | **3,75** |

Les quatre statuts positifs comprennent un résultat *Validé dans le modèle réduit* et trois résultats *Établi*. Ce compteur décrit le registre interne. Il ne représente pas quatre validations scientifiques indépendantes du cadre général.

**Le cadre introduit 3,75 concepts par résultat positif obtenu.** Onze hypothèses sont réfutées, cinq non concluantes, six non testées, une sans verdict et une non évaluée. Le rapport mesure l'avancement, pas la valeur intrinsèque du programme. Les résultats négatifs restent informatifs même s'ils ne figurent pas au numérateur.

## Items non couverts

| Item | Obstacle |
|---|---|
| T2.2, adaptations nécessaires par branche | demande un codage manuel comparé |
| T2.8, accord de codage entre disciplines | demande des codeurs |
| T2.9, audit du langage par experts externes | humain |
| T4.5, évaluation de clarté par lecteurs indépendants | humain |
| T4.6, distinguer utilité pédagogique et valeur scientifique | jugement, non calculable |

**T2.10, réviser le Codebook à partir des échecs**, reste engagé. Les notions sans mesure doivent être déclarées comme schémas, retirées ou rendues effectivement calculables.
