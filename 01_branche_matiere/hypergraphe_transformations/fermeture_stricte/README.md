# Fermeture stricte

Ce paquet localise le verrou des sept nœuds et teste des réparations dans des copies du graphe. Il ne modifie jamais l'hypergraphe canonique.

```bash
python analyser_verrou.py
python -m pytest -q tests
```

Le scénario `R1` est une réparation structurelle candidate. Sa réussite mathématique ne vaut pas validation historique ou naturelle.
