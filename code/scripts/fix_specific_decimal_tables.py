import re

with open('thesis/vi/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Tables where X.XXX is definitely a decimal percentage or millisecond
target_tables = [
    'tab:target-only-summary',
    'tab:benign-invariant-main',
    'tab:runtime-decomp',
    'tab:comparison-paired',
    'tab:target-only-k500'
]

# Pattern for numbers to replace in these tables
decimal_nums = [
    '1.075', '2.708', '1.225', '4.999', '1.713', '1.530', '7.564',
    '37.001', '1.009', '1.036', '1.100', '3.831',
    '1.083', '3.036', '4.830', '6.231', '2.285', '1.150', '4.402', '5.291',
    '52.461', '54.643',
    '1.825', '5.636', '1.165', '5.244'
]

count = 0
for tbl in target_tables:
    pos = text.find(tbl)
    if pos == -1:
        print(f"Table {tbl} not found!")
        continue
    start = text.rfind(r'\begin{', 0, pos)
    end = text.find(r'\end{', pos) + 30
    block = text[start:end]
    new_block = block
    for num in decimal_nums:
        if num in new_block:
            # Check context: do not change if preceded by word like "MLP 1.500 vòng"
            comma_num = num.replace('.', ',')
            new_block = re.sub(rf'(?<!\d){re.escape(num)}(?!\d)', comma_num, new_block)
            count += 1
    text = text[:start] + new_block + text[end:]

print(f"Replaced {count} specific 3-digit decimal occurrences in tables!")

with open('thesis/vi/main.tex', 'w', encoding='utf-8') as f:
    f.write(text)
