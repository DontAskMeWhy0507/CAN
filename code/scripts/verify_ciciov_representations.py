"""Audit the complete SPEED hexadecimal/decimal export disagreement; no mutation."""
import sys,argparse,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd
from can_research.io import canonical_csv,sha256_file

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--output',default='results/ciciov_speed_format_verification.json')
 args=p.parse_args();root=Path(args.root)
 h=root/'data/CICIoV2024/hexadecimal/hexadecimal_spoofing-SPEED.csv'
 d=root/'data/CICIoV2024/decimal/decimal_spoofing-SPEED.csv'
 a=pd.read_csv(h,dtype=str,keep_default_na=False);b=pd.read_csv(d,dtype=str,keep_default_na=False)
 if len(a)!=len(b):raise ValueError('Unequal lengths; cannot assume row alignment.')
 c=canonical_csv(a,'ciciov'); mismatches={}
 for col in ['ID',*[f'DATA_{j}' for j in range(8)]]:
  av=a.ID.map(lambda x:int(x,16)) if col=='ID' else c.data_field.str[int(col[-1])*2:int(col[-1])*2+2].map(lambda x:int(x,16))
  bad=av.to_numpy()!=b[col].astype(int).to_numpy()
  mismatches[col]=dict(count=int(bad.sum()),first_row_index=int(bad.nonzero()[0][0]) if bad.any() else None)
 label_mismatches=int((a.label.to_numpy()!=b.label.to_numpy()).sum())
 report=dict(scope='All rows; positional alignment assumption checked by ID and label agreement.',rows=len(a),
  lexical_normalizations=c.attrs['format_normalizations'],observed_DATA_6=a.DATA_6.value_counts().to_dict(),
  mismatches=mismatches,label_mismatches=label_mismatches,hex_sha256=sha256_file(h),decimal_sha256=sha256_file(d),
  status='REPRESENTATION_MISMATCH' if label_mismatches or any(x['count'] for x in mismatches.values()) else 'MATCH',
  raw_files_modified=False)
 out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))
