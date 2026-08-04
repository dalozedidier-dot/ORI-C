# Corrections issues de l’audit du 4 août 2026

Version : `0.9.2-research`

## Corrections appliquées

- détection explicite des pointeurs Git LFS dans `verifier_dossier.py` ;
- séparation entre arbre source contrôlable et archive canonique autonome ;
- conservation des OID et tailles réelles LFS lors de la reconstruction des manifestes ;
- ajout d’un constructeur d’archive canonique qui refuse tout objet LFS non hydraté ;
- distinction documentée entre dépôt Git, ZIP source GitHub et archive hydratée ;
- correction du statut de la branche vivant : analyse exploratoire exécutée, résultat non confirmatoire ;
- harmonisation de l’état courant à 59 moteurs, avec conservation explicite de l’instantané historique à 56 moteurs ;
- marquage des anciens compteurs de tests comme instantanés historiques ;
- correction de `etat_des_tests.py` afin de maintenir les deux formats du manifeste ;
- définition d’un environnement canonique Python 3.12 et d’une matrice de compatibilité 3.12 et 3.13 ;
- renommage de `plateforme/requirements-lock.txt` en `plateforme/requirements.txt`, car ce fichier contient des bornes minimales ;
- conservation du vrai verrou exact dans `plateforme/source_corrigee/requirements-lock.txt` ;
- mise à jour de `CITATION.cff` avec le dépôt réel et la version ;
- clarification du statut juridique par un fichier `LICENSE` conservatoire, sans choisir automatiquement une licence ouverte au nom de l’auteur ;
- identification du dossier scientifique canonique et de ses alias de livraison ;
- ajout d’une CI Python 3.12 et 3.13 avec compilation complète et contrôle LFS strict ;
- correction de deux lignes finales vides dans les CSV signalés ;
- passage des six scripts shell en mode exécutable ;
- ajout de la version `0.9.2-research` et mise à jour des instructions de publication.

## Correctif CI 0.9.2

- correction du test d’intégrité strict : la présence du libellé « objets LFS non hydratés » ne suffit plus à conclure à une erreur ;
- lecture explicite du compteur numérique, avec succès lorsque ce compteur vaut zéro et code 2 uniquement lorsqu’il est supérieur à zéro ;
- comportement désormais valide dans les deux contextes : archive source avec pointeurs LFS et dépôt GitHub Actions après `git lfs pull`.

## Validation finale

- 948 contenus présents et conformes ;
- 70 pointeurs Git LFS valides dont l’OID correspond au contenu attendu ;
- 0 fichier réellement modifié par rapport au manifeste ;
- 0 fichier absent ;
- 0 fichier non listé ;
- 0 entrée de structure manquante ;
- 261 tests réussis dans les suites distinctes ;
- 3 tests ignorés ;
- 2 `xfail` attendus et documentés ;
- 21 tests sur 21 réussis pour la campagne maximale sur les trois branches ;
- cinq sorties canoniques identiques sur deux exécutions successives ;
- résultats de campagne identiques à ceux présents avant les corrections.

## Limite matérielle restante

Le ZIP source contient encore 70 pointeurs Git LFS. Leurs OID sont corrects,
mais les objets réels ne peuvent pas être téléchargés dans l’environnement de
correction, qui ne dispose pas d’un accès réseau à GitHub ou au stockage LFS.
Le fichier livré est donc une archive source corrigée, pas l’archive canonique
hydratée.

Après clonage sur une machine connectée :

```bash
git lfs install
git lfs pull
python verifier_dossier.py
python scripts/valider_tout.py --strict-lfs
python scripts/construire_archive_canonique.py --output-dir dist
```

Le dernier script ne produira le ZIP canonique que lorsque les 70 objets réels
seront présents.
