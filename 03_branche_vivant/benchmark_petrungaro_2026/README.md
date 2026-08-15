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
