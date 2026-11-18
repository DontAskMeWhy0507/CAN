"""Preserve earlier outputs and recover the exact hashed training runner."""
from pathlib import Path
import hashlib
import json
import zipfile
CODE = Path(__file__).resolve().parents[1]
OUT = CODE/'results/mixstyle_posthoc_2026-11-09'
dest = OUT/'provenance'
dest.mkdir(exist_ok=True)
archive = dest/'before_secondary_2026-11-10.zip'
if not archive.exists():
    paths = list((OUT/'analysis').glob('*'))
    paths += [CODE/'notebooks/10_mixstyle_posthoc_executed.ipynb', OUT/'execution.log']
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            if p.is_file(): z.write(p, p.relative_to(CODE).as_posix())
current = CODE/'scripts/run_mixstyle_study.py'
source = current.read_text(encoding='utf-8')
start = source.index('                # Baseline artifacts also contain')
end = source.index('    d = pd.concat(frames', start)
original = source[:start] + "                frames.append(pd.read_csv(base/'metrics.csv'))\n" + source[end:]
start = original.index('    # The frozen baseline artifacts also retain')
end = original.index('    if len(pooled)', start)
original = original[:start] + "    pooled = d[d.file.eq('ALL')&d.condition.isin(list('ABCD'))]\n" + original[end:]
original = original.replace("in calibrated[calibrated.file.ne('ALL')&calibrated.condition.isin(list('ABCD'))]",
                            "in d[d.file.ne('ALL')&d.condition.isin(list('ABCD'))]")
m = json.loads((OUT/'main/set_01/attempt_001/manifest.json').read_text())
expected = m['signature']['code']['scripts/run_mixstyle_study.py']
matches = [b for b in [original.encode('utf-8'), original.replace('\n','\r\n').encode('utf-8')]
           if hashlib.sha256(b).hexdigest()==expected]
if len(matches) != 1:
    raise ValueError('Cannot recover exact original runner; do not label reconstruction as verified')
(dest/'run_mixstyle_study_training_snapshot.py').write_bytes(matches[0])
fix = dict(status='VERIFIED', original_runner_sha256=expected,
           corrected_runner_sha256=hashlib.sha256(current.read_bytes()).hexdigest(),
           change='Aggregation now filters baseline default_0.5 rows. Training and scoring functions unchanged.',
           original_notebook='Historical notebook 10 preserves the first failed aggregation; notebook 11 completes corrected verification.',
           historical_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest())
(dest/'aggregation_fix.json').write_text(json.dumps(fix, indent=2)+'\n', encoding='utf-8')
print(json.dumps(fix, indent=2))
