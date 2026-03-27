#!/usr/bin/env python3
"""全站自查脚本：对比 quietview-demo.html 和 quietview-v3.html"""

import re
from html.parser import HTMLParser

DEMO = "/root/.openclaw/workspace/quietview-demo.html"
V3   = "/root/.openclaw/workspace/quietview-v3.html"

# ── 1. HTML div 配对检查 ──────────────────────────────────────────────────────
class DivChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.stack:
                self.stack.pop()
            else:
                self.errors.append("Extra </div> with empty stack")

def check_divs(path, label):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    p = DivChecker()
    p.feed(content)
    print(f"\n[{label}] div 检查")
    print(f"  Remaining unclosed divs: {len(p.stack)}")
    if p.errors:
        for e in p.errors:
            print(f"  ERROR: {e}")
    if len(p.stack) == 0 and not p.errors:
        print("  ✅ div 配对正常")
    else:
        print(f"  ⚠️  未闭合 div 数量: {len(p.stack)}")

check_divs(DEMO, "demo")
check_divs(V3,   "v3  ")

# ── 2. content-panel ID 存在性检查 ───────────────────────────────────────────
def check_panels(path, label):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    defined_ids = set(re.findall(r'id="(panel-[^"]+)"', content))
    refs_data  = set(re.findall(r'data-panel="([^"]+)"', content))
    refs_js    = set(re.findall(r"openPanel\(['\"]([^'\"]+)['\"]\)", content))
    all_refs   = refs_data | refs_js

    missing = all_refs - defined_ids
    print(f"\n[{label}] content-panel 检查")
    print(f"  定义 panel 数: {len(defined_ids)}")
    print(f"  引用 panel 数: {len(all_refs)}")
    if missing:
        print(f"  ❌ 缺失 panel IDs: {sorted(missing)}")
    else:
        print(f"  ✅ 所有引用 panel 均已定义")

check_panels(DEMO, "demo")
check_panels(V3,   "v3  ")

# ── 3. 成长板块三个 panel 内容检查 ──────────────────────────────────────────
def check_growth_panels(path, label):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    print(f"\n[{label}] 成长板块 panel 内容检查")

    # panel-diary-20260325
    if 'id="panel-diary-20260325"' in content:
        idx = content.find('id="panel-diary-20260325"')
        chunk = content[idx:idx+3000]
        has_40 = '年近四十' in chunk or '四十' in chunk
        print(f"  panel-diary-20260325: {'✅ 存在，含「年近四十」' if has_40 else '⚠️  存在但未找到「年近四十」关键词'}")
    else:
        print("  panel-diary-20260325: ❌ panel 不存在")

    # panel-dialogue-20260325
    if 'id="panel-dialogue-20260325"' in content:
        idx = content.find('id="panel-dialogue-20260325"')
        chunk = content[idx:idx+4000]
        items = len(re.findall(r'class="tl-item"', chunk))
        print(f"  panel-dialogue-20260325: ✅ 存在  tl-item 数: {items}")
    else:
        print("  panel-dialogue-20260325: ❌ panel 不存在")

    # panel-miao-thoughts
    if 'id="panel-miao-thoughts"' in content:
        idx = content.find('id="panel-miao-thoughts"')
        chunk = content[idx:idx+4000]
        has_date = '2026-03-25' in chunk or '2026.03.25' in chunk
        items = len(re.findall(r'class="tl-item"', chunk))
        print(f"  panel-miao-thoughts: ✅ 存在  日期={'✅ 2026-03-25' if has_date else '⚠️ 未找到'}  tl-item: {items}")
    else:
        print("  panel-miao-thoughts: ❌ panel 不存在")

check_growth_panels(DEMO, "demo")
check_growth_panels(V3,   "v3  ")

# ── 4. 行业声音 tl-item 数量 ────────────────────────────────────────────────
def check_voice_items(path, label):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    idx = content.find('行业声音')
    if idx >= 0:
        nearby = content[idx:idx+5000]
        count = nearby.count('class="tl-item"')
        print(f"\n[{label}] 行业声音附近 tl-item 数量: {count} {'✅ 符合7条' if count == 7 else ('❌ 期望7' if count != 7 else '')}")
    else:
        print(f"\n[{label}] 行业声音: ❌ 未找到")

check_voice_items(DEMO, "demo")
check_voice_items(V3,   "v3  ")

# ── 5. CSS 类名一致性 ───────────────────────────────────────────────────────
CSS_CLASSES = ['.tl-tag', '.tl-title', '.tl-body', '.tl-source']

def extract_css(content, cls):
    pattern = re.escape(cls) + r'\s*\{[^}]*\}'
    return re.findall(pattern, content)

def check_css(demo_content, v3_content):
    print("\n[CSS] tl-* 类名定义一致性检查")
    for cls in CSS_CLASSES:
        d_rules = extract_css(demo_content, cls)
        v_rules = extract_css(v3_content, cls)
        d_str = ' '.join(d_rules).strip()
        v_str = ' '.join(v_rules).strip()
        if not d_str and not v_str:
            status = "⚠️  两边均无定义（内联样式）"
        elif d_str == v_str:
            status = "✅ 一致"
        elif not d_str and v_str:
            status = f"❌ demo 缺失，v3 定义: {v_str[:150]}"
        else:
            status = f"⚠️  不同\n    demo: {d_str[:80]}\n    v3:   {v_str[:80]}"
        print(f"  {cls}: {status}")

with open(DEMO, encoding='utf-8') as f:
    demo_c = f.read()
with open(V3, encoding='utf-8') as f:
    v3_c = f.read()

check_css(demo_c, v3_c)

# ── 6. 额外差异清单 ──────────────────────────────────────────────────────────
print("\n[额外差异] demo vs v3 快速对比")
demo_lines = len(demo_c.splitlines())
v3_lines   = len(v3_c.splitlines())
print(f"  demo 行数: {demo_lines}, v3 行数: {v3_lines}")

remaining_tl_person = demo_c.count('tl-person')
print(f"  demo 中残留 tl-person: {remaining_tl_person} {'✅ 0个残留' if remaining_tl_person == 0 else '⚠️  仍有残留（CSS定义本身不算）'}")

# CSS 中的 .tl-person 定义不算残留，检查 HTML 中的 div class
html_tl_person = len(re.findall(r'class="tl-person"', demo_c))
print(f"  demo 中 class=\"tl-person\" 用法: {html_tl_person} {'✅' if html_tl_person == 0 else '⚠️  有残留'}")

# timeline id 差异
v3_timeline_ids = set(re.findall(r'id="timeline-[^"]*"', v3_c))
demo_timeline_ids = set(re.findall(r'id="timeline-[^"]*"', demo_c))
only_v3 = v3_timeline_ids - demo_timeline_ids
only_demo = demo_timeline_ids - v3_timeline_ids
if only_v3:
    print(f"  v3 有但 demo 没有的 timeline id: {sorted(only_v3)}")
if only_demo:
    print(f"  demo 有但 v3 没有的 timeline id: {sorted(only_demo)}")

print("\n✅ 全站自查完成")
