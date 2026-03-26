#!/usr/bin/env python3
"""
微信公众号行业声音定时抓取脚本
支持两种模式：
  Mode A (cookie): 有微信登录cookie时，直接调微信公众号文章列表API
  Mode B (no-cookie): 无cookie时，跳过本次更新并发送提醒

目标公众号：
  - 财躺平          __biz=MzUyNTU4NzY5MA==
  - 卓哥投研笔记    __biz=Mzk0MzY0OTU5Ng==
  - 中金点睛        __biz=MzI3MDMzMjg0MA==
  - 方伟看十年      __biz=MzU5OTAzMDg1OQ==
  - 刘煜辉的高维宏观 __biz=MzYzNzAzODcwNw==

用法：
  python3 wx_voice_updater.py [--date YYYY-MM-DD] [--dry-run]
"""

import re
import sys
import os
import json
import subprocess
import shutil
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from html.parser import HTMLParser

# ─── 配置 ─────────────────────────────────────────────────────────────────────

HTML_PATH      = "/root/.openclaw/workspace/quietview-demo.html"
REPO_DIR       = "/root/.openclaw/workspace"
WX_COOKIE_FILE = "/root/.openclaw/weibo/wx_cookies.env"
STATE_FILE     = "/root/.openclaw/weibo/wx_voice_state.json"

ACCOUNTS = [
    {"name": "财躺平",           "biz": "MzUyNTU4NzY5MA==",  "color": "rgba(224,123,57,.12)", "text_color": "#e07b39"},
    {"name": "卓哥投研笔记",     "biz": "Mzk0MzY0OTU5Ng==",  "color": "rgba(46,125,50,.1)",   "text_color": "#2e7d32"},
    {"name": "中金点睛",         "biz": "MzI3MDMzMjg0MA==",  "color": "rgba(21,101,192,.1)",  "text_color": "#1565c0"},
    {"name": "方伟看十年",       "biz": "MzU5OTAzMDg1OQ==",  "color": "rgba(106,27,154,.1)",  "text_color": "#6a1b9a"},
    {"name": "刘煜辉的高维宏观", "biz": "MzYzNzAzODcwNw==",  "color": "rgba(198,40,40,.1)",   "text_color": "#c62828"},
]


# ─── Cookie 加载 ───────────────────────────────────────────────────────────────

def load_wx_cookie():
    """从 wx_cookies.env 读取 cookie"""
    if not os.path.exists(WX_COOKIE_FILE):
        return None

    env = {}
    with open(WX_COOKIE_FILE, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()

    # 优先使用完整cookie字符串
    if env.get('WX_COOKIE', '').strip():
        return env['WX_COOKIE'].strip()

    # 否则用 uin + key 拼装
    uin = env.get('WX_UIN', '').strip()
    key = env.get('WX_KEY', '').strip()
    if uin and key:
        return f"uin={uin}; key={key}; pass_ticket=; appmsg_token="

    return None


# ─── 微信公众号文章列表 API ────────────────────────────────────────────────────

def fetch_articles_wx_api(biz, cookie, count=3):
    """
    通过微信公众号文章列表接口获取最新文章
    需要有效的登录 cookie
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.45",
        "Referer": f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124",
        "Cookie": cookie,
    }

    # 先访问主页获取 appmsg_token
    profile_url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124"
    req = urllib.request.Request(profile_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            profile_html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        raise RuntimeError(f"访问公众号主页失败: {e}")

    # 提取 appmsg_token
    token_m = re.search(r'"appmsg_token"\s*:\s*"([^"]+)"', profile_html)
    if not token_m:
        # 检查是否要求登录
        if 'verify' in profile_html.lower() or '验证' in profile_html:
            raise RuntimeError("Cookie已过期，需要重新登录")
        raise RuntimeError("无法提取 appmsg_token")

    appmsg_token = token_m.group(1)

    # 获取文章列表
    api_url = (
        f"https://mp.weixin.qq.com/mp/profile_ext"
        f"?action=getmsg&__biz={biz}&f=json&offset=0&count={count}"
        f"&is_ok=1&scene=124&uin=777&key=777&pass_ticket=&wxtoken=&appmsg_token={appmsg_token}&x5=0&f=json"
    )
    req2 = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req2, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8', errors='ignore'))

    if data.get('ret') != 0:
        raise RuntimeError(f"API返回错误: ret={data.get('ret')}, msg={data.get('msg')}")

    msgs = json.loads(data.get('general_msg_list', '{}'))
    return msgs.get('list', [])


def parse_wx_articles(msg_list, account_name):
    """解析微信文章列表，返回文章信息"""
    articles = []
    for msg in msg_list:
        comm = msg.get('comm_msg_info', {})
        app = msg.get('app_msg_ext_info', {})

        if not app:
            continue

        title = app.get('title', '').strip()
        digest = app.get('digest', '').strip()
        content_url = app.get('content_url', '').replace('\\/', '/')
        datetime_ts = comm.get('datetime', 0)

        if not title:
            continue

        # 时间处理
        if datetime_ts:
            dt = datetime.fromtimestamp(datetime_ts)
            time_str = dt.strftime("%H:%M")
        else:
            time_str = datetime.now().strftime("%H:%M")

        articles.append({
            'name': account_name,
            'title': title,
            'body': digest[:150] if digest else title,
            'link': content_url,
            'time': time_str,
            'ts': datetime_ts,
        })

        # 也处理多图文的子文章
        for sub in app.get('multi_app_msg_item_list', []):
            sub_title = sub.get('title', '').strip()
            sub_url = sub.get('content_url', '').replace('\\/', '/')
            sub_digest = sub.get('digest', '').strip()
            if sub_title and sub_url:
                articles.append({
                    'name': account_name,
                    'title': sub_title,
                    'body': sub_digest[:150] if sub_digest else sub_title,
                    'link': sub_url,
                    'time': time_str,
                    'ts': datetime_ts,
                })

    return articles


# ─── AI 摘要（当文章body太短时补充）─────────────────────────────────────────

def ai_summarize(title, body):
    """用 catclaw proxy AI 生成摘要"""
    if body and len(body) > 50:
        return body

    prompt = f"请用2-3句话简明概括以下文章标题的核心观点，直接输出摘要，不要任何前缀：\n\n{title}"

    try:
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
            "max_tokens": 150,
            "stream": True
        }).encode('utf-8')

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        headers.update(extra_headers)

        req = urllib.request.Request(f"{base_url}/chat/completions", data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')

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

        result = ''.join(full_content).strip()
        return result if result else body

    except Exception as e:
        print(f"  AI摘要失败: {e}", file=sys.stderr)
        return body


# ─── HTML 生成 ────────────────────────────────────────────────────────────────

def _escape(s):
    if not s:
        return ''
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def articles_to_html(articles, accounts_map):
    """将文章列表转为 tl-item HTML"""
    html_parts = []
    for art in articles:
        acct = accounts_map.get(art['name'], {})
        color = acct.get('color', 'rgba(100,100,100,.1)')
        text_color = acct.get('text_color', '#555')
        link = art.get('link', '')
        body = art.get('body', '')

        source_html = (
            f'<a class="tl-source" href="{_escape(link)}" target="_blank">→ 阅读原文</a>'
            if link else '<span class="tl-source">→ 微信公众号</span>'
        )

        body_html = f'<div class="tl-body">{_escape(body)}</div>\n                ' if body else ''

        html_parts.append(
            f'\n<div class="tl-item">\n'
            f'                <div class="tl-dot"></div>\n'
            f'                <div class="tl-time">{_escape(art["time"])}</div>\n'
            f'                <div class="tl-tag" style="background:{color};color:{text_color};">{_escape(art["name"])}</div>\n'
            f'                <div class="tl-title">{_escape(art["title"])}</div>\n'
            f'                {body_html}{source_html}\n'
            f'              </div>'
        )

    return ''.join(html_parts)


# ─── HTML 替换 ────────────────────────────────────────────────────────────────

def update_html(html_path, articles, accounts_map, target_date_str):
    """
    替换指定日期的行业声音 INJECT 区块
    target_date_str: 'YYYYMMDD' 格式（用于找 INJECT:voice_YYYYMMDD）
    """
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    inject_key = f"voice_{target_date_str}"
    items_html = articles_to_html(articles, accounts_map)
    count = len(articles)

    pattern = rf'(<!-- INJECT:{inject_key} -->)(.*?)(<!-- /INJECT:{inject_key} -->)'
    replacement = rf'\g<1>{items_html}\n              \g<3>'
    new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)

    if n == 0:
        print(f"  ⚠️  未找到 INJECT:{inject_key} 标记，HTML 不更新")
        return 0

    # 更新 badge 计数
    badge_id = f"voice-count-{target_date_str}"
    new_html = re.sub(
        rf'(<span class="col-count-badge" id="{badge_id}">)[^<]*(</span>)',
        rf'\g<1>· {count}\g<2>',
        new_html
    )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"  ✅ HTML 更新：{inject_key}，共 {count} 条")
    return count


def verify_divs(html_path):
    """div 自查"""
    class DivChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.depth = 0
        def handle_starttag(self, tag, attrs):
            if tag == 'div': self.depth += 1
        def handle_endtag(self, tag):
            if tag == 'div': self.depth -= 1

    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    c = DivChecker()
    c.feed(html)
    if c.depth != 0:
        raise ValueError(f"div depth={c.depth}，不为0！")
    print("  ✅ div depth 自查通过 (depth=0)")


def git_push(count, target_date_str):
    """git commit + push"""
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
    subprocess.run(['git', 'add', 'quietview-demo.html'], cwd=REPO_DIR, check=True)
    result = subprocess.run(
        ['git', 'commit', '-m', f'auto: 行业声音更新 {target_date_str} {now_str} ({count}条)'],
        cwd=REPO_DIR, capture_output=True, text=True
    )
    if result.returncode != 0:
        if 'nothing to commit' in result.stdout + result.stderr:
            print("  ⚠️  无变化，跳过 commit")
            return
        raise RuntimeError(f"git commit 失败: {result.stderr}")
    subprocess.run(['git', 'push'], cwd=REPO_DIR, check=True)
    print(f"  ✅ git push 完成")


# ─── 状态管理（避免重复推送同一篇文章）──────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {"published_links": [], "last_run": ""}


def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ─── 主流程 ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=None, help='目标日期 YYYY-MM-DD，默认今天')
    parser.add_argument('--dry-run', action='store_true', help='不写入HTML，只打印结果')
    args = parser.parse_args()

    if args.date:
        target_dt = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_dt = datetime.now()

    target_date_str = target_dt.strftime("%Y%m%d")  # 用于 INJECT 标记
    now_str = target_dt.strftime("%Y.%m.%d %H:%M")
    print(f"[{now_str}] 行业声音更新开始（目标日期：{target_date_str}）...")

    # 加载 cookie
    cookie = load_wx_cookie()
    if not cookie:
        print("  ⚠️  未找到微信 cookie，跳过本次更新")
        print("  📋 请按照以下步骤获取 cookie：")
        print("     1. 用浏览器打开 https://mp.weixin.qq.com")
        print("     2. 扫码登录后，按F12打开开发者工具")
        print("     3. Network > 任意请求 > Request Headers > 复制 'cookie:' 的值")
        print(f"     4. 粘贴到 {WX_COOKIE_FILE} 的 WX_COOKIE= 后面")
        sys.exit(0)

    # 备份
    if not args.dry_run:
        backup_path = f"{HTML_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(HTML_PATH, backup_path)
        print(f"  备份: {os.path.basename(backup_path)}")

    # accounts_map
    accounts_map = {a['name']: a for a in ACCOUNTS}

    # 抓取所有公众号文章
    state = load_state()
    published_set = set(state.get('published_links', []))

    all_articles = []
    today_cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for acct in ACCOUNTS:
        print(f"  抓取 {acct['name']} ({acct['biz'][:15]}...)...")
        try:
            msg_list = fetch_articles_wx_api(acct['biz'], cookie, count=3)
            articles = parse_wx_articles(msg_list, acct['name'])

            # 过滤今天的文章、去重
            today_articles = []
            for art in articles:
                if art['ts'] and datetime.fromtimestamp(art['ts']) < today_cutoff:
                    continue  # 只取今天的
                if art.get('link') in published_set:
                    continue  # 已发过的跳过
                today_articles.append(art)

            print(f"    找到 {len(articles)} 篇，今日新增 {len(today_articles)} 篇")

            # AI 补充摘要
            for art in today_articles:
                if not art.get('body') or len(art['body']) < 30:
                    art['body'] = ai_summarize(art['title'], art.get('body', ''))

            all_articles.extend(today_articles)

        except RuntimeError as e:
            err_msg = str(e)
            print(f"    ❌ 失败: {err_msg}", file=sys.stderr)
            if 'Cookie已过期' in err_msg or 'Cookie' in err_msg:
                print("  ⚠️  Cookie 已失效，请重新登录并更新 wx_cookies.env", file=sys.stderr)
                sys.exit(1)

    print(f"  共收集 {len(all_articles)} 条新文章")

    if not all_articles:
        print("  ⚠️  今日暂无新文章，保持原内容不变")
        return

    if args.dry_run:
        print("  [DRY-RUN] 不写入文件")
        for art in all_articles:
            print(f"    [{art['name']}] {art['time']} {art['title'][:40]}")
        return

    # 按时间排序（最新的在前）
    all_articles.sort(key=lambda x: x.get('ts', 0), reverse=True)

    # 更新 HTML
    count = update_html(HTML_PATH, all_articles, accounts_map, target_date_str)
    if count == 0:
        print("  ⚠️  HTML 未更新（可能是日期不匹配）")
        return

    # div 自查
    verify_divs(HTML_PATH)

    # git push
    git_push(count, target_date_str)

    # 更新状态
    new_links = [art['link'] for art in all_articles if art.get('link')]
    state['published_links'] = list(set(state.get('published_links', [])) | set(new_links))[-500:]
    state['last_run'] = datetime.now().isoformat()
    save_state(state)

    print(f"[{now_str}] ✅ 完成")


if __name__ == '__main__':
    main()
