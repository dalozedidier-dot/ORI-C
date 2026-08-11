# Campagne centrale ORI-C — 2026-08-11

Cette campagne transforme le plan directeur en objets contrôlables. Elle ne
présente jamais une tâche documentaire comme une expérience réalisée.

Principe de priorité : un travail n'entre dans la campagne active que s'il
ferme un mécanisme, mesure un domaine de possibles, teste un invariant, fournit
une réplication, ajoute une intervention, produit une prédiction prospective ou
peut réfuter une hypothèse importante.

Le lanceur produit l'admission de `PALEO-HISTORY-01`, une matrice
dataset→tests pondérée, un benchmark transversal de 20 cas, l'audit des cinq
invariants et un état d'exécution des 30 axes. Les expériences et acquisitions
absentes restent `bloque_externe`, sans résultat synthétique.

État après exécution : les neuf familles paléoclimatiques sont normalisées mais
le protocole 01 reste `non_testable` faute de distributions chronologiques
point par point et parce que son contrôle négatif réel n'a pas été identifié
dans le gel. Le benchmark transversal contient 20 cas réels ou explicitement
classés comme résultats de modèle ; aucun ne renseigne encore simultanément
`X,H,m,Theta,tau,P_acc,R`. Les invariants restent donc `non_testable`, et non
« réfutés ».

```bash
python plan_directeur/campagne_centrale_2026_08_11/run_all.py
python -m pytest -q plan_directeur/campagne_centrale_2026_08_11/tests
```
