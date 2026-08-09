# Programme prébiotique dirigé — régime 7

**Statut : programme de recherche. Trajectoires de populations disponibles, critère héréditaire non testé.**
Deux trajectoires expérimentales de populations d’ARN catalytique sur huit cycles sont maintenant intégrées. Elles décrivent des fréquences de séquences, sans filiation parent-descendant de compartiments. Ce document précise ce qu’il faudrait encore mesurer et à quelles conditions un résultat sur la continuité héréditaire compterait.

## 1. Le verrou

Le verrou ORI-C n'est pas dans l'ARN, ni dans les membranes, ni dans les
réactions prébiotiques pris séparément. Ces travaux fournissent des briques.

> Le verrou est dans le **couplage** entre compartimentation, copie par
> matrice, variation héritable et persistance — c'est-à-dire dans leur
> intégration en une architecture capable de poursuivre sa propre continuité.

C'est la formulation directe, dans ce domaine, de ce que le socle appelle le
seuil du vivant (`CODEBOOK.md` §12.5) : l'organisation devient capable de
participer activement à la conservation, à la reproduction et à la
transformation de ses propres conditions de persistance.

## 2. Séparation stricte d'avec l'acte 3

| | Régime 7, ce programme | Régime 8, acte 3 de l'article |
|---|---|---|
| Objet | chimie organisée, pas encore vivante | population déjà vivante |
| Système | protocellules, matrices, vésicules | bactéries, résistance aux antibiotiques |
| Question | l'hérédité peut-elle apparaître ? | comment une hérédité existante répond-elle à une contrainte ? |
| Hérédité | à établir | présupposée |

**Les deux ne doivent pas être mélangés, ni dans les données, ni dans les
verdicts.** L'expérience sur les antibiotiques porte sur un système qui possède
déjà tout ce que ce programme cherche à voir apparaître. Un succès de l'un
n'appuie pas l'autre.

## 3. Les dix axes

| Recherche | Données à recueillir | Ce que cela teste dans ORI-C |
|---|---|---|
| Formation des briques prébiotiques | concentrations initiales et finales, rendements, sous-produits, stabilité, vitesse de réaction | quels constituants deviennent accessibles sous chaque environnement |
| Polymérisation | longueur des polymères, distribution des tailles, séquences, taux de dégradation, répétabilité | passage de molécules simples à des structures portant une histoire |
| Copie par matrice | nucléotides copiés, fidélité, taux d'erreur, vitesse, blocages, dépendance à la séquence | existence d'une reproduction de structure guidée par un héritage |
| Compartimentation | taille et nombre de vésicules, perméabilité, encapsulation, croissance, division, durée de vie | transformation d'une chimie dispersée en organisation localisée |
| **Couplage copie-compartiment** | taux de copie dedans et dehors, effet de la membrane, rétention des produits, partage à la division | transmission d'une organisation chimique entre générations de compartiments |
| Apport énergétique | gradients redox, pH, température, énergie libre, consommation de réactifs, rendement | capacité à utiliser un flux pour maintenir ses transformations |
| Variation héritable | mutations, stabilité des variantes, transmission après division, fréquence au fil des cycles | apparition d'une histoire propre au système |
| Sélection prébiotique | croissance différentielle, vitesse de copie, résistance à la dégradation, succès de division | filtrage des variantes par leur capacité de persistance |
| Dépendance au chemin | résultats après des ordres différents de chauffage, séchage, hydratation, gel, irradiation | influence de l'histoire sur les états accessibles |
| **Intégration en protocellule** | maintien simultané de membrane, copie, énergie et transmission sur plusieurs cycles | franchissement possible du verrou matière → hérédité |

Les deux lignes en gras sont les seules qui portent sur le couplage. Les huit
autres produisent des briques. **Un programme qui les exécute toutes sauf ces
deux-là n'a pas abordé le verrou.**

## 4. Les quatre types de données décisives

La présence d'une molécule ne compte pas. Quatre types de données comptent.

### 4.1 Les trajectoires complètes

```text
préparation → assemblage → copie → croissance → division → transmission → nouveau cycle
```

Une mesure finale isolée ne dit pas comment l'état a été atteint. C'est le §4
du `PROTOCOLE_DONNEES.md` appliqué ici : la série doit couvrir l'approche, le
franchissement et le régime transitoire, pas un avant-après.

Une première donnée de ce type est intégrée dans `donnees_reelles/trajectoires_population/` : deux branches d’ARN catalytique, huit cycles et dix séries de séquences suivies. Elle établit une dynamique expérimentale de composition. Elle ne contient ni compartiments individualisés, ni relations parent-descendant, ni transmission fonctionnelle mesurée.

### 4.2 Les lignées

Chaque compartiment porte un identifiant reliant : contenu initial, molécules
copiées, croissance, division, contenu transmis aux descendants, survie après
plusieurs cycles.

> **Sans données de lignées, on observe une production chimique, pas une
> hérédité.** C'est la ligne de partage de tout le programme.

Le schéma correspondant est exécutable : `schema_lignees/`, vérifié par
`valider_lignees.py`. Une table de lignées qui ne passe pas n'est pas une table
de lignées.

### 4.3 Les témoins

| Témoin | Ce qu'il isole |
|---|---|
| même chimie sans compartiment | rôle de la localisation |
| compartiment sans matrice | rôle du modèle copié |
| matrice sans mécanisme de copie | rôle de la copie |
| copie sans apport énergétique renouvelé | rôle du flux |
| système complet sans variation | rôle de la variation |
| système complet avec variation | condition testée |
| même état final visé après deux histoires différentes | dépendance au chemin |

### 4.4 La persistance après retrait de la contrainte

Que subsiste-t-il quand l'impulsion disparaît ? Le polymère reste-t-il intact ?
La membrane conserve-t-elle son contenu ? La variante est-elle transmise ? La
fonction réapparaît-elle au cycle suivant ? L'organisation doit-elle être
reconstruite entièrement de l'extérieur ?

C'est ici que se distingue une réaction ponctuelle d'une inscription
historique.

## 5. Le témoin manquant, à ajouter

La liste du §4.3 isole la **fonction** de chaque composant. Elle ne contient
pas le témoin qui a fait basculer le verdict de la branche 2, et le socle
l'exige : `PROTOCOLE_DONNEES.md` §6, **témoin de complexité égale**.

> **À ajouter comme huitième témoin.** Un compartiment portant un polymère
> **non copiable** de longueur, de charge et d'encombrement appariés à la
> matrice, avec le même nombre d'espèces moléculaires et le même apport
> énergétique. Il possède autant de degrés de liberté chimiques que le système
> testé, et aucun mécanisme d'hérédité.

Sans lui, une différence de persistance entre compartiments peut venir de la
charge macromoléculaire, de l'osmolarité ou de la stabilisation de membrane par
un polyanion — et non de la copie. La branche 2 a produit un témoin mal
apparié et le rapport correspondant a dû conclure « non concluant » ; le §6.1
du protocole impose depuis de **publier les plages d'exploitation** de chaque
variable substituée. La même exigence s'applique ici : longueur, charge et
concentration du polymère témoin doivent être publiées à côté de celles de la
matrice, pas déclarées équivalentes.

## 6. Critère minimal de réussite

Six conditions, toutes requises simultanément :

1. une matrice produit des copies **avec des variations** ;
2. les copies restent associées à un compartiment ;
3. les compartiments croissent et se divisent ;
4. une partie des variantes est transmise aux descendants ;
5. certaines variantes **modifient la persistance ou la reproduction** du
   compartiment ;
6. cette différence se maintient sur plusieurs cycles **sans réinitialisation
   complète par l'expérimentateur**.

La condition 6 est celle qui est le plus souvent relâchée en pratique, et c'est
elle qui distingue une continuité propre d'un entretien externe.

Ces six conditions sont évaluées par `valider_lignees.py --critere` sur une
table de lignées conforme. Elles ne sont pas laissées à l'appréciation.

**Ce que la preuve serait, et ne serait pas.** Elle ne serait pas « la création
de la vie ». Elle montrerait une transition mesurable entre chimie organisée et
continuité héréditaire. C'est une revendication plus étroite et vérifiable.

## 7. Priorité expérimentale

> Comparer plusieurs trajectoires environnementales sur des protocellules
> contenant une matrice d'ARN ou un polymère analogue, puis mesurer copie,
> encapsulation, division, transmission et persistance sur plusieurs cycles.

Trajectoires à comparer : cycles humides et secs ; gel et dégel ; gradients
hydrothermaux ; surfaces minérales ; alternance de plusieurs environnements.

**Variable principale.**

> La proportion de compartiments descendants qui conservent une information
> moléculaire héritée **et** une différence fonctionnelle mesurable après
> plusieurs cycles.

Les deux conditions sont conjointes. Une information transmise sans effet
fonctionnel est une trace ; un effet fonctionnel sans information transmise est
un état. Ni l'une ni l'autre n'est une hérédité.

C'est la donnée qui manque le plus pour relier la branche 1 à la branche 3.

## 8. Rattachement au socle

Ce programme n'invente pas de vocabulaire. Il instancie celui du socle.

| Notion du socle | Instanciation ici |
|---|---|
| `S` / `m` / `A` (`CODEBOOK` §13.4) | `S` concentrations et volumes ; `m` séquence du polymère et composition transmise ; `A` couplage membrane-copie-énergie |
| Critère état / architecture (§13.4) | une variation reste dans `S` si elle se corrige au cycle suivant sans changer le mécanisme ; elle devient architecturale si le mode de transmission lui-même change |
| Diagnostic `D-H-L` (§13.2) | `D` nombre de cycles de survie de la variante ; `H` écart entre conditions d'acquisition et de perte ; `L` variantes définitivement sorties de la population |
| Hiérarchie des possibles (§13.3) | `P^adm` produits compatibles avec la chimie ; `P^att` produits atteignables depuis l'état courant ; `P^kin(T,C,ε)` produits accessibles dans le nombre de cycles et avec les ressources déclarés ; `P^pers` produits laissant une trace au-dessus du seuil retenu |
| Mémoire distribuée (§13.1) | séquence, composition membranaire et gradient énergétique sont **trois mémoires de constantes de temps différentes**, et l'irréversibilité peut passer de l'une à l'autre |
| Signature de transition (§6) | `ΔΠ` nouveau mode de persistance ; `ΔH` importance nouvelle de l'héritage — ce sont les deux termes que le franchissement du verrou doit faire basculer |
| Témoins (`PROTOCOLE_DONNEES` §6) | les sept témoins du §4.3, **plus** le témoin de complexité égale du §5 |

**Attention sur la mémoire distribuée.** Si les trois mémoires ont des
constantes de temps très différentes, le §3 du protocole s'applique : la fenêtre
d'observation doit être longue devant **toutes**. Un protocole sur trois cycles
ne peut rien conclure sur une mémoire dont le temps caractéristique en vaut
huit. C'est l'erreur exacte que la branche 2 a commise et corrigée.

## 9. Ce que ce programme ne prétend pas

- Il apporte une trajectoire expérimentale de composition, mais **aucun résultat sur le verrou héréditaire**. Son critère central reste *Non testé* dans `ETAT_DES_PREUVES.md`.
- Il ne prétend pas que l'intégration soit réalisable avec les techniques
  actuelles. Il dit à quelles conditions un résultat compterait.
- Il ne transfère aucun statut depuis la branche 1 ni vers la branche 3, et
  n'appuie pas l'acte 3.
- Il ne remplace pas les travaux sur les briques. Il constate qu'elles ne
  suffisent pas et désigne ce qui manque.
