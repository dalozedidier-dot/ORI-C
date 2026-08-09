# Socle commun ORI-C

Le socle rassemble ce que les trois branches partagent. Il ne contient aucun
résultat **empirique** propre à une branche et **n'est pas une quatrième
branche**.

Il contient en revanche un résultat **formel** commun : le test interventionnel
et son analyse exhaustive établissent, dans un modèle minimal, le signe de
l'effet d'une réduction du terme de perte et les bornes de validité de cette
affirmation. C'est une validation interne du mécanisme, pas une validation
empirique d'un domaine.

## Contenu

| Dossier | Contenu |
|---|---|
| `CODEBOOK.md` | définitions communes : six dimensions, chaîne historique multi-échelle, hiérarchie des possibles, persistance, liens typés, niveaux et modes de preuve |
| `PROTOCOLE_DONNEES.md` | quelles données récupérer pour tester le cadre, y compris la provenance épistémique et le test même état/histoires différentes |
| `valider_donnees.py` | rend les trois tables canoniques vérifiables par machine |
| `carte_relationnelle/` | 40 transitions, 47 relations typées, données, scripts et sorties |
| `test_interventionnel/` | chémostat, contrôle général du mécanisme d'intervention |
| `tests/` | suite transversale, voir `ETAT_DES_TESTS.md` |
| `schema_synthetique/` | schéma stabilisé TR-001 à TR-040 |
| `note_integration/` | note d'intégration |
| `sources/` | inventaire des preuves, rapports de durcissement et de lecture |

## Carte relationnelle

40 transitions réparties en huit régimes, reliées par 47 liens typés. Le graphe
est faiblement connexe, sans nœud isolé, acyclique sauf pour l'unique lien
`FEED`. Chaque relation porte sa portée, son niveau de preuve, son mode de
preuve, sa justification, sa limite interprétative et sa référence clé.

Répartition des codes :

```text
ENBL 19   MATR 13   ENVR 4   STAB 2   CATL 1   CNST 2
CONT 1    DEPG 1    INCO 1   DESC 2   FEED 1
```

Niveaux : 16 Établi, 12 Fortement inféré, 17 Plausible, 2 Hypothétique.

Quatre liens sont explicitement déclarés non causaux historiquement. Voir les
règles d'emploi dans `CODEBOOK.md`.

### Fermetures et recodages

Le schéma des nœuds porte désormais `domaine_ferme`, renseigné pour cinq
transitions. Les codes `CLOS` et `INTG` sont définis au codebook mais aucune
arête ne les porte encore : la carte affichée reste exacte pour ce qu'elle
montre, et incomplète pour le reste.

La raison n'est pas un oubli. Une fermeture agissant sur une architecture
antérieure est une arête vers le passé, incompatible avec l'acyclicité que la
suite de tests impose. Détail et plan de régénération dans
`carte_relationnelle/REGENERATION_REQUISE.md`.

## Test interventionnel

Chémostat à deux variables :

```text
dS/dt = D (S_in − S) − μ(S) P
dP/dt = μ(S) P − (δ + l) P
```

`l` est la seule variable d'intervention. Le test compare une phase libre
(`l = 0,25`) à un compartiment sélectif (`l = 0,02`) et vérifie que la
réduction du terme de perte augmente l'équilibre positif.

L'analyse exhaustive conclut **11 sections réussies sur 11**. Le niveau 1,
théorème dans le modèle, est déclaré établi ; le niveau 2, robustesse
structurelle, établi avec réserve ; le niveau 3, validité biologique, ne l'est
pas.

Deux défauts ont été corrigés pour y parvenir ; leur historique est conservé
dans `test_interventionnel/resultats_exhaustifs/CORRECTION_ANALYSE_EXHAUSTIVE.md`
et résumé dans `AUTORITE_DES_DOCUMENTS.md`.

Quatorze contrôles C01 à C14 : solution stationnaire en forme close, convergence
temporelle, stabilité linéaire, invariance au solveur et à la discrétisation,
bilan de matière, invariance aux conditions initiales, balayage de
l'intervention, contrôle négatif, contrôle de signe, placebo, seuil de lavage,
sensibilité globale, robustesse structurelle et stochastique.

Le domaine de validité est borné par le seuil de lavage :

```text
l_crit = μ_max S_in / (K_s + S_in) − δ
```

Au-delà, réduire la perte ne retient plus rien, puisqu'il n'y a plus de P.

## Exécution

```bash
cd 00_socle
pip install -r requirements.txt
python -m pytest -q
```

La régénération complète de la carte exige Graphviz sur le `PATH`.
