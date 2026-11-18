"""Summarize complete, compatible runs; disclose an incomplete planned matrix."""
import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from can_research.reporting import summarize

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('runs', nargs='+')
    p.add_argument('--output')
    p.add_argument('--require-complete', action='store_true')
    args = p.parse_args()
    out, aggregate = summarize(args.runs, args.output, args.require_complete)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    selected = aggregate[aggregate.operating_point.eq('source_calibrated') & aggregate.condition.isin(list('ABCD'))]
    for (set_name, metric), frame in (( (s, m), g) for s, g in selected.groupby('set') for m in ['Recall', 'FAR_per_100k', 'Attack_F1']):
        pivot = frame.pivot_table(index='condition', columns='model', values=metric, aggfunc='mean')
        ax = pivot.plot.bar(figsize=(10, 5), rot=0, ylabel=metric)
        if metric != 'FAR_per_100k':
            ax.set_ylim(0, 1)
        ax.set_xlabel('Evaluation condition; source-calibrated threshold')
        ax.legend(fontsize=7)
        plt.tight_layout()
        plt.savefig(out/f'{set_name}_{metric}.png', dpi=180)
        plt.close()
    print('Saved summaries:', out)
