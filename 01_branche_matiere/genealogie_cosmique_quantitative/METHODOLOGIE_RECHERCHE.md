# Méthodologie de recherche et de transcription

## Recherche bibliographique

La campagne privilégie les articles primaires et les produits officiels. Les revues servent à orienter la recherche mais ne fournissent pas de valeurs au registre machine lorsqu’une source primaire est disponible.

Pour chaque maillon, la recherche porte séparément sur : mesure directe, échantillon retourné, chronométrie, expérience de laboratoire, analogue astrophysique et limite d’identifiabilité. Cela évite de confondre observation d’un état, mécanisme plausible et reconstruction historique.

## Transcription

Chaque nombre utilisé est transcrit dans `data/MESURES_EMPIRIQUES.csv` avec : identifiant, stade, source, mode de preuve, quantité, valeur, incertitude lorsqu’elle est publiée, unité, taille d’échantillon lorsqu’elle est disponible et note de portée.

Aucune valeur manquante n’est remplacée. Une grandeur présentée uniquement comme sortie d’un modèle n’est pas transcrite. Une grandeur calculée dans ORI-C n’est autorisée que si elle est une opération déterministe sur des mesures publiées, par exemple un produit de deux rapports isotopiques mesurés ou un écart d’âges publiés. Ces dérivations sont listées dans `RESULTATS_EMPIRIQUES.json`.

## Contrôle des comparaisons inter-études

Les comparaisons entre études ne sont jamais présentées comme mesure commune si les échantillons ou méthodes diffèrent. Les différences d’âges inter-études sont marquées « nominales ». Les comparaisons isotopiques propagent les incertitudes publiées lorsque cela est possible.

## Pare-feu des analogues

V883 Ori, TW Hya, HOPS-315, TMC1A, IRS63, DSHARP et PDS 70 démontrent l’existence de processus ou d’états dans de vrais systèmes planétaires en formation. Ils ne sont pas assimilés au Soleil jeune. Leur rôle est indiqué comme `analogue` ou `cross_system` dans les liens et claims.

## Reproductibilité

`run_all.py` reconstruit toutes les sorties à partir des CSV versionnés. Les tests exécutent une seconde reconstruction dans un dossier temporaire et comparent les empreintes octet par octet. `RESULTATS.sha256` couvre toutes les sorties locales sauf lui-même.
