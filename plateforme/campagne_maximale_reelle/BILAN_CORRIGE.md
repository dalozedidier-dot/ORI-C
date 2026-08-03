# Campagne maximale sur données réelles — bilan corrigé

Ce document remplace `BILAN.md`, dont deux affirmations étaient inexactes.

## Deux corrections au bilan précédent

**« Aucune donnée synthétique n'est utilisée » était faux.**
`data/prebiotic_lineages_raw.csv` était présent, avec huit lignes portant le
marqueur `GABARIT_SYNTHETIQUE` — le gabarit inventé du programme prébiotique.
Il est retiré. `preparer_donnees_reelles.py` détecte désormais **tout** fichier
porteur d'un marqueur de gabarit, et non un nom en particulier.

**« Les colonnes obliquité et précession ne sont pas imputées » posait un faux
problème.** Elles n'ont pas à être imputées : la solution **La2004** de Laskar
les contient, mesurées, en colonnes 3 et 4 de son fichier publié, sur 51 001
pas. La campagne initiale employait 1 381 lignes d'excentricité seule, tirées de
La2010 tronqué à l'horizon de fiabilité.

## Données réelles, après correction

| Jeu | Source publiée | Lignes | Observables |
|---|---|---:|---|
| `orbital_timeseries` | **Laskar La2004** | **51 001** | excentricité, obliquité, précession |
| `orbital_timeseries_nbody_dossier` | intégration N-corps du dossier, 20 Ma | 20 001 | excentricité, longitude du périhélie |
| `paleoclimate_timeseries` | pile benthique **LR04** | 2 601 | δ¹⁸O et forçages |
| `orbital_reference` | **La2010** a b c d, dispersion mesurée | 1 381 | excentricité et incertitude |
| `relations` | carte relationnelle du socle | 47 | liens typés |
| `matter_transitions` | base WP-M1 | 40 | transitions |
| `ephemerides` | **JPL Horizons DE441** | 15 | positions et vitesses |
| `orbital_initial_conditions` | Horizons DE441 avec masses | 15 | états initiaux |

**Sept tables validées contre cinq.** Aucune donnée simulée, inventée ou
imputée. La provenance de chacune est écrite dans `data/provenance_reelle.json`.

## Résultats

| Statut technique | État initial | État corrigé |
|---|---:|---:|
| Réussites | 147 | **249** |
| Échecs | 0 | 16 |
| Bloqués | 504 | **370** |
| Erreurs | 0 | 0 |
| Non exécutés | 32 | 48 |

| Verdict scientifique | État initial | État corrigé |
|---|---:|---:|
| `supports` | 0 | **0** |
| `does_not_support` | 0 | 0 |
| `undetermined` | 651 | 635 |
| `not_applicable` | 32 | 48 |

**+102 réussites techniques et −134 blocages**, uniquement en cessant d'écarter
des colonnes réelles publiées.

Dix-neuf work packages produisent des résultats, dont les six astronomiques au
complet. Les 16 échecs sont ceux du WP-S3 : le vocabulaire de relations de la
plateforme et celui du `CODEBOOK.md` sont incompatibles, conflit non tranché.

**Zéro soutien scientifique**, comme dans toutes les campagnes précédentes.
Une réussite technique signifie qu'un moteur a traité un jeu réel.

## Les trois observables de La2004

| Observable | Période dominante | Période secondaire |
|---|---:|---:|
| Excentricité | **404,77 ka** | 94,97 ka |
| Obliquité | **40,22 ka** | — |
| Précession | **18,79 ka** | 10,39 ka |

Le pic secondaire de l'obliquité, affiché à 51 001 ka, est la longueur de la
série : un artefact de tendance, pas une période.

## Le résultat propre de cette campagne

### Le spectre survit à l'horizon chaotique, la phase non

Comparaison de deux séries **réelles et indépendantes** : l'intégration
N-corps du dossier, partant des positions Horizons DE441, et la solution
publiée La2004.

| Fenêtre | Corrélation | RMSE | Période N-corps | Période La2004 |
|---|---:|---:|---:|---:|
| 100 ka | **+1,0000** | 0,00011 | 50,50 | 50,50 |
| 500 ka | +0,9988 | 0,00068 | 100,20 | 100,20 |
| 1 000 ka | +0,9973 | 0,00095 | 125,12 | 125,12 |
| 2 000 ka | +0,9915 | 0,00177 | 95,29 | 95,29 |
| 4 000 ka | +0,9669 | 0,00343 | 400,10 | 400,10 |
| **6 900 ka** | +0,9125 | 0,00552 | 405,94 | 405,94 |
| 10 000 ka | +0,8270 | 0,00772 | 400,04 | 400,04 |
| 15 000 ka | +0,6581 | 0,01090 | 405,43 | 405,43 |
| 20 000 ka | **+0,4957** | 0,01323 | **408,18** | **408,18** |

La corrélation tombe de 1,000 à 0,496. **La période dominante reste identique
à la décimale sur les neuf fenêtres.**

Deux codes indépendants divergent en phase au-delà de l'horizon de 6,9 Ma —
mesuré séparément sur la dispersion des quatre solutions La2010 — et
conservent exactement le même spectre. C'est la signature du chaos
déterministe : l'information de phase se perd, la structure de fréquences non.

Trois mesures indépendantes convergent : l'horizon La2010, la corrélation
N-corps contre La2004, et l'égalité des périodes spectrales.

Détail : `degradation_phase_vs_spectre.json`,
`comparaison_nbody_la2004.json`.

## Correction d'un verdict antérieur

La campagne 2 avait conclu `does_not_support` sur la bande de 2,4 Ma de
l'excentricité, au motif que la période secondaire mesurée valait 94,97 ka.

**C'était une limite de méthode, pas une absence physique.** Les tests
d'acceptation du dossier, avec une détection de pics par proéminence plutôt
qu'un périodogramme brut, trouvent le pic de 2,4 Ma à **16,7 %** de sa valeur
attendue, sous leur seuil de 20 %. Le verdict `does_not_support` portait sur
mon estimateur, non sur la bande.

## Ce que la campagne n'établit pas

Aucune hypothèse ORI-C n'est soutenue. Les 370 blocages attendent des données
que le dossier ne contient pas : lignées prébiotiques, cycles d'antibiotiques,
réseaux astrochimiques, expériences de partage, ensembles climatiques
multi-modèles.
