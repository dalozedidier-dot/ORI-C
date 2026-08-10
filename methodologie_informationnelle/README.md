# Méthodologie informationnelle

Deux formalismes externes sont intégrés sans modifier les certifications existantes :

1. `pid.py` : PID bivariée discrète avec redondance `I_min` de Williams & Beer ; application exploratoire à D'Onofrio dans `03_branche_vivant/.../PID_X_M_A.json`.
2. `causal_states.py` : approximation **à histoire finie** des états prédictifs. Elle mesure `C_mu` fini, information prédictive finie et une crypticité-proxy, sans se présenter comme CSSR complet ni epsilon-machine asymptotique.

Les méthodes ont des tests synthétiques et des contrôles par permutation.
