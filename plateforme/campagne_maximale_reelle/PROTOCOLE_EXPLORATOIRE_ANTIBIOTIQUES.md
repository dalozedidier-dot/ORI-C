# Test exploratoire de l'histoire antibiotique

Ce test exploite uniquement les mesures longitudinales réelles Windels. Il ne remplace pas le protocole confirmatoire ORIC-ABX-001 : les phénotypes terminaux restent non joignables et un seul antibiotique est présent.

La cible est la prochaine survie observée en log10. Les lignées sont séparées entre apprentissage et test. Trois modèles sont comparés : état courant ; témoin flexible à six variables ; histoire à six variables comprenant moyenne, dispersion et pente antérieures. La régularisation est choisie uniquement dans l'apprentissage.

Deux cents partitions groupées servent à estimer la robustesse exploratoire. Aucun seuil confirmatoire n'est appliqué après observation. Un résultat positif justifie seulement l'acquisition d'un jeu externe avec séquences d'exposition variées et test final tenu secret.

Les sources de la revue orientent les futurs témoins : CARD et BV-BRC pour l'annotation/validation inter-souches, COBRApy pour un témoin physiologique et Tigramite pour la causalité temporelle. Leur mention ne signifie pas qu'elles ont déjà été intégrées au calcul.

