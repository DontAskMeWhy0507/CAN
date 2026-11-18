"""Human-reviewed source limits and traceable claim locations."""
from pathlib import Path
import json,re,csv,html
from .references import entries,clean

NOTES={
 'axelsson2000base':'DOI registry retry verified year/title/authors/venue/pages; source probability argument only, not measured CAN performance.',
 'tariq2020cantransfer':'Crossref separates title CANTransfer and subtitle. Author GitHub README confirms full title, authors and one-shot abstract. No matched-score comparison.',
 'rajapaksha2024canmirgu':'Publisher PDF first-page author order is retained; Crossref deposits Kalutarage before Madzudzo. PDF is authoritative for this cited version.',
 'rajapaksha2023survey':'Corrected Cheah, Michael to Cheah, Madeline against ACM publisher and author institutional repository; survey abstract supports taxonomy only.',
 'lee2017otids':'Registry page field 57-5709 is malformed; accessible 10-page author PDF has no printed pagination. Page span omitted rather than infer 57-66. DOI/title/authors/year identify the work.',
 'gulrajani2021domainbed':'OpenReview forum/PDF/API blocked. Canonical citation changed to accessible arXiv:2007.01434v1 (2020), title/authors/abstract verified; no assumption of identity to inaccessible ICLR version.',
 'ganin2016dann':'JMLR HTML meta truncates Mario Marchand to Mario March. Publisher PDF page 1 confirms Marchand; retain PDF name and labeled-source/unlabeled-target setting.',
 'lampe2023appendix':'arXiv v1 specifically identifies the historical count audit; not assumed identical to the journal appendix.',
 'lampe2024curated':'Journal metadata verified through DOI; dataset design supported by author preprint. No journal/preprint appendix identity assumption.',
 'jo2025indirect':'Only registry title/authors/year/venue/pages were verified; detailed centre-selection and training claims removed from the thesis.',
 'jo2026fusion':'Abstract-level discussion only; full split, target-data budget and latency details remain unverified and are not asserted.',
 'khreasat2026relational':'Registry abstract supports statistics/transitions/topology and target-calibration distinction; PMC fetch was a reCAPTCHA challenge, not full text.',
 's26051489':'Registry abstract supports Pearson/deep learning/frequency-domain design; PMC challenge is not full text; no replication or matched benchmark claim.',
 'dong2026mtff':'Registry abstract supports same-ID/inter-ID streams and attention fusion; PMC challenge is not full text; no comparable latency/split claim.',
 'dupont2019automotive':'DataCite record and 4TU dataset Version 2 landing JSON-LD confirm creators, year 2019, DOI, version and dataset identity; local README/signature audit provides labels.',
 'won2026canbertplus':'USENIX metadata and cached publisher PDF pp.97-115 identify the original; own adapter and pinned source provide reproduction-departure details.',
 'balasubramanian2025canlp':'DOI journal metadata and author abstract identify frame-level TF-IDF detection. Adapter is a disclosed char-DNN port, not an unchanged journal reproduction.',
}

# Locations identify the accessible version and the scope actually used, not a claim
# that every cited paper was independently reproduced or read in its entirety.
LOCATIONS={
 'koscher2010experimental':'Author PDF p.1 abstract and introduction; DOI-free author-hosted paper metadata.',
 'checkoway2011comprehensive':'Author PDF p.1 abstract; external attack-surface categories, not this thesis threat feasibility.',
 'vaswani2017attention':'arXiv:1706.03762 abstract and citation metadata; Transformer/attention provenance.',
 'axelsson2000base':'Crossref DOI record title/authors/year/container/pages; base-rate discussion only, with precision/denominator algebra specified in the thesis.',
 'lampe2024curated':'Author preprint local papers/Lampe_Meng_preprint_journal2024.pdf: abstract and dataset split description; journal identity separately from Crossref.',
 'lampe2023appendix':'Version-specific arXiv:2308.04972v1 record and appendix confusion-count audit; do not transfer appendix numbers to journal version.',
 'lee2017otids':'Author-hosted OTIDS PDF p.1 abstract, 10 physical PDF pages; unpaginated author copy, not proof of publisher page span.',
 'tariq2020cantransfer':'Author repository README abstract and BibTeX entry: convolutional LSTM and one-shot transfer; DOI metadata for proceedings identity.',
 'dupont2019automotive':'4TU Version 2 landing page JSON-LD creator/date/version and DataCite DOI identity; local dataset README/ledger for labels.',
 'rajapaksha2024canmirgu':'Publisher PDF p.1 title/author order/abstract; local label schema and exclusions are checked separately.',
 'koltai2026trust':'arXiv:2606.30430v1 abstract (five IDS approaches, seven datasets); pinned CrySyS implementation for W900/stride450 adaptation details.',
 'obafemi2026travel':'Publisher PDF abstract and source/target local-calibration discussion; source-only comparison boundary retained.',
 'hewitt2019probes':'ACL Anthology D19-1275 abstract: control tasks and probe interpretation; own CAN controls are a disclosed adaptation.',
 'gulrajani2021domainbed':'arXiv:2007.01434v1 (2020) PDF p.1 abstract and model-selection discussion; inaccessible ICLR version not used as verified evidence.',
 'saito2015pr':'PLOS publisher HTML Abstract and precision-recall discussion; AP implementation and undefined cases specified independently.',
 'kidmose2025cansleuth':'Publisher HTML Abstract and can-train-and-test-v1.5 / suppress / masquerade discussion; v1.5 not used in the experiments.',
 'cho2016fingerprint':'USENIX author/publisher page Abstract: ECU clock-skew fingerprinting.',
 'chiscop2021modification':'SCITEPRESS paper page Abstract: modification attacks and temporal convolutional networks.',
 'hanselmann2020canet':'Author arXiv preprint local CANet_preprint_2019_journal2020.pdf pp.2-5 (LSTM architecture); 2020 journal identity from DOI.',
 'alkhatib2022canbert':'Author arXiv preprint local CAN_BERT_2022_preprint.pdf abstract and masking discussion; 2022 AICCSA identity from DOI.',
 'won2026canbertplus':'USENIX publisher PDF physical p.2 title/abstract and pp.7-9 representation/MLM/fine-tuning; cover is physical p.1. Adapter changes from pinned code, not publisher scores.',
 'balasubramanian2025canlp':'Author publication page Abstract (frame-level TF-IDF); pinned repository notebook for char-DNN adapter; journal DOI metadata separately verified.',
 'jo2025indirect':'Crossref .message title/author/published/container-title/page only; detailed methodological claims removed.',
 'jo2026fusion':'ScienceDirect article preview Abstract/Conclusion, https://www.sciencedirect.com/science/article/abs/pii/S1570870526000909, checked 2026-11-09; payload/periodicity decision fusion only.',
 'song2020dcnn':'ScienceDirect article preview Abstract/Introduction, https://www.sciencedirect.com/science/article/pii/S2214209619302451, checked 2026-11-09; DCNN traffic patterns, no matched-score ranking.',
 'islam2020graph':'Author arXiv:2009.11440 landing-page Abstract; graph-based CAN IDS design, journal identity separately from DOI.',
 'jeong2024xcanids':'Author arXiv:2303.12278 landing-page Abstract; signal-aware explainable IDS, journal identity separately from DOI.',
 'neto2024ciciov2024':'Crossref title/authors/year/journal/DOI for dataset identity; local downloaded README/schema and exclusion ledger provide the evaluated labels and absence of measured timestamps.',
 'sommer2010outside':'Author-hosted https://www.icir.org/robin/papers/oakland10-ml.pdf Abstract, checked 2026-11-09; closed-world versus operational intrusion detection discussion.',
 'ganin2016dann':'JMLR publisher PDF p.1 author list and abstract: labeled source/unlabeled target; HTML author truncation not propagated.',
 'zhao2019invariant':'PMLR v97/zhao19a Abstract: invariant representations are insufficient under conditional shift.',
 'hoang2022supcon':'arXiv:2207.10814v1 Abstract: supervised contrastive ResNet/transfer; no direct CAN score comparison.',
}

def report(docs,source_dir,out):
 source_dir=Path(source_dir);out=Path(out);raw=json.loads((source_dir/'reference_access_audit.json').read_text(encoding='utf-8'))
 retry=source_dir/'axelsson_retry.json'
 if retry.exists():raw=[json.loads(retry.read_text(encoding='utf-8')) if r['key']=='axelsson2000base' else r for r in raw]
 bykey={r['key']:r for r in raw};es=entries(docs['vi'][1]);assert len(es)==39
 rows=[]
 for e in es:
  key=e['key'];r=bykey[key];f=e['fields'];reg=r.get('registry');note=NOTES.get(key,'Primary registry/page metadata reviewed; substantive claims are limited to the accessible abstract or identified publisher/author text, not proof of comparable CAN performance.')
  sources=r['sources'];accessible=[]
  for source in sources:
   if source.get('access')!='FETCHED':continue
   cache=source_dir/source['cached'];body=cache.read_bytes()
   if source.get('sha256') and __import__('hashlib').sha256(body).hexdigest()!=source['sha256']:raise ValueError('Reference cache changed')
   if cache.suffix=='.html' and (len(body)<512 or any(v in body.lower() for v in [b'checking your browser',b'verifying your browser',b'recaptcha'])):continue
   accessible.append(source)
  if key=='gulrajani2021domainbed':accessible=[{'url':'https://arxiv.org/abs/2007.01434v1','cached':'domainbed.pdf'}]
  if not accessible:raise ValueError('No accessible identity source: '+key)
  if reg:
   registered=reg['title']
   if key=='tariq2020cantransfer':registered+=': transfer learning based intrusion detection on a controller area network using convolutional LSTM network'
   if clean(f['title'])!=clean(registered):raise ValueError('Unresolved title mismatch: '+key)
   if int(f['year']) not in reg['years']:raise ValueError('Unresolved year mismatch: '+key)
  location=LOCATIONS.get(key,'Crossref .message title/author/published/container-title/volume/issue/page, with .message.abstract for the qualitative discussion; no unseen full-text details asserted.')
  rows.append(dict(key=key,title=f.get('title'),authors=f.get('author'),year=f.get('year'),venue=f.get('journal',f.get('booktitle',f.get('note','Dataset/preprint'))),doi=f.get('doi','not supplied'),url=f.get('url',''),version=f.get('note','Version as identified by DOI/record'),verification='IDENTITY_METADATA_REVIEWED_WITH_SOURCE_LIMITS',source_location='; '.join(s.get('url','') for s in accessible),support_location=location,review_note=note))
 with (out/'reference_verification.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 claims=[]
 for lang,(text,bib,_) in docs.items():
  chapter='Front matter';section=''
  lines=text.splitlines();start=0
  for i,line in enumerate(lines):
   ch=re.search(r'\\chapter\{([^}]+)\}',line);se=re.search(r'\\section\{([^}]+)\}',line)
   if ch:chapter=ch[1]
   if se:section=se[1]
   if not line.strip():start=i+1
   for match in re.finditer(r'\\cite\w*\{([^}]+)\}',line):
    paragraph=' '.join(lines[start:i+1])
    for key in match[1].split(','):
     key=key.strip();source=next(r for r in rows if r['key']==key)
     claims.append(dict(language=lang,chapter=chapter,section=section,line=i+1,claim_context=paragraph,source_key=key,source_location=source['source_location'],support_location=source['support_location'],support_boundary=source['review_note']))
 with (out/'claim_source_matrix.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(claims[0]));w.writeheader();w.writerows(claims)
 (out/'reference_review.json').write_text(json.dumps(dict(entries=39,scope='Identity metadata and claim limits; not independent reproduction or a plagiarism/rubric certificate',records=rows,claims=len(claims)),ensure_ascii=False,indent=2),encoding='utf-8')
