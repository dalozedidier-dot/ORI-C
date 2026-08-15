# Petrungaro 2026 — fond génétique et futurs de résistance

Analyse rétrospective de populations évolutives réelles. Elle compare, pour
chaque antibiotique, une prédiction par résistance initiale (`X`) à la même
prédiction enrichie du fond génétique initial (`X + m`). Les plis répartissent
les répétitions de chaque fond entre apprentissage et test. Le bootstrap porte
sur les populations et la permutation du fond reste conditionnée par classes
de résistance initiale.

Les trajectoires temporelles publiées sont extraites séparément. Elles sont
des réponses de sélection/croissance et ne sont pas rebaptisées trajectoires
MIC. L'absence de croissance initiale appariée à toutes les populations est
explicitement conservée comme donnée manquante.

## Approfondissement NIT

`approfondir_nit.py` produit deux analyses rétrospectives distinctes, toujours
sur données réelles :

- les 803 populations phénotypées servent à estimer l'amplitude par fond et la
  reproductibilité entre répétitions, avec bootstrap par fond génétique ;
- les 102 populations NIT séquencées servent à comparer `X`, `X + m`,
  `X + mutations` et `X + m + mutations`.

Les identifiants de ces deux cohortes ne sont pas joignables directement. Le
script ne fabrique donc aucune jointure entre elles. Les gènes utilisés comme
prédicteurs doivent être observés dans au moins deux populations ; les
mutations singleton restent dans la source mais ne peuvent pas être apprises
hors échantillon.

La diminution de l'effet prédictif de `m` après ajout des mutations est une
décomposition associative rétrospective. Elle ne constitue pas une médiation
causale, car les mutations sont mesurées après l'exposition et l'incrément
mutationnel doit aussi passer son bootstrap groupé.
