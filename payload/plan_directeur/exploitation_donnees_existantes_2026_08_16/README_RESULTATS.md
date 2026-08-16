# Synthèse scientifique corrigée des sept axes

Cette synthèse distingue les résultats réellement recalculés dans le paquet des résultats historiques conservés pour traçabilité. Le score §XIV reste 7/12. Aucun seuil n'est déplacé et aucun résultat négatif n'est requalifié.

## 1. Vésicules

Les 59,328 mesures temporelles sont réellement recalculées. Entre 2 et 6 h, la pente A400 de FR gen1 dépasse FU de 0.0566365865 A400/h, UR de 0.0395212392 et UU de 0.0245737981. Les trois permutations donnent p = 0,00005. Le contraste Pacc historique reste -0,0375 avec IC95 [-0,1458333333 ; 0,0625]. La dynamique temporelle est donc informative alors que ce proxy discret final reste négatif.

## 2. Watkins

Les 209 essais de `exp.zip` sont inclus. La reconstruction physique des sorties est reproduite avec une séparation nette : max sans bascule = 0,9986572266 et min avec bascule = 48,7998962402 pour le seuil brut 25. Les métriques du classifieur de la conversation précédente restent historiques : X seul = 26.79 %, X+H = 30.62 %, gain = 3.83 points, sous le seuil gelé de 10 points. Le script exact du classifieur précédent n'étant plus récupérable, ces métriques ne sont pas présentées comme un nouveau rerun.

## 3. Endosymbiose

Les 85 génomes et 15,810 appels HMM sont recalculés. Les rétentions moyennes sont traduction 0.925, transcription 0.735, réplication 0.653, enveloppe 0.499, PMF 0.464. Dans le quartile le plus réduit, traduction = 0.802, enveloppe = 0.095. Friedman p = 1.036e-41.

## 4. Gajrani

Le benchmark causal H -> m -> R est rerun depuis le brut inclus. Le Pacc rétrospectif de rétention au jour 12 donne ΔPacc = -0.0807291667, IC95 [-0.1145833333 ; -0.0416666667]. Il reste hors PACC-INT strict. En extension descriptive, il porte opérationnellement X, H, m, Θ, τ, Pacc et R, sans ajouter de point au §XIV.

## 5. AICC2023

Les chronologies et incertitudes sont recalculées depuis `AICC2023.zip`. Pour EDC, n = 5,806, âge maximal = 813.4067 ka. La médiane de sigma vaut 0.066 ka entre 0 et 100 ka et 2.37 ka entre 600 et 850 ka. La présence d'incertitudes d'âge réelles est confirmée.

## 6. Accrétion tardive et biais de publication

Le tableau d'accrétion tardive contient 122,159 mesures, 29,461 échantillons avec au moins deux traceurs et 7,827 avec au moins quatre. La fraction d'incertitudes renseignées est 0.0. Ces données soutiennent un audit multitraceur, pas un modèle de mélange calibré sans pôles et incertitudes adaptés. Le constat SiC de 20 432 grains dont 11 567 non publiés exclus, soit 56,61 %, reste un résultat historique du dépôt précédent. Le brut non publié n'est pas recréé.

## 7. Réfutations et généralité

Watkins reste négatif au seuil gelé. Yen-Papin reste historiquement à 1.95 % de gain, puis 0.265 % lorsque la MIC de jour 20 entre dans X. MPT-M2 reste négatif. Cet ensemble soutient une condition de domaine importante : lorsque X encode suffisamment l'état présent et les traces utiles du passé, l'apport résiduel de H peut disparaître.

La séparation hypergraphe reste 46/53 pour le baseline gelé et 53/53 pour l'extension HC02-E1. Ces deux nombres ne doivent pas être fusionnés. Windels reste aveugle.

## État de livraison

Le précédent audit décrivait 47 fichiers de campagne et 663 433 lignes CSV. Quarante-trois payloads exacts ont été récupérés avec leur SHA-256. Quatre payloads exacts ne sont plus accessibles et sont explicitement listés. Le paquet ne remplace aucune donnée absente par une version plus ancienne portant un autre hash.
