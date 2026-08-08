# Politique de licence

Depuis le 8 août 2026, ORI-C abandonne le régime unique « tous droits réservés »
au profit de licences séparées par nature de contenu. Ce changement est
**explicite et non rétroactif** : les versions publiées avant cette date restent
sous leur régime d'origine, conformément à ce que la version `0.9.4-research`
annonçait.

Ce fichier fait autorité en cas de doute.

---

## La carte

| contenu | licence | fichier de référence |
|---|---|---|
| **Code** — `.py`, `.yml`, `.sh`, `.bat`, notebooks | **MIT** | `LICENSE` |
| **Données produites par ORI-C** — tables canoniques, résultats, manifestes, JSON de campagne | **CC BY 4.0** | `LICENSES/CC-BY-4.0.txt` |
| **Tables dérivées de GEOROC** | **CC BY-SA 4.0** | `LICENSES/CC-BY-SA-4.0.txt` |
| **Table dérivée de CHNOSZ OBIGT** | **GPL-3.0** | `LICENSES/GPL-3.0.txt` |
| **Articles, PDF, DOCX, figures** | tous droits réservés | ci-dessous |
| **Données tierces brutes** | licence de leur source, inchangée | `SOURCE.json` de chaque jeu |

## Pourquoi deux exceptions virales

Ouvrir le dépôt ne permet pas de relicencier ce qui ne nous appartient pas. Deux
tables sont des **adaptations** de sources dont la licence impose sa propre
propagation. Les placer sous CC BY 4.0 serait juridiquement faux.

### `plateforme/campagne_maximale_reelle/data/late_accretion_tracers.csv`

Dérivée de la compilation GEOROC / DIGIS, doi `10.25625/2JETOA`, publiée sous
**CC BY-SA 4.0**. Le partage à l'identique se propage aux œuvres dérivées : cette
table et toute table qui en dérive restent sous CC BY-SA 4.0. Attribution
obligatoire à GEOROC / DIGIS, Université de Göttingen.

### `plateforme/campagne_maximale_reelle/data/thermochemical_phases.csv`

Calculée à partir des paramètres thermodynamiques de la base OBIGT du paquet
CHNOSZ, distribuée sous **GPL-3.0**. Le statut d'une table de valeurs dérivée
d'un jeu de données sous GPL n'est pas tranché en droit. Par prudence, elle est
distribuée sous GPL-3.0 et attribuée à CHNOSZ. Quiconque souhaite la réutiliser
sous un autre régime doit recalculer les valeurs depuis une source dont la
licence le permet.

## Ce qui reste fermé, et pourquoi

Les **textes** — articles, dossier scientifique, PDF, DOCX — et les **figures**
restent sous « tous droits réservés ». Ce sont des œuvres rédactionnelles dont
l'ouverture n'apporte rien à la reproductibilité : le code et les données
suffisent à rejouer et à vérifier chaque résultat. La citation reste évidemment
libre dans les conditions ordinaires du droit d'auteur.

## Ce que cela débloque

- **Forker** le dépôt et réutiliser le code sans autorisation préalable.
- **Citer** et redistribuer les données produites, avec attribution.
- **Contribuer** : les correctifs et extensions sont recevables, la
  contribution est régie par `CONTRIBUTING.md`.
- **Archiver** sur Zenodo avec un DOI, et être indexé comme dépôt ouvert.

## Ce que cela ne change pas

Les jeux tiers intégrés pour la reproductibilité conservent leur attribution,
leur DOI et leurs conditions propres, inscrits dans leur `SOURCE.json` et dans
`EXTERNAL_DATA_MANIFEST.csv`. Leur présence dans le dépôt ne transfère aucun
droit, ni à ORI-C ni à ses réutilisateurs. Les DOI et les citations
scientifiques restent obligatoires dans toute production dérivée.
