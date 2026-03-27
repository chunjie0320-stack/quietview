#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

html_path = '/root/.openclaw/workspace/quietview-demo.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the #miao-notice div and count its depth
miao_pattern = r'(<div[^>]*id="miao-notice"[^>]*>)(.*?)(</div>)'
match = re.search(miao_pattern, content, re.DOTALL)

if match:
    # Check div nesting depth within miao-notice
    inner_content = match.group(2)
    # Count unclosed div openings minus closings in the inner content
    open_count = inner_content.count('<div')
    close_count = inner_content.count('</div>')
    depth = open_count - close_count  # inner div nesting depth
    print(f"✅ miao-notice depth check: {depth}")
    if depth == 0:
        print("✅ Depth = 0, OK to proceed")
    else:
        print(f"⚠️  Depth = {depth}, expected 0")
else:
    print("❌ miao-notice not found")
