# Correspondance entre les protocoles et le code

## Test MPT

| Élément du protocole | Implémentation |
|---|---|
| LR04 | `data/raw/lisiecki2005-d18o-stack-noaa.txt` |
| La2004, 65°N | `data.py`, insolation journalière au solstice |
| Calibration 2,6–1,2 Ma | `mpt.py`, masque de calibration |
| Paramètres figés | une seule optimisation avant la propagation complète |
| M0 | état glaciaire, temps de réponse fixe |
| M1 | M0 avec état lent du régolithe |
| M2 | M1 avec mémoire lente du carbone |
| RMSE, corrélation, retard | `metrics.py` |
| Puissance 100/41 ka | bandes 80–120 et 39–43 ka |
| AIC/BIC | vraisemblance gaussienne sur les résidus |
| Wilcoxon | blocs contigus de 50 ka |

### Correction du protocole

Les paramètres α et R* ne peuvent pas être identifiés séparément si R n’a pas
d’unité externe fixée. Il en va de même pour β et γ dans une mémoire carbone
linéaire. Le code fixe donc les échelles de R et C. Cette correction retire deux
redondances sans retirer de mécanisme.

## Test exoplanétaire

| Élément du protocole | Implémentation |
|---|---|
| Deux histoires | trajectoires A et B prescrites |
| Même état final | égalité bit à bit après 50 Ma |
| Maintien final | 10 Ma |
| État final | moyenne sur les 2 derniers Ma |
| N = 20 | ensemble apparié, graine 729 |
| Modèle classique | température, glace et CO₂ |
| M2 | noyau classique, régolithe et carbone lents |
| Ablation | R et C fixés à une référence commune |
| Tests | Wilcoxon apparié et correction de Holm |

### Écart volontaire avec le protocole

La génération REBOUND/REBOUNDx n’est pas incluse dans ce premier calcul. Deux
trajectoires Hamiltoniennes distinctes ne convergent pas spontanément vers le
même état complet sans dissipation ou contrainte externe. Les forçages sont
donc prescrits afin d’isoler proprement la question climatique. Le code accepte
ensuite le remplacement de ces séries par des trajectoires N-corps-spin
validées.

L’EMIC est volontairement réduit. Il sert à tester la structure H3/H4 et
l’ablation. Il ne peut pas fournir une validation quantitative de
l’habitabilité ou de la productivité avant calibration sur des sorties GCM.

