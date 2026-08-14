# Check-up complet ORI-C — 14 août 2026

## Conclusion

Le dépôt est techniquement sain à la base `70689f27fb2250f397d7944a2b05c7ef525efdcf`.
La validation locale complète passe avec l'environnement verrouillé : compilation
intégrale, validation rapide et **489 tests passés, 2 ignorés, 1 échec attendu**.
Les trois avertissements observés proviennent d'un cas synthétique à tableau vide
et de la détection du nombre de cœurs sous Windows ; aucun ne modifie un résultat.
Après ajout des six livrables de ce check-up, le manifeste racine passe de
**1 768 à 1 774 fichiers**, sans charge brute ni installateur ajouté au dépôt.

Le dépôt a scientifiquement avancé depuis les états précédents :

- le benchmark transversal comporte désormais **21 cas**, dont **6 cas complets**
  pour `X,H,m,Theta,tau,P_acc,R`, représentant **5 systèmes distincts** ;
- cette complétude ne vaut pas validation commune : elle mélange encore mesures
  rétrospectives, quantités dérivées et résultats de modèles explicitement étiquetés ;
- l'extension `HC02-E1` atteint **53/53** en reachabilité structurelle qualifiée,
  tandis que le baseline gelé reste **46/53** ;
- `VES-PACC-INT-01` et `MAG-PAIR-001` possèdent des schémas, préparateurs,
  analyses et portes machine testés ; aucune mesure prospective n'existe encore ;
- le seuil scientifique reste **7/12**, avec les conditions 3, 4, 9, 10 et 11 ouvertes.

## Vérification du plan demandé

### Réplication vivante indépendante

Wong & Seguin 2015 a été retrouvé et inspecté à sa source Dryad officielle.
Le jeu contient 46 populations évoluées, six génotypes progéniteurs, des MIC de
ciprofloxacine, des mesures de fitness et des comptes de mutations. Il n'est pas
admissible comme réplication stricte de D'Onofrio : le « passé » disponible est
le génotype fondateur, pas le traitement historique C/N gelé, chaque population
n'a qu'un MIC terminal, et les candidats d'état présent sont des variables
terminales susceptibles d'être médiatrices. Aucun seuil ni modèle n'a été changé
pour le rendre artificiellement admissible. La route LTEE avec nouvelles MIC
reste donc la bonne route prospective.

### VES-PACC-INT-01

La chaîne logicielle est complète et testée. La porte confirme : bundle absent,
résultat absent, dépendance à OSF/Zenodo limitée aux métadonnées et au droit de
revendiquer une préinscription prospective. Les éléments impossibles à produire
dans un dépôt restent : accord de laboratoire, disponibilité instrumentale,
fenêtre d'acquisition, clé aveugle hors dépôt et mesures physiques.

### MAG-PAIR-001

La chaîne logicielle est complète et testée. Le candidat public Vervelidou 2023
ne fournit pas les courbes brutes de l'expérience basalte et n'isole pas une
réponse future indépendante de la trace ; il ne ferme donc pas C03. Le pilote
instrumental sacrificiel reste nécessaire pour figer le plateau AF, le champ
test, la température et ses tolérances avant toute mesure confirmatoire.

### Pipeline transversal

Un schéma commun machine-lisible a été ajouté avec toutes les propriétés requises.
Les valeurs absentes restent explicitement `missing`; une définition, un design
ou une préparation ne sont jamais convertis en mesure. L'audit `INV-A` lit ce
bundle et conserve les niveaux empirique, dérivé et modèle.

### Cosmos, paléoclimat et §XIV

Aucune réanalyse cosmique n'est justifiée sans cohorte météoritique indépendante.
PALEO-HISTORY possède ses neuf familles normalisées, mais reste non testable sans
incertitudes chronologiques ponctuelles et vrai contrôle négatif. Aucun nouveau
résultat de ce check-up ne ferme une condition du §XIV ; le compteur reste 7/12.

## Frontière d'exécution réelle

Tout ce qui pouvait être exécuté honnêtement dans le dépôt l'a été. Les résultats
VES et MAG demandés par le plan ne sont pas des calculs manquants : ce sont deux
expériences physiques encore non réalisées. Les inventer, simuler leurs données
ou renseigner des paramètres de laboratoire non mesurés violerait le protocole
gelé et créerait de fausses preuves.
