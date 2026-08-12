# Dépôt public OSF des quatre prédictions prospectives ORI-C

Les quatre paquets présents dans ce dossier sont scientifiquement gelés avant
les données de test. Le dépôt OSF sert uniquement à leur donner un horodatage
public et persistant. Les hypothèses, seuils, témoins et règles de décision ne
doivent plus être modifiés après cet enregistrement.

Une seule registration OSF peut contenir les quatre prédictions si les huit
fichiers source/registration sont tous archivés ensemble. Dans ce cas, la même
URL publique et le même DOI peuvent être reportés dans les quatre fiches
`.registration.json`.

Après publication OSF, utiliser
`appliquer_enregistrement_osf.py` pour renseigner uniquement les métadonnées
publiques (`public_url`, `registered_at`, éventuellement `doi`). Le script
vérifie auparavant l'empreinte SHA-256 du protocole scientifique source et ne
modifie aucun champ de prédiction.

Exemple :

```bash
python plan_directeur/campagne_centrale_2026_08_11/PREDICTIONS_PROSPECTIVES/ENREGISTREMENTS_PUBLICS/appliquer_enregistrement_osf.py \
  --all \
  --public-url https://osf.io/XXXXX \
  --registered-at 2026-08-13 \
  --doi 10.17605/OSF.IO/XXXXX
```

Le statut `publicly_registered` ne constitue pas un succès prédictif. Il rend
simplement possible qu'un futur résultat hors échantillon soit évalué comme
préenregistré publiquement.
