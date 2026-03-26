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
    html_path = os.path.join(REPO_DIR, "quietview-demo.html")
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
    data['miao_notice'] = {
        "content": notice_content,
        "label": f"🐱 喵子告知 · {slot_label}"
    }
    data['generated_at'] = datetime.now().isoformat()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON updated: {path}")


# ── 5. 确保当天 HTML panel 存在 ──────────────────────────────────────────────

def ensure_html_panel(date_str, data):
    """如果 HTML 里没有当天的静态 panel，自动创建并插入"""
    html_path = os.path.join(REPO_DIR, "quietview-demo.html")
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
    miao = data.get('miao_notice', {})
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
        <div id="miao-notice-{date_str}" class="miao-bubble" style="margin-bottom:24px;border-radius:12px;">
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
            <div class="timeline" id="timeline-voice-{date_str}" style="max-height:520px;overflow-y:auto;">
{voice_items_html(voice)}
            </div>
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
        m = re.search(r"\{ id: 'daily-brief-\d{8}',", html)
        if m:
            prev_nav_entry = html[m.start():html.find('}', m.start()) + 1]
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
    return True  # 新建了


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
    files = [f"data/{date_str}.json"]
    if html_changed:
        files.append("quietview-demo.html")
    for f in files:
        subprocess.run(['git', 'add', f], cwd=REPO_DIR, check=True)
    result = subprocess.run(
        ['git', 'commit', '-m', f'auto: 喵子告知更新 {slot_label}'],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    if result.returncode != 0 and 'nothing to commit' in result.stdout + result.stderr:
        print("  nothing to commit, skipping push")
        return
    subprocess.run(['git', 'push'], cwd=REPO_DIR, check=True)
    print(f"✅ pushed: 喵子告知 {slot_label}")


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
