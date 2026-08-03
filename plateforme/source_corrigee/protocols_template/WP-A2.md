# Protocole WP-A2

## Règles

- Geler les données confirmatoires avant analyse.
- Déclarer le modèle nul et le témoin de complexité égale.
- Conserver les échecs et analyses non concluantes.
- Ne jamais transformer un contrôle technique réussi en validation scientifique.

## Registre

### A2-001

Utiliser plusieurs éphémérides JPL.

- Mode : `external_code`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-002

Propager les covariances des conditions initiales.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-003

Générer des ensembles d’états initiaux cohérents avec les incertitudes.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-004

Comparer coordonnées cartésiennes et éléments orbitaux.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-005

Tester les transformations de repère.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-006

Tester plusieurs époques initiales.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-007

Comparer aux solutions La2004, La2010 et autres références indépendantes.

- Mode : `external_code`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-008

Valider sur des horizons croissants.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-009

Mesurer le temps de divergence chaotique.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.

### A2-010

Ne jamais interpréter au-delà de l’horizon de fiabilité.

- Mode : `data_required`
- Moteur : `astronomy_initial_conditions`
- Priorité : 2
- Confirmatoire : non
- Données : orbital_initial_conditions, ephemerides
- Prédiction ORI-C : À renseigner avant exécution confirmatoire.
- Modèle nul : À renseigner.
- Témoin de complexité égale : À renseigner.
- Métrique principale : À renseigner.
- Seuil : À renseigner.
- Conditions d’arrêt : À renseigner.
