# Check-up complet ORI-C

`checkup_complet.py` est le point d'entrée unique pour auditer le dépôt et
rejouer les chaînes scientifiques versionnées sans reconstruire silencieusement
le manifeste.

## Commande normale

```bash
python checkup_complet.py
```

Le lanceur vérifie le manifeste initial, l'intégrité stricte, les données
externes déclarées si leurs chemins sont fournis, le paléoclimat, la généalogie
cosmique, les mesures locales `m/P_acc`, la campagne de recherche suivante, la
campagne centrale, la campagne maximale trois branches, l'audit transversal,
les certifications, le registre de preuves et le manifeste final.

Deux variantes existent :

```bash
python checkup_complet.py --quick
python checkup_complet.py --dry-run
```

`--quick` conserve les recalculs directement nécessaires aux dépendances
transversales mais saute les campagnes globales les plus lourdes. `--dry-run`
ne lance aucun calcul et vérifie seulement la configuration et les chemins.

## Données externes locales

Le dépôt contient `checkup_complet.paths.example.json`. Le fichier réellement
renseigné doit rester hors du dépôt, par défaut un niveau au-dessus sous le nom
`checkup_complet.paths.json`, afin que les chemins locaux Windows/Linux ne
modifient ni Git ni les manifestes.

Exemple :

```text
ORI-C-parent/
├── checkup_complet.paths.json
└── ORI-C/
    ├── checkup_complet.py
    └── ...
```

Le fichier de configuration lui-même est optionnel : s’il est absent, le
check-up du dépôt s’exécute quand même et les réinspections de données externes
locales sont marquées `SKIP`. Les entrées absentes peuvent rester à `null`. Un
fichier externe non disponible est signalé comme `SKIP`, jamais transformé en
preuve positive.

## Règle de reproductibilité

Le check-up **vérifie** les manifestes ; il ne les reconstruit pas pour masquer
une divergence. Si un recalcul modifie un artefact versionné, le contrôle final
doit échouer jusqu'à ce que la différence soit examinée, scientifiquement
acceptée, puis scellée volontairement dans une mise à jour.
