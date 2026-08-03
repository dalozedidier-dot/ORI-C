# Provenance des vecteurs JPL Horizons

Le fichier `horizons_j2000_de441.csv` contient des vecteurs cartésiens
barycentriques à l’époque J2000, JD TDB 2451545.0, obtenus par l’API officielle
NASA/JPL Horizons.

- éphéméride sélectionnée par Horizons : DE441
- centre : barycentre du Système solaire
- plan de référence : écliptique J2000
- unités reçues : UA et UA/jour
- unités stockées : UA et UA/année julienne de 365,25 jours
- corps : Soleil, huit barycentres planétaires, Pluton et cinq astéroïdes

Le fichier `horizons_j2000_de441_raw.json` conserve les requêtes et les réponses
brutes. Le script `scripts/fetch_horizons_j2000.py` permet de refaire le
téléchargement.

Sources :

- https://ssd.jpl.nasa.gov/horizons/
- https://ssd-api.jpl.nasa.gov/doc/horizons.html
- https://ssd.jpl.nasa.gov/planets/phys_par.html
- https://ssd.jpl.nasa.gov/sats/phys_par/

Empreintes SHA-256 :

| Fichier | SHA-256 |
|---|---|
| `data/horizons_j2000_de441.csv` | `1169fb0ded56dd6eae815c7c0cba692d1840e8453da4da678195fbe003e76924` |
| `data/horizons_j2000_de441_raw.json` | `0076d4c24dc4faf952fa10fcd2519d8b963d81ad913ed7f555baf5a16909d660` |

Les masses d’Iris et Bamberga ne sont pas fournies par Horizons dans cette
requête. Elles proviennent des estimations citées explicitement dans le CSV.
Cette approximation est signalée dans le rapport scientifique.
