# ORI-C v0.9.9-research — consolidation et traçabilité

19 août 2026. Cette version **n'avance aucun niveau de preuve**. Le seuil §XIV
reste à **7/12**, avec les conditions **3, 4, 9, 10 et 11** ouvertes. Elle ferme
des manques d'instrumentation, corrige un défaut du pare-feu empirique et
consigne une objection non tranchée. C'est une release d'honnêteté, pas
d'avancée.

## Le verrou paléoclimatique est instrumenté et scellé

`PALEO-HISTORY-01` était resté `gele_avant_execution` depuis sa rédaction, non
par erreur de conception mais faute de deux pièces qu'il exigeait sans les
nommer. Les deux sont acquises.

**Incertitude chronologique.** Stack benthique de l'Atlantique Nord tié aux
spéléothèmes datés U-Th, `10.5281/zenodo.14796413`, CC-BY-4.0 : 337 profondeurs
× 1 000 tirages d'âge sur l'échelle composite d'IODP U1308, couvrant
3,2–650,5 ka, σ médian 1,94 ka. Les quatre empreintes MD5 concordent avec celles
publiées par Zenodo. Le jeu fournit aussi un modèle d'âge **non accordé**, retenu
comme primaire parce qu'un modèle accordé rendrait la cible partiellement
prédictible par les forçages astronomiques par construction. Écart médian entre
les deux modèles : 10,18 ka.

**Contrôle négatif physique.** Paléointensité géomagnétique relative d'IODP
U1308, `10.1594/PANGAEA.808947`, CC-BY-3.0 : 10 763 points, résolution médiane
0,14 ka. Publiée indexée en âge, sa profondeur est restituée par la table de
susceptibilité — même nombre de lignes, même ordre. Vérifié et non supposé :
14 reculs d'âge sur 10 762 pas, soit 0,13 % et 0,53 ka au maximum, et 99,87 % des
couples profondeur-âge croissants après tri.

Les deux jeux tombent sur la même carotte, donc le contrôle négatif hérite des
mêmes artefacts de chronologie que la cible — ce qu'une permutation ne peut pas
reproduire. Et la RPI n'a pas servi à construire cette chronologie : le stack est
tié aux spéléothèmes, jamais à la magnétostratigraphie.

`PALEO-HISTORY-02` hérite intégralement du critère primaire de 01 et est
**scellé le 19 août 2026, avant toute exécution**. Trois décisions ont été
tranchées et consignées : quatre blocs, imposés par la prédiction publiquement
enregistrée qui fixe « au moins 3 blocs sur 4 » ; modèle d'âge non accordé en
primaire, accordé en robustesse déclarée à l'avance ; graine 20260819.

## L'intervalle primaire est ramené à 0–650 ka

0–800 ka est inexécutable, et c'est une mesure, non un arbitrage. Aucune source
d'incertitude chronologique ne l'atteint. PALMOD 130k, acquis intégralement
— 475 sites sur 475, 1,34 Go, zéro échec — s'arrête vers 130 ka : âge maximal
médian par site 41,6 ka, et aucun des 80 sites échantillonnés n'atteint 800 ka.
Il est conservé et reclassé en robustesse multi-sites hors test primaire.

## Une fuite du pare-feu empirique, colmatée

Dans la table canonique `paleoclimate_timeseries.csv`, seule la cible est une
mesure. La colonne `forcing_1` vaut **exactement `2600 − time_kyr`** sur les
2 601 lignes : c'est l'axe temporel retourné, pas un forçage. `forcing_2` est
constante par morceaux. Le fichier était pourtant classé
`eligible_for_empirical_proof: true`.

Les données n'ont pas été réécrites — leur empreinte est épinglée ailleurs et
89 tests sont calibrés dessus. Le défaut est déclaré là où le pare-feu le lit,
identiquement dans `REAL_DATA_COVERAGE.json` et `EMPIRICAL_POLICY.json` : aucune
des deux colonnes ne peut servir de forçage admissible, et aucun test de mémoire,
D-H-L ou restauration ne peut être crédité à partir d'elles.

## Trois préenregistrements publics reportés au dépôt

`PRED-COSMOS-NCCC-001` (`osf.io/bmkgp`), `PRED-MATIERE-ABLATION-001`
(`osf.io/px4rd`) et `PRED-VIVANT-HISTOIRE-001` (`osf.io/kfju5`) étaient
publiquement enregistrés depuis le 13 août sans que le dépôt le sache : les six
paquets portaient `public_url: null`. L'audit §XIV en était aveugle.

Le report a été fait après vérification du contenu enregistré : seuils, critères
de succès et date de gel concordent avec les paquets. Une limite est consignée —
aucune des trois registrations ne cite l'empreinte SHA-256 du paquet gelé, si
bien que le lien entre l'enregistrement public et le fichier versionné est
affirmé mais non vérifiable par un tiers depuis le texte OSF seul. À corriger sur
les enregistrements restants.

`strict_success_count` reste à **0** : une antériorité publique rend éligible,
elle ne fait pas réussir.

## Une objection non tranchée sur HC02-E1

`valider_hc02_extension.py` contrôle la comptabilité de l'extension et fait
confiance au champ `verdict` au lieu de l'éprouver. Une relecture sémantique
indépendante a été écrite pour combler ce vide. Elle rend **`fail_closed`**, avec
trois objections convergeant sur la composante `catalysis` : le JSON la déclare
`supported_by` là où les trois autres sont `supported_directly` ; sa sémantique
exigée établit une compatibilité — « phases compatibles avec l'altération
primitive » — et non une production par les entrées déclarées N051+N028 ; et sa
source ne documente aucune production à partir de ces entrées.

Une quatrième objection porte sur l'outillage : le JSON et la matrice CSV
nomment leurs quatre composantes différemment, sans qu'aucune machine ne
vérifie qu'elles décrivent les mêmes.

**Le statut n'a pas été basculé.** L'objection repose sur une lecture de
sémantique scientifique et demande arbitrage. Elle est versée, horodatée et
publiée telle quelle. Le baseline scellé **46/53** est inchangé et reste l'état
publié.

## Résultats négatifs conservés

Astronomie **13 / 15**. M2 **1 / 10**, 0 sur 5 contre témoin apparié.
`C-MAT-MEM-05` non soutenu. Contraste P_acc vésiculaire négatif pour la
direction attendue. Campagne générique des 683 : 9 réussites techniques, **0
verdict scientifique `supports`** en réel strict, ce qui est le comportement
attendu d'un pare-feu fail-closed. INV-A reste exploratoire.

## Correctifs techniques

Le cron mensuel de `campagne-matiere.yml` ne téléchargeait rien : sur
`schedule`, `inputs.telecharger != false` s'évalue à faux, les quatre étapes
d'acquisition étaient sautées. Corrigé par un test explicite de `event_name`.

`evaluer_seuil_xiv.py` écrivait ses six sorties sans `newline=""`, corrompant les
fins de ligne à chaque exécution Windows. Corrigé à la source.

Un identifiant LiPD contenant la sous-chaîne `dhl` déclenchait à tort le
détecteur de la notion « diagnostic D-H-L » et faisait basculer
`traverse_deux_branches_ou_plus`, indicateur du seuil §XIV-11. La provenance
d'acquisition a été sortie du périmètre d'audit. Trois détecteurs restent
fragiles face à des identifiants opaques — `dhl` 126 faux positifs sur 200 000,
`M1P` 62, `Pacc` 7 — et alimentent les §XIV-4, 9 et 11. Non corrigés : modifier
un instrument de mesure du seuil demande arbitrage.

## Criblage documenté

Aucun jeu public ne satisfait la spécification gelée de
`PRED-VIVANT-PETRUNGARO-NIT-001`. Deux candidats ont été criblés et rejetés avec
motifs. Le point dur est nommé : les études d'évolution expérimentale ont les
effectifs mais pas l'environnement de sélection ; les études cliniques ont
l'environnement mais ni les effectifs ni l'indépendance.
