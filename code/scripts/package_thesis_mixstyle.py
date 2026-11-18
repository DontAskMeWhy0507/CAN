"""Package the visually reviewed bilingual revision and promote its sources."""
from pathlib import Path
import hashlib,json,re,shutil,zipfile
import fitz
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'code/output/thesis_supervisor_mixstyle_2026-11-10'
OLD=ROOT/'code/output/thesis_supervisor_final_2026-11-09'
STUDY=ROOT/'code/results/mixstyle_posthoc_2026-11-09'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
qa=json.loads((OUT/'visual_qa/geometry_and_contact_index.json').read_text())
for lang in ['vi','en']:
    assert qa[lang]['pdf_sha256']==sha(OUT/lang/'main.pdf')
    assert not any(p['outside_page'] for p in qa[lang]['page_geometry'])
    log=(OUT/lang/'build_console.log').read_text(encoding='utf-8')
    assert not re.search(r'Overfull|Missing character:|undefined references|Citation.*undefined|Reference.*undefined',log,re.I)
review=dict(status='REVIEWED',pdf_sha256={l:sha(OUT/l/'main.pdf') for l in ['vi','en']},
    coverage='All 141 pages: 122 body regions pixel-identical to previously reviewed PDFs; all 19 changed pages inspected on six contact sheets. Final bibliography-only change inspected full-size in both languages.',
    additional_checks='All-page geometry, continuation headers, contents, captions, references and final page numbering checked.',
    limitations='Underfull spacing and the pre-existing nonfatal logo ICC checksum warning remain in logs; no visible clipping or missing content observed.')
(OUT/'visual_qa/visual_review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
shutil.copy2(OLD/'NOTE_CAN_GVHD_XAC_NHAN.txt',OUT/'NOTE_CAN_GVHD_XAC_NHAN.txt')
ledger=dict(primary_reference=40,key='zhou2021mixstyle',source='https://arxiv.org/abs/2104.02008v1',
    support='Method section 2.2 and appendices A.1/A.2; original visual/CNN scope.',
    adaptation='Temporal same-label source mixing is this study design; effectiveness is measured from local predictions.',
    data={p.name:sha(p) for p in (STUDY/'analysis').glob('*.csv')},
    boundaries='No original-score SOTA ranking; no vehicle-invariance, deployment or publication guarantee.')
(OUT/'audit/mixstyle_claims_and_source.json').write_text(json.dumps(ledger,indent=2),encoding='utf-8')
status=dict(status='READY_FOR_SUPERVISOR_REVIEW',revision='2026-11-10',pages={l:qa[l]['pages'] for l in qa},
    references=40,pdf_sha256=review['pdf_sha256'],original_primary_result_preserved=True,
    supplement='12 additional IDS fits, 24 reused controls, same 57 external captures, matched probes and remeasured runtime',
    tests='11 experiment tests plus one bilingual manuscript integration test passed',
    academic_approval='Requires supervisor/faculty review; see supervisor note')
(OUT/'final_status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
(OUT/'DOC_TRUOC.txt').write_text('''BẢN KHÓA LUẬN CẬP NHẬT 10/11/2026 — GỬI GVHD PHẢN BIỆN

Bản Việt 70 trang; bản Anh 71 trang. Đã thêm mục 5.7 MixStyle, cập nhật
tóm tắt, kết luận, năm bảng và tài liệu tham khảo thứ 40. Tiêu chí chính
Recall W64/B được giữ nguyên; kết quả MixStyle được trình bày là đánh đổi.
Đây là nghiên cứu hậu nghiệm, không phải xác nhận trên xe mới độc lập.

Kiểm chứng: final_status.json; audit/mixstyle_supplement.json;
audit/mixstyle_claims_and_source.json; visual_qa/visual_review.json.
Các báo cáo cũ 39 nguồn vẫn mô tả lần kiểm chứng trước; nguồn MixStyle thứ
40 và số liệu bổ sung có ledger riêng, không tự nhận đã đọc full text cả 40.

Tái tạo trong workspace gốc F:\\00_Research:
.venv/Scripts/python.exe -X utf8 code/scripts/finalize_thesis_for_supervisor.py --build --include-mixstyle --output-dir code/output/new_thesis_build
--reuse-audit chỉ dùng khi đã có bản audit đầy đủ trong thư mục output.

ZIP chứa PDF, nguồn, hình, bằng chứng, notebook và code tái tạo. Dataset,
checkpoint và toàn bộ dự đoán vẫn ở workspace gốc; gói không phải môi trường
huấn luyện độc lập. PDF bài báo của bên thứ ba không được sao vào ZIP này.
Các bản PDF/ZIP ngày 09/11 được giữ nguyên. Nguồn thesis/vi và thesis/en
đã đồng bộ bản cập nhật sau kiểm tra; bản trước cập nhật có ZIP dự phòng.

Điều cần GVHD xác nhận nằm trong NOTE_CAN_GVHD_XAC_NHAN.txt.
''',encoding='utf-8')
# Preserve all current working thesis artifacts before promotion.
backup=ROOT/'revision_backup/before_mixstyle_thesis_2026-11-10.zip'
if not backup.exists():
    with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
        for lang in ['vi','en']:
            for name in ['main.tex','refs.bib','main.pdf']:
                p=ROOT/'thesis'/lang/name
                if p.exists():z.write(p,p.relative_to(ROOT).as_posix())
for lang in ['vi','en']:
    for name in ['main.tex','refs.bib','main.pdf']:shutil.copy2(OUT/lang/name,ROOT/'thesis'/lang/name)
# Retain the existing reproduction bundle, overlaying the current documents/code.
with zipfile.ZipFile(OLD/'KHOA_LUAN_GUI_GVHD_2026-11-09.zip') as z:
    payload={n:z.read(n) for n in z.namelist() if not n.startswith('visual_qa/') and n!='PACKAGE_MANIFEST.json'}
for lang in ['vi','en']:
    for name in ['main.tex','refs.bib','main.pdf','main.log','build_console.log']:
        payload[f'{lang}/{name}']=(OUT/lang/name).read_bytes()
for folder in ['audit','visual_qa']:
    for p in (OUT/folder).glob('*.json'):payload[p.relative_to(OUT).as_posix()]=p.read_bytes()
for name in ['DOC_TRUOC.txt','NOTE_CAN_GVHD_XAC_NHAN.txt','final_status.json']:
    payload[name]=(OUT/name).read_bytes()
payload['audit/pytest_mixstyle_integration.xml']=(OUT/'audit/pytest_mixstyle_integration.xml').read_bytes()
for folder in ['thesis_final','research_mixstyle']:
    for p in (ROOT/'code'/folder).rglob('*.py'):payload['reproduction/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
for p in (ROOT/'code/scripts').glob('*mixstyle*.py'):payload['reproduction/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
for name in ['finalize_thesis_for_supervisor.py']:
    p=ROOT/'code/scripts'/name;payload['reproduction/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
for p in (ROOT/'code/tests').glob('*mixstyle*.py'):payload['reproduction/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
for p in (ROOT/'code/notebooks').glob('*mixstyle*.ipynb'):payload['reproduction/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
for p in [ROOT/'code/notes/mixstyle_proposed_protocol_2026-11-09.json',
          ROOT/'code/notes/PHUONG_PHAP_BO_SUNG_MIXSTYLE_2026-11-09.txt',
          ROOT/'code/notes/mixstyle_sources_2026-11-09/references.bib',
          ROOT/'code/notes/mixstyle_sources_2026-11-09/source.json']:
    payload['reproduction/'+p.relative_to(ROOT).as_posix()]=p.read_bytes()
for folder in ['analysis','provenance']:
    for p in (STUDY/folder).glob('*'):
        if p.is_file():payload['mixstyle_evidence/'+p.relative_to(STUDY).as_posix()]=p.read_bytes()
for name in ['mixstyle_tests_final.xml','handoff_check.json','DOC_TRUOC.txt']:
    payload['mixstyle_evidence/'+name]=(STUDY/name).read_bytes()
manifest={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in sorted(payload.items())}
(OUT/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
payload['PACKAGE_MANIFEST.json']=(OUT/'PACKAGE_MANIFEST.json').read_bytes()
target=OUT/'KHOA_LUAN_CAP_NHAT_2026-11-10.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in sorted(payload.items()):z.writestr(n,b)
with zipfile.ZipFile(target) as z:
    assert len(z.namelist())==len(payload)
    for n,m in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==m['sha256']
(target.with_suffix('.zip.sha256')).write_text(sha(target)+'  '+target.name+'\n',encoding='utf-8')
print(json.dumps(dict(status=status['status'],pages=status['pages'],zip_files=len(payload),zip_sha256=sha(target)),indent=2))
