# Codebook du socle ORI-C

Ce document définit le langage partagé par les trois branches. Il ne contient
aucun résultat **empirique**. Toute branche qui emploie ces symboles doit s'y conformer ;
toute branche qui a besoin d'un symbole absent d'ici doit le définir chez elle
et ne pas le faire remonter.

## 1. Architecture matérielle

Un ensemble de constituants dont la configuration, les interactions et
l'environnement produisent une unité ou un régime collectif identifiable. Cette
unité peut être liée, métastable, entretenue par un flux ou reconstruite
activement.

La composition est nécessaire, jamais suffisante. Le graphite et le diamant ont
la même composition. L'eau liquide, la glace et la vapeur aussi.

## 2. Les six dimensions

```text
A(t) = [ n(t), G(t), I(t), E(t), Π(t), H(t) ]
```

| Symbole | Nom | Contenu |
|---|---|---|
| `n` | composition | inventaire des constituants |
| `G` | configuration | relations spatiales et topologiques |
| `I` | interactions | liaisons, réactions, flux |
| `E` | environnement | ressources et domaine accessible |
| `Π` | persistance | mode de maintien dans le temps |
| `H` | histoire | inscriptions héritées, dépendance au chemin |

Les propriétés observables sont produites par l'architecture entière :

```text
Y(t) = Φ[ n, G, I, E, Π, H ]
```

## 3. La chaîne ORI-C

> **Statut : schéma d'organisation, pas quantité mesurée.** L'audit
> transversal du WP-T2 a cherché une instanciation de cette chaîne dans tous
> les fichiers générés du dossier, dans les trois branches. Il n'en trouve
> aucune. Elle articule le vocabulaire et ordonne l'analyse ; elle ne produit
> par elle-même aucune mesure et ne doit donc pas être citée au même niveau
> que les notions des §6, §12 et §13, qui en produisent. Voir
> `../plan_directeur/AUDIT_TRANSVERSAL.md`.

Forme générale, valable dans les trois branches :

```text
F_t → θ_eff → Σ_t → B_t → O_t → Π_t → H_t → m_t → P_t^(s)
```

Forme condensée, celle qui sert de fil conducteur :

```text
Histoire → Architecture → Contraintes → Réponse → Inscription → Possibilités futures
```

Chaque branche instancie cette chaîne avec ses propres variables. La branche 2
écrit par exemple :

```text
H^SysSol → m^SysSol → S_astro → C_k → H_i^Terre → R_i → m^Terre
```

L'instanciation appartient à la branche. La forme générale appartient au socle.

## 4. Le vecteur de persistance

```text
Π = (π_liée, π_métastable, π_dissipative, π_homéostatique,
     π_reconstructive, π_reproductive, π_évolutive)
```

| Composante | Échelle | Mécanisme |
|---|---|---|
| liée | constituant | liaison ou barrière énergétique |
| métastable | constituant | maintien hors équilibre sans flux entretenu |
| dissipative | système ouvert | entretien par un flux |
| homéostatique | système régulé | régulation interne |
| reconstructive | organisation individuelle | réparation et renouvellement |
| reproductive | individus et générations | propagation de l'organisation |
| évolutive | population et lignée | variation héréditaire et sélection |

Les trois dernières ne sont pas trois degrés d'une même propriété. Leur
couplage caractérise le régime biologique pleinement développé, mais leurs
précurseurs ont pu apparaître dans un ordre encore inconnu.

## 5. Les types d'héritage

| Type | Exemple |
|---|---|
| matériel | éléments lourds, croûte différenciée, sédiments |
| configuratif | défauts cristallins, séquences, structures héritées |
| dynamique | gradients modifiés, cycles installés, réservoirs couplés |
| contraignant | voies rendues accessibles, coûteuses ou impossibles |
| génératif | machinerie capable de reproduire et réinterpréter l'héritage |

## 6. Signature d'une transition

```text
S = (ΔV, ΔC, ΔΠ, ΔH, ΔR, ΔF)
```

| Terme | Ce qu'il mesure |
|---|---|
| `ΔV` | apparition de variables collectives nouvelles |
| `ΔC` | modification de la connectivité entre états accessibles |
| `ΔΠ` | nouveau mode de persistance |
| `ΔH` | importance nouvelle de l'héritage |
| `ΔR` | robustesse et récupération |
| `ΔF` | possibilités fermées, contractées ou rendues plus coûteuses |

La signature caractérise la **nature** d'un changement architectural. Elle ne
mesure pas un volume absolu et les domaines ne sont pas commensurables entre
familles.

> **Note.** `ΔF` a désormais une contrepartie : l'attribut de nœud
> `domaine_ferme`, renseigné pour cinq transitions. Le code de lien `CLOS` est
> défini au paragraphe 7 mais aucune arête ne le porte encore, pour une raison
> structurelle expliquée au même endroit.

## 7. Les liens typés de la carte

| Code | Sens | Portée causale |
|---|---|---|
| `ENBL` | rend possible | causale historique |
| `MATR` | fournit les constituants | causale historique |
| `ENVR` | modifie l'environnement | causale historique |
| `STAB` | stabilise | causale historique |
| `CATL` | catalyse | causale historique |
| `CNST` | contraint | contrainte sur le domaine accessible |
| `CONT` | contribue ou favorise | contributif, non suffisant |
| `DEPG` | dépendance fonctionnelle générale | **non causal historiquement** |
| `INCO` | incorporation ou trace | **non causal historiquement** |
| `DESC` | ascendance générale | **non causal historiquement** |
| `FEED` | rétroaction | causale, seul lien rétroactif admis |
| `CLOS` | ferme, contracte ou fragmente un domaine | causale, **défini, non encore instancié** |
| `INTG` | intégration durable de deux architectures distinctes | causale, **défini, non encore instancié** |

### `CLOS` — fermeture

> Une architecture, une transformation ou une contrainte réduit, fragmente ou
> ferme un domaine d'états auparavant accessible.

C'est la contrepartie négative de `ΔF`. Le code est défini ici mais **aucune
arête ne le porte encore**, pour une raison structurelle qui doit être
explicite.

La carte est un graphe orienté acyclique, ordonné par régime, et la suite de
tests impose que `FEED` soit le seul lien créant un cycle. Or la plupart des
fermetures que le cadre nomme agissent sur une architecture **antérieure** :

| Fermeture | Arête correspondante | Représentable ? |
|---|---|---|
| Le code verrouille les réassignations | `TR-036 → TR-035` | non, inverse une arête existante et crée un cycle |
| La cristallisation ferme le régime fondu | `TR-022 → TR-022` | non, boucle sur soi |
| La spécialisation réduit l'autonomie cellulaire | pas de nœud cible | non |
| L'oxygénation contracte les voies abiotiques de surface | `TR-029 → TR-031`, `TR-029 → TR-034` | oui, compatible avec l'ordre des régimes |

**Une fermeture qui agit vers le passé n'est pas représentable par une arête
dans un graphe acyclique ordonné par le temps.** La représentation primaire
d'une fermeture est donc l'attribut de nœud `domaine_ferme`, renseigné dans
`noeuds_poc.csv`. Le code `CLOS` reste réservé aux fermetures qui pointent vers
l'avant et qui ne créent pas de cycle.

### `INTG` — intégration

> Intégration durable de deux architectures auparavant distinctes, produisant
> une nouvelle unité fonctionnelle et historique.

Le cas motivant est l'endosymbiose mitochondriale. `DESC` y décrit une
ascendance simple, alors que l'événement associe puis intègre deux lignées. La
relation `TR-037 → TR-039` porte donc `code_cible = INTG` dans les données,
en attente de la régénération de la carte.

La définition reste volontairement biologique. Elle ne sera étendue à d'autres
domaines que si des cas réellement comparables apparaissent.

### Règles d'emploi

1. Un chemin qui traverse un lien `DEPG`, `INCO` ou `DESC` **ne porte pas
   d'affirmation causale historique**. Ces liens sont déclarés non causaux.
2. `CONT` marque une contribution non suffisante. Un chemin qui le traverse
   n'établit pas une condition nécessaire.
3. `FEED` est le seul lien autorisé à créer un cycle. Le reste du graphe doit
   rester acyclique, et la suite de tests le vérifie.
4. Aucune boucle sur soi. Aucune paire source-cible répétée sous deux codes.

## 8. Niveaux et modes de preuve

Chaque relation de la carte porte deux qualifications indépendantes.

**Niveau** : Établi, Fortement inféré, Plausible, Hypothétique.

**Mode** : observation, reconstruction, simulation, expérimentation, hypothèse,
ou une combinaison.

Un niveau élevé ne dispense pas d'un mode faible, et l'inverse. La combinaison
« Établi » avec « Simulation + hypothèse » doit être considérée comme une
incohérence à corriger.

Le niveau de preuve est un classement interne prudent. Il ne remplace pas une
revue bibliographique relation par relation.

## 8 bis. Colonnes de transition du codage

Deux colonnes accompagnent chaque relation pendant la période où le vocabulaire
évolue plus vite que les figures générées.

| Colonne | Rôle |
|---|---|
| `code_cible` | code qui s'appliquera après régénération de la carte |
| `note_codage` | raison documentée de l'écart |

Tant que `code_cible` diffère de `relation`, la carte affichée reste correcte
pour ce qu'elle montre, mais incomplète. Voir
`carte_relationnelle/REGENERATION_REQUISE.md`.

## 9. Profil temporel d'une transition

Une architecture ne se date pas par un point. Elle se décrit par :

- la **première occurrence possible**, contrainte par la physique ;
- la **première occurrence attestée**, contrainte par la conservation ;
- la **généralisation**, si elle a lieu ;
- la **récurrence**, si l'architecture réapparaît indépendamment ;
- la **fermeture éventuelle**, locale ou durable.

Les premières occurrences ont rarement laissé la première preuve accessible.
Toute fenêtre doit être accompagnée de son incertitude.

## 10. Quatre conditions pour retenir une innovation d'architecture

1. une propriété collective nouvelle possède un rôle causal mesurable ;
2. un mode de persistance ou de transformation nouveau apparaît ;
3. l'architecture ouvre des combinaisons ou des trajectoires auparavant
   inaccessibles ;
4. elle laisse une inscription, une descendance ou un héritage capable
   d'influencer les états futurs.

## 10 bis. Quelles données récupérer

Le présent document définit le vocabulaire. `PROTOCOLE_DONNEES.md` dit quelles
données collecter pour que ce vocabulaire serve à **tester** plutôt qu'à
décrire : séries temporelles plutôt que mesures avant-après, six témoins dont
celui de complexité égale, et vérification publiée de l'appariement de ce
témoin. Ses trois tables canoniques sont validées par `valider_donnees.py`.

## 11. Règles de formulation

Employer « ORI-C propose de décrire », « la grille distingue », « cette
relation peut être cartographiée » lorsque le cadre réorganise des
connaissances existantes.

Réserver « démontre », « établit », « prédit » aux cas où un test explicite a
été exécuté et son critère préenregistré atteint.

Les identifiants `TR-001` à `TR-040` sont internes. La littérature peut valider
les événements auxquels ils renvoient ; elle ne valide ni l'identifiant, ni la
place que la carte lui attribue.

## 12. Directionnalité, entropie et complexité

Cette section contraint la manière dont **toutes** les branches peuvent parler
de complexité. Elle a valeur de règle, pas d'illustration.

### 12.1 Aucune direction générale

L'histoire cosmique ne produit pas nécessairement davantage de complexité et ne
suit aucune direction générale vers celle-ci. À l'échelle globale, la flèche
thermodynamique correspond à une augmentation de l'entropie et à une dégradation
progressive de l'énergie disponible pour produire du travail.

Cette évolution reste **compatible** avec la formation locale de structures sous
l'effet de la gravitation et de gradients énergétiques. Il n'y a là aucune
tension : une poche d'organisation se maintient en dissipant les gradients qui
l'alimentent.

### 12.2 Chaque transition transforme l'espace des états accessibles

De la nucléosynthèse stellaire à la formation des nuages moléculaires puis à la
différenciation planétaire, chaque grande transition redistribue les
constituants et les contraintes. Elle rend certaines trajectoires accessibles,
en déplace d'autres et en ferme une partie.

C'est la justification de la signature `S = (ΔV, ΔC, ΔΠ, ΔH, ΔR, ΔF)` et, en
particulier, de la présence de `ΔF` à côté des termes d'ouverture. Une
transition qui n'aurait que des effets ouvrants serait mal décrite.

### 12.3 Où la complexité apparaît

La complexité apparaît **localement**, lorsque certaines bifurcations permettent
à une organisation de conserver, combiner et prolonger des possibilités
héritées. Elle émerge lorsqu'une structure intègre une partie de ce qui la
précède et la réagence de manière à maintenir son organisation ou à ouvrir de
nouvelles transformations.

Trois traits accompagnent cette dynamique : une mémoire matérielle, une
réutilisation de l'héritage, un emboîtement progressif des processus. Ce sont
les trois choses que les dimensions `H` et `Π` servent à décrire.

### 12.4 Ce que la règle interdit

- Présenter l'apparition du vivant ou de la conscience comme une marche
  inévitable.
- Traiter une architecture tardive comme « supérieure » à une architecture
  ancienne. Une cellule est plus autonome qu'un cristal sur certains axes, et
  beaucoup plus fragile sur d'autres.
- Décrire la Terre comme le résultat d'un programme cosmique. Elle représente
  une trajectoire particulière, au cours de laquelle un héritage élémentaire,
  chimique et minéralogique a été sélectionné, transformé, différencié puis
  recombiné.
- Employer une mesure unique de complexité entre familles de régimes. Les
  domaines `Ω` ne sont pas commensurables.

### 12.5 Le seuil du vivant

Certaines transformations produisent des cycles capables de se maintenir, de
s'emboîter et d'ouvrir de nouvelles possibilités. Le vivant marque un seuil
supplémentaire : l'organisation devient capable de **participer activement** à
la conservation, à la reproduction et à la transformation de ses propres
conditions de persistance.

C'est ce que le vecteur `Π` distingue par ses composantes reconstructive,
reproductive et évolutive. Le seuil n'est pas un degré de complexité plus élevé
sur une échelle unique ; c'est un changement de mode de continuité.

### 12.6 Formulation retenue

> L'histoire cosmique ne produit pas nécessairement davantage de complexité.
> Elle transforme le paysage des possibles. La complexité apparaît localement
> lorsque certaines bifurcations permettent à une organisation de conserver,
> combiner et prolonger des possibilités héritées.

## 13. Mémoire, architecture et domaine des possibles

Cette section est un **apport du socle**, extrait de l'article d'application
`../02_branche_systeme_solaire/application_climat/Le_climat_comme_architecture_historique_ORI-C.docx`.

Elle ne contient rien de climatique. Le climat est le domaine où ces cinq
distinctions ont d'abord été formulées et où elles correspondent à des
quantités mesurées ; elles s'appliquent aux trois branches. Tout ce qui touche
à l'océan, à la cryosphère, au pergélisol, aux forêts, à l'AMOC, à l'engagement
d'émissions nulles ou à la décision publique **reste dans l'article** et
n'appartient pas au socle.

### 13.1 La mémoire est distribuée, pas scalaire

Le socle notait l'histoire `H` comme une dimension unique. C'est insuffisant.
Un système conserve son passé dans plusieurs compartiments dont les mécanismes
et les constantes de temps diffèrent :

```text
m(t) = [m₁, m₂, …, m_k]
```

En approximation linéaire, chaque composante est la convolution d'un forçage
passé avec un noyau propre, qui décrit la vitesse d'inscription **et**
d'effacement :

```text
mᵢ(t) = ∫ Kᵢ(t − τ) F(τ) dτ
```

Trois propriétés en découlent, et ce sont elles qui comptent.

1. **Les noyaux dépendent de l'état.** `Kᵢ = Kᵢ(X(t), m(t), A(t))`. Un noyau
   fixe est une approximation, pas une définition.
2. **Les mémoires sont couplées, et les couplages dépendent aussi de l'état.**
   `Cᵢⱼ = Cᵢⱼ(X(t), m(t), A(t))`. Un lien faible peut devenir dominant près
   d'un seuil.
3. **L'irréversibilité se transmet.** Une perturbation réversible dans un
   compartiment rapide peut, par transfert, produire une inscription
   hystérétique ou structurelle dans un compartiment lent — et réciproquement,
   une composante lente altérée impose ensuite de nouvelles contraintes aux
   composantes rapides.

**Conséquence de protocole.** Une intégrale temporelle unique du forçage cumulé
ne représente pas la mémoire d'un système à plusieurs compartiments, même
lorsqu'elle est fortement corrélée à la réponse globale. Elle en résume un
canal. Voir `PROTOCOLE_DONNEES.md` §3, *Persistance* : la fenêtre
d'observation doit être longue devant **toutes** les constantes de temps, au
pluriel.

### 13.2 Diagnostic D-H-L

Réversible, hystérétique, irréversible **ne sont pas trois degrés d'une même
échelle**. Ce sont trois propriétés indépendantes, à mesurer séparément.

| Symbole | Propriété | Mesure |
|---|---|---|
| `D` | durée de persistance de la trace | temps de relaxation, de résidence ou de reconstruction |
| `H` | asymétrie aller-retour | écart entre seuil de basculement et seuil de retour ; coût du retour |
| `L` | perte de composants, de relations ou d'accessibilité | disparition d'un constituant, d'un lien, ou d'un chemin de récupération |

Les trois se dissocient : une anomalie peut avoir `D` élevé sans `H` marqué ;
un système à deux régimes peut avoir `H` élevé sans `L` ; une extinction a `L`
maximal sans avoir demandé de basculement brutal.

**Règle.** Un rapport qui annonce une « irréversibilité » sans dire lequel des
trois est mesuré n'est pas recevable. `D` seul mesure une mémoire longue, pas
une amputation.

**Rapport à la signature de transition du §6.** La correspondance est partielle
et il faut l'énoncer comme telle. `ΔF` — possibilités fermées, contractées ou
rendues plus coûteuses — est bien la même quantité que `L`, à quoi s'ajoute
`ΔC` pour la part « connectivité des chemins de récupération ». `ΔR` recouvre
`H` sans s'y réduire, puisqu'il mesure aussi la robustesse et pas seulement
l'asymétrie du retour. `D` **n'a pas d'équivalent dans la signature** : `ΔH`
mesure l'importance nouvelle prise par l'héritage, ce qui est une propriété de
l'architecture, non la durée de la trace. La signature caractérise la nature
d'un changement ; `D-H-L` caractérise la récupérabilité d'une inscription. Les
deux sont complémentaires et ne se substituent pas l'une à l'autre.

### 13.3 `Pth` et `Pacc` — deux domaines de possibles, pas un

La chaîne du §3 se termine par « possibilités futures ». Ce terme recouvrait
deux choses distinctes, qu'il faut désormais séparer :

```text
Pth              possibles théoriques, compatibles avec les lois
Pacc(T, C, ε)    possibles atteignables avant l'horizon T, sous les
                 contraintes et ressources C, avec une probabilité ≥ ε
```

`ε` doit être **déclaré**. Sans lui, « accessible » n'a pas de contenu
vérifiable.

Les quatre régimes d'inscription s'écrivent alors sans ambiguïté, `O*` désignant
l'organisation antérieure :

| Régime | Écriture |
|---|---|
| Réversible | `O* ∈ Pacc(T, C, ε)` |
| Hystérétique | `O* ∈ Pacc`, mais `B_retour ≠ B_basculement` |
| Structurel récupérable | `O* ∉ Pacc(A(t), m(t))`, mais `O* ∈ Pacc(R(A(t)), R(m(t)))` |
| Structurel quasi irréversible | `O* ∉ Pacc(T, C, ε)` |

`R` est une opération de **restauration active** : le retour cesse d'être une
relaxation spontanée et devient une reconstruction, avec son propre coût.

Une organisation peut rester dans `Pth` en étant sortie de `Pacc`. Un
constituant dont l'information reproductive a disparu du système sort des deux.
« Quasi irréversible » est toujours relatif à `T` : l'horizon doit être écrit.

### 13.4 Séparer l'état `X`, les mémoires `m` et l'architecture `A`

L'écriture usuelle `X(t+1) = F(X(t), U(t))` laisse `F` inchangée. Le cadre
ORI-C affirme précisément le contraire. Il faut donc trois lois couplées :

```text
X(t+1)  = F[A(t)](X(t), U(t), m(t), ξ(t))
mᵢ(t+1) = Gᵢ(m(t), X(t), A(t), U(t), ξ(t))
A(t+1)  = Q(A(t), m(t), X(t), U(t), ξ(t))
Pacc(t+1; T, C, ε) = P(A(t+1), m(t+1), C(t+1), ε)
```

`X` est l'état présent, `m` les inscriptions héritées, `A` les composants,
relations et fonctions qui rendent la réponse possible, `U` les perturbations
imposées, `ξ(t)` la variabilité interne et les événements rares. `ξ` est
retenu parce que **l'ordre** des perturbations rares suffit à faire diverger
deux systèmes soumis au même forçage moyen ; le socle ne prétend pas en fournir
la loi.

**Critère de partage `X` / `A`, opératoire.**

> Une variation appartient à l'**état** si elle peut être représentée en
> conservant l'opérateur d'évolution et en modifiant seulement les variables ou
> les conditions initiales. Elle devient **architecturale** dès qu'elle exige
> de modifier les composants, les relations, les paramètres structurels ou
> l'opérateur lui-même.

Le partage est **relatif au niveau de description** et doit donc être déclaré
avec le modèle, pas supposé évident.

> **Le plancher de bruit doit être déclaré avec le verdict.** Le banc
> synthétique du socle mesure ce critère sur des systèmes où la vérité est
> connue : il classe correctement les trois cas construits — état, paramètre,
> topologie — à 100 %. Mais avec 2 % de bruit d'observation, une dérive de
> paramètre de **3 %** est classée « architecturale » dans **82,5 %** des cas.
> Ce n'est pas une défaillance du critère, c'est sa relativité au niveau de
> description prise au sérieux : à ce plancher de bruit, cette dérive **est**
> un changement d'opérateur détectable. Il s'ensuit qu'une classification
> `X` / `A` sans plancher de bruit publié n'est pas interprétable. Voir
> Ce résultat provenait d'un ancien banc synthétique, retiré de la
> distribution canonique réservée aux données réelles. Il n'est donc plus
> revendiqué comme résultat du dossier consolidé.

`A(t)` est ainsi une variable dynamique, non une structure fixe. L'histoire
peut se contenter de déplacer l'état ; elle peut déformer les bassins ; elle
peut supprimer des régimes. Ces trois cas sont différents et le §13.2 sert à
les distinguer.

### 13.5 Critère d'altération architecturale

Une fonction de réponse peut varier continûment sans qu'aucune architecture
soit altérée.

> **Une variation de noyau ne démontre pas, à elle seule, une transformation
> structurelle.**

L'altération architecturale profonde commence lorsque l'accumulation historique
affecte l'un des quatre points suivants :

1. la **topologie des relations** entre constituants ;
2. le **nombre ou la nature** des régimes stables ;
3. les **composants capables d'assurer une fonction** donnée ;
4. la **connectivité des chemins de récupération**.

Un changement de régime n'est donc pas une preuve d'amputation : le système
peut franchir un seuil et revenir. Inversement, une altération lente peut
supprimer des chemins de retour sans aucun seuil spectaculaire. Quatre
propriétés sont à examiner séparément — amplitude, franchissement de seuil,
asymétrie du retour, possibilité de reconstruction — et le langage des
attracteurs n'est utilisable qu'en distinguant trois situations : l'attracteur
antérieur est accessible ; il existe mais son bassin ou son coût d'accès
l'écarte ; l'architecture actuelle ne le soutient plus. Seul le troisième cas
est une amputation.

**Conséquence de méthode.** Une perturbation réversible ne garantit pas des
conséquences réversibles. C'est le passage d'un compartiment à un autre, décrit
au §13.1, qui convertit la première en secondes.

### 13.6 Ce que cette section ne fait pas

Elle n'ajoute aucune quatrième branche et ne propage aucun niveau de preuve.
Ces cinq distinctions sont des **définitions et des critères**, au même titre
que les §6 à §8 : elles disent comment coder et comment vérifier, elles
n'établissent aucun résultat. Leur instanciation sur un domaine réel, avec ses
repères empiriques et ses niveaux de confiance, appartient à l'article
d'application.
