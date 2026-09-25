# Benchmark externe d'histoire antibiotique 2026

Source externe : Donofrio et al., Dryad `10.5061/dryad.1zcrjdg68`.

Le témoin de référence utilise l'antibiotique et la limitation élémentaire sous laquelle la souche a évolué, conformément à la définition de la variable `Limitation` dans la source Dryad. Le modèle historique ajoute l'ascendance LTEE. L'évaluation est groupée par souche afin qu'une souche ne soit jamais présente à la fois dans l'apprentissage et le test. Le critère principal est la RMSE de `log2(MIC)`.

Précision de portée du 25 septembre 2026 : les champs historiques `rmse_state_only` et `present_limitation` conservent leurs noms dans les sorties publiées. Le témoin mesure l'apport de l'ascendance au-delà de l'antibiotique et de l'environnement d'évolution. Il ne décrit pas un état physiologique et génétique complet. Cette clarification ne change ni les calculs, ni les critères, ni les verdicts existants.

Le résultat est conservé quel que soit son signe. Ce jeu est indépendant de Card 2019, mais l'analyse ORI-C reste postérieure à la publication des données et n'est donc pas qualifiée de confirmation prospective parfaite.

L'[approfondissement du 25 septembre 2026](approfondissement_2026_09_25/README.md) ajoute des permutations par clone, une sensibilité aux partitions et un transfert entre environnements. Il reste exploratoire et séparé du résultat canonique.
