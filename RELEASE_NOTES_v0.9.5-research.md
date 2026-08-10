# ORI-C v0.9.5-research

Publication stable du snapshot scientifique du **10 août 2026**.

## Résultats conservés sans embellissement

- **Astronomie N-corps : 13 / 15.** Les interventions Jupiter/Saturne restent détectables bien au-dessus des planchers numériques sélectionnés. Les deux critères échoués restent visibles.
- **Paléoclimat M2 : 1 / 10.** M2 reste non soutenu ; face à M1P de même complexité, 0 critère sur 5 est réussi. Aucun nouvel outil exploratoire ne modifie ce verdict.
- **D’Onofrio : E2**, **vésicules : E2 et E4**, **astronomie : E4_model**, **matière transversale : does_not_support**. Les certifications existantes sont conservées.

## Système solaire

La branche comprend maintenant trois couches explicitement séparées : N-corps, spin-orbite, mémoire historique. Le module spin séculaire propage la normale orbitale jusqu’à l’obliquité et l’insolation. Sur 2 Ma, le témoin avec couple lunaire effectif reste entre environ 22,09° et 24,44°, tandis que l’ablation du couple lunaire explore environ 1,25° à 45,04° dans ce modèle réduit. La validation La2004 et la convergence numérique sont conservées.

Cette couche **ne résout pas** l’orbite lunaire mensuelle, les marées ni l’évolution de la distance Terre-Lune.

## Chaîne de preuve publique

- `preuves/PREUVES.json` : registre machine des statuts et empreintes.
- `preuves/CHIFFRES.json` : chiffres canoniques reliés aux sorties machine.
- `ETAT_DES_PREUVES.md` : vue générée.
- GitHub Pages synchronisé sur ces valeurs et sur la frontière scientifique de la release.

## Formalismes externes

Viabilité, PID, états causaux finis, topologie persistante, COT, puissance conjointe matière, CCM, PCMCI+, LTEE et Assembly Theory sont intégrés comme extensions **exploratoires, méthodologiques ou non concluantes** selon le registre. Le PCMCI+ du run complet est versionné comme diagnostic exploratoire et ne requalifie pas M2.

## Publication et intégrité

La release reconstruit les sous-manifestes mémoire et revue systématique, puis le manifeste racine en dernier. L’archive canonique hydratée et son SHA-256 sont produits par le workflow `Publication stable ORI-C`.

La licence du code est MIT. Les autres contenus suivent la carte de `LICENSING.md`.
