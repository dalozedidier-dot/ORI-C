# VES-PACC-INT-01 — Pacc causal prospectif sur vésicules

**Statut au 13 août 2026 : protocole scientifique gelé, non exécuté.** Aucune nouvelle donnée de test ne doit être acquise avant l’enregistrement public du protocole, du plan de puissance et des empreintes SHA-256 du JSON et du script d’analyse.

## Question confirmatoire

Dans un système réel de vésicules d’acide décanoïque:décanol 2:1, une intervention physique ciblée qui réinitialise la trace structurale parentale `m` modifie-t-elle causalement l’accessibilité future `P_acc` sous des défis identiques, lorsque `X`, `Theta` et l’architecture expérimentale restent appariés ?

## Unité et effectif

L’unité indépendante est une population parentale physiquement séparée, incubée et manipulée indépendamment, puis scindée en trois bras. `n=48` unités sont prévues. Le seuil minimal pour la décision primaire est `n=40`. Les répétitions techniques, temps de lecture, aliquotes de défi et bras issus d’un même parent ne comptent jamais comme unités indépendantes.

## Intervention `do(m)` et sham

`m` est la distribution physique de taille des vésicules parentales, mesurée par DLS (`Z-average` et PDI), explicitement exclue de `X`.

- contrôle : matériau parental resuspendu, sans extrusion membranaire
- `do(m)` : 11 passages à travers une membrane polycarbonate track-etched de 100 nm
- sham : 11 passages dans le même appareil à travers une membrane polycarbonate de 5 µm

L’opérateur `do(m)` doit produire, au niveau de la population expérimentale, un `Z-average` médian de 80 à 150 nm et un PDI médian `<=0,25`. Le sham doit rester à `<=10 %` du contrôle pour le `Z-average` médian et à `<=0,05` de différence absolue de PDI. Aucun échantillon n’est retiré pour améliorer ces critères. Un échec rend la qualification causale stricte invalide et le résultat reste descriptif.

## Appariement `X / Theta / A`

`X` est mesuré sur le parent commun immédiatement avant la scission des bras : A400, fluorescence Nile Red I640, rapport Nile Red 610/660, fraction de fluorescence calceine retenue, pH, température et concentration totale en amphiphiles. Aucune variable DLS n’entre dans `X`.

L’architecture `A` reste commune : parent, lots de tampon et d’amphiphiles, volume final, bloc expérimental, température, instruments et répartition de plaque. Tolérances : `|ΔpH|<=0,05`, `|ΔT|<=0,5 °C`, différence relative d’amphiphiles `<=2 %`, différence de volume `<=1 %`, différence de temps de manipulation `<=2 min`.

## Défis futurs `Theta`

Douze défis sont gelés : trois apports futurs d’amphiphiles frais, `30`, `60` et `90 mM`, croisés avec quatre fenêtres de lecture, `0,5`, `1,5`, `5` et `24 h`. Chaque défi part de `80 µL` du bras parental dans un volume final de `200 µL`. Les volumes de stock 1 M sont respectivement `6`, `12` et `18 µL`, le tampon étant ajusté à `114`, `108` et `102 µL`.

## Réponse `R`, seuils et `P_acc`

Quatre dimensions sont gelées, toutes rapportées au niveau pré-intervention du même parent, normalisé à `1` : A400 `0,10`, Nile Red I640 `0,10`, rapport Nile Red 610/660 `0,05`, fraction de calceine retenue `0,10`.

`P_acc` est calculé avec `PACC-INT-CHALLENGE-V1` sur `12 × 4 = 48` cellules, à poids uniformes. Le bootstrap utilise les populations parentales, 5000 tirages, graine `20260813`. Le sham doit présenter un écart absolu maximal de `P_acc <= 0,0625`, soit au plus trois cellules sur 48 pour une unité.

## SESOI, puissance et décision

Le contraste primaire est `Delta_P_acc = P_acc_do(m) - P_acc_control`. Le signe attendu est négatif. Le SESOI est `|Delta_P_acc|=0,08`. Avec un écart-type apparié de planification de `0,15`, alpha bilatéral `0,05` et puissance cible `0,90`, l’approximation t appariée demande 39 unités. `n=40` donne environ `0,908` de puissance et `n=48` environ `0,951`.

La mesure locale de la condition §XIV-9 est acquise uniquement si la qualification causale stricte passe, quel que soit le signe observé. Le soutien direct à `INV-A` exige en plus `Delta_P_acc moyen <= -0,08` et une borne supérieure bootstrap 95 % strictement inférieure à zéro. Un résultat nul, positif ou trop petit est un non-soutien, sans redéfinition du protocole.

## Porte de préenregistrement

Les champs scientifiques sont complets. La porte d’exécution reste fermée tant que `VES-PACC-INT-01.registration.json` ne contient pas une URL publique, un horodatage antérieur aux nouvelles données et les empreintes correspondant exactement au protocole et au script d’analyse. Le JSON scientifique, ce document, `POWER_PLAN.json` et `analyser_ves_pacc_int_01.py` restent gelés. Après publication OSF, seule la couche administrative de la fiche `.registration.json` est renseignée.

## Fichiers canoniques

- `PROTOCOLE_PACC_CAUSAL_PROSPECTIF_V1.json` : définition machine gelée
- `POWER_PLAN.json` : SESOI, puissance et unité indépendante
- `analyser_ves_pacc_int_01.py` : analyse confirmatoire gelée
- `VES-PACC-INT-01.registration.json` : métadonnées administratives du préenregistrement public

## Références de méthode

Sokolskyi & Baum, *Langmuir* (2026), doi:10.1021/acs.langmuir.6c00275. Dryad doi:10.5061/dryad.fbg79cp99. Zhu, Budin & Szostak, *Methods in Enzymology* 533 (2013), doi:10.1016/B978-0-12-420067-8.00021-0. Blöchliger et al., *J. Phys. Chem. B* 102, 10383–10390 (1998), doi:10.1021/jp981234w.
