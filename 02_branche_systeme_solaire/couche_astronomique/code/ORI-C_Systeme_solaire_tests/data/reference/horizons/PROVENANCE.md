# Série de validation JPL Horizons

`earth_elements_j2000_to_minus6kyr.csv` contient l’excentricité osculatrice et
le demi-grand axe du barycentre Terre–Lune, calculés par NASA/JPL Horizons tous
les 100 ans entre J2000 et 6 000 ans avant J2000.

- cible Horizons : `3`, barycentre Terre–Lune
- centre : `500@10`, Soleil
- type : éléments osculateurs géométriques
- plan et repère : écliptique J2000
- type de liste temporelle explicitement fixé à `JD`
- éphéméride sélectionnée par Horizons : DE441

Le script `scripts/fetch_horizons_earth_validation.py` reconstruit la requête.
Le JSON brut conserve les paramètres et la réponse intégrale.

Source : https://ssd-api.jpl.nasa.gov/doc/horizons.html

| Fichier | SHA-256 |
|---|---|
| `earth_elements_j2000_to_minus6kyr.csv` | `117eabb289dd7c53359c8d92e3cd69bb2aae51a7fc76644756fe453350faa4e4` |
| `earth_elements_j2000_to_minus6kyr_raw.json` | `b90167aa7b68d00fdf1360f58871c3e105855e325f68eb790422a0356ed3c585` |
