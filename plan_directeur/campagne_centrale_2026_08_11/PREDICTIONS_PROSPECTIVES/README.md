# Prédictions prospectives

Chaque prédiction est créée à partir de `SCHEMA_PREDICTION.json`, reçoit un
identifiant daté, puis une empreinte SHA-256 avant ouverture des données. Le
répertoire ne contient volontairement aucune pseudo-prédiction rétrospective.

Cycle obligatoire : `train → gel → données cachées → prédiction → ouverture`.

