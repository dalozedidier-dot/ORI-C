# VES-PACC-INT-01 — paquet laboratoire

Le protocole scientifique reste gelé. Ce document ne change aucun seuil, aucune dose ni aucune règle de décision.

## Ce qui est déjà directement compatible avec la littérature de référence

Sokolskyi & Baum 2026 (`doi:10.1021/acs.langmuir.6c00275`) utilisent le même système 2:1 acide décanoïque:décanol et documentent A400, Nile Red, calcein et DLS/Zetasizer. ORI-C ajoute une intervention `do(m)` par extrusion 100 nm, un sham 5 µm et le calcul prospectif `P_acc` déjà gelé.

## Instrumentation minimale

- lecteur de plaque capable de A400 et fluorescence Nile Red / calcein ;
- DLS pour Z-average et PDI ;
- mini-extrudeur compatible membranes track-etched 100 nm et 5 µm ;
- pipetage 96 puits, contrôle pH et température ;
- possibilité de conserver les codes d'armement aveugles jusqu'au gel de la table d'analyse.

## Candidats identifiés sans prétendre à une collaboration

1. **Baum Lab, University of Wisconsin-Madison** : laboratoire du système expérimental de référence.
2. **ULB EMNS** : Zetasizer Ultra + UV-Vis + spectrofluorimétrie.
3. **ULB BioMatter** : lecteur TECAN Spark X UV/fluorescence et infrastructure humide.

Une exécution ULB pourrait combiner EMNS pour DLS et BioMatter/plateforme équivalente pour les lectures de plaque. Cela doit être confirmé par les responsables avant tout gel administratif.

## Gate

Aucune donnée prospective n'est autorisée tant que `VES-PACC-INT-01.registration.json` n'indique pas `publicly_registered` avec URL et horodatage antérieurs à la première mesure. Le pilote technique éventuel doit être explicitement séparé et ne peut servir ni à recalibrer les seuils gelés ni à compter comme résultat prospectif.
