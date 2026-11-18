"""Align the method specification with the active 28/30-dimensional study."""

def legacy_main():
    from pathlib import Path
    import re,zipfile
    ROOT=Path(__file__).resolve().parents[2]
    backup=ROOT/'revision_backup/before_advisor_completion_2026-11-09.zip'
    if not backup.exists():
        with zipfile.ZipFile(backup,'w',zipfile.ZIP_DEFLATED) as z:
            for lang in ['vi','en']:
                for name in ['main.tex','refs.bib']:
                    p=ROOT/'thesis'/lang/name;z.write(p,p.relative_to(ROOT).as_posix())
    for lang in ['vi','en']:
        p=ROOT/'thesis'/lang/'main.tex';t=p.read_text(encoding='utf-8');vi=lang=='vi'
        section=r'\section{Đặc trưng thô và cấu trúc}' if vi else r'\section{Raw and structural features}'
        start=t.index(section);end=t.index(r'\subsection{Tính bất biến đổi tên ID}' if vi else r'\subsection{Identifier-renaming invariance}',start)
        body=t[start:end]
        if vi:
            body=re.sub(r'Đầu vào raw gồm.*?Các phép chuẩn hóa là hằng số cố định, không học từ test\.', lambda _: 'Giao thức thực nghiệm dùng raw 28 chiều: 11 bit ID, DLC chuẩn hóa, 8 byte payload và 8 mặt nạ. Structural có 30 chiều như Bảng~'+r'\ref{tab:features}'+'. Cả hai không có đặc trưng thời gian. Chuẩn hóa dùng hằng số cố định, không học từ test.',body,count=1,flags=re.S)
        else:
            body=re.sub(r'Raw inputs contain.*?Normalization constants are fixed and never fitted to tests\.', lambda _: 'The executed protocol uses 28 raw dimensions: 11 ID bits, normalized DLC, eight payload bytes and eight masks. Structural inputs have 30 dimensions as specified in Table~'+r'\ref{tab:features}'+'. Neither includes timing. Normalization constants are fixed and never fitted to tests.',body,count=1,flags=re.S)
        # Remove the two inactive timing rows, then renumber the four local features.
        lines=body.splitlines();has_timing=any(line.startswith('26 &') and r'\log' in line for line in lines)
        lines=[line for line in lines if not ((line.startswith('26 &') or line.startswith('27 &')) and r'\log' in line)]
        body='\n'.join(lines)+'\n'
        if has_timing:
            for old,new in [(28,26),(29,27),(30,28),(31,29)]:
                body=re.sub(r'^'+str(old)+r' &',str(new)+' &',body,flags=re.M)
        body=body.replace('Hai feature 29 và 30','Hai feature 27 và 28').replace('Features 29 and 30','Features 27 and 28')
        body=body.replace('$f_{30}/f_{29}','$f_{28}/f_{27}').replace('chiều 30','chiều 28').replace('dimension 30','dimension 28')
        body=body.replace('ngoài timing và payload history','ngoài lịch sử payload').replace('beyond timing and payload history','beyond payload history')
        body=body.replace('Nhánh content loại raw index 28 và structural index 26, 27.', 'So với đặc tả timed v2.1 lưu trong mã lịch sử, nhánh content loại raw index 28 và hai chiều thời gian structural cũ 26, 27; các chỉ số trong Bảng~'+r'\ref{tab:features}'+' đã được đánh lại cho nhánh 30 chiều.')
        body=body.replace('The content tier removes raw index 28 and structural indices 26 and 27, producing 28 and 30 dimensions respectively.', 'Relative to the archived timed v2.1 specification, the content tier removes raw index 28 and old structural timing indices 26 and 27. Table~'+r'\ref{tab:features}'+' renumbers the active content dimensions from 0 to 29.')
        t=t[:start]+body+t[end:]
        t=t.replace('Structural-minus-timing & Vai trò hai khoảng thời gian', 'Structural-minus-timing & Trùng structural trong nhánh content; không đếm thành thí nghiệm riêng')
        t=t.replace('Structural-minus-timing & The two timing intervals', 'Structural-minus-timing & Identical to structural in the content tier; not counted separately')
        t=t.replace('Bỏ riêng chiều 30, giữ các thống kê khác','Bỏ riêng chiều 28 của content, giữ các thống kê khác').replace('Remove only dimension 30; retain other statistics','Remove content dimension 28 only; retain other statistics')
        t=t.replace('ID/payload/timing-only & Giới hạn từng nhóm đầu vào','ID-only / raw-minus-ID & Giới hạn từng nhóm nội dung; timing-only không áp dụng')
        t=t.replace('ID/payload/timing-only & Limits of individual modalities','ID-only / raw-minus-ID & Content-modality limits; timing-only is not applicable')
        t=t.replace('RQ2 gồm 13 biểu diễn,','Thiết kế timed ban đầu nêu 13 tên biến thể; nghiên cứu content kiểm tra 10 biểu diễn khác nhau vì loại timing-only và gộp các tên trùng. Trong đó,')
        t=t.replace('RQ2 contains 13 representations,','The original timed design listed 13 variant names; the content study tests ten distinct representations after excluding timing-only and merging aliases. These include')
        t=t.replace('Khác với bản thăm dò, $\\Delta t$ của frame đầu cửa sổ được tính so với frame cuối cửa sổ trước trong cùng file, không bị đặt 0 chỉ vì đổi cửa sổ. Lịch sử cùng ID cũng được giữ qua chunk.', 'Trong nhánh content, lịch sử payload cùng ID được giữ liên tục qua cửa sổ và chunk theo thứ tự file. Timestamp không tham gia đầu vào mô hình.')
        t=t.replace('Unlike the exploratory implementation, the first frame of a window uses the preceding window\'s final frame to compute $\\Delta t$. Same-ID history also survives I/O chunks.', 'In the content tier, same-ID payload history survives window and I/O chunk boundaries in file order. Timestamps do not enter model inputs.')
        t=t.replace('Timestamp thật phải hữu hạn và không giảm trong cùng capture. Kiểm tra này thực hiện cả trong chunk lẫn giữa hai chunk.', 'Chỉ nhánh timed yêu cầu timestamp hữu hạn và không giảm trong capture, kể cả qua biên chunk. Phép so content hiện tại giữ nguyên timestamp để kiểm toán các lần giảm, nhưng không dùng chúng làm đặc trưng hoặc tự sắp xếp lại dữ liệu.')
        t=t.replace('Real timestamps must be finite and nondecreasing within a capture, including across chunk boundaries.', 'Only the timed branch requires finite, nondecreasing capture timestamps, including across chunks. The executed content comparison retains original timestamps for inversion audits but does not use them as features or reorder records.')
        t=t.replace('Khóa luận đặc tả và triển khai biểu diễn CAN cấu trúc kết hợp payload, mặt nạ hợp lệ, biến thiên payload cùng ID, thời gian và quan hệ định danh cục bộ.', 'Khóa luận đặc tả và triển khai biểu diễn CAN cấu trúc kết hợp payload, mặt nạ hợp lệ, biến thiên payload cùng ID và quan hệ định danh cục bộ trong nhánh nội dung. Thành phần thời gian của thiết kế ban đầu không nằm trong kết quả được xác nhận.')
        t=t.replace('The thesis specifies and implements a structural CAN representation combining payload, validity masks, same-ID payload changes, timing and local identifier relations.', 'The thesis specifies and implements a structural CAN representation combining payload, validity masks, same-ID payload changes and local identifier relations in the content tier. Timing components of the original design are outside the confirmed results.')
        t=t.replace('Trong đó, trong đó','Trong đó').replace('These include including','These include')
        p.write_text(t,encoding='utf-8')


if __name__ == '__main__':
    import sys
    if '--legacy-manuscript' in sys.argv:
        sys.argv.remove('--legacy-manuscript')
        legacy_main()
    else:
        from pathlib import Path
        import subprocess
        args=sys.argv[1:]
        if not any(a in args for a in ['--check','--build']):args=['--build',*args]
        raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).with_name('finalize_thesis_for_supervisor.py')),*args]))
