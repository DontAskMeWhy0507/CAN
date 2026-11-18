"""Registry and primary-page provenance; never infer unavailable metadata."""
from pathlib import Path
import re,json,hashlib,concurrent.futures,urllib.request,urllib.parse,unicodedata

def entries(text):
 out=[]
 for m in re.finditer(r'(?ms)^@(\w+)\{([^,]+),(.*?)(?=^@|\Z)',text):
  kind,key,body=m.groups();fields={}
  for f in re.finditer(r'(?m)\b(\w+)\s*=\s*([{"])',body):
   pos=f.end();level=1;quote=f[2]=='"';end=pos
   while end<len(body):
    ch=body[end]
    if quote and ch=='"':break
    if not quote:
     if ch=='{':level+=1
     if ch=='}':
      level-=1
      if level==0:break
    end+=1
   fields[f[1].lower()]=body[pos:end]
  out.append(dict(key=key,kind=kind,fields=fields))
 return out

EXTRA={
 'koscher2010experimental':'https://www.autosec.org/pubs/cars-oakland2010.pdf',
 'checkoway2011comprehensive':'https://www.autosec.org/pubs/cars-usenixsec2011.pdf',
 'axelsson2000base':'https://doi.org/10.1145/357830.357849',
 'vaswani2017attention':'https://arxiv.org/abs/1706.03762',
 'lampe2023appendix':'https://arxiv.org/abs/2308.04972v1',
 'koltai2026trust':'https://arxiv.org/abs/2606.30430v1',
}

def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'ThesisReferenceAudit/1.0 (academic metadata verification)'})
 with urllib.request.urlopen(req,timeout=35) as r:return r.read(),r.headers.get('Content-Type',''),r.geturl()

def clean(s):
 s=re.sub(r'\\[a-zA-Z]+','',s);s=unicodedata.normalize('NFKD',s)
 return re.sub(r'[^a-z0-9]','',s.lower())

def audit_one(e,folder):
 f=e['fields'];row={'key':e['key'],'local':f,'access':'UNVERIFIED','checks':{},'sources':[]}
 doi=f.get('doi');urls=[]
 if doi and not doi.lower().startswith('10.48550/arxiv'):
  urls.append('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))
  if doi.startswith('10.4121'):urls.append('https://api.datacite.org/dois/'+urllib.parse.quote(doi,safe=''))
 page=f.get('url') or EXTRA.get(e['key']);
 if page:urls.append(page)
 for i,url in enumerate(dict.fromkeys(urls)):
  try:
   data,ctype,final=get(url);name=e['key']+f'_{i}'+('.json' if 'json' in ctype else '.pdf' if 'pdf' in ctype else '.html')
   (folder/name).write_bytes(data);row['sources'].append({'url':url,'resolved':final,'cached':name,'sha256':hashlib.sha256(data).hexdigest(),'content_type':ctype,'access':'FETCHED'})
   if url.startswith('https://api.crossref.org'):
    m=json.loads(data)['message'];title=m.get('title',[''])[0];authors=[(a.get('given','')+' '+a.get('family','')).strip() for a in m.get('author',[])]
    years=sorted({v[0] for k in ['published','published-print','published-online','issued'] for v in m.get(k,{}).get('date-parts',[])})
    row['registry']={'title':title,'authors':authors,'venue':m.get('container-title',[]),'years':years,'doi':m.get('DOI'),'volume':m.get('volume'),'issue':m.get('issue'),'pages':m.get('page',m.get('article-number'))}
    row['checks']['title']=clean(title)==clean(f.get('title',''))
    row['checks']['year']=int(f['year']) in years if f.get('year','').isdigit() else False
    row['access']='REGISTRY_METADATA_FETCHED'
   elif 'pdf' in ctype:row['access']='PRIMARY_PDF_FETCHED'
   elif row['access']=='UNVERIFIED':row['access']='PRIMARY_PAGE_FETCHED'
  except Exception as exc:row['sources'].append({'url':url,'access':'UNAVAILABLE','reason':str(exc)})
 return row

def audit(bib,folder):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);es=entries(Path(bib).read_text(encoding='utf-8'));assert len(es)==39
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rows=list(ex.map(lambda e:audit_one(e,folder),es))
 (folder/'reference_access_audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 return rows

if __name__=='__main__':
 import sys
 audit(sys.argv[1],sys.argv[2])
