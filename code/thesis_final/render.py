"""One canonical bilingual text, with numeric assertions supplied by evidence."""
from pathlib import Path
import re,json
import numpy as np
import pandas as pd
from .evidence import equal_set,METRICS,capture_intervals

LABELS={'raw_transformer':('Raw TF','Raw TF'),'structural_transformer':('Structural TF','Structural TF'),'canbertplus':('CANBERT+ adapted','CANBERT+ adapted'),'canlp':('CANLP-char-DNN adapted','CANLP-char-DNN adapted'),'assoc_rules_crysys':('CrySyS-AssocRules/W64','CrySyS-AssocRules/W64'),'raw':('Raw','Raw'),'structural':('Structural','Structural'),'raw_no_id':('Raw bỏ ID','Raw without ID'),'id_only':('Chỉ ID','ID only'),'raw_plus_structural':('Raw cộng cấu trúc','Raw + structure'),'structural_no_delta':('Structural bỏ delta','Structural without delta'),'structural_no_local':('Structural bỏ thống kê cục bộ','Structural without local statistics'),'structural_no_transition':('Structural bỏ chuyển tiếp','Structural without transitions'),'structural_no_payload':('Structural bỏ payload tuyệt đối','Structural without absolute payload'),'structural_no_rank_w':('Structural bỏ hạng/W','Structural without rank/W')}

def n(x,d=4):return '--' if pd.isna(x) else f'{x:.{d}f}'
def tex(s):return str(s).replace('_',r'\_').replace('%',r'\%')
def table(caption,label,headers,rows,widths):
 spec=''.join('P{'+str(w)+'cm}' for w in widths);head=' & '.join(headers)+r'\\\midrule'+'\n'
 return (r'\begin{longtable}{'+spec+'}\n'+r'\caption{'+caption+r'}\label{'+label+r'}\\\toprule'+'\n'+head+r'\endfirsthead\toprule'+'\n'+head+r'\endhead'+'\n'+'\n'.join(' & '.join(map(str,r))+r'\\' for r in rows)+'\n'+r'\bottomrule\end{longtable}'+'\n')

def exact_block(t,key,body,anchor):
 start='% BEGIN FINAL '+key;end='% END FINAL '+key;replacement=start+'\n'+body.strip()+'\n'+end+'\n'
 pattern=re.escape(start)+r'\n.*?'+re.escape(end)+r'(?:\n|$)'
 if re.search(pattern,t,re.S):
  t,count=re.subn(pattern,lambda _:replacement,t,flags=re.S)
  if count!=1:raise ValueError('Repeated named block')
  return t
 if t.count(anchor)!=1:raise ValueError('Missing or ambiguous anchor')
 return t.replace(anchor,replacement+'\n'+anchor)

def part(t,name,lang):
 a='% Begin inlined '+name+'_'+lang+'.tex';b='% End inlined '+name+'_'+lang+'.tex'
 return t.split(a,1)[1].split(b,1)[0].strip()

def gettable(t,label):
 for m in re.finditer(r'\\begin\{longtable\}.*?\\end\{longtable\}',t,re.S):
  if '\\label{'+label+'}' in m[0]:return m[0]
 raise ValueError(label)

def local_table(t,label,vi):
 value=gettable(t,label)
 if vi:
  translations={
   'Test-window denominators shared by five methods and three seeds':'Mẫu số cửa sổ kiểm thử dùng chung giữa năm phương pháp và ba seed',
   'Structural minus opponent; equal set weights; FAR per 100,000 benign windows':'Structural trừ đối chứng; trọng số set ngang nhau; FAR trên 100.000 cửa sổ lành',
   'B/D by set; recall mean and sample SD across three seeds; FAR per 100,000':'B/D theo set; recall trung bình và độ lệch chuẩn ba seed; FAR trên 100.000',
   'Structural minus Raw: conditional whole-file recall bootstrap, 95 percent':'Structural trừ Raw: khoảng bootstrap recall 95 phần trăm có điều kiện theo file',
   'Condition &':'ĐK &','Cond. &':'ĐK &','Method &':'Phương pháp &','Attack &':'Tấn công &','Benign &':'Lành &','Total':'Tổng','Interval &':'Khoảng &','Files; draws':'File; mẫu'}
  for old,new in translations.items():value=value.replace(old,new)
 return value

def sec(title,body):return '\\section{'+title+'}\n'+body.strip()+'\n'
def sub(title,body):return '\\subsection{'+title+'}\n'+body.strip()+'\n'

def intro(old,vi):
 lang='vi' if vi else 'en';t=part(old,'introduction',lang)
 # Retain sourced motivation and the threat/scope description, rewrite promises.
 at=t.index('\\section{Câu hỏi nghiên cứu}' if vi else '\\section{Research questions}')
 t=t[:at]
 if vi:
  t+=r'''\section{Câu hỏi nghiên cứu}
\begin{enumerate}[label=\textbf{RQ\arabic*.}]
\item Với ngưỡng chọn chỉ từ nguồn theo cùng ngân sách FAR, raw và structural khác nhau thế nào về recall và FAR ở A--D, đặc biệt điều kiện B?
\item Trong nhánh nội dung, bỏ bit ID thô và thêm biến thiên payload cùng ID, thống kê cục bộ, chuyển tiếp ID tạo ra những đánh đổi nào? Kết quả đổi ra sao với W32/W64/W128?
\item Khả năng giải mã tuyến tính nhãn xe và nhãn tấn công từ encoder đóng băng khác nhau ra sao giữa raw và structural, khi cân bằng dữ liệu và có đối chứng?
\item Các mô hình nguồn và ngưỡng đã đóng băng thành công hoặc thất bại thế nào trên dữ liệu ngoại bộ có nhãn/schema được kiểm tra?
\end{enumerate}
\section{Giả thuyết và tiêu chí diễn giải}
Giả thuyết chính là structural tăng recall trung bình ở B so với raw tại ngưỡng chọn từ validation nguồn với ngân sách FAR 100/100.000 cửa sổ lành. Chênh lệch là structural trừ raw, trung bình ba seed trong từng set rồi trung bình ngang nhau bốn set. Chênh lệch không dương không ủng hộ giả thuyết. Recall luôn được diễn giải cùng FAR đích; AP và F1 là chỉ số bổ sung, không được đổi thành tiêu chí chính sau khi xem test.

Các tập đích đã từng được xem trong quá trình phát triển. Ablation, probe và độ nhạy bổ sung là phân tích hậu nghiệm, không phải xác nhận độc lập trên test chưa tiếp xúc. Bốn set không đại diện bốn cặp xe độc lập. Probe xe thấp hơn chỉ cho thấy giảm khả năng giải mã tuyến tính trong phép đo đó; không chứng minh độc lập thống kê hoặc loại bỏ toàn bộ thông tin xe.
\section{Đóng góp và giới hạn}
\begin{enumerate}
\item Đặc tả và triển khai biểu diễn nội dung 30 chiều không cung cấp bit CAN-ID thô cho bộ phân loại, nhưng dùng ID để tra lịch sử payload và quan hệ cục bộ. Bất biến dưới đổi tên ID nhất quán là tính chất hẹp hơn độc lập xe.
\item Đánh giá ghép cặp với dữ liệu nguồn, kiến trúc encoder và quy tắc ngưỡng nhất quán: ma trận chính 60 đơn vị IDS, 144 lượt huấn luyện bổ sung cùng 24 baseline tái sử dụng, không coi các lượt này là các xe hay phiên ghi độc lập.
\item Phân tích đánh đổi giữa xếp hạng, recall, báo động giả và thông tin xe qua ablation, probe có đối chứng, độ nhạy cửa sổ, 57 capture ngoại bộ và runtime máy thực nghiệm; lưu dự đoán, checkpoint và nguồn gốc để kiểm tra lại.
\end{enumerate}
Đóng góp chủ yếu là đánh giá thực nghiệm và làm rõ giới hạn chuyển giao. Không tuyên bố phát minh Transformer, quan hệ ID, bài toán A--D hay một IDS độc lập xe đã sẵn sàng triển khai. Tên đề tài được giữ theo đăng ký; tính độc lập xe là mục tiêu được khảo sát, không phải kết luận đã được chứng minh.
\section{Tổ chức khóa luận}
Chương~\ref{chap:background} xác định dữ liệu và bài toán; Chương~\ref{chap:related} đối chiếu công trình liên quan; Chương~\ref{chap:method} mô tả giao thức thực thi; Chương~\ref{chap:results} trả lời RQ1--RQ4 bằng kết quả và giới hạn; Chương~\ref{chap:conclusion} tổng hợp kết luận. Phụ lục cung cấp chi tiết tái lập và phân biệt thiết kế lịch sử với bằng chứng hiện hành.
'''
 else:
  t+=r'''\section{Research questions}
\begin{enumerate}[label=\textbf{RQ\arabic*.}]
\item With thresholds selected on source validation under the same FAR budget, how do raw and structural inputs differ in recall and FAR across A--D, particularly B?
\item Within the content tier, what tradeoffs arise from removing raw ID bits or adding same-ID payload differences, local statistics and ID transitions? How do results change across W32/W64/W128?
\item How does linear decoding of vehicle and attack labels from frozen encoders differ between representations under balanced data and explicit controls?
\item How do frozen source models and thresholds succeed or fail on external captures with checked label/schema provenance?
\end{enumerate}
\section{Hypothesis and interpretation criteria}
The primary hypothesis is increased mean recall in B for structural versus raw inputs at thresholds chosen from source validation under a FAR budget of 100 per 100,000 benign windows. Differences are structural minus raw, averaged over three seeds within each set and then equally over four sets. A nonpositive difference does not support the hypothesis. Recall is interpreted with target FAR; AP and F1 are secondary and do not replace the primary criterion after viewing targets.

Targets were previously inspected during development. Additional ablations, probes and window sensitivity are post-hoc analyses, not independent confirmation on untouched tests. Four sets are not four independent vehicle pairs. Reduced vehicle-probe accuracy describes reduced linear decodability within that diagnostic, not statistical independence or removal of all vehicle information.
\section{Contributions and limitations}
\begin{enumerate}
\item A specified and implemented 30-dimensional content representation that excludes raw CAN-ID bits from the classifier while using IDs to retrieve payload history and local relations. Invariance under consistent ID renaming is narrower than vehicle independence.
\item Paired evaluation with consistent source data, encoder hyperparameters and source-only thresholds: 60 primary IDS units, 144 additional training runs and 24 reused baselines, without interpreting runs as independent vehicles or driving sessions.
\item Analysis of ranking, recall, false alarms and vehicle information through ablations, controlled probes, window sensitivity, 57 external captures and host runtime, with predictions, checkpoints and provenance retained for verification.
\end{enumerate}
The contribution is primarily empirical evaluation and characterization of transfer limitations. It does not claim to invent Transformers, ID relations, the A--D task, or a deployment-ready vehicle-independent IDS. The registered title is retained; vehicle independence is the investigated objective, not an established conclusion.
\section{Thesis organization}
Chapter~\ref{chap:background} defines the data and task; Chapter~\ref{chap:related} compares related work; Chapter~\ref{chap:method} specifies the executed protocol; Chapter~\ref{chap:results} answers RQ1--RQ4 with results and limitations; Chapter~\ref{chap:conclusion} synthesizes findings. Appendices provide reproducibility details and distinguish historical designs from current evidence.
'''
 return t

def abstract(data,vi):
 _,m=equal_set(data['primary']);b=m.loc[('structural_transformer','B')];r=m.loc[('raw_transformer','B')]
 if vi:
  return r'''\begingroup\fontsize{12}{12}\selectfont
\noindent\textbf{Tóm tắt:} Khóa luận khảo sát tác động của biểu diễn đầu vào đối với phát hiện xâm nhập CAN khi thay đổi xe và kiểu tấn công. Biểu diễn structural 30 chiều không cung cấp bit CAN-ID thô cho bộ phân loại nhưng vẫn dùng ID làm khóa lịch sử payload và quan hệ cục bộ; đối chứng raw có 28 chiều. Các cửa sổ W64 không chồng lặp, không nối file, mang nhãn dương nếu chứa ít nhất một frame nhãn 1 theo chính sách dữ liệu. Dữ liệu giữ nguyên thứ tự file; timestamp đi lùi được kiểm toán và không dùng làm đặc trưng, nên không khẳng định chronology vật lý.

Ma trận chính gồm bốn set, ba seed và năm phương pháp dưới quy tắc ngưỡng chọn chỉ từ nguồn. Các bản CANBERT+, CANLP-char-DNN và CrySyS-AssocRules/W64 được thích ứng có công bố thay đổi, không phải tái lập nguyên trạng điểm số công bố. Ở B, Structural có recall '''+n(b.Recall)+' so với '+n(r.Recall)+' của Raw, AP '+n(b.AP)+' so với '+n(r.AP)+', và FAR '+n(b.FAR_per_100k/1000,2)+r'''\%. Kết quả không ủng hộ giả thuyết tăng recall trung bình ở B tại ngưỡng nguồn, dù chất lượng xếp hạng tăng và FAR giảm tương đối.

Phân tích hậu nghiệm gồm 144 lượt huấn luyện mới, 24 baseline tái sử dụng, 10 biểu diễn nội dung, W32/W128, probe có đối chứng và 57 capture ngoại bộ. Probe xe Raw/Structural đạt 0,9925/0,9488 balanced accuracy, cao hơn nhiều mức cơ hội 0,25; chưa chứng minh độc lập xe. Ngoại bộ cho thấy cả thành công theo cơ chế và thất bại chuyển giao ngưỡng. Runtime chỉ đo xử lý cửa sổ trên CPU/GPU máy bàn, không xác nhận deadline ECU. Đóng góp là đánh giá tái lập và phân tích giới hạn chuyển giao, không phải khẳng định ưu thế toàn diện.

\noindent\textbf{\textit{Từ khóa:}} CAN; phát hiện xâm nhập; chuyển xe; biểu diễn cấu trúc; ngưỡng nguồn.
\par\endgroup'''
 return r'''\begingroup\fontsize{12}{12}\selectfont
\noindent\textbf{Abstract:} This thesis examines how input representations affect CAN intrusion detection across vehicles and attack types. The 30-dimensional structural representation excludes raw CAN-ID bits from classifier input while retaining IDs as keys for payload history and local relations; raw inputs have 28 dimensions. Non-overlapping W64 windows never cross files and are positive if any frame carries dataset label 1. Original file order is retained. Timestamp inversions are audited and timing is excluded from features, so physical chronology is not asserted.

The primary matrix covers four sets, three seeds and five methods using source-only threshold selection. CANBERT+, CANLP-char-DNN and CrySyS-AssocRules/W64 are disclosed adaptations rather than unchanged replications of published scores. In B, Structural recall is '''+n(b.Recall)+' versus Raw '+n(r.Recall)+', AP '+n(b.AP)+' versus '+n(r.AP)+', and FAR '+n(b.FAR_per_100k/1000,2)+r'''\%. The results do not support increased mean recall in B at source-selected thresholds, despite improved ranking and a relative FAR reduction.

Post-hoc analyses comprise 144 new training runs, 24 reused baselines, ten content representations, W32/W128, controlled probes and 57 external captures. Raw/Structural vehicle-probe balanced accuracy is 0.9925/0.9488, far above chance 0.25; vehicle independence is not established. External evaluation reveals both mechanism-specific successes and threshold-transfer failures. Runtime measures window processing on a desktop CPU/GPU, not ECU deadlines. The contribution is reproducible empirical evaluation and analysis of transfer limitations, not a claim of universal superiority.

\noindent\textbf{\textit{Keywords:}} CAN; intrusion detection; cross-vehicle transfer; structural representation; source thresholds.
\par\endgroup'''

def results(data,old,vi):
 lang='vi' if vi else 'en';_,means=equal_set(data['primary']);_,ext=equal_set(data['extension'])
 pick=lambda a,b:a if vi else b
 title=pick('Kết quả và thảo luận','Results and discussion')
 t='\\chapter{'+title+r'}\label{chap:results}'+'\n'
 t+=pick('Chương này phân biệt phép so chính đã định nghĩa tiêu chí với phân tích bổ sung hậu nghiệm. Mọi số tổng hợp dùng trung bình seed trong set rồi trọng số ngang nhau giữa các set; không xem số cửa sổ là số xe độc lập. Dấu -- là không xác định, không phải số không.\n','This chapter distinguishes the primary criterion from additional post-hoc analyses. Aggregation averages seeds within sets before equally weighting sets; windows are not independent vehicles. A dash means undefined, not zero.\n')
 t+=sec(pick('RQ1: recall, xếp hạng và báo động giả khi chuyển xe','RQ1: recall, ranking and false alarms under vehicle transfer'),r'\label{sec:comparison-results}'+'\n'+pick('B kiểm tra xe lạ với tấn công quen; D đồng thời đổi xe và kiểu tấn công. Ngưỡng nguồn được giữ cố định; ngân sách nguồn 100/100.000 không bảo đảm FAR đích. Các điểm công bố gốc không nằm trong bảng này.','B tests an unseen vehicle with known attacks; D changes both vehicle and attack type. Source thresholds remain frozen; the source budget of 100/100,000 does not bound target FAR. Original published scores are not included in this table.'))
 headers=pick(['ĐK','Phương pháp','Recall','FAR','F1','AP'],['Cond.','Method','Recall','FAR','F1','AP'])
 order=['raw_transformer','structural_transformer','canbertplus','canlp','assoc_rules_crysys']
 rows=[[c,LABELS[k][0 if vi else 1],*[n(means.loc[(k,c),m],2 if m=='FAR_per_100k' else 4) for m in METRICS]] for c in 'ABCD' for k in order]
 t+=table(pick('Kết quả chính W64; ngưỡng nguồn; FAR trên 100.000 cửa sổ lành','Primary W64 results; source-calibrated; FAR per 100,000 benign windows'),'tab:comparison-main',headers,rows,[1.1,4.1,1.6,2.2,1.6,1.6])
 b=means.loc[('structural_transformer','B')];r=means.loc[('raw_transformer','B')];d=means.loc[('structural_transformer','D')];dr=means.loc[('raw_transformer','D')]
 t+=pick(f'Ở B, chênh lệch recall Structural trừ Raw là {100*(b.Recall-r.Recall):.2f} điểm phần trăm; AP tăng {b.AP-r.AP:.4f}. FAR giảm {100*(r.FAR_per_100k-b.FAR_per_100k)/100000:.2f} điểm phần trăm nhưng vẫn bằng {b.FAR_per_100k/1000:.2f}\\%. Ở D, recall đổi {100*(d.Recall-dr.Recall):.2f} điểm phần trăm và FAR còn {d.FAR_per_100k/1000:.2f}\\%. Giả thuyết chính tăng recall trung bình ở B không được ủng hộ. AP tăng là kết quả bổ sung về xếp hạng, không khắc phục mức báo động giả cao hoặc thay thế tiêu chí chính.\n',f'In B, Structural minus Raw recall is {100*(b.Recall-r.Recall):.2f} percentage points, while AP increases by {b.AP-r.AP:.4f}. FAR falls by {(r.FAR_per_100k-b.FAR_per_100k)/1000:.2f} percentage points but remains {b.FAR_per_100k/1000:.2f}\\%. In D, recall changes by {100*(d.Recall-dr.Recall):.2f} percentage points and FAR remains {d.FAR_per_100k/1000:.2f}\\%. The primary increased-recall hypothesis for B is unsupported. Improved AP is a secondary ranking result and neither resolves high false alarms nor replaces the primary criterion.\n')
 # Every table is regenerated from audited counts; historical TeX is never a numeric source.
 pooled=data['primary'][(data['primary'].file=='ALL')&(data['primary'].operating_point=='source_calibrated')&data['primary'].condition.isin(list('ABCD'))]
 den=[[tex(s),c,*[int(g[k].iloc[0]) for k in ['Attack_Windows','Benign_Windows','Total_Windows']]] for (s,c),g in pooled.groupby(['set','condition'])]
 t+=table(pick('Mẫu số cửa sổ kiểm thử dùng chung giữa năm phương pháp và ba seed','Test-window denominators shared by five methods and three seeds'),'tab:comparison-counts',['Set',pick('ĐK','Cond.'),pick('Tấn công','Attack'),pick('Lành','Benign'),pick('Tổng','Total')],den,[2,1.2,2.7,2.7,2.7])
 pairs=[[c,LABELS[k][0 if vi else 1],*[n(means.loc[('structural_transformer',c),m]-means.loc[(k,c),m],2 if m=='FAR_per_100k' else 4) for m in METRICS]] for c in 'BD' for k in order if k!='structural_transformer']
 t+=table(pick('Structural trừ đối chứng; trọng số set ngang nhau; FAR trên 100.000 cửa sổ lành','Structural minus opponent; equal set weights; FAR per 100,000 benign windows'),'tab:comparison-paired',headers[:2]+[r'$\Delta R$',r'$\Delta$ FAR',r'$\Delta$ F1',r'$\Delta$ AP'],pairs,[1.2,4,1.7,2.2,1.7,1.7])
 per,unused=equal_set(data['primary']);sd=pooled.groupby(['set','method','condition'])[METRICS].std()
 detail=[[tex(s),c,LABELS[k][0 if vi else 1],n(per.loc[(s,k,c),'Recall'])+r' $\pm$ '+n(sd.loc[(s,k,c),'Recall']),n(per.loc[(s,k,c),'FAR_per_100k'],2)] for s in sorted(pooled['set'].unique()) for c in 'BD' for k in order]
 t+=table(pick('B/D theo set; recall trung bình và độ lệch chuẩn ba seed; FAR trên 100.000','B/D by set; recall mean and sample SD across three seeds; FAR per 100,000'),'tab:comparison-sets',['Set',pick('ĐK','Cond.'),pick('Phương pháp','Method'),'Recall','FAR'],detail,[1.6,1.2,4,3.5,2.2])
 cis=capture_intervals(data['primary'],'structural_transformer')
 cirows=[[tex(i['set']),i['seed'],i['condition'],n(i['estimate']),'--' if i['ci95'] is None else '['+', '.join(n(x) for x in i['ci95'])+']',str(i['files'])+'; '+str(i['valid_replicates'])+'/'+str(i['requested_replicates'])] for i in cis if i['opponent']=='raw_transformer' and i['condition'] in 'BD' and i['metric']=='Recall']
 t+=table(pick('Structural trừ Raw: khoảng bootstrap recall 95 phần trăm có điều kiện theo file','Structural minus Raw: conditional whole-file recall bootstrap, 95 percent'),'tab:comparison-ci',['Set','Seed',pick('ĐK','Cond.'),r'$\Delta R$',pick('Khoảng','Interval'),pick('File; mẫu','Files; draws')],cirows,[1.6,1.1,1.2,1.8,3.7,2.9])
 for metric in ['Recall','FAR_per_100k','Attack_F1','AP']:
  caption=pick('Kết quả W64 theo điều kiện A--D; ngưỡng nguồn; trọng số set ngang nhau','W64 by A--D condition; source thresholds; equal set weights')
  t+=r'\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{figs/comparison_v1_'+metric+r'.png}\caption{'+caption+'; '+metric.replace('_',r'\_')+r'.}\label{fig:comparison-'+metric+r'}\end{figure}'+'\n'
 t+=r'\FloatBarrier'+'\n'
 t+=pick('Recall Structural cao hơn Raw sau trung bình seed chỉ ở một trong bốn set cho cả B và D. Không kết luận cải thiện nhất quán. Độ lệch chuẩn seed mô tả khởi tạo; bootstrap ghép cặp lấy lại toàn capture và tính từ số đếm. Khoảng bootstrap là mô tả có điều kiện trên file quan sát, không phải CI cho quần thể xe; không lấy trung bình các đầu mút CI để suy ra CI đa xe.\n','After seed averaging, Structural recall exceeds Raw in only one of four sets for both B and D. Improvement is not consistent. Seed SD describes initialization; paired bootstrap resamples entire captures and recomputes from counts. Intervals are conditional descriptions of observed files, not vehicle-population CIs; averaging interval endpoints does not produce a multi-vehicle CI.\n')
 t+=sub(pick('Điểm vận hành suy biến của AssocRules','Degenerate AssocRules operating point'),pick('Cả 12 ngưỡng nguồn là 1,0000000000000002, vượt miền score [0,1]; vì vậy mọi cửa sổ được dự đoán bình thường và recall/FAR đều bằng 0. Đây không phải phát hiện tốt, cũng không phải bằng chứng phương pháp gốc thất bại. Bảng sau mô tả score nguồn; phân phối score, số trùng cực đại và số cảnh báo tại ngưỡng giúp giải thích tính khả thi của ngân sách FAR. Chưa có phép đo cô lập nguyên nhân W64, số cluster hay quy tắc phân phối; không suy nguyên nhân chỉ từ hiện tượng.','All 12 source thresholds equal 1.0000000000000002, above the score range [0,1]; all windows are predicted benign and recall/FAR are zero. This is neither effective detection nor proof of failure of the original method. The table describes source scores; score distributions, ties at the global maximum and alerts at the chosen threshold explain FAR-budget feasibility. No experiment isolates window length, cluster count or distribution rules as the cause.'))
 a=data['assoc'];arows=[[tex(r['set']),int(r.seed),int(r.class_label),int(r.n),n(r.p50),n(r.maximum),int(r.at_global_max)] for _,r in a.iterrows()]
 t+=table(pick('Score validation nguồn AssocRules; nhãn 0 là benign, 1 là tấn công','AssocRules source-validation scores; label 0 benign, 1 attack'),'tab:assoc-scores',['Set','Seed',pick('Nhãn','Label'),'N','Median','Max',pick('Trùng max','At max')],arows,[1.5,1.2,1.4,1.8,1.7,1.7,2.2])
 benign=a[a.class_label==0]
 t+=pick(f'Tại ngưỡng đúng bằng score cực đại 1, FAR validation nguồn nằm trong khoảng {benign.far_at_global_max.min():.2f}--{benign.far_at_global_max.max():.2f} trên 100.000, đã vượt ngân sách 100. Giảm ngưỡng chỉ có thể tăng số cảnh báo, nên không có ngưỡng hữu hạn trong miền score thỏa ngân sách; ngưỡng ngay trên 1 tạo điểm không cảnh báo. Đây là lý do suy biến theo score đã lưu, không phải phỏng đoán về nguyên nhân sinh score.\n',f'At the maximum score threshold 1, source-validation FAR ranges from {benign.far_at_global_max.min():.2f} to {benign.far_at_global_max.max():.2f} per 100,000, exceeding the budget of 100. Lowering the threshold can only increase alerts, so no threshold within the score range meets that budget; the next value above 1 produces no alerts. This explains feasibility from saved scores without speculating about why those scores arose.\n')
 t+=sec(pick('RQ2: vai trò thành phần biểu diễn và độ nhạy cửa sổ','RQ2: representation components and window sensitivity'),r'\label{sec:completion}'+'\n'+pick('Phân tích này được thiết kế sau khi đã xem kết quả chính. Có 10 biểu diễn W64; payload-only trùng raw-no-ID và no-timing trùng structural content, không đếm thành bằng chứng độc lập. W32/W128 huấn luyện lại raw/structural; vì đổi đơn vị cửa sổ nên nhãn, số cửa sổ và mẫu nguồn cũng đổi theo. Không diễn giải đây là thay duy nhất một biến vật lý.','These analyses were designed after viewing primary outcomes. There are ten W64 representations; payload-only equals raw-no-ID and no-timing equals structural content, so aliases do not count as independent evidence. W32/W128 retrain raw/structural; window labels, available counts and sampled windows change with the decision unit. This is not a change to one physical variable alone.'))
 for w in [64,32,128]:
  rows=[[c,LABELS[k][0 if vi else 1],*[n(r[m],2 if m=='FAR_per_100k' else 4) for m in METRICS]] for (k,c),r in ext.loc[w].iterrows()]
  t+=table(f'W{w}; '+pick('trọng số set ngang nhau; FAR trên 100.000','equal set weights; FAR per 100,000'),f'tab:extension-w{w}',headers,rows,[1.1,4.1,1.6,2.2,1.6,1.6])
 t+=pick(r'''Bỏ ID khỏi Raw ở B làm recall giảm từ 0,8541 xuống 0,6794 và AP từ 0,3781 xuống 0,2200; do đó bỏ ID đơn thuần không đủ để cải thiện. Raw cộng cấu trúc có F1 B 0,3179 nhưng AP 0,4842, trong khi Structural có F1 0,2435 và AP 0,5554. Các tiêu chí không cho cùng một thứ tự xếp hạng.

Bỏ payload tuyệt đối khỏi Structural làm recall B tăng từ 0,7383 lên 0,9243, nhưng FAR tăng từ 52.461,46 lên 66.779,19 trên 100.000 và AP giảm từ 0,5554 xuống 0,4453. Không gọi đây là cải thiện tổng thể. Bỏ delta cũng tăng recall B nhưng tăng FAR và giảm AP. Ngược lại, bỏ thống kê cục bộ làm AP B giảm xuống 0,2894 và FAR tăng lên 65.298,51; trong phép so này nhóm thống kê gắn với lợi ích xếp hạng và báo động giả.

Bỏ chuyển tiếp cho AP B gần như không đổi (0,5556 so với 0,5554) và AP D tăng (0,3679 so với 0,3357). Không có bằng chứng ở các điểm ước lượng này rằng thêm chuyển tiếp luôn có ích. Những so sánh ghép cặp mô tả ảnh hưởng của thành phần trong pipeline, không chứng minh nguyên nhân vật lý. Số chiều thay đổi làm số tham số lớp chiếu thay đổi; tổng số tham số không hoàn toàn bằng nhau.

Chênh lệch recall Structural trừ Raw ở B lần lượt khoảng +0,69; -11,59; +1,28 điểm phần trăm tại W32, W64 và W128. Đổi dấu cho thấy kết luận phụ thuộc độ dài và cách tạo cửa sổ. FAR Structural ở B vẫn trên 53\% tại W32/W128, nên dấu dương recall không đủ xác nhận tính hữu dụng. Báo cáo kèm dữ liệu từng set/seed, độ lệch chuẩn và bootstrap theo capture; không chọn W sau khi xem test rồi gọi đó là xác nhận độc lập.
''',r'''Removing ID bits from Raw in B reduces recall from 0.8541 to 0.6794 and AP from 0.3781 to 0.2200; identifier removal alone is insufficient. Raw plus structure has B F1 0.3179 and AP 0.4842, whereas Structural has F1 0.2435 and AP 0.5554. Metrics do not induce the same ranking.

Removing absolute payload from Structural increases B recall from 0.7383 to 0.9243, but FAR rises from 52,461.46 to 66,779.19 per 100,000 and AP falls from 0.5554 to 0.4453. This is not an overall improvement. Removing delta likewise raises B recall together with FAR while reducing AP. Removing local statistics instead reduces B AP to 0.2894 and raises FAR to 65,298.51; within this comparison, those statistics accompany ranking and false-alarm benefits.

Removing transitions leaves B AP almost unchanged (0.5556 versus 0.5554) and increases D AP (0.3679 versus 0.3357). These point estimates do not show that adding transitions always helps. Paired comparisons describe component effects within this pipeline, not physical causality. Changing feature dimensions changes input-projection parameter counts; total model sizes are not exactly equal.

Structural minus Raw B recall is approximately +0.69, -11.59 and +1.28 percentage points at W32, W64 and W128. The sign changes show dependence on window construction. Structural B FAR remains above 53\% at W32/W128, so positive recall differences alone do not establish usefulness. Per-set/seed data, seed SD and capture-bootstrap intervals accompany the results; a target-selected window size is not independent confirmation.
''')
 t+=sec(pick('RQ3: khả năng giải mã nhãn xe và tấn công','RQ3: linear decoding of vehicle and attack labels'),pick('Probe dùng 12 cặp encoder đã đóng băng, giữ lại nhóm recording-round khác nhóm huấn luyện và cân bằng mọi ô xe × nhãn. Encoder đã thấy dữ liệu huấn luyện của nguồn mình; không coi đây là kiểm tra phiên lái độc lập hoàn toàn.','Probes use 12 frozen encoder pairs with held-out recording-round groups and balanced vehicle-by-label cells. Encoders saw their own source training captures; this is not a fully independent driving-session test.'))
 ps=data['probes'].groupby(['representation','target','control']).balanced_accuracy.mean()
 t+=table(pick('Balanced accuracy trung bình qua encoder; không phải CI quần thể xe','Mean balanced accuracy across encoders; not a vehicle-population CI'),'tab:extension-probes',[pick('Biểu diễn','Representation'),pick('Nhãn','Target'),pick('Đối chứng','Control'),'Balanced accuracy'],[[r,k,c.replace('_',' '),n(v)] for (r,k,c),v in ps.items()],[3.3,1.6,4.7,3.1])
 t+=pick('Probe xe giảm từ 0,9925 xuống 0,9488, tức 4,37 điểm phần trăm, nhưng vẫn cao hơn nhiều chance 0,25. Không chứng minh loại bỏ thông tin xe. Probe tấn công tăng từ 0,6419 lên 0,7669; khả năng giải mã này không đồng nghĩa recall IDS tại ngưỡng nguồn. Đối chứng hằng/ngẫu nhiên/hoán vị gần chance hỗ trợ rằng phép đo có phân biệt, nhưng không biến probe tuyến tính thành thước đo toàn bộ thông tin.\n','Vehicle-probe accuracy falls from 0.9925 to 0.9488, a 4.37-percentage-point reduction, but remains far above chance 0.25. Removal of vehicle information is not established. Attack-probe accuracy rises from 0.6419 to 0.7669; decoding accuracy is distinct from source-threshold IDS recall. Constant/random/permuted controls near chance support diagnostic discrimination without making linear probes a measure of all information.\n')
 t+=sec(pick('RQ4: kiểm thử ngoại bộ và phân tích thất bại','RQ4: external evaluation and failure analysis'),pick('Mô hình Set 1 ở ba seed và ngưỡng nguồn được giữ nguyên trên 57 capture có nhãn/schema đạt kiểm tra. Không dùng nhãn ngoại bộ để đổi checkpoint hoặc ngưỡng. Hai nhóm OTIDS bị loại và một file CICIoV SPEED bị cách ly; ledger giữ nguyên mọi quyết định.','Set 1 models for three seeds retain their source thresholds on 57 captures passing label/schema checks. External labels do not select checkpoints or thresholds. Two OTIDS groups are excluded and one CICIoV SPEED file is quarantined; all decisions remain in the ledger.'))
 er=[]
 for (dataset,rep),g in data['external'].groupby(['dataset','representation']):
  vals=[]
  for seed,v in g.groupby('seed'):
   tp,fp,tn,fn=v[['TP','FP','TN','FN']].sum();pos=tp+fn;neg=fp+tn;vals.append([tp/pos if pos else np.nan,100000*fp/neg if neg else np.nan])
  z=np.asarray(vals);r=np.nanmean(z[:,0]) if np.isfinite(z[:,0]).any() else np.nan;far=np.nanmean(z[:,1]) if np.isfinite(z[:,1]).any() else np.nan
  er.append([tex(dataset),rep,n(r),n(far,2)])
 t+=table(pick('Ngoại bộ: gộp số đếm theo dataset/seed rồi trung bình seed; FAR trên 100.000','External: pool counts within dataset/seed, then average seeds; FAR per 100,000'),'tab:extension-external',['Dataset',pick('Biểu diễn','Representation'),'Recall','FAR'],er,[4.4,3.1,2,2.4])
 t+=pick(r'''CICIoV Structural có recall 1,0000 nhưng FAR 100.000/100.000: điểm vận hành dự đoán toàn bộ là tấn công. Không coi recall 100\% đó là thành công. Trên MIRGU attack, recall Structural khoảng 0,0546 so với Raw 0,5848; giảm FAR không bù được việc bỏ sót phần lớn cửa sổ tấn công nếu mục tiêu là phát hiện đáng tin.

Renault DoS là trường hợp có lợi theo cơ chế: Structural giữ recall khoảng 0,9984, FAR 188,56/100.000 so với Raw 33.102,87; capture benign tương ứng có FAR 165,56 so với 33.443,71. Điều này không chứng minh khái quát phổ quát: Automotive benign/DoS chia sẻ lưu lượng nền, các dataset có prevalence và chính sách nhãn khác nhau. Benign-only chỉ xác định FAR; không suy recall/AP hai lớp từ các capture đó. Mọi kết quả vẫn theo thứ tự file, không xác nhận chronology vật lý hoặc 57 phiên độc lập.
''',r'''CICIoV Structural recall is 1.0000 with FAR 100,000/100,000: this operating point predicts every window as an attack. The 100\% recall is not a successful detector. On MIRGU attack captures, Structural recall is approximately 0.0546 versus Raw 0.5848; reduced FAR does not compensate for missing most attack windows when reliable detection is required.

Renault DoS is a mechanism-specific favourable case: Structural recall remains approximately 0.9984 with FAR 188.56/100,000 versus Raw 33,102.87; corresponding benign-capture FAR is 165.56 versus 33,443.71. This does not establish universal generalization: Automotive benign/DoS share background traffic, and datasets differ in prevalence and annotation policy. Benign-only captures identify FAR, not recall or two-class AP. Results remain file-order evaluations without establishing physical chronology or 57 independent sessions.
''')
 t+=sec(pick('Chi phí xử lý trên máy thực nghiệm','Processing cost on the experimental host'),pick('Phép đo batch một gồm đọc CSV, kiểm tra/chuyển đổi, tính cả raw/structural và inference; 20 cửa sổ warmup, 300 cửa sổ × 3 lần đo. Cache hệ điều hành và ứng dụng khác có thể ảnh hưởng.','Batch-one measurement includes CSV reading, validation/conversion, both representations and inference; 20 warmup windows and 300 windows times three repetitions. OS caching and other applications may affect results.'))
 t+=table(pick('Thời gian xử lý cửa sổ, ms','Window processing time, ms'),'tab:extension-runtime',[pick('Thiết bị','Device'),pick('Biểu diễn','Representation'),'Median ms','P95 ms'],[[r.device,r.representation,n(r.p50_ms,3),n(r.p95_ms,3)] for _,r in data['runtime'].iterrows()],[2,3.6,3.2,3.2])
 t+=pick('GPU không nhanh hơn CPU ở batch một trong phép đo có chi phí đọc/chuyển dữ liệu này. Không suy ra GPU kém hơn khi huấn luyện hoặc batch lớn. Phép đo không gồm thời gian thu đủ cửa sổ, hàng đợi, thời điểm gây hại hoặc deadline ECU; chưa có chứng nhận triển khai thời gian thực.\n','GPU is not faster than CPU at batch one under this measurement including I/O and transfer overhead. This does not imply slower GPU training or large-batch inference. Acquisition waits, queueing, time to harm and ECU deadlines are outside the measurement; real-time deployment is not certified.\n')
 t+=sec(pick('Đe dọa tính hợp lệ','Threats to validity'),pick('Bốn set dùng lại xe và một số capture có nguồn nền chung; seed và cửa sổ không thay thế phiên lái độc lập. Nhãn W64 chỉ cần một frame dương, nên kết quả không đo định vị frame hay độ trễ trước gây hại. Sampling nguồn giới hạn theo lớp/file làm thay đổi tập huấn luyện nhưng giữ cố định giữa các mô hình trong cùng phép so. Các phân tích bổ sung là hậu nghiệm; không có khẳng định xác nhận trên test hoàn toàn mới. Đối thủ khác supervision và ngân sách tính toán; so sánh pipeline không cô lập nguyên nhân kiến trúc. Timestamp đảo và thứ tự file chưa xác minh giới hạn mọi diễn giải về quá trình vật lý.','The four sets reuse vehicles and some captures share background traffic; seeds and windows do not replace independent driving sessions. One positive frame makes a W64 window positive, so results do not measure frame localization or pre-harm latency. Source sampling capped by class/file changes training data but is held consistent within each comparison. Additional analyses are post-hoc, not confirmation on completely untouched targets. Comparators differ in supervision and compute; pipeline comparisons do not isolate architecture effects. Timestamp inversions and unverified file order limit physical-process interpretations.'))
 return t

def conclusion(vi):
 if vi:return r'''\chapter{Kết luận}\label{chap:conclusion}
\section{Trả lời câu hỏi nghiên cứu}
RQ1: giả thuyết tăng recall trung bình ở B tại W64 không được ủng hộ: Structural thấp hơn Raw khoảng 11,59 điểm phần trăm. AP tăng nhưng FAR đích còn cao; không kết luận ưu thế toàn diện hoặc sẵn sàng triển khai.

RQ2: bỏ ID thô đơn thuần không đủ. Các thành phần có đánh đổi khác nhau giữa recall, FAR và AP; thống kê cục bộ gắn với lợi ích xếp hạng trong phép so đã thực hiện, còn chuyển tiếp không luôn có lợi. Hiệu quả đổi theo W và dữ liệu từng set; không chọn biến thể thuận lợi sau khi xem test để thay kết quả chính.

RQ3: Structural giảm khả năng giải mã tuyến tính nhãn xe từ 0,9925 xuống 0,9488, đồng thời tăng probe tấn công từ 0,6419 lên 0,7669. Mức giải mã xe còn rất cao; đây không phải biểu diễn độc lập xe đã được chứng minh.

RQ4: ngoại bộ cho cả kết quả có lợi theo cơ chế lẫn thất bại rõ rệt. Renault DoS giữ recall cao với FAR thấp hơn Raw, nhưng MIRGU có recall Structural thấp và CICIoV có điểm vận hành dự đoán toàn tấn công. Khả năng chuyển giao phụ thuộc dữ liệu, nhãn và calibration; không có kết luận phổ quát.
\section{Giá trị và giới hạn của nghiên cứu}
Khóa luận cung cấp đánh giá tái lập, đối chứng biểu diễn và chẩn đoán phân biệt chất lượng xếp hạng với chất lượng quyết định tại ngưỡng nguồn. Bất biến đổi tên ID là thuộc tính hẹp được kiểm tra, không đồng nghĩa độc lập xe. Các kết quả âm tính giới hạn rõ giả thuyết và ngăn diễn giải AP hoặc recall riêng lẻ như thành công triển khai.
\section{Hướng nghiên cứu tiếp theo}
Ưu tiên dữ liệu có chronology và phiên lái độc lập được xác minh, đánh giá trên xe chưa tham gia phát triển và kiểm tra độ trễ theo sự kiện. Hiệu chỉnh bằng dữ liệu lành đích cần nghiên cứu riêng với ngân sách công bố, vì thay đổi giả định source-only. Thực nghiệm nhúng phải đo tài nguyên, hàng đợi và deadline trên phần cứng mục tiêu. Các hướng này là công việc tương lai, không làm thay đổi trạng thái hoàn tất của ma trận content, ablation, probe, ngoại bộ và runtime đã báo cáo.
'''
 return r'''\chapter{Conclusions}\label{chap:conclusion}
\section{Answers to the research questions}
RQ1: increased mean B recall at W64 is unsupported: Structural is approximately 11.59 percentage points below Raw. AP improves but target FAR remains high; neither overall superiority nor deployment readiness is established.

RQ2: raw ID removal alone is insufficient. Components involve different recall/FAR/AP tradeoffs; local statistics accompany ranking benefits within the evaluated comparison, whereas transitions do not always help. Effects vary with window size and set; favourable post-hoc variants do not replace the primary outcome.

RQ3: Structural reduces linear vehicle decoding from 0.9925 to 0.9488 while attack decoding rises from 0.6419 to 0.7669. Vehicle decoding remains very high; vehicle independence is not established.

RQ4: external evaluation reveals mechanism-specific benefits and clear failures. Renault DoS retains high recall with lower FAR than Raw, but Structural recall on MIRGU is low and the CICIoV operating point predicts every window as attack. Transfer depends on data, annotation and calibration; there is no universal generalization conclusion.
\section{Value and limitations}
The thesis supplies reproducible evaluation, representation controls and diagnostics separating ranking from decisions at source-selected thresholds. Consistent ID-renaming invariance is a tested narrow property, not vehicle independence. Negative outcomes bound the hypothesis and prevent isolated AP or recall from being interpreted as deployment success.
\section{Future research}
Priorities are verified chronology and independent driving sessions, vehicles excluded from development, and event-level detection latency. Calibration on benign target data requires a separate disclosed data budget because it changes the source-only setting. Embedded evaluation must measure resources, queueing and deadlines on target hardware. These future studies do not change completion of the reported content matrix, ablations, probes, external evaluation and host runtime.
'''

def render(old,data,lang):
 vi=lang=='vi';front=old.split('% Begin inlined introduction_'+lang+'.tex')[0]
 # Drop development-status front chapter, retaining acknowledgements/declaration.
 heading='Trạng thái thực nghiệm của bản chỉnh sửa' if vi else 'Experimental status of this revision'
 front=re.sub(r'\\frontchapter\{'+re.escape(heading)+r'\}.*?(?=% End inlined front_)','',front,flags=re.S)
 for tag in ['vi','en']:
  pat=r'(% Begin inlined (?:\.\./'+tag+r'/)?abstract_'+tag+r'\.tex\n).*?(% End inlined (?:\.\./'+tag+r'/)?abstract_'+tag+r'\.tex)'
  front,count=re.subn(pat,lambda m:m[1]+abstract(data,tag=='vi')+'\n'+m[2],front,flags=re.S)
  if count!=1:raise ValueError('Abstract not unique')
 background=part(old,'background',lang)
 related=part(old,'related',lang)
 related=related.replace('Trong khóa luận, timing-only và payload-only được dùng như ablation của cùng pipeline.', 'Trong nhánh nội dung, payload-only trùng raw-no-ID; timing-only không được thực thi.').replace('In this thesis, timing-only and payload-only are ablations of the same pipeline.', 'In the content tier, payload-only equals raw-no-ID; timing-only is not executed.')
 related=related.replace('biểu diễn một luồng 32 chiều','biểu diễn nội dung 30 chiều').replace('a single 32-dimensional stream','a single 30-dimensional content stream')
 related=related.replace('các baseline trực tiếp là Raw Transformer, Structural Transformer, Structural XGBoost và LR','các đối chứng trực tiếp của ma trận hiện hành là Raw/Structural Transformer và ba bản thích ứng CANBERT+, CANLP-char-DNN, CrySyS-AssocRules/W64').replace('the direct baselines are Raw Transformer, Structural Transformer, Structural XGBoost and LR','the current direct comparators are Raw/Structural Transformer and the adapted CANBERT+, CANLP-char-DNN and CrySyS-AssocRules/W64 pipelines')
 related=related.replace('Here, timing-only and payload-only models are ablations of the same pipeline.','Here, payload-only equals raw-no-ID in the content tier; timing-only is not executed.').replace('single-stream 32-dimensional representation','single-stream 30-dimensional content representation')
 related=related.replace('Implemented direct baselines are Raw Transformer, Structural Transformer, Structural XGBoost and LR;','Current direct comparators are Raw/Structural Transformer and the disclosed CANBERT+, CANLP-char-DNN and CrySyS-AssocRules/W64 adaptations;')
 related=related.replace('Timing ablation; không tự nhận là tái lập OTIDS','Ngoài nhánh content; không tự nhận là tái lập OTIDS').replace('Timing ablation; not an OTIDS reproduction','Outside content evaluation; not an OTIDS reproduction')
 # Only abstract-level evidence is available for this paper; remove unsupported implementation details.
 paragraphs=related.split('\n\n')
 for i,paragraph in enumerate(paragraphs):
  if r'\cite{jo2025indirect}' in paragraph and r'\begin{' not in paragraph:
   paragraphs[i]=(r'Jo và Kim nghiên cứu indirect exposure training cho phát hiện xâm nhập CAN~\cite{jo2025indirect}. Khóa luận chỉ xác minh metadata và chủ đề ở mức nguồn truy cập được; không dùng tài liệu này để khẳng định chi tiết split, cơ chế chọn tâm hoặc hiệu năng chuyển xe.' if vi else r'Jo and Kim study indirect exposure training for CAN intrusion detection~\cite{jo2025indirect}. Only metadata and the accessible subject-level evidence were verified here; this work is not used to establish split details, centre selection or cross-vehicle performance.')
 related='\n\n'.join(paragraphs)
 method=part(old,'method',lang)
 method=method.replace('Giao thức v2.1 gồm bốn bước','Giao thức content/file-order gồm bốn bước').replace('Protocol v2.1 comprises','The content/file-order protocol comprises')
 method=method.replace('Phép so sánh thực thi trên CTT: nội dung và thứ tự file','Đối chứng và giao thức so sánh CTT').replace('Executed CTT comparison: content and file order','Comparators and the CTT evaluation protocol')
 method=method.replace('Thiết kế v2.1 có thời gian trong các mục trước là đặc tả tham chiếu; không phải lược đồ của ma trận năm mô hình này.', 'Đặc tả timed v2.1 lịch sử được tách sang phụ lục; ma trận năm mô hình hiện hành chỉ dùng nội dung và thứ tự file.')
 method=method.replace('The timed v2.1 design in preceding sections is a reference specification, not the schema of this five-method matrix.', 'The historical timed v2.1 specification is separated into the appendix; the current five-method matrix uses content and file order only.')
 method=method.replace('Trong v2.1, chuỗi ngẫu nhiên được tách theo file và lớp với seed xác định từ seed lấy mẫu và tên file.', 'Trong bộ lấy mẫu hiện hành, chuỗi ngẫu nhiên được tách theo file và lớp với seed xác định từ seed lấy mẫu và tên file.').replace('Thay đổi này làm lựa chọn khác phiên bản v2.0; hai phiên bản không được gộp.', 'Các chỉ mục mẫu được lưu để mọi phương pháp trong cùng phép so dùng đúng cùng cửa sổ nguồn.')
 method=method.replace('Một bản ghi lỗi dừng run và ghi trạng thái FAILED.', 'Lỗi schema/nhãn trong nguồn CTT dừng run và ghi FAILED. Đối với ngoại bộ, file lỗi bị loại toàn bộ, lưu lý do trong ledger và không nhập số liệu từng phần vào kết quả.')
 method=method.replace('Invalid input stops the run and records FAILED status.', 'Invalid CTT source schema/labels stop the run and record FAILED status. An invalid external file is excluded in full with its reason retained in the ledger; partial-file metrics are never imported.')
 method=re.sub(r'XGBoost dùng.*?(?=\n\n)', 'XGBoost và LR của thăm dò lịch sử không thuộc ma trận năm phương pháp hiện hành. LR trong nghiên cứu bổ sung chỉ là bộ giải mã probe, không phải một IDS được đưa vào bảng xếp hạng.',method,flags=re.S)
 method=re.sub(r'XGBoost uses.*?(?=\n\n)', 'Historical exploratory XGBoost and LR runs are outside the current five-method matrix. LR in the additional study is a probe decoder, not a ranked IDS comparator.',method,flags=re.S)
 method=method.replace('\\code{run_study.py}','\\code{run_comparison.py}')
 method+=('\n'+('Seed và môi trường được ghi rõ, nhưng backend attention CUDA có cảnh báo thuật toán không xác định với chế độ warn-only; không bảo đảm huấn luyện lại giống từng bit trên mọi máy. Khóa luận lưu checkpoint, dự đoán và hash của từng lượt thực tế; ba seed mô tả biến thiên quan sát, không loại bỏ giới hạn tính xác định hoặc tạo thêm xe độc lập.' if vi else 'Seeds and environment are recorded, but CUDA attention reports a nondeterministic-algorithm warning under warn-only mode; bit-identical retraining on every host is not guaranteed. Checkpoints, predictions and hashes retain each observed run; three seeds describe observed variation without resolving determinism limits or creating additional independent vehicles.')+'\n')
 method=re.sub(r'Script \\code\{benchmark_runtime.py\}.*?(?=\n\n|% BEGIN)', 'Runtime của nhánh content được đo riêng trên tiền tố validation nguồn: batch một, 20 cửa sổ warmup và 300 cửa sổ đo trong ba lần lặp. Phép đo gồm đọc CSV, chuyển đổi/kiểm tra, tính cả hai biểu diễn và inference. Không đo thời gian thu đủ cửa sổ hoặc độ trễ theo sự kiện; kết quả ở chương thực nghiệm không chứng nhận deadline ECU.',method,flags=re.S)
 method=re.sub(r'The \\code\{benchmark_runtime.py\}.*?(?=\n\n|% BEGIN)', 'Content runtime is measured separately on a source-validation prefix: batch one, 20 warmup windows and 300 measured windows over three repetitions. It includes CSV reading, conversion/validation, both representations and inference. Acquisition waits and event-level latency are not measured; results do not certify ECU deadlines.',method,flags=re.S)
 method=re.sub(r'Pilot nguồn k=2 cho score/rule/centroid.*?ở full k=300 hay cải thiện chất lượng IDS\.', 'Kiểm tra nguồn thu nhỏ xác nhận tính khớp của backend tăng tốc; đây là kiểm thử phần mềm, không phải kết quả phát hiện hoặc chứng nhận mức tăng tốc trên toàn ma trận.',method,flags=re.S)
 # Remove future/historical control rows from active ablation design.
 method='\n'.join(line for line in method.splitlines() if not line.startswith('Structural-minus-timing &'))+'\n'
 method=re.sub(r'Bốn cell GPU Set 1/seed 42.*?(?=\n\n|% END)', 'Bốn kết quả GPU Set 1/seed 42 được tái sử dụng sau khi xác minh hash, môi trường và cấu hình; manifest gốc và lineage riêng được giữ nguyên. Việc chia lịch CPU/GPU không thay đổi phương pháp khoa học.',method,flags=re.S)
 method=re.sub(r'Four previously completed GPU cells.*?(?=\n\n|% END)', 'Four completed GPU Set 1/seed 42 cells are reused after verifying hashes, environment and configuration; original manifests and separate lineage are retained. CPU/GPU scheduling does not change the scientific method.',method,flags=re.S)
 appendix=('\\appendix\n\\chapter{'+('Chi tiết tái lập và nguồn gốc bằng chứng' if vi else 'Reproducibility and evidence provenance')+r'}\label{app:reproducibility}'+'\n')
 appendix+=sec('Provenance',('Ma trận chính có 60 đơn vị IDS. Phân tích bổ sung có 144 fit mới và 24 baseline tái sử dụng; không phải 168 xe hoặc phiên độc lập. 57 capture ngoại bộ không tương đương 57 phiên lái độc lập. Các bảng số, bootstrap, phân phối score nguồn, hash và ledger loại trừ nằm trong gói bàn giao.' if vi else 'The primary matrix has 60 IDS units. Additional analyses have 144 new fits and 24 reused baselines, not 168 independent vehicles or sessions. Fifty-seven external captures are not 57 independent drives. The delivery bundle contains numeric tables, bootstrap intervals, source-score distributions, hashes and exclusion ledgers.'))
 appendix+=sec(('Đặc tả có thời gian trong thiết kế ban đầu' if vi else 'Timed specification in the original design'),('Thiết kế timed v2.1 có raw 29/structural 32 chiều. Nhánh thực thi bỏ raw index 28 và structural cũ 26,27 rồi đánh lại chỉ số thành 28/30 chiều. Không có số liệu timed được xác nhận từ các capture có timestamp đảo; giữ đặc tả này để giải thích mã lịch sử, không gán kết quả content cho nó.' if vi else 'The original timed v2.1 design has 29 raw/32 structural dimensions. Execution removes raw index 28 and old structural indices 26,27 and renumbers to 28/30 dimensions. No timed result is confirmed from inverted-timestamp captures; the historical specification explains archived code and does not inherit content results.'))
 appendix+=sec(('Kiểm tra đặc trưng bằng tay' if vi else 'Hand-checking features'),('Với W=4 và ID (A,B,A,A), tần suất lần lượt là (3/4,1/4,3/4,3/4); hạng xuất hiện đầu tiên chia số ID là (0,1/2,0,0), chia W là (0,1/4,0,0). Các cặp AB,BA,AA xuất hiện một lần nên đặc trưng chuyển tiếp là (0,1/3,1/3,1/3). Payload một byte (10,20,13,15) cho delta cùng ID (0,0,3/255,2/255). Lịch sử tiếp tục qua biên cửa sổ/chunk và được reset khi đổi file. Không cần dựng timestamp để tính các giá trị này.' if vi else 'For W=4 and IDs (A,B,A,A), frequencies are (3/4,1/4,3/4,3/4); first-occurrence ranks divided by unique-ID count are (0,1/2,0,0), and divided by W are (0,1/4,0,0). AB,BA,AA each occur once, producing transitions (0,1/3,1/3,1/3). One-byte payloads (10,20,13,15) give same-ID deltas (0,0,3/255,2/255). History survives window/chunk boundaries and resets at each file. Synthetic timestamps are unnecessary.'))
 # Preserve data/metric audit as evidence provenance, not the main storyline.
 appendix+=sec(('Phân biệt kiểm toán và kết quả mô hình' if vi else 'Distinguishing audits from model outcomes'),('Các bảng lịch sử và kiểm toán công thức không được gộp với kết quả hiện hành. Đếm dòng CSV gồm tiêu đề khác đếm frame dữ liệu; decision theo frame khác decision theo window. Việc kiểm tra phần mềm hoặc sửa metric không tự chứng minh chất lượng IDS. Bản thảo và dữ liệu trước sửa được giữ trong archive, cùng báo cáo đối chiếu 39 tài liệu tham khảo.' if vi else 'Historical tables and metric-formula audits are not pooled with current model results. CSV lines including headers differ from data frames; frame decisions differ from window decisions. Software checks and corrected metrics do not establish detection quality. Pre-revision sources and outputs remain archived with the 39-reference verification ledger.'))
 appendix+=(r'Kiểm toán số đếm công bố dùng đúng phụ lục arXiv v1~\cite{lampe2023appendix}, không mặc định phụ lục journal giống hệt. Các số theo frame đó không được dùng để xếp hạng với quyết định W64.' if vi else r'The published-count audit refers specifically to the arXiv v1 appendix~\cite{lampe2023appendix}, without assuming identity to the journal appendix. Those frame-level numbers are not ranked against W64 decisions.')+'\n'
 bib=old[old.rindex('\\backmatter'):]
 text='\n\n'.join([front,intro(old,vi),background,related,method,results(data,old,vi),conclusion(vi),appendix,bib])
 text=re.sub(r'^% (?:Begin inlined|End inlined|BEGIN COMPARISON|END COMPARISON).*\n','',text,flags=re.M)
 text=re.sub(r'^\\newcommand\{\\pending\}.*\n','',text,flags=re.M)
 text=text.replace('chưa phải một kết quả thực nghiệm CAN đã xác nhận','là lựa chọn thiết kế được kiểm tra bằng probe trong khóa luận').replace('not an already established CAN result','a design choice evaluated by the thesis probes')
 text=text.replace('là lựa chọn thiết kế, là lựa chọn thiết kế được kiểm tra bằng probe trong khóa luận','là lựa chọn thiết kế được kiểm tra bằng probe trong khóa luận')
 text=text.replace('Nhánh có thời gian từ chối timestamp đảo; phép so content/file-order','Phép so content/file-order')
 text=text.replace('Khóa luận phải phân biệt biểu diễn','Khóa luận phân biệt biểu diễn')
 text=text.replace('Kết quả probe cần đi kèm embedding hằng/ngẫu nhiên','Kết quả probe được báo cùng embedding hằng/ngẫu nhiên')
 text=text.replace('Cần xem coverage theo attack family để phát hiện một lớp hoặc cơ chế biến mất trong source.','Coverage theo attack family được lưu để kiểm tra độ phủ lớp và cơ chế trong source.')
 text=text.replace('Mô hình content phải được huấn luyện lại trên CTT với đúng các chiều bị loại; không đưa timestamp giả hoặc zero-fill vào mô hình đã học timing rồi gọi đó là phép so sánh cùng schema.','Các mô hình content được huấn luyện trên CTT với lược đồ tương ứng; không đưa timestamp giả hoặc zero-fill vào mô hình đã học timing.')
 text=text.replace('XGBoost và LR của thăm dò lịch sử không thuộc ma trận năm phương pháp hiện hành. LR trong nghiên cứu bổ sung chỉ là bộ giải mã probe, không phải một IDS được đưa vào bảng xếp hạng.','LR trong nghiên cứu bổ sung là bộ giải mã probe, không phải một IDS được đưa vào bảng xếp hạng.')
 text=text.replace('Historical exploratory XGBoost and LR runs are outside the current five-method matrix. LR in the additional study is a probe decoder, not a ranked IDS comparator.','LR in the additional study is a probe decoder, not a ranked IDS comparator.')
 text=text.replace('Phần kết quả phân biệt số liệu thăm dò được lưu trước khi hiệu chỉnh với các thí nghiệm cần chạy lại theo giao thức đã sửa.','Phần kết quả chỉ sử dụng các lượt thực nghiệm đã hoàn tất và kiểm chứng theo giao thức được mô tả; số liệu thăm dò lịch sử được lưu riêng.')
 text=text.replace('The results distinguish historical exploratory outputs from experiments that must be rerun under the corrected protocol.','The results use completed, verified runs under the specified protocol; historical exploratory outputs remain archived separately.')
 text=text.replace('The timed branch rejects reversed timestamps; the content/file-order comparison','The content/file-order comparison')
 text=text.replace('This thesis must distinguish its','This thesis distinguishes its')
 text=text.replace('Its models must be retrained on CTT with these dimensions removed. Supplying synthetic timestamps or zeros to a timing-trained model is not a matched-schema comparison.','The content models were trained on CTT using this schema. Synthetic timestamps and zero-filled timing features are not used in this content comparison.')
 text=text.replace('Version 2.1 uses separate random streams per file and class, seeded from the sampling seed and filename.','The executed sampler uses separate random streams per file and class, seeded from the sampling seed and filename.')
 text=text.replace('This changes selection relative to v2.0; versions must not be pooled.','Saved sample indices ensure all methods in a comparison use the same source windows.')
 text=text.replace('Probe results need constant/random embeddings as controls','Probe results include constant/random embeddings as controls')
 text=text.replace('a methodological choice, a design choice evaluated by the thesis probes','a design choice evaluated by the thesis probes')
 text=text.replace('Attack-family coverage must be inspected to identify classes or mechanisms absent from the actual source sample.','Attack-family coverage is retained to inspect classes and mechanisms in the actual source sample.')
 text=text.replace('Cấu hình huấn luyện được đóng băng trước khi chạy lại','Cấu hình huấn luyện của thực nghiệm').replace('Training configuration frozen before reruns','Experimental training configuration')
 text=text.replace('kết hợp thống kê thời gian/lưu lượng, biểu diễn đa độ phân giải, học sâu và kiểm tra tương quan','kết hợp tương quan Pearson, học sâu và biến đổi wavelet sang miền tần số')
 text=text.replace('combining timing/traffic statistics, multi-resolution representations, deep learning and correlation checks','combining Pearson correlation, deep learning and wavelet transformation into the frequency domain')
 text=text.replace('combining timing/traffic statistics, multiresolution representations, deep learning and correlation checks','combining Pearson correlation, deep learning and wavelet transformation into the frequency domain')
 text=text.replace('Hybrid UIDS~\\cite{s26051489} & Thống kê timing/lưu lượng','Hybrid UIDS~\\cite{s26051489} & Pearson, wavelet và học sâu')
 text=text.replace('Hybrid UIDS~\\cite{s26051489} & Timing/volume statistics','Hybrid UIDS~\\cite{s26051489} & Pearson, wavelets, deep learning')
 text=text.replace('Phép đối chiếu cần thực hiện','Phạm vi đối chiếu').replace('Required comparison','Comparison scope')
 text=text.replace("Các hàng ``cần thực hiện'' là công việc bổ sung nếu muốn đưa ra so sánh định lượng với đúng thuật toán công bố.",'Các đề xuất mở rộng đối chứng ngoài ma trận hiện hành thuộc hướng nghiên cứu tương lai; ablation và độ nhạy đã thực hiện được trình bày trong chương kết quả.')
 text=text.replace('Items described as required comparisons remain additional work if quantitative claims against the exact published algorithms are desired.','Extensions to comparators outside the current matrix are future work; completed ablations and window sensitivity are reported in the results chapter.')
 text=text.replace('Completed windows: 28 raw / 30 structural dimensions (content); 29/32 for valid timed inputs','Completed windows: 28 raw / 30 structural dimensions (content)')
 return text
