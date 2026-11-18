"""Opt-in CPU acceleration. Uses a separate output to preserve native run provenance."""
from pathlib import Path
import sys
CODE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE),str(CODE/'src')]
import comparison.adapters as adapters
import comparison.run as runner
from acceleration.assoc import FastAssocRulesAdapter
from can_research.io import sha256_file

adapters.AssocRules=FastAssocRulesAdapter
original_fingerprints=runner.fingerprints
def fingerprints():
    hashes=original_fingerprints()
    for path in [CODE/'acceleration/assoc.py',CODE/'acceleration/__init__.py',Path(__file__)]:
        hashes[path.relative_to(CODE).as_posix()]=sha256_file(path)
    return hashes
runner.fingerprints=fingerprints
if '--output' not in sys.argv:
    sys.argv.extend(['--output',str(CODE/'results/comparison_content_fast_v1')])
if __name__=='__main__':runner.main()
