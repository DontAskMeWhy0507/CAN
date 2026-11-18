"""Run from any working directory; see --help."""
import sys
from pathlib import Path
CODE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE),str(CODE/'src')]
from comparison.run import main
if __name__=='__main__':main()
