#!/usr/bin/env python3
"""
inject_content.py
将JSON数据注入到 quietview-demo.html 的对应 INJECT 标记位置
"""

import json
import re
import os
from datetime import datetime

# 路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(BASE_DIR)
HTML_FILE = os.path.join(WORKSPACE_DIR, "quietview-demo.html")
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")

# tl-item 模板（带链接）
TL_ITEM_TEMPLATE = """\
<div class="tl-item">
  <div class="tl-dot"></div>
  <div class="tl-time">{time}</div>
  <div class="tl-title">{title}</div>
  <div class="tl-desc">{summary} <a href="{url}" target="_blank">→ 查看原文</a></div>
</div>"""

# tl-item 模板（无链接，仅显示摘要）
TL_ITEM_NO_URL_TEMPLATE = """\
<div class="tl-item">
  <div class="tl-dot"></div>
  <div class="tl-time">{time}</div>
  <div class="tl-title">{title}</div>
  <div class="tl-desc">{summary}</div>
</div>"""


def parse_time_for_sort(time_str: str) -> str:
    """
    将各种时间格式统一为可排序字符串（倒序：越新越大）
    支持：'HH:MM'、'今日'、'YYYY-MM-DD HH:MM:SS'、ISO 8601 等
    """
    if not time_str:
        return "00:00"
    # 去除多余空格
    t = time_str.strip()
    # 如果是 HH:MM 格式直接返回（用于同日内排序）
    if re.match(r'^\d{2}:\d{2}$', t):
        return t
    # 如果包含完整日期，提取时间部分
    m = re.search(r'(\d{2}:\d{2})', t)
    if m:
        return m.group(1)
    if t in ('今日', 'today', 'Today'):
        return '99:99'  # 今日排最前
    return '00:00'


def load_json(filepath: str):
    """读取JSON文件，返回列表；不存在或格式错误时返回 None"""
    if not os.path.exists(filepath):
        print(f"[skip] 文件不存在: {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            print(f"[skip] 文件为空: {filepath}")
            return None
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"[error] 读取失败 {filepath}: {e}")
        return None


def build_news_html(items: list) -> str:
    """将新闻列表构建为 tl-item HTML，按时间倒序排列"""
    # 按时间倒序排列
    sorted_items = sorted(
        items,
        key=lambda x: parse_time_for_sort(x.get('time', x.get('pub_time', ''))),
        reverse=True
    )
    html_parts = []
    for item in sorted_items:
        time_val = item.get('time', item.get('pub_time', ''))
        title = item.get('title', '').replace('<', '&lt;').replace('>', '&gt;')
        summary = item.get('summary', item.get('desc', item.get('body', '')))
        url = item.get('url', item.get('link', ''))

        if url:
            html_parts.append(TL_ITEM_TEMPLATE.format(
                time=time_val,
                title=title,
                summary=summary,
                url=url
            ))
        else:
            html_parts.append(TL_ITEM_NO_URL_TEMPLATE.format(
                time=time_val,
                title=title,
                summary=summary
            ))
    return '\n'.join(html_parts)


def inject_block(html: str, key: str, new_content: str) -> tuple[str, bool]:
    """
    替换 <!-- INJECT:key --> ... <!-- /INJECT:key --> 之间的内容
    返回 (新HTML, 是否成功替换)
    """
    pattern = re.compile(
        r'(<!-- INJECT:' + re.escape(key) + r' -->)(.*?)(<!-- /INJECT:' + re.escape(key) + r' -->)',
        re.DOTALL
    )
    if not pattern.search(html):
        print(f"[warn] 未找到注入标记: INJECT:{key}")
        return html, False

    replacement = f'<!-- INJECT:{key} -->\n{new_content}\n<!-- /INJECT:{key} -->'
    new_html = pattern.sub(replacement, html)
    return new_html, True


def main():
    # 读取 HTML
    if not os.path.exists(HTML_FILE):
        print(f"[fatal] HTML文件不存在: {HTML_FILE}")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    changed = False

    # ── 1. 注入投资行业资讯 ──────────────────────────────────────
    investment_data = load_json(os.path.join(DATA_DIR, 'investment_news.json'))
    if investment_data is not None:
        news_html = build_news_html(investment_data)
        html, ok = inject_block(html, 'investment_news', news_html)
        if ok:
            print(f"[ok] investment_news 注入 {len(investment_data)} 条")
            changed = True

    # ── 2. 注入AI行业声音 ────────────────────────────────────────
    ai_data = load_json(os.path.join(DATA_DIR, 'ai_news.json'))
    if ai_data is not None:
        ai_html = build_news_html(ai_data)
        html, ok = inject_block(html, 'ai_news', ai_html)
        if ok:
            print(f"[ok] ai_news 注入 {len(ai_data)} 条")
            changed = True

    # ── 3. 注入市场数据更新时间 ──────────────────────────────────
    market_data = load_json(os.path.join(DATA_DIR, 'market_data.json'))
    if market_data is not None:
        updated_at = ''
        if isinstance(market_data, dict):
            updated_at = market_data.get('updated_at', '')
        elif isinstance(market_data, list) and market_data:
            updated_at = market_data[0].get('updated_at', '')

        if updated_at:
            html, ok = inject_block(html, 'market_updated_at', updated_at)
            if ok:
                print(f"[ok] market_updated_at 注入: {updated_at}")
                changed = True

    # ── 写回 HTML ────────────────────────────────────────────────
    if changed:
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[done] HTML已更新: {HTML_FILE}")
    else:
        print("[info] 无内容变更，HTML保持不变")


if __name__ == '__main__':
    main()
