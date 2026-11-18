"""Canonical final thesis: --check audits only; --build stages bilingual PDFs.

Original experiment artifacts and historical PDFs are never rewritten.
"""
from pathlib import Path
import sys,argparse,json,shutil,subprocess,re,hashlib,zipfile
CODE=Path(__file__).resolve().parents[1];ROOT=CODE.parent
sys.path[:0]=[str(CODE),str(CODE/'src')]
from thesis_final.evidence import load_verified,sha,verify_inputs
from thesis_final.render import render
from thesis_final.references import entries
from thesis_final.claims import report as reference_report

DEFAULT=CODE/'output/thesis_supervisor_final_2026-11-09'

def structural(text,bib):
 keys={e['key'] for e in entries(bib)}
 cites=[k.strip() for group in re.findall(r'\\cite\w*\{([^}]+)\}',text) for k in group.split(',')]
 labels=re.findall(r'\\label\{([^}]+)\}',text)
 refs=re.findall(r'\\(?:ref|pageref|eqref)\{([^}]+)\}',text)
 if not set(cites)<=keys:raise ValueError('Unknown citations: '+str(set(cites)-keys))
 if len(labels)!=len(set(labels)):raise ValueError('Duplicate labels')
 if not set(refs)<=set(labels):raise ValueError('Unknown labels: '+str(set(refs)-set(labels)))
 banned=['Thứ tự hoàn thành','bản GVHD','bản chỉnh sửa','chưa hoàn thành','Chờ chạy cấu hình','các thí nghiệm cần chạy lại','experiments that must be rerun','models must be retrained','v2.0; versions must not be pooled','timing-only và payload-only được dùng','Structural XGBoost và LR','Completion priorities','for the supervisor review','unfinished result matrix']
 for term in banned:
  if term in text:raise ValueError('Stale academic prose: '+term)
 if r'\ref' not in text or '\r' in text:raise ValueError('Malformed TeX escape')
 return dict(labels=sorted(labels),citations=sorted(cites),sections=text.count('\\section{'),subsections=text.count('\\subsection{'))

def sources(data,out):
 result={}
 for lang in ['vi','en']:
  base=CODE/'thesis_final/templates'/lang
  old=(base/'main.tex').read_text(encoding='utf-8');bib=(base/'refs.bib').read_text(encoding='utf-8')
  bib=bib.replace('Cheah, Michael','Cheah, Madeline')
  # The registry page span is malformed and the accessible author PDF is unpaginated.
  bib=re.sub(r'(@inproceedings\{lee2017otids,.*?)pages\s*=\s*\{57--66\},\s*',r'\1',bib,flags=re.S)
  bib=re.sub(r'(@article\{axelsson2000base,.*?)(\n\})',lambda m:m[1].rstrip(',\n ')+',\n  doi = {10.1145/357830.357849}'+m[2],bib,flags=re.S)
  # Use the accessible, verified preprint rather than claim an inaccessible conference version.
  bib=re.sub(r'@inproceedings\{gulrajani2021domainbed,.*?\n\}',r'''@misc{gulrajani2021domainbed,
  author = {Gulrajani, Ishaan and Lopez-Paz, David},
  title = {In Search of Lost Domain Generalization},
  year = {2020}, note = {arXiv:2007.01434v1; verified preprint version},
  url = {https://arxiv.org/abs/2007.01434v1}
}''',bib,flags=re.S)
  text=render(old,data,lang)
  # Source-language references that became irrelevant during restructuring.
  text=text.replace('\\ref{tab:pending}','\\ref{sec:comparison-results}')
  result[lang]=(text,bib,structural(text,bib))
 for k in ['labels','citations','sections','subsections']:
  if result['vi'][2][k]!=result['en'][2][k]:raise ValueError('Bilingual structural mismatch: '+k)
 return result

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--check',action='store_true');g.add_argument('--build',action='store_true')
 p.add_argument('--output-dir',type=Path,default=DEFAULT)
 p.add_argument('--reuse-audit',action='store_true',help='Layout-only rebuild after verified immutable manifest snapshot')
 p.add_argument('--include-mixstyle',action='store_true',help='Include the separately verified post-hoc MixStyle study')
 a=p.parse_args(argv);out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
 report=out/'final_status.json'
 if a.reuse_audit:
  previous=json.loads((out/'audit/evidence_audit.json').read_text())
  for name,digest in previous['manifest_snapshot']:
   if sha(name)!=digest:raise ValueError('Manifest changed since audit')
 data=load_verified(out/'audit',verify_hashes=not a.reuse_audit)
 verify_inputs(out/'audit',data['report']['manifest_snapshot'],data['coverage'],full=not a.reuse_audit)
 docs=sources(data,out)
 reference_sources=out/'reference_sources'
 if not (reference_sources/'reference_access_audit.json').exists():reference_sources=DEFAULT/'reference_sources'
 reference_report(docs,reference_sources,out/'audit')
 if a.include_mixstyle:
  from thesis_final.mixstyle import integrate
  supplement={}
  for lang,(text,bib,_) in docs.items():
   text,bib,supplement[lang]=integrate(text,bib,lang)
   docs[lang]=(text,bib,structural(text,bib))
  for key in ['labels','citations','sections','subsections']:
   if docs['vi'][2][key]!=docs['en'][2][key]:raise ValueError('Supplement bilingual mismatch: '+key)
  (out/'audit/mixstyle_supplement.json').write_text(json.dumps(supplement,indent=2),encoding='utf-8')
 (out/'structure_check.json').write_text(json.dumps({l:docs[l][2] for l in docs},ensure_ascii=False,indent=2),encoding='utf-8')
 if a.check:
  report.write_text(json.dumps(dict(status='CHECK_COMPLETE',source_changes=False,scope='Evidence and generated source checks; PDF visual review is separate'),indent=2),encoding='utf-8');return
 for lang,(text,bib,_) in docs.items():
  target=out/lang;target.mkdir(exist_ok=True)
  (target/'main.tex').write_text(text,encoding='utf-8');(target/'refs.bib').write_text(bib,encoding='utf-8')
  shutil.copytree(ROOT/'thesis'/lang/'figs',target/'figs',dirs_exist_ok=True)
  with (target/'build_console.log').open('w',encoding='utf-8') as log:
   subprocess.run([str(ROOT/'.tools/tectonic/tectonic.exe'),'-X','compile','main.tex','--outdir',str(target),'--keep-logs'],cwd=target,stdout=log,stderr=subprocess.STDOUT,check=True)
  log=(target/'build_console.log').read_text(encoding='utf-8')
  if re.search(r'Overfull|Missing character:|undefined references|Citation.*undefined|Reference.*undefined',log,re.I):raise RuntimeError('Build warnings require correction: '+lang)
  images=out/('render_'+lang);images.mkdir(exist_ok=True)
  subprocess.run(['pdftoppm','-scale-to','1300','-png',str(target/'main.pdf'),str(images/'page')],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
 report.write_text(json.dumps(dict(status='PDFS_BUILT_VISUAL_REVIEW_PENDING',output=str(out),evidence=data['report']),ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
