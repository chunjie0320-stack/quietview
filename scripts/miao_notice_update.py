#!/usr/bin/env python3
"""
喵子告知 自动更新脚本（v2 - JSON模式）
每天 06:00 / 10:00 / 14:00 / 18:00 / 22:00 触发

读取 data/YYYYMMDD.json 中的 news + voice 内容
调用 AI 生成喵子告知，更新 JSON 文件的 miao_notice 字段
git commit + push
"""

import re
import sys
import subprocess
import json
from datetime import datetime
import os

REPO_DIR   = "/root/.openclaw/workspace"
DATA_DIR   = os.path.join(REPO_DIR, "data")


# ── 1. 读取当天 JSON 数据 ─────────────────────────────────────────────────────

def load_today_data(date_str):
    """date_str: YYYYMMDD"""
    path = os.path.join(DATA_DIR, f"{date_str}.json")
    if not os.path.exists(path):
        # 创建空结构
        print(f"  [warn] {path} 不存在，创建空结构")
        data = {
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "voice": [],
            "news": [],
            "ai_voice": [],
            "miao_notice": {"content": "", "label": ""}
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    return data, path


# ── 2. 从 HTML 补充资讯数据（如果JSON里为空，fallback读HTML） ─────────────────

def extract_from_html(date_str):
    """从 HTML 提取当天资讯，作为fallback"""
    html_path = os.path.join(REPO_DIR, "index.html")
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    # 找当天 section (panel-daily-brief-YYYYMMDD)
    panel_id = f"panel-daily-brief-{date_str}"
    idx = html.find(f'id="{panel_id}"')
    if idx < 0:
        # 也找带 <!-- 每日简报 的注释
        date_dot = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
        idx = html.find(f'<!-- 每日简报 {date_dot}')
        if idx < 0:
            return [], []

    # 找当天section到下一个section的范围
    next_section = html.find('<!-- 每日简报', idx + 50)
    section = html[idx: next_section if next_section > 0 else idx + 20000]

    news_items = re.findall(
        r'<div class="tl-title">([^<]+)</div>\s*<div class="tl-body">([^<]+)</div>',
        section
    )
    voice_items = re.findall(
        r'<div class="tl-tag">([^<]+)</div>\s*<div class="tl-title">([^<]+)</div>\s*<div class="tl-body">([^<]+)</div>',
        section
    )
    news = [{"title": t, "body": b} for t, b in news_items]
    voice = [{"tag": src, "title": t, "body": b} for src, t, b in voice_items]
    return news, voice


# ── 3. 调用 AI 生成喵子告知 ──────────────────────────────────────────────────

def build_prompt(news_list, voice_list, slot_label):
    news_text = "\n".join([f"· {n['title']}：{n.get('body','')[:80]}" for n in news_list]) if news_list else "（暂无资讯）"
    voice_text = "\n".join([f"· [{v.get('tag','来源')}] {v['title']}：{v.get('body','')[:80]}" for v in voice_list]) if voice_list else "（暂无声音）"

    return f"""你是喵子，一只资深投资视角+产品思维的三花猫AI助手，文风简练有料。

现在是{slot_label}，请基于以下行业资讯和行业声音，写一段「喵子告知」：
- 整理核心信息，找出关键信号
- 给出喵子自己的判断和点评
- 风格：一针见血，大白话优先，100-200字，不超过3段

【行业资讯】
{news_text}

【行业声音】
{voice_text}

直接输出告知内容，不要任何前缀或解释。"""


def call_ai(prompt):
    import urllib.request
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(config_path, encoding='utf-8') as f:
        cfg = json.load(f)
    provider = cfg.get('models', {}).get('providers', {}).get('kubeplex-maas', {})
    base_url = provider.get('baseUrl', 'https://mmc.sankuai.com/openclaw/v1')
    api_key  = provider.get('apiKey', 'catpaw')
    model_id = provider.get('models', [{}])[0].get('id', 'catclaw-proxy-model')
    extra_headers = provider.get('headers', {})

    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "stream": False
    }).encode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    headers.update(extra_headers)

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw = resp.read().decode('utf-8', errors='ignore')

    if raw.strip().startswith('data:'):
        full_content = []
        for line in raw.split('\n'):
            line = line.strip()
            if not line.startswith('data:'):
                continue
            json_str = re.sub(r'^data:data:', '', line)
            json_str = re.sub(r'^data:', '', json_str).strip()
            if json_str in ('[DONE]', ''):
                continue
            try:
                chunk = json.loads(json_str)
                delta = chunk.get('choices', [{}])[0].get('delta', {})
                if delta.get('content'):
                    full_content.append(delta['content'])
            except Exception:
                continue
        return ''.join(full_content).strip()
    else:
        data = json.loads(raw)
        return data['choices'][0]['message']['content'].strip()


def generate_notice(news_list, voice_list, slot_label):
    try:
        prompt = build_prompt(news_list, voice_list, slot_label)
        content = call_ai(prompt)
        if content:
            return content
    except Exception as e:
        print(f"  [generate_notice] error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    return "（喵子暂时无法生成告知：AI接口连接失败）"


# ── 4. 更新 JSON 文件 ─────────────────────────────────────────────────────────

def update_json(data, path, notice_content, slot_label):
    new_entry = {
        "content": notice_content,
        "label": f"🐱 喵子告知 · {slot_label}"
    }
    existing = data.get('miao_notice', [])
    if isinstance(existing, dict):
        existing = [existing]  # 兼容旧格式（单对象→数组）
    # 避免同一时间点重复插入
    if not existing or existing[0].get('label') != new_entry['label']:
        existing.insert(0, new_entry)
    data['miao_notice'] = existing
    data['generated_at'] = datetime.now().isoformat()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON updated: {path}")


# ── 5. 确保当天 HTML panel 存在 ──────────────────────────────────────────────

def ensure_html_panel(date_str, data):
    """如果 HTML 里没有当天的静态 panel，自动创建并插入"""
    html_path = os.path.join(REPO_DIR, "index.html")
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    panel_id = f"panel-daily-brief-{date_str}"
    if panel_id in html:
        # panel 已存在，只更新 active class 和 currentPanel
        _update_active_panel(html_path, html, date_str)
        return False  # 未新建

    print(f"  [ensure_html_panel] {date_str} panel 不存在，开始创建...")

    # 读当天数据
    news = data.get('news', [])
    voice = data.get('voice', [])
    _miao_raw = data.get('miao_notice', {})
    if isinstance(_miao_raw, list):
        miao = _miao_raw[0] if _miao_raw else {}
    else:
        miao = _miao_raw
    miao_content = miao.get('content', '（今日简报生成中…）')
    miao_label = miao.get('label', f'🐱 喵子告知 · {date_str[:4]}.{date_str[4:6]}.{date_str[6:]}')

    def esc(s):
        return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                 .replace('\n\n', '<br><br>').replace('\n', '<br>'))

    def news_items_html(items):
        if not items:
            return '              <div class="tl-item"><div class="tl-dot"></div><div class="tl-title" style="color:#aaa">暂无资讯</div></div>'
        parts = []
        for n in items:
            t = esc(n.get('title', ''))
            b = esc(n.get('body', '')[:120])
            tag = esc(n.get('tag', ''))
            tm = esc(n.get('time', ''))
            url = n.get('url', '')
            src = esc(n.get('source', ''))
            tag_h = f'<div class="tl-tag">{tag}</div>' if tag else ''
            tm_h = f'<div class="tl-time">{tm}</div>' if tm else ''
            lnk_h = f'<div class="tl-link"><a href="{url}" target="_blank">→ {src or "原文"}</a></div>' if url else ''
            parts.append(f'              <div class="tl-item"><div class="tl-dot"></div><div>{tm_h}{tag_h}<div class="tl-title">{t}</div><div class="tl-body">{b}</div>{lnk_h}</div></div>')
        return '\n'.join(parts)

    def voice_items_html(items):
        if not items:
            return '              <div class="tl-item"><div class="tl-dot"></div><div class="tl-title" style="color:#aaa">暂无声音</div></div>'
        parts = []
        for v in items:
            tag = esc(v.get('tag', ''))
            t = esc(v.get('title', ''))
            b = esc(v.get('body', '')[:200])
            url = v.get('url', '')
            src = esc(v.get('source', v.get('tag', '')))
            lnk_h = f'<div class="tl-link"><a href="{url}" target="_blank">→ {src or "原文"}</a></div>' if url else ''
            parts.append(f'              <div class="tl-item"><div class="tl-dot"></div><div><div class="tl-time">今日</div><div class="tl-tag">{tag}</div><div class="tl-title">{t}</div><div class="tl-body">{b}</div>{lnk_h}</div></div>')
        return '\n'.join(parts)

    date_dot = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
    new_section = f"""<!-- 每日简报 {date_dot} -->
    <div class="content-panel active" id="{panel_id}">
      <div class="page-header">
        <h1>每日简报</h1>
        <div class="sub">{date_dot} · 行业资讯 &amp; 行业声音</div>
        <div class="page-header-divider"></div>
      </div>
      <div class="card">
        <div id="miao-notice-{date_str}" class="miao-bubble" style="margin-bottom:24px;border-radius:12px;max-height:420px;overflow-y:auto;">
          <span class="miao-bubble-label">{miao_label}</span>
          {esc(miao_content)}
        </div>
        <div class="two-col">
          <div>
            <div class="col-title">行业资讯<span class="col-count-badge" id="news-count-{date_str}">· {len(news)}</span></div>
            <div class="timeline" id="timeline-news-{date_str}" style="max-height:520px;overflow-y:auto;">
{news_items_html(news)}
            </div>
          </div>
          <div class="two-col-divider"></div>
          <div>
            <div class="col-title">行业声音<span class="col-count-badge" id="voice-count-{date_str}">· {len(voice)}</span></div>
            <div class="timeline" id="timeline-voice-{date_str}" style="max-height:520px;overflow-y:auto;"><!-- INJECT:voice_{date_str} -->
{voice_items_html(voice)}
<!-- /INJECT:voice_{date_str} --></div>
          </div>
        </div>
      </div>
    </div>
    """

    # 找最近一天的 panel 注释，在它前面插入新section
    prev_dates = sorted(
        [m.group(1).replace('.', '') for m in re.finditer(r'<!-- 每日简报 (\d{4}\.\d{2}\.\d{2}) -->', html)],
        reverse=True
    )
    if prev_dates:
        prev = prev_dates[0]
        prev_dot = f"{prev[:4]}.{prev[4:6]}.{prev[6:]}"
        marker = f"<!-- 每日简报 {prev_dot} -->"
        html = html.replace(marker, new_section + marker, 1)
    else:
        # fallback: 插到 #main 开头
        html = html.replace('<div id="main">', '<div id="main">\n    ' + new_section, 1)

    # 去掉其他 panel 的 active class（保证只有今天是 active）
    html = re.sub(r'class="content-panel active" id="panel-daily-brief-(?!' + date_str + r')',
                  'class="content-panel" id="panel-daily-brief-', html)

    # 更新 NAV_DATA（在最新日期前插入今天）
    prev_nav_entry = None
    for pd in prev_dates:
        pd_dot = f"{pd[4:6]}月{pd[6:]}日"
        candidate = f"{{ id: 'daily-brief-{pd}', label: '03月{pd[6:]}日', panel: 'panel-daily-brief-{pd}' }}"
        # 更通用：用正则找第一个 daily-brief-YYYYMMDD entry
        m = re.search(r"\{ id: 'daily-brief-\d{8}', label: '[^']+', panel: '[^']+' \}", html)
        if m:
            prev_nav_entry = m.group(0)
            break

    label_month = date_str[4:6].lstrip('0')
    label_day = date_str[6:].lstrip('0')
    new_nav = f"{{ id: 'daily-brief-{date_str}', label: '0{label_month}月{label_day}日', panel: '{panel_id}' }}"
    if prev_nav_entry and prev_nav_entry not in html:
        prev_nav_entry = None
    if prev_nav_entry:
        html = html.replace(prev_nav_entry, new_nav + ',\n        ' + prev_nav_entry, 1)

    # 更新 currentPanel
    html = re.sub(r"var currentPanel = 'panel-daily-brief-\d{8}';",
                  f"var currentPanel = '{panel_id}';", html)

    # div 自查
    import html.parser as _html_parser
    class _P(_html_parser.HTMLParser):
        def __init__(self): super().__init__(); self.d = 0
        def handle_starttag(self, t, a):
            if t == 'div': self.d += 1
        def handle_endtag(self, t):
            if t == 'div': self.d -= 1
    p = _P(); p.feed(html)
    if p.d != 0:
        raise ValueError(f"div depth={p.d} after inserting panel, aborting!")
    print(f"  div depth OK (0)")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  ✅ HTML panel {date_str} 创建完成")

    # 同步确保 ai-voice panel 也存在
    ensure_ai_voice_panel(date_str, data)

    # 同步确保 miao 自言自语 panel 也存在
    ensure_miao_panel(date_str)

    return True  # 新建了


def ensure_ai_voice_panel(date_str, data):
    """检查并新建 panel-ai-voice-{date_str}（AI行业声音面板）"""
    html_path = os.path.join(REPO_DIR, "index.html")
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    panel_id = f"panel-ai-voice-{date_str}"
    if panel_id in html:
        print(f"  [ai_voice_panel] {panel_id} 已存在，跳过创建")
        return False

    print(f"  [ai_voice_panel] {panel_id} 不存在，开始创建...")

    ai_voice = data.get('ai_voice', [])

    def esc(s):
        return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    items_html = ''
    for item in ai_voice:
        title = esc(item.get('title', ''))
        source = esc(item.get('source', ''))
        url = item.get('link', item.get('url', '#')) or '#'
        body = esc((item.get('body', '') or '')[:200])
        body_div = f'            <div class="tl-body">{body}</div>\n' if body else ''
        items_html += (
            f'          <div class="tl-item">\n'
            f'            <div class="tl-dot"></div>\n'
            f'            <div class="tl-time">今日</div>\n'
            f'            <div class="tl-tag">{source}</div>\n'
            f'            <div class="tl-title">{title}</div>\n'
            + body_div +
            f'            <a class="tl-source" href="{url}" target="_blank">→ 原文</a>\n'
            f'          </div>\n'
        )

    date_dot = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
    new_panel = (
        f'    <!-- AI > 行业声音 {date_dot} -->\n'
        f'    <div class="content-panel" id="{panel_id}">\n'
        f'      <div class="page-header">\n'
        f'        <h1>AI · 行业声音</h1>\n'
        f'        <div class="sub">{date_dot}</div>\n'
        f'        <div class="page-header-divider"></div>\n'
        f'      </div>\n'
        f'      <div class="card">\n'
        f'        <div class="timeline">\n'
        + items_html +
        f'        </div>\n'
        f'      </div>\n'
        f'    </div>\n\n'
    )

    # 插入位置：在现有最新一天的 ai-voice panel 之前
    m = re.search(r'    <!-- AI > 行业声音 \d{4}\.\d{2}\.\d{2} -->', html)
    if m:
        html = html[:m.start()] + new_panel + html[m.start():]
    else:
        # fallback: 直接追加到 </div> <!-- end main --> 之前
        html = html.replace('</div>\n</body>', new_panel + '</div>\n</body>', 1)

    # 更新 NAV_DATA：在 ai-voice children 里加入新条目
    nav_m = re.search(r"\{ id: 'ai-voice-(\d{8})', label: '[^']+', panel: '[^']+' \}", html)
    if nav_m:
        existing_entry = nav_m.group(0)
        label_month = date_str[4:6]
        label_day = date_str[6:]
        new_nav = f"{{ id: 'ai-voice-{date_str}', label: '{label_month}月{label_day}日', panel: '{panel_id}' }}"
        if new_nav not in html:
            html = html.replace(existing_entry, new_nav + ',\n        ' + existing_entry, 1)

    # div 自查
    import html as _html_mod
    from html.parser import HTMLParser
    class _P(HTMLParser):
        def __init__(self): super().__init__(); self.d = 0
        def handle_starttag(self, t, a):
            if t == 'div': self.d += 1
        def handle_endtag(self, t):
            if t == 'div': self.d -= 1
    p = _P(); p.feed(html)
    if p.d != 0:
        raise ValueError(f"ai_voice panel div depth={p.d}, aborting!")
    print(f"  [ai_voice_panel] div depth OK (0)")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  ✅ ai-voice panel {date_str} 创建完成，共 {len(ai_voice)} 条")
    return True


def ensure_miao_panel(date_str):
    """检查并新建 panel-miao-{date_str}（喵子自言自语面板）"""
    html_path = os.path.join(REPO_DIR, "index.html")
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    panel_id = f"panel-miao-{date_str}"
    if panel_id in html:
        print(f"  [miao_panel] {panel_id} 已存在，跳过创建")
        return False

    print(f"  [miao_panel] {panel_id} 不存在，开始创建...")

    date_dot = f"{date_str[:4]}.{date_str[4:6]}.{date_str[6:]}"
    new_panel = (
        f'    <!-- 成长 > 喵子自言自语 {date_dot} -->\n'
        f'    <div class="content-panel" id="{panel_id}">\n'
        f'      <div class="page-header">\n'
        f'        <h1>喵子自言自语</h1>\n'
        f'        <div class="sub">{date_dot}</div>\n'
        f'        <div class="page-header-divider"></div>\n'
        f'      </div>\n'
        f'      <div class="miao-card">\n'
        f'        <div class="miao-card-header">\n'
        f'          <span class="miao-card-time">今日</span>\n'
        f'        </div>\n'
        f'        <div class="miao-card-body">今日喵子还没说话 🐾</div>\n'
        f'      </div>\n'
        f'    </div>\n\n'
    )

    # 插入位置：在现有最新一天的 miao panel 之前
    m = re.search(r'    <!-- 成长 > 喵子自言自语 \d{4}\.\d{2}\.\d{2} -->', html)
    if m:
        html = html[:m.start()] + new_panel + html[m.start():]
    else:
        # fallback: 在第一个 panel-miao- 前插入
        m2 = re.search(r'<div class="content-panel" id="panel-miao-\d{8}">', html)
        if m2:
            html = html[:m2.start()] + new_panel + html[m2.start():]
        else:
            print(f"  [miao_panel] 找不到插入位置，跳过创建")
            return False

    # 更新 NAV_DATA：在 miao-thoughts children 里加入新条目
    nav_m = re.search(r"\{ id: 'miao-\d{8}', label: '[^']+', panel: '[^']+' \}", html)
    if nav_m:
        existing_entry = nav_m.group(0)
        label_month = date_str[4:6]
        label_day = date_str[6:]
        new_nav = f"{{ id: 'miao-{date_str}', label: '{label_month}月{label_day}日', panel: '{panel_id}' }}"
        if new_nav not in html:
            html = html.replace(existing_entry, new_nav + ',\n        ' + existing_entry, 1)
    else:
        print(f"  [miao_panel] 未找到 nav miao 条目，跳过nav更新")

    # div 自查
    from html.parser import HTMLParser as _HP
    class _P(_HP):
        def __init__(self): super().__init__(); self.d = 0
        def handle_starttag(self, t, a):
            if t == 'div': self.d += 1
        def handle_endtag(self, t):
            if t == 'div': self.d -= 1
    p = _P(); p.feed(html)
    if p.d != 0:
        raise ValueError(f"miao panel div depth={p.d}, aborting!")
    print(f"  [miao_panel] div depth OK (0)")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  ✅ miao panel {date_str} 创建完成")
    return True


def _update_active_panel(html_path, html, date_str):
    """panel 已存在时，确保 active class 和 currentPanel 正确"""
    panel_id = f"panel-daily-brief-{date_str}"
    changed = False

    # 确保今天是 active
    target = f'class="content-panel active" id="{panel_id}"'
    if target not in html:
        html = re.sub(r'class="content-panel(?: active)?" id="' + panel_id + '"',
                      f'class="content-panel active" id="{panel_id}"', html)
        changed = True

    # 去掉其他 panel 的 active
    new_html = re.sub(r'class="content-panel active" id="panel-daily-brief-(?!' + date_str + r')',
                      'class="content-panel" id="panel-daily-brief-', html)
    if new_html != html:
        html = new_html
        changed = True

    # 更新 currentPanel
    new_html = re.sub(r"var currentPanel = 'panel-daily-brief-\d{8}';",
                      f"var currentPanel = '{panel_id}';", html)
    if new_html != html:
        html = new_html
        changed = True

    if changed:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✅ active panel 更新为 {date_str}")


# ── 6. git commit + push ──────────────────────────────────────────────────────

def git_push(date_str, slot_label, html_changed=False):
    sys.path.insert(0, os.path.dirname(__file__))
    from git_lock import git_push_with_lock

    files = [f"data/{date_str}.json", "data/"]
    if html_changed:
        files.append("index.html")
        files.append("index.html")

    # 推送前健康检查
    import subprocess as sp2
    check = sp2.run(['python3', '/root/.openclaw/workspace/scripts/check_health.py'], capture_output=True, text=True)
    if check.returncode != 0:
        print('❌ 健康检查失败，终止push：')
        print(check.stdout)
        print(check.stderr)
        return False
    print(check.stdout)

    git_push_with_lock(REPO_DIR, f'auto: 喵子告知更新 {slot_label}', files)
    print(f"✅ pushed: 喵子告知 {slot_label}")


# ── 微信行业声音抓取（mp.weixin.qq.com API）────────────────────────────────────

def fetch_wx_voice(cutoff_days=3):
    """用 mp.weixin.qq.com API 抓取公众号最新文章，返回 voice 列表"""
    import urllib.request as ureq
    cookies_path = "/root/.openclaw/weibo/cookies.env"
    if not os.path.exists(cookies_path):
        print("  [wx_voice] cookies.env 不存在，跳过微信抓取")
        return None  # None 表示跳过

    # 读 cookie
    env = {}
    with open(cookies_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()

    slave_sid = env.get('WX_SLAVE_SID', '')
    token     = env.get('WX_TOKEN', '')
    bizuin    = env.get('WX_BIZUIN', '')
    if not slave_sid or not token:
        print("  [wx_voice] cookie未配置，跳过")
        return None

    accounts = [
        ("财躺平",           env.get('WX_FAKEID_CAITANGPING', 'MzUyNTU4NzY5MA==')),
        ("卓哥投研笔记",     env.get('WX_FAKEID_ZHUOGE',      'Mzk0MzY0OTU5Ng==')),
        ("中金点睛",         env.get('WX_FAKEID_ZJDJ',        'MzI3MDMzMjg0MA==')),
        ("方伟看十年",       env.get('WX_FAKEID_FANGWEI',     'MzU5NzAzMDg1OQ==')),
        ("刘煜辉的高维宏观", env.get('WX_FAKEID_GAOWEIHMG',  'MzYzNzAzODcwNw==')),
    ]

    headers = {
        "Cookie": f"slave_sid={slave_sid}; slave_user=gh_6849aa768b70; bizuin={bizuin}",
        "Referer": f"https://mp.weixin.qq.com/cgi-bin/appmsg?token={token}&lang=zh_CN",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    cutoff = int((datetime.now().timestamp()) - cutoff_days * 86400)
    voice_items = []
    cookie_expired = False

    for name, fakeid in accounts:
        url = (f"https://mp.weixin.qq.com/cgi-bin/appmsg"
               f"?action=list_ex&begin=0&count=10&fakeid={fakeid}"
               f"&type=9&query=&token={token}&lang=zh_CN&f=json&ajax=1")
        req = ureq.Request(url, headers=headers)
        try:
            import time as _time
            with ureq.urlopen(req, timeout=15) as resp:
                d = json.loads(resp.read())
            ret = d.get('base_resp', {}).get('ret', -1)
            if ret == 200013:  # cookie过期
                cookie_expired = True
                print(f"  [wx_voice] ⚠️ cookie已过期（ret=200013），跳过微信抓取")
                break
            for item in d.get('app_msg_list', []):
                ts = item.get('create_time', 0)
                if ts >= cutoff:
                    voice_items.append({
                        "source": name,
                        "tag": name,
                        "title": item.get('title', ''),
                        "body": item.get('digest', ''),
                        "digest": item.get('digest', ''),
                        "url": item.get('link', ''),
                        "link": item.get('link', ''),
                        "timestamp": ts
                    })
            _time.sleep(0.5)
        except Exception as e:
            print(f"  [wx_voice] {name} 抓取失败: {e}")

    if cookie_expired:
        return None
    voice_items.sort(key=lambda x: x['timestamp'], reverse=True)
    print(f"  [wx_voice] 抓取完成：{len(voice_items)} 条（近{cutoff_days}天）")
    return voice_items


# ── AI 行业声音抓取（读取 ai_news.json 缓存）────────────────────────────────

def fetch_ai_voice(cutoff_days=3):
    """
    读取 data/ai_news.json（AI新闻缓存），转成 ai_voice 列表格式（近3天数据）。
    ai_news.json 结构：{"updated_at": ..., "count": N, "news": [{"time": ..., "title": ..., "summary": ..., "source": ..., "url": ...}]}
    返回 ai_voice 格式：[{"title": ..., "source": ..., "link": ..., "body": ..., "time": ...}]
    """
    ai_news_path = os.path.join(DATA_DIR, "ai_news.json")
    if not os.path.exists(ai_news_path):
        print(f"  [ai_voice] {ai_news_path} 不存在，跳过")
        return None

    try:
        with open(ai_news_path, encoding='utf-8') as f:
            raw = json.load(f)
    except Exception as e:
        print(f"  [ai_voice] 读取 ai_news.json 失败: {e}")
        return None

    news_list = raw.get('news', [])
    if not news_list:
        print("  [ai_voice] ai_news.json 为空")
        return []

    # 过滤近 cutoff_days 天内的数据
    # ai_news.json 的 time 字段格式不统一（"2026/03/39" 或 "2026-03-25 19:47"）
    # 取全部数据（字段已是近期抓取），直接转换格式
    ai_voice = []
    for item in news_list:
        title = item.get('title', '') or ''
        summary = item.get('summary', '') or ''
        source = item.get('source', '') or ''
        url = item.get('url', '') or ''
        time_str = item.get('time', '') or ''
        if not title:
            continue
        ai_voice.append({
            "title": title,
            "source": source,
            "link": url,
            "url": url,
            "body": summary if summary != title else '',
            "time": time_str,
            "timestamp": 0
        })

    print(f"  [ai_voice] 从 ai_news.json 读取 {len(ai_voice)} 条")
    return ai_voice


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now()
    slot_label = now.strftime("%Y.%m.%d %H:%M")
    date_str   = now.strftime("%Y%m%d")

    print(f"[{slot_label}] 喵子告知更新开始（JSON模式）...")

    try:
        # 1. 读当天JSON
        data, json_path = load_today_data(date_str)
        news_list  = data.get('news', [])
        voice_list = data.get('voice', [])

        # 1b. 先刷新微信行业声音
        wx_voice = fetch_wx_voice(cutoff_days=3)
        if wx_voice is not None:
            data['voice'] = wx_voice
            voice_list = wx_voice
            print(f"  voice数据已更新：{len(voice_list)} 条")

        # 1c. 刷新 AI 行业声音（量子位/机器之心等）
        ai_voice = fetch_ai_voice()
        if ai_voice:
            data['ai_voice'] = ai_voice
            print(f"  ai_voice数据已更新：{len(ai_voice)} 条")

        # 2. 如果JSON里没有数据，fallback读HTML
        if not news_list and not voice_list:
            print("  JSON中无数据，fallback读HTML...")
            news_list, voice_list = extract_from_html(date_str)

        print(f"  资讯条数: {len(news_list)}, 声音条数: {len(voice_list)}")

        # 3. 生成告知
        notice = generate_notice(news_list, voice_list, slot_label)
        print(f"  生成内容: {notice[:80]}...")

        # 4. 更新JSON
        update_json(data, json_path, notice, slot_label)

        # 5. 确保 HTML panel 存在（含 active class + currentPanel + NAV_DATA）
        # 重新加载 data（因为刚写入了 miao_notice）
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        html_changed = ensure_html_panel(date_str, data)

        # 6. push
        git_push(date_str, slot_label, html_changed)

        print(f"[{slot_label}] ✅ 完成")

    except Exception as e:
        print(f"[{slot_label}] ❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
