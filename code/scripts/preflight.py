import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import argparse
from can_research.preflight import audit_workspace
if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root', default='.')
    p.add_argument('--output', required=True)
    p.add_argument('--resume', action='store_true', help='Reuse successful scans only if validator, ledger and file hashes still match')
    a=p.parse_args()
    audit_workspace(a.root,a.output,a.resume)
