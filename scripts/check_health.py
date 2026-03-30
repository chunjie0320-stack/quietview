#!/usr/bin/env python3
"""
quietview 健康检查脚本
每次 git push 前运行，确保基础结构正确
"""
import os, json, re
from html.parser import HTMLParser

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(WORKSPACE, 'index.html')
DATA_DIR = os.path.join(WORKSPACE, 'data')

errors = []
warnings = []

# 1. HTML div 配对检查
class DivCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.min_depth = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'div': self.depth += 1
    def handle_endtag(self, tag):
        if tag == 'div':
            self.depth -= 1
            self.min_depth = min(self.min_depth, self.depth)

with open(HTML_FILE) as f:
    html = f.read()

p = DivCounter()
p.feed(html)
if p.depth != 0:
    errors.append(f'HTML div 不配对: 最终depth={p.depth}（应为0）')
elif p.min_depth < 0:
    errors.append(f'HTML 有多余闭合标签: 最小depth={p.min_depth}')
else:
    print('✅ HTML div 配对正常')

# 2. 检查每个日期的 INJECT 标记
dates_in_html = re.findall(r'timeline-voice-(\d{8})', html)
for d in set(dates_in_html):
    if f'INJECT:voice_{d}' not in html:
        warnings.append(f'⚠️  timeline-voice-{d} 缺少 INJECT:voice_{d} 标记')
    else:
        print(f'✅ INJECT:voice_{d} 标记存在')

# 3. 检查 JSON 文件完整性
for fname in sorted(os.listdir(DATA_DIR)):
    if not fname.endswith('.json') or not fname.startswith('202'):
        continue
    fpath = os.path.join(DATA_DIR, fname)
    try:
        with open(fpath) as f:
            d = json.load(f)
        news_count = len(d.get('news', []))
        voice_count = len(d.get('voice', []))
        mn = d.get('miao_notice')
        mn_count = len(mn) if isinstance(mn, list) else (1 if mn else 0)
        print(f'✅ {fname}: news={news_count}, voice={voice_count}, miao_notice={mn_count}')
        if news_count == 0:
            warnings.append(f'⚠️  {fname} news=0，可能未抓取')
    except Exception as e:
        errors.append(f'{fname} JSON解析失败: {e}')

# 4. 检查 git add 范围（读取更新脚本）
script_path = os.path.join(WORKSPACE, 'scripts', 'miao_notice_update.py')
if os.path.exists(script_path):
    with open(script_path) as f:
        script = f.read()
    if 'git add' in script and 'data/' not in script:
        errors.append('miao_notice_update.py: git add 未包含 data/ 目录')
    else:
        print('✅ miao_notice_update.py git add 范围正常')

# 汇总
print()
if warnings:
    for w in warnings: print(w)
if errors:
    print()
    print('❌ 发现错误，请修复后再 push：')
    for e in errors: print(f'  - {e}')
    exit(1)
else:
    print('🎉 健康检查通过！可以 push。')
