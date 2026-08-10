# Provenance — fréquences séculaires La2010a

Les fichiers `La2010a_secular_frequencies.csv` et
`La2010a_eccentricity_combinations.csv` sont des tables de référence dérivées,
pas de nouvelles observations ORI-C.

Source primaire : J. Laskar, A. Fienga, M. Gastineau & H. Manche (2011),
*La2010: a new orbital solution for the long-term motion of the Earth*,
Astronomy & Astrophysics 532, A89, Table 6.

La Table 6 publie les fréquences principales `g_i` et `s_i` de La2004 et
La2010a. Les quatre planètes internes sont analysées sur 20 Ma et les modes des
planètes externes sur 50 Ma. Les valeurs `Delta_100` décrivent la variation
des fréquences sur 100 Ma rapportée par les auteurs.

Le fichier des combinaisons est recalculé localement avec
`P = 1 296 000 / |g_i - g_j|`, où les fréquences sont exprimées en
arcsecondes par an. Les périodes obtenues héritent donc directement de
l'arrondi des valeurs tabulées et ne doivent pas être appelées « exactes ».

Référence de diffusion des solutions : IMCCE, *Astronomical Solutions for
Earth Paleoclimates*. L'IMCCE indique que La2010 fournit les éléments orbitaux
de la Terre de -250 Ma au présent et que La2004 doit être utilisée pour les
produits d'insolation et d'obliquité associés.
