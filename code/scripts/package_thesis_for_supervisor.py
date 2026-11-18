"""Package reviewed bilingual theses without copying raw datasets/checkpoints."""
from pathlib import Path
import argparse,json,hashlib,zipfile,shutil,csv

ROOT=Path(__file__).resolve().parents[2]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser();p.add_argument('output_dir',type=Path);a=p.parse_args();out=a.output_dir.resolve()
 visual=json.loads((out/'visual_qa/visual_review.json').read_text(encoding='utf-8'))
 for lang in ['vi','en']:
  r=visual[lang]
  if r['status']!='ALL_PAGES_VISUALLY_REVIEWED' or r['reviewed_pages']!=list(range(1,r['pages']+1)) or digest(out/lang/'main.pdf')!=r['pdf_sha256']:raise ValueError('Visual review missing or stale')
 for name in ['evidence_audit_full.json','input_hash_audit_full.json']:
  if json.loads((out/'audit'/name).read_text())['status']!='PASS':raise ValueError('Missing full evidence audit')
 note='''VIỆC CẦN GVHD XÁC NHẬN
1. Mẫu trình bày, rubric và yêu cầu khai báo hỗ trợ AI chính thức của khoa; bản hiện tại giữ định dạng sẵn có.
2. Việc giữ nguyên tên đề tài đã đăng ký và diễn giải “độc lập đặc thù xe” là mục tiêu khảo sát, chưa được chứng minh.
3. Đánh giá học thuật cuối: đóng góp đánh giá thực nghiệm, kết quả âm tính và giới hạn đã nêu có đáp ứng yêu cầu khóa luận hay cần điều chỉnh phạm vi.
Không còn thí nghiệm đã hoàn tất nào được ghi là chờ chạy. Không tự chứng nhận đạt rubric, được thông qua hoặc đủ điều kiện công bố.
'''
 (out/'NOTE_CAN_GVHD_XAC_NHAN.txt').write_text(note,encoding='utf-8')
 readme='''GÓI KHÓA LUẬN GỬI GVHD — 09/11/2026
vi/main.pdf và en/main.pdf: hai bản cần đọc. main.tex, refs.bib và figs trong từng thư mục là nguồn LaTeX độc lập của PDF tương ứng.
Tên đề tài giữ nguyên theo đăng ký. Bằng chứng chưa chứng minh tính độc lập xe hoặc khả năng triển khai ECU; kết luận chính W64/B không ủng hộ tăng recall. AP là chỉ số bổ sung.
audit/: dữ liệu bảng đã đối chiếu, bootstrap tính lại, phân phối score AssocRules, 39 mục tham khảo và ma trận nhận định–nguồn, ledger ngoại bộ, kiểm thử và phiếu đóng phát hiện.
visual_qa/: chỉ mục và biên bản rà toàn bộ trang, gắn với hash PDF.
evidence_manifests/: manifest gốc của 60 đơn vị chính và 39 đơn vị nghiên cứu bổ sung; đây là bản sao, không thay đổi nguồn thực nghiệm.
reproduction/: mã sinh bản thảo chuẩn, mã thực nghiệm, cấu hình, notebook và kiểm thử. Không cộng 60 lượt chính, 144 fit mới, 24 baseline tái sử dụng hay 57 capture thành quan sát độc lập.
PACKAGE_MANIFEST.json liệt kê SHA-256 mọi file trong ZIP (trừ chính manifest). File .zip.sha256 kiểm tra ZIP.

TÁI TẠO
PDF từ LaTeX: cài Tectonic/XeLaTeX cùng Times New Roman, Arial, Consolas; chạy tectonic -X compile main.tex trong vi hoặc en. Giữ figs và refs.bib cùng thư mục.
Kiểm chứng/sinh bản thảo từ workspace nghiên cứu F:\\00_Research:
.venv\\Scripts\\python.exe code\\scripts\\finalize_thesis_for_supervisor.py --check
.venv\\Scripts\\python.exe code\\scripts\\finalize_thesis_for_supervisor.py --build --output-dir code\\output\\new_review_build
--check chỉ ghi báo cáo, không sửa nguồn thesis hoặc đầu ra thực nghiệm. --reuse-audit dành cho tái biên dịch bố cục sau full audit; kiểm tra lại snapshot manifest/mã nhưng không băm lại mọi byte. PDF mới luôn cần rà trang lại.
Các writer cũ chuyển mặc định sang quy trình chuẩn; chỉ dùng --legacy-manuscript khi chủ động tái tạo tài liệu lịch sử.

DỮ LIỆU VÀ GIỚI HẠN GÓI
Để kiểm chứng lại từ dữ liệu cần workspace gốc cùng code/data, code/results và các phụ thuộc khoa học; ZIP này không nhân đôi raw data/checkpoint/prediction dung lượng lớn. Các đường dẫn và digest được lưu trong audit/input_hash_audit_full.json và evidence_manifests. Không phải gói tự chứa để huấn luyện khi thiếu dữ liệu.
PDF/ZIP lịch sử được giữ nguyên; các nguồn học thuật đã tải được giữ trong reference_sources tại workspace, không phát hành lại toàn văn của nhà xuất bản trong ZIP này. Báo cáo nguồn ghi rõ metadata/abstract/toàn văn truy cập được, không xác nhận đã đọc toàn văn cả 39 bài.
Kiểm thử có hai cảnh báo KMeans trên fixture trùng điểm và một cảnh báo attention CUDA không xác định; không bảo đảm tái huấn luyện giống từng bit. Build còn có thể báo underfull và ICC profile của ảnh logo; không có lỗi TeX, tràn dòng, glyph thiếu hoặc citation/ref chưa giải quyết trong bản đã rà.
Chấp thuận học thuật và tuân thủ mẫu khoa do GVHD/khoa xác nhận; xem NOTE_CAN_GVHD_XAC_NHAN.txt.
'''
 (out/'DOC_TRUOC.txt').write_text(readme,encoding='utf-8')
 files={}
 def add(path,name):
  path=Path(path)
  if path.is_file():files[name.replace('\\','/')]=path
 for lang in ['vi','en']:
  for name in ['main.pdf','main.tex','refs.bib','build_console.log','main.log']:add(out/lang/name,lang+'/'+name)
  for path in (out/lang/'figs').rglob('*'):add(path,lang+'/figs/'+path.relative_to(out/lang/'figs').as_posix())
 for folder in ['audit','visual_qa']:
  for path in (out/folder).iterdir():
   if path.suffix.lower() in ['.json','.csv','.xml','.txt']:add(path,folder+'/'+path.name)
 for name in ['DOC_TRUOC.txt','NOTE_CAN_GVHD_XAC_NHAN.txt','structure_check.json','final_status.json']:add(out/name,name)
 audit=json.loads((out/'audit/evidence_audit_full.json').read_text())
 for path,h in audit['manifest_snapshot']:
  if digest(path)!=h:raise ValueError('Experiment manifest changed')
  add(path,'evidence_manifests/'+Path(path).relative_to(ROOT/'code').as_posix())
 for folder in ['src','comparison','extensions','acceleration','configs','scripts','tests','thesis_final','notebooks','third_party']:
  for path in (ROOT/'code'/folder).rglob('*'):
   if any(x in path.parts for x in ['.git','__pycache__','.pytest_cache']):continue
   if path.suffix.lower() in ['.py','.ipynb','.json','.toml','.txt','.md','.yml','.yaml','.bib','.tex'] or path.name.startswith('LICENSE'):add(path,'reproduction/code/'+path.relative_to(ROOT/'code').as_posix())
 for path in ROOT.glob('*'):
  if path.is_file() and path.name.lower() in ['requirements.txt','pyproject.toml','uv.lock']:add(path,'reproduction/'+path.name)
 for path in (ROOT/'code').glob('*'):
  if path.is_file() and (path.suffix.lower() in ['.py','.txt','.toml'] or path.name=='README.md'):add(path,'reproduction/code/'+path.name)
 manifest={'scope':'Supervisor review; raw data/checkpoints remain frozen in original workspace','files':{name:{'sha256':digest(path),'bytes':path.stat().st_size} for name,path in sorted(files.items())}}
 (out/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 package=out/'KHOA_LUAN_GUI_GVHD_2026-11-09.zip'
 with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
  for name,path in sorted(files.items()):z.write(path,name)
  z.write(out/'PACKAGE_MANIFEST.json','PACKAGE_MANIFEST.json')
 with zipfile.ZipFile(package) as z:
  for name,row in manifest['files'].items():
   if hashlib.sha256(z.read(name)).hexdigest()!=row['sha256']:raise ValueError('Packaged file hash mismatch')
 (out/(package.name+'.sha256')).write_text(digest(package)+'  '+package.name+'\n',encoding='ascii')
 # Promote only reviewed textual sources. Historical PDFs/ZIPs retain their paths and bytes.
 for lang in ['vi','en']:
  for name in ['main.tex','refs.bib']:shutil.copy2(out/lang/name,ROOT/'thesis'/lang/name)
 print(json.dumps({'zip':str(package),'files':len(files),'bytes':package.stat().st_size}))

if __name__=='__main__':main()
