# Architecture technique

La plateforme sépare cinq niveaux.

1. **Plan directeur** : source des 683 entrées.
2. **Catalogue** : identifiants, work packages, modes, moteurs et données requises.
3. **Moteurs** : calculs communs par famille de tests.
4. **Critères gelés** : traduction des métriques en verdicts scientifiques individuels.
5. **Provenance** : environnement, rapports JSON/CSV/Markdown et manifeste SHA-256.

## Règle de vérité

Un moteur partagé peut valider le fonctionnement technique de plusieurs entrées. Il ne produit jamais automatiquement  plusieurs confirmations scientifiques. Chaque test confirmatoire doit posséder son propre critère gelé.

## Applications couvertes

- Socle formel et interventionnel
- Réseau des transitions
- Nucléosynthèse, astro-chimie et condensation
- Filtrages planétaires
- Dynamique astronomique et spectres
- Paléoclimat et climat moderne
- Prébiotique
- Architecture cellulaire et endosymbiose
- Antibiotiques
- Benchmarks transversaux et red team
