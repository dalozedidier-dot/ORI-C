# HC02 — extension qualifiée croûte primitive + hydrosphère → interface eau-roche-gaz

`HC02` reste séparée de `hyperaretes.csv`, qui demeure le baseline gelé v0.9.3. La nouveauté est que l'audit sémantique de `N030` est maintenant couvert par un faisceau de **trois expériences primaires**.

## Relation

`N051 Croûte primitive + N028 Atmosphère/hydrosphère → N030 Interfaces eau-roche-gaz`.

L'ajout non destructif de cette relation à la fermeture stricte produit **53/53**, sans recoder `H052`.

## Couverture de N030

- **Interface eau-roche-gaz** : Hao & Li 2018 fait réagir komatiite, péridotite et basalte avec H2O-CO2 dans un dispositif explicitement conçu comme analogue croûte/proto-atmosphère de la Terre primitive.
- **Chimie de l'interface et gradients** : Ueda et al. 2021 suit pH, H2 et espèces dissoutes lors de réactions hydrothermales komatiite/eau de mer primitive et documente le contraste entre fluides hydrothermaux alcalins riches en H2 et eau de mer hadéenne acide/neutre.
- **Catalyse** : Zhong et al. 2026 montre expérimentalement que des carbonates et phyllosilicates, précisément les familles de phases attendues lors de l'altération ultramafique/mafique primitive, acquièrent une activité catalytique de réduction du CO2 en présence de métaux traces; un dispositif H2 reproduit en plus le contexte géoélectrochimique hydrothermal.

La matrice traçable est `HC02_EVIDENCE_MATRIX.csv`.

## Verdict

`HC02` passe de **candidat sémantique ouvert** à **extension empiriquement qualifiée**. Le baseline historique reste 46/53 parce qu'il est gelé. La couche d'extension atteint **53/53 en fermeture stricte**.

Ce 53/53 signifie seulement que la circularité de représentation est levée par une relation appuyée expérimentalement. Il ne démontre ni une histoire naturelle unique, ni la chimie prébiotique `H033`, ni l'invariant transversal complet.
