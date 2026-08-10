#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def link_key(row):
    return (row['source'], row['target'], int(row['lag_kyr']), row['graph_mark'])

def p_close(a,b):
    a=float(a); b=float(b)
    if a <= 1e-8 and b <= 1e-8:
        return True
    return math.isclose(a,b,rel_tol=5e-3,abs_tol=1e-10)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--reference',required=True)
    ap.add_argument('--candidate',required=True)
    args=ap.parse_args()
    r=json.loads(Path(args.reference).read_text())
    c=json.loads(Path(args.candidate).read_text())
    errors=[]
    for key in ['status','variables','tau_max_kyr','pc_alpha','scope']:
        if r.get(key)!=c.get(key): errors.append(f'{key}: {r.get(key)!r} != {c.get(key)!r}')
    rl={link_key(x):x for x in r['significant_links_raw_p_le_0p01']}
    cl={link_key(x):x for x in c['significant_links_raw_p_le_0p01']}
    if set(rl)!=set(cl):
        errors.append(f'topologie des liens différente: ref={len(rl)} cand={len(cl)}')
    for k in sorted(set(rl)&set(cl)):
        a,b=rl[k],cl[k]
        if not math.isclose(float(a['value']),float(b['value']),rel_tol=5e-4,abs_tol=2e-5):
            errors.append(f'value {k}: {a["value"]} != {b["value"]}')
        if not p_close(a['p'],b['p']):
            errors.append(f'p {k}: {a["p"]} != {b["p"]}')
    print(json.dumps({'reference_links':len(rl),'candidate_links':len(cl),'errors':errors,'status':'ok' if not errors else 'error'},ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)
if __name__=='__main__': main()
