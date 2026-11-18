from pathlib import Path
import argparse
import sys
CODE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE),str(CODE/'src')]
from acceleration.merge import merge
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();merge(args.inputs,args.output)
