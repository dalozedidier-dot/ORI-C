from __future__ import annotations

from pathlib import Path
import json
import math
import numpy as np
import pandas as pd


def generate_all(data_dir: Path, seed: int = 0) -> dict[str, int]:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    counts: dict[str, int] = {}

    def save(name: str, frame: pd.DataFrame) -> None:
        frame.to_csv(data_dir / name, index=False)
        counts[name] = len(frame)

    # Socle
    save("states.csv", pd.DataFrame([
        {"system_id": f"S{i}", "time": t, "state_json": json.dumps({"x": float(np.sin(t+i)), "m": i % 3})}
        for i in range(5) for t in range(6)
    ]))
    relation_types = ["DESC", "TRANS", "ASSOC", "INTG", "CLOS", "PERT", "COND", "HERIT"]
    save("relations.csv", pd.DataFrame([
        {"source": f"TR-{i:03d}", "target": f"TR-{i+1:03d}", "relation_type": relation_types[i % len(relation_types)]}
        for i in range(1, 40)
    ] + [
        {"source": "TR-005", "target": "TR-010", "relation_type": "COND"},
        {"source": "TR-012", "target": "TR-020", "relation_type": "HERIT"},
        {"source": "TR-021", "target": "TR-028", "relation_type": "PERT"},
    ]))

    # Matière
    transitions = []
    for i in range(40):
        regime = i // 5
        values = rng.normal(loc=regime / 7, scale=0.15, size=6)
        transitions.append({
            "transition_id": f"TR-{i+1:03d}",
            "before_state": f"R{regime}_S{i%5}",
            "after_state": f"R{min(regime+1,7)}_S{(i+1)%5}",
            "n": values[0], "G": values[1], "I": values[2], "E": values[3], "Pi": values[4], "H": values[5],
            "evidence_level": int(1 + i % 4),
        })
    save("matter_transitions.csv", pd.DataFrame(transitions))

    elements = ["H", "He", "C", "N", "O", "Mg", "Si", "Fe", "Ni", "Sr", "Ba", "Eu"]
    yields = []
    for source in range(60):
        mass = rng.choice([1.5, 3, 8, 15, 25, 40])
        metallicity = rng.choice([0.0001, 0.001, 0.01, 0.02])
        for j, element in enumerate(elements):
            base = math.exp(-abs(j - mass/5) / 4) * (1 + metallicity * 5)
            yields.append({"source_id": f"SRC{source:03d}", "mass_solar": mass, "metallicity": metallicity, "element": element, "yield_mass": max(base + rng.normal(0, 0.03), 1e-6), "uncertainty": 0.05 + 0.02*rng.random()})
    save("nucleosynthesis_yields.csv", pd.DataFrame(yields))

    species = ["H", "H2", "O", "OH", "H2O", "C", "CO", "CO2", "N", "NH", "NH2", "NH3", "CH3OH", "HCN"]
    reactions = []
    for i in range(len(species)-1):
        reactions.append({"reaction_id": f"RX{i:03d}", "reactants": species[i], "products": species[i+1], "rate": 1e-10*(1+i/10), "temperature_min": 10 + 5*(i%3), "temperature_max": 300 - 5*(i%4)})
    reactions += [
        {"reaction_id": "RX100", "reactants": "H+H", "products": "H2", "rate": 2e-10, "temperature_min": 5, "temperature_max": 1000},
        {"reaction_id": "RX101", "reactants": "H2+O", "products": "OH+H", "rate": 1e-11, "temperature_min": 20, "temperature_max": 1000},
        {"reaction_id": "RX102", "reactants": "OH+H2", "products": "H2O+H", "rate": 5e-11, "temperature_min": 20, "temperature_max": 1000},
    ]
    save("reaction_network.csv", pd.DataFrame(reactions))
    save("molecular_inventory.csv", pd.DataFrame([
        {"environment_id": f"ENV{e}", "species": s, "abundance": 10**rng.uniform(-12,-4), "uncertainty": rng.uniform(0.05,0.3)}
        for e in range(8) for s in species
    ]))

    phases = ["CAI", "Fe_metal", "forsterite", "enstatite", "troilite", "water_ice", "CO2_ice"]
    thermo = []
    for temp in np.linspace(100, 1800, 45):
        for pressure in [1e-6, 1e-4, 1e-2]:
            for idx, phase in enumerate(phases):
                optimal = [1650, 1370, 1350, 1250, 700, 170, 80][idx]
                gibbs = ((temp-optimal)/250)**2 + 0.05*np.log10(pressure+1e-12)**2 + rng.normal(0,0.02)
                thermo.append({"phase": phase, "temperature": temp, "pressure": pressure, "gibbs_energy": gibbs, "composition": phase})
    save("thermochemical_phases.csv", pd.DataFrame(thermo))

    # Planètes
    tracers = ["Ti", "Cr", "Mo", "W", "Ni", "Ru", "Pd"]
    iso = []
    for i in range(80):
        group = "CC" if i < 40 else "NC"
        shift = 1.2 if group == "CC" else -1.2
        for j, tracer in enumerate(tracers):
            iso.append({"sample_id": f"MET{i:03d}", "group": group, "tracer": tracer, "value": shift*(1+j/10)+rng.normal(0,0.35), "uncertainty": 0.1+rng.random()*0.05})
    save("isotope_tracers.csv", pd.DataFrame(iso))

    save("chronometers.csv", pd.DataFrame([
        {"sample_id": f"MET{i:03d}", "system": system, "age_myr": rng.uniform(0.2,6.0), "uncertainty_myr": rng.uniform(0.02,0.3)}
        for i in range(50) for system in ["Al-Mg", "Hf-W", "Mn-Cr", "Pb-Pb"]
    ]))
    bodies = []
    for i in range(80):
        bodies.append({"body_id": f"B{i:03d}", "radius_km": rng.uniform(5,300), "density": rng.uniform(2000,4500), "porosity": rng.uniform(0.02,0.45), "formation_time_myr": rng.uniform(0.2,5), "al26_ratio": rng.uniform(0.2,1.5)})
    save("body_properties.csv", pd.DataFrame(bodies))

    part = []
    for i in range(500):
        element = rng.choice(["Fe","Ni","Co","Nb","Ta","W","Mo","N","P","C","S","Os","Ir","Au"])
        p = rng.uniform(1,70); temp = rng.uniform(1500,4000); diw = rng.uniform(-5,1)
        element_shift = (hash(element)%17-8)/10
        logd = 0.02*p - 0.0004*(temp-2500) - 0.55*diw + element_shift + rng.normal(0,0.35)
        part.append({"experiment_id": f"EXP{i:04d}", "element": element, "pressure_gpa": p, "temperature_k": temp, "delta_iw": diw, "logD": logd, "uncertainty": rng.uniform(0.05,0.25)})
    save("partition_experiments.csv", pd.DataFrame(part))

    volatile_rows = []
    for i in range(100):
        volatile = rng.choice(["H2O","C","N","S"])
        initial = rng.uniform(1,100)
        fractions = rng.dirichlet([1.5,3,1.2,2.5])
        volatile_rows.append({"sample_id": f"V{i:03d}", "volatile": volatile, "initial_mass": initial, "core_mass": initial*fractions[0], "mantle_mass": initial*fractions[1], "atmosphere_mass": initial*fractions[2], "lost_mass": initial*fractions[3]})
    save("volatile_inventory.csv", pd.DataFrame(volatile_rows))

    late = []
    for i in range(120):
        source = rng.choice(["CC", "NC", "mixed"])
        shift = {"CC":1.0,"NC":-0.7,"mixed":0.2}[source]
        late.append({"sample_id": f"LA{i:03d}", "tracer": rng.choice(["Mo","Ru","W","Os","Ir","Au"]), "final_value": shift+rng.normal(0,0.3), "uncertainty": rng.uniform(0.05,0.2), "candidate_source": source})
    save("late_accretion_tracers.csv", pd.DataFrame(late))

    histories = []
    for i in range(240):
        init = rng.choice(["reduced","mixed","oxidized"]); prov = rng.choice(["CC","NC","mixed"])
        acc = rng.choice(["early","intermediate","late"]); thermal = rng.choice(["cold","partial_melt","magma_ocean"])
        redox = rng.choice(["reducing","moderate","oxidizing"]); loss = rng.choice(["low","medium","high"]); late_in = rng.choice(["none","CC","NC"])
        final = f"{redox}_{thermal}_{late_in}_{'retained' if loss!='high' else 'depleted'}"
        histories.append({"body_id": f"PB{i:03d}", "initial_composition": init, "provenance": prov, "accretion_time": acc, "thermal_history": thermal, "redox_history": redox, "losses": loss, "late_inputs": late_in, "final_partition": final})
    save("planetary_histories.csv", pd.DataFrame(histories))

    # Astronomie
    initial = []
    for name, a, mass in [("Mercury",0.39,1.65e-7),("Venus",0.72,2.45e-6),("Earth",1.0,3.0e-6),("Mars",1.52,3.2e-7),("Jupiter",5.2,9.54e-4),("Saturn",9.54,2.86e-4)]:
        initial.append({"body":name,"epoch":"J2000","x":a,"y":0,"z":0,"vx":0,"vy":2*np.pi/np.sqrt(a),"vz":0,"mass":mass})
    save("orbital_initial_conditions.csv", pd.DataFrame(initial))
    eph = []
    for t in np.linspace(0,100,1001):
        for row in initial:
            a=row["x"]; angle=2*np.pi*t/(a**1.5)
            eph.append({"time":t,"body":row["body"],"x":a*np.cos(angle),"y":a*np.sin(angle),"z":0,"vx":-a*np.sin(angle),"vy":a*np.cos(angle),"vz":0})
    save("ephemerides.csv", pd.DataFrame(eph))
    t = np.linspace(0,2000,8000)
    orbital = pd.DataFrame({"time":t,"eccentricity":0.03+0.01*np.sin(2*np.pi*t/100)+0.005*np.sin(2*np.pi*t/405),"obliquity":23.4+1.2*np.sin(2*np.pi*t/41),"precession":np.sin(2*np.pi*t/23)+0.4*np.sin(2*np.pi*t/19)})
    save("orbital_timeseries.csv", orbital)
    ref_rows=[]
    for col in ["eccentricity","obliquity","precession"]:
        for tt,val in zip(t[::20],orbital[col].to_numpy()[::20]+rng.normal(0,0.001,len(t[::20]))):
            ref_rows.append({"time":tt,"observable":col,"value":val,"uncertainty":0.002})
    save("orbital_reference.csv",pd.DataFrame(ref_rows))

    # Climat
    tc=np.linspace(0,1200,2401)
    f1=np.sin(2*np.pi*tc/41); f2=np.sin(2*np.pi*tc/100)
    memory=np.convolve(f1,np.exp(-np.arange(300)/80)/80,mode='full')[:len(tc)]
    target=0.5*f1+0.8*f2+1.2*memory+rng.normal(0,0.15,len(tc))
    save("paleoclimate_timeseries.csv",pd.DataFrame({"time_kyr":tc,"target":target,"forcing_1":f1,"forcing_2":f2}))

    modern=[]
    dates=pd.date_range('1950-01-01',periods=900,freq='MS')
    temp=np.linspace(0,1.4,len(dates))+0.15*np.sin(np.arange(len(dates))*2*np.pi/12)+rng.normal(0,0.08,len(dates))
    ocean=np.convolve(temp,np.exp(-np.arange(120)/36)/36,mode='full')[:len(temp)]
    for region,scale in [("global",1.0),("north",1.15),("south",0.85)]:
        for variable,values in [("temperature",scale*temp),("ocean_heat",scale*ocean),("soil_moisture",-0.3*scale*temp+rng.normal(0,0.1,len(temp)))]:
            modern.extend({"time":i,"variable":variable,"value":v,"region":region} for i,v in enumerate(values))
    save("modern_climate_timeseries.csv",pd.DataFrame(modern))

    ensemble=[]
    for model in range(6):
        for scenario,slope in [("low",0.015),("mid",0.025),("high",0.04)]:
            for member in range(8):
                value=0.0
                for year in range(2020,2101):
                    value += slope+rng.normal(0,0.01)
                    ensemble.append({"model":f"M{model}","scenario":scenario,"member":member,"time":year,"variable":"warming","value":value,"region":"global"})
    save("modern_climate_ensemble.csv",pd.DataFrame(ensemble))

    # Prébiotique et vivant
    design=[]
    for i,(temp,ph,cycles,uv,mineral) in enumerate([(t,p,c,u,m) for t in [25,50,80] for p in [5,7,9] for c in [0,10] for u in [0,1] for m in ["none","clay"]]):
        for rep in range(3):
            design.append({"condition_id":f"C{i:03d}","temperature":temp,"ph":ph,"wet_dry_cycles":cycles,"uv_flux":uv,"mineral":mineral,"replicate":rep})
    save("prebiotic_design.csv",pd.DataFrame(design))

    lineages=[]
    for root in range(30):
        parent=""
        cumulative=0.4+rng.random()*0.2
        for generation in range(8):
            lid=f"P{root:03d}G{generation:02d}"
            cumulative=np.clip(cumulative+rng.normal(0.04,0.03),0,1)
            lineages.append({"lineage_id":lid,"parent_id":parent,"generation":generation,"condition_id":f"C{root%20:03d}","yield":np.clip(cumulative+rng.normal(0,0.08),0,1),"polymer_length":max(1,5+generation*3+rng.normal(0,2)),"compartment_stability":np.clip(0.2+generation*0.08+rng.normal(0,0.05),0,1),"copy_fidelity":np.clip(0.5+generation*0.06+rng.normal(0,0.03),0,1)})
            parent=lid
    save("prebiotic_lineages.csv",pd.DataFrame(lineages))

    cell=[]
    components=[("membrane","compartmentalization"),("ribosome","translation"),("nucleus","genome_control"),("mitochondrion","energy"),("cytoskeleton","transport"),("proteasome","quality_control")]
    for taxon in ["animal","plant","fungus","protist"]:
        for comp,func in components:
            cell.append({"taxon":taxon,"component":comp,"origin":"ancestral" if comp not in ["mitochondrion"] else "endosymbiotic","function":func,"dependency":"membrane" if comp!="membrane" else "","evidence_level":rng.integers(2,5)})
    save("cell_architecture.csv",pd.DataFrame(cell))

    endo=[]
    for i in range(40):
        endo.append({"event_id":f"E{i:03d}","host":rng.choice(["archaea","eukaryote"]),"symbiont":rng.choice(["alphaproteobacteria","cyanobacteria","bacteria"]),"gene_transfer":rng.uniform(0.3,1),"metabolic_integration":rng.uniform(0.2,1),"dependency":rng.uniform(0.2,1),"evidence_level":rng.integers(1,5)})
    save("endosymbiosis_events.csv",pd.DataFrame(endo))

    cases=[]
    for i in range(180):
        state=f"S{i%12}"; history=f"H{i%5}"; future=f"F{(i%12 + i%5)%7}"
        cases.append({"case_id":f"BIO{i:03d}","domain":rng.choice(["cell","endosymbiosis","evolution"]),"history":history,"state":state,"future_outcome":future,"oric_features":json.dumps({"D":i%3,"H":i%2,"L":i%4})})
    save("biology_cases.csv",pd.DataFrame(cases))

    # Antibiotiques
    design_rows=[]; cycle_rows=[]; measure_rows=[]; lineage_rows=[]
    antibiotics=["A","B"]
    for arm in range(8):
        schedule_type=arm%4
        design_rows.append({"arm_id":f"A{arm:02d}","species":"E_coli","antibiotic":"A+B" if arm>=4 else antibiotics[arm%2],"schedule":str(schedule_type),"dose":1.0,"replicates":8})
        for rep in range(8):
            lineage=f"A{arm:02d}R{rep:02d}"
            cumulative=0.0; mic=1.0
            parent=""
            for cycle in range(1,21):
                if schedule_type==0: ab="A"; dose=0.5+0.08*cycle
                elif schedule_type==1: ab="B"; dose=0.5+0.08*cycle
                elif schedule_type==2: ab=antibiotics[cycle%2]; dose=1.2
                else: ab=antibiotics[(cycle//5)%2]; dose=0.8 if cycle%5 else 2.0
                cumulative+=dose
                path_bonus=(0.025 if ab=="A" else 0.018)*(1+0.2*schedule_type)
                mic=max(0.2,mic*np.exp(path_bonus*dose+rng.normal(0,0.025)))
                cycle_rows.append({"lineage_id":lineage,"cycle":cycle,"antibiotic":ab,"dose":dose,"duration":1.0,"recovery_duration":1.0})
                measure_rows.append({"lineage_id":lineage,"cycle":cycle,"mic":mic,"lag_time":1+0.05*cycle+rng.normal(0,0.1),"growth_rate":max(0.1,1.2-0.02*cycle+rng.normal(0,0.04)),"survival":np.clip(0.1+0.03*cycle+rng.normal(0,0.03),0,1),"persister_fraction":np.clip(0.001*np.exp(0.08*cycle)+rng.normal(0,0.0005),0,1),"fitness":max(0.1,1-0.015*cycle+rng.normal(0,0.03))})
                mut=f"g{(arm+cycle)%15}:{cycle%4}"
                lineage_rows.append({"lineage_id":lineage,"parent_id":parent,"cycle":cycle,"mutation":mut,"allele_frequency":np.clip(cycle/20+rng.normal(0,0.05),0,1),"phenotype":f"MIC_{round(mic,2)}"})
                parent=f"{lineage}_C{cycle}"
    save("antibiotic_design.csv",pd.DataFrame(design_rows))
    save("antibiotic_cycles.csv",pd.DataFrame(cycle_rows))
    save("antibiotic_measurements.csv",pd.DataFrame(measure_rows))
    save("antibiotic_lineages.csv",pd.DataFrame(lineage_rows))

    # Benchmark
    bench=[]
    domains=["phase","planetary","orbital","climate","prebiotic","bacterial"]
    for i in range(600):
        domain=domains[i%len(domains)]
        history={"path":i%7,"order":i%3,"loss":i%4}
        state={"x":i%11,"energy":round((i%13)/13,3)}
        future={"class":(i%11+i%7+i%3)%9}
        split="train" if i<420 else "validation" if i<510 else "test"
        bench.append({"case_id":f"B{i:04d}","domain":domain,"history_json":json.dumps(history),"state_json":json.dumps(state),"future_json":json.dumps(future),"split":split,"oric_features":json.dumps({"D":i%3,"H":i%2,"L":i%4,"Pacc":(i%10)/10})})
    save("benchmark_cases.csv",pd.DataFrame(bench))

    (data_dir / "SYNTHETIC_DATA_NOTICE.md").write_text(
        "# Données synthétiques\n\nCes jeux servent uniquement à vérifier le code et les schémas. Ils ne constituent aucune preuve scientifique ORI-C.\n",
        encoding="utf-8",
    )
    return counts
