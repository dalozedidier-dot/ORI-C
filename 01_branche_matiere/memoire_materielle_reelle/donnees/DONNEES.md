# D'où viennent les données

Ce dossier contient ce qu'il faut pour rejouer les verdicts de la campagne
`WP-MAT-MEM-2026` **sans rien télécharger**, et pour vérifier que ces données
sont bien celles que les dépôts publics ont publiées.

## Ce qui est ici

| fichier | contenu |
|---|---|
| `PROVENANCE.json` | 46 sources et 4 023 fichiers : DOI, URL, taille, licence, SHA-256 |
| `iodp_remanence_par_mesure.csv.gz` | 131 855 mesures de rémanence, 5 031 échantillons |

Les tables par unité expérimentale — une ligne par échantillon, éprouvette ou
condition — sont dans `../derive/`. Ce sont elles que les tests lisent.

## Ce qui n'est pas ici, et pourquoi

Les fichiers d'origine, 7,2 Go après tri, restent hors du dépôt. Ils sont
publiés sous DOI par leurs auteurs, qui en sont les garants ; les recopier
ajouterait du poids et un second exemplaire susceptible de diverger du premier.

`PROVENANCE.json` porte pour chacun son URL et son empreinte SHA-256 : tout est
retéléchargeable à l'identique et vérifiable octet par octet.

## Les 46 sources

Toutes sont publiées sur Zenodo sous licence CC-BY 4.0 ou CC0, à une exception
près : le jeu de reconstruction La₂NiO₄ porte le DOI éditeur
`10.1021/jacs.4c00863`.

| famille | jeux | ce qu'ils apportent |
|---|---|---|
| magnétisme | 25 expéditions IODP, 3 autres | rémanence naturelle puis désaimantation progressive |
| plasticité | FABEST, AlSi10Mg, Inconel 939 | cyclage, écrouissage, détensionnement |
| transition de phase | Zr15Nb, aciers moyen-Mn, Ti-Nb-Sn | traitements thermiques et fractions de phase |
| verre et relaxation | polyéthylènes vieillis, verres sous `Tg` | oxydation thermique, relaxation |
| traces de fission | zircon ZAD, monazite KTB | recuit de traces induites par irradiation |
| reconstruction de surface | Fischer-Tropsch, Cu CO₂RR, préconditionnement | histoire de surface et activité ultérieure |
| martensitique, luminescence | mémoire de forme, OSL quartz | cyclage de transformation, dose optique |

La liste exacte, avec les identifiants de dépôt, est dans `../SOURCES.json`.

## Refaire les verdicts

```bash
cd 01_branche_matiere/memoire_materielle_reelle
python run_all.py --sans-verification
```

Environ deux minutes. Les tests lisent les tables de `../derive/` et
`donnees/`, et n'ont besoin d'aucun accès réseau.

Pour repartir des sources d'origine, retélécharger et tout recalculer :

```bash
python run_all.py --telecharger
```

Compter plusieurs heures et 13 Go. C'est ce que fait le workflow
`campagne-matiere.yml`, une fois par mois : il retélécharge depuis les DOI,
compare les empreintes, rejoue tout, et échoue si les tables versionnées
diffèrent de ce qu'une exécution propre produit.

## Une réserve

Treize sources portent `sha256_recalcule: null` dans `PROVENANCE.json`, avec la
mention `empreinte_perdue`. Leur provenance d'origine — DOI, URL, taille,
licence, somme annoncée par le dépôt — est complète et suffit à retélécharger à
l'identique. Ce qui manque est l'empreinte calculée sur les octets effectivement
reçus lors du premier téléchargement. Relancer `telecharger_toutes_sources.py`
la rétablit.
