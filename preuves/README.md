# Registres d'autorité des preuves

- `PREUVES.json` : registre machine lisible des verdicts certifiés et des extensions exploratoires/non concluantes.
- `CHIFFRES.json` : nombres canoniques reliés à une sortie machine et, lorsque nécessaire, à leurs rendus publics.

`ETAT_DES_PREUVES.md` est généré par `scripts/construire_registre_preuves.py`. Le validateur `scripts/valider_registre_preuves.py` vérifie les empreintes des artefacts, la conservation des cinq certifications spécialisées et l'égalité des chiffres avec leurs sources.
