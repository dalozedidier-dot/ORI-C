# Check-up complet ORI-C

`checkup_complet.py` est le point d'entrée unique pour auditer le dépôt et
rejouer les chaînes scientifiques versionnées sans reconstruire silencieusement
le manifeste.

## Commande normale

```bash
python checkup_complet.py
```

Le lanceur vérifie le manifeste initial, l'intégrité stricte, les données
externes déclarées si leurs chemins sont fournis, les sorties structurelles déterministes (généalogies, hypergraphe et
inventaires), le
paléoclimat, la généalogie cosmique, les mesures locales `m/P_acc`, la campagne
de recherche suivante, la campagne centrale, la campagne maximale trois
branches, l'audit transversal, les certifications, le registre de preuves et le
manifeste final.

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

Le check-up **vérifie** les manifestes sans les reconstruire. Les trois sorties
numériques explicitement déclarées dans `NUMERIC_OUTPUTS` sont comparées aux
références présentes au démarrage, avec les tolérances de la CI : `1e-8` en
relatif et `1e-10` en absolu. Cette liste couvre le résultat et les prédictions
du benchmark Santos-López, ainsi que leur reprise dans la synthèse de la
campagne de recherche suivante.

Après une étape réussie, les recalculs différents sont archivés sous
`reproductibilite/` dans le dossier du rapport, avec leurs références et un
fichier `comparison.json`. Si la comparaison confirme leur équivalence, les
octets de référence sont rétablis avant les étapes suivantes. Le rapport
mentionne cette opération. Une différence hors tolérance, un fichier absent,
une modification de structure ou de verdict provoque un échec et conserve les
sorties modifiées pour examen. Les autres fichiers restent soumis au contrôle
strict du manifeste. Une évolution scientifique des résultats exige toujours
une mise à jour examinée et scellée volontairement.

Les générateurs structurels écrivent leurs sorties en LF sur tous les systèmes.
Les figures astronomiques utilisent le moteur non interactif Agg, qui permet
de produire des PNG sans installation de Tcl/Tk.

## Synchronisation structurelle

Le check-up rejoue désormais les sorties structurelles versionnées avant les
campagnes scientifiques. Une source ajoutée à `sources.csv`, une relation modifiée
ou un inventaire recalculé qui n'aurait pas été répercuté dans son JSON dérivé
fera donc échouer le manifeste final. Le workflow `analyse-structure.yml` applique
le même principe et échoue immédiatement si une sortie structurelle déterministe
présente un `git diff`. Les sorties numériques explicitement contrôlées à
tolérance (calibrage, audit transversal) conservent leur comparaison spécialisée.

Le contrôle Git final ne se contente plus d'exécuter `git status` : toute sortie
non commise ou tout fichier non suivi restant dans le dépôt est désormais un
échec du check-up.
