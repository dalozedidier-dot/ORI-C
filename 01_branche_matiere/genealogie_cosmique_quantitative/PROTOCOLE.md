# Protocole — généalogie cosmique empirique

## Objet

Tester, sans simulation ni données synthétiques, si l’histoire cosmique et planétaire laisse des inscriptions mesurables qui modifient ce qui est matériellement ou architecturalement disponible aux étapes suivantes.

## Unité de preuve

Une unité de preuve est un enregistrement de `MESURES_EMPIRIQUES.csv` relié à une source primaire ou à un produit observationnel officiel. Chaque source déclare : le mode de preuve, la portion utilisée, la portion exclue et les stades couverts.

## Admissibilité

Sont admis : observation astronomique, observation spatiale, échantillon retourné, mesure isotopique météoritique, chronométrie météoritique, expérience de laboratoire, reconstruction planétaire fondée sur isotopes mesurés, produit observationnel officiel.

Sont exclus des verdicts : simulation numérique, donnée synthétique, mock, benchmark construit, imputation, table de rendement stellaire théorique, sortie thermochimique, intégration N-corps, scénario orbital servant à combler une archive manquante.

Un article mixte n’est pas rejeté en bloc. Sa partie observationnelle peut être utilisée si les grandeurs employées sont mesurées et si les sorties modélisées sont explicitement exclues dans `SOURCES_EMPIRIQUES.csv`.

## Hiérarchie de lecture

1. **Continuité matérielle directe** : un objet physique ancien est mesuré dans un objet ultérieur, par exemple un grain présolaire dans un échantillon retourné.
2. **Même système / même archive** : des isotopes ou âges différents dans des matériaux du Système solaire enregistrent une structure ou un ordre temporel.
3. **Observation d’un mécanisme analogue** : un autre système montre physiquement une étape inaccessible dans les archives solaires directes, par exemple un streamer ou une protoplanète en accrétion.
4. **Expérience de laboratoire** : mécanisme physique mesuré sous conditions contrôlées.
5. **Synthèse inter-domaines** : plusieurs résultats locaux indépendants soutiennent un mécanisme général, sans créer une trajectoire unique.

Aucune catégorie n’est automatiquement promue au niveau supérieur.

## Critère ORI-C local

Pour chaque claim, il faut identifier :

- une grandeur ou structure effectivement mesurée à l’étape amont ;
- un porteur d’histoire persistant ou une transformation mesurée ;
- une grandeur, structure ou domaine matériel différent à l’étape aval ;
- la force de liaison permise par les données ;
- les scénarios que le résultat ne permet pas de sélectionner.

La synthèse globale est positive seulement si plusieurs porteurs indépendants sont soutenus : composition, matière présolaire, molécules/isotopes, architecture du disque/chronologie, croissance de corps et histoires planétaires.

## Limite non négociable

L’architecture actuelle du Système solaire est observée. Ses histoires de croissance sont partiellement contraintes par des archives isotopiques. Une trajectoire orbitale détaillée unique depuis le disque jusqu’aux orbites actuelles n’est pas directement enregistrée. Sans recours aux simulations, cette question doit rester ouverte.

## Campagne quantitative réelle

La couche quantitative d’autorité est définie par `GEL_ANALYSE_QUANTITATIVE_REELLE.json`. Ce gel est **prospectif uniquement pour les ajouts futurs** : les tests de la campagne quantitative réelle ont été définis sur le corpus déjà connu et ne sont donc pas présentés comme préenregistrés pour les données actuelles.

Les huit tests/audits couvrent : réplication inter-missions, compatibilité isotopologique, ordre chronométrique avec propagation d’incertitudes, contraste temporel du même objet, réplication de streamers, réactivation tardive d’un corps retourné, robustesse du graphe empirique et ablations par famille de preuve.

Un test quantitatif n’est déclaré positif que selon le critère enregistré dans le gel. Un résultat positif ne relève jamais automatiquement le niveau de causalité au-delà de la `directness` documentée par les sources.


## Campagne quantitative complète

`GEL_ANALYSE_QUANTITATIVE_COMPLETE.json` fige les règles de la campagne finale. Le gel est rétrospectif : le corpus existait avant la définition des tests, donc aucun résultat de la campagne complète ne doit être décrit comme préenregistré.

Les calculs déterministes dérivés sont autorisés uniquement lorsque toutes les entrées numériques proviennent de mesures publiées ou de produits empiriques officiels. Les incertitudes sont propagées analytiquement au premier ordre ou par intervalles. Aucun tirage Monte-Carlo, aucune imputation et aucune population synthétique ne sont autorisés comme preuve.

Chaque test `GCQ-T09` à `GCQ-T16` doit produire : un verdict machine, un artefact individuel sous `resultats/claims_quantitatifs/`, les sources utilisées, les stades concernés, le résultat numérique et une limite d’interprétation. Les claims quantitatifs complets sont des extensions quantitatives empiriques non préenregistrées, jamais des certifications historiques automatiques.

Le critère de fermeture de bout en bout est strict : une chaîne n’est déclarée fermée que si un chemin composé exclusivement de relations d’archive, de continuité matérielle ou de séquence empirique documentée relie les deux endpoints. Un analogue inter-système ou un pont mécanisme→observation ne ferme jamais artificiellement un maillon.


## Extension par données massives réelles

Extension rétrospective au niveau grain/échantillon. Les fichiers bruts sont sélectionnés avant analyse et consignés dans `data_massives_reelles/IMPORT_SELECTION.json`. Un format canonique unique est retenu pour chaque base afin d’éviter le double comptage. Pour PGD SiC, seules les lignes `Data Published = full|partial` sont admissibles. Toute ligne non publiée, synthétique, imputée, simulée ou issue d’un prior/Monte-Carlo reste hors verdict. Les analyses sont déterministes et n’inventent aucune valeur manquante.
