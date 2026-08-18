# Données réelles ORI-C — dossier séparé

**7 août 2026** · 402 fichiers · 813 Mo · toutes les empreintes SHA-256 vérifiées

Ce dossier est **indépendant du dépôt**. Rien n'a été écrit dans
`C:\Users\didou\Documents\GitHub\ORI-C\ORI-C`.

Il ne contient que des données **mesurées ou observées**. Aucune valeur n'est simulée,
générée, imputée ni interpolée. Les seules exceptions sont clairement isolées dans
`05_tables_candidates/`, avec leur notice.

Tout ce qui n'était pas exploitable a été retiré. `RETRAITS.json` donne la liste exacte
et le motif de chaque retrait : 3 fichiers et 16 945 lignes.

## Vérifier

```bash
python verifier_donnees.py
```

Contrôle hors ligne, sans réseau et sans écriture : chaque fichier est comparé à son
empreinte dans `MANIFESTE.csv`.

---

## Organisation

```
01_sources_primaires/          105 fichiers  274,5 Mo   données brutes des fournisseurs
   astronomie_orbites/                        4 jeux
   climat_paleoclimat/                        7 jeux
   biologie_evolution/                        8 jeux
   matiere_astrochimie/                      11 jeux

02_tables_derivees/             44 fichiers   54,5 Mo   tables canoniques ORI-C
03_documentation_provenance/    12 fichiers    0,2 Mo   fichiers de provenance d'origine
04_acquisitions_externes_2026-08-07/
                               236 fichiers  465,2 Mo   téléchargées ce jour, hors dépôt
05_tables_candidates/            4 fichiers   19,1 Mo   propositions, lire NOTICE.md
RETRAITS.json                    liste et motif de chaque suppression

MANIFESTE.csv / MANIFESTE.json   chemin, taille, SHA-256, fournisseur, identifiant,
                                 licence, description et origine de chaque fichier
verifier_donnees.py              contrôle d'intégrité autonome
```

---

## 01 — Sources primaires, récupérées du dépôt et de ses archives

Trois gisements de données réelles étaient absents du dépôt de travail. Ils ont été
reconstitués depuis les archives locales et vérifiés par empreinte.

| ce qui manquait | volume | retrouvé dans | contrôle |
|---|---:|---|---|
| 69 objets Git LFS — toute la sortie N-corps `real_science_max` | 16,7 Mo | `ORI-C-0.9.4-research-canonique.zip` | 69/69 par leur propre `oid sha256` |
| `sources_brutes/`, vidé le 6 août par le commit gitignore | 87,7 Mo | `ORI-C_DOSSIER_COMPLET.zip` | manifeste du dépôt |
| `lot_scientifique.../raw/`, jamais versionné | 206 Mo | zip du lot + 3 fichiers isolés de `Downloads` | 29/29 par `SOURCE.json` |

### Astronomie et orbites
- **IMCCE La2004** — insolation et éléments orbitaux terrestres sur 100 Ma.
- **IMCCE La2010 a-d** — quatre solutions d'excentricité, référence indépendante.
- **JPL Horizons DE441** — positions et vitesses mesurées de 15 corps à J2000.
- **NASA Exoplanet Archive** — catalogue des systèmes planétaires.

### Climat et paléoclimat
- **NASA GISTEMP v4** — dont l'ensemble d'incertitude à 200 membres, LSAT, SST et combinée.
- **HadCRUT 5.1.0.0** — série globale mensuelle 1850-2026, 200 réalisations.
- **CMIP6 NASST**, **moyennes globales**, **ensembles originaux** — Zenodo.
- **NOAA spéléothèmes 0-22 ka** — 27 721 couples âge-isotope sur 36 sites.
- **NOAA LR04**, Lisiecki et Raymo 2005.

### Biologie et évolution
- **Dryad D'Onofrio 2026** — MIC et fitness, jeu du résultat positif histoire contre état seul.
- **Dryad Sokolskyi et Baum 2026** — 12 classeurs de lignées de vésicules, 11 760 couples parent-descendant.
- **Dryad Card 2019** — MIC de la population Ara+5 du LTEE.
- **Zenodo Papastavrou** — évolution d'ARN catalytique sur huit cycles.
- **Zenodo Windels** — E. coli sous amikacine, 24 populations par condition.
- **Zenodo 10780716** — HMM dans 85 génomes endosymbiotiques.
- **Zenodo pucerons**, **Zenodo 3588334**.

### Matière et astrochimie
- **UMIST Rate22** — 8 767 réactions en phase gazeuse.
- **KIDA uva 2024** — 7 667 réactions.
- **SIMPLE CCSNe v3.1** — 1 383 rendements élémentaires, 56 507 isotopiques, 18 modèles.
- **Dégazage de Murchison** — 3 648 mesures dans trois conditions.
- **Acides aminés** — 1 387 mesures dans 69 environnements.
- **Partage métal-silicate du carbone**, **isotopes Ca lunaires**, **NUBASE**, **benchmark MESA**.

---

## 04 — Acquisitions externes du 7 août 2026

236 fichiers téléchargés ce jour depuis leur fournisseur officiel, hors du dépôt.
`ACQUISITION.json` porte l'URL exacte, la date, la taille et l'empreinte de chacun.

### Thermochimie — base OBIGT de CHNOSZ, GPL-3
2 565 espèces, dont **2 437 énergies de Gibbs de formation** publiées, avec enthalpie,
entropie, capacité calorifique, volume molaire, coefficients de Maier-Kelley et
température maximale de validité. Minéraux, gaz et espèces aqueuses.

### Géochimie — GEOROC / DIGIS, CC BY-SA 4.0
**Sept compilations, 197 fichiers, 555 677 analyses roche totale publiées** : types de
roches, cratons archéens, trapps continentaux, plateaux océaniques, trapps de bassins
océaniques, contextes volcaniques complexes, lithologies ultramafiques. Chaque analyse
porte sa méthode, son laboratoire et sa référence bibliographique.

**185 090 mesures** brutes d'éléments fortement sidérophiles et de Mo-W, ramenées à
**122 159 mesures exploitables** après déduplication et retrait des valeurs sous limite
de détection.

### Thermochimie — paramètres d'équation d'état Berman
Douze jeux de paramètres publiés de capacité calorifique et d'équation d'état V(T,P),
qui permettent d'ajouter proprement la dimension pression.

### Matière et noyaux
- **NUBASE2020** — masses, spins, demi-vies et modes de décroissance mesurés, 5 868 lignes.
- **Carte des nuclides de l'AIEA** — 3 386 nuclides, énergie de liaison, abondance naturelle, rayon de charge.

### Climat observationnel indépendant
- **Berkeley Earth** — troisième reconstruction globale, indépendante de GISTEMP et HadCRUT, 4 200 mois depuis 1850.
- **NOAA GML** — CO₂ mensuel de Mauna Loa depuis 1958 jusqu'à juillet 2026, CO₂ global annuel, CH₄ et N₂O globaux.
- **HadCRUT 5.0.2.0** série annuelle résumée, **GISTEMP** version du jour.

### Paléoclimat
- **EPICA Dome C** — CO₂ sur 800 ka, deutérium et température sur 800 ka, chronologie EDC3.
- **Vostok** — deutérium et température sur 420 ka.
- **LR04** — version NOAA courante.

### Astronomie
- **NASA Exoplanet Archive** au 7 août 2026 — 6 336 planètes, 4 749 systèmes,
  19 083 excentricités mesurées, 22 364 demi-grands axes, découvertes de 1992 à 2026.
- **SILSO** — nombre mensuel de taches solaires depuis 1749, 3 331 mois.

---

## 05 — Tables candidates

Trois tables construites au schéma ORI-C : `late_accretion_tracers.csv`
(122 159 mesures, 56 614 échantillons), `thermochemical_phases.csv` (64 512 points,
1 025 phases, **1 bar à 5 GPa**) et `volatile_inventory.csv`.

Une quatrième, `planetary_histories.csv`, est **délibérément absente** : aucune source
publique harmonisée n'existe et la remplir de mémoire violerait la règle du dossier.

**Lis `05_tables_candidates/NOTICE.md` avant de t'en servir.** Elle détaille les contrôles
physiques passés — rapport Os/Ir mesuré 1,04 contre 1,07 chondritique, zéro violation de
`dG/dP > 0`, alignement des conventions thermodynamiques vérifié à 26 J/mol près — et ce
qui reste absent : pression bornée à 5 GPa, pôles de mélange, incertitudes analytiques.

### Effet mesuré

Sur la campagne des 683 entrées, en mode données réelles strict :

| état du jeu de données | réussites | échecs | bloquées | non exécutables |
|---|---:|---:|---:|---:|
| chiffres publiés dans `README.md` | 298 | 0 | 337 | 48 |
| dépôt tel quel, code actuel | 451 | 0 | 200 | 32 |
| + climat multi-variables réel | 461 | 0 | 190 | 32 |
| + thermochimie et traceurs | 486 | 0 | 165 | 32 |
| **+ inventaire volatil** | **486** | **10** | **155** | **32** |

Aucune régression à aucune étape. Les 10 échecs sont un résultat, pas un bug : les budgets
volatils publiés de la Terre ne ferment que si le noyau porte le haut de sa fourchette.

**Ce que cela ne veut pas dire.** Le dépôt est explicite : une réussite technique signifie
seulement que l'analyse a été exécutée, pas qu'un résultat est confirmé. Le verdict
scientifique de ces entrées reste `undetermined`.

---

## Ce qui reste introuvable

Deux jeux du dépôt n'ont été trouvés nulle part, ni dans les archives locales ni en ligne
sous forme déjà harmonisée :

| fichier | entrées | état |
|---|---:|---|
| `planetary_histories.csv` | 11 bloquées | aucune source publique harmonisée ; demande une compilation manuelle avec une référence par cellule |

Les 144 autres blocages sont **corrects** : ce sont les moteurs que la règle « aucune
donnée simulée » exclut délibérément.

---

## Licences

Chaque fichier conserve la licence de sa source, portée dans `MANIFESTE.csv`.
Elles ne sont pas uniformes : CC0-1.0 pour les jeux Dryad, CC BY-SA 4.0 pour GEOROC,
GPL-3 pour OBIGT, CC BY-NC 4.0 pour SILSO, Open Government Licence v3 pour HadCRUT,
domaine public pour la NASA et la NOAA, usage académique avec citation obligatoire pour
l'IMCCE, l'UMIST, KIDA et NUBASE.

Les citations scientifiques et les DOI restent obligatoires dans toute production ORI-C.
Aucune de ces données ne devient une production ORI-C du fait d'être rassemblée ici.
