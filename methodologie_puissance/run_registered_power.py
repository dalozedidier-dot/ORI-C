#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'methodologie_puissance/power_monte_carlo.py'
REGISTRY = ROOT / 'methodologie_puissance/PROTOCOL_REGISTRY.json'


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['ci','full'], default='full')
    args = p.parse_args()
    registry = json.loads(REGISTRY.read_text(encoding='utf-8'))
    completed=[]
    for item in registry['protocols']:
        if not item.get('enabled', True):
            continue
        plan = ROOT / item['plan']
        output = ROOT / item['output']
        command = item['command']
        simulations = int(item.get('ci_simulations', 200 if args.mode=='ci' else 0))
        cmd=[sys.executable, str(ENGINE), command, str(plan), '--repo-root', str(ROOT), '--output', str(output)]
        if command == 'estimate' and args.mode == 'ci' and simulations:
            cmd += ['--simulations', str(simulations)]
        subprocess.run(cmd, cwd=ROOT, check=True)
        completed.append({'protocol_id': item['protocol_id'], 'command': command, 'output': str(output.relative_to(ROOT))})
    print(json.dumps({'status':'ok','mode':args.mode,'completed':completed}, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
