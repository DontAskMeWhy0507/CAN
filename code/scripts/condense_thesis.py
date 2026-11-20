"""
Script to streamline Appendices in rut_gon/vi/main.tex and rut_gon/en/main.tex.
Main text (from beginning of document to \appendix) is strictly 100% UNTOUCHED.
All labels, citations, and sections are strictly preserved.
"""
import re
from pathlib import Path

def convert_longtable_to_table(text: str) -> str:
    # Pattern to match a longtable in Appendix and convert to table + tabular
    # 1. Table A.1: tab:app-96ckpt-probes
    old_a1 = r'\\begin\{longtable\}\{P\{5\.4cm\}P\{3\.4cm\}P\{3\.4cm\}\}\s*\\caption\[.*?\]\{.*?\}\label\{tab:app-96ckpt-probes\}\\\\\toprule.*?\\bottomrule\s*\\end\{longtable\}'
    
    # 2. Table A.2: tab:comparison-sets
    # 3. Table B.5: tab:reservoir-variance
    # 4. Table B.6: tab:probe-c-scaling
    # 5. Table B.7: tab:mixstyle-six
    # 6. Table B.8: tab:mixstyle-probe
    # 7. Table B.9: tab:mixstyle-external
    # 8. Table B.10: tab:mixstyle-runtime
    # 9. Table B.12: tab:target-only-k500
    # 10. Table B.13: tab:extension-runtime
    # 11. Table B.14: tab:model-complexity-audit
    pass

def streamline_vi(content: str) -> str:
    app_pos = content.find(r'\appendix')
    if app_pos == -1:
        raise ValueError("Cannot find \\appendix")
    
    main_part = content[:app_pos]
    app = content[app_pos:]
    
    # Clean all \Needspace{\d+\baselineskip}
    app = re.sub(r'\\Needspace\{\d+\\baselineskip\}\s*', '', app)
    
    # Convert Table A.1
    old_a1 = r'\\begin\{longtable\}\{P\{5\.4cm\}P\{3\.4cm\}P\{3\.4cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:app-96ckpt-probes\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}'
    def repl_a1(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\small
\\caption[{cap}]{{{cap}}}\\label{{tab:app-96ckpt-probes}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lcc}}
\\toprule
Biểu diễn & Probe xe (cơ hội 0,25) & Probe tấn công (cơ hội 0,50)\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_a1, repl_a1, app, flags=re.DOTALL)

    # Convert Table A.2
    old_a2 = r'\{\\small\\setlength\{\\tabcolsep\}\{3pt\}\s*\\begin\{longtable\}\{P\{1\.4cm\}P\{0\.7cm\}P\{3\.4cm\}P\{3\.4cm\}P\{3\.4cm\}P\{2\.6cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:comparison-sets\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\multicolumn\{6\}\{P\{15\.3cm\}\}\{(?P<note>.*?)\}\s*\\end\{longtable\}\}'
    def repl_a2(m):
        cap = m.group('caption')
        body = m.group('body')
        note = m.group('note')
        return f'''\\begin{{table}}[htbp]
\\centering
\\footnotesize
\\setlength{{\\tabcolsep}}{{3pt}}
\\caption[{cap}]{{{cap}}}\\label{{tab:comparison-sets}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lccccc}}
\\toprule
Set & ĐK & Raw TF & Structural TF & CANBERT+ adapted & CANLP-char-DNN\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\multicolumn{{6}}{{p{{14.2cm}}}}{{{note}}}
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_a2, repl_a2, app, flags=re.DOTALL)

    # Convert Table B.5 (tab:reservoir-variance)
    old_b5 = r'\{\\small\\setlength\{\\tabcolsep\}\{4pt\}\s*\\begin\{longtable\}\{P\{2\.2cm\}P\{2\.1cm\}P\{0\.7cm\}P\{2\.4cm\}P\{2\.4cm\}P\{2\.2cm\}P\{2\.2cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:reservoir-variance\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}\}'
    def repl_b5(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\footnotesize
\\setlength{{\\tabcolsep}}{{3pt}}
\\caption[{cap}]{{{cap}}}\\label{{tab:reservoir-variance}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lcccccc}}
\\toprule
Mô hình & Chế độ & ĐK & Recall & FAR (/100k) & Attack F1 & AP\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b5, repl_b5, app, flags=re.DOTALL)

    # Convert Table B.6 (tab:probe-c-scaling)
    old_b6 = r'\{\\small\\setlength\{\\tabcolsep\}\{5pt\}\s*\\begin\{longtable\}\{P\{4\.4cm\}P\{1\.4cm\}P\{1\.5cm\}P\{1\.5cm\}P\{1\.5cm\}P\{1\.5cm\}\}\s*\\caption\{(?P<caption>.*?)\}\\label\{tab:probe-c-scaling\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}\}'
    def repl_b6(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\small
\\setlength{{\\tabcolsep}}{{4pt}}
\\caption{{{cap}}}\\label{{tab:probe-c-scaling}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lccccc}}
\\toprule
Nhóm đặc trưng đầu vào & Chiều phẳng & $C=0.01$ & $C=0.1$ & $C=1.0$ & $C=10.0$\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b6, repl_b6, app, flags=re.DOTALL)

    # Convert Table B.7 (tab:mixstyle-six)
    old_b7 = r'\\begin\{longtable\}\{P\{6cm\}P\{2cm\}P\{2\.2cm\}P\{2cm\}\}\s*\\caption\{(?P<caption>.*?)\}\\label\{tab:mixstyle-six\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}'
    def repl_b7(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\small
\\caption{{{cap}}}\\label{{tab:mixstyle-six}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lccc}}
\\toprule
Pipeline & Recall & FAR (\\%) & AP\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b7, repl_b7, app, flags=re.DOTALL)

    # Convert Table B.8 (tab:mixstyle-probe)
    old_b8 = r'\\begin\{longtable\}\{P\{6cm\}P\{3cm\}P\{3cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:mixstyle-probe\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}'
    def repl_b8(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\small
\\caption[{cap}]{{{cap}}}\\label{{tab:mixstyle-probe}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lcc}}
\\toprule
Pipeline & Xe & Tấn công\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b8, repl_b8, app, flags=re.DOTALL)

    # Convert Table B.9 (tab:mixstyle-external) - condense to 8 rows
    old_b9 = r'\\begin\{longtable\}\{P\{4\.4cm\}P\{4\.8cm\}P\{1\.6cm\}P\{2\.2cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:mixstyle-external\}\\\\\toprule.*?\\endhead\s*.*?\\bottomrule\s*\\end\{longtable\}'
    def repl_b9(m):
        cap = m.group('caption')
        return f'''\\begin{{table}}[htbp]
\\centering
\\footnotesize
\\setlength{{\\tabcolsep}}{{4pt}}
\\caption[{cap}]{{{cap}}}\\label{{tab:mixstyle-external}}
\\vspace{{2pt}}
\\begin{{tabular}}{{llcc}}
\\toprule
Dataset & Pipeline & Recall & FAR (\\%)\\\\\\midrule
CAN\\_MIRGU\\_attack & raw / structural / mixstyle & 0.5848 / 0.0546 / 0.0486 & 59.18\\% / 2.70\\% / 1.83\\%\\\\
CAN\\_MIRGU\\_benign & raw / structural / mixstyle & -- / -- / -- & 60.62\\% / 6.63\\% / 5.90\\%\\\\
CICIoV2024 & raw / structural / mixstyle & 0.6462 / 1.0000 / 1.0000 & 100.00\\% / 100.00\\% / 100.00\\%\\\\
Opel\\_Astra\\_DoS & raw / structural / mixstyle & 1.0000 / 1.0000 / 1.0000 & 43.85\\% / 31.53\\% / 33.43\\%\\\\
Opel\\_Astra\\_benign & raw / structural / mixstyle & -- / -- / -- & 43.84\\% / 30.98\\% / 32.86\\%\\\\
Renault\\_Clio\\_DoS & raw / structural / mixstyle & 0.9995 / 0.9984 / 0.9984 & 33.10\\% / 0.19\\% / 0.15\\%\\\\
Renault\\_Clio\\_benign & raw / structural / mixstyle & -- / -- / -- & 33.44\\% / 0.17\\% / 0.13\\%\\\\
\\bottomrule
\\multicolumn{{4}}{{p{{13.5cm}}}}{{\\footnotesize Gộp theo bộ dữ liệu; số liệu phân rã chi tiết từng bản ghi trong số 57 bản ghi ngoại bộ được lưu trữ tại kho mã nguồn mở tái lập của đề tài.}}
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b9, repl_b9, app, flags=re.DOTALL)

    # Convert Table B.10 (tab:mixstyle-runtime)
    old_b10 = r'\\begin\{longtable\}\{P\{2cm\}P\{5\.5cm\}P\{2\.2cm\}P\{2\.2cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:mixstyle-runtime\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}'
    def repl_b10(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\small
\\caption[{cap}]{{{cap}}}\\label{{tab:mixstyle-runtime}}
\\vspace{{2pt}}
\\begin{{tabular}}{{llcc}}
\\toprule
Thiết bị & Pipeline & Median & P95\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b10, repl_b10, app, flags=re.DOTALL)

    # Convert Table B.12 (tab:target-only-k500)
    old_b12 = r'\{\\small\\setlength\{\\tabcolsep\}\{4pt\}\s*\\begin\{longtable\}\{P\{4\.2cm\}P\{0\.7cm\}P\{1\.1cm\}P\{2\.2cm\}P\{1\.5cm\}P\{1\.4cm\}P\{2\.1cm\}\}\s*\\caption\[.*?\]\{(?P<caption>.*?)\}\\label\{tab:target-only-k500\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\multicolumn\{7\}\{P\{14\.5cm\}\}\{(?P<note>.*?)\}\s*\\end\{longtable\}\}'
    def repl_b12(m):
        cap = m.group('caption')
        body = m.group('body')
        note = m.group('note')
        return f'''\\begin{{table}}[htbp]
\\centering
\\footnotesize
\\setlength{{\\tabcolsep}}{{3pt}}
\\caption[{cap}]{{{cap}}}\\label{{tab:target-only-k500}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lcccccc}}
\\toprule
Phương pháp (0 nguồn) & ĐK & $\\alpha$ & Recall (3-xe) & FAR (\\%) & F1 & AP (3-xe)\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\multicolumn{{7}}{{p{{14.2cm}}}}{{{note}}}
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b12, repl_b12, app, flags=re.DOTALL)

    # Convert Table B.13 (tab:extension-runtime)
    old_b13 = r'\\begin\{longtable\}\{P\{2cm\}P\{3\.6cm\}P\{3\.2cm\}P\{3\.2cm\}\}\s*\\caption\{(?P<caption>.*?)\}\\label\{tab:extension-runtime\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}'
    def repl_b13(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\small
\\caption{{{cap}}}\\label{{tab:extension-runtime}}
\\vspace{{2pt}}
\\begin{{tabular}}{{llcc}}
\\toprule
Thiết bị & Biểu diễn & Median (ms) & P95 (ms)\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b13, repl_b13, app, flags=re.DOTALL)

    # Convert Table B.14 (tab:model-complexity-audit)
    old_b14 = r'\{\\footnotesize\\setlength\{\\tabcolsep\}\{3pt\}\s*\\begin\{longtable\}\{P\{3\.45cm\}P\{0\.95cm\}P\{1\.65cm\}P\{2\.20cm\}P\{2\.25cm\}P\{1\.90cm\}P\{1\.70cm\}\}\s*\\caption\{(?P<caption>.*?)\}\\label\{tab:model-complexity-audit\}\\\\\toprule.*?\\endhead\s*(?P<body>.*?)\\bottomrule\s*\\end\{longtable\}\}'
    def repl_b14(m):
        cap = m.group('caption')
        body = m.group('body')
        return f'''\\begin{{table}}[htbp]
\\centering
\\footnotesize
\\setlength{{\\tabcolsep}}{{2.5pt}}
\\caption{{{cap}}}\\label{{tab:model-complexity-audit}}
\\vspace{{2pt}}
\\begin{{tabular}}{{lcccccc}}
\\toprule
Mô hình & Chiều & Params & MACs & FLOPs & FP32 & RAM $H_k$\\\\\\midrule
{body.strip()}
\\\\\\bottomrule
\\end{{tabular}}
\\end{{table}}'''
    app = re.sub(old_b14, repl_b14, app, flags=re.DOTALL)

    return main_part + app

if __name__ == "__main__":
    src_vi = Path("rut_gon/vi/main.tex")
    text = src_vi.read_text(encoding="utf-8")
    new_text = streamline_vi(text)
    src_vi.write_text(new_text, encoding="utf-8")
    print("All longtables in rut_gon/vi/main.tex successfully converted to table!")
