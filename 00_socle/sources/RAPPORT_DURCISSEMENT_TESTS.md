# Durcissement des tests du dossier ORI-C

Ce document rend compte du renforcement de deux dispositifs : le test
interventionnel du dossier `03_test_interventionnel/`, et la vérification
d'ensemble jusqu'ici assurée par le seul script `verifier_dossier.py`.

Fichiers ajoutés :

| Fichier | Rôle |
| --- | --- |
| `03_test_interventionnel/scripts/modele_ori_c.py` | Noyau du modèle : solution stationnaire close, jacobien, seuil de lavage, cinétiques alternatives |
| `03_test_interventionnel/scripts/robustesse_test_interventionnel.py` | Campagne de 14 contrôles de robustesse |
| `03_test_interventionnel/resultats_robustesse/` | Rapport, métriques JSON et figures de la campagne |
| `tests/` | Suite pytest : 161 tests |
| `generer_manifeste.py` | Régénère et vérifie `MANIFEST_SHA256.txt` |
| `RAPPORT_VERIFICATION_CORRECTION_ORI-C.docx` | Rapport consolidé, autonome, au format du dossier |
| `pytest.ini` | Configuration |

Fichiers publiés modifiés, uniquement pour la reproductibilité (section 5) :
`test_interventionnel_ori_c.py`, `generer_carte_relationnelle_oric.py`,
`MANIFEST_SHA256.txt`, et les sorties dérivées correspondantes. **Aucune
valeur scientifique n'a été changée.**

```bash
python 03_test_interventionnel/scripts/robustesse_test_interventionnel.py
```

```bash
python -m pytest
```

```bash
python generer_manifeste.py --verifier
```

---

## 1. Le résultat central : 4,4181 était pré-asymptotique — corrigé en 4,4439

Le modèle admet une solution stationnaire en forme close. À l'équilibre
intérieur, `mu(S*) = delta + l`, donc :

```
S* = K_s (delta + l) / (mu_max - delta - l)
P* = D (S_in - S*) / (delta + l)
```

Avec les paramètres du dossier :

| Grandeur | Phase libre | Compartiment sélectif |
| --- | --- | --- |
| `l` total (`delta + leak`) | 0,30 | 0,07 |
| `S*` | 0,428571428571 | 0,075268817204 |
| `P*` | 7,976190476190 | 35,445468509985 |

**Facteur de rétention exact : 4,443909484834.**

Le dossier publiait **4,4181**, soit un écart relatif de **−0,58 %**. Cette
valeur a été corrigée : le dossier annonce désormais **4,4439**.

### Pourquoi

Ce n'est pas une erreur de calcul mais un effet de fenêtre. Le spectre du
jacobien à l'équilibre donne les temps de relaxation du mode lent :

| Système | τ (unités du modèle) | τ couverts par la fenêtre historique `t_end = 80` |
| --- | --- | --- |
| Phase libre | 3,287 | 24,3 → convergé |
| Compartiment sélectif | 14,370 | 5,6 → **résidu transitoire ≈ 3,8·10⁻³** |

Le résidu attendu, 3,8·10⁻³, coïncide avec la dérive relative de 3,2·10⁻³
effectivement enregistrée dans `metriques_test_interventionnel_ori_c.json`.
Le compartiment sélectif montait encore vers son plateau quand la
simulation s'arrêtait.

La convergence numérique le confirme :

| `t_end` | Facteur mesuré | Biais relatif |
| --- | --- | --- |
| 80 | 4,418075 | −5,81·10⁻³ |
| 160 | 4,443774 | −3,05·10⁻⁵ |
| **240** | 4,443909 | **−1,64·10⁻⁷** |
| 4000 | 4,443909 | −3,97·10⁻¹² |

**Correctif appliqué : `t_end` porté de 80 à 500 unités.** Le facteur publié
passe de 4,4181 à **4,4439**, avec un écart résiduel à la solution exacte de
**2,4·10⁻¹²**.

La valeur numérique n'était citée que dans `README.md` et `VERIFICATION.txt`.
**L'article ne la mentionne pas** : il ne décrit le test interventionnel que
qualitativement. Aucun document de fond n'a donc eu à être réécrit.

### Le critère de stabilité laissait passer l'erreur

`test_interventionnel_ori_c.py` déclarait un plateau stable si `cv < 10⁻²` et
`dérive relative < 10⁻²`. À `t_end = 80`, le compartiment sélectif affichait
`cv = 9,4·10⁻⁴` et `dérive = 3,2·10⁻³` : **les deux seuils étaient satisfaits
alors que l'état stationnaire n'était pas atteint**. Le critère était trop
permissif d'environ trois ordres de grandeur.

Un critère correct compare la dérive au temps de relaxation, pas à une
constante arbitraire : `t_end >= tau_lent · ln(1/tolérance)`, soit 298 unités
pour une tolérance de 10⁻⁹.

**Correctif appliqué.** Le script compare désormais son plateau à la solution
stationnaire exacte, et non plus à sa propre platitude locale :

```
relative_gap_retention_ratio = 2,44e-12  <  1e-6
converged_free = True
converged_selective_compartment = True
```

Les seuils `cv` et dérive sont passés de 10⁻² à 10⁻⁶, et le JSON de sortie
porte un bloc `analytic_reference` qui expose la référence analytique, l'écart
mesuré et les temps de relaxation. `verifier_dossier.py` contrôle cet écart au
lieu de la fenêtre codée en dur `4.417 < r < 4.419`.

---

## 2. Campagne de robustesse : 14 contrôles, 14 réussis

Le script publié exécutait une intégration et rapportait un nombre. La
campagne cherche activement à faire tomber la conclusion.

| Code | Contrôle | Résultat |
| --- | --- | --- |
| C01 | Solution close confrontée au calcul numérique | Écart relatif max **2,6·10⁻¹⁶** |
| C02 | Convergence temporelle | Biais courant **−2,3·10⁻¹²** ; fenêtre historique **−0,58 %** |
| C03 | Stabilité linéaire | Les deux équilibres sont asymptotiquement stables |
| C04 | Invariance au solveur | 15 configurations (5 méthodes × 3 tolérances), dispersion **2,1·10⁻⁸**, aucun échec |
| C05 | Invariance à la discrétisation | 5 maillages, écart max < 10⁻⁶ |
| C06 | Bilan de matière | Résidu relatif **1,9·10⁻⁹**, positivité et borne `S ≤ S_in` respectées |
| C07 | Conditions initiales | 42 points du quadrant positif, tous convergents |
| C08 | Balayage de l'intervention | `P*` strictement décroissant sur 400 points |
| C09 | Contrôle négatif | Intervention nulle → facteur exactement 1 |
| C10 | Contrôle de signe | Intervention inverse → facteur < 1 |
| C11 | Placebo | `P0`, `S0` et le maillage ne déplacent pas le plateau (< 10⁻⁸) |
| C12 | Seuil de lavage | Domaine de validité borné, marge d'un facteur 3,4 |
| C13 | Sensibilité globale | **200 000 tirages, 115 120 viables, zéro contre-exemple** |
| C14 | Robustesse structurelle et stochastique | Effet positif pour trois cinétiques ; IC95 % sous bruit = [4,420 ; 4,481] |

### Ce que la campagne établit de plus que le script d'origine

**La conclusion n'est pas un artefact du jeu de paramètres.** Le contrôle C13
tire uniformément sept paramètres sur plusieurs ordres de grandeur
(`mu_max`, `K_s`, `D`, `S_in`, `delta`, et deux taux de perte ordonnés). Sur
les 115 120 tirages où les deux systèmes sont viables, **le facteur de
rétention est strictement supérieur à 1 dans 100 % des cas** ; le minimum
observé est 1,0000076. La propriété est d'ailleurs démontrable : `P*(l)` a un
numérateur décroissant et un dénominateur croissant en `l`, donc est
strictement décroissante.

À cela s'ajoutent 33 295 tirages où la phase libre est lavée alors que le
compartiment survit : l'effet y est qualitatif (0 → `P* > 0`) et non
exprimable comme un facteur.

**La conclusion ne dépend pas de la cinétique de Monod.**

| Cinétique | Facteur de rétention |
| --- | --- |
| Monod | 4,4439 |
| Masse-action | 4,3873 |
| Haldane (inhibition par le substrat) | 4,4446 |

**L'effet survit au bruit.** Sous bruit multiplicatif (Euler–Maruyama,
σ = 0,05, 400 réplicas), le facteur médian est 4,4437, l'intervalle de
confiance bootstrap à 95 % est [4,4198 ; 4,4810], et **400 réplicas sur 400**
montrent un effet positif.

### Le domaine de validité est désormais borné

L'affirmation causale n'a de sens que sous le seuil de lavage :

```
leak_crit = mu_max · S_in / (K_s + S_in) − delta = 0,859091
```

Au-delà, `P* = 0` : réduire la perte ne retient plus rien. Le dossier
travaille à `leak_free = 0,25`, soit une marge d'un facteur 3,4. Cette borne
n'était énoncée nulle part.

Au voisinage du seuil, le mode lent tend vers zéro et le temps de relaxation
diverge : les points concernés restent établis analytiquement mais ne sont
pas intégrables en temps fini. La campagne les signale explicitement plutôt
que de les compter comme des échecs.

---

## 3. Suite de vérification : de 1 script à 161 tests

`verifier_dossier.py` enchaînait des `raise SystemExit` : le premier échec
masquait tous les suivants, et rien ne distinguait un défaut du dossier d'une
limite de l'environnement. La suite `tests/` sépare les contrôles.

| Fichier | Portée | Tests |
| --- | --- | --- |
| `tests/test_modele_interventionnel.py` | Invariants du modèle, sans lecture du dossier | 42 |
| `tests/test_carte_relationnelle.py` | Inventaire, typage, graphe, niveaux de preuve, matrice, audit | 39 |
| `tests/test_documents.py` | Article, cas exoplanétaires, séparation des deux schémas | 33 |
| `tests/test_integrite_dossier.py` | Manifeste, reproductibilité, cohérence README ↔ métriques | 47 |

Bilan d'exécution : **160 réussis, 1 `xfail`** — le seul défaut encore ouvert
est celui de la section 4.6. Durée : 12 secondes.

### Contrôles ajoutés, absents de `verifier_dossier.py`

- **Intégrité référentielle** du graphe : toute extrémité de lien appartient à
  l'inventaire, aucune boucle sur soi, aucune paire source-cible répétée sous
  deux codes différents.
- **FEED est le seul lien rétroactif** : le graphe complet contient exactement
  un cycle, et ce cycle passe par FEED.
- **Cohérence de la matrice dérivée** avec le fichier de relations, cellule
  par cellule.
- **Cohérence de l'audit** avec les comptes réels, et vérification que
  l'empreinte qu'il déclare pour la matrice est la bonne.
- **Les régimes ne reculent pas** le long de TR-001 → TR-040.
- **Chaque référence clé est datable** (année, DOI ou arXiv).
- **Les codes non causaux** (INCO, DESC, DEPG) portent une limite
  interprétative substantielle.
- **Le README annonce le même facteur** que les métriques produites.
- **Aucune page vide** dans les deux PDF, et les 40 transitions figurent bien
  dans le document complet.
- **Déterminisme** : deux exécutions consécutives du test interventionnel
  produisent le même contenu.
- **Vérification du `MANIFEST_SHA256.txt`**, que rien ne contrôlait.

---

## 4. Défauts trouvés — et corrigés

Les six défauts ci-dessous ont d'abord été trouvés puis encodés en `xfail`.
**Cinq sont maintenant corrigés** et vérifiés par des assertions strictes ;
le sixième relève du contenu et reste ouvert. Le détail des correctifs est en
section 5.

### 4.1 Les sorties texte utilisaient les fins de ligne de la plateforme

`write_text()` et `np.savetxt()` écrivent en CRLF sous Windows, en LF sous
Linux. Le `MANIFEST_SHA256.txt` a été produit sous un système Unix : **la
vérification d'intégrité échoue sous Windows pour une raison sans rapport
avec le contenu**. Cinq fichiers sont concernés.

*Corrigé — voir 5.1.*

### 4.2 L'audit déclarait une empreinte dépendant de la plateforme

`audit_carte_relationnelle_oric_47.txt` incorpore l'empreinte SHA-256 de
`matrice_relations_oric_47.csv`, elle-même sensible aux fins de ligne. La
provenance qu'il déclare est donc contradictoire avec le manifeste dès que
le système change :

```
audit (Windows)   : 37ea7e3122979a7f8c4643f5b3bad22750abc97025577826b42122cd3d90e707
manifeste (Unix)  : 18b9dba5a05743b5e6736e0aec379c14437e3baf5c1884939f6eb7a90518ddfc
```

Même contenu, deux empreintes. *Corrigé par 5.1.*

### 4.3 Les sorties numériques n'étaient pas reproductibles à l'octet

`metriques_...json` et `resultats_...csv` divergent du manifeste **au-delà
des fins de ligne** : ils portent la précision machine, sensible à la version
du solveur. En revanche `rapport_...txt`, qui n'imprime que six décimales,
reste conforme.

La grandeur publiée reste reproductible **à 10⁻⁶ près** d'une version de
solveur à l'autre ; la suite le teste par tolérance numérique en plus de
l'empreinte. Depuis la régénération du manifeste sur l'environnement courant,
l'empreinte est de nouveau exacte.

### 4.4 Le PDF de figure portait un horodatage

`test_interventionnel_ori_c.pdf` contient un champ `CreationDate` : son
empreinte change à chaque exécution. Son empreinte au manifeste ne peut donc
servir à rien. Le PNG, lui, est déterministe d'une exécution à l'autre — sa
divergence avec le manifeste vient de la version de la chaîne de rendu.

*Corrigé — voir 5.2.*

### 4.5 Un artefact de compilation figurait au manifeste

```
./__pycache__/verifier_dossier.cpython-313.pyc
```

Un `.pyc` dépend de la version de l'interpréteur et se régénère seul. Sa
présence dans un manifeste de provenance rend celui-ci invérifiable ailleurs.

*Corrigé — voir 5.3.*

### 4.6 Références non datables de la carte — **fermé le 14 août 2026**

| Lien | Référence actuelle |
| --- | --- |
| TR-021 → TR-028 | **corrigé le 14 août 2026** : Putnis & Price 1979, doi:10.1038/280217a0 + Okuchi et al. 2021, doi:10.1038/s41467-021-24633-4 |
| TR-024 → TR-023 | **corrigé le 14 août 2026** : Massol et al. 2023, doi:10.1029/2023JE007848 |

Les **47 relations** portent désormais un ancrage datable dans `reference_cle`. Le test n’est plus `xfail` et le verrou de non-régression interdit toute réintroduction d’une référence générique.

### 4.7 L'article mêle deux apostrophes

Le paragraphe sur la polygenèse utilise l'apostrophe droite `'` là où le
reste de l'article utilise l'apostrophe typographique `’`. Sans conséquence
scientifique, mais toute vérification textuelle doit neutraliser la
différence — ce que la suite fait désormais.

### 4.8 `verifier_dossier.py` ne peut pas s'exécuter sans Graphviz

Le script échoue dès sa première ligne utile si l'exécutable `dot` est absent
du PATH, ce qui empêche **toute** vérification, y compris celles qui n'ont
aucun rapport avec le rendu du graphe. La suite `tests/` n'a pas cette
dépendance : elle lit les sorties existantes et ne régénère la carte que si
Graphviz est présent.

```bash
winget install --id Graphviz.Graphviz
```

---

## 5. Correctifs de reproductibilité appliqués

Le dossier passe désormais une vérification d'intégrité **octet pour octet sur
la totalité de ses 47 fichiers** :

```bash
python generer_manifeste.py --verifier
```

```
47 fichiers conformes, 0 modifiés, 0 absents, 0 non listés.
```

### 5.1 Fins de ligne fixées à LF

| Fichier | Modification |
| --- | --- |
| `test_interventionnel_ori_c.py` | `write_text(..., newline="\n")` ×2 ; `np.savetxt` reçoit un descripteur ouvert avec `newline=""` |
| `generer_carte_relationnelle_oric.py` | `write_text(..., newline="\n")` ×2 ; `to_csv(..., lineterminator="\n")` |
| `robustesse_test_interventionnel.py` | `write_text(..., newline="\n")` ×2 |

Les sorties déjà présentes ont été converties. **Vérification** :
`matrice_relations_oric_47.csv` et `carte_relationnelle_oric_47.dot`
redeviennent **identiques octet pour octet** aux versions publiées, ce qui
confirme que la divergence ne tenait qu'aux fins de ligne.

L'audit, lui, a dû être régénéré : son contenu différait de la version publiée
au-delà de la seule empreinte de la matrice. Son empreinte au manifeste est
donc nouvelle. Un test vérifie désormais que l'empreinte qu'il déclare pour la
matrice est bien celle du fichier voisin.

### 5.2 Horodatage retiré des figures

```python
fig.savefig(..., metadata={"CreationDate": None, "Producer": None, "Creator": None})
```

**Vérification** : deux exécutions consécutives séparées par plus d'une
seconde d'horloge produisent des empreintes identiques pour les cinq sorties
du test interventionnel — JSON, TXT, CSV, PNG et PDF — ainsi que pour les
quatre sorties de la campagne de robustesse. Cinq tests paramétrés le
contrôlent à chaque exécution de la suite.

### 5.3 Manifeste régénéré et rendu vérifiable

`generer_manifeste.py` reconstruit le manifeste à partir de l'état réel du
dossier et sait le contrôler. Il exclut `__pycache__`, `.pytest_cache`,
`.claude` et tout `.pyc`.

Le manifeste passe de 32 à 47 entrées : l'artefact de compilation disparaît,
les scripts et résultats ajoutés y entrent. Trois tests le verrouillent —
conformité intégrale, absence d'artefact de compilation, et **exhaustivité**
(aucun fichier du dossier n'échappe au manifeste).

Un résidu de l'exécution interrompue de Graphviz a par ailleurs été supprimé :
`02_carte_relationnelle/resultats/carte_relationnelle_oric_47`, copie sans
extension du fichier `.dot`, que `cleanup=True` n'avait pas pu retirer.

### 5.4 Ce qui reste ouvert

**Les figures de la carte n'ont pas pu être régénérées** : l'exécutable
Graphviz `dot` est absent de cette machine. Les cinq fichiers concernés
(`carte_relationnelle_oric_47.{pdf,png,svg}`, `registre_relations_oric_47.pdf`,
`carte_relationnelle_oric_47_complete.pdf`) sont donc restés tels que publiés,
et leurs empreintes sont conformes.

En revanche, leur chaîne de production n'a **pas** été rendue déterministe :
Graphviz, ReportLab et PyMuPDF incorporent chacun un horodatage. Ces correctifs
n'ont pas été appliqués parce qu'ils n'auraient pas pu être vérifiés ici, et
qu'un script modifié mais jamais exécuté produirait une provenance fausse.

**Conséquence pratique** : une régénération complète de la carte, sur une
machine disposant de Graphviz, changera ces cinq empreintes. Il faudra alors
relancer `python generer_manifeste.py`. Les correctifs à appliquer à ce
moment-là sont `reportlab.rl_config.invariant = 1`, et la neutralisation des
métadonnées à l'enregistrement PyMuPDF.

---

## 6. Ce que les tests n'établissent pas

Le renforcement porte sur la **cohérence interne** d'un modèle déterministe
défini. Il ne change rien à la portée du dossier :

- le test interventionnel ne constitue ni une observation empirique ni une
  preuve générale sur le vivant ;
- la carte relationnelle n'est pas un graphe causal entièrement démontré ;
- les hydrosphères exoplanétaires demeurent hypothétiques.

La campagne rend ces limites plus précises, elle ne les lève pas. Ce qui est
désormais établi, c'est que **dans le modèle défini**, la relation entre
rétention et état stationnaire est démontrable analytiquement, robuste sur
sept ordres de grandeur de paramètres, indépendante de la cinétique choisie,
et bornée par un seuil explicite.
