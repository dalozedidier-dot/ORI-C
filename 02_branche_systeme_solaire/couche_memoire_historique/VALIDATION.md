# Validation du paquet

## Évaluation globale

Prêt à être partagé comme résultat préliminaire avec les limites indiquées.

L’implémentation, les données, les calculs exportés et les tests d’ablation sont
cohérents. Le test MPT ne valide pas l’hypothèse ORI-C dans cette formulation :
M2 perd contre un témoin de complexité égale. Le test exoplanétaire établit la
dépendance au chemin structurelle du modèle réduit, mais montre qu’elle est
transitoire.

## Données

- LR04 : 2 115 lignes sources
- La2004 : 51 001 lignes sources
- grille fusionnée : 2 601 lignes, pas de 1 ka
- valeurs manquantes : 0
- âges dupliqués : 0
- plage d’insolation calculée : 435,52 à 564,69 W m⁻²
- empreintes des deux sources conformes à `data/PROVENANCE.md`

## Recalculs indépendants

Les contrôles suivants ont été exécutés à partir des CSV exportés, sans
réutiliser les objets internes du calcul :

- RMSE M0, M1, M2, M1P et M2 sans carbone
- corrélations sur la fenêtre 1,2–0 Ma
- rapports de puissance 100/41 ka
- différences finales A–B des ensembles exoplanétaires
- égalité exacte des forçages après 50 Ma

Toutes les valeurs recalculées concordent à mieux que 10⁻¹² avec les fichiers
de métriques.

## Noyau de calcul accéléré

`oric_memory_tests.fastcore` transcrit `simulate_mpt` pour la boucle
d’optimisation. `verify_against_reference` compare les deux implémentations sur
des paramètres tirés au hasard dans les bornes, pour tous les modèles et pour
l’ablation carbone. L’écart maximal est exactement **0,0** : les deux versions
exécutent la même suite d’opérations flottantes dans le même ordre. Le gain de
vitesse mesuré est d’environ 129×.

### Portabilité : tolérance stricte plutôt qu'égalité binaire

L'écart nul est constaté sur l'environnement de livraison. Il n'est pas
portable : numpy, scipy et numba peuvent réordonner ou vectoriser les
opérations flottantes d'une version à l'autre, ce qui déplace le dernier bit.
Des exécutions sur d'autres versions ont produit des écarts de l'ordre de
10⁻¹⁴ à 10⁻¹⁸.

Le paquet retient la **reproductibilité numérique tolérée** et non la
reproductibilité binaire. Les comparaisons au modèle de référence exigent un
écart sous 1e-11.

La tolérance retenue reste très inférieure aux échelles numériques pertinentes
pour les résultats rapportés. Elle absorbe les écarts d'arrondi entre
environnements et détecte les divergences dépassant le seuil fixé. Le test
`test_la_tolerance_detecte_une_divergence_algorithmique` documente ce point :
une perturbation relative de 1e-9 sur une constante de temps produit un écart
qui dépasse la tolérance et fait échouer la comparaison.

La reproductibilité binaire aurait exigé un environnement figé ou un conteneur,
incompatible avec des dépendances bornées seulement par le bas
(`numpy>=2.0`, `scipy>=1.14`). Le choix est explicite pour que personne ne lise
un écart de dernier bit comme une erreur de calcul.


Ce contrôle est exécuté par la suite de tests. Sans lui, le budget
d’optimisation corrigé serait hors de portée et le verdict retomberait sur des
ajustements non convergés.

## Tests logiciels

Vingt-deux tests unitaires vérifient :

- lecture et intégrité LR04
- lecture et intégrité La2004
- ordre de grandeur de l’insolation
- construction de la grille commune
- détection spectrale
- correction de Holm
- convergence de M0 sous forçage constant
- égalité de la frontière orbitale finale, pour tout palier final
- déterminisme du modèle classique
- cohérence des résultats exportés avec les métriques
- égalité exacte du noyau compilé et de la référence, pour les quatre modèles
- égalité exacte de l’ablation carbone compilée et de la référence
- égalité du nombre de paramètres entre M2 et M1P
- réduction exacte de M1P à M1 lorsque le couplage lent est annulé
- égalité du rapport spectral rapide et de la référence
- taille d’échantillon efficace sur bruit blanc et sur AR(1)
- conservation du spectre par les surrogates à phases aléatoires

## Risques méthodologiques

### Chronologie LR04

La chronologie LR04 est accordée à l’insolation du 21 juin à 65°N. Le test
emploie La2004 pour reconstruire cette sollicitation. La cible n’est donc pas
totalement indépendante du prédicteur astronomique.

La campagne de contrôles mesure l’ampleur du problème : sur onze définitions du
forçage calculées depuis le même fichier La2004, la corrélation de chronologie
la plus élevée n’est pas obtenue avec l’insolation prescrite. Le rapport complet
est dans `STRESS_REPORT.md`.

### Optimisation

Les quatre modèles sont ajustés avec quatre redémarrages indépendants et un
budget de 800 générations. La convergence, la dispersion entre redémarrages et
les paramètres restant sur une borne sont journalisés dans
`results/mpt/summary.json` et `results/mpt/optimization.json`.

Un paramètre encore sur une borne après élargissement d’un ordre de grandeur ne
signale pas un optimum contraint mais une non-identifiabilité. C’est le cas du
couplage carbone de M2, dont le profil de vraisemblance et la stabilité entre
fenêtres sont analysés dans `STRESS_REPORT.md`.

### Autocorrélation des résidus

Le BIC calculé sur 1 200 points supposés indépendants surestime massivement le
support des paramètres supplémentaires. Le verdict utilise la taille
d’échantillon efficace. Le compte brut reste exporté sous `bic_naive` pour
permettre la comparaison avec la première version du rapport.

### Test exoplanétaire

Les forçages sont prescrits et l’EMIC n’est pas calibré sur un GCM. Les écarts
de M2 sont statistiquement distincts de l’ablation et bien au-dessus de l’erreur
d’intégration, mais aucun ne franchit le seuil de matérialité, et aucun ne
survit au palier de persistance. Le résultat établit le fonctionnement logique
du test H3/H4, pas sa pertinence climatique quantitative.

Une limite structurelle supplémentaire est documentée dans `STRESS_REPORT.md` :
sous le forçage final prescrit, l’EMIC réduit possède un attracteur unique et
quasi totalement englacé. Les deux histoires sont donc comparées entre deux
états presque saturés, sur le chemin d’un même état final.

## Contrôles de livraison

- manifeste SHA-256 vérifié
- aucun secret détecté
- figures inspectées visuellement
- code compilé sans erreur
- exécution complète terminée avec le code de sortie 0
