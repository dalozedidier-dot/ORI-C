#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

PACKAGE=Path(__file__).resolve().parent
PAYLOAD=PACKAGE/'payload'

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def git_blob(path:Path)->str:
    b=path.read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def run(repo:Path,*cmd:str, env_extra=None)->None:
    env=os.environ.copy(); env['PYTHONUTF8']='1'; env['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    if env_extra: env.update(env_extra)
    print('+',' '.join(map(str,cmd)))
    p=subprocess.run(cmd,cwd=repo,env=env)
    if p.returncode: raise RuntimeError(f"commande en échec ({p.returncode}): {' '.join(cmd)}")

def replace_one(path:Path, old:str, new:str, label:str)->None:
    s=path.read_text(encoding='utf-8')
    if new in s: return
    if old not in s: raise RuntimeError(f'{path}: motif introuvable pour {label}')
    path.write_text(s.replace(old,new,1),encoding='utf-8',newline='\n')

def insert_after(path:Path, anchor:str, insertion:str, marker:str)->None:
    s=path.read_text(encoding='utf-8')
    if marker in s: return
    if anchor not in s: raise RuntimeError(f'{path}: ancre introuvable pour insertion')
    path.write_text(s.replace(anchor,anchor+insertion,1),encoding='utf-8',newline='\n')

def patch_public_docs(repo:Path)->None:
    # README courant : compteur générique strict + séparation puissance/preuve.
    p=repo/'README.md'
    old="La campagne stricte des 683 entrées produit **298 réussites techniques, 337 blocages, 48 protocoles non exécutables informatiquement, 0 échec et 0 erreur**. Ce compteur décrit la plateforme d’intégration et ne remplace pas les verdicts ciblés obtenus dans les campagnes de branche."
    new="La campagne générique des 683 entrées, réauditée le 7 août 2026 avec le pare-feu empirique `fail_closed_v2`, produit **9 réussites techniques, 626 blocages, 48 protocoles non exécutables informatiquement, 0 échec et 0 erreur**. Elle produit **0 verdict scientifique `supports`**. Ce compteur décrit uniquement la plateforme d’intégration et ne remplace ni les verdicts ciblés sur données réelles ni les résultats explicitement issus de modèles. Voir [`MISE_A_JOUR_PREUVES_EMPIRIQUES_2026-08-07.md`](MISE_A_JOUR_PREUVES_EMPIRIQUES_2026-08-07.md) et [`ERRATUM_SCIENTIFIQUE_v0.9.4_2026-08-07.md`](ERRATUM_SCIENTIFIQUE_v0.9.4_2026-08-07.md)."
    replace_one(p,old,new,'compteur README')
    old2='| `methodologie_puissance/` | plans de puissance a priori, simulation du pipeline complet et sorties JSON reproductibles | transversal |'
    new2='| `methodologie_puissance/` | plans de puissance et analyses de sensibilité méthodologiques ; aucune simulation de puissance n’est une preuve empirique | transversal |'
    replace_one(p,old2,new2,'description puissance')

    p=repo/'ETAT_DES_PREUVES.md'
    old='| Exécution technique | 298 réussites, 337 blocages, 48 non-exécutions, 0 échec et 0 erreur | **réexécution consolidée actuelle** |'
    new='| Exécution technique stricte | 9 réussites, 626 blocages, 48 non-exécutions, 0 échec et 0 erreur | **pare-feu empirique `fail_closed_v2`, 7 août 2026** |'
    replace_one(p,old,new,'compteur ETAT_DES_PREUVES')
    oldp="Les compteurs 235/370 conservés dans `plan_directeur/campagne_plateforme/README.md`\nappartiennent à une campagne historique. Le bilan actuel est\n`plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`."
    newp="Les compteurs 235/370 et 298/337/48 conservés dans des instantanés antérieurs appartiennent à des campagnes techniques historiques. Le bilan empirique strict courant est `plateforme/campagne_maximale_reelle/BILAN_CANONIQUE.md`. La matrice générique ne produit aucun `supports` ; les verdicts ciblés restent attachés à leurs protocoles propres."
    replace_one(p,oldp,newp,'historique ETAT_DES_PREUVES')

    p=repo/'AVANCEES_ET_DECOUVERTES_2026-08-06.md'
    insert_after(p,'Date : 6 août 2026\n','\n> **Mise à jour du 7 août 2026.** Le compteur générique `298/337/48` est un instantané technique supersédé. Le mode empirique strict courant utilise `fail_closed_v2` et donne `9/626/48`, avec 0 verdict scientifique `supports` dans la matrice générique. Les résultats ciblés ci-dessous restent attachés à leurs protocoles. Voir `MISE_A_JOUR_PREUVES_EMPIRIQUES_2026-08-07.md`.\n','Mise à jour du 7 août 2026')
    old='La campagne stricte des 683 entrées produit 298 réussites techniques, 337 blocages, 48 protocoles non exécutables informatiquement, 0 échec et 0 erreur. La campagne de recherche suivante exécute H011, `Pacc`, les vésicules, D’Onofrio et l’audit des spéléothèmes avec les données intégrées hors ligne.'
    new='Le réaudit empirique strict des 683 entrées produit 9 réussites techniques, 626 blocages, 48 protocoles non exécutables informatiquement, 0 échec et 0 erreur, avec 0 verdict `supports` dans la matrice générique. La campagne de recherche suivante conserve séparément H011, `Pacc`, les vésicules, D’Onofrio et l’audit des spéléothèmes selon leurs protocoles propres.'
    replace_one(p,old,new,'compteur AVANCEES')

    p=repo/'site/index.html'
    replace_one(p,'<article class="metric"><strong>298</strong><span>analyses exécutées</span><small>0 échec, 0 erreur</small></article>', '<article class="metric"><strong>9</strong><span>analyses exécutées</span><small>626 bloquées par le pare-feu empirique</small></article>','site index compteur')
    replace_one(p,'<article class="metric"><strong>1 238</strong><span>fichiers manifestés</span><small>contrôle SHA-256 portable</small></article>', '<article class="metric"><strong>SHA-256</strong><span>manifestes reconstruits</span><small>après chaque mise à jour</small></article>','site index manifeste')

    p=repo/'site/preuves.html'
    replace_one(p,'<article class="metric"><strong>298</strong><span>analyses exécutées</span><small>sur 683 entrées réelles</small></article>', '<article class="metric"><strong>9</strong><span>analyses exécutées</span><small>626 bloquées en mode empirique strict</small></article>','site preuves compteur haut')
    replace_one(p,'<p class="claim">Une donnée partielle ne débloque que les protocoles qu’elle mesure réellement.</p>', '<p class="claim">Une donnée partielle ne débloque que les protocoles qu’elle mesure réellement. La présence d’un fichier ne suffit jamais à créer une preuve.</p>','site preuves règle')
    replace_one(p,'<div><dt>Exécutées</dt><dd>298 réussites techniques.</dd></div>', '<div><dt>Exécutées</dt><dd>9 réussites techniques sous pare-feu empirique fail-closed.</dd></div>','site preuves exécutées')
    replace_one(p,'<div><dt>Autres statuts</dt><dd>337 blocages documentés, 48 protocoles externes, 0 échec et 0 erreur.</dd></div>', '<div><dt>Autres statuts</dt><dd>626 blocages, 48 protocoles externes, 0 échec, 0 erreur et 0 soutien scientifique issu de la matrice générique.</dd></div>','site preuves statuts')

    p=repo/'site/reproductibilite.html'
    replace_one(p,'<article class="metric"><strong>1 238</strong><span>fichiers manifestés</span><small>SHA-256 portable</small></article>', '<article class="metric"><strong>SHA-256</strong><span>manifestes reconstruits</span><small>après chaque mise à jour</small></article>','site repro manifeste')
    replace_one(p,'<article class="metric"><strong>298</strong><span>réussites techniques</span><small>337 blocages documentés</small></article>', '<article class="metric"><strong>9</strong><span>réussites techniques</span><small>626 blocages, pare-feu fail-closed</small></article>','site repro compteur')

    # Fins de ligne stables pour les tables canoniques générées par ORI-C.
    p=repo/'.gitattributes'
    marker='plateforme/campagne_maximale_reelle/data/*.csv text eol=lf'
    s=p.read_text(encoding='utf-8')
    if marker not in s:
        if not s.endswith('\n'): s+='\n'
        s+='\n# Tables canoniques générées par ORI-C : fins de ligne stables sur toutes les plateformes.\n'+marker+'\n'
        p.write_text(s,encoding='utf-8',newline='\n')

def verify_payload()->None:
    doc=json.loads((PACKAGE/'PATCH_MANIFEST.json').read_text(encoding='utf-8'))
    bad=[]
    for item in doc['files']:
        p=PAYLOAD/item['path']
        if not p.is_file() or p.stat().st_size!=item['size'] or sha256(p)!=item['sha256']: bad.append(item['path'])
    if bad: raise RuntimeError('payload invalide: '+', '.join(bad[:20]))
    print(f"Payload vérifié: {len(doc['files'])} fichiers")

def preflight(repo:Path, allow_drift:bool)->None:
    base=json.loads((PACKAGE/'BASELINE_GIT_BLOBS.json').read_text(encoding='utf-8'))['files']
    problems=[]
    for rel, allowed in base.items():
        p=repo/rel
        if not p.exists(): problems.append(f'{rel}: absent'); continue
        got=git_blob(p)
        payload=PAYLOAD/rel
        if payload.exists() and p.read_bytes()==payload.read_bytes(): continue
        # Surgical files already updated are accepted by their explicit markers.
        if rel=='README.md' and 'fail_closed_v2' in p.read_text(encoding='utf-8'): continue
        if rel=='ETAT_DES_PREUVES.md' and '9 réussites, 626 blocages' in p.read_text(encoding='utf-8'): continue
        if rel=='AVANCEES_ET_DECOUVERTES_2026-08-06.md' and 'Mise à jour du 7 août 2026' in p.read_text(encoding='utf-8'): continue
        if rel.startswith('site/') and '626 blocages' in p.read_text(encoding='utf-8'): continue
        if rel=='.gitattributes' and 'plateforme/campagne_maximale_reelle/data/*.csv text eol=lf' in p.read_text(encoding='utf-8'): continue
        if got not in allowed: problems.append(f'{rel}: blob {got} attendu {allowed}')
    if problems and not allow_drift:
        raise RuntimeError('Le dépôt ne correspond pas à la base vérifiée. Aucun fichier modifié.\n- '+'\n- '.join(problems))
    if problems:
        print('ATTENTION: dérive de base autorisée:'); [print(' -',x) for x in problems]
    else: print('Préflight Git: base compatible')

def main()->int:
    ap=argparse.ArgumentParser(description='Applique la mise à jour empirique ORI-C du 7 août 2026 et reconstruit les SHA après toutes les écritures.')
    ap.add_argument('--repo',required=True,type=Path)
    ap.add_argument('--check',action='store_true',help='Vérifie le paquet et la compatibilité du dépôt sans écrire.')
    ap.add_argument('--full-validation',action='store_true',help='Ajoute la suite complète plateforme et une réexécution temporaire des 683 entrées.')
    ap.add_argument('--allow-baseline-drift',action='store_true',help='Déconseillé: autorise une base différente des blobs contrôlés.')
    a=ap.parse_args(); repo=a.repo.expanduser().resolve()
    for req in ['build_manifest.py','verifier_dossier.py','plateforme/source_corrigee/src/oric_full/runner.py']:
        if not (repo/req).exists(): raise SystemExit(f'Ce chemin ne ressemble pas à la racine ORI-C: {repo} ({req} absent)')
    verify_payload(); preflight(repo,a.allow_baseline_drift)
    if a.check:
        print('CHECK OK - aucune écriture effectuée'); return 0

    payload_doc=json.loads((PACKAGE/'PATCH_MANIFEST.json').read_text(encoding='utf-8'))['files']
    surgical=['README.md','ETAT_DES_PREUVES.md','AVANCEES_ET_DECOUVERTES_2026-08-06.md','site/index.html','site/preuves.html','site/reproductibilite.html','.gitattributes','MANIFEST.sha256','MANIFEST.sha256.json']
    targets=sorted(set([x['path'] for x in payload_doc]+surgical))
    stamp=time.strftime('%Y%m%d-%H%M%S')
    backup=repo.parent/f'{repo.name}_backup_avant_mise_a_jour_empirique_{stamp}'
    backup.mkdir(parents=True,exist_ok=False)
    existed={}
    for rel in targets:
        src=repo/rel; existed[rel]=src.exists()
        if src.exists():
            dst=backup/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    print('Sauvegarde:',backup)

    try:
        for item in payload_doc:
            rel=item['path']; src=PAYLOAD/rel; dst=repo/rel
            dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
        patch_public_docs(repo)

        # Cette étape écrit l'audit canonique; elle doit précéder la reconstruction des manifestes.
        run(repo,sys.executable,'scripts/auditer_donnees_reelles_2026_08_07.py')
        run(repo,sys.executable,'-m','pytest','-q',
            'plateforme/source_corrigee/tests/test_empirical_firewall.py',
            'plateforme/source_corrigee/tests/test_real_data_scope.py',
            'plateforme/source_corrigee/tests/test_external_scientific_bundle.py')

        # Les deux manifestes sont reconstruits APRÈS toutes les écritures canoniques.
        run(repo,sys.executable,'build_manifest.py','build')
        run(repo,sys.executable,'build_manifest.py','verify')
        run(repo,sys.executable,'verifier_dossier.py','--allow-lfs-pointers')
        run(repo,sys.executable,'scripts/valider_barriere_empirique.py')
        run(repo,sys.executable,'scripts/valider_publication_stable.py')

        if a.full_validation:
            run(repo,sys.executable,'-m','pytest','-q','plateforme/source_corrigee/tests')
            with tempfile.TemporaryDirectory(prefix='oric_strict_683_') as td:
                out=Path(td)/'strict'
                run(repo,sys.executable,'-m','oric_full.cli','run','--all',
                    '--data-dir',str(repo/'plateforme/campagne_maximale_reelle/data'),
                    '--output-dir',str(out),'--oric-root',str(repo),'--real-data-only',
                    env_extra={'PYTHONPATH':str(repo/'plateforme/source_corrigee/src')})
                d=json.loads((out/'results.json').read_text(encoding='utf-8'))
                expected={'pass':9,'fail':0,'skip':0,'blocked':626,'error':0,'not_run':48}
                sci={'undetermined':635,'supports':0,'does_not_support':0,'inconclusive':0,'not_applicable':48}
                if d['counts']!=expected or d['scientific_counts']!=sci or d['metadata'].get('empirical_firewall')!='fail_closed_v2':
                    raise RuntimeError(f"réexécution 683 divergente: {d['counts']} / {d['scientific_counts']}")
                print('Réexécution temporaire 683 conforme:',d['counts'])
            run(repo,sys.executable,'scripts/valider_tout.py')

        # Détecte toute écriture inattendue sur un fichier manifesté pendant les validations.
        run(repo,sys.executable,'build_manifest.py','verify')
        run(repo,sys.executable,'verifier_dossier.py','--allow-lfs-pointers')
        manifest=json.loads((repo/'MANIFEST.sha256.json').read_text(encoding='utf-8'))
        print(f"MISE À JOUR OK - {len(manifest['files'])} fichiers manifestés")
        print('Sauvegarde conservée:',backup)
        return 0
    except Exception as exc:
        print('ECHEC:',exc,file=sys.stderr)
        print('Restauration automatique...',file=sys.stderr)
        for rel in reversed(targets):
            dst=repo/rel; bak=backup/rel
            if existed.get(rel):
                dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(bak,dst)
            else:
                if dst.exists(): dst.unlink()
        print('Dépôt restauré. Sauvegarde conservée:',backup,file=sys.stderr)
        return 2

if __name__=='__main__': raise SystemExit(main())
