"""Run fixed linear probes and controls after the IDS is frozen."""
import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from can_research.probes import run_probe

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='.')
    p.add_argument('--checkpoint-dir', required=True)
    p.add_argument('--output', required=True)
    args = p.parse_args()
    result = run_probe(args.root, args.checkpoint_dir, args.output)
    print(result.to_string(index=False))
