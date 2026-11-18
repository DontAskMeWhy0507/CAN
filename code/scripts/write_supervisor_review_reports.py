"""Close the review ledger only after visual review of the final PDF hashes."""
from pathlib import Path
import argparse,json,csv,sys,xml.etree.ElementTree as ET
CODE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(CODE),str(CODE/'src')]
from thesis_final.evidence import sha
from comparison.run import verify_upstream

def main():
 p=argparse.ArgumentParser();p.add_argument('output_dir',type=Path);a=p.parse_args();out=a.output_dir;aud=out/'audit'
 visual=json.loads((out/'visual_qa/visual_review.json').read_text(encoding='utf-8'))
 for l,r in visual.items():
  if r['status']!='ALL_PAGES_VISUALLY_REVIEWED' or r['pdf_sha256']!=sha(out/l/'main.pdf'):raise ValueError('Stale visual review')
 lock=verify_upstream();(aud/'upstream_adapter_verification.json').write_text(json.dumps({'status':'PASS','pinned_repositories':lock,'scope':'Pinned source file hashes; adaptations disclosed in Chapter 4, not original-score replication'},indent=2),encoding='utf-8')
 adapters=[
  dict(method='CANBERT+ adapted',commit=lock[0]['commit'],source=lock[0]['url'],supervision='Source benign MLM + source frame-label fine-tuning',sampling='Shared source sampled W64 indices; grouped source split',decision='Maximum frame score per nonoverlapping W64',calibration='Source validation only; FAR budget 100/100000',departures='Lightning to PyTorch loop; fixed 3+3 epochs; shared sampling; source vocabulary; at least one masked token per batch; no frame-localization claim'),
  dict(method='CANLP-char-DNN adapted',commit=lock[1]['commit'],source=lock[1]['url'],supervision='Original frame labels in source sampled windows',sampling='Shared sampled W64; grouped source split; no deduplication',decision='Maximum frame score/W64; original paper uses frame-level decisions',calibration='Source validation only; FAR budget 100/100000',departures='Pinned notebook char TF-IDF/DNN ported to PyTorch; binary labels; fixed 30 epochs instead of notebook selection; no direct ranking against journal frame scores'),
  dict(method='CrySyS-AssocRules/W64',commit=lock[2]['commit'],source=lock[2]['url'],supervision='Benign source only',sampling='Shared source window samples; no relation across sampling gaps',decision='W64/stride64 instead of reference W900/stride450',calibration='Source validation only; all 12 thresholds nextafter(1,+inf)',departures='W64 protocol adaptation; default k=300,distance=.3,itemset3/2 retained; exact-call cache validated; all-benign operating point; no causal attribution to W64')]
 with (aud/'adapter_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(adapters[0]));w.writeheader();w.writerows(adapters)
 history=[]
 for pth in list((CODE/'output').glob('*.zip'))+list((CODE.parent/'revision_backup').glob('*.zip')):
  history.append(dict(path=str(pth.resolve()),sha256=sha(pth),bytes=pth.stat().st_size))
 for folder in (CODE/'output').iterdir():
  if folder.is_dir() and folder.resolve()!=out.resolve():
   for pth in folder.rglob('*.pdf'):history.append(dict(path=str(pth.resolve()),sha256=sha(pth),bytes=pth.stat().st_size))
 (aud/'preserved_historical_artifacts.json').write_text(json.dumps({'scope':'Historical PDFs and ZIPs retained; final delivery is written to a new directory','files':history},indent=2),encoding='utf-8')
 findings=[
 ('PB1','Tên đề tài và độc lập xe','Giữ nguyên tên Việt–Anh; phân biệt mục tiêu khảo sát, bất biến đổi tên ID và độc lập xe.','Ch.1; Ch.4; Ch.5 RQ3','Probe xe 0.9488; không chứng minh độc lập xe.'),
 ('PB2','Giả thuyết và chỉ số chính','Giữ recall B/W64 làm tiêu chí; AP bổ sung; FAR báo cả /100k và phần trăm.','Ch.1; Ch.5 RQ1; primary_equal_set.csv','Giả thuyết tăng recall không được ủng hộ; FAR đích còn cao.'),
 ('PB3','Ablation và độ nhạy','Phân tích bỏ ID/payload/delta/local/transition và W32/W64/W128; bootstrap và seed SD riêng.','Ch.5 RQ2; extension_capture_intervals.json; extension_seed_variability.csv','Hậu nghiệm; thay W đổi nhãn/mẫu; không suy nhân quả vật lý.'),
 ('PB4','Đối thủ và AssocRules','Kiểm tra commit/file hash; nêu supervision và mọi thay đổi; tính score nguồn/max ties/FAR.','Ch.4; Ch.5; adapter_comparison.csv; assoc_source_distribution.csv','AssocRules toàn benign; không quy nguyên nhân W64 hoặc phủ định thuật toán gốc.'),
 ('PB5','Ngoại bộ và chronology','Đối chiếu 342 dòng metric với dự đoán cho 57 capture; giữ đủ loại trừ; phân tích CICIoV/MIRGU.','Ch.5 RQ4; evidence_audit_full.json; external_exclusion_ledger.json','Không chứng minh thứ tự thời gian vật lý, 57 phiên độc lập hay deadline ECU.'),
 ('PB6','Trạng thái và cấu trúc luận văn','Viết lại RQ1–RQ4, abstract và kết luận; bỏ câu chờ chạy đã lỗi thời; chuyển lịch sử xuống phụ lục.','vi/main.tex; en/main.tex; structure_check.json; pytest_manuscript_final.xml','Chấp thuận học thuật thuộc GVHD.'),
 ('SRC','39 tài liệu và nhận định','Đối chiếu metadata; sửa Cheah; dùng đúng preprint DomainBed; bỏ phân trang OTIDS không xác minh; thêm vị trí hỗ trợ.','reference_verification.csv; claim_source_matrix.csv','Không xác nhận toàn văn cả 39 tài liệu; một số nhận định giới hạn ở abstract/metadata.'),
 ('DATA','Đóng băng và mẫu số','Băm lại dữ liệu/cache/mã/đầu ra; kiểm tra đủ cell, trùng, số đếm, baseline tái sử dụng và đơn vị.','input_hash_audit_full.json; evidence_audit_full.json','Seed/set/capture không được cộng thành các quan sát xe độc lập.'),
 ('PIPE','Điểm xuất bản thảo và hồi quy','Một CLI --check/--build; writer cũ mặc định chuyển sang CLI; block có biên chính xác; sinh nội dung ổn định.','reproduction/code/scripts/finalize_thesis_for_supervisor.py; pytest_final.xml','--reuse-audit là tái biên dịch từ full audit trước đó, không phải băm lại mọi byte.'),
 ('PDF','PDF và rà trang','Biên dịch không TeX error/overfull/missing glyph/undefined citation/ref; rà mọi trang và trang thay đổi sau chỉnh từ.','visual_qa/visual_review.json; geometry_and_contact_index.json; main.log','Có underfull và cảnh báo ICC logo không gây mất/chồng/tràn nội dung; giữ định dạng hiện có chờ mẫu khoa.'),
 ]
 rows=[dict(id=i,issue=issue,status='DA_SUA_VA_KIEM_TRA',resolution=res,evidence=evidence,remaining_limits=limit) for i,issue,res,evidence,limit in findings]
 with (aud/'DONG_PHAT_HIEN_PHAN_BIEN.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 test=ET.parse(aud/'pytest_final.xml').getroot();cases=list(test.iter('testcase'))
 if len(cases)!=77 or list(test.iter('failure')) or list(test.iter('error')):raise ValueError('Tests not passing')
 status=dict(status='READY_FOR_SUPERVISOR_REVIEW',academic_approval='REQUIRES_SUPERVISOR_AND_FACULTY',tests_passed=len(cases),references=39,pages={l:r['pages'] for l,r in visual.items()},pdf_sha256={l:r['pdf_sha256'] for l,r in visual.items()},review_findings_closed=len(rows),limitations='See closure ledger and supervisor note; no publication/rubric/vehicle-independence guarantee')
 (out/'final_status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
 (aud/'BAO_CAO_KIEM_CHUNG.txt').write_text('BẢN GỬI GVHD ĐÃ ĐƯỢC KIỂM TRA\n'+json.dumps(status,ensure_ascii=False,indent=2)+'\n\nFull audit băm lại artifact thực nghiệm, dữ liệu/cache và mã nguồn. Các lượt build sau chỉ dùng snapshot đã kiểm chứng; không thay checkpoint, dự đoán hoặc manifest gốc. Hai PDF đã được rà toàn bộ trang; biên bản gắn với hash cuối. Bảng đóng phát hiện nêu cả bằng chứng và giới hạn; thành công biên dịch không được xem là tự đủ nghiệm thu học thuật.\n',encoding='utf-8')
 print(json.dumps(status,ensure_ascii=False))

if __name__=='__main__':main()
