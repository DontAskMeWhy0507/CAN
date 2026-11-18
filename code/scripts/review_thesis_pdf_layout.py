"""Prepare every-page contact sheets and geometry checks; does NOT mark visual QA done.

Run with a Python environment containing PyMuPDF and Pillow after the canonical build.
"""
from pathlib import Path
import argparse,json,hashlib,csv
import fitz
from PIL import Image,ImageOps,ImageDraw

def main():
 p=argparse.ArgumentParser();p.add_argument('output_dir',type=Path);a=p.parse_args()
 dest=a.output_dir/'visual_qa';dest.mkdir(exist_ok=True);report={}
 for lang in ['vi','en']:
  pdf=a.output_dir/lang/'main.pdf';doc=fitz.open(pdf);rows=[];sheets=[]
  for start in range(0,len(doc),4):
   sheet=Image.new('RGB',(1320,1910),'#e8e8e8');draw=ImageDraw.Draw(sheet)
   for j,i in enumerate(range(start,min(start+4,len(doc)))):
    page=doc[i];pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    im.thumbnail((640,910));x=10+(j%2)*660;y=30+(j//2)*950
    sheet.paste(im,(x,y));draw.text((x,y-20),f'{lang.upper()} physical page {i+1}',fill='black')
    bad=[]
    for block in page.get_text('dict')['blocks']:
     if block['type']!=0:continue
     for line in block['lines']:
      for span in line['spans']:
       x0,y0,x1,y1=span['bbox']
       if x0<0 or y0<0 or x1>page.rect.width+.5 or y1>page.rect.height+.5:bad.append(span['text'])
    rows.append(dict(page=i+1,characters=len(page.get_text()),outside_page=bad))
   name=f'{lang}_{start+1:02d}_{min(start+4,len(doc)):02d}.jpg';sheet.save(dest/name,quality=92);sheets.append(name)
  report[lang]=dict(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),pages=len(doc),contact_sheets=sheets,page_geometry=rows)
 (dest/'geometry_and_contact_index.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:dict(pages=v['pages'],sheets=len(v['contact_sheets']),outside=sum(bool(r['outside_page']) for r in v['page_geometry'])) for k,v in report.items()}))

if __name__=='__main__':main()
