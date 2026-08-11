#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
cert=json.loads((ROOT/'plateforme/campagne_maximale_reelle/RESULTATS_SCIENTIFIQUES_CERTIFIES.json').read_text())
entries=[]
for r in cert['resultats']:
 entries.append({'id':r['criterion_id'],'question':r['enonce'],'statut':'certifie','verdict':r['verdict'],'niveau_preuve':r['niveau_preuve'],'portee':r['portee'],'artefact':r['artefact'],'empreinte_sortie':r['artefact_sha256'],'source':r['source'],'mesures':r['mesures'],'supersede_par':None})
extra=[
 ('SPIN-ORB-EXE','spin, obliquité et insolation sous couple lunaire effectif','exploratoire','executed_model','modele_reduit','02_branche_systeme_solaire/couche_spin_orbite/resultats/summary.json'),
 ('VIAB-SPIN-01','distance des trajectoires spin-orbite à une enveloppe de référence','exploratoire','executed_not_kernel','modele_reduit','02_branche_systeme_solaire/couche_spin_orbite/resultats/viabilite/RESULTAT.json'),
 ('PID-ANT-01','information unique de l’histoire et synergie X×m sur D’Onofrio','exploratoire','executed','empirique_externe_secondaire','03_branche_vivant/benchmark_histoire_antibiotique_2026/resultats/PID_X_M_A.json'),
 ('CSTATE-01','états prédictifs à histoire finie sur séries ORI-C','exploratoire','executed_finite_proxy','methodologique','methodologie_informationnelle/RESULTATS_ETATS_CAUSAUX.json'),
 ('TOPO-MAT-01','persistance multi-seuil de l’expansion simpliciale documentaire','exploratoire','executed','structure_documentaire','01_branche_matiere/hypergraphe_transformations/resultats_topologie/RESULTAT.json'),
 ('COT-MAT-01','organisation chimique close et auto-maintenue','non_concluant','not_evaluable_missing_stoichiometry','structure_documentaire','01_branche_matiere/organisations_chimiques/resultats/DIAGNOSTIC.json'),
 ('POWER-MAT-01','puissance conjointe du futur protocole matière','exploratoire','prospective_simulation','dimensionnement','methodologie_puissance/PUISSANCE_CONJOINTE_MATIERE.json'),
 ('MPT-M2-01','formulation paléoclimatique M2 contre M1 et témoin apparié M1P','resultat_negatif','does_not_support','modele_paleoclimatique_orbitally_tuned','02_branche_systeme_solaire/couche_memoire_historique/results/mpt/summary.json'),
 ('CCM-CLIM-01','cross-mapping convergent exploratoire LR04/La2004','exploratoire','executed','observational_orbitally_tuned','02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/resultats/CCM_RESULTAT.json'),
 ('PCMCI-CLIM-01','PCMCI+ exploratoire LR04/La2004, p brutes et sans reclassement de M2','exploratoire','executed_raw_p','observational_orbitally_tuned','02_branche_systeme_solaire/couche_memoire_historique/exploratoire_causalite/resultats/PCMCI_PLUS_RESULTAT.json'),
 ('LTEE-REPLAY-01','rejeu évolutif depuis ancêtres congelés, comptes publiés','exploratoire','secondary_reanalysis','empirique_externe_table_transcription','03_branche_vivant/ltee_replay_history/resultats/RESULTAT.json'),
 ('ASSEMBLY-BRIDGE-01','comparaison ORI-C / Assembly Theory sur objets appariés','non_concluant','not_evaluable_missing_paired_observables','comparaison_formelle','comparaisons_externes/assembly_theory/DIAGNOSTIC.json')]
for id,q,statut,verdict,portee,p in extra:
 entries.append({'id':id,'question':q,'statut':statut,'verdict':verdict,'niveau_preuve':None,'portee':portee,'artefact':p,'empreinte_sortie':sha(p),'source':None,'mesures':None,'supersede_par':None})

# Généalogie cosmique : synthèse empirique stricte, séparée des certifications héritées.
gc_path=ROOT/'01_branche_matiere/genealogie_cosmique_quantitative/resultats/CLAIMS.json'
if gc_path.is_file():
 gc=json.loads(gc_path.read_text(encoding='utf-8'))
 if gc.get('schema')!='oric.gc.claims.v3': raise ValueError('schéma CLAIMS généalogie cosmique inattendu')
 for c in gc['claims']:
  cid=c['claim_id']; artefact=f'01_branche_matiere/genealogie_cosmique_quantitative/resultats/claims/{cid}.json'
  if c['verdict'].startswith('undetermined_'): statut='ouvert_empirique'
  elif c['verdict'].startswith('supports_'): statut='extension_empirique_non_preregistered'
  else: statut='extension_empirique_non_concluante'
  entries.append({'id':cid,'question':c['question'],'statut':statut,'verdict':c['verdict'],'niveau_preuve':None,'portee':f"{c['directness']} — {c['scope']}",'artefact':artefact,'empreinte_sortie':sha(artefact),'source':c.get('source_ids'),'mesures':{'stages':c.get('stages'),'mechanism':c.get('mechanism'),'preregistration':c.get('preregistration')},'supersede_par':None})

out={'schema':'oric.proofs-registry.v1','authority':'machine-readable registry; certified entries are imported byte-for-byte in status from RESULTATS_SCIENTIFIQUES_CERTIFIES.json','entries':entries}
(ROOT/'preuves/PREUVES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Markdown généré
lines=['# État des preuves','', '> **Fichier généré. Ne pas modifier à la main.** Source : `preuves/PREUVES.json`.','', 'Les certifications historiques restent inchangées. Les nouvelles analyses importées sont explicitement séparées en exploratoire, non concluant ou modèle.','', '## Résultats certifiés','', '| ID | Verdict | Niveau | Portée | Artefact |','|---|---|---|---|---|']
for e in entries:
 if e['statut']=='certifie': lines.append(f"| `{e['id']}` | **{e['verdict']}** | {e['niveau_preuve'] or '—'} | {e['portee']} | `{e['artefact']}` |")
lines += ['', '## Extensions exécutées sans reclassement des certifications','', '| ID | Statut | Verdict technique | Portée |','|---|---|---|---|']
for e in entries:
 if e['statut']!='certifie': lines.append(f"| `{e['id']}` | {e['statut']} | {e['verdict']} | {e['portee']} |")
lines += ['', '## Règle de lecture','', "Un calcul exploratoire ne devient pas une preuve certifiée par sa simple présence dans ce registre. `C-MAT-MEM-05` reste négatif, M2 reste non réussi, et `C-AST-01` reste limité au niveau modèle. Les ponts vers la théorie de la viabilité, la PID, la mécanique computationnelle, COT, CCM, LTEE et Assembly Theory sont des extensions méthodologiques ou des analyses supplémentaires. La généalogie cosmique est soumise à un pare-feu empirique propre : aucune simulation, donnée synthétique ou sortie de modèle n'entre dans ses claims. Ses 15 résultats soutenus sont des extensions empiriques initiales non préenregistrées ; la trajectoire orbitale unique reste ouverte et C-AST demeure séparé au niveau modèle.",'']
(ROOT/'ETAT_DES_PREUVES.md').write_text('\n'.join(lines),encoding='utf-8')
print(f"PREUVES.json: {len(entries)} entrées; ETAT_DES_PREUVES.md généré")
