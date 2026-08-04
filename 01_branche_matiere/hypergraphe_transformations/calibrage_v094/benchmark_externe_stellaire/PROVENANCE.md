# Provenance du benchmark stellaire

Le benchmark encode uniquement les étapes et critères d'arrêt décrits dans la documentation officielle de la suite de tests MESA :

- `1M_pre_ms_to_wd`, étoile de 1 masse solaire et Z = 0,02, de la pré-séquence principale au refroidissement d'une naine blanche ;
- `12M_pre_ms_to_core_collapse`, étoile de 12 masses solaires et métallicité solaire, de la pré-séquence principale à l'effondrement du cœur.

Une troisième référence, Choi et al. 2016, documente le contexte des trajectoires MIST calculées avec MESA.

Le benchmark ne contient pas les sorties numériques complètes de MESA. Il teste le transfert de la représentation par états, transitions, critères explicites et fermeture stricte. Il ne constitue pas une validation observationnelle des modèles stellaires.
