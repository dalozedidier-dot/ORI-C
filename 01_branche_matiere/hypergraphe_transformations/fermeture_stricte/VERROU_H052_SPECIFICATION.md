# Le verrou 46/53 — spécification exacte de ce qui manque

**8 août 2026**

Ce document isole précisément ce qui bloque la fermeture stricte, et énonce la
question scientifique unique dont dépend sa levée. Il ne modifie pas le graphe
canonique.

---

## Ce n'est pas une hyperarête manquante

La formulation courante — « il manque une hyperarête » — est imprécise. Les 53
hyperarêtes sont présentes. Le blocage vient du **codage des entrées de H052**.

Le diagnostic (`resultats/diagnostic_fermeture.json`) isole une boucle de quatre
nœuds dont chaque arête exige en entrée le nœud produit par la précédente :

```
N029 Inventaire accessible
  └─ H030 ← N054                     (Formation de l'inventaire accessible)
N030 Interfaces eau roche gaz
  └─ H031 ← N029                     (Circulation entre réservoirs et interfaces)
N053 Système hydrothermal
  └─ H052 ← N030                     (Circulation hydrothermale entretenue)
N054 Phosphates solubles, carbonates et sels
  └─ H053 ← N053                     (Altération aqueuse produisant des espèces solubles)
                                      et la boucle se referme sur N029
```

Rien ne peut démarrer : chacun des quatre attend l'un des trois autres. Trois
nœuds supplémentaires — N031 système serpentinisé, N032 chimie organique
organisée, N035 matière disponible pour organisation active — sont bloqués en
aval par simple conséquence. D'où 46 nœuds atteints sur 53.

**N'importe laquelle des quatre graines externes suffit.** Le diagnostic le
montre : injecter N029, ou N030, ou N053, ou N054 seul rend les sept accessibles.
Le verrou est donc entièrement porté par un seul point d'entrée manquant, pas par
un déficit documentaire diffus.

## La question scientifique unique

H052 « Circulation hydrothermale entretenue » est aujourd'hui codée :

```
entrées  N051 Croûte primitive | N028 Atmosphère et hydrosphère | N030 Interfaces eau roche gaz
sorties  N053 Système hydrothermal
```

La réparation R1 déplace N030 de l'entrée vers la sortie :

```
entrées  N051 | N028
sorties  N053 | N030
```

Tout tient donc à une question, et à une seule :

> **La circulation hydrothermale entretenue exige-t-elle une interface
> eau-roche-gaz préexistante, ou la produit-elle ?**

Si elle la produit, la boucle s'ouvre et les 53 nœuds sont atteints. Si elle
l'exige, le verrou est réel et structurel.

## Ce que la littérature suggère, et ce qu'elle ne démontre pas encore

Une recherche ciblée fait converger plusieurs travaux vers l'idée que les
systèmes hydrothermaux **génèrent et entretiennent leur propre perméabilité**,
plutôt que d'hériter d'une interface préexistante. Deux candidats sont à
vérifier en texte intégral avant tout usage :

| source candidate | pertinence | statut |
|---|---|---|
| Farough et al. 2016, *Geochemistry, Geophysics, Geosystems* — évolution de la perméabilité de fracture de roches ultramafiques en cours de serpentinisation, **étude expérimentale** | le supplément S1 fournit 94 mesures `(t,Q,ΔP,k_e)` sur cinq expériences | supplément vérifié le 12 août 2026 : dans les cinq séries `k_e` décroît avec le temps ; cela ne démontre pas que H052 produit N030 |
| Alexander et al. 2026, *AGU Advances* — perméabilité crustale induite par impacts sur la Terre primitive | les impacts fracturent la croûte et ouvrent la circulation sans interface préalable | non vérifié en texte intégral |

**Ces références ne sont pas injectées dans le graphe.** Le supplément numérique
de Farough a désormais été lu et calculé, mais l'article principal et Alexander
ne sont pas tous vérifiés en texte intégral. Surtout, aucune ne porte encore sur l'hyperarête exacte : elles
établissent qu'une circulation crée de la perméabilité, pas que H052 produise
N030 au sens où ORI-C code ce nœud. La distinction est ténue et elle est
décisive.

La source qui porte actuellement H052 est S14, *Follow the serpentine as a
comprehensive diagnostic for extraterrestrial habitability*, Nature Astronomy
2024. C'est elle qu'il faudrait rouvrir en premier pour savoir si le codage
actuel lui est fidèle.

## Ce qu'il faut faire, dans l'ordre

1. **Lire S14 en texte intégral** et vérifier si le codage actuel de H052 lui est
   fidèle, ou s'il ajoute une précondition que la source n'impose pas. Si le
   codage est une sur-interprétation, le corriger est une correction
   documentaire, pas une réparation.
2. **Si S14 ne tranche pas**, vérifier l'article principal de Farough 2016 et
   Alexander 2026. Le supplément Farough ne suffit pas : il montre une perte de
   perméabilité au cours des cinq expériences. Exiger
   qu'une source démontre explicitement la production de l'interface par la
   circulation, dans des conditions compatibles avec N051 et N028.
3. **Si aucune source ne tranche**, ne pas fermer le graphe. Geler à la place un
   protocole de sensibilité qui mesure ce que l'absence de cette entrée change
   sur les métriques d'accessibilité — le calibrage v0.9.4 en fait déjà une
   partie sous stress documentaire.

## Ce qui reste vrai quoi qu'il arrive

La fermeture mathématique n'établit ni l'occurrence naturelle de la relation, ni
une séquence historique unique. Un graphe qui se ferme n'est pas un graphe qui
décrit le monde. Le scénario R1 est une **réparation structurelle**, le scénario
R2 une **hypothèse testable non canonique**, et le scénario R0 — 46 sur 53 —
reste le résultat courant du dossier.
## Mise à jour — source primaire expérimentale trouvée

Okamoto et al. (2025), DOI `10.1016/j.gca.2025.06.018`, mesure dans une même
expérience d'hydratation de periclase la génération de contrainte, la rupture,
l'augmentation d'environ deux ordres de grandeur de la perméabilité et
l'accélération d'environ 18 fois de la réaction. L'audit détaillé est dans
`PREUVE_PRIMAIRE_HC01_OKAMOTO_2025.md`.

Cette source ferme le mécanisme sur analogue expérimental, mais pas encore le
cas naturel de croûte primitive requis pour promouvoir HC01 dans l'hypergraphe
canonique. Farough demeure insuffisant pour cette promotion.

## Audit ciblé du 14 août 2026

L'audit `AUDIT_H052_2026-08-14.md` ajoute Shen et al. 2024, Okamoto et al. 2025 et Alexander et al. 2026 à la lecture structurée. Le verdict reste fail-closed : **46/53**. Okamoto soutient le mécanisme auto-généré de fracture/permeabilité sur analogue expérimental ; Alexander soutient la création de perméabilité de croûte primitive au niveau modèle ; aucune de ces sources ne suffit encore à promouvoir `HC01` comme relation empirique canonique.

## Mise à jour expérimentale — Lawal et al. 2026

Lawal et al. (2026), DOI `10.1029/2025GL120883`, expérimente la serpentinisation de dunite riche en olivine et observe par micro-CT l’initiation et la propagation de microfissures associées à la réaction. Cela renforce directement le mécanisme `réaction eau-roche → création de fissures/interfaces`. Le verrou canonique reste néanmoins à **46/53** : l’expérience ne suffit pas à établir que le contexte représente `N051 Croûte primitive` ni que ces fissures initient à elles seules un `N053 Système hydrothermal` sans interface préalable.

## Voie HC02 — bootstrap direct de N030

Une voie plus conservatrice est désormais qualifiée en extension : `HC02-E1 = N051|N028 -> N030`. Elle laisse `H052` inchangée. Hao & Li 2018 (`10.3389/feart.2018.00180`) couvre l'interface croûte–H2O/CO2 et ses produits minéraux, Ueda et al. 2021 (`10.1029/2021GC009827`) couvre la chimie et les gradients hydrothermaux, et Zhong et al. 2026 (`10.1038/s41467-026-71130-7`) couvre la capacité catalytique des carbonates/phyllosilicates pertinents. La matrice sémantique est 4/4. **Le baseline gelé reste 46/53 ; l'extension HC02-E1 atteint 53/53.**
