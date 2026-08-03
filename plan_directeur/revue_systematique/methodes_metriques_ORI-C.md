# Méthodes proposées pour renforcer les métriques ORI-C

## 1. Information effective / émergence causale
**Cible :** Six dimensions et niveaux d’architecture
**Principe :** Mesurer si un niveau macroscopique augmente le pouvoir causal interventionnel
**Test minimal :** TPM ou modèle dynamique, interventions définies
**Force :** Évite le simple recodage du régime
**Risque :** Dépend du choix d’interventions et du coarse-graining

## 2. PID / ΦID
**Cible :** Intégration I et synergies
**Principe :** Décomposer information unique, redondante et synergique
**Test minimal :** Séries multivariées suffisantes
**Force :** Teste l’intégration sans analogie
**Risque :** Estimateurs fragiles en haute dimension

## 3. Computational mechanics / complexité statistique
**Cible :** Histoire H et mémoire
**Principe :** Reconstruire les états causaux minimaux prédictifs
**Test minimal :** Séries longues stationnaires ou segmentées
**Force :** Mesure mémoire prédictive minimale
**Risque :** Sensible à l’échantillonnage

## 4. Information closure
**Cible :** Architecture et autonomie
**Principe :** Tester si une macrovariable est prédictivement fermée sur elle-même
**Test minimal :** Séries micro/macro synchronisées
**Force :** Opérationnalise autonomie
**Risque :** Ne prouve pas finalité ni vie

## 5. Réseaux temporels d’ordre supérieur
**Cible :** Carte relationnelle
**Principe :** Comparer structure temporelle et chronologie simple
**Test minimal :** Événements datés et séquences
**Force :** Capte ordre, durée et mémoire des liens
**Risque :** Risque de surparamétrage

## 6. Découverte causale avec interventions
**Cible :** Chaîne ORI-C
**Principe :** Reconstruire les arêtes soutenues par observations + interventions
**Test minimal :** Données temporelles et contrastes
**Force :** Remplace la chaîne imposée par un graphe testable
**Risque :** Confusion latente et équivalence de Markov

## 7. Invariant causal prediction / OOD
**Cible :** Généralité interbranche
**Principe :** Chercher relations stables entre environnements
**Test minimal :** Plusieurs environnements ou domaines
**Force :** Teste invariance plutôt que corrélation
**Risque :** Peut être trop conservateur

## 8. Koopman / DMD
**Cible :** Opérateur A(t)
**Principe :** Identifier dynamiques et changements d’opérateur
**Test minimal :** Séries multivariées
**Force :** Sépare état et opérateur
**Risque :** Dictionnaire/observables critiques

## 9. SINDy
**Cible :** Lois dynamiques compactes
**Principe :** Découvrir termes nécessaires au lieu de les ajouter intuitivement
**Test minimal :** Dérivées ou données lissées
**Force :** Interprétable et parcimonieux
**Risque :** Bruit, dérivées, bibliothèque de termes

## 10. Régression symbolique
**Cible :** Pacc et lois effectives
**Principe :** Chercher formes compactes avec pénalité de complexité
**Test minimal :** Données propres et contraintes physiques
**Force :** Peut révéler correction d’échelle
**Risque :** Surajustement et recherche coûteuse

## 11. Viability kernel / reachability
**Cible :** Pacc
**Principe :** Calculer états atteignables sous T,C,ε
**Test minimal :** Modèle dynamique, contraintes, incertitude
**Force :** Donne un contenu mathématique direct à Pacc
**Risque :** Coût exponentiel en dimension

## 12. Analyse de bassins / edge states
**Cible :** Hystérésis et persistance
**Principe :** Mesurer frontières, coûts de retour et attracteurs
**Test minimal :** Modèle multistable
**Force :** Sépare retard, hystérésis, amputation
**Risque :** Difficile en haute dimension

## 13. Continuation et bifurcations
**Cible :** Seuil B
**Principe :** Localiser Hopf, fold, Bautin, transcritique
**Test minimal :** Équations ou simulateur différentiable
**Force :** Tests falsifiables des seuils
**Risque :** Ne couvre pas tous les tipping non bifurcatifs

## 14. Modèles à retard
**Cible :** Mémoire distribuée
**Principe :** Représenter délais sans état lent arbitraire
**Test minimal :** Choix/estimation du noyau de retard
**Force :** Famille concurrente forte pour MPT
**Risque :** Non-identifiabilité des retards

## 15. State-space hiérarchique
**Cible :** m(t) distribuée
**Principe :** Estimer états lents et incertitudes
**Test minimal :** Séries temporelles et modèles d’observation
**Force :** Sépare processus et mesure
**Risque :** Hypothèses de bruit et identifiabilité

## 16. Change-point / regime switching
**Cible :** Transitions
**Principe :** Détecter changements sans date imposée
**Test minimal :** Séries longues
**Force :** Teste dates et régimes
**Risque :** Confond changement de variance et mécanisme

## 17. Surrogates de Fourier
**Cible :** Nulls spectraux
**Principe :** Tester structure au-delà du spectre
**Test minimal :** Séries stationnaires par segment
**Force :** Contrôle faux positifs de phase
**Risque :** Puissance faible avec peu de tirages

## 18. Validation croisée bloquée / rolling origin
**Cible :** Prédiction historique
**Principe :** Éviter fuite temporelle
**Test minimal :** Séries ordonnées
**Force :** Critère OOS propre
**Risque :** Peu de blocs indépendants

## 19. Témoins appariés de complexité
**Cible :** Apport propre ORI-C
**Principe :** Comparer budget paramétrique et flexibilité
**Test minimal :** Modèles concurrents explicites
**Force :** Ferme les gains dus à la complexité
**Risque :** Appariement imparfait possible

## 20. Identifiabilité profil / Fisher / posterior
**Cible :** Paramètres
**Principe :** Mesurer stabilité et équifinalité
**Test minimal :** Modèle calibré et incertitudes
**Force :** Évite interprétation de paramètres arbitraires
**Risque :** Dépend de la paramétrisation

## 21. Ablation et mécanism-denial
**Cible :** Mécanismes
**Principe :** Retirer un canal à la fois avec témoin apparié
**Test minimal :** Modèle modulaire
**Force :** Attribution causale interne
**Risque :** Interactions entre ablations

## 22. Analyse topologique persistante
**Cible :** Connectivité ΔC / L
**Principe :** Mesurer changements de bassins et chemins
**Test minimal :** Nuages de points ou trajectoires
**Force :** Quantifie connectivité sans labels imposés
**Risque :** Interprétation physique non automatique

## 23. Optimal transport / Wasserstein
**Cible :** Distance entre architectures
**Principe :** Comparer distributions et trajectoires
**Test minimal :** Distributions empiriques
**Force :** Sensible à géométrie, pas seulement moyennes
**Risque :** Choix du coût

## 24. Minimum Description Length / compression
**Cible :** Coût du vocabulaire
**Principe :** Comparer gain prédictif net de complexité
**Test minimal :** Modèles codables
**Force :** Teste compression explicative
**Risque :** Choix du code universel

## 25. Accord inter-codeurs
**Cible :** Dimensions matière
**Principe :** Mesurer reproductibilité des codages
**Test minimal :** Au moins trois codeurs aveugles
**Force :** Teste si les dimensions existent opératoirement
**Risque :** Nécessite formation et protocole
