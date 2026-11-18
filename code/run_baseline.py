"""The unified runner includes Logistic Regression and XGBoost baselines."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from can_research.experiment import main
if __name__ == '__main__':
    main()
