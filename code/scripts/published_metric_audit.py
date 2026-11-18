"""Recompute frame metrics from visually/textually checked arXiv-v1 appendix rows.

    All rows are dataset #1, subset #2. This is not a comparison to our windows,
    and does not assume the 2024 journal version has identical appendix numbers.
"""
from pathlib import Path
import pandas as pd
ROWS=[('BIRCH',0,164167,6283750,0,'A.26',41,.9620),
      ('MLP',6227,157940,6226232,57518,'A.28',41,.9594),
      ('Logistic Regression',6195,157972,6161349,122401,'A.15',38,.9539),
      ('Linear SVM',5923,158244,6179525,104225,'A.16',38,.0432),
      ('Gradient Boosting',164079,88,4108265,2175485,'A.21',39,.7739)]
out=[]
for model,tp,fn,tn,fp,table,page,reported in ROWS:
    f1=2*tp/(2*tp+fp+fn)
    neg=2*tn/(2*tn+fp+fn)
    weighted=((tp+fn)*f1+(tn+fp)*neg)/(tp+fn+tn+fp)
    matches='attack_f1' if round(f1,4)==reported else 'weighted_f1' if round(weighted,4)==reported else 'neither'
    out.append(dict(model=model,unit='frame',TP=tp,FN=fn,TN=tn,FP=fp,
                    attack_f1=f1,recall=tp/(tp+fn),precision=tp/(tp+fp) if tp+fp else None,
                    weighted_f1=weighted,source_f1=reported,source_f1_matches_rounded=matches,
                    far_per_100k_frames=100000*fp/(tn+fp),
                    source_url='https://arxiv.org/pdf/2308.04972v1',source_table=table,source_pdf_page=page,
                    source_dataset=1,source_subset=2,verified_date='2026-11-04',
                    provenance='arXiv:2308.04972v1 appendix; journal-version equivalence not assumed'))
dest=Path('results/published_metric_audit.csv')
dest.parent.mkdir(exist_ok=True)
pd.DataFrame(out).to_csv(dest,index=False)
print(dest)
