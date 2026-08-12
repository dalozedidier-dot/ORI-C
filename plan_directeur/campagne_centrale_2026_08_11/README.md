# Campagne centrale ORI-C — 2026-08-11

Cette campagne transforme le plan directeur en objets contrôlables. Elle ne
présente jamais une tâche documentaire comme une expérience réalisée.

Principe de priorité : un travail n'entre dans la campagne active que s'il
ferme un mécanisme, mesure un domaine de possibles, teste un invariant, fournit
une réplication, ajoute une intervention, produit une prédiction prospective ou
peut réfuter une hypothèse importante.

Le lanceur produit l'admission de `PALEO-HISTORY-01`, une matrice
dataset→tests pondérée, un benchmark transversal de 20 cas, l'audit des cinq
invariants, quatre mesures locales non homogénéisées, un registre de trois
bifurcations et un état d'exécution des 30 axes. Les expériences et acquisitions
absentes restent `bloque_externe`, sans résultat synthétique. Quatre prédictions
sont gelées localement avec empreinte SHA-256 ; elles ne sont ni ouvertes ni
présentées comme des préinscriptions publiques.

État après exécution : les neuf familles paléoclimatiques sont normalisées mais
le protocole 01 reste `non_testable` faute de distributions chronologiques
point par point et parce que son contrôle négatif réel n'a pas été identifié
dans le gel. Le benchmark transversal contient 20 cas réels ou explicitement
classés comme résultats de modèle. **Cinq claims renseignent désormais les sept
champs `X,H,m,Theta,tau,P_acc,R`, représentant quatre systèmes distincts**.
Cette complétude de champs ne vaut ni indépendance des cas, ni chaîne causale
commune : `INV-A` devient seulement `exploratory_comparison_ready_not_confirmatory`,
`INV-C` est partiellement opérationnalisé, et aucun invariant général n’est validé.

Les données qui peuvent être téléchargées, celles qui nécessitent un accès
manuel et celles qui doivent encore être produites sont séparées dans
`DONNEES_EXTERNES_A_ACQUERIR.json`. L'inspection de l'archive magnétique légère
du dépôt Zenodo 17522856 ne montre pas les cinq bras appariés requis et ne crée
donc pas une septième admission.

```bash
python plan_directeur/campagne_centrale_2026_08_11/run_all.py
python -m pytest -q plan_directeur/campagne_centrale_2026_08_11/tests
```
