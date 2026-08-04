# Publication sur GitHub

## Formes de livraison

Le dépôt Git utilise Git LFS pour les fichiers NetCDF, GZIP, ZIP et bundles.
Le ZIP source généré automatiquement par GitHub ne télécharge pas ces objets et
ne doit jamais être présenté comme l'archive scientifique canonique.

La publication complète comprend :

1. le dépôt Git ;
2. une version taguée correspondant au fichier `VERSION` ;
3. une archive de release hydratée ;
4. le fichier SHA-256 produit avec cette archive ;
5. des notes de version décrivant les changements scientifiques et techniques.

## Préparer la copie locale

```bash
git lfs install
git lfs pull
python verifier_dossier.py
python scripts/valider_tout.py --strict-lfs
```

Le premier contrôle doit afficher zéro objet LFS non hydraté.

## Construire l'archive autonome

```bash
python scripts/construire_archive_canonique.py --output-dir dist
```

Le script refuse de produire l'archive tant qu'un pointeur Git LFS est encore
présent. Il régénère les manifestes, exécute les contrôles, crée un ZIP
déterministe et écrit son SHA-256.

## Traçabilité Git

Utiliser des messages décrivant réellement la modification, par exemple :

```text
fix: distinguish strict hypergraph closure
docs: align platform engine counts
data: publish hydrated LFS release bundle
test: add three-branch regression campaign
```

Créer ensuite un tag annoté, par exemple :

```bash
git tag -a v0.9.2-research -m "ORI-C v0.9.2-research"
git push origin main --follow-tags
```
