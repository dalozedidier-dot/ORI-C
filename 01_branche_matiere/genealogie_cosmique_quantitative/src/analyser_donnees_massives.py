from __future__ import annotations
import csv,json,math,statistics
from collections import Counter
from pathlib import Path

def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def num(x):
    try:return float(x)
    except:return None
def vals(rows,key):return [num(r.get(key)) for r in rows if num(r.get(key)) is not None]
def median(rows,key):
    v=vals(rows,key); return statistics.median(v) if v else None
def mean(v):return sum(v)/len(v)
def effect_size(a,b):
    sa=statistics.stdev(a);sb=statistics.stdev(b)
    p=math.sqrt(((len(a)-1)*sa*sa+(len(b)-1)*sb*sb)/(len(a)+len(b)-2))
    return (mean(b)-mean(a))/p

def pairwise_z(rows,value_key,error_2sigma_key):
    rr=[r for r in rows if num(r.get(value_key)) is not None and num(r.get(error_2sigma_key)) not in (None,0)]
    out=[]
    for i in range(len(rr)):
        for j in range(i+1,len(rr)):
            s1=num(rr[i][error_2sigma_key])/2.0;s2=num(rr[j][error_2sigma_key])/2.0
            z=abs(num(rr[i][value_key])-num(rr[j][value_key]))/math.sqrt(s1*s1+s2*s2)
            out.append(z)
    return out

def analyse(base:Path):
    d=base/'data_massives_reelles'
    sel=json.loads((d/'IMPORT_SELECTION.json').read_text(encoding='utf-8'))
    sic=read_csv(d/'PGD_SiC_PUBLISHED_SELECTED.csv');gra=read_csv(d/'PGD_GRAPHITE_PUBLISHED_SELECTED.csv')
    sossi=read_csv(d/'SOSSI_NC_CC_MEASURED.csv');wolfer=read_csv(d/'WOLFER_TICRMO_TABLES1_3.csv')
    fuk=read_csv(d/'FUKUDA_CHONDRULE_O_CR_TI.csv');bennu25=read_csv(d/'BENNU_PRESOLAR_GRAINS_2025.csv');bennu26=read_csv(d/'BENNU_REFRACTORY_O_2026.csv')

    # T17 - published presolar-grain distributions, no unpublished SiC rows.
    type_counts=Counter(r['Type'] for r in sic)
    bytype={t:[r for r in sic if r['Type']==t] for t in ('M','X','AB','Y','Z')}
    med={}
    for t,rr in bytype.items():
        med[t]={k:{'n':len(vals(rr,k)),'median':median(rr,k)} for k in ('12C/13C','26Al/27Al','d(29Si/28Si)','d(30Si/28Si)')}
    mx_factor=med['X']['26Al/27Al']['median']/med['M']['26Al/27Al']['median']
    pg={
      'SiC_total_database_rows':sel['pgd_sic_total_rows'],'SiC_unpublished_rows_excluded':sel['pgd_sic_unpublished_excluded'],
      'SiC_admissible_published_or_partial_rows':len(sic),'graphite_admissible_rows':len(gra),'admissible_grains_total':len(sic)+len(gra),
      'SiC_type_counts':dict(sorted(type_counts.items())),'selected_SiC_type_isotope_medians':med,
      'X_to_M_median_26Al_27Al_factor':mx_factor,
      'graphite':{k:{'n':len(vals(gra,k)),'median':median(gra,k),'min':min(vals(gra,k)) if vals(gra,k) else None,'max':max(vals(gra,k)) if vals(gra,k) else None} for k in ('12C/13C','14N/15N','26Al/27Al','d(29Si/28Si)','d(30Si/28Si)')},
      'criterion':'at_least_10000_published_grains_and_X_M_26Al_median_factor_gt_100_and_opposite_Si_median_signs'
    }
    t17=(pg['admissible_grains_total']>=10000 and mx_factor>100 and med['M']['d(29Si/28Si)']['median']>0 and med['X']['d(29Si/28Si)']['median']<0 and med['M']['d(30Si/28Si)']['median']>0 and med['X']['d(30Si/28Si)']['median']<0)

    # T18 - NC/CC separation with observed values only, no missing-value imputation.
    feats=['17O','48Ca','50Ti','54Cr','54Fe','64Ni','66Zn','96Zr','94Mo','95Mo','100Ru']
    effects={}
    for f in feats:
        nc=[num(r[f]) for r in sossi if r['Reservoir']=='NC' and num(r[f]) is not None]
        cc=[num(r[f]) for r in sossi if r['Reservoir']=='CC' and num(r[f]) is not None]
        effects[f]={'NC_n':len(nc),'CC_n':len(cc),'CC_minus_NC_Cohen_d':effect_size(nc,cc)}
    loo=[]
    for i,row in enumerate(sossi):
        train=[r for j,r in enumerate(sossi) if j!=i]; dists={}
        for cls in ('NC','CC'):
            s=0.0;n=0
            for f in feats:
                x=num(row[f]); allv=[num(r[f]) for r in train if num(r[f]) is not None]; cv=[num(r[f]) for r in train if r['Reservoir']==cls and num(r[f]) is not None]
                if x is None or not cv or len(allv)<2: continue
                scale=statistics.stdev(allv)
                if scale<=0:continue
                s+=((x-mean(cv))/scale)**2;n+=1
            dists[cls]=math.sqrt(s/n) if n else float('inf')
        pred=min(dists,key=dists.get);loo.append({'sample_group':row['Chondrites'],'observed':row['Reservoir'],'predicted':pred,'features_used':sum(num(row[f]) is not None for f in feats)})
    correct=sum(x['observed']==x['predicted'] for x in loo)
    nccc={'rows':len(sossi),'isotope_systems':len(feats),'effect_sizes':effects,'leave_one_out_correct':correct,'leave_one_out_total':len(loo),'accuracy':correct/len(loo),'missing_values_imputed':0,'classifier':'deterministic_nearest_centroid_using_only_observed_features'}
    t18=(correct==len(loo) and min(abs(v['CC_minus_NC_Cohen_d']) for v in effects.values())>1.5)

    # T19 - within-Allende chondrule heterogeneity from published O-Cr-Ti table.
    allende=[r for r in fuk if r['meteorite']=='Allende']; metrics={}
    for vk,ek in [('epsilon54Cr','epsilon54Cr_2sigma'),('epsilon50Ti','epsilon50Ti_2sigma'),('Delta17O','Delta17O_2sigma_or_2SD')]:
        vv=vals(allende,vk);zz=pairwise_z(allende,vk,ek)
        metrics[vk]={'n':len(vv),'min':min(vv),'max':max(vv),'pair_count':len(zz),'pairs_gt_2sigma':sum(z>2 for z in zz),'pairs_gt_3sigma':sum(z>3 for z in zz),'fraction_gt_3sigma':sum(z>3 for z in zz)/len(zz),'max_pairwise_z':max(zz)}
    ch={'table_rows':len(fuk),'Allende_chondrules':len(allende),'metrics':metrics,'sampling_limit':'Table S6 is a literature compilation and oversized chondrules are over-represented; the test establishes measured within-meteorite heterogeneity, not a unique transport mechanism.'}
    t19=all(x['fraction_gt_3sigma']>0.70 for x in metrics.values())

    # T20 - direct Wölfer Allende subsample Ti heterogeneity, Tables 1-3 only.
    sub=[r for r in wolfer if r['group']=='Allende subsamples' and r.get('Ti_reference')=='this study']
    zz=pairwise_z(sub,'epsilon50Ti','epsilon50Ti_2sigma'); vv=vals(sub,'epsilon50Ti')
    maxpair=None
    for i in range(len(sub)):
      for j in range(i+1,len(sub)):
       if num(sub[i]['epsilon50Ti']) is None or num(sub[j]['epsilon50Ti']) is None:continue
       z=abs(num(sub[i]['epsilon50Ti'])-num(sub[j]['epsilon50Ti']))/math.sqrt((num(sub[i]['epsilon50Ti_2sigma'])/2)**2+(num(sub[j]['epsilon50Ti_2sigma'])/2)**2)
       if maxpair is None or z>maxpair['z']:maxpair={'z':z,'sample_a':sub[i]['lab_id'],'sample_b':sub[j]['lab_id']}
    wo={'dataset_rows':len(wolfer),'Allende_subsamples_n':len(sub),'epsilon50Ti_min':min(vv),'epsilon50Ti_max':max(vv),'epsilon50Ti_mean':mean(vv),'pair_count':len(zz),'pairs_gt_2sigma':sum(z>2 for z in zz),'pairs_gt_3sigma':sum(z>3 for z in zz),'fraction_gt_2sigma':sum(z>2 for z in zz)/len(zz),'max_pairwise':maxpair,'literature_Table4_used':False}
    t20=(len(sub)==12 and wo['fraction_gt_2sigma']>0.8 and wo['epsilon50Ti_max']-wo['epsilon50Ti_min']>1.5)

    # T21 - returned Bennu samples: individual presolar grains + refractory O-isotope spots.
    dio=[r for r in bennu26 if r['mineral']=='diopside']; refractory=[r for r in bennu26 if r['mineral'] in ('spinel','hibonite','olivine')]
    zs=[]
    if len(dio)==1:
        a=dio[0]
        for b in refractory:
            z=abs(num(a['Delta17O'])-num(b['Delta17O']))/math.sqrt((num(a['Delta17O_2sigma'])/2)**2+(num(b['Delta17O_2sigma'])/2)**2);zs.append(z)
    bres={'Bennu_2025_individual_presolar_grains':len(bennu25),'Bennu_2025_phase_counts':dict(sorted(Counter(r['phase'] or 'not_determined' for r in bennu25).items())),'Bennu_2026_O_isotope_spots':len(bennu26),'Bennu_2026_mineral_counts':dict(sorted(Counter(r['mineral'] for r in bennu26).items())),'refractory_spinel_hibonite_olivine_Delta17O_median':statistics.median(vals(refractory,'Delta17O')),'diopside_Delta17O':num(dio[0]['Delta17O']) if dio else None,'diopside_vs_each_refractory_min_z':min(zs) if zs else None,'diopside_vs_each_refractory_max_z':max(zs) if zs else None,'number_refractory_spots_all_gt_3sigma_from_diopside':sum(z>3 for z in zs),'interpretation_limit':'This establishes isotopic heterogeneity among measured returned-sample components; it does not by itself prove the dynamical path or transport distance.'}
    t21=(len(bennu25)>=50 and len(bennu26)>=18 and len(zs)>=10 and min(zs)>5)

    tests=[
      ('GCQ-T17','Les bases publiées de grains présolaires révèlent-elles des populations isotopiques quantitativement distinctes ?',t17,['S044','S045'],pg,'published_presolar_grain_population_structure'),
      ('GCQ-T18','La dichotomie NC/CC reste-t-elle quantitativement séparable à travers plusieurs systèmes isotopiques mesurés sans imputation ?',t18,['S043'],nccc,'multisystem_NC_CC_isotopic_separation'),
      ('GCQ-T19','Des chondres d’une même météorite montrent-ils une hétérogénéité O-Cr-Ti résolue au-delà des incertitudes ?',t19,['S047'],ch,'within_meteorite_chondrule_isotopic_heterogeneity'),
      ('GCQ-T20','Des sous-échantillons d’Allende mesurés dans une même étude montrent-ils une hétérogénéité Ti spatialement résolue ?',t20,['S046'],wo,'within_meteorite_subsample_Ti_heterogeneity'),
      ('GCQ-T21','Les échantillons retournés de Bennu contiennent-ils des composants individuels isotopiquement distincts à plusieurs niveaux ?',t21,['S010','S048'],bres,'returned_sample_multiscale_isotopic_heterogeneity')]
    claims=[]
    for tid,q,ok,sources,res,mech in tests:
        claims.append({'claim_id':tid,'question':q,'executed':True,'criterion_met':bool(ok),'verdict':'supports_'+mech if ok else 'undetermined_'+mech,'source_ids':sources,'stage_ids':['GC-E03','GC-E08','GC-E10'] if tid=='GCQ-T17' else ['GC-E08','GC-E10'] if tid in ('GCQ-T18','GCQ-T19','GCQ-T20') else ['GC-E03','GC-E07','GC-E10'],'preregistered':False,'analysis_status':'retrospective_data_rich_extension','data_policy':'published_or_primary_measured_rows_only_no_simulation_no_synthetic_no_imputation','result':res})
    audit={'schema':'oric.gc.massive-real-data-audit','normalized_input_files':7,'imported_rows':len(sic)+len(gra)+len(sossi)+len(wolfer)+len(fuk)+len(bennu25)+len(bennu26),'published_presolar_grains':len(sic)+len(gra),'unpublished_SiC_rows_excluded':sel['pgd_sic_unpublished_excluded'],'synthetic_rows_used':0,'imputed_rows_used':0,'simulation_rows_used':0,'duplicate_spreadsheet_formats_used_as_independent_data':0,'selection_manifest':'data_massives_reelles/IMPORT_SELECTION.json'}
    result={'schema':'oric.gc.quantitative-massive-data-results','authority':'extension_quantitative_empirique_data_rich_retrospective','tests_total':len(tests),'criteria_met':sum(c['criterion_met'] for c in claims),'all_criteria_met':all(c['criterion_met'] for c in claims),'audit':audit,'presolar_grains':pg,'NC_CC':nccc,'Allende_chondrules':ch,'Allende_subsamples':wo,'Bennu_returned_samples':bres,'global_result':{'distribution_level_testing_now_available':True,'history_encoded_in_material_distributions_supported':all(c['criterion_met'] for c in claims),'unique_end_to_end_cosmic_genealogy_closed':False,'interpretation':'Les distributions individuelles renforcent la démonstration que l’histoire est physiquement inscrite dans des populations, réservoirs et sous-échantillons mesurables. Elles ne ferment pas une trajectoire causale unique du primordial au présent.'}}
    return result,{'schema':'oric.gc.quantitative-massive-data-tests','tests':[{'test_id':c['claim_id'],'executed':c['executed'],'criterion_met':c['criterion_met'],'verdict':c['verdict']} for c in claims]}, {'schema':'oric.gc.quantitative-massive-data-claims','claims':claims},audit
