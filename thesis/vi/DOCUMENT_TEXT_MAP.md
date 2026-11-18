<!-- FILE: main.tex -->
\documentclass[12pt, a4paper, reqno, oneside]{book}
\usepackage[left=2.5cm, right=2cm, top=2cm, bottom=2cm]{geometry}
\usepackage{amsmath,amsxtra,amssymb,latexsym, amscd,amsthm}
\usepackage{microtype}
\usepackage{indentfirst}
\usepackage{color}
\usepackage{empheq}
\usepackage{iftex}
\ifXeTeX
  \usepackage{fontspec}
  \setmainfont[Ligatures=TeX]{Times New Roman}
  \setsansfont[Ligatures=TeX]{Arial}
  \usepackage[vietnamese,english]{babel}
\else
  \usepackage[utf8]{inputenc}
  \usepackage[T5]{fontenc}
  \usepackage[vietnamese]{babel}
\fi
% \usepackage{amsmath} % đã được nạp ở dòng 3
\usepackage[mathscr]{eucal}
\usepackage{amsfonts}
\usepackage{graphicx}
\usepackage{float}
\usepackage{listings}
\usepackage[dvipsnames]{xcolor}
\usepackage{verbatim}
\usepackage{tikz}
\usetikzlibrary{calc,positioning,arrows.meta}
\usepackage{tkz-graph}
\usepackage{array}
\usepackage{multirow}
% Note: subfigure is legacy and conflicts with modern subcaption; kept commented for compatibility
% \usepackage{subfigure}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{rotating}
\usepackage{longtable}
\usepackage{supertabular}
\usepackage{subcaption}
\usepackage{tabularx}
\usepackage[normalem]{ulem}
\usepackage{pdfpages}
\usepackage[square,numbers]{natbib}
\usepackage{booktabs}
\usepackage{chngcntr}
\usepackage{tabularray}
\usepackage{placeins}
\usepackage{enumitem}
\usepackage{seqsplit}
\usepackage{needspace}
\usepackage[labelfont=bf, textfont=it, justification=centering]{caption}
\captionsetup{labelfont={color=black, bf}, textfont={color=black, it}}
\captionsetup[table]{position=top}
\captionsetup[figure]{position=bottom}

\hyphenation{op-tical net-works semi-conduc-tor}
\usepackage[hyphens,spaces,obeyspaces]{url}
\usepackage{xurl}
\usepackage[colorlinks,bookmarksopen,bookmarksnumbered,citecolor=blue,colorlinks=true,linkcolor=blue,urlcolor=blue,pdftitle={Biểu diễn cấu trúc cho hệ thống phát hiện xâm nhập mạng CAN bus đa phương tiện},pdfauthor={Vũ Tiến Tuấn Trung}]{hyperref}
\def\UrlBreaks{\do\/\do-\do_\do.\do=\do?\do&\do~}
\def\UrlNoBreaks{\do\(\do\[\do\{\do\<\do\:}
\setlength{\emergencystretch}{1.5em}

\renewcommand{\baselinestretch}{1.10}
\setlength{\headheight}{15pt}
\setlength{\textfloatsep}{10pt plus 2pt minus 2pt}
\setlength{\intextsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{8pt plus 2pt minus 2pt}
\setlength{\abovecaptionskip}{4pt}
\setlength{\belowcaptionskip}{4pt}
\titleformat{\section}{\normalfont\Large\bfseries\raggedright}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\large\bfseries\raggedright}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries\raggedright}{\thesubsubsection}{1em}{}

\fancyhf{}
\fancyhead[L]{\small{\leftmark}}
\fancyfoot[C]{\thepage}

\newcommand\chap[1]{%
  \clearpage\phantomsection%
  \chapter*{#1}%
  \addcontentsline{toc}{chapter}{#1}%
  \markboth{#1}{}%
}
\newcommand\sect[1]{%
  \phantomsection%
  \section*{#1}%
  \addcontentsline{toc}{section}{#1}%
}

\renewcommand{\theequation}{\thechapter.\arabic{equation}}
\newtheorem{lemma}{\bf Bổ đề}[chapter]
\newtheorem{theorem}{\bf Định lý}[chapter]
\newtheorem{proposition}{\bf Mệnh đề}[chapter]
\newtheorem{corollary}{\bf Hệ quả}[chapter]
\newtheorem{definition}{\bf Định nghĩa}[chapter]
\newtheorem{remark}{\bf Chú ý}[section]

% Mức tiêu đề sâu (subsubsubsection, paragraph)
\titleclass{\subsubsubsection}{straight}[\subsection]
\newcounter{subsubsubsection}[subsubsection]
\renewcommand\thesubsubsubsection{\thesubsubsection.\arabic{subsubsubsection}}
\renewcommand\theparagraph{\thesubsubsubsection.\arabic{paragraph}}

\titleformat{\subsubsubsection}
  {\normalfont\normalsize\bfseries}{\thesubsubsubsection}{1em}{}
\titlespacing*{\subsubsubsection}
  {0pt}{3.25ex plus 1ex minus .2ex}{1.5ex plus .2ex}

\makeatletter
\renewcommand\paragraph{\@startsection{paragraph}{5}{\z@}%
  {3.25ex \@plus1ex \@minus.2ex}%
  {-1em}%
  {\normalfont\normalsize\bfseries}}
\renewcommand\subparagraph{\@startsection{subparagraph}{6}{\parindent}%
  {3.25ex \@plus1ex \@minus .2ex}%
  {-1em}%
  {\normalfont\normalsize\bfseries}}
\def\toclevel@subsubsubsection{4}
\def\toclevel@paragraph{5}
\def\toclevel@paragraph{6}
\def\l@subsubsubsection{\@dottedtocline{4}{7em}{4em}}
\def\l@paragraph{\@dottedtocline{5}{10em}{5em}}
\def\l@subparagraph{\@dottedtocline{6}{14em}{6em}}
\makeatother

\setcounter{secnumdepth}{4}
\setcounter{tocdepth}{2}

% Thư mục hình ảnh
\graphicspath{{./figs/}}

\definecolor{mygreen}{rgb}{0,0.6,0}
\definecolor{mygray}{rgb}{0.5,0.5,0.5}
\definecolor{mymauve}{rgb}{0.58,0,0.82}

\lstdefinestyle{customc}{
  belowcaptionskip=1\baselineskip,
  breaklines=true,
  frame=single,
  xleftmargin=\parindent,
  language=C,
  showstringspaces=false,
  basicstyle=\footnotesize\ttfamily,
  keywordstyle=\bfseries\color{green!40!black},
  commentstyle=\itshape\color{purple!40!black},
  identifierstyle=\color{blue},
  stringstyle=\color{orange},
  numbers=left,
  numberstyle=\tiny\color{gray},
  stepnumber=1, 
}

\lstdefinestyle{customasm}{
  belowcaptionskip=1\baselineskip,
  frame=single,
  xleftmargin=\parindent,
  language=[x86masm]Assembler,
  basicstyle=\footnotesize\ttfamily,
  commentstyle=\itshape\color{purple!40!black},
  numbers=left,
  numberstyle=\tiny\color{gray},
  stepnumber=1, 
}

\lstset{escapechar=@,style=customc}

\definecolor{processblue}{cmyk}{0.96,0,0,0}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\definecolor{eclipseStrings}{RGB}{42,0.0,255}
\definecolor{eclipseKeywords}{RGB}{127,0,85}
\colorlet{numb}{magenta!60!black}

\lstdefinelanguage{json}{
    basicstyle=\normalfont\ttfamily,
    commentstyle=\color{eclipseStrings},
    stringstyle=\color{eclipseKeywords},
    numbers=left,
    numberstyle=\scriptsize,
    stepnumber=1,
    numbersep=8pt,
    showstringspaces=false,
    breaklines=true,
    frame=lines,
    string=[s]{"}{"},
    comment=[l]{:\ "},
    morecomment=[l]{:"},
    literate=
        *{0}{{{\color{numb}0}}}{1}
         {1}{{{\color{numb}1}}}{1}
         {2}{{{\color{numb}2}}}{1}
         {3}{{{\color{numb}3}}}{1}
         {4}{{{\color{numb}4}}}{1}
         {5}{{{\color{numb}5}}}{1}
         {6}{{{\color{numb}6}}}{1}
         {7}{{{\color{numb}7}}}{1}
         {8}{{{\color{numb}8}}}{1}
         {9}{{{\color{numb}9}}}{1}
}

\DeclareRobustCommand{\code}[1]{\nolinkurl{#1}}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\newcolumntype{P}[1]{>{\raggedright\arraybackslash}p{#1}}

\begin{document}
\hypersetup{pageanchor=false}
\selectlanguage{vietnamese}

% =========================================================================
% TRANG BÌA NGOÀI (BÌA CHÍNH - KHUNG ĐÔI TIKZ)
% =========================================================================
\begin{titlepage}
\begin{center}
	\begin{tikzpicture}[overlay,remember picture]
	    \draw [line width=3pt,rounded corners=0pt]
	        ($ (current page.north west) + (20mm,-20mm) $)
	        rectangle
	        ($ (current page.south east) + (-15mm,20mm) $);
	    \draw [line width=1pt,rounded corners=0pt]
	        ($ (current page.north west) + (21.5mm,-21.5mm) $)
	        rectangle
	        ($ (current page.south east) + (-16.5mm,21.5mm) $);
	\end{tikzpicture}
	\\[1mm]
    \centerline{\bf ĐẠI HỌC QUỐC GIA HÀ NỘI}
    \centerline{\bf TRƯỜNG ĐẠI HỌC CÔNG NGHỆ}
    
    \vspace*{1.8cm}
    \large
        \begin{figure}[H]
        \centering
        \includegraphics[width=0.23\linewidth]{figs/uet.jpg}
        \end{figure}
    \vspace*{1cm}
    \centerline{\bf VŨ TIẾN TUẤN TRUNG}
    \vspace*{2.0cm}
    {\fontsize{15}{19}\selectfont\bfseries
    \centerline{BIỂU DIỄN CẤU TRÚC CHO HỆ THỐNG}
    \centerline{PHÁT HIỆN XÂM NHẬP MẠNG CAN BUS}
    \centerline{ĐA PHƯƠNG TIỆN\par}}
    \vspace*{2.2cm}
    \centerline{\bf KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC HỆ CHÍNH QUY}
    \vspace*{0.2cm}
    \centerline{\bf Ngành: Hệ thống thông tin}
    
    \vfill
    \centerline{\bf Hà Nội -- 2026}
    \vspace{13pt}
\end{center}
\end{titlepage}

\newpage

% =========================================================================
% TRANG BÌA PHỤ (BÌA TRONG - CÓ CÁN BỘ HƯỚNG DẪN)
% =========================================================================
\begin{titlepage}
\begin{center}
	\begin{tikzpicture}[overlay,remember picture]
	    \draw [line width=3pt,rounded corners=0pt]
	        ($ (current page.north west) + (20mm,-20mm) $)
	        rectangle
	        ($ (current page.south east) + (-15mm,20mm) $);
	    \draw [line width=1pt,rounded corners=0pt]
	        ($ (current page.north west) + (21.5mm,-21.5mm) $)
	        rectangle
	        ($ (current page.south east) + (-16.5mm,21.5mm) $);
	\end{tikzpicture}
	\\[1mm]
    \centerline{\bf ĐẠI HỌC QUỐC GIA HÀ NỘI}
    \centerline{\bf TRƯỜNG ĐẠI HỌC CÔNG NGHỆ}
    \vspace*{1.8cm}
    \large
        \begin{figure}[H]
        \centering
        \includegraphics[width=0.23\linewidth]{figs/uet.jpg}
        \end{figure}
    \vspace*{0.9cm}
    \large
    \centerline{\bf VŨ TIẾN TUẤN TRUNG}
    \vspace*{1.8cm}
    {\fontsize{15}{19}\selectfont\bfseries
    \centerline{BIỂU DIỄN CẤU TRÚC CHO HỆ THỐNG}
    \centerline{PHÁT HIỆN XÂM NHẬP MẠNG CAN BUS}
    \centerline{ĐA PHƯƠNG TIỆN\par}}
    \vspace*{1.5cm}
    \centerline{\bf KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC HỆ CHÍNH QUY}
    \vspace*{0.2cm}
    \centerline{\bf Ngành: Hệ thống thông tin}
    
    \vspace*{1.4cm}
    \centerline{\bf Cán bộ hướng dẫn:}
    \centerline{\bf PGS. TS. Nguyễn Ngọc Hóa}
    
    \vfill
    \centerline{\bf Hà Nội -- 2026}
    \vspace{13pt}
\end{center}
\end{titlepage}

\newpage
\hypersetup{pageanchor=true}
\pagenumbering{roman}
\pagestyle{plain}

% =========================================================================
% LỜI CẢM ƠN
% =========================================================================
\chap{Lời cảm ơn}
\vspace{20pt}
Em xin chân thành cảm ơn PGS. TS. Nguyễn Ngọc Hóa đã hướng dẫn, góp ý và định hướng nghiên cứu trong quá trình thực hiện khóa luận. Em cảm ơn các tác giả đã công bố dữ liệu và công trình về an ninh mạng CAN, tạo điều kiện cho việc kiểm chứng thực nghiệm.

Các công cụ AI được sử dụng để hỗ trợ soạn thảo, dịch thuật, rà soát tài liệu và phát triển mã nguồn. Tác giả có trách nhiệm kiểm tra nguồn trích dẫn, hiểu và xác nhận mã nguồn, chạy thực nghiệm và chịu trách nhiệm đối với nội dung cuối cùng. Phần kết quả chỉ sử dụng các lượt thực nghiệm đã hoàn tất và kiểm chứng theo giao thức được mô tả; số liệu thăm dò lịch sử được lưu riêng.

\newpage

% =========================================================================
% LỜI CAM ĐOAN
% =========================================================================
\chap{Lời cam đoan}
\vspace{20pt}
Tôi cam đoan ghi rõ nguồn của các ý tưởng, dữ liệu và công trình được sử dụng. Tôi không trình bày kết quả chưa được chạy như kết quả đã thực nghiệm, và không gán số liệu của một cấu hình cho cấu hình khác. Các giới hạn về dữ liệu, phạm vi kiểm chứng và khả năng tái lập được nêu trong nội dung khóa luận. Tôi chịu trách nhiệm kiểm tra và xác nhận bản cuối cùng trước khi nộp.

\begin{flushright}
{\it Tác giả khóa luận}
\hskip 1.5cm\quad

\vskip 2cm
{\bf Vũ Tiến Tuấn Trung}  \quad\ \quad
\end{flushright}

\newpage

% =========================================================================
% TÓM TẮT KHÓA LUẬN (VINAMESE)
% =========================================================================
\chap{Tóm tắt}
\vspace{15pt}

Phát hiện xâm nhập trên mạng CAN (\textit{Controller Area Network}) khi chuyển giao sang các dòng xe chưa từng quan sát là một thách thức lớn do mã định danh CAN-ID mang tính đặc thù riêng của từng nhà sản xuất. Khóa luận này đề xuất và đánh giá thực nghiệm quy trình biểu diễn cấu trúc (\textit{Structural Representation}) 30 chiều hướng tới mục tiêu chuyển giao xuyên phương tiện: cho phép mô hình phát hiện xâm nhập được huấn luyện một lần duy nhất tại phòng thí nghiệm trên dữ liệu xe nguồn nhưng có khả năng chuyển giao và bảo vệ được nhiều dòng xe khác nhau mà không đòi hỏi phải thu thập dữ liệu tấn công có nhãn để huấn luyện lại từ đầu. Biểu diễn đề xuất loại bỏ hoàn toàn các bit CAN-ID thô khỏi đầu vào của bộ phân loại, thay thế bằng các đặc trưng nội tại của luồng truyền thông bao gồm: tần suất xuất hiện và thứ tự khung tin trong cửa sổ, xác suất chuyển tiếp giữa các thông điệp, và vi sai biến thiên dữ liệu tải ($\Delta$payload) cùng ID.

Trên bộ đối chuẩn \textit{can-train-and-test} gồm 4 tập dữ liệu qua 3 hạt giống ngẫu nhiên, kết quả thực nghiệm chỉ ra rằng tại các ngưỡng tĩnh đóng băng từ dữ liệu nguồn, biểu diễn cấu trúc chưa tự động gia tăng độ nhạy (Recall điều kiện B đạt 73,83\% so với 85,41\% của mô hình Raw) và tỷ lệ báo động giả còn cao ($\text{FAR} = 52{,}46\%$). Tuy nhiên, xét về chất lượng xếp hạng độc lập ngưỡng, biểu diễn cấu trúc thể hiện ưu thế vượt trội khi nâng độ chính xác trung bình (Average Precision -- AP) từ 0,3781 lên 0,5554 (+17,74 điểm phần trăm chênh lệch ghép cặp; +17,73 điểm phần trăm chênh lệch trung bình so với Raw). Phân tích chẩn đoán bằng Linear Probe giải thích nguyên nhân: các đặc trưng hình thái khung tin (như độ dài DLC) vừa mang thông tin nhận diện hãng xe (probe đạt 94,88\%), vừa là tín hiệu cốt lõi để phát hiện tấn công (hiện tượng đan xen đặc trưng).

Để khắc phục hiện tượng trôi dạt ngưỡng giữa các dòng xe mà không cần huấn luyện lại mô hình, khóa luận tích hợp cơ chế hiệu chuẩn nền lành tính không giám sát (\textit{Benign Warmup Calibration}) trong giai đoạn khởi động ngắn ($K = 500$ cửa sổ, tương đương khoảng 16 giây khi nổ máy). Cơ chế này giúp khôi phục hoàn toàn ưu thế vận hành thực tế: nâng Recall điều kiện B lên 40,42\%--48,59\% trong khi kiểm soát tỷ lệ báo động giả thực nghiệm dưới ngưỡng mục tiêu ($\text{FAR} \le 1{,}08\%$), đồng thời loại bỏ điểm suy biến báo động giả trên dữ liệu ngoại bộ CICIoV2024 và Opel Astra.

Nghiên cứu mang lại đóng góp quan trọng trong việc phân tách rõ ràng giữa năng lực biểu diễn và điểm vận hành ngưỡng quyết định, cung cấp cơ sở thực nghiệm vững chắc và có khả năng tái lập cao cho việc phát triển các hệ thống phát hiện xâm nhập CAN bus chuyển giao đa phương tiện trong thực tế.

\vspace{1em}
\noindent \textit{\textbf{Từ khóa:}} Mạng CAN, phát hiện xâm nhập, chuyển giao đa phương tiện, biểu diễn cấu trúc, hiệu chuẩn nền lành tính, an toàn ô tô.

\newpage

% =========================================================================
% TÓM TẮT KHÓA LUẬN (ENGLISH ABSTRACT)
% =========================================================================
\chap{Abstract}
\vspace{15pt}

Cross-vehicle intrusion detection on Controller Area Network (CAN) buses poses a fundamental challenge because message identifiers (CAN-IDs) are manufacturer-proprietary, causing models trained on one vehicle to degrade significantly on unseen platforms. This thesis investigates a 30-dimensional Structural Representation pipeline designed for cross-vehicle intrusion detection, aiming to enable a model trained once in the laboratory to protect diverse vehicle platforms without requiring labeled attack data for retraining on each target vehicle. By excluding raw identifier bits from classifier inputs, the proposed representation captures intrinsic traffic regularities, including intra-window message frequencies, arrival order, sequential transitions, and same-ID payload differences ($\Delta$payload).

Evaluated across four cross-vehicle benchmark sets over three random seeds, empirical results show that under static decision thresholds frozen from source data, structural representations do not automatically boost detection sensitivity (Condition B recall reaches 73.83\% versus 85.41\% for Raw baselines) while target false alarm rates remain elevated ($\text{FAR} = 52.46\%$). However, in threshold-independent ranking, structural features demonstrate clear superiority, increasing Average Precision (AP) from 0.3781 to 0.5554 (+17.74 percentage points paired difference; +17.73 percentage points difference of means over Raw). Phased diagnostic probing reveals that message syntax features inherently retain manufacturer identity (vehicle probe accuracy of 94.88\%) due to feature entanglement between vehicle topology and attack signatures.

To resolve inter-vehicle threshold shift without model retraining, the thesis incorporates an unsupervised benign warmup calibration during initial vehicle ignition ($K = 500$ windows, $\approx 16$ seconds). This lightweight calibration successfully restores operational viability, boosting Condition B recall to 40.42\%--48.59\% while strictly constraining empirical target FAR below 1.08\%, eliminating false-alarm collapse on CICIoV2024, and suppressing Opel Astra DoS false alarms from 31.5\% to 0.17\%.

These findings provide crucial empirical evidence delineating feature ranking quality from operational threshold selection, establishing a reproducible foundation for deployable cross-vehicle automotive intrusion detection systems.

\vspace{1em}
\noindent \textit{\textbf{Keywords:}} CAN bus, intrusion detection, cross-vehicle transfer, structural representation, benign warmup calibration, automotive cybersecurity.

\newpage

% =========================================================================
% DANH MỤC (TOC, LOF, LOT, ABBREVIATIONS)
% =========================================================================
\begingroup
\small
\renewcommand{\baselinestretch}{0.95}\selectfont
\setlength{\parskip}{0pt}
\makeatletter
\renewcommand*\l@chapter[2]{%
  \ifnum \c@tocdepth >\m@ne
    \addpenalty{-\@highpenalty}%
    \vskip 0.25em \@plus\p@
    \setlength\@tempdima{1.5em}%
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      \leavevmode \bfseries
      \advance\leftskip\@tempdima
      \hskip -\leftskip
      #1\nobreak\hfil \nobreak\hb@xt@\@pnumwidth{\hss #2}\par
      \penalty\@highpenalty
    \endgroup
  \fi}
\makeatother
\tableofcontents
\endgroup
\clearpage

\begingroup
\small
\setlength{\parskip}{0pt}
\let\clearpage\relax
\let\cleardoublepage\relax
\phantomsection
\addcontentsline{toc}{chapter}{Danh sách hình vẽ}
\listoffigures
\vspace{0.8cm}
\phantomsection
\addcontentsline{toc}{chapter}{Danh sách bảng}
\listoftables
\endgroup
\clearpage

\chap{Danh mục từ viết tắt}
\vspace{10pt}
{\small\setlength{\tabcolsep}{4pt}
\noindent\begin{tabularx}{\textwidth}{@{}lXlX@{}}
\toprule
\textbf{Ký hiệu} & \textbf{Ý nghĩa} & \textbf{Ký hiệu} & \textbf{Ý nghĩa} \\ \midrule
AP & Average Precision & IDS & Intrusion Detection System \\
CAN & Controller Area Network & INLP & Iterative Nullspace Projection \\
CI & Khoảng tin cậy (Confidence Interval) & LEACE & Least-Squares Concept Erasure \\
CTT & can-train-and-test dataset & LOVO & Leave-One-Vehicle-Out \\
DANN & Domain-Adversarial Neural Network & LR & Logistic Regression \\
DBC & Cơ sở dữ liệu mô tả CAN (Database CAN) & MLM & Masked Language Modeling \\
DLC & Data Length Code & PCA & Principal Component Analysis \\
DNN & Deep Neural Network & PR & Precision--Recall \\
DoS & Denial of Service & TF & Transformer \\
ECU & Electronic Control Unit & TF-IDF & Term Frequency--Inv. Doc. Freq. \\
FAR & False Alarm Rate (/100k hay \%) & TN/TP & True Negative / True Positive \\
FN/FP & False Negative / False Positive & UET & Trường ĐH Công nghệ, ĐHQGHN \\
FPR & False Positive Rate & VNU & Đại học Quốc gia Hà Nội \\
GRL & Gradient Reversal Layer & & \\
\bottomrule
\end{tabularx}}
\addtocounter{table}{-1}

\newpage
\pagenumbering{arabic}
\pagestyle{fancy}



\chap{Mở đầu}\label{chap:introduction}
\sect{Động cơ nghiên cứu}
Mạng CAN kết nối các bộ điều khiển điện tử trong phương tiện. Thiết kế giao thức ưu tiên truyền thông và phân xử truy cập bus, không cung cấp sẵn xác thực mật mã cho từng nguồn phát. Các thực nghiệm an ninh ô tô đã chỉ ra rằng khi có quyền truy cập phù hợp, kẻ tấn công có thể tác động tới thông điệp và chức năng điều khiển~\cite{koscher2010experimental,checkoway2011comprehensive}. Một IDS thụ động có thể giám sát lưu lượng mà không yêu cầu thay đổi mọi ECU, nhưng chất lượng phát hiện cần được đo trong các điều kiện triển khai có ý nghĩa.

Hiệu năng của IDS có thể thay đổi đáng kể giữa các bộ dữ liệu và điều kiện đánh giá~\cite{koltai2026trust}. Một mô hình học từ xe nguồn có thể khai thác tương quan giữa nhãn tấn công với CAN-ID, payload hoặc chu kỳ truyền của riêng xe đó; các tương quan này có thể đổi khi chuyển xe. Tuy nhiên, hiệu năng suy giảm không tự động chứng minh mô hình học thuộc ID: ngưỡng phân loại, cách lấy mẫu, chính sách nhãn và cơ chế tấn công cũng có thể góp phần. Nghiên cứu vì vậy tách phép đo hiệu năng khỏi giả thuyết giải thích nguyên nhân.

Khóa luận chọn can-train-and-test làm đối chuẩn chính vì bộ dữ liệu đã tổ chức bốn điều kiện xe quen/lạ và tấn công quen/lạ~\cite{lampe2024curated}; trong đó điều kiện B (xe lạ, tấn công quen) và D (xe lạ, tấn công lạ) là trọng tâm khảo sát chuyển giao đa xe. Các nghiên cứu gần đây cũng đã đề xuất sử dụng quan hệ chuyển tiếp ID, lịch sử thông điệp hoặc đánh giá xuyên bộ dữ liệu~\cite{khreasat2026relational,dong2026mtff,koltai2026trust,obafemi2026travel}. Tuy nhiên, khoảng trống tri thức hiện hữu nằm ở hai bất cập phương pháp luận: (1) Nhiều công trình báo cáo khả năng chuyển giao tốt khi bỏ CAN-ID nhưng lại kết hợp đồng thời với bước hiệu chuẩn thống kê trên dữ liệu lành của xe đích hoặc không cố định ngưỡng phân loại, khiến chưa thể tách bạch được đóng góp thực chất của bản thân biểu diễn đặc trưng khỏi các tham số hiệu chỉnh thích ứng; (2) Có sự đánh đồng ngầm định giữa \textit{tính bất biến đổi tên định danh} (ID-renaming invariance) với \textit{tính độc lập miền xe thực tế} (vehicle-domain invariance), trong khi sự thay đổi xe thực tế còn kéo theo biến thiên payload và quy luật phân phối cục bộ. Do đó, nghiên cứu này tiếp cận bài toán theo quy trình hai giai đoạn rõ ràng: trước hết cô lập tác động của việc bỏ giá trị ID thô kết hợp bổ sung lịch sử payload cùng ID và quan hệ cục bộ dưới kịch bản zero-shot nghiêm ngặt (cùng dữ liệu nguồn, cùng mẫu cửa sổ, cùng kiến trúc bộ mã hóa và ngưỡng đóng băng từ nguồn) để bóc tách bản chất biểu diễn; sau đó mới tích hợp cơ chế hiệu chuẩn thích ứng có kiểm soát trên nền lành tính ban đầu nhằm giải quyết bài toán vận hành thực tế.

\sect{Vấn đề và phạm vi}
Với luồng CAN được ghi theo thứ tự, hệ thống đưa ra một quyết định nhị phân bình thường/tấn công sau mỗi cửa sổ hoàn chỉnh gồm 64 khung tin không chồng lặp. Các cửa sổ không nối qua biên file. Nhãn cửa sổ dương tính khi chứa ít nhất một khung tin được bộ dữ liệu gán nhãn 1; ý nghĩa nhãn 1 phụ thuộc chính sách gán nhãn, chẳng hạn có thể đánh dấu khoảng suspension mà không có khung tin độc hại được chèn~\cite{rajapaksha2024canmirgu}. Nghiên cứu không khẳng định nhận diện được ECU bị xâm nhập hoặc ý nghĩa vật lý của từng tín hiệu. Việc phát hiện trước thời điểm gây hại cần phép đo độ trễ theo sự kiện riêng, không suy từ F1 cửa sổ.

Mô hình, các tham số chuẩn hóa cần học và ngưỡng quyết định chỉ được huấn luyện hoặc chọn bằng dữ liệu nguồn; khi đánh giá xe đích, chúng được giữ cố định. Bộ trích xuất có thể dùng các khung tin quá khứ của chính bản ghi đích để tính đặc trưng, nhưng không dùng nhãn đích và không cập nhật mô hình hoặc ngưỡng. Đây là phạm vi chuyển giao không hiệu chỉnh theo xe đích được khảo sát trong khóa luận.

Trong phạm vi triển khai hiện tại, dữ liệu là CAN cổ điển với ID chuẩn 11 bit và tối đa 8 byte payload. Khung CAN-FD, ID mở rộng hoặc nhãn chưa xác định sẽ bị từ chối. Qua kiểm toán toàn diện 236 tệp của bộ dữ liệu \texttt{can-train-and-test} (193.240.845 khung tin), nghiên cứu phát hiện 12.527 lần timestamp đi lùi ($\Delta t < 0$) phân bố trên 100 tệp; phân tích định lượng biên độ cho thấy 12.507/12.527 trường hợp (99,84\%) nhỏ hơn hoặc bằng 1~ms (trung vị $25{,}03\,\mu\text{s}$, phân vị p95 đạt $92{,}27\,\mu\text{s}$), 20 trường hợp nằm trong khoảng $(1\text{ ms};\, 7{,}895\text{ ms}]$ và hoàn toàn không có bước nhảy lùi nào vượt quá 1~giây ($0/12.527$). Điều này chứng minh các điểm đi lùi là nhiễu đồng hồ/bộ đệm ở mức dưới mili-giây khi ghi nhận chứ không phải hiện tượng xáo trộn khối bản ghi quy mô lớn. Tuy vậy, để không phụ thuộc giả định chronology vật lý, phép so sánh chính tuân thủ nhánh \textit{content-only} theo thứ tự tệp (loại chiều $\Delta t$) và kiểm chứng độ nhạy riêng giữa 136 tệp đơn điệu nghiêm ngặt với 100 tệp có đi lùi ở Chương~\ref{chap:results}. Bộ phân loại không nhận trực tiếp giá trị ID toàn cục trong nhánh cấu trúc; bộ trích xuất vẫn dùng ID làm khóa để tìm khung tin trước cùng ID. 

Khóa luận tập trung vào biểu diễn cấu trúc (\textit{Structural Representation}) không phụ thuộc CAN-ID thô nhằm kiểm chứng giả thuyết: liệu việc loại bỏ định danh và khai thác quy luật cấu trúc có thể tạo ra khả năng chuyển giao đa phương tiện hiệu quả hay không. Lưu ý về thuật ngữ: Cụm từ ``đa phương tiện'' trong tên đề tài được hiểu chính xác theo ngữ cảnh an toàn ô tô là chuyển giao xuyên phương tiện (\textit{cross-vehicle transfer} giữa nhiều dòng xe khác nhau), hoàn toàn không mang hàm nghĩa truyền thông đa phương tiện (\textit{multimedia}). Nghiên cứu sử dụng các phép đo thăm dò tuyến tính (\textit{Linear Probes}) nhằm định lượng chính xác mức độ tồn lưu thông tin nhận diện xe trong không gian đặc trưng ẩn, qua đó xác lập ranh giới định lượng giữa tính bất biến đổi tên định danh (\textit{ID-renaming invariance}) và tính độc lập miền xe thực tế (\textit{vehicle-domain invariance}).

\sect{Mục tiêu và định hướng nghiên cứu}
Xuất phát từ bài toán thực tế trong an ninh mạng ô tô, \textbf{mục tiêu tổng thể của khóa luận là thiết lập một quy trình (pipeline) biểu diễn đặc trưng độc lập với CAN-ID thô, cho phép mô hình phát hiện xâm nhập được huấn luyện một lần duy nhất tại phòng thí nghiệm trên dữ liệu xe nguồn nhưng có khả năng chuyển giao và bảo vệ được nhiều dòng xe khác nhau mà không đòi hỏi phải thu thập dữ liệu tấn công có nhãn để huấn luyện lại từ đầu}.

Để hiện thực hóa mục tiêu này một cách khoa học và chặt chẽ, nghiên cứu tiếp cận theo lộ trình hai giai đoạn phương pháp luận:
\begin{enumerate}
    \item \textit{Giai đoạn kiểm định zero-shot nghiêm ngặt:} Kiểm chứng giả thuyết khoa học: \textit{Liệu việc loại bỏ CAN-ID thô và thay thế bằng các đặc trưng cấu trúc (biến thiên payload cùng ID, thống kê mật độ cục bộ, chuyển tiếp thông điệp) dưới ngưỡng đóng băng hoàn toàn từ nguồn có thực sự giúp mô hình đạt được tính độc lập đặc thù xe và nâng cao hiệu năng phát hiện tấn công hay không?} Giai đoạn này nhằm đo lường độc lập năng lực biểu diễn và phân định ranh giới giữa tính bất biến đổi tên định danh với tính độc lập miền xe thực tế.
    \item \textit{Giai đoạn thích ứng vận hành thực tế:} Khi thực nghiệm giai đoạn 1 bộc lộ hiện tượng trôi dạt phân phối logit nền khiến ngưỡng tĩnh từ nguồn bị lệch, nghiên cứu đề xuất và đánh giá cơ chế hiệu chuẩn nền lành tính ngắn ($K=500$ cửa sổ, tương đương khoảng $16\text{--}32$ giây khi nổ máy xe) kết hợp lọc sự kiện trượt nhằm khôi phục điểm vận hành tối ưu trên xe đích mà không cần huấn luyện lại bất kỳ trọng số mô hình nào.
\end{enumerate}

Để làm sáng tỏ các mục tiêu trên một cách khách quan và có hệ thống, nghiên cứu định hướng trả lời bốn câu hỏi nghiên cứu (Research Questions --- RQ) chính:
\begin{enumerate}[label=\textbf{RQ\arabic*:}]
    \item \textbf{Đánh giá khả năng chuyển giao đa xe dưới ngưỡng đóng băng từ nguồn:} So sánh trực diện biểu diễn đặc trưng thô (Raw) và biểu diễn cấu trúc (Structural) về độ nhạy (Recall) và tỷ lệ báo động giả (FAR) trên cả bốn điều kiện chuyển giao (từ điều kiện A đến D, đặc biệt là điều kiện B trên xe lạ với tấn công quen), dưới cùng một ngân sách báo động giả nghiêm ngặt được hiệu chuẩn từ dữ liệu nguồn.
    \item \textbf{Bóc tách vai trò các thành phần và độ nhạy kích thước cửa sổ:} Phân tích các đánh đổi thực nghiệm khi loại bỏ bit CAN-ID thô, bổ sung biến thiên payload $\Delta$ cùng ID, thống kê cục bộ và chuyển tiếp thông điệp; đồng thời kiểm chứng tính ổn định của kết quả khi thay đổi kích thước cửa sổ phân tích ($W \in \{32, 64, 128\}$).
    \item \textbf{Định lượng mức độ tồn lưu thông tin xe và phân tách tấn công:} Sử dụng các phép đo thăm dò tuyến tính có đối chứng (\textit{controlled linear probes}) trên biểu diễn ẩn của bộ mã hóa đã đóng băng nhằm đo lường độc lập mức độ rò rỉ danh tính xe và khả năng phân tách tín hiệu tấn công.
    \item \textbf{Kiểm định độ bền vững trên dữ liệu ngoại bộ:} Đánh giá khả năng tổng quát hóa của các mô hình nguồn đóng băng trên các bộ dữ liệu ngoại bộ độc lập, phân tích các nguyên nhân gốc rễ dẫn đến thành công hoặc thất bại trong kịch bản triển khai thực tế.
\end{enumerate}

Tiêu chí kiểm định chính của nghiên cứu là xem xét mức tăng recall trung bình ở điều kiện B của biểu diễn Structural so với Raw tại ngưỡng chọn từ validation nguồn với ngân sách FAR $100/100.000$ cửa sổ lành. Mọi so sánh recall luôn được diễn giải song hành cùng FAR trên xe đích; các chỉ số AP và F1 đóng vai trò là thước đo bổ sung để đánh giá chất lượng xếp hạng độc lập ngưỡng. Bên cạnh đó, nghiên cứu thực hiện thêm phân tích hậu nghiệm với kỹ thuật trộn thống kê đặc trưng MixStyle~\cite{zhou2021mixstyle} nhằm kiểm tra xem liệu việc điều chuẩn phân phối ẩn trong quá trình huấn luyện nguồn đơn có giúp hạn chế rò rỉ danh tính xe hay không.

\sect{Đóng góp và phạm vi giới hạn}
Khóa luận mang lại ba đóng góp thực nghiệm và phương pháp luận chính:
\begin{enumerate}
\item \textbf{Đặc tả biểu diễn cấu trúc 30 chiều và phân định lý thuyết về tính bất biến:} Thiết kế và kiểm chứng biểu diễn nội dung cấp khung tin không cung cấp bit CAN-ID thô cho bộ phân loại nhưng duy trì ID làm khóa truy xuất biến thiên payload ($\Delta$payload) và thống kê chuyển tiếp cục bộ. Khóa luận chứng minh cả về mặt hình thức lẫn thực nghiệm rằng \textit{tính bất biến dưới phép đổi tên ID nhất quán (ID-renaming invariance)} là một tính chất hẹp hơn và không tự động kéo theo \textit{tính độc lập đặc thù xe (vehicle-domain invariance)}.
\item \textbf{Thiết lập giao thức đối chứng nghiêm ngặt và mở rộng chuyển giao đa xe:} Khóa luận thiết lập ma trận chính 60 đơn vị IDS (4 tập $\times$ 3 seed $\times$ 5 phương pháp) dưới ngưỡng đóng băng từ nguồn ($\text{FAR} \le 100/100.000$), kết hợp với 144 lượt ablation nội dung, 12 lượt MixStyle, lưới hiệu chuẩn nền lành tính ($K \in \{200, 500, 1000\}$), 48 lượt huấn luyện đa nguồn LOVO với đối kháng có điều kiện DANN, 96 pipeline làm trắng nền lành tính kết hợp triệt tiêu khái niệm tuyến tính (LEACE/INLP8), cùng 120 lượt thực nghiệm kiểm chứng mở rộng (48 lượt đối chứng Timed/Content trên 136 tệp đơn điệu, 48 lượt cửa sổ đẳng lượng khung tin W32/W128, 24 lượt phương sai lấy mẫu reservoir đa seed).
\item \textbf{Định lượng sự phân kỳ giữa chất lượng xếp hạng, xóa thông tin xe và điểm vận hành:} Khóa luận chứng minh trên 57 bản ghi ngoại bộ và các nghiên cứu hậu nghiệm rằng dù biểu diễn Structural nâng AP điều kiện B từ 0,3781 lên 0,5554 (trung bình 3 xe đích khử lặp: 0,5510 so với 0,4281), thông tin xe vẫn giải mã được ở mức 94,88\% (linear probe); học đa nguồn có đối kháng chỉ giảm FAR còn 31,97\%, trong khi làm trắng nền lành xe đích kết hợp LEACE/INLP8 đưa linear vehicle probe của điểm rủi ro về mức sát ngẫu nhiên (27,30\%--28,90\% so với 25\%) và điểm năng lượng làm trắng đạt AP 0,6172 (recall 46,06\%, FAR 0,30\%), đồng thời bộc lộ rõ đánh đổi với thông tin phi tuyến còn sót lại (probe MLP 1.500 vòng còn 42,01\%--57,17\%).
\end{enumerate}

\noindent\textbf{Phạm vi và giới hạn:} Khóa luận tập trung vào đánh giá thực nghiệm có khả năng tái lập (lưu trữ đầy đủ manifest, mã băm dữ liệu, checkpoint và dự đoán từng cửa sổ) thay vì tuyên bố một hệ thống IDS phổ quát sẵn sàng triển khai. Các phép đo thời gian xử lý trên CPU/GPU máy trạm phản ánh chi phí tính toán từng cửa sổ trong môi trường thí nghiệm, không thay thế cho kiểm định độ trễ thời gian thực và deadline trên vi điều khiển ECU nhúng.

\sect{Tổ chức khóa luận}
Chương~\ref{chap:background} trình bày cơ sở lý thuyết về mạng CAN, các cơ chế tấn công trên bus, bài toán dịch chuyển phân phối đa phương tiện và nền tảng học biểu diễn chuỗi; Chương~\ref{chap:related} khảo sát và đối chiếu các công trình liên quan nhằm định vị khoảng trống nghiên cứu; Chương~\ref{chap:method} phát biểu hình thức bài toán, mô hình đe dọa, khung biểu diễn cấu trúc 30 chiều và các cơ chế thích ứng miền; Chương~\ref{chap:results} thiết lập giao thức thực nghiệm, trình bày kết quả đánh giá trên đối chuẩn và dữ liệu ngoại bộ cùng phân tích chi phí xử lý và đe dọa tính hợp lệ; \hyperref[chap:conclusion]{Phần Kết luận và hướng phát triển} tổng kết các phát hiện chính, giới hạn và định hướng nghiên cứu tiếp theo. Phụ lục~\ref{app:reproducibility} cung cấp chi tiết tái lập và phân biệt thiết kế lịch sử với bằng chứng hiện hành.

\chapter{Cơ sở lý thuyết}\label{chap:background}
Chương này thiết lập các nền tảng lý thuyết cốt lõi cho bài toán phát hiện xâm nhập mạng nội xe đa phương tiện, bao gồm cơ chế giao thức CAN và kiến trúc quan sát thụ động của IDS, các hình thái tấn công phổ biến trên bus, bản chất chuyển dịch phân phối giữa các dòng xe cùng vai trò của các bộ dữ liệu đối chuẩn, và nền tảng học biểu diễn chuỗi nhằm xử lý dịch chuyển miền.

\section{Giao thức mạng CAN và kiến trúc quan sát của IDS thụ động}
CAN sử dụng mã định danh để phân xử truy cập đường truyền và biểu thị loại thông điệp. ID không phải địa chỉ nguồn xác thực. IDS trong nghiên cứu quan sát bản ghi khung tin sau khi truyền, không quan sát trực tiếp mọi trạng thái vật lý của ECU. Chênh lệch thời gian trong log còn phụ thuộc phần cứng thu, độ phân giải timestamp và tải bus. Vì vậy không được diễn giải mọi thay đổi nhịp là hành vi tấn công~\cite{bozdal2020evaluation,verma2024road}.

Ký hiệu khung tin thứ $i$ là
\begin{equation}
F_i=(t_i,c_i,d_i,\mathbf{b}_i,y_i),\quad d_i\in\{0,\ldots,8\},\quad y_i\in\{0,1\},
\end{equation}
trong đó $t_i$ là timestamp, $c_i$ là ID, $d_i$ là số byte hữu hiệu, $\mathbf{b}_i$ là payload đã đệm và $y_i$ là nhãn nhị phân sau khi kiểm tra chính sách gán nhãn của bộ dữ liệu. Timestamp do công cụ ghi nhận, không phải một trường payload được xác thực. Byte đệm mang giá trị 0 nhưng mặt nạ phân biệt byte không tồn tại với byte thực bằng 0.

\section{Các cơ chế tấn công trên mạng nội xe}
Kẻ tấn công được giả định có khả năng phát, thay đổi hoặc làm gián đoạn lưu lượng trong phạm vi các kịch bản đã ghi trong bộ dữ liệu. Các cơ chế quan tâm gồm flooding/DoS, fuzzing, injection/spoofing, thay đổi payload và suspension. IDS chỉ đọc dữ liệu; nó không ngăn chặn frame và không thay thế cơ chế xác thực hoặc điều khiển an toàn. Tấn công sửa đồng thời nhãn chuẩn và log của hệ thống thu nằm ngoài phạm vi, bởi khi đó ground truth không còn đáng tin.

Đối với dữ liệu mô phỏng hoặc sửa bản ghi, nghiên cứu chỉ kết luận về dấu vết đã tạo trên luồng bus, không khẳng định tác động vật lý ngoài đời. Với Automotive v2, tấn công DoS là đoạn dữ liệu bị thay thế trong bản sao trace bình thường. Với CAN-MIRGU, nhãn từng khung tin được trích xuất từ cột nhãn tường minh ở cuối dòng thay vì giả định toàn bộ các khung tin trong tệp chứa từ khóa ``attack'' đều là tấn công.

\section{Bài toán dịch chuyển phân phối đa phương tiện và các bộ dữ liệu đối chuẩn}
\subsection{Các điều kiện dịch chuyển xe và tấn công}
Bốn điều kiện là các tập con đối chuẩn được thiết kế để khảo sát hai loại chuyển dịch (được tổng hợp chi tiết tại Bảng~\ref{tab:conditions}). Chúng không tạo một thí nghiệm nhân quả chỉ thay đúng một yếu tố: phiên ghi, trạng thái vận hành, tỷ lệ lớp và hiện thực tấn công có thể đồng thời thay đổi. Các chênh lệch A--B hoặc C--D vì vậy được diễn giải trong phạm vi bộ dữ liệu.
Gọi $v_s,v_t$ là miền xe nguồn và đích; $a_s,a_t$ là tập kiểu tấn công xuất hiện trong train và test. Điều kiện A/B/C/D giữ hoặc thay đổi hai yếu tố này. ``Quen'' phải được kiểm tra trên dữ liệu thực sự đi vào huấn luyện: một attack family có tên trong thư mục nhưng bị bỏ hết bởi sampling chưa thể coi là đã được học.

\begin{table}[htbp]\centering
\caption{Bốn điều kiện kiểm thử được kế thừa từ đối chuẩn}\label{tab:conditions}
\begin{tabular}{clll}\toprule Điều kiện & Xe & Tấn công & Vai trò\\\midrule
A & Quen & Quen & Đối chứng trong miền\\
B & Lạ & Quen & Chuyển dịch xe\\
C & Quen & Lạ & Chuyển dịch tấn công\\
D & Lạ & Lạ & Chuyển dịch đồng thời\\\bottomrule\end{tabular}
\end{table}

Ngoại suy sang dataset khác còn thay đổi công cụ thu, định dạng nhãn và môi trường. Nó không phải phép thay đổi riêng xe. Các dataset hoặc trace chia sẻ nguồn ghi cũng không phải các quan sát độc lập chỉ vì có tên file khác. Các cặp phương tiện nguồn và đích tương ứng trong bốn set thực nghiệm được quy định cụ thể tại Bảng~\ref{tab:vehicle_pairs}.

\begin{table}[htbp]\centering
\caption{Ánh xạ xe nguồn và xe đích của bốn set}\label{tab:vehicle_pairs}
\begin{tabular}{lll}\toprule Set & Xe nguồn & Xe đích\\\midrule
1 & Chevrolet Impala & Chevrolet Silverado\\
2 & Chevrolet Traverse & Subaru Forester\\
3 & Chevrolet Silverado & Subaru Forester\\
4 & Subaru Forester & Chevrolet Traverse\\\bottomrule\end{tabular}
\end{table}

Bốn set chỉ sử dụng bốn xe vật lý và chỉ có ba xe đích phân biệt (Silverado, Forester, Traverse); trong đó \textit{Subaru Forester} đóng vai trò xe đích ở cả Set 2 và Set 3, đồng thời Chevrolet Silverado xuất hiện ở vai trò đích trong Set 1 nhưng là xe nguồn ở Set 3. Do đó, nếu chỉ lấy trung bình cộng đồng đều bốn set (trọng số $1/4$ mỗi set), Subaru Forester chiếm tới $50\%$ trọng số đánh giá chuyển xe. Để kiểm soát thiên lệch lặp xe đích này, Chương~\ref{chap:results} báo cáo song song trung bình 4 set chuẩn đối chuẩn và \textit{trung bình 3 xe đích phân biệt khử lặp} với trọng số bằng nhau theo xe đích: $w_{\text{Set 1}}=1/3$ (Silverado), $w_{\text{Set 2}}=w_{\text{Set 3}}=1/6$ (mỗi lần Forester lấy nửa trọng số) và $w_{\text{Set 4}}=1/3$ (Traverse).

\subsection{Nguồn dữ liệu đối chuẩn và ngoại bộ}
Khóa luận khảo sát và phân loại các bộ dữ liệu được sử dụng cùng vai trò và điều kiện kiểm thử hợp lệ được tổng hợp tại Bảng~\ref{tab:datasets}.
\begin{longtable}{P{3.3cm}P{4.4cm}P{5.2cm}}
\caption{Vai trò và điều kiện hợp lệ của dữ liệu}\label{tab:datasets}\\\toprule
Dataset & Vai trò & Điều kiện\\\midrule\endfirsthead
\caption[]{(tiếp theo)}\\\toprule Dataset & Vai trò & Điều kiện\\\midrule\endhead
can-train-and-test~\cite{lampe2024curated} & Đối chuẩn chính, bốn set & Tách source-validation; không thay test chính thức\\
Automotive v2~\cite{dupont2019automotive} & DoS và benign trên Opel/Renault & Nhãn theo interval và chữ ký frame; không gán cả file\\
CAN-MIRGU~\cite{rajapaksha2024canmirgu} & Ngoại suy timestamped & Yêu cầu nhãn từng frame; log tấn công nằm trong thư mục con; cần preflight toàn file\\
CICIoV2024~\cite{neto2024ciciov2024} & Ngoại suy không dùng timing & CSV hexadecimal không cung cấp timestamp đo; giữ giới hạn row-order\\
OTIDS~\cite{lee2017otids} & Chưa đưa vào kết luận xác nhận & Cần xác minh nhãn bản chuyển đổi; loại các file shuffled\\\bottomrule
\end{longtable}
Cần phân biệt rõ bộ dữ liệu HCRL OTIDS (thu thập trên dòng xe Kia Soul theo mô tả phát hành chính thức) với Car-Hacking Dataset. Đối với CAN-MIRGU, nghiên cứu tuân thủ chặt chẽ các thông số kỹ thuật được tài liệu gốc công bố và không tự ý suy đoán các thông tin định danh chưa được kiểm chứng.

\section{Nền tảng học biểu diễn chuỗi và dịch chuyển phân phối trong phát hiện xâm nhập}
Để mô hình hóa chuỗi thông điệp nội xe theo thứ tự truyền tin mà không phụ thuộc giả định tuyến tính hay độ dài cửa sổ cố định của các mạng hồi quy truyền thống, kiến trúc Transformer~\cite{vaswani2017attention} sử dụng cơ chế tự chú ý đa đầu (multi-head self-attention) kết hợp mã hóa vị trí nhằm ánh xạ trực tiếp chuỗi $W$ vector đặc trưng cấp khung tin thành biểu diễn ngữ cảnh thống nhất. Khi triển khai từ xe nguồn $v_s$ sang xe đích $v_t$, bài toán phát hiện xâm nhập đối mặt đồng thời với dịch chuyển hiệp phương sai ở phân phối đầu vào ($P_s(X) \neq P_t(X)$), dịch chuyển có điều kiện giữa đặc trưng và nhãn ($P_s(Y\mid X) \neq P_t(Y\mid X)$), và sự trôi dạt phân phối điểm số đầu ra làm sai lệch ngưỡng quyết định nguồn.

Trong học máy thích ứng miền, các hướng tiếp cận nhằm đối phó với dịch chuyển phân phối có thể phân thành ba nhóm nền tảng: (1) học biểu diễn bất biến qua đối kháng miền DANN~\cite{ganin2016dann} dùng tầng đảo ngược gradient (mặc dù Zhao và cộng sự~\cite{zhao2019invariant} chứng minh tính bất biến phân phối biên và lỗi nguồn thấp chưa tự động bảo đảm hiệu năng khi tồn tại dịch chuyển có điều kiện); (2) điều chuẩn thống kê đặc trưng trong pha huấn luyện như MixStyle~\cite{zhou2021mixstyle} bằng phép trộn kỳ vọng và độ lệch chuẩn theo từng lô; và (3) triệt tiêu khái niệm tuyến tính hậu nghiệm trên không gian ẩn như chiếu không gian hạch lặp INLP~\cite{ravfogel2020null} hoặc biến đổi affine dạng đóng LEACE~\cite{belrose2023leace} để cô lập mức độ rò rỉ thuộc tính miền.

\section{Tóm tắt chương}
Chương này đã hệ thống hóa cấu trúc khung tin CAN, các hình thái tấn công nội xe, bốn điều kiện chuyển giao A--D cùng vai trò các bộ dữ liệu đối chuẩn và cơ sở lý thuyết học biểu diễn dưới dịch chuyển miền. Trên nền tảng đó, Chương~\ref{chap:related} tiếp tục khảo sát, phân loại và đối chiếu các công trình nghiên cứu liên quan nhằm xác định rõ khoảng trống phương pháp luận của khóa luận.

\chapter{Các nghiên cứu liên quan}\label{chap:related}
Rajapaksha và cộng sự hệ thống hóa các hướng IDS dùng AI trên mạng nội xe~\cite{rajapaksha2023survey}; đây là nguồn phân loại phương pháp, không phải kết quả đối chuẩn trực tiếp cho giao thức xuyên xe của khóa luận. Sharmin và cộng sự chỉ ra các nghiên cứu CAN IDS dùng điều kiện thực nghiệm, đặc trưng và metric khác nhau, khiến so sánh điểm số giữa bài báo thiếu cơ sở nếu không khớp giao thức~\cite{sharmin2024benchmark}. Vì vậy phần dưới đối chiếu đầu vào, đơn vị dự đoán, ngân sách dữ liệu xe đích và cách chia dữ liệu trước khi bàn về hiệu năng.

\section{Phát hiện dựa trên thời gian và chuỗi thông điệp}
Cho và Shin sử dụng sai lệch đồng hồ của ECU suy ra từ khoảng cách giữa thông điệp tuần hoàn để phát hiện và truy nguồn tấn công~\cite{cho2016fingerprint}. Cách này cần xây dựng fingerprint theo ECU/xe; vì vậy không thể đồng nhất với đặc trưng thời gian không gắn danh tính ECU của khóa luận. Chiscop và cộng sự nghiên cứu sửa đổi thông điệp mà không thay đổi mẫu thời gian, với mạng tích chập theo thời gian trên tín hiệu CAN~\cite{chiscop2021modification}. Đây là động cơ cụ thể để kiểm tra nhánh payload, nhưng chưa chứng minh nhánh đó tổng quát hóa xuyên xe.

OTIDS phân tích quan hệ thời gian liên quan tới remote frame~\cite{lee2017otids}; phương pháp này cho thấy thời gian có thể là tín hiệu phát hiện, nhưng không làm mọi tấn công payload trở nên quan sát được. Song và cộng sự nghiên cứu bộ phát hiện dùng mạng tích chập trên lưu lượng nội xe~\cite{song2020dcnn}. Hai hướng này cung cấp đối chứng về thông tin đầu vào và kiến trúc, không phải bằng chứng sẵn có rằng mọi mô hình tương ứng đều thất bại trên xe lạ.

Trong nhánh nội dung, payload-only trùng raw-no-ID; timing-only không được thực thi. Chúng không được gọi là tái lập OTIDS hoặc DCNN vì khác thuật toán, dữ liệu đầu vào và giao thức. Việc tái lập một phương pháp công bố đòi hỏi mô tả chính xác cửa sổ, tiền xử lý, hyperparameter và cơ chế quyết định của phương pháp đó.

Jo và Kim kết hợp một bộ phát hiện dựa trên payload với một bộ phát hiện dựa trên tính chu kỳ qua chính sách hợp nhất quyết định~\cite{jo2026fusion}. Thông tin công khai được đối chiếu ở mức abstract; chưa có toàn văn để khẳng định chi tiết split, ngân sách dữ liệu đích hoặc độ trễ. Dong và cộng sự xây dựng hai nhánh lịch sử cùng ID và lịch truyền giữa các ID, sau đó hợp nhất bằng attention cho bài toán spoofing tác động trạng thái~\cite{dong2026mtff}. Vì vậy tổ hợp payload history với quan hệ thời gian không phải ý tưởng chưa từng được nghiên cứu. Khóa luận phân biệt biểu diễn nội dung 30 chiều, đơn vị quyết định theo cửa sổ và giao thức source-only của mình với hai hướng này; khác biệt thiết kế chưa phải bằng chứng vượt trội.

\section{Mô hình tái tạo, Transformer và biểu diễn ngôn ngữ}
CANet sử dụng một nhánh LSTM theo từng ID và ghép trạng thái để tái tạo tín hiệu CAN~\cite{hanselmann2020canet}. Cấu trúc này xử lý thông điệp không đồng bộ nhưng cần ánh xạ ID và tín hiệu tương ứng. Từ kiến trúc đó, không thể suy ra khả năng áp dụng nguyên trạng lên một xe có tập ID khác; đây là khác biệt giả định đầu vào, chưa phải kết quả so sánh hiệu năng.

CAN-BERT học chuỗi ID bằng mục tiêu dự đoán token bị che~\cite{alkhatib2022canbert}. CANBERT+ mở rộng biểu diễn mỗi thông điệp bằng ID, DLC và payload, với tiền huấn luyện tự giám sát và tinh chỉnh có giám sát~\cite{won2026canbertplus}. Chính bài CANBERT+ nêu khác biệt từ điển ID và tín hiệu giữa xe là giới hạn chuyển giao. Các nghiên cứu này làm rõ rằng Transformer và việc kết hợp payload với ngữ cảnh đều đã có tiền lệ; đóng góp ở đây phải được kiểm tra qua giao thức và đối chứng biểu diễn cụ thể.

CANLP dùng TF-IDF và học máy để phát hiện ở mức frame~\cite{balasubramanian2025canlp}. Đây là hướng biểu diễn lấy cảm hứng từ ngôn ngữ nhưng không đồng nghĩa với Transformer. Khác biệt về đơn vị quyết định và thiết bị đo khiến điểm số hoặc độ trễ của CANLP không thể được xếp hạng trực tiếp với cửa sổ 64 frame.

Jo và Kim nghiên cứu indirect exposure training cho phát hiện xâm nhập CAN~\cite{jo2025indirect}. Khóa luận chỉ xác minh metadata và chủ đề ở mức nguồn truy cập được; không dùng tài liệu này để khẳng định chi tiết split, cơ chế chọn tâm hoặc hiệu năng chuyển xe.

\section{Đồ thị và biểu diễn quan hệ}
X-CANIDS giải mã payload thành tín hiệu có thể diễn giải bằng cơ sở dữ liệu CAN rồi phát hiện bất thường trên các tín hiệu này~\cite{jeong2024xcanids}. Đó là một hướng đối chiếu quan trọng về khả năng diễn giải, nhưng giả định có CAN database và đơn vị đầu vào khác với biểu diễn byte/bit không cần DBC đang được khảo sát ở đây. Chưa có phép so sánh định lượng cùng tập dữ liệu và cùng giao thức.

Islam và cộng sự xây dựng IDS theo đồ thị cho CAN~\cite{islam2020graph}. Khreasat và González nghiên cứu đặc trưng thống kê, chuyển tiếp ID và topology, đồng thời phân tích ranh giới transfer và một thí nghiệm hiệu chuẩn bằng dữ liệu bình thường của xe đích~\cite{khreasat2026relational}. Vì vậy không thể tuyên bố rằng việc dùng quan hệ ID hoặc phân tích giới hạn ngoại suy tự nó là mới.

Khác biệt cần kiểm chứng ở đây là sự kết hợp biến thiên payload cùng ID với quan hệ trong cửa sổ và mô hình chuỗi, dưới điều kiện không hiệu chuẩn bằng dữ liệu đích. Đồ thị chuyển tiếp mô tả thứ tự thông điệp quan sát được; không nên gọi cạnh đó là đường giao tiếp vật lý giữa hai ECU. Hai ID liên tiếp có thể xuất phát từ các nguồn khác nhau mà dataset không định danh.

\section{Transfer learning và mục tiêu universal IDS}
CANTransfer sử dụng convolutional LSTM và thích nghi từ dữ liệu mới hạn chế theo hướng one-shot~\cite{tariq2020cantransfer}. Khóa luận sử dụng strict zero-shot nên không đặt điểm của hai chế độ cạnh nhau để kết luận hơn kém mà không nêu lượng dữ liệu đích đã dùng.

Islam và cộng sự đề xuất một hướng universal IDS kết hợp tương quan Pearson, học sâu và biến đổi wavelet sang miền tần số~\cite{s26051489}. Đây là công trình cần đối chiếu gần với mục tiêu tổng quát hóa. Điểm khác cần kiểm chứng của khóa luận là giữ payload và biến thiên cùng ID, dùng A--D và tách nhánh content-only khi không có timestamp. Các khác biệt thiết kế chưa chứng minh ưu thế hiệu năng.

Obafemi báo cáo sự sụt giảm khi chuyển bộ dữ liệu và thử đặc trưng không dùng ID one-hot kết hợp hiệu chỉnh thống kê bằng một đoạn lưu lượng lành của xe đích~\cite{obafemi2026travel}. Ý tưởng bỏ ID thô do đó không thể xem là mới riêng của khóa luận. Vì bài này sử dụng dữ liệu lành đích, điểm số của nó thuộc chế độ thích nghi khác với giao thức source-only ở đây; chưa có tái lập cùng dữ liệu và đơn vị quyết định.

\section{Học tương phản và đối kháng miền}
Hoang và Kim nghiên cứu SupCon ResNet cùng transfer learning trên dữ liệu CAN~\cite{hoang2022supcon}. Kết quả của họ tạo động cơ khảo sát hàm mục tiêu, nhưng khác dữ liệu và phép chia nên không chứng minh contrastive loss chắc chắn vượt cross-entropy trong giao thức này. Cross-entropy vẫn học biểu diễn qua encoder; việc chưa thêm điều chuẩn bất biến không có nghĩa không học biểu diễn.

DANN gốc sử dụng dữ liệu nguồn có nhãn và dữ liệu đích không nhãn~\cite{ganin2016dann}. Trong biến thể đa nguồn giữ ngoài một xe (LOVO), bộ phân loại miền dự đoán xe nguồn kèm điều kiện nhãn lớp nhằm giảm lỗi phân tách miền, còn encoder nhận gradient đảo chiều qua tầng GRL. Tuy nhiên, Zhao và cộng sự chỉ ra bất biến biểu diễn biên cùng lỗi nguồn thấp chưa đủ bảo đảm thích nghi thành công khi có dịch chuyển phân phối có điều kiện~\cite{zhao2019invariant}. Bên cạnh học đối kháng trong khi huấn luyện, các phương pháp triệt tiêu khái niệm hậu nghiệm trên biểu diễn đóng băng như Iterative Nullspace Projection (INLP)~\cite{ravfogel2020null} chiếu lặp biểu diễn vào không gian hạch của các bộ phân loại tuyến tính thuộc tính xe, còn Least-Squares Concept Erasure (LEACE)~\cite{belrose2023leace} xây dựng phép biến đổi affine dạng đóng triệt tiêu chính xác tương quan tuyến tính giữa biểu diễn và thuộc tính xe có điều kiện theo nhãn. Phối hợp chuẩn hóa hiệp phương sai trên lưu lượng lành tính xe đích với các phép xóa tuyến tính fit trên nguồn giúp kiểm tra tách bạch được rò rỉ tuyến tính khỏi rò rỉ phi tuyến trên biểu diễn CAN.

Bên cạnh đó, các kỹ thuật điều chuẩn phân phối như MixStyle~\cite{zhou2021mixstyle} đề xuất trộn thống kê đặc trưng (mean và standard deviation) giữa các mẫu trong quá trình huấn luyện nhằm tăng độ bền vững trước sự dịch chuyển miền. Việc thích ứng ý tưởng này vào mô hình chuỗi thời gian trên mạng nội xe là một hướng khảo sát khả dĩ để kiểm tra liệu việc làm phẳng phong cách đặc trưng có giúp giảm rò rỉ danh tính xe hay không. Các mở rộng đa nguồn LOVO, đối kháng DANN có điều kiện và làm trắng--xóa tuyến tính LEACE/INLP được thực thi và báo cáo tách biệt ở cuối Chương~\ref{chap:results} dưới cùng chuẩn kiểm toán tái lập.

\section{Chất lượng bộ dữ liệu, đánh giá xuyên miền và diễn giải độ đo}
\subsection{Giới hạn bộ dữ liệu và giao thức đánh giá xuyên miền}
Kidmose và cộng sự phân tích giới hạn của các bộ dữ liệu CAN, mở rộng can-train-and-test thành v1.5 với suppress và masquerade, đồng thời cảnh báo đánh giá suppress bằng nhãn frame thông thường có thể gây hiểu sai~\cite{kidmose2025cansleuth}. Bộ v1.5 chưa được dùng trong các run hiện tại. Koltai và cộng sự đánh giá năm hướng IDS trên bảy bộ dữ liệu, cho thấy kết quả phụ thuộc mạnh vào dữ liệu và giao thức đánh giá~\cite{koltai2026trust}. Trong nghiên cứu công bố bộ dữ liệu \texttt{can-train-and-test}, Lampe và Meng~\cite{lampe2024curated} cũng đã chứng kiến sự sụt giảm hiệu năng rõ rệt của các mô hình học sâu cơ sở khi chuyển từ điều kiện A sang B và D, khẳng định thách thức lớn của tính biến thiên giữa các dòng xe. Vì vậy đánh giá trên nhiều dataset tự nó không tạo tính mới; cần chỉ ra khác biệt về phép biểu diễn, ngân sách dữ liệu đích, nhãn và đơn vị metric.

Trong nghiên cứu tổng quát hóa miền, Gulrajani và Lopez-Paz nhấn mạnh việc chọn mô hình theo nguồn và so sánh trong điều kiện nhất quán~\cite{gulrajani2021domainbed}. Đây là nguyên tắc thiết kế từ benchmark ngoài CAN, không phải bằng chứng một thuật toán cụ thể sẽ tốt trên CAN. Khóa luận chốt quy tắc chọn checkpoint/ngưỡng trên nguồn trước khi diễn giải điểm đích.

\subsection{Vấn đề tỷ lệ nền và diễn giải độ đo dưới dịch chuyển miền}
Vấn đề base rate khiến xác suất một cảnh báo là tấn công phụ thuộc mạnh vào tần suất tấn công thực tế~\cite{axelsson2000base}. Weighted F1 vẫn là metric hợp lệ, nhưng không trả lời riêng khả năng bắt lớp tấn công. Tương tự, FAR thấp có thể đi kèm recall thấp nếu mô hình hiếm khi cảnh báo. Khóa luận vì vậy báo cáo cả denominators, precision, recall, F1, AP và FAR.

Saito và Rehmsmeier giải thích vì sao đường precision--recall hữu ích khi lớp dương hiếm~\cite{saito2015pr}. Do AP phụ thuộc tỷ lệ lớp dương, mọi bảng ngoại bộ vẫn cần báo prevalence và số mẫu; bài này không làm ROC-AUC vô nghĩa trong mọi bối cảnh.

Dưới sự dịch chuyển phân phối giữa các dòng xe (covariate shift và logit shift), cần phân biệt rõ giữa \textit{khả năng phân tách và xếp hạng bất thường không phụ thuộc ngưỡng} (đo bằng AP hay diện tích dưới đường cong Precision--Recall) với \textit{hiệu năng vận hành tại điểm quyết định cố định} (đo bằng Recall và FAR tại ngưỡng chọn từ nguồn $\tau_{\text{source}}$). Một biểu diễn có thể cải thiện mạnh thứ tự sắp xếp xác suất của các cửa sổ bất thường, nhưng nếu hàm phân phối điểm số nền bị trôi dạt trên xe đích, ngưỡng cố định từ nguồn có thể dẫn tới sự bùng nổ báo động giả hoặc sụt giảm đột ngột tỷ lệ phát hiện.

Sommer và Paxson nhấn mạnh những khó khăn khi đưa học máy ra ngoài bối cảnh đánh giá đóng~\cite{sommer2010outside}. Trong nghiên cứu này, hệ quả phương pháp là phải kiểm tra nguồn nhãn, thứ tự thời gian, thay đổi phân phối và chi phí cảnh báo. Không sử dụng nhận định tổng quan đó để suy luận rằng một mô hình cụ thể chắc chắn thất bại khi chưa kiểm chứng.

\section{Ma trận đối chiếu và phạm vi tuyên bố mới}
Bảng~\ref{tab:related} tổng hợp đối chiếu định tính phương pháp đề xuất với các công trình nghiên cứu gần nhất về phạm vi đối chuẩn và giả định đầu vào.
\begin{longtable}{P{3.2cm}P{4.1cm}P{7.2cm}}
\caption{Đối chiếu định tính với các công trình gần nhất}\label{tab:related}\\\toprule
Công trình & Hướng tiếp cận & Phạm vi đối chiếu\\\midrule\endfirsthead
\caption[]{(tiếp theo)}\\\toprule Công trình & Hướng tiếp cận & Phạm vi đối chiếu\\\midrule\endhead
OTIDS~\cite{lee2017otids} & Thông tin thời gian & Ngoài nhánh content; không tự nhận là tái lập OTIDS\\
DCNN~\cite{song2020dcnn} & Mạng tích chập & Baseline chuỗi cùng dữ liệu nếu mở rộng kiến trúc\\
Graph IDS~\cite{islam2020graph} & Biểu diễn đồ thị & Thêm baseline đồ thị được tái lập từ đặc tả gốc\\
CANTransfer~\cite{tariq2020cantransfer} & Thích nghi ít mẫu & Báo riêng ngân sách target adaptation\\
Lampe--Meng~\cite{lampe2024curated} & Đối chuẩn nhiều xe & Cùng split và đơn vị window khi so model\\
Relational modelling~\cite{khreasat2026relational} & Chuyển tiếp/topology & So structural-only với payload+structure\\
Hybrid UIDS~\cite{s26051489} & Pearson, wavelet và học sâu & Phân biệt dữ liệu, tần suất injection và calibration\\
MTFF~\cite{dong2026mtff} & Lịch sử cùng ID, lịch truyền, attention & Khác đầu vào, đơn vị frame/window và giao thức\\
Jo--Kim~\cite{jo2026fusion} & Hợp nhất payload và chu kỳ & Chỉ đối chiếu thiết kế khi chưa có full text\\
Obafemi~\cite{obafemi2026travel} & Bỏ ID one-hot, hiệu chỉnh lành đích & Tách ngân sách dữ liệu đích khỏi source-only\\
Koltai~\cite{koltai2026trust} & Benchmark nhiều dataset & Kiểm phép chia và đơn vị đo trước định lượng\\
Khóa luận & Payload, history, structure, Transformer & Ablation cùng model, source-only threshold, tái lập\\\bottomrule
\end{longtable}
Ma trận này nêu sự liên quan, không xếp hạng. Các đề xuất mở rộng đối chứng ngoài ma trận hiện hành thuộc hướng nghiên cứu tương lai; ablation và độ nhạy đã thực hiện được trình bày trong chương kết quả. Trong phạm vi đã triển khai, các đối chứng trực tiếp của ma trận hiện hành là Raw/Structural Transformer và ba bản thích ứng CANBERT+, CANLP-char-DNN, CrySyS-AssocRules/W64; các mô hình này không được đổi tên thành phương pháp của bài báo khác.

\section{Tóm tắt chương}
Chương này đã đối chiếu năm hướng tiếp cận chính trong phát hiện xâm nhập CAN bus, làm rõ các giới hạn về bộ dữ liệu, tính nhất quán của đơn vị đánh giá và sự khác biệt giữa xếp hạng điểm bất thường với quyết định tại ngưỡng đóng băng. Trên cơ sở khoảng trống nghiên cứu được tổng hợp tại Bảng~\ref{tab:related}, Chương~\ref{chap:method} trình bày phát biểu hình thức bài toán và khung biểu diễn cấu trúc đề xuất.

\chapter{Khung biểu diễn cấu trúc xuyên phương tiện}\label{chap:method}
Dựa trên các khoảng trống về tính bất biến định danh và điểm vận hành dưới dịch chuyển miền đã xác định ở Chương~\ref{chap:related}, chương này phát biểu hình thức bài toán và thiết kế chi tiết khung biểu diễn cấu trúc xuyên phương tiện cùng các cơ chế thích ứng và hiệu chuẩn vận hành.

\section{Phát biểu bài toán và mô hình đe dọa}
\subsection{Đơn vị đánh giá cửa sổ và quy tắc gán nhãn}
Với kích thước $W$ và stride $W$, cửa sổ thứ $k$ trong một file gồm
\begin{equation}
\mathcal{W}_k=(F_{kW},\ldots,F_{kW+W-1}),\qquad Y_k=\max_{i=kW}^{kW+W-1}y_i.
\end{equation}
Phần dư cuối file nhỏ hơn $W$ bị bỏ và số frame bị bỏ được ghi lại. Cửa sổ dương có thể chứa phần lớn frame mang nhãn 0; do đó precision/recall theo cửa sổ không bằng precision/recall theo frame. Với nhãn của tấn công chèn, một cửa sổ 64 frame chứa một frame được gán nhãn 1 vẫn là cửa sổ dương; cảnh báo đúng không có nghĩa định vị được frame đó. Với CAN-MIRGU suspension, toàn bộ khoảng đình chỉ được gán nhãn 1 dù không có frame tấn công được chèn~\cite{rajapaksha2024canmirgu}. Vì vậy nhãn 1 không được diễn giải chung là một frame độc hại được chèn.

Khi so sánh với công trình khác, cần trùng đơn vị quyết định, quy tắc nhãn, split và mẫu đánh giá. Không thể chỉ nhân mẫu số FAR theo 64 để biến một bài toán window thành bài toán frame, vì phép gộp nhãn là phi tuyến và quyết định của mô hình không phân bổ ngược duy nhất về các frame.

\subsection{Mục tiêu tối ưu, trạng thái nhân quả và ranh giới tính bất biến}
Bộ trích xuất $\Phi$ biến cửa sổ thành ma trận $X\in\mathbb{R}^{W\times D}$. Bộ phân loại $f_\theta$ trả xác suất lớp 1 và dự đoán
\begin{equation}
p_k=\operatorname{softmax}(f_\theta(\Phi(\mathcal{W}_k)))_1,
\qquad \widehat Y_k=\mathbf{1}[p_k\geq\tau].
\end{equation}
Tham số $\theta$ chỉ học từ phần train nguồn. Ngưỡng $\tau$ chỉ chọn từ validation nguồn và được đóng băng trước test. Các số chia cố định trong feature không được fit lại trên xe đích. Điều này vẫn cho phép đọc lịch sử quá khứ của chính trace đích để tính khoảng cách cùng ID: đó là xử lý đầu vào nhân quả, không phải huấn luyện bằng nhãn đích.

Khác biệt quan trọng là giữa bất biến đổi tên ID và bất biến miền xe. Một phép đổi tên một-một bảo toàn quan hệ cùng ID có thể không thay đổi feature cấu trúc; chuyển xe thực lại thay cả payload, chu kỳ và cấu trúc thông điệp. Chứng minh tính chất thứ nhất không kéo theo tính chất thứ hai.
Để thể hiện phụ thuộc vào quá khứ, có thể viết chính xác đầu vào là $\Phi(\mathcal W_k;H_k)$, với $H_k$ là trạng thái lịch sử trước cửa sổ. Trạng thái bắt đầu rỗng ở mỗi file. Các công thức rút gọn $\Phi(\mathcal W_k)$ trong khóa luận luôn đi kèm quy tắc trạng thái này; mỗi cửa sổ không phải một đoạn độc lập được trích xuất lại từ đầu.

Đặt dưới mô hình đe dọa IDS thụ động đã nêu tại Chương~\ref{chap:background}, lộ trình phương pháp phân tách rõ hai chế độ đánh giá: kiểm định zero-shot nghiêm ngặt với trọng số $\theta$ và ngưỡng $\tau$ hoàn toàn đóng băng từ nguồn để cô lập năng lực biểu diễn, và hiệu chuẩn khởi động nền lành tính không nhãn trên xe đích nhằm giải quyết sai lệch ngưỡng khi triển khai thực tế.

\section{Kiến trúc luồng xử lý và hợp đồng dữ liệu đầu vào}
\subsection{Luồng xử lý và phân chia trách nhiệm}
Giao thức thực nghiệm tuân thủ quy trình xử lý chặt chẽ gồm bốn giai đoạn độc lập: kiểm chứng dữ liệu tiền trạm (preflight verification), trích xuất đặc trưng cửa sổ, huấn luyện và hiệu chuẩn mô hình trên tập nguồn, và đánh giá hiệu năng đóng băng trên tập đích. Toàn bộ các cấu phần thuật toán được module hóa đồng bộ; cấu hình siêu tham số, phiên bản thư viện và mã nguồn thực thi được kiểm soát tường minh qua hệ thống tệp kê khai (manifest). Luồng xử lý đảm bảo nguyên tắc nhân quả một chiều: dữ liệu của phương tiện đích hoàn toàn không được sử dụng trong các bước huấn luyện, chọn mô hình hoặc tối ưu ngưỡng quyết định, như được mô hình hóa trực quan tại Hình~\ref{fig:pipeline}.

\begin{figure}[htbp]\centering
\begin{tikzpicture}[node distance=0.35cm, every node/.style={draw,rounded corners,align=center,font=\small,text width=11cm,inner sep=4.5pt},>=Stealth]
\node (a) {File gốc và nguồn nhãn: kiểm tra schema, thứ tự thời gian, hash};
\node (b) [below=of a] {Cửa sổ hoàn chỉnh: raw 28 / structural 30 chiều (content)};
\node (c) [below=of b] {Nhóm train nguồn: lấy mẫu toàn file, huấn luyện classifier};
\node (d) [below=of c] {Nhóm validation nguồn: chọn ngưỡng theo ngân sách FAR};
\node (e) [below=of d] {Đóng băng checkpoint và ngưỡng: A--D, ngoại suy theo schema};
\node (f) [below=of e] {Dự đoán từng cửa sổ, confusion matrix, metric và báo cáo};
\foreach \s/\t in {a/b,b/c,c/d,d/e,e/f} \draw[->] (\s)--(\t);
\end{tikzpicture}
\caption{Pipeline với ranh giới nguồn/đích rõ ràng. Nhánh content-only bỏ các chiều thời gian ở cả train và test.}\label{fig:pipeline}
\end{figure}

\subsection{Hợp đồng dữ liệu và kiểm tra đầu vào}
Schema tối thiểu gồm \code{timestamp}, \code{arbitration_id}, \code{data_field} và \code{attack}; DLC được giữ nếu nguồn cung cấp. ID và payload được đọc như chuỗi để tránh mất số 0 đầu hoặc đổi hex thành số thập phân. Không loại ký tự tùy tiện để ``sửa'' một ID sai. Payload có số ký tự lẻ, dài quá 8 byte hoặc mâu thuẫn DLC sẽ gây lỗi. Nhãn thiếu không được mặc định là benign.

Chỉ nhánh timed yêu cầu timestamp hữu hạn và không giảm trong capture, kể cả qua biên chunk. Phép so content hiện tại giữ nguyên timestamp để kiểm toán các lần giảm, nhưng không dùng chúng làm đặc trưng hoặc tự sắp xếp lại dữ liệu. Với dataset không có thời gian, timestamp được giữ là thiếu và chỉ nhánh content-only được phép chạy. Với dữ liệu không chứng minh được thứ tự bản ghi, ngay cả đặc trưng chuyển tiếp cũng cần giới hạn diễn giải: content-only không tự chứng minh thứ tự vật lý của các dòng CSV.

Parser không tự sắp xếp lại theo timestamp vì nhiều capture khác nhau có thể dùng cùng gốc thời gian. Lỗi schema/nhãn trong nguồn CTT dừng run và ghi FAILED. Đối với ngoại bộ, file lỗi bị loại toàn bộ, lưu lý do trong ledger và không nhập số liệu từng phần vào kết quả. Điều này giữ nguyên thông tin cần điều tra, thay vì tạo bảng kết quả sau khi âm thầm bỏ các mẫu khó xử lý.

\subsection{Cửa sổ, trạng thái và tính độc lập với khối đọc}
Mỗi file có một đối tượng trích xuất riêng. Đối tượng lưu các frame chưa đủ cửa sổ, timestamp trước và lịch sử của mỗi ID. Khi đọc chunk tiếp theo, phần dư được nối với chunk trong cùng file. Khi file kết thúc, phần dư bị bỏ; trạng thái không chuyển sang file khác.

Trong nhánh content, lịch sử payload cùng ID được giữ liên tục qua cửa sổ và chunk theo thứ tự file. Timestamp không tham gia đầu vào mô hình. Vì vậy thay chunksize không được làm thay đổi số cửa sổ hoặc feature. Tính chất này được kiểm bằng đối chiếu trích xuất toàn bộ với nhiều kích thước chunk không chia hết cho $W$.

Thống kê tần suất và chuyển tiếp dùng đủ $W$ frame. Do đó thời điểm quyết định sớm nhất là khi có frame cuối cửa sổ. Đây là thiết kế causal ở cấp cửa sổ, không phải dự đoán ngay khi frame đầu tới. Không sử dụng frame của cửa sổ tương lai để tính feature của cửa sổ hiện tại. Về chính sách quản lý trạng thái lịch sử $H_k$ khi triển khai liên tục (bên ngoài ranh giới tệp thí nghiệm): đối với CAN chuẩn 11-bit ($2.048$ định danh tối đa), bảng lịch sử cố định chỉ chiếm $130\text{ KiB}$ RAM (cờ hợp lệ $1\text{ B}$ + vector payload cuối $8\times 4\text{ B}$ + mặt nạ DLC $8\times 4\text{ B}$ mỗi ID), cần được đặt lại (\textit{reset}) theo phiên khóa điện (ignition cycle) hoặc khi phát hiện im lặng bus quá ngưỡng timeout (chẳng hạn $\tau_{\text{idle}}>5\text{ s}$) nhằm tránh ghép $\Delta\text{payload}$ qua các lần ngắt ECU/ngủ đông; khi mở rộng sang CAN mở rộng 29-bit hoặc CAN-FD (payload tới $64\text{ B}$), bảng chỉ mục trực tiếp $2^{11}$ mục phải thay bằng bảng băm giới hạn dung lượng (ví dụ LRU $256\text{--}1.024$ ID hoạt động) kèm nén tóm tắt payload vượt 8 byte.

\section{Đặc tả biểu diễn đặc trưng cấu trúc 30 chiều}
Giao thức thực nghiệm dùng raw 28 chiều bao gồm: 11 bit nhị phân của \code{arbitration_id} được giải nén từ bit trọng số cao (MSB, bit 10) đến bit trọng số thấp (LSB, bit 0); 1 chiều DLC chuẩn hóa ($d_i/8$); 8 byte payload chuẩn hóa ($b_{i,j}/255$, byte ngoài DLC được đệm 0); và 8 chiều mặt nạ tính hợp lệ ($m_{i,j}=\mathbf{1}[j<d_i]$). Biểu diễn structural có 30 chiều như đặc tả trong Bảng~\ref{tab:features}. Cả hai biểu diễn đều không sử dụng đặc trưng thời gian. Chuẩn hóa dùng hằng số cố định, không học từ tập kiểm thử.
\begin{longtable}{P{2.4cm}P{1.2cm}P{9.2cm}}
\caption{Định nghĩa biểu diễn structural ở cấp frame}\label{tab:features}\\\toprule
Chỉ số & Chiều & Định nghĩa\\\midrule\endfirsthead
\caption[]{(tiếp theo)}\\\toprule Chỉ số & Chiều & Định nghĩa\\\midrule\endhead
0 & 1 & $d_i/8$, với $d_i$ là độ dài payload được xác minh\\
1--8 & 8 & $b_{i,j}/255$; byte ngoài DLC được đệm 0\\
9--16 & 8 & $m_{i,j}=\mathbf{1}[j<d_i]$\\
17--24 & 8 & $|b_{i,j}-b_{q,j}|m_{i,j}m_{q,j}/255$, với $q$ là frame trước cùng ID trong file\\
25 & 1 & $h_i = \mathbf{1}[\text{lịch sử}(c_i) \neq \emptyset]$, cờ chỉ báo tồn tại frame trước cùng ID\\
26 & 1 & $f_k(c_i)/W$, tần suất xuất hiện của ID $c_i$ trong cửa sổ $k$\\
27 & 1 & $\operatorname{rank}_0(c_i)/U_k$, thứ tự xuất hiện đầu tiên (bắt đầu từ 0) chia số ID phân biệt $U_k$ trong cửa sổ\\
28 & 1 & $\operatorname{rank}_0(c_i)/W$, cùng hạng cục bộ chia kích thước cửa sổ $W$\\
29 & 1 & $T_k(c_{i-1}, c_i)/(W-1)$ cho $i>0$ và $0$ khi $i=0$; số lần chuyển tiếp giữa cặp ID liên tiếp trong cửa sổ\\\bottomrule
\end{longtable}
Hai feature 27 và 28 cùng dựa trên thứ tự xuất hiện, với mẫu số khác nhau. Chúng không được tuyên bố là hai nguồn thông tin độc lập. Ablation nhóm local statistics kiểm tra liệu nhóm này có bổ sung giá trị ngoài lịch sử payload hay không. Hiệu payload chỉ được tính trên các byte hữu hiệu ở cả hai frame, tránh biến sự thay đổi padding thành tín hiệu cảm biến giả.

Gọi $r_i = \operatorname{rank}_0(c_i)$ là thứ tự xuất hiện đầu tiên (tính từ $0$) của định danh $c_i$ trong cửa sổ $k$; với $r_i > 0$, tỷ số $f_{28}/f_{27}=U_k/W$ cố định trong cửa sổ $k$, nhưng $U_k$ có thể đổi giữa các cửa sổ. Không suy ra đồng tuyến toàn bộ dữ liệu hoặc tác hại tối ưu chỉ từ tỷ số này. Biến thể bỏ riêng chiều 28 kiểm tra vai trò của cách mã hóa thứ hai; biến thể bỏ byte payload tuyệt đối giữ DLC, mask (9 chiều) và biến thiên cùng cờ $h_i$ để khảo sát tín hiệu phụ thuộc xe.

Hiệu từng byte không phải khoảng cách tín hiệu vật lý: nếu hai byte mã hóa số nguyên 16 bit, chuyển $\texttt{00FF}\rightarrow\texttt{0100}$ chỉ tăng một đơn vị nhưng byte thấp thay đổi 255. Khoảng cách Hamming cũng đổi 9 bit trong ví dụ này. Vì vậy entropy hoặc Hamming chỉ là ứng viên mở rộng cần đối chứng, không được gọi là phép sửa đã chứng minh cải thiện.

\subsection{Nhánh không dùng thời gian}
So với đặc tả timed v2.1 lưu trong mã lịch sử, nhánh content loại raw index 28 và hai chiều thời gian structural cũ 26, 27; các chỉ số trong Bảng~\ref{tab:features} đã được đánh lại cho nhánh 30 chiều. Kích thước tương ứng là 28 và 30. Các mô hình content được huấn luyện trên CTT với lược đồ tương ứng; không đưa timestamp giả hoặc zero-fill vào mô hình đã học timing. Dataset đích vẫn cần giữ thứ tự hàng có căn cứ nếu sử dụng history và transition. Nếu thứ tự không được xác nhận, kết quả chỉ là đánh giá trên thứ tự cung cấp và không phải chứng minh tính thời gian thực.

\subsection{Tính bất biến đổi tên ID}
Xét một ánh xạ một-một $g$ áp dụng nhất quán cho toàn bộ ID trong một capture và trạng thái lịch sử, giữ nguyên timestamp và payload. Quan hệ $c_i=c_j$ tương đương $g(c_i)=g(c_j)$; tần suất, thứ tự xuất hiện đầu tiên, các cặp chuyển tiếp và vị trí frame trước cùng ID vì vậy được bảo toàn. Các feature structural không thay đổi dưới phép đổi tên này. Ánh xạ phải nằm trong miền ID được parser hỗ trợ.

Nếu đổi tên độc lập ở từng cửa sổ mà không đổi lịch sử tương ứng, tính chất trên không còn được bảo đảm. Nếu thay đổi payload hoặc thời gian như khi đổi xe thực, chứng minh cũng không áp dụng. Kiểm thử invariance là kiểm tra phần triển khai của tính chất hẹp đã định nghĩa, không phải bằng chứng tổng quát hóa đa xe.

\section{Bộ mã hóa chuỗi Transformer và hàm mục tiêu}
Mô hình dựa trên cơ chế attention~\cite{vaswani2017attention}. Mỗi vector được chiếu tuyến tính tới 64 chiều rồi cộng positional embedding học được kích thước $W\times64$. Hai Transformer encoder layers sử dụng 4 heads, feed-forward 128, GELU và dropout 0,1. Mean pooling tạo embedding 64 chiều; head gồm LayerNorm, Linear 64-to-32, ReLU và Linear 32-to-2.

Với logits $z_{k,0},z_{k,1}$, mô hình tối ưu cross-entropy hai lớp:
\begin{equation}
\mathcal L(\theta)=-\frac1N\sum_{k=1}^N\log\frac{\exp z_{k,Y_k}}{\exp z_{k,0}+\exp z_{k,1}}.
\end{equation}
Không dùng Focal Loss hay contrastive loss trong cấu hình xác định ở đây. Các phương án đó chỉ có thể được bổ sung như thí nghiệm riêng có run ID riêng. Do chỉ tầng chiếu đầu vào thay đổi theo số chiều $D$, số lượng tham số thực tế (trích xuất trực tiếp từ mô hình) là 75.170 tham số cho Raw Transformer (28D) và 75.298 tham số cho Structural Transformer (30D; chênh nhau đúng $2\times 64 = 128$ trọng số ở lớp tuyến tính đầu vào), trong khi các biến thể ablation NoPayload (22D) có 74.786 tham số, NoDelta (21D) có 74.722 tham số, và NoLocal (27D) có 75.106 tham số. Đối chiếu với hai baseline học sâu trong ma trận chính, mô hình \code{CANLP-char-DNN} gọn nhẹ hơn (43.458 tham số cho đầu vào 273 chiều TF-IDF + ID) còn \code{CANBERT+} lớn hơn nhiều lần (54.247.853 tham số từ kiến trúc BERT 6 tầng, 12 head, kích thước ẩn 768). Vì vậy ``cùng kiến trúc bộ mã hóa'' giữa Raw và Structural giữ bất biến toàn bộ phần thân Transformer và đầu phân loại, chỉ khác duy nhất 128 tham số tầng chiếu đầu vào. Toàn bộ sơ đồ luồng dữ liệu từ trích xuất đặc trưng 30 chiều, bộ mã hóa Transformer đến các nhánh phân loại và thích ứng miền được minh họa trực quan trong Hình~\ref{fig:architecture-30d}.

\begin{figure}[htbp]\centering
\includegraphics[width=0.98\textwidth]{figs/pipeline_architecture_30d.png}
\caption{Sơ đồ kiến trúc tổng thể phương pháp Structural Transformer và các nhánh thích ứng/chẩn đoán: (1) Đầu vào luồng CAN thô ($W=64$) kết hợp cập nhật nhân quả bảng lịch sử $H_k$; (2) Trích xuất vector 30 chiều đặc trưng cấu trúc cấp khung tin; (3) Bộ mã hóa Transformer 2 tầng ($75.298$ tham số) tích hợp MixStyle và Mean Pooling tạo biểu diễn ẩn cửa sổ $z_k \in \mathbb{R}^{64}$; (4) Nhánh phân loại chính (kèm hiệu chuẩn Benign Warmup $K=500$ và lọc sự kiện $m$-of-$n$) cùng 3 nhánh mở rộng: học đa nguồn LOVO-cAdv DANN, triệt tiêu tuyến tính LEACE/INLP8 với năng lượng Mahalanobis, và bộ thăm dò chẩn đoán rò rỉ danh tính xe.}\label{fig:architecture-30d}
\end{figure}

Cross-entropy ràng buộc dự đoán trên mẫu huấn luyện, không buộc mọi tấn công chưa thấy thuộc lớp bình thường. Điểm thấp ở C/D có thể liên quan tới độ phủ tấn công, biểu diễn, dịch chuyển phân phối hoặc ngưỡng. Chưa có đối chứng nên không quy toàn bộ thất bại lịch sử cho hàm mất mát và cũng không bảo đảm thêm nhánh tái tạo sẽ khắc phục được. Các siêu tham số huấn luyện và ngân sách báo động giả chi tiết của thực nghiệm được trình bày tại Mục~\ref{sec:comparison-protocol} (Bảng~\ref{tab:config}).

\section{Các phương pháp thích ứng miền và hiệu chuẩn vận hành}\label{sec:domain-adaptation-methods}
Dưới sự dịch chuyển phân phối giữa các dòng xe (đặc biệt là hiện tượng trôi dạt phân phối logit nền khiến ngưỡng tĩnh từ xe nguồn bị lệch), khóa luận mở rộng nghiên cứu bằng bốn hướng phương pháp thích ứng miền và triệt tiêu đặc thù xe:

\subsection{Trộn đặc trưng miền theo lô (MixStyle)}\label{subsec:method-mixstyle}
Nhằm nâng cao khả năng khái quát hóa miền mà không yêu cầu nhãn của phương tiện mới, kỹ thuật MixStyle~\cite{zhou2021mixstyle} được thích ứng cho bộ mã hóa Transformer trên chuỗi thời gian CAN. Trong quá trình huấn luyện, với mỗi cặp biểu diễn đầu vào $(X, \widetilde{X})$ thuộc cùng một lớp nhãn ($Y = \widetilde{Y}$), sau tầng chiếu tuyến tính ($E \in \mathbb{R}^{W \times d}$, với $d=64$) và trước khi cộng mã hóa vị trí, ta tính vector kỳ vọng và độ lệch chuẩn theo trục khung tin:
\begin{equation}
\mu(X) = \frac{1}{W}\sum_{i=1}^W E_i, \qquad \sigma(X) = \sqrt{\frac{1}{W}\sum_{i=1}^W (E_i - \mu(X))^2 + \epsilon}.
\end{equation}
Thống kê phong cách hỗn hợp được tạo qua phép nội suy lồi:
\begin{align}
\gamma &= \lambda \sigma(X) + (1 - \lambda) \sigma(\widetilde{X}),\\
\beta &= \lambda \mu(X) + (1 - \lambda) \mu(\widetilde{X}),
\end{align}
trong đó $\lambda \sim \text{Beta}(\alpha, \alpha)$ với tham số $\alpha = 0{,}1$. Biểu diễn chuẩn hóa sau khi trộn phong cách được xác định bởi:
\begin{equation}
\operatorname{MixStyle}(X) = \gamma \odot \frac{E - \mu(X)}{\sigma(X)} + \beta.
\end{equation}
Phép biến đổi này được kích hoạt ngẫu nhiên với xác suất $p=0{,}5$ trong pha huấn luyện; khi suy luận (inference), mô hình hoạt động ở chế độ tất định thuần túy (identity).

\subsection[Hiệu chuẩn nền lành tính không giám sát]{Hiệu chuẩn nền lành tính không giám sát (Unsupervised Benign Warmup Calibration)}\label{subsec:method-calibration}
Nhằm khắc phục hiện tượng trôi dạt ngưỡng nguồn $\tau_{\text{src}}$ trên phương tiện đích mà không cần bất kỳ nhãn tấn công nào, phương pháp hiệu chuẩn nền lành tính tận dụng một đoạn lưu lượng ban đầu gồm $K$ cửa sổ lành tính khi xe khởi động (\textit{warmup prefix}). Để ngăn ngừa hoàn toàn hiện tượng rò rỉ thông tin tấn công (\textit{non-leaky prefix}), chỉ số giới hạn được chặn trên bởi:
\begin{equation}
K_{\text{valid}} = \min\big(K, \lfloor \text{prefix\_end} / 2 \rfloor\big), \qquad K \in \{200, 500, 1000\}.
\end{equation}
Ngưỡng quyết định vận hành trên xe đích được xác định theo phân vị mẫu tương ứng với ngân sách báo động giả mục tiêu $\alpha \in \{0{,}1\%, 0{,}5\%, 1{,}0\%, 2{,}0\%\}$:
\begin{equation}
\tau_{\text{target}} = \operatorname{Quantile}_{1-\alpha}\big(\{s(X_k)\}_{k=1}^{K_{\text{valid}}}\big).
\end{equation}
Đồng thời, để kiểm soát số lượng cảnh báo giả theo giờ trong điều kiện tốc độ bus cao ($1.000\text{--}2.000\text{ khung/giây}$), cơ chế lọc gộp sự kiện trượt $m$-trong-$n$ (\textit{sliding $m$-of-$n$ filter}) được áp dụng: một cảnh báo tấn công chỉ được kích hoạt chính thức khi có ít nhất $m$ trong $n$ cửa sổ liên tiếp ($m/n \in \{2/3, 3/5\}$) vượt ngưỡng $\tau_{\text{target}}$.

\subsection[Học đa nguồn LOVO kết hợp đối kháng có điều kiện]{Học đa nguồn LOVO kết hợp phân loại đối kháng có điều kiện (LOVO-cAdv DANN)}\label{subsec:method-lovo}
Trong kịch bản có sẵn dữ liệu từ nhiều dòng xe nguồn, kiến trúc học đa nguồn theo giao thức giữ ngoài một xe (Leave-One-Vehicle-Out --- LOVO) tích hợp mạng đối kháng miền (Domain-Adversarial Neural Network --- DANN)~\cite{ganin2016dann}. Hệ thống gồm ba thành phần: bộ trích xuất đặc trưng $G_f(\cdot; \theta_f)$, bộ phân loại xâm nhập $G_y(\cdot; \theta_y)$, và bộ phân biệt miền đối kháng $G_d(\cdot; \theta_d)$. Nhánh đối kháng nhận đầu vào là tích tensor có điều kiện giữa vector đặc trưng $z_k = G_f(X_k)$ và phân phối xác suất dự đoán $\hat{y}_k = G_y(z_k)$, đi qua tầng đảo ngược gradient (Gradient Reversal Layer --- GRL):
\begin{equation}
\mathcal{L}_{\text{total}} = \mathcal{L}_y(G_y(G_f(X)), Y) - \lambda_{\text{adv}} \mathcal{L}_d\big(G_d(\operatorname{GRL}_{\lambda}(z \otimes \hat{y})), V\big),
\end{equation}
trong đó $V$ là nhãn định danh xe nguồn và $\lambda_{\text{adv}}$ tăng dần theo lịch trình huấn luyện nhằm ép bộ mã hóa học các biểu diễn bất biến theo phương tiện.

\subsection[Làm trắng nền lành tính, xóa tuyến tính và năng lượng Mahalanobis]{Làm trắng hiệp phương sai nền lành tính, triệt tiêu khái niệm tuyến tính (LEACE/INLP8) và điểm năng lượng Mahalanobis}\label{subsec:method-whitening}
Để phân tích sâu bản chất của thông tin định danh xe trên không gian embedding đóng băng $z_k \in \mathbb{R}^{64}$, khóa luận thiết lập khung xử lý gồm chuẩn hóa làm trắng kết hợp triệt tiêu không gian con:
\begin{enumerate}
    \item \textbf{Làm trắng hiệp phương sai nền lành tính:} Từ $1.000$ cửa sổ lành vị trí chẵn của xe đích, ước lượng kỳ vọng $\mu_b$ và ma trận hiệp phương sai co $\Sigma_s = (1-\gamma)\Sigma_b + \gamma \bar{\sigma}^2 I$ (với hệ số co $\gamma = 0{,}1$). Ma trận làm trắng $W_{\text{white}} = \Sigma_s^{-1/2}$ biến đổi embedding thành $z'_k = W_{\text{white}}(z_k - \mu_b)$ sao cho nền lành tính của mọi xe có kỳ vọng triệt tiêu và hiệp phương sai đơn vị.
    \item \textbf{Triệt tiêu khái niệm tuyến tính:} Áp dụng phép chiếu trực giao LEACE~\cite{belrose2023leace} hoặc phép chiếu không gian rỗng lặp INLP~\cite{ravfogel2020null} (với $8$ vòng lặp) fit trên các xe nguồn nhằm xóa bỏ hoàn toàn các hướng tuyến tính chứa thông tin nhận diện hãng xe.
    \item \textbf{Điểm bất thường năng lượng Mahalanobis (\code{white\_energy}):} Thay vì dựa vào đầu phân loại nguồn, điểm bất thường được tính trực tiếp từ khoảng cách năng lượng bình phương trên không gian đã làm trắng:
    \begin{equation}
    E(X_k) = \| W_{\text{white}} (z_k - \mu_b) \|_2^2,
    \end{equation}
    tạo ra một bộ đo bất thường thuần túy trên nền lành của xe đích, hoàn toàn độc lập với trọng số phân loại nhị phân ban đầu.
\end{enumerate}

\section{Tóm tắt chương}
Chương này đã hoàn thiện đặc tả hình thức của bài toán, hợp đồng dữ liệu nhân quả, không gian đặc trưng cấu trúc 30 chiều, kiến trúc Transformer mã hóa chuỗi cùng bốn mở rộng thích ứng miền và hiệu chuẩn nền lành tính. Chương~\ref{chap:results} tiếp tục thiết lập giao thức thực nghiệm chi tiết và báo cáo toàn bộ kết quả kiểm chứng định lượng.

\chapter{Thực nghiệm và đánh giá}\label{chap:results}
Chương này phân biệt phép so chính đã định nghĩa tiêu chí với phân tích bổ sung hậu nghiệm. Mọi số tổng hợp dùng trung bình seed trong set rồi trọng số ngang nhau giữa các set; không xem số cửa sổ là số xe độc lập. Dấu -- là không xác định, không phải số không. Bố cục chương được tổ chức theo bốn phần: Mục 4.1 xác lập thiết lập và giao thức thực nghiệm; Mục 4.2 đánh giá chuyển giao zero-shot và chẩn đoán biểu diễn cấu trúc tương ứng RQ1--RQ4; Mục 4.3 đánh giá các cơ chế thích ứng miền và khôi phục điểm vận hành; và Mục 4.4 phân tích chi phí xử lý cùng các đe dọa tính hợp lệ.

\section{Thiết lập và giao thức thực nghiệm}
\subsection{Tách nguồn, lấy mẫu reservoir và chống rò rỉ}
Bảng~\ref{tab:split-stats} tổng hợp cấu trúc chia tách theo hậu tố vòng ghi (\textit{recording round}), quy mô cửa sổ W64 trước/sau lấy mẫu và độ phủ các họ tấn công của 4 set sau preflight: Set 1--4 có tổng cộng 30 tệp huấn luyện nguồn (388.435 W64 khả dụng; hậu tố 1 và 3) và 30 tệp validation nguồn (385.168 W64 đầy đủ không cắt tỉa; hậu tố 2 và 4), hoàn toàn không dùng hậu tố test A--D trong bước học hay chọn ngưỡng.

\begin{table}[htbp]\centering\small
\caption{Thống kê chia tách nguồn, số tệp và họ tấn công trên 4 set \texttt{can-train-and-test}}\label{tab:split-stats}
\begin{tabular}{P{1.1cm}P{2.2cm}P{2.2cm}P{1.5cm}P{6.3cm}}
\toprule
Set & Nguồn (Train/Val) & Test A/B/C/D & Hậu tố Val & Họ tấn công trong A--B / C--D \\ \midrule
1 & 6 / 6 tệp & 8 / 8 / 12 / 12 & 2, 4 & A--B: DoS, force-neutral, rpm, standstill; C--D: double, fuzzing, interval, speed, systematic, triple \\
2 & 8 / 8 tệp & 12 / 12 / 8 / 8 & 2, 4 & A--B: double, fuzzing, interval, speed, systematic, triple; C--D: DoS, force-neutral, rpm, standstill \\
3 & 7 / 7 tệp & 10 / 10 / 14 / 14 & 2, 4 & A--B: DoS, double, force-neutral, fuzzing, triple; C--D: interval, rpm, rpm-acc., speed, speed-acc., standstill, systematic \\
4 & 9 / 9 tệp & 14 / 14 / 10 / 10 & 2, 4 & A--B: interval, rpm, rpm-acc., speed, speed-acc., standstill, systematic; C--D: DoS, double, force-neutral, fuzzing, triple \\
\bottomrule
\end{tabular}
\end{table}

Các file nguồn được nhóm theo hậu tố số vòng ghi; toàn bộ file cùng hậu tố ở cùng phía train hoặc validation. Nhóm hậu tố lớn nhất mặc định làm validation. Đây là cách chia bảo thủ hơn random windows, nhưng cần xác nhận metadata để chứng minh các vòng là những chuyến lái độc lập. Không tái huấn luyện với validation sau khi chọn ngưỡng, vì việc đó làm checkpoint và ngưỡng không còn tương ứng.

Lấy mẫu giới hạn bộ nhớ bằng random-priority reservoir riêng cho mỗi lớp và file. Mỗi cửa sổ nhận một khóa ngẫu nhiên; giữ tối đa 1.000 khóa nhỏ nhất cho từng lớp. Toàn bộ file phải được đọc trước khi hoàn tất mẫu. Một attack ở cuối file vì vậy vẫn có cơ hội được chọn như một attack đầu file. Lấy mẫu diễn ra sau trích xuất trạng thái liên tục, không nối các frame đã chọn rời rạc thành chuỗi giả.

Danh sách window index đã chọn, số cửa sổ có sẵn và số được chọn của từng lớp/file được xuất ra. Mọi representation dùng cùng mẫu. Validation và test được đánh giá đầy đủ với prevalence gốc, không cân bằng lại để làm đẹp metric. Coverage theo attack family được lưu để kiểm tra độ phủ lớp và cơ chế trong source.

Trong bộ lấy mẫu hiện hành, chuỗi ngẫu nhiên được tách theo file và lớp với seed xác định từ seed lấy mẫu và tên file. Vì vậy thay đổi chunksize hoặc thứ tự duyệt file không đổi lựa chọn cửa sổ trong cùng file. Các chỉ mục mẫu được lưu để mọi phương pháp trong cùng phép so dùng đúng cùng cửa sổ nguồn.

Lần chạy nghiên cứu yêu cầu manifest preflight toàn file có trạng thái PASS, khớp mã kiểm tra, ledger và hash dữ liệu hiện dùng. Preflight yêu cầu đủ bốn set và các thư mục A--D, ghi riêng dữ liệu ngoại bộ thiếu/bị loại, và phát hiện tệp trùng hệt liên quan nguồn trong cùng set. SHA-256 không loại trừ các đoạn trace dùng chung hoặc chứng minh các chuyến lái độc lập; nguồn gốc phiên ghi vẫn là giới hạn cần xác nhận.

\subsection{Đối chứng, cấu hình huấn luyện và giao thức so sánh CTT}\label{sec:comparison-protocol}
Toàn bộ cấu hình siêu tham số huấn luyện chi tiết của thực nghiệm được tóm tắt tại Bảng~\ref{tab:config}.
\begin{table}[htbp]\centering
\caption{Cấu hình huấn luyện của thực nghiệm}\label{tab:config}
\begin{tabular}{ll}\toprule Tham số & Giá trị\\\midrule
Cửa sổ chính / độ nhạy & 64 / 32 và 128\\
Hidden / layers / heads & 64 / 2 / 4\\
Feed-forward / dropout & 128 / 0,1\\
Optimizer & AdamW\\
Learning rate / weight decay & 0,001 / $10^{-4}$\\
Epochs / batch size & 10 / 128\\
Scheduler & Cosine theo epoch\\
Seed khởi tạo & 42, 43, 44\\
Seed lấy mẫu chung & 20261103\\
Giới hạn mỗi file, mỗi lớp train & 1.000 cửa sổ\\
Ngân sách FAR validation & 100/100.000 cửa sổ benign\\\bottomrule\end{tabular}
\end{table}

Ngân sách FAR là một lựa chọn thiết kế để so sánh, không phải chuẩn an toàn vận hành ô tô. Các ngân sách khác cần cấu hình và phân tích riêng. LR trong nghiên cứu bổ sung là bộ giải mã probe, không phải một IDS được đưa vào bảng xếp hạng.

\textbf{Giao thức đang thực thi là \code{ctt-content-order-comparison-v1}.}
Đặc tả timed v2.1 lịch sử được tách sang phụ lục; ma trận năm mô hình hiện hành chỉ dùng nội dung và thứ tự file. Quét toàn bộ 236 file CTT cho thấy 193.240.845 khung dữ liệu, 3.019.271 cửa sổ W64 hoàn chỉnh và 12.527 lần timestamp giảm trong 100 file. Số cửa sổ trên là toàn bộ kho dữ liệu, bao gồm cả vai trò huấn luyện, validation và kiểm thử; không phải mẫu số test của mỗi mô hình. Chênh lệch 236 so với tổng số dòng 193.241.081 là một dòng tiêu đề mỗi file. Số dòng và số khung dữ liệu không được dùng thay thế nhau.

Cache giữ nguyên ID, DLC, payload, nhãn, timestamp và thứ tự dòng; không sắp xếp lại, xóa trùng hay dựng thời gian. Phép so bỏ raw index 28 và structural index 26--27 theo chỉ số bắt đầu từ 0: raw còn 28 chiều và structural còn 30 chiều. Các đặc trưng lịch sử được tính theo thứ tự file, không diễn giải thành chu kỳ vật lý. Nhánh timed vẫn bị chặn cho tới khi nguồn timestamp được xác minh. Mã băm toàn vẹn (SHA-256) của manifest cache và các tệp dữ liệu được lưu trữ chi tiết tại Phụ lục~\ref{sec:app-provenance}.

Ma trận gồm bốn set, seed 42/43/44 và năm phương pháp: tổng 60 đơn vị IDS, mỗi đơn vị đánh giá A--D. Pretrain và fine-tune của CANBERT+ là hai giai đoạn trong một đơn vị, không phải hai cell độc lập. W64 không chồng lặp và không nối file. Reservoir lấy tối đa 1.000 cửa sổ mỗi lớp mỗi file trên toàn bộ nhóm huấn luyện nguồn, sampling seed 20261103. Các phương pháp nhận cùng chỉ mục mẫu nguồn. Validation tách theo nhóm hậu tố recording-round; vocabulary, TF-IDF và mọi tham số học chỉ dùng nguồn.

\subsubsection{Đối thủ, supervision và thay đổi so với công bố}
Raw và Structural Transformer dùng cùng kiến trúc bộ mã hóa, mẫu nguồn, CE/AdamW/Cosine, 10 epoch, batch 128 và learning rate 0,001; khác biệt chính là biểu diễn 28/30 chiều. Chênh lệch này kiểm tra gói biểu diễn, chưa tách được ảnh hưởng bỏ ID khỏi từng đặc trưng cấu trúc.

CANBERT+~\cite{won2026canbertplus} dùng module BERT/MLM của tác giả, hidden 768, 6 lớp và 12 head. Vocabulary chỉ từ nguồn; pretrain masked-ID 15\% trên benign nguồn trong 3 epoch, sau đó fine-tune nhãn frame 3 epoch, batch 8. Chuyển vòng lặp Lightning sang PyTorch, lấy mẫu nguồn chung, split theo nhóm, W64, epoch cố định và bảo đảm có token mask trong batch là các thay đổi được công bố ở đây. Điểm cửa sổ là điểm frame lớn nhất ($\max_{i\in\mathcal{W}_k} s_i$), không phải kết quả định vị frame. Phép gộp cực đại này nhạy với cực trị đơn lẻ trong 64 frame: nếu một số frame validation nhận điểm cao khiến giá trị tối đa gần 1,0, ngưỡng chọn trên nguồn sẽ bị ép sát biên cực đoan (chẳng hạn tại Set 1 seed 42 ngưỡng nguồn suy biến về $8{,}34\times 10^{-16}$ sau làm phẳng tập trung quanh cực trị, dẫn đến FAR đích $99{,}84\%$ ở Điều kiện B) hoặc sụp đổ recall ngay trên xe quen (Điều kiện A chỉ đạt recall trung bình 0,3843).

CANLP~\cite{balasubramanian2025canlp} được thích ứng thành char TF-IDF unigram, tối đa 256 bigram và ID/2048, tiếp theo Dense 128/64 với dropout 0,15 và hai lớp đầu ra. Bản PyTorch dùng Adam 0,001, batch 512, 30 epoch, nhãn frame gốc và max score/W64. TF-IDF fit trên các frame thuộc mẫu huấn luyện nguồn. Split nguồn theo nhóm, không xóa trùng, nhãn nhị phân và epoch cố định thay cho lựa chọn checkpoint trong công bố gốc; tên báo cáo là CANLP-char-DNN adapted.

CrySyS-AssocRules/W64 lấy implementation association rules trong framework~\cite{koltai2026trust}, fit chỉ benign nguồn. Độ dài/stride 64/64 thay 900/450 của implementation tham chiếu; không ghép quan hệ qua khoảng trống giữa mẫu được chọn. Giữ k-cluster mặc định 300, distance threshold 0,3 và itemset tối đa 3 khi học, 2 khi chấm. Đây là baseline được thích ứng từ framework, không phải tuyên bố tái lập nguyên trạng một phương pháp khác có tên gần giống. Phiên bản mã nguồn của các phương pháp đối thủ được cố định chính xác theo commit Git lưu trữ tại Phụ lục~\ref{sec:app-provenance}.

Các điều kiện supervision và ngân sách tính toán khác nhau: Transformer học nhãn cửa sổ, CANBERT+ có thêm pretrain benign và nhãn frame, CANLP học nhãn frame, AssocRules chỉ học benign. Vì vậy đây là so sánh pipeline dưới giao thức dữ liệu/đánh giá chung, không phải ablation cùng ngân sách hay phép xếp hạng trực tiếp các điểm công bố gốc. Mọi bản thích ứng phải giữ tên tương ứng trong bảng.

\subsubsection{Ngưỡng, ghép cặp, tăng tốc và giới hạn diễn giải}
Ngưỡng được chọn từ validation nguồn để tối đa recall trong ngân sách FAR 100/100.000 cửa sổ benign nguồn. Không hiệu chỉnh bằng nhãn đích; FAR đích có thể vượt ngân sách. Báo recall cùng FAR, F1 lớp tấn công, AP và số đếm TP/FP/TN/FN. Max frame score/W64 chỉ đồng nhất đơn vị quyết định, không chứng minh nhãn supervision hoặc chi phí các phương pháp bằng nhau.

Phép so chính lấy Structural trừ đối thủ trong cùng set và seed. Trung bình seed trước trong từng set, rồi trung bình ngang nhau bốn set. B và D được phân tích riêng; A và C vẫn phải báo. Bootstrap ghép cặp lấy lại toàn capture file và tính lại từ số đếm; khoảng này mô tả biến thiên có điều kiện trên các file quan sát được, không phải khoảng tin cậy cho quần thể xe. Bốn set dùng lại xe, các cửa sổ tương quan và chronology vật lý chưa xác minh là những giới hạn còn lại.

Bốn phương pháp neural chạy trên RTX 5060; AssocRules chạy CPU bằng backend cache lời gọi chính xác. Backend giữ thuật toán học/score gốc, cache theo cặp ID--payload và giữ nguyên thứ tự cộng ở kiểm tra phân phối. Thực nghiệm pilot $k=2$ trên tập nguồn đã kiểm chứng sự trùng khớp tuyệt đối về score, rule và centroid, giúp tăng tốc chấm điểm khoảng 8,3 lần; đây là kiểm thử phần mềm, không chứng minh mức tăng tốc tương đương ở $k=300$ đầy đủ hay cải thiện chất lượng phát hiện. Ngoài ra, việc lấy mẫu reservoir $1.000$ cửa sổ/lớp/tệp ở tập train kết hợp với cửa sổ ngắn $W=64$ làm tăng độ thưa của itemset; khi chấm điểm trên tập validation nguồn đầy đủ, các cặp chuyển tiếp hiếm chưa xuất hiện trong mẫu train bị gán điểm bất thường tối đa bằng 1,0 vượt quá ngân sách 100/100.000, buộc quy tắc hiệu chuẩn nguồn chọn ngưỡng kế cận trên \code{nextafter} ($\tau = 1{,}0000000000000002$ trên toàn bộ 12 lượt chạy), dẫn đến dự đoán toàn benign (Recall = 0 và FAR = 0 trên cả bốn điều kiện A--D và validation). Hiện tượng suy biến ngưỡng này cho thấy sự phụ thuộc của luật kết hợp vào kích thước cửa sổ và độ phủ mẫu train, và được bóc tách riêng khi so sánh với các mô hình mạng nơ-ron tại Mục~\ref{sec:comparison-results}. Thời gian fit trong artifact không bao gồm toàn bộ đọc dữ liệu và đánh giá, không được đổi tên thành độ trễ online.

Bốn kết quả GPU Set 1/seed 42 được tái sử dụng sau khi xác minh hash, môi trường và cấu hình; manifest gốc và lineage riêng được giữ nguyên. Việc chia lịch CPU/GPU không thay đổi phương pháp khoa học.
% END COMPARISON METHOD
Seed và môi trường được ghi rõ, nhưng backend attention CUDA có cảnh báo thuật toán không xác định với chế độ warn-only; không bảo đảm huấn luyện lại giống từng bit trên mọi máy. Khóa luận lưu checkpoint, dự đoán và hash của từng lượt thực tế; ba seed mô tả biến thiên quan sát, không loại bỏ giới hạn tính xác định hoặc tạo thêm xe độc lập.

\subsection{Ngưỡng quyết định, hệ thống độ đo và thiết kế kiểm định}
Ngưỡng mặc định 0,5 được báo song song với ngưỡng source-calibrated. Ngưỡng hiệu chuẩn tối đa hóa recall validation với FAR quan sát không vượt ngân sách; khi hòa chọn ít FP hơn, rồi ngưỡng cao hơn. Các score bằng nhau được xử lý cùng nhóm, không tách tùy ý để thỏa ngân sách. Nếu không có lựa chọn phù hợp thì ngưỡng trên score lớn nhất cho quyết định toàn benign là lựa chọn khả thi và phải công khai recall 0.

Với $N_+=TP+FN$ và $N_-=TN+FP$:
\begin{align}
P&=TP/(TP+FP), & R&=TP/N_+,\\
F_1&=2TP/(2TP+FP+FN), & \operatorname{FAR}_{100k}&=10^5FP/N_-.
\end{align}
Khi $N_-=0$, FAR là N/A. Khi không có positive ground truth, attack metrics không dùng để kết luận phát hiện. Precision khi không có cảnh báo là N/A; nếu có attack nhưng không phát hiện, recall và F1 bằng 0. AP được tính từ continuous scores khi cả hai lớp hiện diện; không thay bằng F1 khi thiếu scores hoặc thiếu lớp. Chỉ số diện tích dưới đường cong Precision--Recall (PR-AUC) được tính đồng nhất theo Average Precision (AP), phản ánh đúng trung bình có trọng số của các mức precision theo bước nhảy recall thay vì xấp xỉ hình thang gián đoạn.

Ngưỡng chỉ được lựa chọn một lần từ nguồn, sau đó giữ nguyên cho A--D và external tương thích. FAR mục tiêu trên nguồn không bảo đảm FAR đích. Độ phân giải nhỏ nhất của FAR thực nghiệm là $10^5/N_-$; do đó cần báo số mẫu và tránh suy luận ngân sách cực thấp từ validation quá nhỏ.

Danh mục các phép thử cắt bỏ (ablation) và câu hỏi khoa học tương ứng được hệ thống hóa tại Bảng~\ref{tab:ablations}.
\begin{longtable}{P{4.6cm}P{9.2cm}}
\caption{Các đối chứng và câu hỏi được kiểm tra}\label{tab:ablations}\\\toprule
Đối chứng & Mục tiêu\\\midrule\endfirsthead\caption[]{(tiếp theo)}\\\toprule Đối chứng & Mục tiêu\\\midrule\endhead
Raw vs raw-minus-ID & Cô lập loại bỏ 11 bit ID trong feature gốc\\
Raw-plus-structural vs raw & Kiểm tra thêm history/structure khi vẫn giữ ID\\
Structural vs raw-plus-structural & Kiểm tra ID trên nền feature phong phú hơn\\
Structural-minus-delta & Vai trò biến thiên payload và cờ lịch sử\\
Structural-minus-local & Vai trò tần suất và hạng ID cục bộ\\
Structural-minus-transition & Vai trò tần suất bigram\\
Structural-minus-payload & Bỏ byte tuyệt đối, giữ DLC/mask và history\\
Structural-minus-rank-W & Bỏ riêng chiều 28 của content, giữ các thống kê khác\\
ID-only / raw-minus-ID & Giới hạn từng nhóm nội dung; timing-only không áp dụng\\
32/64/128 frame & Độ nhạy kích thước và thời gian chờ cửa sổ\\\bottomrule
\end{longtable}
Probe giữ nguyên encoder raw/structural đã huấn luyện. Dữ liệu chẩn đoán được chia theo nhóm bản ghi; cân bằng ô xe $\times$ nhãn tấn công trong mỗi phía để giảm việc đoán xe từ prevalence tấn công. Một LR học dự đoán xe hoặc attack từ embedding. Probe chỉ phục vụ phân tích sau khi đóng băng IDS, không chọn checkpoint/ngưỡng bằng target. Độ chính xác cơ hội là $1/V$ khi $V$ xe được cân bằng.

Kết quả probe được báo cùng embedding hằng/ngẫu nhiên làm đối chứng năng lực của bộ giải mã và attack-probe để kiểm tra việc giảm thông tin xe có đồng thời làm mất tín hiệu phát hiện hay không. Nguyên tắc control tasks được Hewitt và Liang đề xuất trong nghiên cứu biểu diễn ngôn ngữ~\cite{hewitt2019probes}; vận dụng sang CAN ở đây là lựa chọn thiết kế được kiểm tra bằng probe trong khóa luận.

Ba seed phản ánh biến thiên khởi tạo và thứ tự tối ưu, không tạo ba tập xe độc lập. Báo trung bình và độ lệch chuẩn theo seed với cùng phép chia. Bootstrap ghép cặp lấy mẫu lại toàn bản ghi và dùng cùng mẫu cho hai mô hình. Nếu quá ít nhóm, báo thiếu căn cứ thay vì tạo CI có vẻ chắc chắn. Với metadata mức file, CI chỉ là mô tả có điều kiện vì các file có thể dùng chung chuyến lái.

Probe dùng LR với $C=1$, tối đa 2.000 vòng, chuẩn hóa fit trên probe-train và không chọn siêu tham số theo probe-test. Cùng các cửa sổ đã cân bằng được dùng cho raw và structural. Đối chứng gồm embedding hằng, Gaussian độc lập giữa train/test và hoán vị nhãn probe-train; hai đối chứng ngẫu nhiên lặp năm seed định trước. Nhãn test giữ nguyên. Các đối chứng được báo riêng, không chọn seed probe đẹp nhất hoặc gọi đây là tái lập nguyên bản control task của Hewitt--Liang.

Phân tích ghép cặp báo chênh lệch recall, FAR và F1 tại cả hai ngưỡng, lấy structural trừ raw. Bootstrap lấy lại toàn file, sử dụng cùng số lần chọn file cho hai mô hình và tính lại từ ma trận nhầm lẫn. Báo số mẫu bootstrap hợp lệ; mẫu thiếu mẫu số của metric bị loại có ghi nhận. Dưới ba file không xuất khoảng. So sánh trung bình bốn set thực hiện đúng thứ tự trung bình seed trong set rồi cho mỗi set trọng số bằng nhau; không dùng số cửa sổ làm trọng số xe.

\subsection{Môi trường tính toán và cơ chế đảm bảo tái lập}
Run manifest lưu schema version, config, phiên bản Python/thư viện, thiết bị và hash mã nguồn. Data manifest lưu đường dẫn tương đối, kích thước và SHA-256 toàn file. Mỗi checkpoint có số chiều, window size và ngưỡng; mỗi file dự đoán giữ window index, nhãn, score và timestamp đầu/cuối. Nhằm đảm bảo tính bất biến của kết quả thực nghiệm, hệ thống lưu trữ thiết lập cơ chế khóa ghi đè đối với các thư mục thử nghiệm đã hoàn tất.

Attention có chi phí phụ thuộc bậc hai theo $W$, còn thống kê cửa sổ và cập nhật history tuyến tính theo số frame. Đo runtime cần bao gồm parser, feature extraction, inference và chờ đủ cửa sổ; đo riêng GPU batch throughput không tương đương độ trễ online. Nghiên cứu tập trung vào hiệu năng phân tách bất thường và độ trễ xử lý thực tế trên thiết bị thử nghiệm tiêu chuẩn; các khẳng định về thông lượng cực đại trên phần cứng nhúng chuyên dụng cần được thẩm định độc lập trong các nghiên cứu phần cứng tương lai.
Manifest cuối lưu hash checkpoint, metadata, bảng số và file dự đoán. Bộ tổng hợp từ chối run chưa hoàn tất, đầu ra bị đổi, mã/giao thức khác hoặc ô set--seed--model lặp/thiếu trong run. Báo cáo độ phủ phân biệt một run hoàn tất với đủ ma trận nghiên cứu. Lệnh \code{run_comparison.py} kiểm tra và bỏ qua các đơn vị hoàn tất tương thích; lần bị ngắt được giữ và chạy lại trong thư mục attempt mới, không tiếp tục giả định từ epoch dở dang.

Runtime của nhánh content được đo riêng trên tiền tố validation nguồn trên máy trạm thực nghiệm trang bị CPU AMD Ryzen 5 5600X (6 nhân/12 luồng @ 3,7 GHz, 16 GB DDR4 RAM) và GPU NVIDIA GeForce RTX 5060 (8 GB VRAM, hệ điều hành Windows 11): batch một, 20 cửa sổ warmup và 300 cửa sổ đo trong ba lần lặp. Phép đo gồm đọc CSV, chuyển đổi/kiểm tra, tính cả hai biểu diễn và inference. Không đo thời gian thu đủ cửa sổ hoặc độ trễ theo sự kiện; kết quả ở chương thực nghiệm không chứng nhận deadline ECU.

\section{Đánh giá chuyển giao zero-shot và chẩn đoán biểu diễn cấu trúc}
\subsection{Đánh giá hiệu năng phát hiện và báo động giả khi chuyển giao phương tiện (RQ1)}\label{sec:comparison-results}
B kiểm tra xe lạ với tấn công quen; D đồng thời đổi xe và kiểu tấn công. Ngưỡng nguồn được giữ cố định; ngân sách nguồn 100/100.000 không bảo đảm FAR đích. Các điểm công bố gốc không nằm trong bảng này.
\begin{longtable}{P{1.0cm}P{4.4cm}P{1.4cm}P{3.0cm}P{1.4cm}P{1.4cm}}
\caption{Kết quả chính W64; ngưỡng nguồn; FAR tính trên 100.000 cửa sổ lành (kèm tỷ lệ \% tương đương $\operatorname{FAR}_{100k}/1.000$)}\label{tab:comparison-main}\\\toprule
ĐK & Phương pháp & Recall & FAR /100k (\%) & F1 & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
ĐK & Phương pháp & Recall & FAR /100k (\%) & F1 & AP\\\midrule
\endhead
A & Raw TF & 0.6167 & 115.77 (0.12\%) & 0.7258 & 0.7312\\
A & Structural TF & 0.5886 & 81.67 (0.08\%) & 0.7072 & 0.7483\\
A & CANBERT+ adapted & 0.3843 & 79.27 (0.08\%) & 0.4576 & 0.5335\\
A & CANLP-char-DNN adapted & 0.1228 & 28.37 (0.03\%) & 0.1789 & 0.5482\\
A & CrySyS-AssocRules/W64$^{\dagger}$ & 0.0000 & 0.00 (0.00\%) & 0.0000 & 0.3338\\
B & Raw TF & 0.8541 & 65301.41 (65.30\%) & 0.3000 & 0.3781\\
B & Structural TF & 0.7383 & 52461.46 (52.46\%) & 0.2435 & 0.5554\\
B & CANBERT+ adapted & 0.6395 & 64843.85 (64.84\%) & 0.0593 & 0.0970\\
B & CANLP-char-DNN adapted & 0.2854 & 29695.88 (29.70\%) & 0.0329 & 0.0542\\
B & CrySyS-AssocRules/W64$^{\dagger}$ & 0.0000 & 0.00 (0.00\%) & 0.0000 & 0.0591\\
C & Raw TF & 0.2101 & 91.92 (0.09\%) & 0.2314 & 0.2661\\
C & Structural TF & 0.2230 & 75.82 (0.08\%) & 0.2600 & 0.2928\\
C & CANBERT+ adapted & 0.1037 & 62.54 (0.06\%) & 0.1461 & 0.2218\\
C & CANLP-char-DNN adapted & 0.0020 & 405.49 (0.41\%) & 0.0038 & 0.2373\\
C & CrySyS-AssocRules/W64$^{\dagger}$ & 0.0000 & 0.00 (0.00\%) & 0.0000 & 0.1732\\
D & Raw TF & 0.6614 & 67982.89 (67.98\%) & 0.1213 & 0.1648\\
D & Structural TF & 0.6445 & 54643.37 (54.64\%) & 0.2069 & 0.3357\\
D & CANBERT+ adapted & 0.5549 & 54513.45 (54.51\%) & 0.0644 & 0.1311\\
D & CANLP-char-DNN adapted & 0.2491 & 25452.19 (25.45\%) & 0.0119 & 0.0901\\
D & CrySyS-AssocRules/W64$^{\dagger}$ & 0.0000 & 0.00 (0.00\%) & 0.0000 & 0.0912\\
\bottomrule
\multicolumn{6}{P{13.4cm}}{\footnotesize $^{\dagger}$ Ngưỡng chọn từ validation nguồn suy biến tại $1{,}0000000000000002$ (dự đoán toàn benign, $R=0, \text{FAR}=0$); xem chi tiết ở Mục~\ref{subsec:assoc-degenerate}.}
\end{longtable}
Ở B, chênh lệch recall Structural trừ Raw là $-11{,}59$ điểm phần trăm; mức tăng AP ghép cặp là $+0{,}1774$ (+17,74 điểm phần trăm; chênh lệch giữa hai giá trị trung bình toàn bảng là $0{,}5554 - 0{,}3781 = +0{,}1773$). FAR giảm $12{,}84$ điểm phần trăm nhưng vẫn bằng $52{,}46\%$ ($52.461{,}46/100\text{k}$). Ở D, tại ngưỡng nguồn, Structural đạt AP $0{,}3357$ (trung bình 4 set; $0{,}3404$ khi khử lặp 3 xe đích phân biệt, so với Raw $0{,}1648$ và $0{,}1799$ tương ứng), recall đổi $-1{,}69$ điểm phần trăm và FAR còn $54{,}64\%$ ($43{,}60\%$ khi khử lặp 3 xe); cần lưu ý giá trị AP $0{,}3411$ ở điều kiện D là số liệu sau khi áp dụng hiệu chuẩn nền lành tính $K=500$ (Mục~\ref{sec:benign-calibration}). Khi khử lặp trọng số xe đích Subaru Forester (trung bình 3 xe đích phân biệt với trọng số $1/3, 1/6, 1/6, 1/3$): ở B, Structural đạt recall $0{,}6610$, FAR $41{,}26\%$ ($41.263{,}81/100\text{k}$), F1 $0{,}2891$, AP $0{,}5510$, so với Raw đạt recall $0{,}8722$, FAR $60{,}23\%$, F1 $0{,}3629$, AP $0{,}4281$; ở D, Structural đạt AP $0{,}3404$ (so với Raw $0{,}1799$), FAR $43{,}60\%$ (so với Raw $63{,}69\%$). Như vậy, dù cân bằng lại trọng số 3 xe đích làm nới rộng khoảng cách recall giữa Structural và Raw tại ngưỡng nguồn, ưu thế xếp hạng AP và mức giảm FAR của Structural vẫn giữ nguyên nhất quán. Ngoài ra, hai đối thủ thích ứng gặp khó khăn ngay cả trong miền quen (Điều kiện A): \code{CANBERT+} chỉ đạt recall $0{,}3843$ và \code{CANLP-char-DNN} đạt recall $0{,}1228$ do nhạy cảm của cơ chế gộp cực đại theo frame và mất cân bằng đặc trưng TF-IDF dưới ngưỡng nghiêm ngặt từ validation nguồn. Giả thuyết chính tăng recall trung bình ở B không được ủng hộ; AP tăng phản ánh chất lượng xếp hạng, không khắc phục báo động giả cao hoặc thay thế tiêu chí chính. Mẫu số cửa sổ kiểm thử dùng chung giữa năm phương pháp được thống kê chi tiết tại Bảng~\ref{tab:comparison-counts}, và chênh lệch ghép cặp chi tiết giữa Structural và các đối thủ nơ-ron hoạt động được trình bày tại Bảng~\ref{tab:comparison-paired}.
\begin{table}[htbp]
\centering
\small
\caption{Mẫu số cửa sổ kiểm thử dùng chung giữa năm phương pháp và ba seed (Tấn công / Lành)}\label{tab:comparison-counts}
\vspace{2pt}
\begin{tabular}{lcccc}
\toprule
\textbf{Tập dữ liệu} & \textbf{Điều kiện A} & \textbf{Điều kiện B} & \textbf{Điều kiện C} & \textbf{Điều kiện D} \\
\midrule
\code{set\_01} & 2.987 / 86.114 & 8.430 / 92.315 & 8.636 / 126.284 & 2.088 / 204.476 \\
\code{set\_02} & 2.088 / 204.476 & 2.578 / 129.375 & 1.359 / 188.481 & 1.104 / 73.734 \\
\code{set\_03} & 9.775 / 124.217 & 8.834 / 98.259 & 6.998 / 140.620 & 25.140 / 82.604 \\
\code{set\_04} & 25.140 / 82.604 & 13.782 / 258.213 & 8.834 / 98.259 & 13.615 / 114.249 \\
\bottomrule
\end{tabular}
\end{table}
\begin{longtable}{P{1.1cm}P{4.7cm}P{1.6cm}P{2.8cm}P{1.4cm}P{1.4cm}}
\caption{Chênh lệch ghép cặp: Structural trừ các đối thủ nơ-ron hoạt động (trọng số 4 set ngang nhau; FAR trên 100.000 và điểm phần trăm \%)}\label{tab:comparison-paired}\\\toprule
ĐK & Đối thủ so sánh & $\Delta R$ & $\Delta$ FAR /100k (\%pt) & $\Delta$ F1 & $\Delta$ AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
ĐK & Đối thủ so sánh & $\Delta R$ & $\Delta$ FAR /100k (\%pt) & $\Delta$ F1 & $\Delta$ AP\\\midrule
\endhead
B & Raw TF & -0.1159 & -12839.95 (-12.84) & -0.0565 & 0.1774\\
B & CANBERT+ adapted & 0.0988 & -12382.39 (-12.38) & 0.1842 & 0.4584\\
B & CANLP-char-DNN adapted & 0.4529 & 22765.57 (+22.77) & 0.2106 & 0.5012\\
D & Raw TF & -0.0169 & -13339.51 (-13.34) & 0.0856 & 0.1709\\
D & CANBERT+ adapted & 0.0896 & 129.92 (+0.13) & 0.1425 & 0.2046\\
D & CANLP-char-DNN adapted & 0.3953 & 29191.18 (+29.19) & 0.1950 & 0.2456\\
\midrule
\multicolumn{6}{P{13.4cm}}{\footnotesize \textit{Ghi chú đối chứng suy biến:} \code{CrySyS-AssocRules/W64} bị loại khỏi bảng chênh lệch hiệu quả do ngưỡng nguồn suy biến ở $1{,}0000000000000002$ ($\text{Recall}=0{,}0000, \text{FAR}=0{,}00$ trên mọi tập A--D); việc lấy Structural trừ $0$ ($\Delta R = +0{,}7383$, $\Delta\text{FAR}=+52.461{,}46$ ở B; $\Delta R = +0{,}6445$, $\Delta\text{FAR}=+54.643{,}37$ ở D) chỉ mang ý nghĩa số học và không đại diện cho so sánh với một bộ phát hiện đang hoạt động. Tuy nhiên, xét trên chỉ số độc lập ngưỡng AP, Structural vẫn vượt trội CrySyS-AssocRules/W64 ($\Delta\text{AP}=+0{,}4964$ ở B và $+0{,}2445$ ở D).}\\
\bottomrule\end{longtable}
\begin{figure}[htbp]
\centering
\begin{subfigure}[b]{0.48\textwidth}
  \centering
  \includegraphics[width=\linewidth]{figs/comparison_v1_vi_Recall.png}
  \caption{Recall}\label{subfig:comp-recall}
\end{subfigure}\hfill
\begin{subfigure}[b]{0.48\textwidth}
  \centering
  \includegraphics[width=\linewidth]{figs/comparison_v1_vi_FAR_per_100k.png}
  \caption{FAR trên $100.000$ cửa sổ}\label{subfig:comp-far}
\end{subfigure}
\vskip 6pt
\begin{subfigure}[b]{0.48\textwidth}
  \centering
  \includegraphics[width=\linewidth]{figs/comparison_v1_vi_Attack_F1.png}
  \caption{Attack F1}\label{subfig:comp-f1}
\end{subfigure}\hfill
\begin{subfigure}[b]{0.48\textwidth}
  \centering
  \includegraphics[width=\linewidth]{figs/comparison_v1_vi_AP.png}
  \caption{Average Precision (AP)}\label{subfig:comp-ap}
\end{subfigure}
\caption{Kết quả W64 theo điều kiện A--D dưới ngưỡng nguồn (trọng số 4 set ngang nhau).}\label{fig:comparison-four-metrics}
\end{figure}
\FloatBarrier
Diễn biến so sánh trực quan giữa các phương pháp trên cả bốn chỉ số (Recall, FAR, F1, AP) được thể hiện qua các đồ thị tại Hình~\ref{fig:comparison-four-metrics}.
Recall Structural cao hơn Raw sau trung bình seed chỉ ở một trong bốn set cho cả B và D; do đó không kết luận cải thiện recall nhất quán. Ngoài ra, độ lệch chuẩn giữa 3 seed tại Set 1 điều kiện B của Structural rất lớn ($\pm 0{,}3875$): tách chi tiết từng seed cho thấy ở seed 42 ngưỡng chọn trên validation nguồn bị đẩy lên $\tau=0{,}9904$ (khiến recall chỉ đạt $0{,}0522$ dù AP vẫn là $0{,}6880$), trong khi seed 43 ($\tau=0{,}00084$) đạt recall $0{,}7721$ (AP $0{,}9245$) và seed 44 ($\tau=0{,}0639$) đạt recall $0{,}6606$ (AP $0{,}9420$). Biến động này minh họa trực tiếp tính nhạy cảm của phép chọn ngưỡng ở vùng đuôi $0{,}1\%$ FAR khi không hiệu chuẩn xác suất. Về đối thủ, \code{CANBERT+} ở Set 1 seed 42 sụp đổ ngưỡng về $8{,}34\times 10^{-16}$ làm FAR đạt $99{,}84\%$ ở B (trung bình FAR Set 1 là $61.471{,}41/100\text{k}$), còn \code{CANLP-char-DNN} cho recall/FAR bằng $0/0$ trên cả Set 3 và Set 4 do ngưỡng nguồn vượt vùng score trên xe đích.

Đáng chú ý, phân tích theo cặp xe (chi tiết tại Bảng~\ref{tab:comparison-sets} và khoảng bootstrap 95\% tại Bảng~\ref{tab:comparison-ci} ở Phụ lục~\ref{app:reproducibility}) chỉ ra sự phân hóa sâu sắc giữa chuyển giao cùng nhà sản xuất và khác nhà sản xuất: ở Set 1 (chuyển giao nội bộ hãng Chevrolet: Impala sang Silverado), Structural kiểm soát FAR đích cực kỳ tốt ở mức 32,14/100.000 (0,032\%), thấp hơn nhiều so với Raw (168,99/100.000). Ngược lại, ở Set 2, 3 và 4 (chuyển giao chéo giữa Chevrolet và Subaru), phân phối điểm số nền của cả Raw lẫn Structural bị dịch chuyển mạnh sang bên phải ngưỡng $\tau_{\text{source}}$, làm bùng nổ FAR đích lên 37.700--100.000/100.000 (37,7\%--100\%). Dù vậy, về chất lượng xếp hạng (AP), Structural vượt trội hơn Raw trên cả 4/4 set ở điều kiện B, khẳng định lợi thế phân tách bất thường ổn định của biểu diễn cấu trúc khi chưa tính đến sai lệch ngưỡng. Độ lệch chuẩn seed mô tả khởi tạo; bootstrap ghép cặp lấy lại toàn capture và tính từ số đếm. Khoảng bootstrap là mô tả có điều kiện trên file quan sát, không phải CI cho quần thể xe; không lấy trung bình các đầu mút CI để suy ra CI đa xe.

\subsubsection{Kiểm chứng độ nhạy theo tính đơn điệu timestamp}\label{subsec:monotonic-sensitivity}
Để kiểm chứng nhận định rằng 12.527 điểm đi lùi dưới mili-giây ở 100/236 tệp CTT không làm biến chất biểu diễn \code{Structural 30D} vốn tính toán dựa trên thứ tự dòng CSV, khóa luận tách kết quả đánh giá sau hiệu chuẩn ($K=500$, ngân sách $1{,}0\%$) thành hai nhóm độc lập: 136 tệp có timestamp đơn điệu không giảm tuyệt đối (\textit{monotonic}) và 100 tệp có ít nhất một lần đi lùi (\textit{non-monotonic}). Trên điều kiện B, Structural (Structural+MixStyle) đạt $\text{AP}=0{,}6980$ ($0{,}7188$), recall $55{,}83\%$ ($62{,}53\%$), FAR $0{,}75\%$ ($0{,}90\%$) trên nhóm \textit{monotonic}, so với $\text{AP}=0{,}3548$ ($0{,}3560$), recall $30{,}74\%$ ($31{,}46\%$), FAR $0{,}94\%$ ($1{,}30\%$) trên nhóm \textit{non-monotonic}. Tuy nhiên, khi phân rã từng set cho thấy sự chênh lệch này bắt nguồn từ thành phần set và họ tấn công trong từng nhóm chứ không phải do hiện tượng đi lùi timestamp: chẳng hạn ở Set 3 điều kiện B, nhóm \textit{non-monotonic} (4 tệp) lại đạt hiệu năng cao hơn hẳn nhóm \textit{monotonic} (6 tệp): Structural+MixStyle đạt recall $76{,}61\%$, AP $0{,}9233$ so với $50{,}15\%$, AP $0{,}7221$; ngược lại ở Set 1 điều kiện B, nhóm \textit{non-monotonic} (6 tệp, chứa toàn bộ các kịch bản tấn công vật lý kín đáo như \code{force-neutral}, \code{rpm}, \code{standstill}) cho AP thấp ($0{,}008$), trong khi nhóm \textit{monotonic} (2 tệp \code{DoS}) đạt AP $0{,}9913$. Kết hợp với bằng chứng $0/12.527$ bước nhảy $>1\text{ s}$ và $99{,}84\%$ sai lệch $\le 1\text{ ms}$, điều này xác nhận thứ tự dòng CSV bảo toàn cấu trúc cục bộ của lưu lượng CAN.

Nhằm kiểm chứng trực diện ảnh hưởng của đặc trưng thời gian khi loại bỏ hoàn toàn các tệp nhiễu đồng hồ, khóa luận huấn luyện và đánh giá bổ sung cặp thực nghiệm có đối chứng \code{Content (28D/30D)} so với \code{Timed (29D/32D, bổ sung }$\Delta t$\code{ và }$\Delta t_{\text{ID}}$\code{)} chỉ trên đúng $136/236$ tệp CTT đơn điệu không giảm tuyệt đối ($\text{timestamp\_inversions}=0$ ở tất cả train, validation và A--D qua cả 4 set $\times$ 3 seed = 48 lượt huấn luyện; Bảng~\ref{tab:monotonic-timed-vs-content}). Bộ trích xuất \code{Timed} vector hóa đã được kiểm chứng khớp từng bit (\textit{max diff} $= 0{,}00$) với \code{WindowExtractor(64, 'timed')}.

\Needspace{18\baselineskip}
{\small\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{P{2.8cm}P{1.7cm}P{0.7cm}P{2.1cm}P{1.5cm}P{1.4cm}P{2.1cm}}
\caption{Đối chứng trực tiếp \code{Content} (28D/30D) so với \code{Timed} (29D/32D) trên 136/236 tệp CTT đơn điệu nghiêm ngặt (4 set $\times$ 3 seed; trong ngoặc là trung bình 3 xe đích)}\label{tab:monotonic-timed-vs-content}\\\toprule
Nhánh / Mô hình & Ngưỡng & ĐK & Recall (3-xe) & FAR (\%) & F1 & AP (3-xe)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Nhánh / Mô hình & Ngưỡng & ĐK & Recall (3-xe) & FAR (\%) & F1 & AP (3-xe)\\\midrule
\endhead
Content Raw (28D) & Nguồn & A & 0.7410 & 0.065\% & 0.8390 & 0.8923\\
Timed Raw (29D) & Nguồn & A & 0.6371 & 0.108\% & 0.7467 & 0.8399\\
Content Structural (30D) & Nguồn & A & 0.6100 & 0.088\% & 0.7217 & 0.8182\\
\textbf{Timed Structural (32D)} & Nguồn & A & \textbf{0.8405} & 0.085\% & \textbf{0.8996} & \textbf{0.9638}\\
\midrule
Content Raw & Nguồn & B & 0.9206 (0.8973) & 76.38\% & 0.2624 & 0.5377 (0.6070)\\
Timed Raw & Nguồn & B & 0.8249 (0.8086) & 65.88\% & 0.2560 & 0.5788 (0.6501)\\
Content Structural & Nguồn & B & 0.6479 (0.5808) & 41.16\% & 0.2360 & 0.5786 (0.6123)\\
\textbf{Timed Structural} & Nguồn & B & 0.8123 (\textbf{0.8711}) & \textbf{2.46\%} & \textbf{0.8274} & \textbf{0.9359} (\textbf{0.9508})\\
Content Raw & Nguồn & C & 0.1592 & 0.081\% & 0.1933 & 0.3077\\
Timed Raw & Nguồn & C & 0.1808 & 0.065\% & 0.2295 & 0.3561\\
Content Structural & Nguồn & C & 0.1715 & 0.078\% & 0.2164 & 0.3699\\
\textbf{Timed Structural} & Nguồn & C & \textbf{0.5015} & \textbf{0.065\%} & \textbf{0.5212} & \textbf{0.7537}\\
\midrule
Content Raw & $K=500$, 1.0\% & B & 0.4540 (0.5190) & 0.67\% & 0.5192 & 0.5424 (0.6119)\\
Timed Raw & $K=500$, 1.0\% & B & 0.4857 (0.5442) & 0.70\% & 0.5585 & 0.5850 (0.6572)\\
Content Structural & $K=500$, 1.0\% & B & 0.4264 (0.4689) & 2.24\% & 0.5225 & 0.5857 (0.6185)\\
\textbf{Timed Structural} & $K=500$, 1.0\% & B & \textbf{0.7460} (\textbf{0.8035}) & \textbf{0.63\%} & \textbf{0.8295} & \textbf{0.9451} (\textbf{0.9575})\\
Content Raw & $K=500$, 1.0\% & D & 0.1009 (0.1308) & 1.20\% & 0.1368 & 0.1990 (0.2287)\\
Timed Raw & $K=500$, 1.0\% & D & 0.1192 (0.1544) & 0.93\% & 0.1635 & 0.2325 (0.2684)\\
Content Structural & $K=500$, 1.0\% & D & 0.2537 (0.3065) & 0.62\% & 0.3213 & 0.3904 (0.4190)\\
\textbf{Timed Structural} & $K=500$, 1.0\% & D & \textbf{0.4036} (\textbf{0.4341}) & \textbf{0.28\%} & \textbf{0.4742} & \textbf{0.7219} (\textbf{0.6736})\\
\bottomrule\end{longtable}}

Kết quả trên tập con đơn điệu nghiêm ngặt tại Bảng~\ref{tab:monotonic-timed-vs-content} khẳng định hai điểm quan trọng: (1) Lý do loại bỏ $\Delta t$ khỏi ma trận chính hoàn toàn đến từ tính liêm chính dữ liệu trước 100/236 tệp bị nhiễu đi lùi đồng hồ chứ không nhằm né tránh $\Delta t$ --- trái lại, khi kết hợp trên bus có timestamp đơn điệu sạch, bộ đôi cấu trúc không gian--thời gian \code{Timed Structural (32D)} tạo bước nhảy vượt bậc ở mọi điều kiện chuyển giao ($\text{AP}_B=0{,}9451$, recall sau hiệu chuẩn $K=500, 1{,}0\%$ đạt $74{,}60\%$ [$80{,}35\%$ khử lặp 3 xe] tại FAR $0{,}63\%$, và $\text{AP}_D=0{,}7219$, $\text{AP}_C=0{,}7537$), giảm FAR ngay tại ngưỡng nguồn ở điều kiện B từ $41{,}16\%$ xuống $2{,}46\%$, trong khi \code{Timed Raw (29D)} chỉ tăng nhẹ $\text{AP}_B$ từ $0{,}5377$ lên $0{,}5788$ với FAR nguồn vẫn $65{,}88\%$; (2) Ngược lại, nhánh \code{Content (30D)} giữ vai trò cận dưới bảo thủ an toàn trên các luồng dữ liệu thiếu timestamp đáng tin cậy (như 100 tệp CTT có đi lùi hoặc log hex thuần trên bộ ngoại bộ CICIoV2024).
\subsubsection{Điểm vận hành suy biến của AssocRules}\label{subsec:assoc-degenerate}
Cả 12 ngưỡng nguồn là 1,0000000000000002, vượt miền score [0,1]; vì vậy mọi cửa sổ được dự đoán bình thường và recall/FAR đều bằng 0. Đây không phải phát hiện tốt, cũng không phải bằng chứng phương pháp gốc thất bại. Bảng~\ref{tab:assoc-scores} (ở Phụ lục~\ref{app:reproducibility}) mô tả chi tiết score nguồn; phân phối score, số trùng cực đại và số cảnh báo tại ngưỡng giúp giải thích tính khả thi của ngân sách FAR. Chưa có phép đo cô lập nguyên nhân W64, số cluster hay quy tắc phân phối; không suy nguyên nhân chỉ từ hiện tượng.

Tại ngưỡng đúng bằng score cực đại 1, FAR validation nguồn nằm trong khoảng 348,58--4696,34 trên 100.000, đã vượt ngân sách 100. Giảm ngưỡng chỉ có thể tăng số cảnh báo, nên không có ngưỡng hữu hạn trong miền score thỏa ngân sách; ngưỡng ngay trên 1 tạo điểm không cảnh báo. Để kiểm chứng xem hiện tượng này có do việc lấy mẫu reservoir hay không, nghiên cứu thực hiện huấn luyện lại AssocRules trên 5.000 cửa sổ lành tính liên tục của Set 1: tỷ lệ cửa sổ lành tính đạt score $=1{,}0$ trên validation nguồn vẫn là $0{,}44\%$ ($440/100\text{k}$), tiếp tục vượt ngân sách $100/100\text{k}$ và bắt buộc thuật toán chọn ngưỡng suy biến tại $1{,}0000000000000002$. Đáng chú ý, khi đánh giá chất lượng xếp hạng liên tục không phụ thuộc ngưỡng (Average Precision), AssocRules chỉ đạt $\text{AP}_B = 0{,}0591$ và $\text{AP}_D = 0{,}0912$ (so với Structural $0{,}5554$ và $0{,}3357$; $0{,}3404$ khi khử lặp 3 xe). Hơn nữa, trên xe đích lạ (B và D), $100\%$ số cửa sổ có score bằng đúng $1{,}0$ (\code{frac\_score\_1} $=1{,}0000$) do từ vựng ID và chu kỳ truyền tin của xe lạ vi phạm các luật kết hợp khai phá từ nguồn; vì vậy nếu áp dụng hiệu chuẩn nền lành tính $K=500$ trên xe đích, ngưỡng phân vị suy biến về $1{,}0$ và khiến tỷ lệ báo động giả bùng nổ lên $100\%$ ($\text{FAR}=100.000/100\text{k}$). Điều này khẳng định điểm suy biến của AssocRules là giới hạn nội tại của phương pháp dựa trên luật kết hợp tĩnh khi chuyển giao sang phương tiện có từ vựng ID khác biệt.
\subsubsection{Bóc tách quy tắc gộp khung tin trên CANBERT+ và CANLP-char-DNN}\label{subsec:baseline-pooling-ablation}
Để kiểm chứng liệu điểm số thấp của các mô hình nền học theo khung tin trên Bảng~\ref{tab:comparison-main} có xuất phát từ quy tắc gộp cực đại theo cửa sổ (\code{max} qua 64 khung) như đã thảo luận ở Mục~\ref{subsec:assoc-degenerate} hay không, nghiên cứu tái tính toán trực tiếp toàn bộ chuỗi điểm xác suất cấp khung tin (\code{.frames.f32}) đã lưu trữ trên 24 lượt chạy gốc của \code{CANBERT+} và \code{CANLP-char-DNN} với ba quy tắc gộp: \code{max} (mặc định gốc), \code{top8\_mean} (trung bình 8 khung cao nhất), và \code{mean} (trung bình toàn cửa sổ), đồng thời đánh giá luôn chế độ hiệu chuẩn $K=500$ (ngân sách $1{,}0\%$) trên B và D. Bảng~\ref{tab:baseline-pooling-ablation} tổng hợp kết quả.

\Needspace{18\baselineskip}
{\small\setlength{\tabcolsep}{4pt}
\begin{longtable}{P{3.6cm}P{1.7cm}P{0.8cm}P{1.4cm}P{2.2cm}P{1.4cm}P{1.4cm}}
\caption{Ảnh hưởng của quy tắc gộp khung tin lên CANBERT+ và CANLP (trung bình 4 set $\times$ 3 seed từ score cấp khung đã lưu)}\label{tab:baseline-pooling-ablation}\\\toprule
Phương pháp / Chế độ & Pooling & ĐK & Recall & FAR (/100k hay \%) & Attack F1 & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Phương pháp / Chế độ & Pooling & ĐK & Recall & FAR & Attack F1 & AP\\\midrule
\endhead
CANBERT+ (ngưỡng nguồn) & \code{max} & A & 0.3843 & 79.27 /100k & 0.4576 & 0.5335\\
CANBERT+ (ngưỡng nguồn) & \code{top8\_mean} & A & 0.4227 & 88.79 /100k & 0.5076 & 0.5447\\
CANBERT+ (ngưỡng nguồn) & \code{mean} & A & \textbf{0.4229} & 88.77 /100k & \textbf{0.5077} & \textbf{0.5451}\\
CANBERT+ (ngưỡng nguồn) & \code{max} & B & 0.6395 & 64.84\% & 0.0593 & 0.0970\\
CANBERT+ (ngưỡng nguồn) & \code{mean} & B & 0.7334 & 70.99\% & 0.1011 & 0.1636\\
CANBERT+ (ngưỡng nguồn) & \code{max} & C & 0.1037 & 62.54 /100k & 0.1461 & 0.2218\\
CANBERT+ (ngưỡng nguồn) & \code{mean} & C & 0.1069 & 53.24 /100k & 0.1501 & 0.2256\\
CANBERT+ ($K=500$, 1.0\%) & \code{max} & B & 0.2428 & 20.56\% & 0.1078 & 0.0997\\
CANBERT+ ($K=500$, 1.0\%) & \code{mean} & B & 0.1183 & \textbf{1.89\%} & 0.1562 & 0.1665\\
\midrule
CANLP (ngưỡng nguồn) & \code{max} & A & 0.1228 & 28.37 /100k & 0.1789 & 0.5482\\
CANLP (ngưỡng nguồn) & \code{top8\_mean} & A & 0.4122 & 119.45 /100k & 0.5578 & \textbf{0.5907}\\
CANLP (ngưỡng nguồn) & \code{mean} & A & \textbf{0.4125} & 119.35 /100k & \textbf{0.5582} & 0.5898\\
CANLP (ngưỡng nguồn) & \code{max} & B & 0.2854 & 29.70\% & 0.0329 & 0.0542\\
CANLP (ngưỡng nguồn) & \code{mean} & B & 0.6238 & 60.62\% & 0.1085 & 0.1982\\
CANLP (ngưỡng nguồn) & \code{max} & C & 0.0020 & 405.49 /100k & 0.0038 & 0.2373\\
CANLP (ngưỡng nguồn) & \code{mean} & C & 0.1908 & 330.84 /100k & 0.2189 & 0.2836\\
CANLP ($K=500$, 1.0\%) & \code{max} & B & 0.6578 & 68.25\% & 0.0794 & 0.0564\\
CANLP ($K=500$, 1.0\%) & \code{mean} & B & 0.1402 & \textbf{1.77\%} & 0.1835 & 0.2011\\
CANLP ($K=500$, 1.0\%) & \code{mean} & D & 0.1344 & \textbf{0.81\%} & 0.1858 & 0.2236\\
\bottomrule
\multicolumn{7}{P{13.6cm}}{\footnotesize \textit{Ghi chú:} Bảng đối chiếu các cấu hình gộp tiêu biểu; dưới quy tắc \code{mean} ở Điều kiện D (ngưỡng nguồn), \code{CANBERT+} đạt $\text{AP}_D=0{,}1490$ (Recall $0{,}5982$, FAR $61{,}84\%$), và \code{CANLP} đạt $\text{AP}_D=0{,}2201$ (Recall $0{,}3215$, FAR $28{,}64\%$), đều thấp hơn nhiều so với \code{Structural Transformer} ($\text{AP}_D=0{,}3357$ ở ngưỡng nguồn và $0{,}3411$ sau hiệu chuẩn).}\\
\end{longtable}}

Kết quả ở Bảng~\ref{tab:baseline-pooling-ablation} xác nhận hai hiện tượng rõ ràng: (1) Quy tắc \code{max} qua 64 khung khuếch đại các điểm dị biệt đơn lẻ, khiến \code{CANLP} mất ổn định cắt ngưỡng trên ngay chính xe nguồn (đổi sang \code{mean} nâng recall A từ $0{,}1228$ lên $0{,}4125$, C từ $0{,}0020$ lên $0{,}1908$), đồng thời gây bão hòa điểm $1{,}0$ khi hiệu chuẩn $K=500$ (FAR ở B giảm từ $68{,}25\%$ xuống $1{,}77\%$ với \code{mean}); (2) Tuy nhiên, ngay cả sau khi chuyển sang quy tắc \code{mean} tối ưu hơn cho cả hai đối thủ, chất lượng xếp hạng đa xe ở điều kiện B và D của \code{CANBERT+} ($\text{AP}_B=0{,}1636$, $\text{AP}_D=0{,}1490$) và \code{CANLP} ($\text{AP}_B=0{,}1982$, $\text{AP}_D=0{,}2201$) vẫn kém rất xa \code{Structural Transformer} ($0{,}5554$ ở ngưỡng nguồn và $0{,}5607$ sau hiệu chuẩn), cho thấy nút thắt cốt lõi của các đối thủ này là sự phụ thuộc vào từ vựng định danh và dạng thức ký tự của xe nguồn chứ không đơn thuần do hàm gộp.

\subsubsection{Phân bố số lượng cửa sổ dương/âm từng tệp ở Điều kiện B và D}\label{subsec:bd-per-file-counts}
Để làm rõ độ lệch phân bố lớp theo từng capture khi diễn giải các chỉ số gộp và theo tệp ở Bảng~\ref{tab:comparison-main}--\ref{tab:benign-calibration-summary}, Bảng~\ref{tab:bd-per-file-counts} (ở Phụ lục~\ref{app:reproducibility}) thống kê tổng cửa sổ và biên độ mất cân bằng lớp trên toàn bộ 88 tệp đánh giá điều kiện B và D (44 tệp B + 44 tệp D). Tỷ lệ cửa sổ tấn công trên từng capture biến thiên hơn ba bậc độ lớn: từ $0{,}00\%$ ở \code{set\_04/D/force-neutral-2.csv} (0 cửa sổ dương trong 7.096 cửa sổ) và $0{,}03\%$ ở \code{set\_04/B/speed-1.csv} (14/40.932) tới $97{,}81\%$ ở \code{set\_04/B/interval-1.csv} (9.692/9.909, chỉ còn 217 cửa sổ âm) và $96{,}92\%\text{--}97{,}22\%$ ở hai tệp \code{interval} của \code{set\_03/D}. Do đó, các ngoại lệ nhỏ trên capture ít nền lành tính hoặc gần như toàn lành tính không được diễn giải đồng nhất với phân bố toàn điều kiện.

\subsection{Phân tích vai trò thành phần biểu diễn và độ nhạy kích thước cửa sổ (RQ2)}\label{sec:completion}
Nhằm bóc tách một cách định lượng ảnh hưởng của từng nhóm đặc trưng cấu trúc và khảo sát độ nhạy đối với kích thước cửa sổ phân tích, nghiên cứu đánh giá 10 biến thể biểu diễn ở kích thước $W=64$, đồng thời huấn luyện lại trên các kích thước cửa sổ thay thế $W \in \{32, 128\}$. Lưu ý rằng biến thể payload-only trùng khớp với raw-no-ID và no-timing tương ứng với nhánh structural content. Việc thay đổi $W$ dẫn đến sự thay đổi đồng thời về số lượng cửa sổ và độ phân giải thời gian quan sát. Không diễn giải đây là thay duy nhất một biến vật lý. Toàn bộ kết quả đối chuẩn 10 biến thể biểu diễn ở kích thước $W=64$ được trình bày tại Bảng~\ref{tab:extension-w64}.
\begin{longtable}{P{1.1cm}P{4.9cm}P{1.6cm}P{2.2cm}P{1.6cm}P{1.6cm}}
\caption{W64; trọng số set ngang nhau; FAR trên 100.000}\label{tab:extension-w64}\\\toprule
ĐK & Phương pháp & Recall & FAR & F1 & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
ĐK & Phương pháp & Recall & FAR & F1 & AP\\\midrule
\endhead
A & Chỉ ID & 0.7655 & 90.54 & 0.8439 & 0.8492\\
B & Chỉ ID & 0.8622 & 68896.67 & 0.2573 & 0.3379\\
C & Chỉ ID & 0.1978 & 93.00 & 0.2358 & 0.2736\\
D & Chỉ ID & 0.6822 & 67788.42 & 0.1857 & 0.1914\\
A & Raw & 0.6167 & 115.77 & 0.7258 & 0.7312\\
B & Raw & 0.8541 & 65301.41 & 0.3000 & 0.3781\\
C & Raw & 0.2101 & 91.92 & 0.2314 & 0.2661\\
D & Raw & 0.6614 & 67982.89 & 0.1213 & 0.1648\\
A & Raw bỏ ID & 0.2533 & 100.13 & 0.3668 & 0.4139\\
B & Raw bỏ ID & 0.6794 & 66658.13 & 0.0875 & 0.2200\\
C & Raw bỏ ID & 0.0906 & 62.70 & 0.1466 & 0.2222\\
D & Raw bỏ ID & 0.6871 & 66679.05 & 0.1677 & 0.2175\\
A & Raw cộng cấu trúc & 0.6515 & 84.74 & 0.7380 & 0.7428\\
B & Raw cộng cấu trúc & 0.7604 & 53227.73 & 0.3179 & 0.4842\\
C & Raw cộng cấu trúc & 0.1950 & 91.68 & 0.2296 & 0.2703\\
D & Raw cộng cấu trúc & 0.5783 & 52902.70 & 0.1567 & 0.2976\\
A & Structural & 0.5886 & 81.67 & 0.7072 & 0.7483\\
B & Structural & 0.7383 & 52461.46 & 0.2435 & 0.5554\\
C & Structural & 0.2230 & 75.82 & 0.2600 & 0.2928\\
D & Structural & 0.6445 & 54643.37 & 0.2069 & 0.3357\\
A & Structural bỏ delta & 0.4910 & 89.84 & 0.6050 & 0.6789\\
B & Structural bỏ delta & 0.8306 & 58636.28 & 0.2861 & 0.4927\\
C & Structural bỏ delta & 0.2006 & 73.86 & 0.2363 & 0.2720\\
D & Structural bỏ delta & 0.6795 & 60669.40 & 0.1815 & 0.2745\\
A & Structural bỏ thống kê cục bộ & 0.4851 & 100.21 & 0.6147 & 0.6346\\
B & Structural bỏ thống kê cục bộ & 0.6870 & 65298.51 & 0.0948 & 0.2894\\
C & Structural bỏ thống kê cục bộ & 0.1955 & 99.41 & 0.2412 & 0.2795\\
D & Structural bỏ thống kê cục bộ & 0.6925 & 66400.30 & 0.1626 & 0.3053\\
A & Structural bỏ payload tuyệt đối & 0.6243 & 87.77 & 0.7317 & 0.7644\\
B & Structural bỏ payload tuyệt đối & 0.9243 & 66779.19 & 0.3160 & 0.4453\\
C & Structural bỏ payload tuyệt đối & 0.3328 & 101.16 & 0.4076 & 0.4730\\
D & Structural bỏ payload tuyệt đối & 0.7202 & 67775.85 & 0.2024 & 0.3138\\
A & Structural bỏ hạng/W & 0.5308 & 79.90 & 0.6507 & 0.6837\\
B & Structural bỏ hạng/W & 0.7998 & 59718.63 & 0.2425 & 0.5266\\
C & Structural bỏ hạng/W & 0.2650 & 75.73 & 0.3247 & 0.3420\\
D & Structural bỏ hạng/W & 0.6881 & 62056.45 & 0.1830 & 0.3446\\
A & Structural bỏ chuyển tiếp & 0.5567 & 66.87 & 0.6784 & 0.7044\\
B & Structural bỏ chuyển tiếp & 0.7137 & 53236.21 & 0.2220 & 0.5556\\
C & Structural bỏ chuyển tiếp & 0.2419 & 76.67 & 0.2896 & 0.3210\\
D & Structural bỏ chuyển tiếp & 0.6665 & 55254.24 & 0.2049 & 0.3679\\
\bottomrule\end{longtable}
\begin{table}[htbp]
\centering
\small\setlength{\tabcolsep}{5pt}
\caption{Độ nhạy kích thước cửa sổ $W=32$ và $W=128$ (trọng số set ngang nhau; FAR trên 100.000)}\label{tab:extension-w32}
\vspace{2pt}
\begin{tabular}{cclcccc}
\toprule
$W$ & ĐK & Phương pháp & Recall & FAR (/100k) & F1 & AP\\\midrule
\multirow{8}{*}{$W=32$} 
 & A & Raw & 0.5516 & 107.46 & 0.6827 & 0.7057\\
 & B & Raw & 0.7722 & 61820.20 & 0.2066 & 0.2974\\
 & C & Raw & 0.2010 & 102.37 & 0.2263 & 0.2534\\
 & D & Raw & 0.6019 & 62060.00 & 0.1258 & 0.1285\\
 & A & Structural & 0.5760 & 140.93 & 0.6904 & 0.6952\\
 & B & Structural & 0.7791 & 53054.55 & 0.2420 & 0.4196\\
 & C & Structural & 0.2360 & 87.68 & 0.2765 & 0.2943\\
 & D & Structural & 0.6342 & 55225.47 & 0.1659 & 0.2732\\\midrule
\multirow{8}{*}{$W=128$} 
 & A & Raw & 0.4141 & 104.55 & 0.5186 & 0.6147\\
 & B & Raw & 0.7353 & 61158.10 & 0.1954 & 0.3903\\
 & C & Raw & 0.0702 & 71.78 & 0.1093 & 0.2021\\
 & D & Raw & 0.5957 & 58708.86 & 0.1111 & 0.2516\\
 & A & Structural & 0.6248 & 95.04 & 0.7339 & 0.7299\\
 & B & Structural & 0.7481 & 54375.95 & 0.2468 & 0.4899\\
 & C & Structural & 0.2213 & 68.53 & 0.2558 & 0.3073\\
 & D & Structural & 0.6589 & 56877.92 & 0.1764 & 0.3097\\
\bottomrule
\end{tabular}
\end{table}
Bỏ ID khỏi Raw ở B làm recall giảm từ 0,8541 xuống 0,6794 và AP từ 0,3781 xuống 0,2200; do đó bỏ ID đơn thuần không đủ để cải thiện. Raw cộng cấu trúc có F1 B 0,3179 nhưng AP 0,4842, trong khi Structural có F1 0,2435 và AP 0,5554. Các tiêu chí không cho cùng một thứ tự xếp hạng.

Bỏ payload tuyệt đối khỏi Structural làm recall B tăng từ 0,7383 lên 0,9243, nhưng FAR tăng từ 52.461,46 lên 66.779,19 trên 100.000 và AP giảm từ 0,5554 xuống 0,4453. Không gọi đây là cải thiện tổng thể. Tuy nhiên, một phát hiện có ý nghĩa quan trọng xuất hiện ở điều kiện C (xe quen, tấn công lạ): biến thể bỏ payload tuyệt đối đạt F1 0,4076 và AP 0,4730, vượt trội hoàn toàn so với cả Raw (F1 0,2314, AP 0,2661) lẫn Structural đầy đủ (F1 0,2600, AP 0,2928). Kết quả này chỉ ra rằng việc giữ lại giá trị byte payload tuyệt đối có xu hướng làm mô hình quá khớp (overfit) vào chữ ký payload của các kịch bản tấn công nguồn đã biết, gây cản trở việc phát hiện các cuộc tấn công zero-day trên cùng phương tiện; việc loại bỏ byte thô và chỉ giữ lại động học biến thiên payload $\Delta$ cùng thống kê cục bộ giúp giải phóng mô hình khỏi sự phụ thuộc này. Bỏ delta cũng tăng recall B nhưng tăng FAR và giảm AP. Ngược lại, bỏ thống kê cục bộ làm AP B giảm xuống 0,2894 và FAR tăng lên 65.298,51; trong phép so này nhóm thống kê gắn với lợi ích xếp hạng và báo động giả.

Bỏ chuyển tiếp cho AP B gần như không đổi (0,5556 so với 0,5554) và AP D tăng (0,3679 so với 0,3357). Không có bằng chứng ở các điểm ước lượng này rằng thêm chuyển tiếp luôn có ích. Những so sánh ghép cặp mô tả ảnh hưởng của thành phần trong pipeline, không chứng minh nguyên nhân vật lý. Số chiều thay đổi làm số tham số lớp chiếu thay đổi; tổng số tham số không hoàn toàn bằng nhau.

Chênh lệch recall Structural trừ Raw ở B lần lượt khoảng +0,69; -11,59; +1,28 điểm phần trăm tại W32, W64 và W128 (được thống kê chi tiết tại Bảng~\ref{tab:extension-w32}). Đổi dấu cho thấy kết luận phụ thuộc độ dài và cách tạo cửa sổ. FAR Structural ở B vẫn trên 53\% tại W32/W128, nên dấu dương recall không đủ xác nhận tính hữu dụng. Báo cáo kèm dữ liệu từng set/seed, độ lệch chuẩn và bootstrap theo capture; không chọn W sau khi xem test rồi gọi đó là xác nhận độc lập.

\subsubsection{Kiểm chứng độ nhạy cửa sổ đẳng lượng khung tin và phương sai lấy mẫu reservoir}\label{subsec:frame-equated-w-and-reservoir}
Vì vòng chạy \code{W32/W128} ban đầu giữ cố định trần $1.000$ cửa sổ/tệp/lớp (tương ứng $32\text{k}$, $64\text{k}$ và $128\text{k}$ khung tin), Bảng~\ref{tab:frame-equated-w} kiểm chứng lại trên đúng \textbf{ngân sách đẳng lượng $64.000$ khung tin/tệp/lớp} (\code{W32 cap=2000}, \code{W64 cap=1000}, \code{W128 cap=500}) đồng thời cân bằng ngân sách khởi động hiệu chuẩn $K_{\text{khung}}=32.000$ khung ($K=1.000$, $500$ và $250$ cửa sổ tương ứng) qua $4\text{ set} \times 3\text{ seed}$. Kết quả xác nhận bất biến kép dưới điều kiện đồng lượng dữ liệu: (i) \code{Structural} vượt trội \code{Raw} về AP trên B và D ở cả ba kích thước cửa sổ ($W=32$: $0{,}4304$ so với $0{,}2794$ ở B; $W=64$: $0{,}5607$ so với $0{,}3803$; $W=128$: $0{,}4903$ so với $0{,}3679$), và (ii) $W=64$ tiếp tục là điểm tối ưu vì $W=32$ thiếu ngữ cảnh thống kê nội cửa sổ còn $W=128$ giảm một nửa số bước cập nhật gradient ($500$ so với $1.000$ cửa sổ). Bên cạnh đó, Bảng~\ref{tab:reservoir-variance} đo phương sai giữa 3 seed lấy mẫu reservoir độc lập (\code{20261103, 20261104, 20261105} tại model \code{seed=42}), cho thấy ưu thế AP của \code{Structural} so với \code{Raw} được bảo toàn ổn định ($0{,}5311 \pm 0{,}0466$ so với $0{,}3591 \pm 0{,}0334$ ở B; $0{,}3730 \pm 0{,}0252$ so với $0{,}2065 \pm 0{,}0443$ ở D).

\Needspace{18\baselineskip}
{\small\setlength{\tabcolsep}{4pt}
\begin{longtable}{P{2.2cm}P{2.2cm}P{1.9cm}P{0.7cm}P{2.1cm}P{1.5cm}P{1.4cm}P{1.5cm}}
\caption{Độ nhạy kích thước cửa sổ đẳng lượng $64.000$ khung/tệp/lớp (4 set $\times$ 3 seed; hiệu chuẩn $K_{\text{khung}}=32.000$, ngân sách FAR $1{,}0\%$)}\label{tab:frame-equated-w}\\\toprule
Cấu hình $W$ & Mô hình & Ngưỡng & ĐK & Recall (3-xe) & FAR (\%) & F1 & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Cấu hình $W$ & Mô hình & Ngưỡng & ĐK & Recall (3-xe) & FAR (\%) & F1 & AP\\\midrule
\endhead
$W=32$ (cap 2000) & Raw & Nguồn & B & 0.7901 & 65.61\% & 0.1962 & 0.2759\\
$W=32$ (cap 2000) & Structural & Nguồn & B & 0.8082 & 54.30\% & 0.2709 & 0.4246\\
$W=32$ ($K=1000$) & Raw & Cal 1.0\% & B & 0.2035 (0.2184) & 0.98\% & 0.2562 & 0.2794\\
$W=32$ ($K=1000$) & \textbf{Structural} & Cal 1.0\% & B & \textbf{0.2832} (\textbf{0.3086}) & 1.17\% & \textbf{0.3442} & \textbf{0.4304}\\
$W=32$ ($K=1000$) & Raw & Cal 1.0\% & D & 0.0543 (0.0652) & 1.37\% & 0.0514 & 0.1058\\
$W=32$ ($K=1000$) & \textbf{Structural} & Cal 1.0\% & D & \textbf{0.1690} (\textbf{0.1933}) & \textbf{0.89\%} & \textbf{0.2226} & \textbf{0.2767}\\
\midrule
$W=64$ ($K=500$) & Raw & Cal 1.0\% & B & 0.3373 (0.3922) & 1.05\% & 0.3788 & 0.3803\\
$W=64$ ($K=500$) & \textbf{Structural} & Cal 1.0\% & B & \textbf{0.4042} (\textbf{0.4303}) & \textbf{0.85\%} & \textbf{0.4748} & \textbf{0.5607}\\
$W=64$ ($K=500$) & Raw & Cal 1.0\% & D & 0.0979 (0.1257) & 1.08\% & 0.1195 & 0.1692\\
$W=64$ ($K=500$) & \textbf{Structural} & Cal 1.0\% & D & \textbf{0.2071} (\textbf{0.2255}) & \textbf{0.58\%} & \textbf{0.2728} & \textbf{0.3411}\\
\midrule
$W=128$ (cap 500) & Raw & Nguồn & B & 0.8593 & 73.23\% & 0.2396 & 0.3657\\
$W=128$ (cap 500) & Structural & Nguồn & B & 0.7466 & 56.50\% & 0.2681 & 0.4862\\
$W=128$ ($K=250$) & Raw & Cal 1.0\% & B & 0.3206 (0.3669) & \textbf{0.80\%} & 0.3827 & 0.3679\\
$W=128$ ($K=250$) & \textbf{Structural} & Cal 1.0\% & B & \textbf{0.3819} (\textbf{0.4330}) & 1.69\% & \textbf{0.4204} & \textbf{0.4903}\\
$W=128$ ($K=250$) & Raw & Cal 1.0\% & D & 0.1155 (0.1444) & 1.49\% & 0.1384 & 0.1856\\
$W=128$ ($K=250$) & \textbf{Structural} & Cal 1.0\% & D & \textbf{0.1968} (\textbf{0.2319}) & \textbf{0.72\%} & \textbf{0.2474} & \textbf{0.3334}\\
\bottomrule\end{longtable}}

\Needspace{14\baselineskip}
{\small\setlength{\tabcolsep}{4pt}
\begin{longtable}{P{2.2cm}P{2.1cm}P{0.7cm}P{2.4cm}P{2.4cm}P{2.2cm}P{2.2cm}}
\caption[Phương sai lấy mẫu reservoir đa seed (W64, model seed=42)]{Phương sai lấy mẫu reservoir đa seed (\code{sampling\_seed} $\in \{20261103,\, 20261104,\, 20261105\}$, W64, model \code{seed=42}, mean $\pm$ std qua 3 lượt lấy mẫu $\times$ 4 set)}\label{tab:reservoir-variance}\\\toprule
Mô hình & Chế độ & ĐK & Recall & FAR (/100k) & Attack F1 & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Mô hình & Chế độ & ĐK & Recall & FAR (/100k) & Attack F1 & AP\\\midrule
\endhead
Raw & Nguồn & B & 0.9539 $\pm$ 0.0135 & 80834 $\pm$ 7470 & 0.1916 $\pm$ 0.0968 & 0.3545 $\pm$ 0.0351\\
Structural & Nguồn & B & 0.6878 $\pm$ 0.0914 & 55092 $\pm$ 12450 & 0.1767 $\pm$ 0.0736 & \textbf{0.5272 $\pm$ 0.0468}\\
Raw & Cal $K=500$, 0,1\% & B & 0.2040 $\pm$ 0.1021 & 106,20 $\pm$ 42,45 & 0.2941 $\pm$ 0.0859 & 0.3591 $\pm$ 0.0334\\
\textbf{Structural} & Cal $K=500$, 0,1\% & B & \textbf{0.2482 $\pm$ 0.0233} & \textbf{83,48 $\pm$ 11,30} & \textbf{0.3695 $\pm$ 0.0335} & \textbf{0.5311 $\pm$ 0.0466}\\
Raw & Cal $K=500$, 1,0\% & B & 0.2490 $\pm$ 0.0848 & 779,74 $\pm$ 95,03 & 0.3266 $\pm$ 0.0626 & 0.3591 $\pm$ 0.0334\\
\textbf{Structural} & Cal $K=500$, 1,0\% & B & \textbf{0.4261 $\pm$ 0.0495} & \textbf{627,18 $\pm$ 77,98} & \textbf{0.5242 $\pm$ 0.0441} & \textbf{0.5311 $\pm$ 0.0466}\\
Raw & Cal $K=500$, 1,0\% & D & 0.1418 $\pm$ 0.0698 & 1075,39 $\pm$ 316,44 & 0.1630 $\pm$ 0.0578 & 0.2065 $\pm$ 0.0443\\
\textbf{Structural} & Cal $K=500$, 1,0\% & D & \textbf{0.2018 $\pm$ 0.0259} & \textbf{510,72 $\pm$ 71,19} & \textbf{0.2756 $\pm$ 0.0303} & \textbf{0.3730 $\pm$ 0.0252}\\
\bottomrule\end{longtable}}

\subsection{Đánh giá mức độ độc lập xe và phân tách tấn công qua thăm dò tuyến tính (RQ3)}
Probe dùng 12 cặp encoder đã đóng băng, giữ lại nhóm recording-round khác nhóm huấn luyện và cân bằng mọi ô xe $\times$ nhãn. Encoder đã thấy dữ liệu huấn luyện của nguồn mình; không coi đây là kiểm tra phiên lái độc lập hoàn toàn.
\begin{longtable}{P{3.3cm}P{1.6cm}P{4.7cm}P{3.1cm}}
\caption{Balanced accuracy trung bình qua encoder; không phải CI quần thể xe}\label{tab:extension-probes}\\\toprule
Biểu diễn & Nhãn & Đối chứng & Balanced accuracy\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Biểu diễn & Nhãn & Đối chứng & Balanced accuracy\\\midrule
\endhead
raw & attack & constant & 0.5000\\
raw & attack & learned & 0.6419\\
raw & attack & permuted train labels & 0.5106\\
raw & attack & random embedding & 0.5026\\
raw & vehicle & constant & 0.2500\\
raw & vehicle & learned & 0.9925\\
raw & vehicle & permuted train labels & 0.2444\\
raw & vehicle & random embedding & 0.2496\\
structural & attack & constant & 0.5000\\
structural & attack & learned & 0.7669\\
structural & attack & permuted train labels & 0.4958\\
structural & attack & random embedding & 0.5026\\
structural & vehicle & constant & 0.2500\\
structural & vehicle & learned & 0.9488\\
structural & vehicle & permuted train labels & 0.2287\\
structural & vehicle & random embedding & 0.2496\\
\bottomrule\end{longtable}
Từ Bảng~\ref{tab:extension-probes}, hai kết quả tương phản nổi bật được ghi nhận:
\begin{enumerate}
    \item \textbf{Cải thiện khả năng phân tách tấn công:} Probe giải mã nhãn tấn công từ biểu diễn Structural đạt balanced accuracy 0,7669, tăng vọt 12,50 điểm phần trăm so với Raw (0,6419). Kết quả này khẳng định rằng việc thay thế ID thô bằng các biến thiên payload và thống kê mật độ cục bộ giúp không gian đặc trưng ẩn $z$ của mô hình tổ chức các mẫu hình bất thường một cách mạch lạc và có thể phân tách tuyến tính tốt hơn nhiều so với biểu diễn thô.
    \item \textbf{Tồn lưu danh tính xe:} Ngược lại, khả năng giải mã nhãn xe chỉ giảm nhẹ từ 0,9925 (ở Raw) xuống 0,9488 (ở Structural), tức giảm 4,37 điểm phần trăm nhưng vẫn cao hơn rất nhiều so với mức phỏng đoán ngẫu nhiên 0,2500 (trọng tài ngẫu nhiên hoặc hoán vị nhãn chỉ đạt $\approx 0{,}25$). Mức 94,88\% cho thấy không gian biểu diễn ẩn vẫn duy trì dấu vân tay nhận diện xe cực kỳ sắc nét.
\end{enumerate}

\subsubsection{Chẩn đoán nguồn gốc rò rỉ thông tin xe qua các nhóm đặc trưng đầu vào}
Để trả lời câu hỏi cốt lõi: \textit{``Tại sao đã loại bỏ hoàn toàn 11-bit CAN-ID thô nhưng mô hình vẫn nhận diện được xe với độ chính xác xấp xỉ $95\%$?''}, nghiên cứu tiến hành một thực nghiệm chẩn đoán bóc tách trên $8.440$ cửa sổ cân bằng hoàn toàn qua 4 dòng xe và 2 trạng thái nhãn ($3.800$ cửa sổ tập huấn luyện probe và $4.640$ cửa sổ tập kiểm thử giữ ngoài theo vòng ghi; xem thêm đối chiếu độ nhạy hằng số điều chuẩn $C$ ở Mục~\ref{sec:probe-audit}). Bằng cách cô lập từng nhóm đặc trưng đầu vào và huấn luyện bộ dò tuyến tính trực tiếp trên các nhóm này, kết quả thu được ở Bảng~\ref{tab:input-feature-probes} đã chỉ rõ các kênh truyền dẫn thông tin danh tính phương tiện.

\Needspace{18\baselineskip}
\begin{longtable}{P{6.2cm}C{1.6cm}C{2.1cm}C{1.6cm}C{2.1cm}}
\caption{Khả năng giải mã nhãn xe và tấn công từ từng nhóm đặc trưng đầu vào ($W=64$)}\label{tab:input-feature-probes}\\\toprule
Nhóm đặc trưng đầu vào & Số chiều / khung & Tổng chiều ($W=64$) & Probe xe & Probe tấn công\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Nhóm đặc trưng đầu vào & Số chiều / khung & Tổng chiều ($W=64$) & Probe xe & Probe tấn công\\\midrule
\endhead
Tất cả 30 đặc trưng (Structural) & 30 & 1920 & 0.9804 & 0.7487\\
DLC, mặt nạ hợp lệ và cờ $h_i$ (\texttt{dlc\_and\_masks}) & 10 & 640 & \textbf{0.9670} & 0.6289\\
\quad -- Bóc tách riêng DLC và 8 mặt nạ (chỉ 9 chiều) & 9 & 576 & 0.9642 & 0.5946\\
\quad -- Bóc tách riêng cờ lịch sử $h_i$ (chỉ số 25) & 1 & 64 & 0.2746 & 0.5662\\
Chỉ thống kê cục bộ (\texttt{local\_stats}) & 3 & 192 & \textbf{0.7565} & \textbf{0.7269}\\
Chỉ Payload thô (\texttt{payload}) & 8 & 512 & 0.7621 & 0.5601\\
Chỉ Biến thiên payload ($\Delta\text{payload}$) & 8 & 512 & 0.6498 & 0.6420\\
Chỉ Chuyển tiếp ID (\texttt{transition}) & 1 & 64 & 0.4627 & 0.5013\\
\midrule
Loại bỏ Payload thô (\texttt{no\_payload}) & 22 & 1408 & 0.9565 & 0.7578\\
Loại bỏ Biến thiên payload (\texttt{no\_delta}) & 22 & 1408 & 0.9884 & 0.7252\\
Loại bỏ Thống kê cục bộ (\texttt{no\_local\_stats}) & 27 & 1728 & 0.9541 & 0.6319\\
Loại bỏ Chuyển tiếp ID (\texttt{no\_transition}) & 29 & 1856 & 0.9778 & 0.7241\\
\bottomrule\end{longtable}

Kết quả thực nghiệm tại Bảng~\ref{tab:input-feature-probes} mang lại những bằng chứng vật lý và giao thức quan trọng:
\begin{enumerate}
    \item \textbf{Cú pháp độ dài khung tin (DLC + 8 mặt nạ) là kênh rò rỉ lớn nhất (96,42\%--96,70\%):} Nhóm \texttt{dlc\_and\_masks} gồm 10 chiều/khung ($d_i/8$ [1 chiều], 8 mặt nạ byte hợp lệ $m_{i,j}$ [8 chiều] và cờ chỉ báo lịch sử $h_i$ tại chỉ số 25 [1 chiều]). Khi bóc tách riêng 9 chiều DLC và mặt nạ, probe giải mã xe đạt tới $0{,}9642$ (trong khi đứng độc lập cờ $h_i$ 1 chiều chỉ đạt $0{,}2746$, gần mức cơ hội $0{,}2500$, dù giúp đẩy probe tấn công từ $0{,}5946$ lên $0{,}6289$). Điều này khẳng định rò rỉ xe bắt nguồn từ kiến trúc độ dài khung tin của nhà sản xuất: tỷ lệ khung $8$ byte so với $2, 4, 5$ byte và vị trí đệm trong 64 khung liên tiếp tạo nên ``chữ ký hình thái'' nhận diện hãng xe ngay cả khi bỏ hoàn toàn CAN-ID.
    \item \textbf{Mật độ bus cục bộ mang tính hai mặt (75,65\% xe và 72,69\% tấn công):} Chỉ với 3 chiều đặc trưng thống kê cục bộ (\texttt{count\_in\_window}, \texttt{rank\_id}, \texttt{rank\_w}), bộ dò tuyến tính giải mã được 75,65\% nhãn xe. Mật độ tải bus (bus load) và số lượng ECU phát sóng trong một cửa sổ phản ánh cấu hình phần cứng mạng riêng biệt của xe. Tuy nhiên, nhóm đặc trưng này đồng thời là chìa khóa then chốt nhất để phát hiện tấn công, đạt probe tấn công lên tới 72,69\%.
    \item \textbf{Dải giá trị cảm biến nền (76,21\% xe):} Các byte payload thô phản ánh trạng thái vật lý nền của từng dòng xe (ví dụ cảm biến nhiệt độ, tốc độ quay động cơ ở chế độ cầm chừng), tạo nên một chữ ký phân biệt thứ cấp.
\end{enumerate}

\subsubsection{Hiện tượng đan xen đặc trưng và giới hạn của kỹ thuật cắt bỏ}
Để kiểm chứng xem liệu việc cắt bỏ các nhóm đặc trưng (feature ablation) trong quá trình huấn luyện Transformer có giúp triệt tiêu rò rỉ danh tính xe hay không, nghiên cứu thực hiện probe trên vector biểu diễn ẩn $z \in \mathbb{R}^{64}$ của toàn bộ 96 checkpoint thuộc các kiến trúc cắt bỏ. Kết quả cho thấy:
\begin{itemize}
    \item Khả năng giải mã danh tính xe trong không gian ẩn của tất cả các biến thể cắt bỏ đều duy trì ở mức rất cao ($>94{,}8\%$). Ngay cả khi cắt bỏ toàn bộ payload tuyệt đối (\texttt{no\_payload}), probe xe trên $z$ vẫn là 97,28\%; khi cắt bỏ biến thiên delta (\texttt{no\_delta}), probe xe là 96,52\%; khi cắt bỏ thống kê cục bộ (\texttt{no\_local}), probe xe vẫn là 96,33\%.
    \item Ngược lại, việc cắt bỏ các nhóm đặc trưng cấu trúc gây sụp đổ nặng nề chất lượng phát hiện tấn công: cắt bỏ thống kê cục bộ khiến AP điều kiện B sụt giảm từ 0,5554 xuống 0,2894 (và probe tấn công giảm xuống 0,6319); cắt bỏ payload làm FAR điều kiện B tăng vọt từ 52,46\% lên 66,78\%.
\end{itemize}

Phát hiện này chứng minh sự tồn tại của \textbf{hiện tượng đan xen đặc trưng (Feature Entanglement)}: các đặc tính cấu trúc giúp mô hình nhận diện hành vi bất thường (mật độ gói tin đột biến, tần suất chèn thông điệp, hình thái khung tin) lại chính là những thuộc tính mang đậm dấu ấn cấu trúc mạng của chiếc xe đó. Do tính chất đan xen đa kênh này, không thể loại bỏ dấu vân tay xe bằng các biện pháp cắt lọc đặc trưng tĩnh mà không làm triệt tiêu năng lực phát hiện xâm nhập của hệ thống.

\noindent\textbf{Kết luận và liên kết giải pháp:} Biểu diễn Structural không đạt được tính độc lập đặc thù xe hoàn toàn (94,88\% so với mức ngẫu nhiên $25\%$). Tuy nhiên, vì nó duy trì khả năng phân tách tấn công vượt trội (0,7669), nguyên nhân khiến việc chuyển giao zero-shot thất bại (FAR 52,46\% ở ngưỡng nguồn) không phải do mô hình mất khả năng nhận diện bất thường, mà do vector đặc trưng của xe đích bị dịch chuyển sang một vùng phân phối mới khiến ngưỡng phân loại tĩnh $\tau_{\text{src}}$ không còn phù hợp. Đây chính là bằng chứng lý giải vì sao phương pháp hiệu chuẩn nền lành tính (Benign Warmup Calibration) ở Mục~\ref{sec:benign-calibration} lại phát huy hiệu quả xuất sắc: nó tôn trọng và giữ nguyên không gian biểu diễn phân tách tốt của mô hình, chỉ thực hiện tái cân chỉnh ngưỡng phân vị trên dữ liệu lành tính ban đầu, qua đó kiểm soát mạnh báo động giả (giảm FAR từ $52{,}46\%$ xuống $\le 1{,}08\%$) mà không cần thay đổi hay huấn luyện lại mô hình.
\subsubsection{Độ nhạy hằng số điều chuẩn C của Linear Probe}\label{sec:probe-audit}
Nhằm kiểm chứng kết quả rò rỉ theo từng nhóm đặc trưng tại Bảng~\ref{tab:input-feature-probes} không phụ thuộc vào lựa chọn đơn lẻ hằng số điều chuẩn $C$, Bảng~\ref{tab:probe-c-scaling} quét $C \in \{0{,}01,\,0{,}1,\,1{,}0,\,10{,}0\}$ trên đúng tập $3.800/4.640$ cửa sổ cân bằng. Độ chính xác giải mã xe của \code{dlc\_and\_masks\_10D} (640 chiều phẳng hóa) duy trì ổn định trong khoảng $0{,}9597\text{--}0{,}9670$ qua bốn bậc độ lớn của $C$, còn nhóm tách riêng 9 chiều \code{dlc\_masks\_9D} đạt $0{,}9580\text{--}0{,}9662$; tương tự toàn bộ 30 chiều đạt $0{,}9791\text{--}0{,}9806$, xác nhận dấu vân tay hình thái khung tin theo từng hãng xe tách biệt tuyến tính bền vững ngay cả dưới điều chuẩn $L_2$ mạnh ($C=0{,}01$). Kết quả tổng hợp probe trên đầy đủ 10 biến thể biểu diễn (96+24 checkpoint) được trình bày tại Bảng~\ref{tab:app-96ckpt-probes} ở Phụ lục~\ref{app:reproducibility}.

\Needspace{14\baselineskip}
{\small\setlength{\tabcolsep}{5pt}
\begin{longtable}{P{4.4cm}P{1.4cm}P{1.5cm}P{1.5cm}P{1.5cm}P{1.5cm}}
\caption{Độ nhạy hằng số điều chuẩn $C$ của Linear Probe nhận diện xe (Balanced Accuracy trên 4.640 mẫu giữ ngoài)}\label{tab:probe-c-scaling}\\\toprule
Nhóm đặc trưng đầu vào & Chiều phẳng & $C=0{,}01$ & $C=0{,}1$ & $C=1{,}0$ & $C=10{,}0$\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Nhóm đặc trưng đầu vào & Chiều phẳng & $C=0{,}01$ & $C=0{,}1$ & $C=1{,}0$ & $C=10{,}0$\\\midrule
\endhead
Toàn bộ 30D (\code{all\_30D}) & 1920 & 0.9791 & 0.9804 & 0.9804 & \textbf{0.9806}\\
\code{dlc\_and\_masks\_10D} & 640 & 0.9597 & \textbf{0.9670} & \textbf{0.9670} & 0.9647\\
\code{dlc\_masks\_9D} (bỏ $h_i$) & 576 & 0.9580 & \textbf{0.9662} & 0.9642 & 0.9636\\
\code{local\_stats\_3D} & 192 & 0.7463 & \textbf{0.7631} & 0.7565 & 0.7537\\
\code{payload\_8D} & 512 & \textbf{0.7864} & 0.7782 & 0.7621 & 0.7418\\
\code{delta\_8D} & 512 & \textbf{0.6765} & 0.6597 & 0.6498 & 0.6414\\
\code{transition\_1D} & 64 & \textbf{0.4853} & 0.4692 & 0.4627 & 0.4623\\
\code{has\_prev\_1D} ($h_i$) & 64 & 0.2668 & 0.2744 & 0.2746 & \textbf{0.2752}\\
\bottomrule\end{longtable}}

\subsection{Kiểm thử trên dữ liệu ngoại bộ và phân tích các trường hợp thất bại (RQ4)}
Mô hình Set 1 ở ba seed và ngưỡng nguồn được giữ nguyên trên 57 capture có nhãn/schema đạt kiểm tra (kết quả chi tiết tại Bảng~\ref{tab:extension-external}). Không dùng nhãn ngoại bộ để đổi checkpoint hoặc ngưỡng. Hai nhóm OTIDS bị loại và một file CICIoV SPEED bị cách ly; ledger giữ nguyên mọi quyết định.
\begin{longtable}{P{4.2cm}P{2.8cm}P{1.6cm}P{3.6cm}}
\caption{Ngoại bộ tại ngưỡng nguồn: gộp số đếm theo dataset/seed rồi trung bình seed; FAR trên 100.000 (và \%)}\label{tab:extension-external}\\\toprule
Dataset & Biểu diễn & Recall & FAR /100k (\%)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Dataset & Biểu diễn & Recall & FAR /100k (\%)\\\midrule
\endhead
CAN\_MIRGU\_attack & raw & 0.5848 & 59175.90 (59.18\%)\\
CAN\_MIRGU\_attack & structural & 0.0546 & 2701.79 (2.70\%)\\
CAN\_MIRGU\_benign & raw & -- & 60615.05 (60.62\%)\\
CAN\_MIRGU\_benign & structural & -- & 6631.09 (6.63\%)\\
CICIoV2024 & raw & 0.6462 & 100000.00 (100.00\%)\\
CICIoV2024 & structural & 1.0000 & 100000.00 (100.00\%)\\
Opel\_Astra\_DoS & raw & 1.0000 & 43850.24 (43.85\%)\\
Opel\_Astra\_DoS & structural & 1.0000 & 31534.46 (31.53\%)\\
Opel\_Astra\_benign & raw & -- & 43841.70 (43.84\%)\\
Opel\_Astra\_benign & structural & -- & 30980.52 (30.98\%)\\
Renault\_Clio\_DoS & raw & 0.9995 & 33102.87 (33.10\%)\\
Renault\_Clio\_DoS & structural & 0.9984 & 188.56 (0.19\%)\\
Renault\_Clio\_benign & raw & -- & 33443.71 (33.44\%)\\
Renault\_Clio\_benign & structural & -- & 165.56 (0.17\%)\\
\bottomrule\end{longtable}
CICIoV Structural có recall 1,0000 nhưng FAR 100.000/100.000 (100\%): điểm vận hành dự đoán toàn bộ là tấn công. Không coi recall 100\% đó là thành công. Trên MIRGU attack, recall Structural khoảng 0,0546 so với Raw 0,5848; giảm FAR không bù được việc bỏ sót phần lớn cửa sổ tấn công nếu mục tiêu là phát hiện đáng tin.

Renault DoS là trường hợp có lợi theo cơ chế: Structural giữ recall khoảng 0,9984 (tức $99{,}84\%$), FAR 188,56/100.000 ($0{,}19\%$) so với Raw 33.102,87 ($33{,}10\%$); capture benign tương ứng có FAR 165,56 ($0{,}17\%$) so với 33.443,71 ($33{,}44\%$). Điều này không chứng minh khái quát phổ quát: Automotive benign/DoS chia sẻ lưu lượng nền, các dataset có prevalence và chính sách nhãn khác nhau. Benign-only chỉ xác định FAR; không suy recall/AP hai lớp từ các capture đó. Mọi kết quả vẫn theo thứ tự file, không xác nhận chronology vật lý hoặc 57 phiên độc lập.

\section{Đánh giá các cơ chế thích ứng miền và khôi phục điểm vận hành}
\subsection{Đánh giá thực nghiệm Structural Transformer kết hợp MixStyle}\label{sec:mixstyle-study}
Mục này đánh giá hiệu năng thực nghiệm của mô hình Structural Transformer khi tích hợp kỹ thuật trộn đặc trưng miền MixStyle (đã được đặc tả toán học tại Mục~\ref{subsec:method-mixstyle}). Thực nghiệm gồm 12 lượt huấn luyện mới (4 set $\times$ 3 seed) với cùng bộ siêu tham số và dữ liệu như mô hình gốc. Thống nhất với phần còn lại của Chương~\ref{chap:results}, các bảng kết quả trong mục này (Bảng~\ref{tab:mixstyle-ad}--\ref{tab:mixstyle-external}) báo cáo FAR theo đơn vị phần trăm (\%), tương ứng $\operatorname{FAR}(\%) = \operatorname{FAR}_{100k}/1.000$.
\begin{longtable}{P{1cm}P{4.3cm}P{1.6cm}P{2cm}P{1.5cm}P{1.5cm}}
\caption{MixStyle: trung bình seed trong set rồi trọng số ngang nhau giữa set; FAR tính bằng phần trăm}\label{tab:mixstyle-ad}\\\toprule
A--D & Pipeline & Recall & FAR (\%) & AP & F1\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
A--D & Pipeline & Recall & FAR (\%) & AP & F1\\\midrule
\endhead
A & Raw & 0.6167 & 0.1158 & 0.7312 & 0.7258\\
A & Structural & 0.5886 & 0.0817 & 0.7483 & 0.7072\\
A & Structural + MixStyle & 0.6675 & 0.0827 & 0.7784 & 0.7701\\
B & Raw & 0.8541 & 65.3014 & 0.3781 & 0.3000\\
B & Structural & 0.7383 & 52.4615 & 0.5554 & 0.2435\\
B & Structural + MixStyle & 0.8194 & 64.5387 & 0.5815 & 0.2298\\
C & Raw & 0.2101 & 0.0919 & 0.2661 & 0.2314\\
C & Structural & 0.2230 & 0.0758 & 0.2928 & 0.2600\\
C & Structural + MixStyle & 0.2838 & 0.0781 & 0.3620 & 0.3317\\
D & Raw & 0.6614 & 67.9829 & 0.1648 & 0.1213\\
D & Structural & 0.6445 & 54.6434 & 0.3357 & 0.2069\\
D & Structural + MixStyle & 0.6982 & 66.9915 & 0.3658 & 0.1600\\
\bottomrule\end{longtable}
Ở tiêu chí chính B, recall MixStyle là 0,8194, so với Structural 0,7383 và Raw 0,8541. So với Structural, recall tăng 8,11 điểm phần trăm nhưng FAR cũng tăng 12,08 điểm phần trăm. AP tăng không thay thế tiêu chí recall. So với Raw, recall vẫn thấp hơn; không có cải thiện đồng thời ở B.
Ở A/C/D, trung bình recall cao hơn Raw và FAR thấp hơn Raw, nhưng mức tăng recall chỉ xuất hiện ở 2/4, 4/4 và 1/4 set tương ứng. Vì vậy, trung bình thuận lợi ở D không phải cải thiện nhất quán giữa các xe. FAR B/D vẫn trên 64\%, rất xa ngân sách nguồn 0,1\%; ngân sách nguồn không bảo đảm ngân sách đích. Khoảng bootstrap theo capture và biến thiên seed được báo riêng trong dữ liệu kèm theo; không suy CI cho quần thể xe.

Để so sánh trực tiếp hiệu năng giữa các hướng tiếp cận, Bảng~\ref{tab:mixstyle-six} đối chiếu sáu pipeline tiêu biểu tại điều kiện chuyển xe B.
\Needspace{18\baselineskip}
\begin{longtable}{P{6cm}P{2cm}P{2.2cm}P{2cm}}
\caption{Sáu pipeline ở B; điểm của các bản thích ứng trong cùng giao thức}\label{tab:mixstyle-six}\\\toprule
Pipeline & Recall & FAR (\%) & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Pipeline & Recall & FAR (\%) & AP\\\midrule
\endhead
Raw & 0.8541 & 65.3014 & 0.3781\\
Structural & 0.7383 & 52.4615 & 0.5554\\
Structural + MixStyle & 0.8194 & 64.5387 & 0.5815\\
CANBERT+ adapted & 0.6395 & 64.8438 & 0.0970\\
CANLP-char-DNN adapted & 0.2854 & 29.6959 & 0.0542\\
CrySyS-AssocRules/W64 & 0.0000 & 0.0000 & 0.0591\\
\bottomrule\end{longtable}
Bảng không xếp hạng trực tiếp các điểm công bố gốc. AssocRules có recall/FAR bằng không tại điểm dự đoán toàn benign; đó không phải phát hiện hiệu quả.
\subsubsection{Probe, ngoại bộ và chi phí xử lý}
Kết quả thăm dò tuyến tính (Linear Probe) đo mức độ tồn lưu thông tin xe và khả năng phân tách tấn công của mô hình MixStyle được trình bày tại Bảng~\ref{tab:mixstyle-probe}.
\Needspace{18\baselineskip}
\begin{longtable}{P{6cm}P{3cm}P{3cm}}
\caption{Probe trên cùng 3.800 mẫu huấn luyện probe và 4.640 mẫu kiểm thử giữ ngoài theo vòng ghi; balanced accuracy}\label{tab:mixstyle-probe}\\\toprule
Pipeline & Xe & Tấn công\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Pipeline & Xe & Tấn công\\\midrule
\endhead
raw & 0.9925 & 0.6419\\
structural & 0.9488 & 0.7669\\
structural\_mixstyle & 0.9527 & 0.7737\\
\bottomrule\end{longtable}
Mức cơ hội là 0,25 cho xe và 0,5 cho tấn công. Probe xe MixStyle đạt 0,9527, cao hơn Structural 0,9488; phép đo không ủng hộ giảm khả năng giải mã tuyến tính danh tính xe. Attack probe tăng nhẹ lên 0,7737. Các đối chứng constant/random/permuted được giữ đủ; phiên ghi độc lập và tính bất biến xe vẫn chưa được chứng minh.
\begin{longtable}{P{4.4cm}P{4.8cm}P{1.6cm}P{2.2cm}}
\caption{Ngoại bộ: gộp cửa sổ trong dataset/seed rồi trung bình seed; FAR phần trăm}\label{tab:mixstyle-external}\\\toprule
Dataset & Pipeline & Recall & FAR (\%)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Dataset & Pipeline & Recall & FAR (\%)\\\midrule
\endhead
CAN\_MIRGU\_attack & raw & 0.5848 & 59.1759\\
CAN\_MIRGU\_attack & structural & 0.0546 & 2.7018\\
CAN\_MIRGU\_attack & structural\_mixstyle & 0.0486 & 1.8267\\
CAN\_MIRGU\_benign & raw & -- & 60.6151\\
CAN\_MIRGU\_benign & structural & -- & 6.6311\\
CAN\_MIRGU\_benign & structural\_mixstyle & -- & 5.9049\\
CICIoV2024 & raw & 0.6462 & 100.0000\\
CICIoV2024 & structural & 1.0000 & 100.0000\\
CICIoV2024 & structural\_mixstyle & 1.0000 & 100.0000\\
Opel\_Astra\_DoS & raw & 1.0000 & 43.8502\\
Opel\_Astra\_DoS & structural & 1.0000 & 31.5345\\
Opel\_Astra\_DoS & structural\_mixstyle & 1.0000 & 33.4282\\
Opel\_Astra\_benign & raw & -- & 43.8417\\
Opel\_Astra\_benign & structural & -- & 30.9805\\
Opel\_Astra\_benign & structural\_mixstyle & -- & 32.8628\\
Renault\_Clio\_DoS & raw & 0.9995 & 33.1029\\
Renault\_Clio\_DoS & structural & 0.9984 & 0.1886\\
Renault\_Clio\_DoS & structural\_mixstyle & 0.9984 & 0.1467\\
Renault\_Clio\_benign & raw & -- & 33.4437\\
Renault\_Clio\_benign & structural & -- & 0.1656\\
Renault\_Clio\_benign & structural\_mixstyle & -- & 0.1288\\
\bottomrule\end{longtable}
MIRGU attack có recall MixStyle 0,0486 và FAR 1,8267\%, so với Structural 0,0546 và 2,7018\%: giảm báo động giả đi kèm bỏ sót nhiều hơn. CICIoV vẫn có recall và FAR đều 100\%, nghĩa là dự đoán toàn attack. Renault DoS giữ recall 0,9984 và FAR giảm từ 0,1886\% xuống 0,1467\%, nhưng chưa đạt 0,1\%. Opel FAR tăng so với Structural. Các tập benign-only giữ recall/AP không xác định; giữ nguyên loại trừ OTIDS và cách ly CICIoV SPEED.
\Needspace{18\baselineskip}
\begin{longtable}{P{2cm}P{5.5cm}P{2.2cm}P{2.2cm}}
\caption{Đo lại cùng phiên, batch một, 900 cửa sổ mỗi cấu hình; ms}\label{tab:mixstyle-runtime}\\\toprule
Thiết bị & Pipeline & Median & P95\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Thiết bị & Pipeline & Median & P95\\\midrule
\endhead
cpu & raw & 4.481 & 6.007\\
cpu & structural & 4.001 & 5.033\\
cpu & structural\_mixstyle & 3.785 & 4.427\\
cuda & raw & 3.962 & 5.786\\
cuda & structural & 3.836 & 4.617\\
cuda & structural\_mixstyle & 3.823 & 4.597\\
\bottomrule\end{longtable}
Phép đo gồm đọc CSV, kiểm tra, tạo cả hai biểu diễn và inference trong cùng phiên (giải thích mức $4{,}001\text{ ms}$ ở Bảng~\ref{tab:mixstyle-runtime} khác với $6{,}176\text{ ms}$ ở Bảng~\ref{tab:extension-runtime} do khác biệt tải nền/cache phiên đo, đồng thời thuần forward suy luận trên CPU chỉ tốn $0{,}731\text{ ms}$ như đã tách trong Bảng~\ref{tab:runtime-decomp}); mỗi lần có 20 warmup và 300 mẫu, lặp ba lần. GPU trước đo tải 2\% và có khoảng 6,9 GB VRAM trống. Máy bàn dùng chung, cache, thứ tự đo và tần số xung nhịp hạn chế diễn giải chênh lệch nhỏ; chưa chứng minh MixStyle nhanh hơn. Phép đo này cũng chưa bao gồm độ trễ thu gom cửa sổ $32\text{--}64\text{ ms}$ của thiết kế W64 hay kiểm định deadline trên ECU thực tế.
Kết quả này bổ sung một đánh đổi có đối chứng, không làm thay đổi kết luận chính về hiệu năng chuyển giao zero-shot. Một số chỉ số tăng nhưng điều kiện B và probe không hỗ trợ chọn MixStyle như lời giải tổng quát cho chuyển xe.

\subsection[Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính]{Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính (Benign Warmup Calibration)}\label{sec:benign-calibration}
Một nghịch lý thực nghiệm nổi bật khi đánh giá chuyển giao đa xe (Điều kiện B) là: dù biểu diễn Structural nâng AP từ 0,3781 lên 0,5554 (+17,74 điểm phần trăm chênh lệch ghép cặp; +17,73 điểm phần trăm chênh lệch trung bình) và MixStyle nâng lên 0,5815, recall vận hành tại ngưỡng nguồn $\tau_{\text{src}}$ ở điều kiện B lại thấp hơn Raw (73,83\% và 81,94\% so với 85,41\%), đồng thời FAR đích ở cả hai mô hình đều vượt $52\%$. Bản chất của sự phân kỳ này không nằm ở năng lực phân tách biểu diễn, mà nằm ở \textit{hiện tượng trôi dạt phân phối logit (threshold shift)}: khi chuyển sang phương tiện khác hãng sản xuất, nền logit lành tính bị dịch chuyển tĩnh, khiến ngưỡng cố định $\tau_{\text{src}}$ của xe nguồn không còn là điểm cắt tối ưu trên xe đích.

Để kiểm chứng giả thuyết này và đánh giá tính khả thi vận hành, nghiên cứu áp dụng cơ chế \textbf{Hiệu chuẩn nền lành tính không giám sát (Unsupervised Benign Warmup Calibration)} kết hợp bộ lọc sự kiện trượt $m$-trong-$n$ như đã thiết lập tại Mục~\ref{subsec:method-calibration}.

\subsubsection{Kết quả khôi phục điểm vận hành và phân tích thống kê vùng đuôi}
Thực nghiệm khảo sát ngân sách $K \in \{200, 500, 1000\}$ cửa sổ lành tính đầu tiên không rò rỉ ($K_{\text{valid}} = \min(K, \lfloor \text{prefix\_end} / 2 \rfloor)$) trên từng tệp xe đích ứng với các ngân sách FAR mục tiêu $\alpha \in \{0{,}1\%, 0{,}5\%, 1{,}0\%, 2{,}0\%\}$. Kết quả đánh giá trên toàn bộ phần cửa sổ hậu khởi động còn lại (post-warmup, không chồng lấn) được thể hiện ở Bảng~\ref{tab:benign-calibration-summary} và Hình~\ref{fig:calibration-recovery}. Phân tích thực nghiệm làm rõ hai khía cạnh thống kê quan trọng:
\begin{itemize}
    \item \textbf{Độ phân giải thống kê vùng đuôi ($K\alpha < 1$):} Tại $K=500$ và $\alpha=0{,}1\%$, kỳ vọng số mẫu vượt ngưỡng chỉ là $K\alpha = 0{,}5 < 1$, khiến ngưỡng thực nghiệm suy biến sát giá trị cực đại của mẫu khởi động và có phương sai cao; khi mở rộng ngân sách lên $K=1000$ ($K\alpha = 1$), độ ổn định đuôi được cải thiện rõ rệt (Bảng~\ref{tab:benign-calibration-summary}).
    \item \textbf{Khống chế cảnh báo giả theo giờ qua lọc gộp sự kiện ($m$-trong-$n$):} Với cửa sổ $W=64$ ở tốc độ bus $1.000\text{--}2.000\text{ khung/giây}$ ($56.250\text{--}112.500\text{ cửa sổ/giờ}$), ngay cả $\text{FAR}=0{,}1\%\text{--}1{,}0\%$ theo từng cửa sổ vẫn tương ứng khoảng $56\text{--}1.125$ cảnh báo giả mỗi giờ. Bộ lọc gộp quyết định trượt $m$-trong-$n$ (Bảng~\ref{tab:cal-baselines-mofn}) chứng minh khả năng triệt tiêu phần lớn các cảnh báo giả đột xuất này.
\end{itemize}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{figs/calibration_recovery_comparison.png}
\caption{Đánh giá khôi phục điểm vận hành qua hiệu chuẩn nền lành tính xe đích: (a)--(b) Đường cong Recall theo ngân sách FAR thực nghiệm tại $K=500$; (c)--(d) Điểm F1 theo từng loại tấn công ở điều kiện B và D vẽ tại $K=1000$, ngân sách FAR $1{,}0\%$ (bổ sung bảng đối chiếu chi tiết tại $K \in \{200, 500, 1000\}$ ở Bảng~\ref{tab:benign-calibration-summary}).}\label{fig:calibration-recovery}
\end{figure}

\Needspace{18\baselineskip}
{\small\setlength{\tabcolsep}{4.5pt}
\begin{longtable}{P{0.7cm}P{0.9cm}P{1.7cm}P{3.1cm}P{2.2cm}P{1.4cm}P{1.2cm}P{1.2cm}}
\caption{Hiệu năng hiệu chuẩn nền lành tính theo $K \in \{200, 500, 1000\}$ (trung bình 4 set; trong ngoặc là trung bình 3 xe đích khử lặp)}\label{tab:benign-calibration-summary}\\\toprule
ĐK & $K$ & Ngân sách & Pipeline & Recall (3-xe) & FAR (\%) & AP & F1\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
ĐK & $K$ & Ngân sách & Pipeline & Recall (3-xe) & FAR (\%) & AP & F1\\\midrule
\endhead
B & 200 & 1,0\% & Structural + MixStyle & 0.4734 (0.4949) & 1.2163 & 0.5832 & 0.5344\\
B & 500 & 0,1\% & Raw & 0.3177 (0.3743) & 0.1727 & 0.3803 & 0.3810\\
B & 500 & 0,1\% & Structural & 0.3117 (0.3460) & 0.1024 & 0.5607 & 0.4227\\
B & 500 & 0,1\% & Structural + MixStyle & \textbf{0.3749} (0.3999) & 0.1077 & \textbf{0.5845} & \textbf{0.4955}\\
B & 500 & 1,0\% & Raw & 0.3373 (0.3922) & 1.0509 & 0.3803 & 0.3788\\
B & 500 & 1,0\% & Structural & 0.4042 (0.4303) & 0.8545 & 0.5607 & 0.4748\\
B & 500 & 1,0\% & Structural + MixStyle & \textbf{0.4859} (0.5042) & 1.0752 & \textbf{0.5845} & \textbf{0.5450}\\
B & 1000 & 0,1\% & Structural + MixStyle & 0.4002 (0.4246) & 0.0999 & 0.5864 & 0.5150\\
B & 1000 & 1,0\% & Structural + MixStyle & \textbf{0.5141} (0.5218) & 0.9710 & \textbf{0.5864} & \textbf{0.5697}\\
\midrule
D & 200 & 1,0\% & Structural + MixStyle & 0.2124 (0.2283) & 0.5086 & 0.3680 & 0.2863\\
D & 500 & 0,1\% & Raw & 0.0645 (0.0834) & 0.1087 & 0.1692 & 0.1018\\
D & 500 & 0,1\% & Structural & 0.1196 (0.1403) & 0.0845 & 0.3411 & 0.1793\\
D & 500 & 0,1\% & Structural + MixStyle & \textbf{0.1363} (0.1611) & 0.0772 & \textbf{0.3702} & \textbf{0.2026}\\
D & 500 & 1,0\% & Raw & 0.0979 (0.1257) & 1.0818 & 0.1692 & 0.1195\\
D & 500 & 1,0\% & Structural & 0.2071 (0.2255) & 0.5750 & 0.3411 & 0.2728\\
D & 500 & 1,0\% & Structural + MixStyle & \textbf{0.2175} (0.2340) & 0.6529 & \textbf{0.3702} & \textbf{0.2852}\\
D & 1000 & 1,0\% & Structural + MixStyle & 0.2211 (0.2375) & 0.7078 & 0.3728 & 0.2869\\
\bottomrule\end{longtable}}

\Needspace{18\baselineskip}
\begin{longtable}{P{1.1cm}P{1.2cm}P{3.6cm}P{2.3cm}P{2.2cm}P{2.2cm}}
\caption{Phân rã theo từng set tại $K=500$, ngân sách $1{,}0\%$ (trung bình $\pm$ độ lệch chuẩn 3 seed)}\label{tab:cal-k-per-set}\\\toprule
ĐK & Set & Pipeline & Recall & FAR (\%) & F1\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
ĐK & Set & Pipeline & Recall & FAR (\%) & F1\\\midrule
\endhead
B & Set 1 & Raw & 0.9314 $\pm$ 0.0010 & 0.6413 $\pm$ 0.0863 & 0.9321 $\pm$ 0.0039\\
B & Set 1 & Structural & 0.7730 $\pm$ 0.2290 & 0.9938 $\pm$ 0.4096 & 0.8103 $\pm$ 0.1381\\
B & Set 1 & Structural + MixStyle & 0.8844 $\pm$ 0.0617 & 1.1225 $\pm$ 0.5147 & 0.8831 $\pm$ 0.0160\\
B & Set 2 & Raw & 0.1806 $\pm$ 0.1038 & 0.9213 $\pm$ 0.3416 & 0.2260 $\pm$ 0.1339\\
B & Set 2 & Structural & 0.3875 $\pm$ 0.0996 & 0.6876 $\pm$ 0.1789 & 0.4504 $\pm$ 0.1081\\
B & Set 2 & Structural + MixStyle & 0.3306 $\pm$ 0.2213 & 0.9543 $\pm$ 0.3823 & 0.3665 $\pm$ 0.2401\\
B & Set 3 & Raw & 0.1644 $\pm$ 0.0138 & 0.6386 $\pm$ 0.5029 & 0.2670 $\pm$ 0.0211\\
B & Set 3 & Structural & 0.2645 $\pm$ 0.2323 & 0.2704 $\pm$ 0.1984 & 0.3753 $\pm$ 0.2592\\
B & Set 3 & Structural + MixStyle & 0.5314 $\pm$ 0.1305 & 0.2227 $\pm$ 0.1058 & 0.6773 $\pm$ 0.1020\\
B & Set 4 & Raw & 0.0726 $\pm$ 0.0614 & 2.0025 $\pm$ 2.1866 & 0.0900 $\pm$ 0.0599\\
B & Set 4 & Structural & 0.1919 $\pm$ 0.0215 & 1.4660 $\pm$ 0.4026 & 0.2633 $\pm$ 0.0341\\
B & Set 4 & Structural + MixStyle & 0.1974 $\pm$ 0.0260 & 2.0014 $\pm$ 1.0755 & 0.2529 $\pm$ 0.0186\\
\midrule
D & Set 1 & Structural + MixStyle & 0.0027 $\pm$ 0.0019 & 0.1365 $\pm$ 0.0322 & 0.0047 $\pm$ 0.0033\\
D & Set 2 & Structural + MixStyle & 0.1057 $\pm$ 0.0978 & 0.9910 $\pm$ 0.5286 & 0.1100 $\pm$ 0.1058\\
D & Set 3 & Structural + MixStyle & 0.2299 $\pm$ 0.0542 & 0.4899 $\pm$ 0.0776 & 0.3673 $\pm$ 0.0703\\
D & Set 4 & Structural + MixStyle & 0.5316 $\pm$ 0.0459 & 0.9941 $\pm$ 0.5038 & 0.6588 $\pm$ 0.0210\\
\bottomrule\end{longtable}

\Needspace{18\baselineskip}
{\small\setlength{\tabcolsep}{4.5pt}
\begin{longtable}{P{4.2cm}P{0.9cm}P{1.6cm}P{1.6cm}P{1.6cm}P{1.65cm}P{1.3cm}}
\caption{Đối chứng calibration cho baseline và kỹ thuật lọc gộp sự kiện ($K=500$, ngân sách $1{,}0\%$)}\label{tab:cal-baselines-mofn}\\\toprule
Phương pháp / Quy tắc & ĐK & Recall & FAR (\%) & F1 & Precision & AP\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Phương pháp / Quy tắc & ĐK & Recall & FAR (\%) & F1 & Precision & AP\\\midrule
\endhead
CANBERT+ adapted (Calib. $K=500$) & B & 0.2428 & 20.5601 & 0.1078 & -- & 0.0997\\
CANLP-char-DNN adapted (Calib. $K=500$) & B & 0.6578 & 68.2462 & 0.0794 & -- & 0.0564\\
Raw TF (1-of-1) & B & 0.3373 & 1.0509 & 0.3788 & -- & 0.3803\\
Structural TF (1-of-1) & B & 0.4042 & 0.8545 & 0.4748 & 0.6846 & 0.5607\\
Structural + MixStyle (1-of-1) & B & 0.4859 & 1.0752 & 0.5450 & 0.6603 & 0.5845\\
Structural + MixStyle (2-of-3) & B & 0.4911 & \textbf{0.2234} & 0.5903 & 0.8496 & --\\
Structural + MixStyle (2-of-5) & B & \textbf{0.5351} & 0.5491 & \textbf{0.6141} & 0.7704 & --\\
Structural + MixStyle (3-of-5) & B & 0.4926 & \textbf{0.1387} & 0.5947 & \textbf{0.9131} & --\\
\midrule
Structural + MixStyle (1-of-1) & D & 0.2175 & 0.6529 & 0.2852 & 0.4857 & 0.3702\\
Structural + MixStyle (2-of-3) & D & 0.1995 & \textbf{0.1160} & 0.2820 & 0.5738 & --\\
Structural + MixStyle (3-of-5) & D & 0.1919 & \textbf{0.0575} & 0.2747 & \textbf{0.6091} & --\\
\bottomrule\end{longtable}}

\subsubsection{Phân tích kết quả, đầu độc khởi động và mở rộng ngoại bộ}
Số liệu từ Bảng~\ref{tab:benign-calibration-summary}--\ref{tab:cal-baselines-mofn} và Hình~\ref{fig:calibration-recovery} cho phép rút ra năm kết luận định lượng (với sự thận trọng trước biến thiên giữa các xe và seed):
\begin{enumerate}
    \item \textbf{Chuyển hóa ưu thế AP thành hiệu năng vận hành so với mọi đối thủ hiệu chuẩn:} Khi áp dụng cùng cơ chế hiệu chuẩn $K=500$ ở ngân sách $1{,}0\%$ trên điều kiện B, cả hai đối thủ \code{CANBERT+} (FAR $20{,}56\%$, AP $0{,}0997$, F1 $0{,}1078$) lẫn \code{CANLP-char-DNN} (FAR $68{,}25\%$, AP $0{,}0564$, F1 $0{,}0794$) đều không thể neo giữ báo động giả do điểm số lành tính bị ép cục bộ. Trái lại, Raw giữ FAR gần mục tiêu ($1{,}05\%$) nhưng recall chỉ đạt $33{,}73\%$; Structural ($40{,}42\%$) và Structural+MixStyle ($48{,}59\%$, trung bình 3 xe đích $50{,}42\%$) khai thác tốt thứ tự xếp hạng vượt trội (AP $0{,}5845$). Trên từng set (Bảng~\ref{tab:cal-k-per-set}), hiệu quả tăng rõ ở Set 1 ($88{,}44\%$) và Set 3 ($53{,}14\%$) nhưng vẫn khiêm tốn ở Set 4 ($19{,}74\%$), cho thấy khoảng trống lớn giữa các loại tấn công.
    \item \textbf{Hiệu quả lọc cảnh báo giả qua gộp sự kiện ($m$-of-$n$):} Ở điều kiện B của Structural+MixStyle, áp dụng bộ lọc trượt \code{2-of-3} cắt giảm FAR gần $5\times$ xuống $0{,}2234\%$ (Precision tăng lên $0{,}8496$) mà vẫn nâng nhẹ recall lên $49{,}11\%$; quy tắc \code{3-of-5} đưa FAR xuống $0{,}1387\%$ (Precision $0{,}9131$, F1 $0{,}5947$) và ở điều kiện D giảm FAR còn $0{,}0575\%$ (Precision $0{,}6091$). Tuy nhiên, trên nhãn cấp cửa sổ $W=64$, bộ lọc $m$-of-$n$ không chứng minh khả năng định vị từng frame tấn công đơn lẻ.
    \item \textbf{Rủi ro an toàn khi tiền tố khởi động bị đầu độc (Warmup Poisoning):} Một giả định cốt lõi của hiệu chuẩn không giám sát là đoạn khởi động hoàn toàn sạch. Thử nghiệm tiêm $1\%, 2\%, 5\%$ cửa sổ tấn công vào tập $K=500$ của Structural+MixStyle cho thấy ngưỡng phân vị bị kéo lên nhanh: ở ngân sách $1{,}0\%$ điều kiện B, recall giảm tương ứng từ $48{,}59\%$ xuống $47{,}24\%$ ($1\%$), $44{,}95\%$ ($2\%$) và $32{,}85\%$ ($5\%$); đặc biệt ở ngân sách chặt $0{,}1\%$, chỉ $1\%$ nhiễm bẩn làm recall tụt hơn một nửa từ $37{,}49\%$ xuống $16{,}06\%$ (và xuống $5{,}33\%$ ở mức $5\%$). Vì vậy hệ thống không tự bảo vệ nếu kẻ tấn công chèn lưu lượng độc hại ngay khi khởi động xe.
    \item \textbf{Phân rã theo kiểu tấn công:} Ở B ($K=500, 1{,}0\%$), Structural+MixStyle đạt recall $92{,}42\%$ trên DoS (F1 $0{,}9438$ so với Raw $0{,}5040$) và $72{,}35\%$ trên Systematic (F1 $0{,}7177$; xu hướng F1 tương tự được minh họa tại $K=1000$ trên Hình~\ref{fig:calibration-recovery}c--d); nhưng các tấn công tinh vi chỉ thay đổi nhẹ giá trị tín hiệu như \code{force-neutral} ($0{,}38\%$) hay \code{speed} ($7{,}31\%$) vẫn có recall thấp. Ở D, \code{speed} đạt $40{,}13\%$ (Raw $1{,}03\%$) và \code{fuzzing} đạt $39{,}71\%$.
    \item \textbf{Kiểm chứng ngoại bộ đầy đủ ($K=500$, trung bình $\pm$ độ lệch chuẩn 3 seed):} Trên bốn tập ngoại bộ sau hiệu chuẩn tại ngân sách $0{,}1\%$ ($100/100\text{k}$):
    \begin{itemize}
        \item \textit{Opel\_Astra\_DoS:} FAR của Structural và MixStyle giảm từ $>31\%$ xuống $0{,}271\% \pm 0{,}266\%$ và $0{,}167\% \pm 0{,}079\%$ với recall duy trì $1{,}0000$ (F1 $0{,}9755$ và $0{,}9846$).
        \item \textit{Renault\_Clio\_DoS:} Structural và MixStyle giữ recall $0{,}9984 \pm 0{,}0000$ ($99{,}84\%$, F1 $0{,}9992$) với FAR triệt tiêu về $0{,}0000\%$ trên cả tập DoS và tập lành tính (Raw $0{,}0508\%$ benign).
        \item \textit{CICIoV2024:} Dù điểm suy biến FAR $100\%$ bị loại bỏ ($0{,}047\% \pm 0{,}041\%$ cho Structural và $0{,}086\% \pm 0{,}093\%$ cho MixStyle ở $0{,}1\%$), hiệu năng phát hiện lại có phương sai giữa các seed cực lớn: Structural đạt trung bình recall $0{,}3336 \pm 0{,}5242$ ($\text{AP}=0{,}9172 \pm 0{,}0711$), còn MixStyle chỉ đạt $0{,}0001 \pm 0{,}0002$ ($\text{AP}=0{,}4397 \pm 0{,}4687$, tăng lên $0{,}3229 \pm 0{,}5593$ tại $1{,}0\%$), chứng tỏ độ nhạy điểm cắt cực đoan giữa các seed khởi tạo.
        \item \textit{CAN\_MIRGU:} Trên tập có gán nhãn tấn công (bao gồm cả suspension), recall sau hiệu chuẩn vẫn rất thấp dù FAR được kiểm soát: tại $0{,}1\%$ Structural chỉ đạt $0{,}0065 \pm 0{,}0015$ ($\text{FAR}=0{,}087\%$) và MixStyle đạt $0{,}0072 \pm 0{,}0021$ ($\text{FAR}=0{,}094\%$); kể cả tại $1{,}0\%$ recall cũng chỉ là $0{,}0275 \pm 0{,}0041$ và $0{,}0308 \pm 0{,}0068$ ($\text{AP}=0{,}4282$ và $0{,}4394$). Trên tập \code{CAN\_MIRGU\_benign}, FAR thực tế đạt $1{,}135\%$ ($0{,}1\%$) và $1{,}236\%$ ($1{,}0\%$).
    \end{itemize}
\end{enumerate}

\subsubsection{Đối chứng chỉ dùng dữ liệu đích \texorpdfstring{$K=500$}{K=500} không huấn luyện nguồn}\label{subsec:target-only-k500}
Để phản biện câu hỏi liệu có cần huấn luyện Transformer trên xe nguồn hay không một khi hệ thống đã cho phép thu thập $K=500$ cửa sổ lành tính đầu phiên trên xe đích, Bảng~\ref{tab:target-only-k500} đối chứng hai bộ dò bất thường thuần không giám sát chỉ khớp trên tiền tố $K=500$ của từng tệp xe đích (0 mẫu nguồn, 0 nhãn tấn công): (i) \code{IsolationForest} (200 cây) trên vector tóm tắt cửa sổ Structural 60D (\code{mean}+\code{std}), và (ii) khoảng cách năng lượng hiệp phương sai \code{Mahalanobis} chính quy hóa co $0{,}1$ trên Raw 56D (\code{mean}+\code{std}) và Structural 60D, dưới cả hai giao thức lấy ngưỡng đồng bộ ($K=500$ cùng khớp hiệp phương sai lẫn phân vị) và giao thức tách đôi chống rò rỉ nội mẫu (\textit{split-warmup}: 250 cửa sổ đầu khớp $\mu,\Sigma$ và 250 cửa sổ tiếp theo chọn ngưỡng phân vị).

\Needspace{16\baselineskip}
{\small\setlength{\tabcolsep}{4pt}
\begin{longtable}{P{4.2cm}P{0.7cm}P{1.1cm}P{2.2cm}P{1.5cm}P{1.4cm}P{2.1cm}}
\caption{Đối chứng chỉ dùng nền đích $K=500$ (0 huấn luyện nguồn; trong ngoặc là trung bình 3 xe đích khử lặp)}\label{tab:target-only-k500}\\\toprule
Phương pháp (0 nguồn) & ĐK & $\alpha$ & Recall (3-xe) & FAR (\%) & F1 & AP (3-xe)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Phương pháp (0 nguồn) & ĐK & $\alpha$ & Recall (3-xe) & FAR (\%) & F1 & AP (3-xe)\\\midrule
\endhead
IsolationForest St60 ($K=500$) & B & 0,1\% & 0.3174 (0.3786) & 0.195 & 0.3888 & 0.5989 (0.5945)\\
IsolationForest St60 ($K=500$) & B & 1,0\% & 0.3889 (0.4557) & 2.708 & 0.3575 & 0.5989 (0.5945)\\
Split-Mahalanobis Raw56 (250/250) & B & 0,1\% & 0.5867 (0.5858) & 1.825 & 0.6231 & 0.6349 (0.6206)\\
Split-Mahalanobis Raw56 (250/250) & B & 1,0\% & 0.6561 (0.6508) & 5.636 & 0.5712 & 0.6349 (0.6206)\\
Split-Mahalanobis St60 (250/250) & B & 0,1\% & \textbf{0.6581} (\textbf{0.6317}) & 1.225 & \textbf{0.6829} & \textbf{0.7048} (\textbf{0.6701})\\
Split-Mahalanobis St60 (250/250) & B & 1,0\% & 0.7007 (0.6759) & 4.999 & 0.5968 & \textbf{0.7048} (\textbf{0.6701})\\
\midrule
IsolationForest St60 ($K=500$) & D & 0,1\% & 0.2405 (0.2945) & 0.122 & 0.3238 & 0.5287 (0.5274)\\
IsolationForest St60 ($K=500$) & D & 1,0\% & 0.3931 (0.4531) & 1.713 & 0.4041 & 0.5287 (0.5274)\\
Split-Mahalanobis Raw56 (250/250) & D & 0,1\% & 0.6059 (0.6299) & 1.165 & 0.6185 & 0.6955 (0.6845)\\
Split-Mahalanobis Raw56 (250/250) & D & 1,0\% & 0.6588 (0.6893) & 5.244 & 0.5423 & 0.6955 (0.6845)\\
Split-Mahalanobis St60 (250/250) & D & 0,1\% & \textbf{0.6244} (\textbf{0.6359}) & 1.530 & \textbf{0.6344} & \textbf{0.7605} (\textbf{0.7244})\\
Split-Mahalanobis St60 (250/250) & D & 1,0\% & 0.7193 (0.7268) & 7.564 & 0.5547 & \textbf{0.7605} (\textbf{0.7244})\\
\midrule
\multicolumn{7}{P{13.4cm}}{\footnotesize Đối chiếu tham chiếu in-sample $K=500$ Mahalanobis St60: AP $\text{B}=0{,}7321$ ($\alpha=0{,}1\%$ FAR $0{,}026\%$, $\alpha=1{,}0\%$ trượt lên $6{,}291\%$); AP $\text{D}=0{,}7750$ ($\alpha=0{,}1\%$ FAR $0{,}023\%$, $\alpha=1{,}0\%$ trượt lên $1{,}959\%$).}\\
\bottomrule\end{longtable}}

Kết quả ở Bảng~\ref{tab:target-only-k500} làm nổi bật hai kết luận cân bằng quan trọng: (1) Một khi đã cho phép thu thập nền $K=500$ cửa sổ trên xe đích, mô hình mật độ đơn giản \code{Split-Mahalanobis St60} (chỉ dùng biểu diễn Structural 30 chiều ở dạng mean+std, không cần huấn luyện nguồn) đạt chất lượng xếp hạng AP vượt trội hơn Transformer huấn luyện từ nguồn (B: $0{,}7048$ so với $0{,}5845$; D: $0{,}7605$ so với $0{,}3702$ --- đặc biệt ở điều kiện D zero-day nơi bộ phân loại nhị phân nguồn quá khớp theo tấn công nguồn), và biểu diễn Structural tiếp tục thắng Raw đồng bộ trên mô hình chỉ dùng đích ($0{,}7048$ so với $0{,}6349$ ở B; $0{,}7605$ so với $0{,}6955$ ở D); (2) Tuy vậy, cái giá chí tử của ước lượng hiệp phương sai 60 chiều trên chỉ 250 cửa sổ tương quan thời gian là \textbf{mất kiểm soát báo động giả vùng đuôi}: tại ngân sách $\alpha=0{,}1\%$ và $1{,}0\%$, \code{Split-Mahalanobis St60} trượt FAR thực nghiệm lên $1{,}225\%\text{--}4{,}999\%$ ở B và $1{,}530\%\text{--}7{,}564\%$ ở D (vượt $5\times\text{--}15\times$ ngân sách), tương tự hiện tượng trượt FAR của \code{white\_energy} ($3{,}831\%$ ở Bảng~\ref{tab:benign-invariant-main}); trong khi Transformer nguồn đóng băng chỉ hiệu chuẩn \textbf{một ngưỡng vô hướng 1 chiều} giữ FAR thực sát mục tiêu ($0{,}102\%\text{--}0{,}108\%$ tại $\alpha=0{,}1\%$ và $0{,}855\%\text{--}1{,}075\%$ tại $\alpha=1{,}0\%$). Điều này lý giải vai trò bổ trợ rõ rệt giữa giàu thông tin cấu trúc của biểu diễn 30 chiều và tính ổn định phân vị của bộ mã hóa huấn luyện sẵn.

\subsection{Đánh giá học đa nguồn LOVO với bộ phân loại đối kháng có điều kiện}\label{sec:multisource-lovo}
Nhằm kiểm chứng liệu việc kết hợp nhiều xe nguồn trong huấn luyện kèm nhánh đối kháng miền có điều kiện (LOVO-cAdv DANN, đặc tả toán học tại Mục~\ref{subsec:method-lovo}) có thể tạo ra bộ phát hiện zero-shot hoạt động trực tiếp tại ngưỡng nguồn trên xe đích hay không, nghiên cứu thực hiện 48 lượt huấn luyện theo giao thức giữ ngoài một xe (LOVO) trên 4 dòng xe CTT (\textit{Forester, Impala, Silverado, Traverse}). Ngưỡng quyết định chỉ chọn trên validation của ba xe nguồn (FAR quan sát nguồn tối đa $99{,}87/100\text{k}$). Các mẫu thăm dò (probe) giữ ngoài theo nhóm recording-round và cân bằng ô xe $\times$ nhãn (cơ hội xe $25\%$, tấn công $50\%$). Kết quả tổng hợp trọng số đều 4 xe được trình bày trong Bảng~\ref{tab:multisource-lovo} và Hình~\ref{fig:multisource-lovo}.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{figs/multisource_lovo_overview.png}
\caption{Hiệu năng học đa nguồn LOVO (trung bình đều 4 xe giữ ngoài $\times$ 3 seed) tại ngưỡng validation nguồn và khả năng giải mã xe bằng probe (mức cơ hội $25\%$).}\label{fig:multisource-lovo}
\end{figure}

\begin{table}[htbp]\centering\small
\caption{Kết quả học đa nguồn LOVO (48 fit, trọng số đều 4 xe đích, ngưỡng chọn chỉ từ nguồn)}\label{tab:multisource-lovo}
\begin{tabular}{P{2.8cm}P{1.4cm}P{2.6cm}P{1.2cm}P{1.2cm}P{1.8cm}P{1.8cm}}
\toprule
Phương pháp & Recall & FAR /100k (\%) & AP & F1 & Probe xe (LR/MLP) & Probe atk (LR) \\ \midrule
Raw & 0.7885 & 69835.3 (69.84\%) & 0.2196 & 0.2182 & 99.74\% / 99.47\% & 61.51\% \\
Structural & \textbf{0.7211} & 37022.5 (37.02\%) & \textbf{0.6020} & 0.4073 & 94.49\% / 93.89\% & 80.47\% \\
Structural + cAdv & 0.7161 & 31974.5 (31.97\%) & 0.5970 & \textbf{0.4254} & \textbf{93.22\%} / \textbf{92.36\%} & \textbf{81.11\%} \\
Relative + cAdv & 0.6579 & \textbf{29721.1} (29.72\%) & 0.5764 & 0.4148 & 94.74\% / 93.96\% & 79.94\% \\
\midrule
\multicolumn{7}{P{13.6cm}}{\footnotesize \textit{Ghi chú:} Giá trị in đậm thể hiện kết quả tốt nhất trong các mô hình dựa trên cấu trúc đề xuất (Raw có Recall 0,7885 nhưng suy biến với FAR lên tới 69,84\% và AP chỉ 0,2196). Probe xe thấp hơn thể hiện ít rò rỉ danh tính xe hơn.}\\
\bottomrule
\end{tabular}
\end{table}

Số liệu Bảng~\ref{tab:multisource-lovo} mang lại bằng chứng phủ định quan trọng cho kịch bản zero-shot thuần nguồn đa xe: dù huấn luyện từ 3 xe nguồn khác nhau nâng AP của Structural lên $0{,}6020$ (so với Raw $0{,}2196$) và bổ sung nhánh đối kháng miền có điều kiện (\code{cAdv}) giảm nhẹ FAR nguồn đóng băng từ $37{,}02\%$ xuống $31{,}97\%$ (tăng F1 lên $0{,}4254$), mức FAR đích vẫn cực kỳ lớn và bất ổn theo từng xe. Phân rã từng xe đích của \code{structural\_cadv} cho thấy \textit{Traverse} đạt FAR $0{,}058\%$ (recall $51{,}35\%$, AP $0{,}6193$) và \textit{Impala} đạt FAR $0{,}473\%$ (recall $54{,}26\%$, AP $0{,}6314$), nhưng \textit{Silverado} bùng nổ FAR tới $47{,}46\%$ (recall $85{,}46\%$, AP $0{,}6485$) và \textit{Forester} tới $79{,}91\%$ (recall $95{,}40\%$, AP $0{,}4890$). Đồng thời, probe giải mã xe trên embedding đóng băng của \code{structural\_cadv} vẫn ở mức $93{,}22\%$ (LR) và $92{,}36\%$ (MLP). Kết quả xác nhận: ngay cả trong điều kiện đa nguồn có đối kháng DANN, bộ mã hóa vẫn giữ gần như nguyên vẹn thông tin phân biệt xe và không thể dùng chung một ngưỡng tĩnh cắt từ nguồn để vận hành trên xe chưa thấy.

\subsection[Triệt tiêu thông tin xe tuyến tính và điểm năng lượng]{Triệt tiêu thông tin xe tuyến tính (LEACE/INLP8) và phát hiện bất thường bằng điểm năng lượng}\label{sec:benign-invariant}
Từ thất bại của ngưỡng tĩnh nguồn ở Mục~\ref{sec:multisource-lovo}, mục này đánh giá thực nghiệm khung phân tách biểu diễn trên 96 pipeline hậu nghiệm (12 encoder Structural LOVO đóng băng $\times$ 8 nhánh phương pháp) kết hợp điểm bất thường năng lượng Mahalanobis (\code{white\_energy}) như đã thiết kế tại Mục~\ref{subsec:method-whitening}. Mỗi xe đích dành riêng một bản ghi lành tính xác thực (54.231 cửa sổ loại hẳn khỏi tập đánh giá, kèm phép kiểm tra nhạy \code{content\_disjoint} loại thêm 740 cửa sổ trùng nội dung W64 qua SHA-256). Các biến đổi \code{LEACE}, \code{INLP8} (dừng ở 8 chiều), \code{PCA8} và đầu hồi quy logistic (LR) chỉ fit trên ba xe nguồn. Kết quả tổng hợp được trình bày tại Bảng~\ref{tab:benign-invariant-main} và Hình~\ref{fig:benign-invariant}.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{figs/benign_invariant_overview.png}
\caption{Đối chiếu đồng thời phát hiện tấn công ($\alpha=1\%$, \code{content\_disjoint}), probe 4 xe trên biểu diễn 64 chiều và probe trên điểm rủi ro 1 chiều (mức cơ hội $25\%$).}\label{fig:benign-invariant}
\end{figure}

\begin{table}[htbp]\centering\small
\caption{So sánh làm trắng nền lành tính + xóa khái niệm tuyến tính ($\alpha=1{,}0\%$ chuẩn hóa, \code{content\_disjoint}; bổ sung \code{white\_energy})}\label{tab:benign-invariant-main}
\begin{tabular}{P{3.0cm}P{1.1cm}P{1.3cm}P{1.1cm}P{1.1cm}P{1.7cm}P{1.6cm}P{1.5cm}}
\toprule
Phương pháp & Recall & FAR (\%) & F1 & AP & Probe 64D (LR / MLP300) & MLP 1.500 vòng & Risk 1D (LR) \\ \midrule
Original / source thresh. & 0.7211 & 37.001 & 0.4096 & 0.6042 & 94.18\% / 93.46\% & 93.46\% & 33.40\% \\
Original / target thresh. & \textbf{0.5180} & 1.009 & \textbf{0.6032} & 0.6042 & 94.18\% / 93.46\% & -- & 27.58\% \\
Shared LR / target thresh. & 0.4469 & 0.889 & 0.5362 & 0.5544 & 94.18\% / 93.46\% & -- & 27.38\% \\
Benign diag + LR & 0.4239 & 0.990 & 0.5152 & 0.5243 & 65.63\% / 81.99\% & -- & 26.99\% \\
Benign whitening + LR & 0.3876 & 1.036 & 0.4705 & 0.4852 & 64.29\% / 65.63\% & -- & 26.92\% \\
Whitening + PCA8 + LR & 0.3765 & 1.100 & 0.4361 & 0.4603 & 54.08\% / 56.48\% & 53.68\% & 29.03\% \\
Whitening + LEACE + LR & 0.3321 & \textbf{0.844} & 0.4065 & 0.4242 & 44.96\% / 57.19\% & 57.17\% & \textbf{27.30\%} \\
Whitening + INLP8 + LR & 0.3013 & \textbf{0.844} & 0.3750 & 0.3715 & \textbf{37.53\%} / \textbf{43.97\%} & \textbf{42.01\%} & 28.90\% \\
\midrule
\code{white\_energy} ($\alpha=0{,}1\%$) & 0.4606 & \textbf{0.297} & \textbf{0.5918} & \textbf{0.6172} & -- & -- & -- \\
\code{white\_energy} ($\alpha=1{,}0\%$) & 0.6008 & 3.831 & 0.5323 & \textbf{0.6172} & -- & -- & -- \\
\midrule
\multicolumn{8}{P{13.8cm}}{\footnotesize \textit{Ghi chú:} Giá trị in đậm ở nửa trên thể hiện hiệu năng tốt nhất trong nhóm phân loại nhị phân có giám sát với $\alpha=1{,}0\%$; nửa dưới thể hiện điểm năng lượng không giám sát \code{white\_energy} (đạt Recall 0,6008 ở $\alpha=1{,}0\%$ và FAR 0,297\% ở $\alpha=0{,}1\%$).}\\
\bottomrule
\end{tabular}
\end{table}

Ba phát hiện phương pháp luận quan trọng rút ra từ Bảng~\ref{tab:benign-invariant-main} và Hình~\ref{fig:benign-invariant}:
\begin{enumerate}
    \item \textbf{Phân biệt triệt tiêu trên điểm rủi ro 1D và trên biểu diễn 64D:} Ngay cả khi không làm trắng hay xóa khái niệm, chỉ việc gập biểu diễn xuống một điểm rủi ro vô hướng 1 chiều và cắt ngưỡng đã hạ probe xe từ $33{,}40\%$ xuống $27{,}30\%\text{--}28{,}90\%$ (gần mức ngẫu nhiên $25\%$), trong khi probe trên biểu diễn 64 chiều vẫn đạt $94{,}18\%$. Kết luận độc lập xe dựa riêng vào probe điểm rủi ro là sai lệch về mặt đo lường.
    \item \textbf{Đánh đổi giữa xóa tuyến tính với phát hiện và phần dư phi tuyến:} Kết hợp làm trắng nền lành xe đích với LEACE hoặc INLP8 trên nguồn hạ mạnh probe tuyến tính 64 chiều từ $94{,}18\%$ xuống $44{,}96\%$ (LEACE) và $37{,}53\%$ (INLP8), vượt xa đối chứng chỉ làm trắng ($64{,}29\%$) hay nén PCA8 ($54{,}08\%$), đồng thời giữ probe tách lớp tấn công ở $79{,}05\%\text{--}81{,}44\%$. Tuy vậy, cái giá phải trả là recall phát hiện giảm từ $51{,}80\%$ (\textit{Original / target thresh.}, $\text{AP}=0{,}6042$) xuống còn $33{,}21\%$ (LEACE, $\text{AP}=0{,}4242$) và $30{,}13\%$ (INLP8, $\text{AP}=0{,}3715$), đặc biệt giảm sâu trên xe khó như \textit{Silverado} và \textit{Forester}. Hơn nữa, kiểm thử stress-test bằng bộ giải mã phi tuyến MLP chạy tới $1.500$ vòng vẫn thu được $57{,}17\%$ (LEACE) và $42{,}01\%$ (INLP8), xác nhận xóa tuyến tính không triệt tiêu hoàn toàn cấu trúc phi tuyến mang danh tính xe.
    \item \textbf{Tiềm năng của điểm năng lượng Mahalanobis trên không gian làm trắng (\code{white\_energy}):} Thay vì chiếu xóa chiều rồi phân loại bằng đầu LR nguồn, việc đo trực tiếp khoảng cách năng lượng trên embedding 64D đã làm trắng theo nền lành xe đích đạt $\text{AP} = 0{,}6172$ (cao nhất trong mọi phương án), tại $\alpha=0{,}1\%$ đạt recall $46{,}06\%$, FAR $0{,}297\%$ ($297{,}3/100\text{k}$), F1 $0{,}5918$ (Impala $59{,}09\%$, Silverado $53{,}97\%$, Traverse $52{,}33\%$, Forester $18{,}85\%$); tuy nhiên ở $\alpha=1{,}0\%$ FAR thực nghiệm trượt lên $3{,}83\%$ do tự tương quan thời gian của chuỗi CAN phá vỡ giả định phân phối i.i.d.\ dưới mẫu kiểm chuẩn $1.000$ cửa sổ lẻ.
\end{enumerate}

\section{Chi phí xử lý thực nghiệm và các đe dọa tính hợp lệ}
\subsection{Chi phí xử lý trên máy thực nghiệm và phân rã độ trễ}\label{sec:runtime}
Phép đo batch một tại Bảng~\ref{tab:extension-runtime} và Bảng~\ref{tab:mixstyle-runtime} thực hiện cùng kịch bản: đọc CSV từng khối (\code{accessory-2.csv}), kiểm tra/chuyển đổi, trích xuất đồng thời cả hai biểu diễn Raw 28D và Structural 30D, rồi suy luận (\code{batch\_size}=1, 20 cửa sổ warmup, 300 cửa sổ $\times$ 3 lần đo = 900 mẫu). Sự chênh lệch 35\%--48\% giữa lần đo ban đầu (CPU Structural median 6,176~ms) và lần đo lại cùng phiên MixStyle (4,001~ms) phản ánh khác biệt trạng thái hệ điều hành/bộ nhớ đệm giữa hai phiên đo trên máy bàn dùng chung, vì cả hai đều gộp chung chi phí I/O CSV và trích xuất kép đặc trưng vào con số tổng. Để cô lập chính xác chi phí thực của riêng mô hình IDS và khắc phục sự nhập nhằng này, Bảng~\ref{tab:runtime-decomp} trình bày phép đo phân rã ba thành phần độc lập trên đúng tập 900 cửa sổ đó.

\begin{longtable}{P{2cm}P{3.6cm}P{3.2cm}P{3.2cm}}
\caption{Thời gian xử lý cửa sổ tổng hợp gộp I/O và trích xuất kép (lần đo ban đầu, batch=1, ms)}\label{tab:extension-runtime}\\\toprule
Thiết bị & Biểu diễn & Median (ms) & P95 (ms)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Thiết bị & Biểu diễn & Median (ms) & P95 (ms)\\\midrule
\endhead
cpu & raw & 6.098 & 7.524\\
cpu & structural & 6.176 & 8.024\\
cuda & raw & 7.537 & 9.523\\
cuda & structural & 7.323 & 8.871\\
\bottomrule\end{longtable}

\begin{table}[htbp]\centering\small
\caption{Phân rã chi phí xử lý từng cửa sổ W64 ($N=900$, batch=1, đơn vị ms)}\label{tab:runtime-decomp}
\begin{tabular}{P{1.6cm}P{2.5cm}P{2.5cm}P{2.5cm}P{2.8cm}}
\toprule
Thiết bị & Đọc CSV (Median) & Trích xuất kép 28D+30D (Median) & Suy luận Structural (Median) & Tổng E2E Structural (Median / P95) \\ \midrule
CPU & 1.083 & 3.036 & 0.731 & 4.830 / 6.231 \\
CUDA & 0.932 & 2.285 & 1.150 & 4.402 / 5.291 \\
\bottomrule
\end{tabular}
\end{table}

Bảng~\ref{tab:runtime-decomp} làm rõ ba khía cạnh kỹ thuật quan trọng: (1) Thời gian suy luận thuần của \code{Structural Transformer} trên CPU chỉ là $0{,}731\text{ ms}$ (tương đương Raw $0{,}768\text{ ms}$) và nhanh hơn CUDA ở \code{batch=1} ($1{,}150\text{ ms}$) do chi phí truyền tensor CPU--GPU không đáng kể khi tính trên CPU; (2) Phần lớn thời gian đo E2E thực chất nằm ở khâu đọc chuỗi CSV ($1{,}083\text{ ms}$) và trích xuất đồng thời cả hai biểu diễn trong script benchmark ($3{,}036\text{ ms}$, có thể giảm xuống khoảng một nửa nếu triển khai chỉ chạy nhánh Structural trên luồng nhị phân socket/CAN thay vì phân tích CSV); (3) \textbf{Độ trễ thu gom cửa sổ ($32\text{--}64\text{ ms}$):} Vì thiết kế quyết định theo cửa sổ không chồng lặp $W=64$ khung tin (chỉ đưa ra dự đoán khi khung thứ 64 đến), trên bus CAN 500~kbps thực tế với lưu lượng $\sim 1.000\text{--}2.000\text{ khung/giây}$, tổng độ trễ đầu-cuối (end-to-end latency) từ khung tấn công đầu tiên của cửa sổ đến khi có cảnh báo tối thiểu phải cộng thêm thời gian chờ thu gom cửa sổ là $\approx 32\text{--}64\text{ ms}$ (tổng cộng $\approx 37\text{--}70\text{ ms}$ trên máy thực nghiệm). Do đó, phép đo máy bàn không thay thế kiểm định thời gian thực và deadline trên vi điều khiển ECU nhúng.


\subsubsection{Kiểm toán độ phức tạp kiến trúc, FLOPs và bộ nhớ trạng thái}\label{subsec:complexity-audit}
Bên cạnh thời gian thực thi đo trên máy bàn, Bảng~\ref{tab:model-complexity-audit} tổng hợp số tham số, MACs/cửa sổ, FLOPs/cửa sổ, dung lượng trọng số FP32 và bộ nhớ RAM cho bảng trạng thái lịch sử $H_k$ trên chuẩn CAN 11-bit. \code{Structural Transformer} chỉ bổ sung $128$ tham số ($+0{,}17\%$) và $8.192$ MACs/cửa sổ ($+0{,}15\%$) so với \code{Raw Transformer} ($5{,}37\text{M}$ so với $5{,}36\text{M}$ MACs), cùng $130{,}00\text{ KiB}$ RAM cố định cho bảng trạng thái 2.048 ID. Trái lại, \code{CANBERT+} tiêu thụ tới $54{,}25\text{M}$ tham số ($206{,}94\text{ MiB}$ FP32) và $27{,}24\text{G}$ MACs/cửa sổ ($54{,}48\text{G}$ FLOPs do chạy khối BERT 6 tầng $H=768$ lặp 64 lần cho từng khung $10$ token) — nặng gấp $720\times$ về tham số và $5.075\times$ về MACs/cửa sổ so với \code{Structural Transformer}.

\Needspace{14\baselineskip}
{\footnotesize\setlength{\tabcolsep}{3pt}
\begin{longtable}{P{3.5cm}P{1.0cm}P{1.7cm}P{2.5cm}P{2.5cm}P{1.5cm}P{1.4cm}}
\caption{Kiểm toán độ phức tạp tĩnh (Batch=1, $W=64$, đơn vị tính theo cửa sổ) và bộ nhớ trạng thái $H_k$}\label{tab:model-complexity-audit}\\\toprule
Mô hình & Chiều & Params & MACs & FLOPs & FP32 & RAM $H_k$\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Mô hình & Chiều & Params & MACs & FLOPs & FP32 & RAM $H_k$\\\midrule
\endhead
Raw Transformer & 28 & 75.170 & 5.359.680 & 10.719.360 & 293,63 KiB & 0,0 KiB\\
\textbf{Structural Transformer} & \textbf{30} & \textbf{75.298} & \textbf{5.367.872} & \textbf{10.735.744} & \textbf{294,13 KiB} & \textbf{130,0 KiB}\\
Raw + Structural & 41 & 76.002 & 5.412.928 & 10.825.856 & 296,88 KiB & 130,0 KiB\\
Raw-no-ID & 17 & 74.466 & 5.314.624 & 10.629.248 & 290,88 KiB & 0,0 KiB\\
Structural-no-delta & 21 & 74.722 & 5.331.008 & 10.662.016 & 291,88 KiB & 0,0 KiB\\
Structural-no-payload & 22 & 74.786 & 5.335.104 & 10.670.208 & 292,13 KiB & 130,0 KiB\\
CANLP-char-DNN ($d=273$) & 273 & 43.458 & 2.768.896 & 5.537.792 & 169,76 KiB & 0,0 KiB\\
CANBERT+ (Set 1 vocab) & 10 & 54.247.853 & 27.240.881.280 & 54.481.762.560 & 206,94 MiB & 0,0 KiB\\
\bottomrule\end{longtable}}

\subsection{Đe dọa tính hợp lệ}\label{sec:threats-to-validity}
Tổng hợp toàn bộ thí nghiệm từ ma trận chính đến các mở rộng hậu nghiệm, khóa luận ghi nhận năm nhóm đe dọa tính hợp lệ cần lưu ý khi diễn giải kết quả:
\begin{enumerate}
    \item \textbf{Hiệu lực kết cấu và lặp xe đích:} Bốn set CTT chỉ dùng 4 xe vật lý và 3 xe đích phân biệt (Subaru Forester lặp ở Set 2 và Set 3), đồng thời chia tách vòng ghi theo hậu tố hoặc bản ghi riêng lẻ chưa có metadata chứng minh các chuyến lái hoàn toàn độc lập về thời điểm vật lý. Nhãn cửa sổ $W=64$ chỉ yêu cầu ít nhất một frame dương nên không đo độ chính xác định vị frame hay độ trễ trước thời điểm gây hại; trong ma trận đối sánh, các đối thủ (\code{CANBERT+}, \code{CANLP}, \code{AssocRules}) khác nhau về mức giám sát và ngân sách tham số, và ngưỡng \code{AssocRules} bị suy biến tại $1{,}0000000000000002$.
    \item \textbf{Độ ổn định thống kê vùng đuôi và hiệu chuẩn không nhãn:} Chọn ngưỡng $0{,}1\%$ FAR từ nguồn trên logits cross-entropy chưa hiệu chuẩn dễ gây sai lệch cực đoan (như Seed 42 Set 1 của Structural hay sụp đổ của CANBERT+). Trong chế độ hiệu chuẩn nền lành tính ($K=500$, $\alpha=0{,}1\%$), tích $K\alpha = 0{,}5 < 1$ giới hạn độ phân giải phân vị và nhạy cảm nếu đoạn khởi động bị nhiễm $1\%\text{--}5\%$ lưu lượng tấn công; tương tự, giao thức làm trắng ở Mục~\ref{sec:benign-invariant} đòi hỏi 2.000 cửa sổ phân bố đều trên một bản ghi lành tính đầy đủ chứ chưa tương đương vài giây khởi động trực tuyến và không cung cấp cam kết FAR distribution-free dưới chuỗi CAN tự tương quan.
    \item \textbf{Giới hạn giải mã tuyến tính và cảnh báo hội tụ probe:} Probe bằng hồi quy logistic và MLP vẫn ghi nhận cảnh báo tối ưu ở một số ô (98/576 ô ở LOVO, 133 ô ở nghiên cứu làm trắng, bao gồm các ô đối chứng); đồng thời giảm probe tuyến tính hay probe điểm rủi ro 1D không chứng minh tính bất biến phi tuyến khi MLP 1.500 vòng vẫn giữ $42{,}01\%\text{--}57{,}17\%$.
    \item \textbf{Tính hậu nghiệm và thứ tự tệp vật lý:} Các vòng ablation, MixStyle, Calibration, LOVO và Benign Whitening đều được thiết kế sau khi đã quan sát dữ liệu 4 set ban đầu; nhánh đánh giá content-only giữ thứ tự dòng CSV dựa trên chứng cứ kiểm toán mọi độ đảo ngược timestamp đều $\le 7{,}895\text{ ms}$, song không thay thế được đánh giá trên bộ dữ liệu có chronology vật lý xác thực và trên xe hoàn toàn mới chưa từng tham gia quá trình nghiên cứu.
    \item \textbf{Khoảng cách từ máy bàn đến ECU nhúng:} Các phép đo thời gian tại Mục~\ref{sec:runtime} được thực hiện trên CPU/GPU máy bàn với \code{batch=1}; thời gian thực thi chưa phản ánh tài nguyên hạn chế, bus contention hoặc ràng buộc deadline cứng của vi điều khiển ECU trên xe thật, và mọi cấu hình vẫn cộng thêm $32\text{--}64\text{ ms}$ chờ gom đủ cửa sổ $W=64$.
\end{enumerate}

\section{Tóm tắt chương}
Chương này đã trình bày đầy đủ chuỗi thực nghiệm đối chứng từ đánh giá zero-shot 60 đơn vị IDS, nghiên cứu cắt bỏ thành phần biểu diễn và kích thước cửa sổ, chẩn đoán thăm dò tuyến tính, kiểm thử ngoại bộ trên 57 bản ghi cho tới các thí nghiệm thích ứng miền (MixStyle, LOVO-cAdv, LEACE/INLP8) và khôi phục vận hành qua hiệu chuẩn nền lành tính. Các kết luận khoa học cốt lõi, giới hạn và hướng phát triển được đúc kết trong \hyperref[chap:conclusion]{Phần Kết luận và hướng phát triển}.

\chap{Kết luận và hướng phát triển}\label{chap:conclusion}
\sect{Tổng kết các kết quả nghiên cứu chính}
Qua quá trình thực nghiệm đối chứng nghiêm ngặt trên nhiều điều kiện chuyển giao đa xe và các bộ dữ liệu ngoại bộ, khóa luận rút ra các kết luận khoa học cốt lõi sau:

\textbf{Trả lời RQ1 (Về hiệu năng chuyển giao đa xe và sự phân kỳ ngưỡng):}
Giả thuyết cho rằng biểu diễn cấu trúc giúp tự động tăng độ nhạy (Recall) trên xe đích lạ ở cửa sổ $W=64$ dưới một ngưỡng tĩnh đóng băng từ nguồn ($\text{FAR} \le 100/100.000$) không được ủng hộ bởi thực nghiệm. Tại ngưỡng nguồn, Structural đạt recall 73,83\%, thấp hơn Raw khoảng 11,59 điểm phần trăm (85,41\%), đồng thời tỷ lệ báo động giả trên xe đích tăng cao ($\text{FAR} = 52{,}46\%$). Tuy nhiên, khi đánh giá chất lượng phân tách độc lập với ngưỡng quyết định cố định, biểu diễn Structural thể hiện ưu thế vượt trội: Average Precision (AP) ở điều kiện B tăng vọt từ 0,3781 lên 0,5554 (+17,74 điểm phần trăm chênh lệch ghép cặp; +17,73 điểm phần trăm chênh lệch trung bình so với Raw và vượt xa CANBERT+ 0,0970). Hiện tượng tỷ lệ báo động giả cao khi chuyển xe thực chất bắt nguồn từ sự trôi dạt phân phối logit (\textit{threshold shift}) giữa các hãng xe. Khi kết hợp với cơ chế hiệu chuẩn nền lành tính nhẹ ($K=500$, $\approx 16$ giây ở bus $2.000\text{ khung/giây}$ hay $\approx 32$ giây ở $1.000\text{ khung/giây}$ khi nổ máy xe) ở Mục~\ref{sec:benign-calibration}, biến thể Structural đơn nhánh đạt recall $40{,}42\%$ với FAR thực $0{,}8545\% < 1\%$, còn Structural+MixStyle nâng recall lên $48{,}59\%$ (FAR thực $1{,}0752\%$ ở ngân sách mục tiêu $1\%$, cần lọc gộp $2\text{-of-}3$ hoặc $3\text{-of-}5$ để đưa FAR thực về $\le 0{,}22\%$).

\textbf{Trả lời RQ2 (Về vai trò của các thành phần trong biểu diễn cấu trúc):}
Nghiên cứu chứng minh rằng việc loại bỏ CAN-ID thô một cách đơn thuần là không đủ để tạo ra một biểu diễn chuyển giao tốt; thực tế, bỏ ID khỏi mô hình thô làm AP điều kiện B sụt giảm nghiêm trọng từ 0,3781 xuống 0,2200. Các thành phần trong biểu diễn cấu trúc mang lại những đánh đổi rõ rệt: nhóm thống kê cục bộ (tần suất và thứ tự xuất hiện của ID trong cửa sổ) đóng vai trò sống còn đối với chất lượng xếp hạng và độ nhạy phát hiện bất thường (cắt bỏ thống kê cục bộ làm AP điều kiện B rơi tự do từ 0,5554 xuống 0,2894). Trong khi đó, việc loại bỏ byte payload tuyệt đối và chỉ giữ lại động học biến thiên $\Delta$payload giúp giải phóng mô hình khỏi nguy cơ quá khớp vào chữ ký tấn công nguồn, nâng mạnh hiệu năng phát hiện tấn công zero-day ở điều kiện C (AP đạt 0,4730 so với 0,2661 của Raw).

\textbf{Trả lời RQ3 (Về mức độ độc lập đặc thù xe và hiện tượng đan xen đặc trưng):}
Phép đo thăm dò tuyến tính (\textit{Linear Probe}) chỉ ra rằng biểu diễn Structural chỉ làm giảm nhẹ khả năng giải mã danh tính xe từ 0,9925 xuống 0,9488 (4,37 điểm phần trăm), vẫn cao hơn rất nhiều so với mức cơ hội ngẫu nhiên 0,2500. Phân tích chẩn đoán chuyên sâu bóc tách nguyên nhân rò rỉ: nhóm 10 chiều hình thái khung tin \code{dlc\_and\_masks} (gồm 9 chiều DLC và mặt nạ byte hợp lệ đạt $96{,}42\%$ cùng 1 chiều cờ hợp lệ $h_i$ đạt $27{,}46\%$) cho probe xe tổng hợp $96{,}70\%$, bên cạnh mật độ lưu lượng bus cục bộ ($75{,}65\%$) mang đậm dấu ấn kiến trúc mạng của từng hãng xe. Do hiện tượng đan xen đặc trưng (\textit{feature entanglement}), các kênh cấu trúc mang thông tin xe cũng chính là các tín hiệu nhạy bén nhất để phát hiện bất thường (probe tấn công tăng từ 0,6419 lên 0,7669). Vì vậy, việc cắt bỏ đặc trưng thô bạo sẽ phá hủy khả năng phát hiện xâm nhập. Điều này khẳng định biểu diễn cấu trúc chưa đạt được tính độc lập đặc thù xe hoàn toàn, và bài toán chuyển giao phương tiện đòi hỏi các kỹ thuật thích ứng miền như hiệu chuẩn ngưỡng thay vì kỳ vọng một biểu diễn zero-shot bất biến tuyệt đối.

\textbf{Trả lời RQ4 (Về năng lực tổng quát hóa ngoại bộ và khả năng ứng dụng thực tế):}
Kiểm thử trên 57 bản ghi ngoại bộ độc lập cho thấy khả năng chuyển giao thực tế phụ thuộc sâu sắc vào cấu trúc dữ liệu, từ điển định danh và chính sách gán nhãn. Mô hình đạt hiệu năng cao trên các kịch bản tấn công làm xáo trộn lưu lượng mạnh ở Renault Clio DoS (recall $0{,}9984$, tức $99{,}84\%$ với FAR $0{,}19\%$ tại ngưỡng nguồn và $0{,}00\%$ sau hiệu chuẩn nền lành tính) và Opel Astra DoS (recall $100\%$, FAR $0{,}17\%\text{--}0{,}27\%$ sau hiệu chuẩn), nhưng recall rất thấp trên CAN-MIRGU (0,65\%--3,08\% sau hiệu chuẩn, dù có cả chuỗi suspension không chèn frame) và biến động cực mạnh giữa 3 seed khởi tạo trên CICIoV2024 (Structural đạt trung bình recall $0{,}3336 \pm 0{,}5242$ với $\text{AP}=0{,}9172 \pm 0{,}0711$, trong khi MixStyle đạt $0{,}0001 \pm 0{,}0002$ ở ngân sách $0{,}1\%$ và $0{,}3229 \pm 0{,}5593$ ở $1{,}0\%$; đối chiếu định lượng cho thấy byte payload trung bình của CICIoV2024 có độ lệch chuẩn thậm chí nhỏ hơn CTT [$54{,}14$ so với $76{,}98$], nên độ nhạy thuộc về dịch chuyển từ điển ID/dạng thức hex không timestamp chứ không do biên độ payload). Phát hiện này cảnh báo không suy diễn hiệu năng từ một bộ dữ liệu đơn lẻ thành phổ quát, đồng thời khẳng định vai trò thiết yếu của kiểm toán dữ liệu và hiệu chuẩn nền đích.

\sect{Giá trị và giới hạn của nghiên cứu}
Khóa luận cung cấp đánh giá tái lập, đối chứng biểu diễn và chẩn đoán phân biệt chất lượng xếp hạng với chất lượng quyết định tại ngưỡng nguồn. Bất biến đổi tên ID là thuộc tính hẹp được kiểm tra, không đồng nghĩa độc lập xe. Các kết quả âm tính giới hạn rõ giả thuyết và ngăn diễn giải AP hoặc recall riêng lẻ như thành công triển khai.
\subsection*{Kết luận từ MixStyle, học đa nguồn LOVO và làm trắng--xóa thông tin xe}
MixStyle trên đơn nguồn tăng recall B so với Structural nhưng làm tăng FAR ($64{,}54\%$) và không giảm probe xe ($0{,}9527$). Nghiên cứu mở rộng sang học đa nguồn LOVO với đối kháng có điều kiện DANN (Mục~\ref{sec:multisource-lovo}) xác nhận thêm rằng ngay cả khi kết hợp 3 xe nguồn, ngưỡng tĩnh cắt từ nguồn vẫn để lọt FAR trung bình $31{,}97\%$ và probe xe còn $93{,}22\%$. Khi kết hợp làm trắng hiệp phương sai trên 2.000 cửa sổ lành xe đích với triệt tiêu tuyến tính LEACE/INLP8 fit trên nguồn (Mục~\ref{sec:benign-invariant}), linear probe trên điểm rủi ro 1D giảm về mức gần cơ hội ($27{,}30\%\text{--}28{,}90\%$), probe tuyến tính embedding 64D giảm từ $94{,}18\%$ xuống $37{,}53\%\text{--}44{,}96\%$, song vẫn đánh đổi $18{,}6\text{--}21{,}7$ điểm recall và để lại rò rỉ phi tuyến (MLP 1.500 vòng đạt $42{,}01\%\text{--}57{,}17\%$); trong khi đó điểm năng lượng làm trắng (\code{white\_energy}) đạt AP cao nhất ($0{,}6172$, recall $46{,}06\%$, FAR $0{,}30\%$ ở $\alpha=0{,}1\%$). Do cơ chế này vẫn phụ thuộc một bản ghi lành tính của xe đích để làm trắng và chọn ngưỡng, mục tiêu bộ phát hiện hoàn toàn bất biến phi tuyến zero-shot vẫn là bài toán mở.
\subsection*{Ý nghĩa và giới hạn của hiệu chuẩn nền lành tính}
Thí nghiệm ở Mục~\ref{sec:benign-calibration} xác nhận sự suy giảm của Structural ở ngưỡng nguồn $\tau_{\text{src}}$ chủ yếu do lệch ngưỡng giữa các hãng xe. Khi được hỗ trợ bởi ngân sách khởi động lành tính không nhãn ($K=500\text{--}1000$ cửa sổ), Structural+MixStyle đạt recall B $48{,}59\%\text{--}51{,}41\%$ (3 xe đích khử lặp: $50{,}42\%\text{--}52{,}18\%$) và D $21{,}75\%\text{--}22{,}11\%$, đồng thời lọc sự kiện $2\text{-of-}3$ hoặc $3\text{-of-}5$ cắt giảm FAR xuống $0{,}14\%\text{--}0{,}22\%$. Tuy nhiên, người triển khai phải kiểm soát rủi ro đầu độc giai đoạn khởi động ($1\%\text{--}5\%$ nhiễm bẩn làm suy giảm mạnh recall) và độ phân giải thống kê đuôi khi $K\alpha < 1$.

\sect{Hướng nghiên cứu tiếp theo}
Ưu tiên dữ liệu có chronology và phiên lái độc lập được xác minh (như ROAD dataset), đánh giá trên các mẫu xe mới hoàn toàn độc lập với vòng phát triển, và kiểm tra độ trễ theo sự kiện. Phát triển phương pháp làm mịn/bất biến phi tuyến có điều kiện kết hợp học đa nguồn và thích ứng trực tuyến bền vững trước đầu độc khởi động để vượt qua đánh đổi của triệt tiêu tuyến tính. Thực nghiệm nhúng phải đo tài nguyên, hàng đợi, chính sách đặt lại/eviction cho bảng $H_k$ (ignition-cycle reset và LRU cho ID 29-bit/CAN-FD 64-byte), chi phí chờ $32\text{--}64\text{ ms}$ gom cửa sổ và deadline trên phần cứng mục tiêu (ARM Cortex / Jetson Nano).

\appendix
\chapter{Chi tiết tái lập và nguồn gốc bằng chứng}\label{app:reproducibility}
\section{Provenance}\label{sec:app-provenance}
Ma trận chính gồm 60 đơn vị IDS (4 set $\times$ 3 seed $\times$ 5 phương pháp). Các vòng phân tích bổ sung và mở rộng hậu nghiệm bao gồm: 144 lượt huấn luyện mới cùng 24 baseline tái sử dụng trong nghiên cứu cắt bỏ và độ nhạy cửa sổ ($W \in \{32, 64, 128\}$); 12 lượt huấn luyện \code{Structural + MixStyle}; lưới quét hiệu chuẩn nền lành tính ($K \in \{200, 500, 1000\}$ và kiểm thử đầu độc/gộp $m$-of-$n$ trên các checkpoint đóng băng); 48 lượt huấn luyện học đa nguồn LOVO kèm đối kháng có điều kiện DANN (\code{multisource\_lovo\_v2}); 96 pipeline làm trắng nền lành tính kết hợp triệt tiêu tuyến tính LEACE/INLP8 và năng lượng Mahalanobis (\code{benign\_invariant\_pipeline}); cùng 120 lượt huấn luyện kiểm chứng bổ sung (48 lượt đối chứng Timed/Content trên 136 tệp đơn điệu, 48 lượt cửa sổ đẳng lượng $64.000$ khung, và 24 lượt phương sai lấy mẫu reservoir đa seed). Mọi phép thử 57 capture ngoại bộ không tương đương 57 phiên lái độc lập. Toàn bộ bảng số, bootstrap, phân phối score nguồn, mã băm kiểm chứng (\code{INDEPENDENT\_AUDIT.json}, \code{AUDIT.json}) và ledger loại trừ đều nằm trong gói bàn giao.

\subsection{Mã băm toàn vẹn và phiên bản mã nguồn tham chiếu}\label{subsec:app-hashes}
Để đảm bảo tính toàn vẹn và khả năng tái lập bit-to-bit tuyệt đối, mã băm SHA-256 của các tệp kê khai dữ liệu và mã commit Git của các phương pháp đối thủ được ghim cố định như sau:
\begin{itemize}
\item \textbf{Manifest cache dữ liệu CTT:} \texttt{\seqsplit{03a6bbf16efb4f583ca5566025c8bdc3cc0b65a7138a0a29f652505b2c367f29}}
\item \textbf{CANBERT+ commit:} \texttt{\seqsplit{4c81d9b08e6e0c17b8e70bdab518209e399f0dbe}}
\item \textbf{CANLP commit:} \texttt{\seqsplit{8df8bb74a7aa9925187f4faff05d6c8b824ba5d1}}
\item \textbf{CrySyS-AssocRules commit:} \texttt{\seqsplit{59b9f29f81b0f56f49c218cb1bd8e97552b8d22c}}
\end{itemize}

\section{Đặc tả có thời gian trong thiết kế ban đầu}
Thiết kế timed v2.1 có raw 29/structural 32 chiều (bổ sung $\Delta t$ và $\Delta t_{\text{ID}}$). Ma trận chính sử dụng nhánh content-only (28/30 chiều) để đảm bảo an toàn dữ liệu trước 100 tệp có timestamp đi lùi; kết quả thực nghiệm có đối chứng đầy đủ của nhánh timed trên 136 tệp đơn điệu nghiêm ngặt được báo cáo độc lập tại Bảng~\ref{tab:monotonic-timed-vs-content} ở Mục~\ref{subsec:monotonic-sensitivity}.
\section{Kiểm tra đặc trưng bằng tay}
Với $W=4$ và ID (A,B,A,A), tần suất lần lượt là (3/4,1/4,3/4,3/4); hạng xuất hiện đầu tiên chia số ID là (0,1/2,0,0), chia $W$ là (0,1/4,0,0). Các cặp AB,BA,AA xuất hiện một lần nên đặc trưng chuyển tiếp là (0,1/3,1/3,1/3). Payload một byte (10,20,13,15) cho delta cùng ID (0,0,3/255,2/255). Lịch sử tiếp tục qua biên cửa sổ/chunk và được reset khi đổi file. Không cần dựng timestamp để tính các giá trị này.
\section{Phân biệt kiểm toán và kết quả mô hình}
Các bảng lịch sử và kiểm toán công thức không được gộp với kết quả hiện hành. Đếm dòng CSV gồm tiêu đề khác đếm frame dữ liệu; decision theo frame khác decision theo window. Việc kiểm tra phần mềm hoặc sửa metric không tự chứng minh chất lượng IDS. Bản thảo và dữ liệu trước sửa được giữ trong archive, cùng báo cáo đối chiếu 42 tài liệu tham khảo.
Kiểm toán số đếm công bố dùng đúng phụ lục arXiv v1~\cite{lampe2023appendix}, không mặc định phụ lục journal giống hệt. Các số theo frame đó không được dùng để xếp hạng với quyết định W64.

\section{Tổng hợp Linear Probe trên toàn bộ 10 biến thể biểu diễn}\label{sec:app-96ckpt-probes}
Bảng~\ref{tab:app-96ckpt-probes} báo cáo trung bình và độ lệch chuẩn giải mã tuyến tính trên 96+24 checkpoint của toàn bộ 10 biến thể biểu diễn nội dung ($4\text{ set} \times 3\text{ seed} \times 10\text{ biểu diễn} \times 2\text{ đích} = 240$ phép đo).

\Needspace{14\baselineskip}
\begin{longtable}{P{5.4cm}P{3.4cm}P{3.4cm}}
\caption{Linear Probe trên 10 biểu diễn nội dung (4 set $\times$ 3 seed, mean $\pm$ std balanced accuracy)}\label{tab:app-96ckpt-probes}\\\toprule
Biểu diễn & Probe xe (cơ hội 0,25) & Probe tấn công (cơ hội 0,50)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Biểu diễn & Probe xe (cơ hội 0,25) & Probe tấn công (cơ hội 0,50)\\\midrule
\endhead
\code{raw} (28D) & 0.9925 $\pm$ 0.0099 & 0.6419 $\pm$ 0.0169\\
\code{id\_only} (11D) & 0.9908 $\pm$ 0.0088 & 0.6531 $\pm$ 0.0165\\
\code{raw\_plus\_structural} (41D) & 0.9915 $\pm$ 0.0069 & 0.7451 $\pm$ 0.0255\\
\code{structural\_no\_payload} (22D) & 0.9728 $\pm$ 0.0023 & \textbf{0.7780 $\pm$ 0.0214}\\
\code{raw\_no\_id} (17D) & 0.9693 $\pm$ 0.0246 & 0.6449 $\pm$ 0.0157\\
\code{structural\_no\_delta} (21D) & 0.9652 $\pm$ 0.0225 & 0.6874 $\pm$ 0.0167\\
\code{structural\_no\_local} (27D) & 0.9633 $\pm$ 0.0125 & 0.7502 $\pm$ 0.0392\\
\code{structural\_no\_transition} (29D) & 0.9531 $\pm$ 0.0143 & 0.7701 $\pm$ 0.0379\\
\code{structural\_no\_rank\_w} (29D) & 0.9516 $\pm$ 0.0156 & 0.7669 $\pm$ 0.0362\\
\textbf{\code{structural}} (30D) & \textbf{0.9488 $\pm$ 0.0121} & 0.7669 $\pm$ 0.0271\\
\bottomrule\end{longtable}

\section{Kiểm toán chi tiết kết quả B và D theo từng set và seed}\label{sec:app-comparison-sets}
Bảng~\ref{tab:comparison-sets} tổng hợp kết quả chi tiết của từng set dữ liệu tại Điều kiện B và D qua 3 seed cho các phương pháp nơ-ron hoạt động. Đối thủ \code{CrySyS-AssocRules/W64} suy biến ngưỡng nguồn tại $1{,}0000000000000002$ cho $\text{Recall}=0{,}0000 \pm 0{,}0000$ và $\text{FAR}=0{,}00$ trên mọi set.

\Needspace{14\baselineskip}
{\small\setlength{\tabcolsep}{3pt}
\begin{longtable}{P{1.4cm}P{0.7cm}P{3.4cm}P{3.4cm}P{3.4cm}P{2.6cm}}
\caption{B/D theo set; recall trung bình và độ lệch chuẩn ba seed; FAR trên 100.000}\label{tab:comparison-sets}\\\toprule
Set & ĐK & Raw TF & Structural TF & CANBERT+ adapted & CANLP-char-DNN\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Set & ĐK & Raw TF & Structural TF & CANBERT+ adapted & CANLP-char-DNN\\\midrule
\endhead
\code{set\_01} & B & 0.8165 $\pm$ 0.1960 (169) & 0.4950 $\pm$ 0.3875 (32) & 0.5730 $\pm$ 0.5111 (61471) & 0.1645 $\pm$ 0.0329 (21742)\\
\code{set\_01} & D & 0.0714 $\pm$ 0.1170 (10209) & 0.0005 $\pm$ 0.0008 (77) & 0.2344 $\pm$ 0.3023 (20027) & 0.0540 $\pm$ 0.0078 (4626)\\
\code{set\_02} & B & 1.0000 $\pm$ 0.0000 (100000) & 0.9663 $\pm$ 0.0366 (85422) & 0.9984 $\pm$ 0.0024 (99620) & 0.9772 $\pm$ 0.0059 (97042)\\
\code{set\_02} & D & 1.0000 $\pm$ 0.0000 (100000) & 0.8478 $\pm$ 0.1843 (84374) & 0.9943 $\pm$ 0.0084 (99499) & 0.9426 $\pm$ 0.0055 (97183)\\
\code{set\_03} & B & 0.6001 $\pm$ 0.3550 (61037) & 0.9741 $\pm$ 0.0290 (86687) & 0.0027 $\pm$ 0.0024 (35) & 0.0000 $\pm$ 0.0000 (0)\\
\code{set\_03} & D & 0.5744 $\pm$ 0.4664 (61722) & 0.9469 $\pm$ 0.0524 (91180) & 0.0004 $\pm$ 0.0006 (43) & 0.0000 $\pm$ 0.0000 (0)\\
\code{set\_04} & B & 1.0000 $\pm$ 0.0000 (100000) & 0.5179 $\pm$ 0.2763 (37705) & 0.9838 $\pm$ 0.0276 (98249) & 0.0000 $\pm$ 0.0000 (0)\\
\code{set\_04} & D & 1.0000 $\pm$ 0.0000 (100000) & 0.7827 $\pm$ 0.0870 (42942) & 0.9906 $\pm$ 0.0163 (98485) & 0.0000 $\pm$ 0.0000 (0)\\
\bottomrule
\multicolumn{6}{P{15.3cm}}{\footnotesize Giá trị trong bảng là Recall trung bình $\pm$ độ lệch chuẩn ba seed; số trong ngoặc là FAR trên 100.000 cửa sổ lành.}
\end{longtable}}

\section{Khoảng bootstrap recall 95\% có điều kiện theo file}\label{sec:app-comparison-ci}
Bảng~\ref{tab:comparison-ci} cung cấp khoảng tin cậy bootstrap 95\% có điều kiện theo capture cho chênh lệch recall giữa Structural và Raw ($\Delta R = \text{Structural} - \text{Raw}$).

\Needspace{14\baselineskip}
{\small\setlength{\tabcolsep}{3pt}
\begin{longtable}{P{1.4cm}P{1.0cm}P{1.4cm}P{4.0cm}P{1.4cm}P{4.0cm}}
\caption{Structural trừ Raw: khoảng bootstrap recall 95 phần trăm có điều kiện theo file}\label{tab:comparison-ci}\\\toprule
Set & Seed & $\Delta R_B$ & 95\% CI (Điều kiện B) & $\Delta R_D$ & 95\% CI (Điều kiện D)\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Set & Seed & $\Delta R_B$ & 95\% CI (Điều kiện B) & $\Delta R_D$ & 95\% CI (Điều kiện D)\\\midrule
\endhead
\code{set\_01} & 42 & -0.8782 & [-0.9602, -0.0012] (8 file) & -0.2064 & [-0.3391, -0.1134] (12 file)\\
\code{set\_01} & 43 & 0.1820 & [0.0000, 0.1990] (8 file) & -0.0005 & [-0.0055, 0.0029] (12 file)\\
\code{set\_01} & 44 & -0.2684 & [-0.2936, 0.0000] (8 file) & -0.0057 & [-0.0171, 0.0000] (12 file)\\
\code{set\_02} & 42 & -0.0019 & [-0.0042, 0.0000] (12 file) & -0.0181 & [-0.0541, -0.0046] (8 file)\\
\code{set\_02} & 43 & -0.0737 & [-0.1417, -0.0065] (12 file) & -0.3623 & [-0.6813, -0.1224] (8 file)\\
\code{set\_02} & 44 & -0.0256 & [-0.0487, -0.0027] (12 file) & -0.0761 & [-0.1335, -0.0217] (8 file)\\
\code{set\_03} & 42 & 0.1390 & [0.0407, 0.3676] (10 file) & 0.1164 & [0.0700, 0.1790] (14 file)\\
\code{set\_03} & 43 & 0.1993 & [-0.0147, 0.3589] (10 file) & 0.0936 & [-0.0181, 0.1775] (14 file)\\
\code{set\_03} & 44 & 0.7837 & [0.4389, 0.9840] (10 file) & 0.9076 & [0.8079, 0.9383] (14 file)\\
\code{set\_04} & 42 & -0.2963 & [-0.3695, -0.0491] (14 file) & -0.1661 & [-0.4748, -0.0452] (10 file)\\
\code{set\_04} & 43 & -0.3505 & [-0.4766, -0.0907] (14 file) & -0.1679 & [-0.4542, -0.0541] (10 file)\\
\code{set\_04} & 44 & -0.7996 & [-0.9750, -0.1600] (14 file) & -0.3177 & [-0.7372, -0.1051] (10 file)\\
\bottomrule
\multicolumn{6}{P{15.3cm}}{\footnotesize Ước lượng bootstrap 1.000 mẫu lặp có hoàn lại theo capture.}
\end{longtable}}

\section{Phân phối điểm số validation nguồn của AssocRules}\label{sec:app-assoc-scores}
Bảng~\ref{tab:assoc-scores} thống kê phân phối điểm số bất thường trên tập validation nguồn của mô hình \code{CrySyS-AssocRules/W64} qua 4 set và 3 seed.

\Needspace{14\baselineskip}
{\small\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{P{1.5cm}P{1.0cm}P{1.2cm}P{1.8cm}P{1.7cm}P{1.7cm}P{2.2cm}}
\caption{Score validation nguồn AssocRules; nhãn 0 là benign, 1 là tấn công}\label{tab:assoc-scores}\\\toprule
Set & Seed & Nhãn & N & Median & Max & Trùng max\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Set & Seed & Nhãn & N & Median & Max & Trùng max\\\midrule
\endhead
set\_01 & 42 & 0 & 75185 & 0.9937 & 1.0000 & 451\\
set\_01 & 42 & 1 & 1232 & 0.9939 & 1.0000 & 395\\
set\_01 & 43 & 0 & 75185 & 0.9968 & 1.0000 & 451\\
set\_01 & 43 & 1 & 1232 & 0.9971 & 1.0000 & 395\\
set\_01 & 44 & 0 & 75185 & 0.9934 & 1.0000 & 451\\
set\_01 & 44 & 1 & 1232 & 0.9937 & 1.0000 & 395\\
set\_02 & 42 & 0 & 121062 & 0.9972 & 1.0000 & 427\\
set\_02 & 42 & 1 & 4213 & 1.0000 & 1.0000 & 2966\\
set\_02 & 43 & 0 & 121062 & 0.9973 & 1.0000 & 422\\
set\_02 & 43 & 1 & 4213 & 1.0000 & 1.0000 & 2965\\
set\_02 & 44 & 0 & 121062 & 0.9991 & 1.0000 & 554\\
set\_02 & 44 & 1 & 4213 & 1.0000 & 1.0000 & 2973\\
set\_03 & 42 & 0 & 111163 & 0.9992 & 1.0000 & 493\\
set\_03 & 42 & 1 & 797 & 0.9992 & 1.0000 & 180\\
set\_03 & 43 & 0 & 111163 & 0.9992 & 1.0000 & 493\\
set\_03 & 43 & 1 & 797 & 0.9992 & 1.0000 & 180\\
set\_03 & 44 & 0 & 111163 & 0.9992 & 1.0000 & 493\\
set\_03 & 44 & 1 & 797 & 0.9992 & 1.0000 & 180\\
set\_04 & 42 & 0 & 70374 & 0.9990 & 1.0000 & 3305\\
set\_04 & 42 & 1 & 1142 & 0.9987 & 1.0000 & 100\\
set\_04 & 43 & 0 & 70374 & 0.9990 & 1.0000 & 2774\\
set\_04 & 43 & 1 & 1142 & 0.9987 & 1.0000 & 100\\
set\_04 & 44 & 0 & 70374 & 0.9990 & 1.0000 & 3271\\
set\_04 & 44 & 1 & 1142 & 0.9987 & 1.0000 & 100\\
\bottomrule\end{longtable}}

\section{Kiểm toán phân bố số cửa sổ W64 từng tệp ở Điều kiện B và D}\label{sec:app-bd-per-file-counts}
Bảng~\ref{tab:bd-per-file-counts} kiểm toán số lượng cửa sổ và biên độ mất cân bằng nhãn trên toàn bộ 88 tệp đánh giá điều kiện B và D.

\Needspace{14\baselineskip}
{\small\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{P{1.4cm}P{0.8cm}P{1.0cm}P{1.8cm}P{1.5cm}P{1.8cm}P{3.0cm}P{1.6cm}}
\caption{Kiểm toán phân bố số cửa sổ W64 từng tệp ở Điều kiện B và D}\label{tab:bd-per-file-counts}\\\toprule
Set & ĐK & Số tệp & Tổng cửa sổ & Tổng (+) & Tổng (--) & Tỷ lệ (+) min / med / max & Min (--) / tệp\\\midrule
\endfirsthead\caption[]{(tiếp theo)}\\\toprule
Set & ĐK & Số tệp & Tổng cửa sổ & Tổng (+) & Tổng (--) & Tỷ lệ (+) min / med / max & Min (--) / tệp\\\midrule
\endhead
\code{set\_01} & B & 8 & 100.745 & 8.430 & 92.315 & 0,22\% / 1,03\% / 43,91\% & 6.990\\
\code{set\_01} & D & 12 & 206.564 & 2.088 & 204.476 & 0,19\% / 0,79\% / 5,96\% & 4.857\\
\code{set\_02} & B & 12 & 131.953 & 2.578 & 129.375 & 0,31\% / 0,82\% / 10,90\% & 6.039\\
\code{set\_02} & D & 8 & 74.838 & 1.104 & 73.734 & 0,24\% / 1,12\% / 5,49\% & 4.378\\
\code{set\_03} & B & 10 & 107.093 & 8.834 & 98.259 & 1,72\% / 6,65\% / 34,70\% & 5.554\\
\code{set\_03} & D & 14 & 107.744 & 25.140 & 82.604 & 0,35\% / 6,48\% / 97,22\% & 202\\
\code{set\_04} & B & 14 & 271.995 & 13.782 & 258.213 & 0,03\% / 0,89\% / 97,81\% & 217\\
\code{set\_04} & D & 10 & 127.864 & 13.615 & 114.249 & 0,00\% / 8,03\% / 29,16\% & 5.193\\
\bottomrule\end{longtable}}

\backmatter\phantomsection\addcontentsline{toc}{chapter}{Tài liệu tham khảo}\bibliographystyle{plainnat}\begingroup\small\setlength{\bibsep}{2.5pt}\sloppy\bibliography{refs}\endgroup\end{document}

<!-- FILE: refs.bib -->
@inproceedings{koscher2010experimental,
  author    = {Koscher, Karl and Czeskis, Alexei and Roesner, Franziska and
               Patel, Shwetak and Kohno, Tadayoshi and Checkoway, Stephen and
               McCoy, Damon and Kantor, Brian and Anderson, Danny and
               Shacham, Hovav and Savage, Stefan},
  title     = {Experimental Security Analysis of a Modern Automobile},
  booktitle = {Proceedings of the IEEE Symposium on Security and Privacy},
  pages     = {447--462},
  year      = {2010}
}

@inproceedings{checkoway2011comprehensive,
  author    = {Checkoway, Stephen and McCoy, Damon and Kantor, Brian and
               Anderson, Danny and Shacham, Hovav and Savage, Stefan and
               Koscher, Karl and Czeskis, Alexei and Roesner, Franziska and
               Kohno, Tadayoshi},
  title     = {Comprehensive Experimental Analyses of Automotive Attack Surfaces},
  booktitle = {Proceedings of the 20th USENIX Security Symposium},
  year      = {2011}
}

@article{verma2024road,
  author  = {Verma, Miki E. and Bridges, Robert A. and Iannacone, Michael D. and
             Hollifield, Samuel C. and Moriano, Pablo and Hespeler, Steven C. and
             Kay, Bill and Combs, Frank L.},
  title   = {A Comprehensive Guide to {CAN} {IDS} Data and Introduction of the
             {ROAD} Dataset},
  journal = {PLOS ONE},
  volume  = {19},
  number  = {1},
  pages   = {e0296879},
  year    = {2024},
  doi     = {10.1371/journal.pone.0296879}
}

@article{axelsson2000base,
  title     = {The base-rate fallacy and the difficulty of intrusion detection},
  author    = {Axelsson, Stefan},
  journal   = {ACM Transactions on Information and System Security (TISSEC)},
  volume    = {3},
  number    = {3},
  pages     = {186--205},
  year      = {2000},
  publisher = {ACM},
  doi = {10.1145/357830.357849}
}

@inproceedings{sommer2010outside,
  title     = {Outside the Closed World: On Using Machine Learning for Network Intrusion Detection},
  author    = {Sommer, Robin and Paxson, Vern},
  booktitle = {2010 IEEE Symposium on Security and Privacy},
  pages     = {305--316},
  year      = {2010},
  organization = {IEEE},
  doi       = {10.1109/SP.2010.25}
}

@inproceedings{vaswani2017attention,
  title     = {Attention is all you need},
  author    = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and Kaiser, {\L}ukasz and Polosukhin, Illia},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  volume    = {30},
  pages     = {5998--6008},
  year      = {2017}
}

@article{bozdal2020evaluation,
  title     = {Evaluation of {CAN} Bus Security Challenges},
  author    = {Bozdal, Mehmet and Samie, Mohammad and Aslam, Sohaib and Jennions, Ian K.},
  journal   = {Sensors},
  volume    = {20},
  number    = {8},
  pages     = {2364},
  year      = {2020},
  publisher = {MDPI},
  doi       = {10.3390/s20082364}
}

@article{lampe2024curated,
  author = {Lampe, Brooke and Meng, Weizhi},
  title = {can-train-and-test: A curated {CAN} dataset for automotive intrusion detection},
  journal = {Computers \& Security}, volume = {140}, pages = {103777}, year = {2024},
  doi = {10.1016/j.cose.2024.103777}, url = {https://arxiv.org/abs/2308.04972}
}
@misc{lampe2023appendix,
  author = {Lampe, Brooke and Meng, Weizhi},
  title = {can-train-and-test: A Curated {CAN} Dataset for Automotive Intrusion Detection},
  year = {2023}, howpublished = {arXiv:2308.04972v1},
  note = {Version-specific source for appendix confusion counts; distinct from the journal citation},
  url = {https://arxiv.org/abs/2308.04972v1}
}
@inproceedings{lee2017otids,
  author = {Lee, Hyunsung and Jeong, Seong Hoon and Kim, Huy Kang},
  title = {{OTIDS}: A Novel Intrusion Detection System for In-vehicle Network by Using Remote Frame},
  booktitle = {2017 15th Annual Conference on Privacy, Security and Trust (PST)},
  year = {2017}, doi = {10.1109/PST.2017.00017}
}
@article{song2020dcnn,
  author = {Song, Hyun Min and Woo, Jiyoung and Kim, Huy Kang},
  title = {In-vehicle network intrusion detection using deep convolutional neural network},
  journal = {Vehicular Communications}, volume = {21}, pages = {100198}, year = {2020},
  doi = {10.1016/j.vehcom.2019.100198}
}
@article{islam2020graph,
  author = {Islam, Riadul and Refat, Rafi Ud Daula and Yerram, Sai Manikanta and Malik, Hafiz},
  title = {Graph-Based Intrusion Detection System for Controller Area Networks},
  journal = {IEEE Transactions on Intelligent Transportation Systems},
  volume = {23}, number = {3}, pages = {1727--1736}, year = {2022},
  doi = {10.1109/TITS.2020.3025685}, url = {https://arxiv.org/abs/2009.11440}
}
@inproceedings{tariq2020cantransfer,
  author = {Tariq, Shahroz and Lee, Sangyup and Woo, Simon S.},
  title = {{CANTransfer}: Transfer learning based intrusion detection on a controller area network using convolutional {LSTM} network},
  booktitle = {Proceedings of the 35th Annual ACM Symposium on Applied Computing},
  pages = {1048--1055}, year = {2020}, doi = {10.1145/3341105.3373868}
}
@article{khreasat2026relational,
  author = {Khreasat, Mohammad Khalaf and Gonz{\'a}lez, Gabriel Villarrubia},
  title = {Relational Modelling for Automotive Cybersecurity: Structural Transition and Graph-Topology-Based {CAN} Intrusion Detection},
  journal = {Sensors}, volume = {26}, number = {10}, pages = {2964}, year = {2026},
  doi = {10.3390/s26102964}, url = {https://pmc.ncbi.nlm.nih.gov/articles/PMC13210679/}
}
@article{s26051489,
  author = {Islam, Md Rezanur and Sahlabadi, Mahdi and Batzorig, Munkhdelgerekh and Yim, Kangbin},
  title = {A Hybrid Approach to Universal Intrusion Detection Systems for Automotive Security},
  journal = {Sensors}, volume = {26}, number = {5}, pages = {1489}, year = {2026},
  doi = {10.3390/s26051489}, url = {https://pmc.ncbi.nlm.nih.gov/articles/PMC12986820/}
}
@misc{dupont2019automotive,
  author = {Dupont, Guillaume and Lekidis, Alexios and {den Hartog}, Jerry and Etalle, Sandro},
  title = {Automotive Controller Area Network ({CAN}) Bus Intrusion Dataset v2},
  publisher = {4TU.ResearchData}, year = {2019},
  doi = {10.4121/uuid:b74b4928-c377-4585-9432-2004dfa20a5d},
  url = {https://data.4tu.nl/articles/dataset/Automotive_Controller_Area_Network_CAN_Bus_Intrusion_Dataset/12696950/2}
}
@inproceedings{rajapaksha2024canmirgu,
  author = {Rajapaksha, Sampath and Madzudzo, Garikayi and Kalutarage, Harsha and Petrovski, Andrei and Al-Kadri, M. Omar},
  title = {{CAN-MIRGU}: A Comprehensive {CAN} Bus Attack Dataset from Moving Vehicles for Intrusion Detection System Evaluation},
  booktitle = {Symposium on Vehicles Security and Privacy (VehicleSec)}, year = {2024},
  doi = {10.14722/vehiclesec.2024.23043},
  url = {https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf}
}
@article{neto2024ciciov2024,
  author = {Neto, Euclides Carlos Pinto and Taslimasa, Hamideh and Dadkhah, Sajjad and Iqbal, Shahrear and Xiong, Pulei and Rahman, Taufiq and Ghorbani, Ali A.},
  title = {{CICIoV2024}: Advancing realistic {IDS} approaches against {DoS} and spoofing attack in {IoV} {CAN} bus},
  journal = {Internet of Things}, volume = {26}, pages = {101209}, year = {2024},
  doi = {10.1016/j.iot.2024.101209}, url = {https://www.unb.ca/cic/datasets/iov-dataset-2024.html}
}

@article{kidmose2025cansleuth,
  author = {Kidmose, Brooke and Kidmose, Andreas and Meng, Weizhi},
  title = {can-sleuth: Sleuthing out the capabilities, limitations, and performance impacts of automotive intrusion detection datasets},
  journal = {International Journal of Information Security},
  volume = {24}, pages = {193}, year = {2025},
  doi = {10.1007/s10207-025-01038-8},
  url = {https://link.springer.com/article/10.1007/s10207-025-01038-8}
}

@misc{koltai2026trust,
  author = {Koltai, Beatrix and {\'A}cs, Gergely and Gazdag, Andr{\'a}s},
  title = {{CAN} We Trust Your Results? A Cross-Dataset Study of Automotive {IDS} Evaluation},
  year = {2026}, eprint = {2606.30430}, archivePrefix = {arXiv},
  note = {arXiv preprint, version 1; accepted at ACSW 2026 according to the arXiv record},
  url = {https://arxiv.org/abs/2606.30430v1}
}

@article{dong2026mtff,
  author = {Dong, Chen and Wu, Hao and Li, Cheng},
  title = {Defending Against State-Inducing Spoofing Attacks in Intelligent Connected Vehicles: A Real-Time Temporal Feature Fusion Framework},
  journal = {Sensors}, volume = {26}, number = {15}, pages = {4758}, year = {2026},
  doi = {10.3390/s26154758},
  url = {https://pmc.ncbi.nlm.nih.gov/articles/PMC13468888/}
}

@article{jo2026fusion,
  author = {Jo, Hyunjun and Kim, Deok-hwan},
  title = {Lightweight temporal and spatial fusion for intrusion detection in automotive controller area network},
  journal = {Ad Hoc Networks}, volume = {187}, pages = {104224}, year = {2026},
  doi = {10.1016/j.adhoc.2026.104224},
  url = {https://www.sciencedirect.com/science/article/pii/S1570870526000909}
}

@article{obafemi2026travel,
  author = {Obafemi, Akinwole},
  title = {Do {CAN} Intrusion Detectors Travel? A Cross-Dataset and Zero-Day Study with Identifier-Agnostic, Locally Calibrated Ensembles},
  journal = {World Journal of Advanced Research and Reviews},
  volume = {31}, number = {3}, pages = {1882--1889}, year = {2026},
  doi = {10.30574/wjarr.2026.31.3.2509},
  url = {https://wjarr.com/sites/default/files/fulltext_pdf/WJARR-2026-2509.pdf}
}

@inproceedings{hewitt2019probes,
  author = {Hewitt, John and Liang, Percy},
  title = {Designing and Interpreting Probes with Control Tasks},
  booktitle = {Proceedings of EMNLP-IJCNLP},
  pages = {2733--2743}, year = {2019},
  doi = {10.18653/v1/D19-1275},
  url = {https://aclanthology.org/D19-1275/}
}

@misc{gulrajani2021domainbed,
  author = {Gulrajani, Ishaan and Lopez-Paz, David},
  title = {In Search of Lost Domain Generalization},
  year = {2020}, note = {arXiv:2007.01434v1; verified preprint version},
  url = {https://arxiv.org/abs/2007.01434v1}
}

@article{saito2015pr,
  author = {Saito, Takaya and Rehmsmeier, Marc},
  title = {The Precision-Recall Plot Is More Informative than the {ROC} Plot When Evaluating Binary Classifiers on Imbalanced Datasets},
  journal = {PLOS ONE}, volume = {10}, number = {3}, pages = {e0118432}, year = {2015},
  doi = {10.1371/journal.pone.0118432},
  url = {https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432}
}
@article{rajapaksha2023survey,
  author = {Rajapaksha, Sampath and Kalutarage, Harsha and Al-Kadri, M. Omar and Petrovski, Andrei and Madzudzo, Garikayi and Cheah, Madeline},
  title = {{AI}-Based Intrusion Detection Systems for In-Vehicle Networks: A Survey},
  journal = {ACM Computing Surveys}, volume = {55}, number = {11}, year = {2023},
  doi = {10.1145/3570954}, url = {https://doi.org/10.1145/3570954}
}
@article{sharmin2024benchmark,
  author = {Sharmin, Shaila and Mansor, Hafizah and Abdul Kadir, Andi Fitriah and Aziz, Normaziah A.},
  title = {Benchmarking Frameworks and Comparative Studies of Controller Area Network ({CAN}) Intrusion Detection Systems: A Review},
  journal = {Journal of Computer Security}, volume = {32}, number = {5}, pages = {477--507}, year = {2024},
  doi = {10.3233/JCS-230027}, url = {https://arxiv.org/abs/2402.06904}
}
@inproceedings{cho2016fingerprint,
  author = {Cho, Kyong-Tak and Shin, Kang G.},
  title = {Fingerprinting Electronic Control Units for Vehicle Intrusion Detection},
  booktitle = {25th USENIX Security Symposium}, pages = {911--927}, year = {2016}, publisher = {USENIX Association},
  url = {https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/cho}
}
@inproceedings{chiscop2021modification,
  author = {Chiscop, Irina and Gazdag, Andr{\'a}s and Bosman, Joost and Bicz{\'o}k, Gergely},
  title = {Detecting Message Modification Attacks on the {CAN} Bus with Temporal Convolutional Networks},
  booktitle = {Proceedings of the 7th International Conference on Vehicle Technology and Intelligent Transport Systems},
  pages = {488--496}, year = {2021}, doi = {10.5220/0010445504880496},
  url = {https://www.scitepress.org/Link.aspx?doi=10.5220/0010445504880496}
}
@article{jeong2024xcanids,
  author = {Jeong, Seonghoon and Lee, Sangho and Lee, Hwejae and Kim, Huy Kang},
  title = {{X-CANIDS}: Signal-Aware Explainable Intrusion Detection System for Controller Area Network-Based In-Vehicle Network},
  journal = {IEEE Transactions on Vehicular Technology}, volume = {73}, number = {3}, pages = {3230--3246}, year = {2024},
  doi = {10.1109/TVT.2023.3327275}, url = {https://arxiv.org/abs/2303.12278}
}

@article{hanselmann2020canet,
  author = {Hanselmann, Markus and Strauss, Thilo and Dormann, Katharina and Ulmer, Holger},
  title = {{CANet}: An Unsupervised Intrusion Detection System for High Dimensional {CAN} Bus Data},
  journal = {IEEE Access}, volume = {8}, pages = {58194--58205}, year = {2020},
  doi = {10.1109/ACCESS.2020.2982544}, url = {https://arxiv.org/abs/1906.02492}
}
@inproceedings{alkhatib2022canbert,
  author = {Alkhatib, Natasha and Mushtaq, Maria and Ghauch, Hadi and Danger, Jean-Luc},
  title = {{CAN-BERT} do it? Controller Area Network Intrusion Detection System based on {BERT} Language Model},
  booktitle = {2022 IEEE/ACS 19th International Conference on Computer Systems and Applications (AICCSA)},
  pages = {1--8}, year = {2022}, doi = {10.1109/AICCSA56895.2022.10017800},
  url = {https://arxiv.org/abs/2210.09439}
}
@inproceedings{won2026canbertplus,
  author = {Won, Jun Yeon and Ahmed, Qadeer and Lin, Zhiqiang},
  title = {{CANBERT+}: An Optimized Multi-Layer {BERT}-Based Intrusion Detection for {CAN} Bus},
  booktitle = {4th USENIX Symposium on Vehicle Security and Privacy (VehicleSec 26)},
  pages = {97--115}, year = {2026}, publisher = {USENIX Association},
  url = {https://www.usenix.org/conference/vehiclesec26/presentation/won}
}
@article{balasubramanian2025canlp,
  author = {Balasubramanian, Kavya and Baragur, Adithya Gowda and Donadel, Denis and Sahabandu, Dinuka and Brighente, Alessandro and Ramasubramanian, Bhaskar and Conti, Mauro and Poovendran, Radha},
  title = {{CANLP}: Intrusion Detection for Controller Area Networks Using Natural Language Processing and Embedded Machine Learning},
  journal = {IEEE Transactions on Dependable and Secure Computing}, volume = {22}, number = {6},
  pages = {7203--7214}, year = {2025}, doi = {10.1109/TDSC.2025.3596516},
  url = {https://donadelden.github.io/publication/balasubramanian-canlpnlp-journal-2025/}
}
@article{jo2025indirect,
  author = {Jo, Hyunjun and Kim, Deok-Hwan},
  title = {Indirect Exposure Training for Robust Time-Series {CAN} Bus Intrusion Detection},
  journal = {IEEE Access}, volume = {13}, pages = {213226--213241}, year = {2025},
  doi = {10.1109/ACCESS.2025.3644944}, url = {https://doi.org/10.1109/ACCESS.2025.3644944}
}
@misc{hoang2022supcon,
  author = {Hoang, Thien-Nu and Kim, Daehee},
  title = {Supervised Contrastive {ResNet} and Transfer Learning for the In-vehicle Intrusion Detection System},
  year = {2022}, howpublished = {arXiv:2207.10814v1},
  doi = {10.48550/arXiv.2207.10814}, url = {https://arxiv.org/abs/2207.10814}
}
@article{ganin2016dann,
  author = {Ganin, Yaroslav and Ustinova, Evgeniya and Ajakan, Hana and Germain, Pascal and Larochelle, Hugo and Laviolette, Fran{\c c}ois and Marchand, Mario and Lempitsky, Victor},
  title = {Domain-Adversarial Training of Neural Networks},
  journal = {Journal of Machine Learning Research}, volume = {17}, number = {59}, pages = {1--35}, year = {2016},
  url = {https://jmlr.org/papers/v17/15-239.html}
}
@inproceedings{zhao2019invariant,
  author = {Zhao, Han and Tachet des Combes, Remi and Zhang, Kun and Gordon, Geoffrey},
  title = {On Learning Invariant Representations for Domain Adaptation},
  booktitle = {Proceedings of the 36th International Conference on Machine Learning},
  series = {Proceedings of Machine Learning Research}, volume = {97}, pages = {7523--7532}, year = {2019},
  url = {https://proceedings.mlr.press/v97/zhao19a.html}
}

@inproceedings{zhou2021mixstyle,
  title = {Domain Generalization with {MixStyle}},
  author = {Zhou, Kaiyang and Yang, Yongxin and Qiao, Yu and Xiang, Tao},
  booktitle = {International Conference on Learning Representations},
  year = {2021},
  url = {https://openreview.net/forum?id=6xHJ37MVxxp},
  eprint = {2104.02008},
  archivePrefix = {arXiv},
}

@inproceedings{belrose2023leace,
  title = {{LEACE}: Perfect linear concept erasure in closed form},
  author = {Belrose, Nora and Schneider-Joseph, David and Ravfogel, Shauli and Cotterell, Ryan and Raff, Edward and Biderman, Stella},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2023},
  eprint = {2306.03819},
  archivePrefix = {arXiv},
}

@inproceedings{ravfogel2020null,
  title = {Null It Out: Guarding Protected Attributes by Iterative Nullspace Projection},
  author = {Ravfogel, Shauli and Elazar, Yanai and Gonen, Hila and Twiton, Michael and Goldberg, Yoav},
  booktitle = {Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics},
  year = {2020},
  pages = {7237--7256},
  url = {https://aclanthology.org/2020.acl-main.647/},
}
