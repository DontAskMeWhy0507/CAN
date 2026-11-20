"""Validate completed post-hoc evidence and append it to both manuscripts."""
# CANONICAL WRITER ROUTE: historical generation requires explicit opt-in.
if __name__ == '__main__':
    import sys as _final_sys
    if '--legacy-manuscript' in _final_sys.argv:
        _final_sys.argv.remove('--legacy-manuscript')
    else:
        from pathlib import Path as _FinalPath
        import subprocess as _final_subprocess
        _final_args = _final_sys.argv[1:]
        if not any(v in _final_args for v in ['--check','--build']):
            _final_args = ['--build', *_final_args]
        raise SystemExit(_final_subprocess.call([_final_sys.executable, str(_FinalPath(__file__).with_name('finalize_thesis_for_supervisor.py')), *_final_args]))

from pathlib import Path
import sys,json,hashlib,re,subprocess,zipfile,importlib.util
ROOT=Path(__file__).resolve().parents[2];CODE=ROOT/'code';OUT=CODE/'results/content_completion_2026-11-09'
sys.path[:0]=[str(CODE),str(CODE/'src')]
import pandas as pd
from can_research.io import sha256_file
from comparison.analysis import paired_counts
spec=importlib.util.spec_from_file_location('manuscript_layout',CODE/'scripts/update_comparison_manuscript.py')
layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)

def exact_block(text,key,body,anchor):
    start='% BEGIN COMPARISON '+key;end='% END COMPARISON '+key
    replacement=start+'\n'+body.strip()+'\n'+end+'\n'
    pattern=re.escape(start)+r'\n.*?'+re.escape(end)+r'(?:\n|$)'
    if re.search(pattern,text,re.S):
        text,count=re.subn(pattern,lambda _:replacement,text,flags=re.S);assert count==1
        return text
    assert text.count(anchor)==1
    return text.replace(anchor,replacement+'\n'+anchor)

layout.block=exact_block


def verified(folder):
    results=[]
    for p in sorted(folder.glob('**/manifest.json')):
        m=json.loads(p.read_text())
        if m['status']!='COMPLETE':continue
        for name,digest in m['artifacts'].items():assert sha256_file(p.parent/name)==digest,(p,name)
        results.append((p.parent,m))
    return results


def main():
    nb=json.loads((CODE/'notebooks/10_complete_thesis_evidence.execution.json').read_text());assert nb['status']=='COMPLETE'
    ab=verified(OUT/'ablation');se=verified(OUT/'sensitivity')
    assert len(ab)==12 and len(se)==24
    expected={(f'set_0{s}',seed,w) for s in range(1,5) for seed in (42,43,44) for w in (32,64,128)}
    assert {(m['signature']['set'],m['signature']['seed'],m['signature']['w']) for _,m in ab+se}==expected
    for name in ('runtime','probes','external'):assert len(verified(OUT/name))==1,name
    rows=pd.concat([pd.read_csv(p/'metrics.csv') for p,m in ab+se],ignore_index=True)
    assert not rows.duplicated(['stage','set','seed','window_size','condition','file','method','operating_point']).any()
    rows.to_csv(OUT/'all_extension_metrics.csv',index=False)
    pooled=rows[(rows.file=='ALL')&(rows.operating_point=='source_calibrated')]
    variants=['raw','structural','raw_no_id','id_only','raw_plus_structural','structural_no_delta','structural_no_local','structural_no_transition','structural_no_payload','structural_no_rank_w']
    expected_rows={(f'set_0{s}',seed,w,rep,c) for s in range(1,5) for seed in (42,43,44) for w in (32,64,128) for rep in (variants if w==64 else ['raw','structural']) for c in 'ABCD'}
    assert set(pooled[['set','seed','window_size','method','condition']].itertuples(index=False,name=None))==expected_rows and len(pooled)==672
    cols=['Recall','FAR_per_100k','Attack_F1','AP']
    per=pooled.groupby(['window_size','set','method','condition'])[cols].mean()
    means=per.groupby(['window_size','method','condition'])[cols].mean()
    means.to_csv(OUT/'equal_set_means.csv');per.to_csv(OUT/'by_set.csv')
    pooled.groupby(['window_size','set','method','condition'])[cols].agg(['mean','std','count']).to_csv(OUT/'seed_variability.csv')
    contrasts=[];intervals=[]
    calibrated=rows[rows.operating_point=='source_calibrated']
    for (w,s,seed,c),g in pooled.groupby(['window_size','set','seed','condition']):
        reference=g[g.method=='structural'].iloc[0]
        captures=calibrated[(calibrated.window_size==w)&(calibrated['set']==s)&(calibrated.seed==seed)&(calibrated.condition==c)&(calibrated.file!='ALL')]
        a=captures[captures.method=='structural'].set_index('file').sort_index()
        for _,r in g[g.method!='structural'].iterrows():
            contrasts.append(dict(window_size=w,set=s,seed=seed,condition=c,variant=r.method,**{m:r[m]-reference[m] for m in cols}))
            b=captures[captures.method==r.method].set_index('file').sort_index();assert a.index.equals(b.index)
            for metric in cols[:3]:
                intervals.append(dict(window_size=int(w),set=s,seed=int(seed),condition=c,variant=r.method,**paired_counts(a[['TP','FP','TN','FN']].to_numpy(),b[['TP','FP','TN','FN']].to_numpy(),metric)))
    pd.DataFrame(contrasts).to_csv(OUT/'paired_variant_minus_structural.csv',index=False)
    (OUT/'paired_capture_intervals.json').write_text(json.dumps(intervals,ensure_ascii=False,indent=2),encoding='utf-8')
    probe_dir=verified(OUT/'probes')[0][0];runtime_dir=verified(OUT/'runtime')[0][0];external_dir=verified(OUT/'external')[0][0]
    probes=pd.read_csv(probe_dir/'probe_results.csv');runtime=pd.read_csv(runtime_dir/'runtime.csv');external=pd.read_csv(external_dir/'external_metrics.csv')
    ps=probes.groupby(['representation','target','control'])[['balanced_accuracy','accuracy']].mean();ps.to_csv(OUT/'probe_summary.csv')
    cover=json.loads((external_dir/'coverage.json').read_text());counts=pd.Series([v['status'] for v in cover]).value_counts().to_dict()
    n=lambda x,d=4:'--' if pd.isna(x) else f'{x:.{d}f}'
    for lang in ('vi','en'):
        vi=lang=='vi';body=r'\section{'+('Thực nghiệm bổ sung sau phép so chính' if vi else 'Post-hoc evidence following the primary comparison')+r'}\label{sec:completion}'+'\n'
        body+=('Các phân tích này được thiết kế sau khi đã xem kết quả chính. Chúng không phải một lần xác nhận độc lập trên test chưa tiếp xúc và không thay thế tiêu chí recall/FAR ban đầu. Có 144 fit mới và 24 baseline W64 được giữ nguyên: W64 gồm 10 biểu diễn khác nhau; W32/W128 gồm raw và structural. Payload-only trùng raw-no-ID trong nhánh nội dung; no-timing trùng structural, nên không tính thành bằng chứng độc lập. Không có thí nghiệm timing-only vì chronology chưa được xác minh.\n' if vi else
               'These analyses were designed after viewing the primary results. They are not independent confirmation on untouched targets and do not replace the original recall/FAR criterion. There are 144 new fits and 24 unchanged W64 baselines: ten distinct W64 representations and raw/structural at W32/W128. Payload-only equals raw-no-ID in the content tier; no-timing equals structural, so neither alias counts as independent evidence. Timing-only is excluded because chronology is unverified.\n')
        body+=('Mọi biến thể dùng cùng nhóm nguồn, quy tắc reservoir toàn file, seed 42/43/44, 10 epoch và ngân sách FAR validation nguồn 100/100.000. Mẫu được chọn lại cho W32/W128 vì đơn vị cửa sổ đổi; so sánh độ nhạy vì vậy bao gồm thay đổi nhãn cửa sổ, số mẫu sẵn có và độ dài chuỗi. Không so trực tiếp mẫu số giữa các W.\n' if vi else
               'All variants share source groups, full-file reservoir policy, seeds 42/43/44, ten epochs and a source-validation FAR budget of 100/100,000. Sampling is recomputed at W32/W128 because the decision unit changes; sensitivity therefore includes changed window labels, available samples and sequence length. Denominators are not directly equated across W.\n')
        body+=('Cấu hình encoder được giữ giống nhau nhưng số tham số lớp chiếu đầu vào thay đổi theo số chiều; đây không phải phép so có tổng số tham số hoàn toàn bằng nhau.\n' if vi else 'Encoder hyperparameters are shared, but input-projection parameter counts vary with feature dimension; total parameter counts are not exactly equal.\n')
        body+=r'\subsection{'+('Ablation và độ nhạy cửa sổ' if vi else 'Ablations and window sensitivity')+'}\n'
        labels={'raw':'Raw','structural':'Structural','raw_no_id':'Raw without ID','id_only':'ID only','raw_plus_structural':'Raw + structural','structural_no_delta':'Structural without delta','structural_no_local':'Structural without local counts/ranks','structural_no_transition':'Structural without transitions','structural_no_payload':'Structural without absolute payload','structural_no_rank_w':'Structural without rank/W'}
        for w in [64,32,128]:
            table=[]
            for (method,c),r in means.loc[w].iterrows():
                table.append([c,labels[method],n(r.Recall),n(r.FAR_per_100k,2),n(r.Attack_F1),n(r.AP)])
            body+=layout.table(f'Content W{w}; equal set weights; FAR per 100,000 benign windows',f'tab:extension-w{w}',['Cond.','Representation','Recall','FAR','F1','AP'],table,['1.1','4.2','1.6','2.2','1.6','1.6'])
        body+=('Các bảng báo toàn bộ biến thể, kể cả biến thể bất lợi. Chênh lệch ablation hỗ trợ vai trò của một thành phần trong pipeline này, không chứng minh nguyên nhân vật lý hoặc tính độc lập xe. Không chọn lại mô hình thắng theo test rồi gán cho giả thuyết chính. Số đếm và từng capture nằm trong dữ liệu kèm theo.\n' if vi else
               'Every variant is reported, including losses. Ablation differences support component effects within this pipeline, not physical causality or vehicle independence. A target-selected winner is not reassigned to the primary hypothesis. Per-capture counts remain in the accompanying data.\n')
        body+=r'\subsection{'+('Probe tuyến tính và đối chứng' if vi else 'Linear probes and controls')+'}\n'
        body+=('Encoder của 4 nguồn và 3 seed được đóng băng. Probe dùng nhóm recording-round huấn luyện/giữ lại khác nhau và cân bằng mọi ô xe × nhãn tấn công; mô hình IDS không được cập nhật. Chance là 1/4 cho xe và 1/2 cho tấn công. Đối chứng constant, embedding ngẫu nhiên và hoán vị nhãn huấn luyện được giữ lại; hai đối chứng ngẫu nhiên có 5 lần lặp. Encoder đã thấy capture huấn luyện của chính nguồn mình; phép đo chỉ là khả năng giải mã tuyến tính hậu nghiệm, không chứng minh tổng quát hóa phiên lái độc lập hay độc lập thống kê.\n' if vi else
               'Encoders from four sources and three seeds are frozen. Probe training/holdout uses separate recording-round groups and balances all vehicle-by-attack cells; IDS parameters remain unchanged. Chance is 1/4 for vehicle and 1/2 for attack. Constant, random-embedding and permuted-training-label controls are retained; both randomized controls have five repetitions. Encoders saw their own source training captures. This measures post-hoc linear decodability, not unseen-driving-session generalization or statistical independence.\n')
        body+=layout.table('Mean balanced accuracy across frozen encoders; descriptive, not a vehicle-population CI','tab:extension-probes',['Representation','Target','Control','Balanced accuracy'],[[rep,target,control.replace('_',' '),n(r.balanced_accuracy)] for (rep,target,control),r in ps.iterrows()],['3.3','1.6','4.7','3.1'])
        vr=ps.loc[('raw','vehicle','learned'),'balanced_accuracy'];vs=ps.loc[('structural','vehicle','learned'),'balanced_accuracy']
        ar=ps.loc[('raw','attack','learned'),'balanced_accuracy'];ass=ps.loc[('structural','attack','learned'),'balanced_accuracy']
        probe_interpretation=(f"Probe xe có balanced accuracy Raw {vr:.4f} và Structural {vs:.4f}, so với chance 0,25. Chênh lệch {vs-vr:.4f} chỉ mô tả giảm khả năng giải mã tuyến tính; mức còn lại vẫn cao, nên không chứng minh loại bỏ thông tin xe. Probe tấn công tương ứng {ar:.4f}/{ass:.4f}; không được đồng nhất phép giải mã nhãn với recall của IDS tại ngưỡng nguồn.\n" if vi else
                              f"Vehicle-probe balanced accuracy is {vr:.4f} for Raw and {vs:.4f} for Structural, against chance 0.25. The difference {vs-vr:.4f} describes reduced linear decodability only; the remaining accuracy is high and does not establish removal of vehicle information. Attack-probe values are {ar:.4f}/{ass:.4f}; label decoding is distinct from IDS recall at the source-selected threshold.\n")
        body+=probe_interpretation
        body+=r'\subsection{'+('Kiểm thử ngoại bộ và dữ liệu bị loại' if vi else 'External evaluation and exclusions')+'}\n'
        body+=(f"Đối với dữ liệu ngoại bộ, có {counts.get('COMPLETE',0)} capture hoàn tất; mọi file thiếu, cách ly hoặc sai schema/nhãn được giữ trong ledger đầu ra. Mô hình nguồn Set 1 ở cả ba seed và ngưỡng nguồn được giữ nguyên. Thiếu thời gian vẫn được giữ là thiếu, không dựng timestamp; mọi kết quả theo thứ tự file và không khẳng định chronology vật lý. Automotive benign/DoS có nền dùng chung, nên không được coi là các phiên độc lập.\n" if vi else
               f"External evaluation completed {counts.get('COMPLETE',0)} captures; missing, quarantined and schema/label-invalid files remain in the output ledger. Set 1 source models for all three seeds retain their source thresholds. Missing time stays missing without synthetic timestamps; results follow file order without asserting physical chronology. Automotive benign/DoS captures share background traffic and are not independent sessions.\n")
        er=[]
        for (dataset,rep),g in external.groupby(['dataset','representation']):
            values=[]
            for seed,v in g.groupby('seed'):
                tp,fp,tn,fn=v[['TP','FP','TN','FN']].sum();pos=tp+fn;neg=fp+tn
                values.append([tp/pos if pos else float('nan'),100000*fp/neg if neg else float('nan')])
            v=pd.DataFrame(values,columns=['recall','far']).mean()
            er.append([dataset.replace('_',r'\_'),rep,n(v.recall),n(v.far,2)])
        body+=layout.table('External: pooled file counts within dataset/seed, then mean of three seeds; FAR per 100,000','tab:extension-external',['Dataset','Representation','Recall','FAR'],er,['4.4','3.1','2.0','2.4'])
        body+=('Capture chỉ có benign chỉ xác định FAR, không xác định recall hay AP hai lớp; dấu -- là không xác định, không phải số không. File SPEED của CICIoV và OTIDS chưa rõ nguồn nhãn/thứ tự vẫn bị loại; không sửa byte hoặc suy nhãn từ tên file.\n' if vi else
               'Benign-only captures identify FAR but not recall or two-class AP; a dash is undefined, not zero. CICIoV SPEED and OTIDS derivatives lacking verified byte/label/order provenance remain excluded; bytes are not repaired and labels are not inferred from filenames.\n')
        body+=r'\subsection{'+('Runtime theo cửa sổ trên máy thực nghiệm' if vi else 'Window processing time on the experimental host')+'}\n'
        body+=layout.table('Batch one; 20 warmup windows; 300 measured windows x 3 repetitions; milliseconds','tab:extension-runtime',['Device','Representation','Median ms','P95 ms'],[[r.device,r.representation,n(r.p50_ms,3),n(r.p95_ms,3)] for _,r in runtime.iterrows()],['2.0','3.6','3.2','3.2'])
        body+=('Phép đo gồm đọc CSV, kiểm tra/chuyển đổi, tạo cả hai biểu diễn nội dung và inference. Cache hệ điều hành và ứng dụng khác có thể ảnh hưởng kết quả. Không đo thời gian chờ thu đủ cửa sổ, hàng đợi, thời điểm gây hại hay deadline ECU; đây không phải chứng nhận triển khai thời gian thực.\n' if vi else
               'Measurement includes CSV reading, validation/conversion, both content representations and inference. OS caching and other applications may affect timing. Acquisition waits, queueing, time to harm and ECU deadlines are not measured; this does not certify real-time deployment.\n')
        main=ROOT/'thesis'/lang/'main.tex';text=main.read_text(encoding='utf-8')
        text=layout.block(text,'POSTHOC',body,'% End inlined results_'+lang+'.tex')
        for tag,needle,paragraph in [
            ('VI',r'\noindent\textbf{\textit{Từ khóa:}}',f'Phân tích hậu nghiệm bổ sung đánh giá 10 biểu diễn nội dung, độ nhạy W32/W128, probe cân bằng, ngoại bộ theo ledger và runtime máy thực nghiệm. Probe xe Raw/Structural đạt {vr:.4f}/{vs:.4f} balanced accuracy, cho thấy vẫn còn nhiều thông tin về xe; các bằng chứng này không xác nhận độc lập xe hay khả năng triển khai thời gian thực.'),
            ('EN',r'\noindent\textbf{\textit{Keywords:}}',f'Additional post-hoc analyses cover ten content representations, W32/W128 sensitivity, balanced probes, ledger-governed external evaluation and host runtime. Raw/Structural vehicle probes reach {vr:.4f}/{vs:.4f} balanced accuracy, indicating substantial remaining vehicle information; these results do not establish vehicle independence or real-time deployment readiness.')]:
            text=layout.block(text,'POSTHOC_ABSTRACT_'+tag,paragraph,needle)
        conclusion=(r'\section{Tổng hợp bằng chứng bổ sung cho bản GVHD}' if vi else r'\section{Additional evidence for the supervisor review}')+'\n'+probe_interpretation
        conclusion+=('Các ablation và độ nhạy được báo đầy đủ tại Mục~'+r'\ref{sec:completion}'+'. Đây là bằng chứng hậu nghiệm có giới hạn trên các bản ghi quan sát được. Giả thuyết chính và kết quả 60 lượt ban đầu được giữ nguyên; không chọn kết quả thuận lợi để thay thế tiêu chí chính. Việc đo runtime và kiểm thử ngoại bộ không giải quyết các giới hạn chronology vật lý, độc lập phiên lái và deadline ECU.\n' if vi else
                     'All ablations and sensitivity results appear in Section~'+r'\ref{sec:completion}'+'. This is limited post-hoc evidence over observed captures. The original hypothesis and 60-cell results remain unchanged; favourable secondary findings do not replace the primary criterion. Runtime and external evaluation do not resolve physical chronology, driving-session independence or ECU deadlines.\n')
        text=layout.block(text,'POSTHOC_CONCLUSION',conclusion,'% End inlined conclusion_'+lang+'.tex')
        updated=[]
        for line in text.splitlines():
            key=line.split('&',1)[0].strip()
            statuses_vi={'RQ2':'Đã chạy 10 biểu diễn content; timing-only không áp dụng','RQ3':'Đã probe 12 cặp encoder, cân bằng xe × nhãn và có đối chứng','RQ4':'Đã kiểm thử ngoại bộ theo ledger; giữ mọi loại trừ','Độ nhạy':'Đã chạy W32/W128, bốn set và ba seed','Triển khai':'Đã đo CPU/GPU batch một; chưa xác nhận ECU thời gian thực'}
            statuses_en={'RQ2':'Ten content representations executed; timing-only inapplicable','RQ3':'Twelve encoder pairs; balanced vehicle/attack probes and controls','RQ4':'Ledger-governed external evaluation; all exclusions retained','Sensitivity':'W32/W128 across four sets and three seeds completed','Deployment':'CPU/GPU batch-one timing measured; ECU deadlines unverified'}
            statuses=statuses_vi if vi else statuses_en
            if key in statuses and line.count('&')==2:
                parts=line.split('&');line=parts[0]+'&'+parts[1]+'& '+statuses[key]+r'\\'+(r'\bottomrule' if r'\bottomrule' in line else '')
            if line.strip()==r'\pending':line=('Trạng thái content đã được cập nhật; nhánh timed cần chronology hợp lệ.' if vi else 'Content evidence is updated; timed execution requires verified chronology.')
            updated.append(line)
        text='\n'.join(updated)+'\n'
        text=text.replace('Ablation, probe, ngoại bộ và runtime chưa được xem là hoàn tất.',r'Bằng chứng bổ sung theo nhánh nội dung nằm tại Mục~\ref{sec:completion}; các kết luận timing và triển khai vật lý vẫn chưa được xác nhận.')
        text=text.replace('Ablations, probes, external evaluation and runtime are not automatically complete.',r'Additional content-tier evidence appears in Section~\ref{sec:completion}; timing and physical-deployment claims remain unconfirmed.')
        text=text.replace('Ablation, probe xe/tấn công, độ nhạy cửa sổ và đánh giá ngoại bộ còn là các câu hỏi mở.',r'Kết quả bổ sung hậu nghiệm cho các phép đo này nằm tại Mục~\ref{sec:completion}; kết luận được giới hạn theo dữ liệu và giao thức tại đó.')
        text=text.replace('Ablations, vehicle/attack probes, window sensitivity and external evaluation remain open.',r'Post-hoc evidence for these measurements appears in Section~\ref{sec:completion}, subject to its data and protocol limitations.')
        main.write_text(text,encoding='utf-8')
    subprocess.run([sys.executable,str(CODE/'scripts/check_manuscript.py')],cwd=ROOT,check=True)
    pdfout=CODE/'output/thesis_completion_2026-11-09';pdfout.mkdir(parents=True,exist_ok=True)
    marker=Path(r'C:/Users/tuant/.codex/plugins/cache/openai-primary-runtime/pdf/26.1104.22356/skills/pdf/container_tools/mark_artifact_operation_started.mjs')
    if marker.exists():
        subprocess.run(['node',str(marker),'--operation-kind','edit','--expected-output-count','2','--output-format','pdf'],check=True)
    for lang in ['vi','en']:
        target=pdfout/lang;target.mkdir(exist_ok=True)
        with (target/'build.log').open('w',encoding='utf-8') as log:
            subprocess.run([str(ROOT/'.tools/tectonic/tectonic.exe'),'-X','compile','main.tex','--outdir',str(target),'--keep-logs'],cwd=ROOT/'thesis'/lang,stdout=log,stderr=subprocess.STDOUT,check=True)
        assert 'Overfull' not in (target/'build.log').read_text(encoding='utf-8'),'Inspect PDF layout log'
        render=pdfout/('render_'+lang);render.mkdir(exist_ok=True)
        subprocess.run(['pdftoppm','-scale-to','1100','-png',str(target/'main.pdf'),str(render/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    report={'status':'EVIDENCE_IMPORTED_VISUAL_REVIEW_REQUIRED','analysis_code_sha256':sha256_file(__file__),'model_cells':168,'new_fits':144,'reused':24,'external_coverage':counts,'pdfs':str(pdfout),'remaining':'Final visual and academic review; chronology, independence, ECU real-time and publication acceptance are not established by completed runs.'}
    (OUT/'completion_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
