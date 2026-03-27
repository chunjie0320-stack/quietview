#!/usr/bin/env python3
"""
微信公众号行业声音抓取脚本 v2（搜狗方案）
使用搜狗微信搜索 + 美团内网代理，无需微信 cookie。

目标公众号：
  - 财躺平          (搜索关键词: 财躺平)
  - 卓哥投研笔记    (搜索关键词: 卓哥投研笔记)
  - 中金点睛        (搜索关键词: 中金点睛)
  - 方伟看十年      (搜索关键词: 方伟看十年)
  - 刘煜辉          (搜索关键词: 刘煜辉 宏观)

用法：
  python3 wx_voice_updater.py --test          # 只测试「财躺平」一个
  python3 wx_voice_updater.py --all           # 全量抓取所有公众号
  python3 wx_voice_updater.py --all --output result.json
  python3 wx_voice_updater.py --date YYYY-MM-DD  # 更新指定日期的 HTML
  python3 wx_voice_updater.py --dry-run       # 不写文件，只打印

输出格式（JSON list）：
  [{"title": str, "author": str, "content": str, "url": str, "timestamp": int}, ...]
"""

import re
import sys
import os
import json
import time
import shutil
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from html.parser import HTMLParser

# ─── 配置 ─────────────────────────────────────────────────────────────────────

PROXY       = "http://squid-admin:catpaw@nocode-openclaw-squid.sankuai.com:443"
SLEEP_SEC   = 1.5
HTML_PATH   = "/root/.openclaw/workspace/index.html"
REPO_DIR    = "/root/.openclaw/workspace"
STATE_FILE  = "/root/.openclaw/weibo/wx_voice_state.json"

ACCOUNTS = [
    {
        "name":    "财躺平",
        "query":   "财躺平",
        "author":  "财躺平",
        "color":   "rgba(224,123,57,.12)",
        "text_color": "#e07b39",
    },
    {
        "name":    "卓哥投研笔记",
        "query":   "卓哥投研笔记",
        "author":  "卓哥",
        "color":   "rgba(46,125,50,.1)",
        "text_color": "#2e7d32",
    },
    {
        "name":    "中金点睛",
        "query":   "中金点睛",
        "author":  "中金点睛",
        "color":   "rgba(21,101,192,.1)",
        "text_color": "#1565c0",
    },
    {
        "name":    "方伟看十年",
        "query":   "方伟看十年",
        "author":  "方伟",
        "color":   "rgba(106,27,154,.1)",
        "text_color": "#6a1b9a",
    },
    {
        "name":    "刘煜辉的高维宏观",
        "query":   "刘煜辉 宏观",
        "author":  "刘煜辉",
        "color":   "rgba(198,40,40,.1)",
        "text_color": "#c62828",
    },
]

# ─── requests Session（带代理）────────────────────────────────────────────────

try:
    import requests as _req
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def build_session():
    if not HAS_REQUESTS:
        raise RuntimeError("缺少 requests 库，请运行: pip3 install requests")
    import requests
    s = requests.Session()
    s.proxies = {"http": PROXY, "https": PROXY}
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return s


# ─── 搜狗搜索 ────────────────────────────────────────────────────────────────

def sogou_search_links(session, keyword, page=1):
    """
    搜索搜狗微信，返回 /link?url=... 列表
    """
    try:
        resp = session.get(
            "https://weixin.sogou.com/weixin",
            params={"query": keyword, "type": "2", "ie": "utf8", "page": page},
            timeout=15,
        )
        resp.raise_for_status()
    except Exception as e:
        err = str(e)
        if "timed out" in err.lower() or "timeout" in err.lower():
            raise RuntimeError(
                f"搜狗请求超时 (keyword={keyword})。\n"
                "  可能原因：沙箱/CI 网络不可访问 weixin.sogou.com。\n"
                "  解决方案：\n"
                "    1. 确认代理 PROXY 配置可访问搜狗\n"
                "    2. 在 GitHub Actions 环境中运行（有外网访问权）\n"
                "    3. 或临时修改 PROXY 为可用代理"
            )
        raise

    if "antispider" in resp.url or "antispider" in resp.text:
        raise RuntimeError(f"搜狗触发反爬验证 (keyword={keyword})")

    links = re.findall(r'href="(/link\?[^"]+)"', resp.text)
    seen, result = set(), []
    for lnk in links:
        clean = lnk.replace("&amp;", "&")
        if clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def resolve_sogou_link(session, link_path):
    """
    访问搜狗 /link 页，从 JS 拼出真实 mp.weixin.qq.com 链接
    """
    resp = session.get(
        "https://weixin.sogou.com" + link_path,
        headers={"Referer": "https://weixin.sogou.com/weixin"},
        timeout=15,
    )
    if "antispider" in resp.url:
        return None

    parts = re.findall(r"url \+= '([^']+)'", resp.text)
    if not parts:
        return None
    return "".join(parts).replace("@", "")


def fetch_wx_article(session, article_url):
    """
    抓取 mp.weixin.qq.com 文章正文，使用 MicroMessenger UA 伪装
    """
    resp = session.get(
        article_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 14; Pixel 8) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Mobile Safari/537.36 "
                "MicroMessenger/8.0.45"
            ),
            "Referer": "https://mp.weixin.qq.com/",
        },
        timeout=20,
    )
    resp.raise_for_status()
    content = resp.text

    # 标题
    title_m = (
        re.search(r'og:title[^>]+content="([^"]+)"', content)
        or re.search(r'content="([^"]+)"[^>]+og:title', content)
        or re.search(r'id="activity-name"[^>]*>.*?<span[^>]*>([^<]+)</span>', content, re.DOTALL)
    )
    title = title_m.group(1).strip() if title_m else ""

    # 作者/公众号名
    author_m = (
        re.search(r'og:article:author[^>]+content="([^"]+)"', content)
        or re.search(r'content="([^"]+)"[^>]+og:article:author', content)
        or re.search(r'var\s+nickname\s*=\s*"([^"]+)"', content)
        or re.search(r'id="js_name"[^>]*>\s*([^<\n]+?)\s*</', content)
    )
    author = author_m.group(1).strip() if author_m else ""

    # 发布时间戳
    ts_m = re.search(r'var\s+ct\s*=\s*"?(\d+)"?', content)
    timestamp = int(ts_m.group(1)) if ts_m else int(time.time())

    # 正文
    body_start = content.find('id="js_content"')
    if body_start >= 0:
        snippet = content[body_start:body_start + 30000]
        snippet = re.sub(r"<script[^>]*>.*?</script>", "", snippet, flags=re.DOTALL)
        snippet = re.sub(r"<style[^>]*>.*?</style>", "", snippet, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", "", snippet)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"\s+", " ", text).strip()
    else:
        text = ""

    return {
        "title":     title,
        "author":    author,
        "content":   text[:2000],   # 截断到2000字避免太大
        "url":       article_url,
        "timestamp": timestamp,
    }


# ─── 核心抓取逻辑 ─────────────────────────────────────────────────────────────

def fetch_account(session, acct, max_articles=2):
    """
    抓取单个公众号最新 max_articles 篇文章
    返回格式兼容 JSON list：[{title, author, content, url, timestamp}, ...]
    """
    keyword = acct["query"]
    author_hint = acct["author"]
    name = acct["name"]

    print(f"  🔍 搜索「{name}」(query={keyword})...", file=sys.stderr)
    link_paths = sogou_search_links(session, keyword)
    print(f"     找到 {len(link_paths)} 个搜狗链接", file=sys.stderr)

    articles = []
    for lp in link_paths:
        if len(articles) >= max_articles:
            break

        time.sleep(SLEEP_SEC)

        wx_url = resolve_sogou_link(session, lp)
        if not wx_url:
            continue
        if "mp.weixin.qq.com" not in wx_url:
            continue

        try:
            time.sleep(SLEEP_SEC)
            art = fetch_wx_article(session, wx_url)
        except Exception as e:
            print(f"     ⚠️  抓取失败 ({wx_url[:60]}): {e}", file=sys.stderr)
            continue

        if not art["title"]:
            continue

        # 宽松作者过滤：标题里有公众号关键词，或 author 字段包含 author_hint
        title_match = any(kw in art["title"] for kw in [name, keyword.split()[0]])
        author_match = author_hint.split()[0] in art.get("author", "")
        if not (title_match or author_match):
            # 进一步宽松：只要搜到的就算
            pass  # 实践中搜狗结果已经足够精准，不做硬过滤

        # 补充 name 字段（用于 HTML 渲染）
        art["name"] = name

        articles.append(art)
        print(f"     ✅ [{art['author']}] {art['title'][:40]}", file=sys.stderr)

    return articles


# ─── HTML 更新逻辑（与原脚本兼容）───────────────────────────────────────────

def _escape(s):
    if not s:
        return ''
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def articles_to_html(articles, accounts_map):
    html_parts = []
    for art in articles:
        name = art.get("name", "")
        acct = accounts_map.get(name, {})
        color = acct.get("color", "rgba(100,100,100,.1)")
        text_color = acct.get("text_color", "#555")
        link = art.get("url", "")
        ts = art.get("timestamp", 0)
        time_str = datetime.fromtimestamp(ts).strftime("%H:%M") if ts else datetime.now().strftime("%H:%M")

        # 正文摘要（取前150字）
        body = art.get("content", "")[:150]

        source_html = (
            f'<a class="tl-source" href="{_escape(link)}" target="_blank">→ 阅读原文</a>'
            if link else '<span class="tl-source">→ 微信公众号</span>'
        )
        body_html = f'<div class="tl-body">{_escape(body)}</div>\n                ' if body else ''

        html_parts.append(
            f'\n<div class="tl-item">\n'
            f'                <div class="tl-dot"></div>\n'
            f'                <div class="tl-time">{_escape(time_str)}</div>\n'
            f'                <div class="tl-tag" style="background:{color};color:{text_color};">{_escape(name)}</div>\n'
            f'                <div class="tl-title">{_escape(art["title"])}</div>\n'
            f'                {body_html}{source_html}\n'
            f'              </div>'
        )
    return ''.join(html_parts)


def update_html(html_path, articles, accounts_map, target_date_str):
    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    inject_key = f"voice_{target_date_str}"
    items_html = articles_to_html(articles, accounts_map)
    count = len(articles)

    pattern = rf'(<!-- INJECT:{inject_key} -->)(.*?)(<!-- /INJECT:{inject_key} -->)'
    new_html, n = re.subn(pattern, rf'\g<1>{items_html}\n              \g<3>', html, flags=re.DOTALL)

    if n == 0:
        print(f"  ⚠️  未找到 INJECT:{inject_key} 标记，HTML 不更新", file=sys.stderr)
        return 0

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
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
    subprocess.run(['git', 'add', 'index.html'], cwd=REPO_DIR, check=True)
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
    print("  ✅ git push 完成")


# ─── 状态管理 ─────────────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {"published_links": [], "last_run": ""}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ─── 主入口 ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="微信公众号抓取（搜狗方案）")
    parser.add_argument("--test",    action="store_true", help="只测试「财躺平」一个公众号")
    parser.add_argument("--all",     action="store_true", help="全量抓取所有公众号")
    parser.add_argument("--date",    default=None,        help="目标日期 YYYY-MM-DD（更新HTML用）")
    parser.add_argument("--dry-run", action="store_true", help="不写入文件，只打印结果")
    parser.add_argument("--output",  default=None,        help="JSON 输出到指定文件（默认 stdout）")
    args = parser.parse_args()

    # 日期处理
    if args.date:
        target_dt = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        target_dt = datetime.now()
    target_date_str = target_dt.strftime("%Y%m%d")

    # 确定要抓的公众号列表
    if args.test:
        targets = [ACCOUNTS[0]]   # 只跑财躺平
        print(f"[TEST MODE] 只测试「{targets[0]['name']}」...", file=sys.stderr)
    else:
        targets = ACCOUNTS
        print(f"[FULL MODE] 抓取 {len(targets)} 个公众号...", file=sys.stderr)

    session = build_session()
    accounts_map = {a["name"]: a for a in ACCOUNTS}
    all_articles = []

    for acct in targets:
        try:
            arts = fetch_account(session, acct, max_articles=2)
            all_articles.extend(arts)
        except Exception as e:
            print(f"  ❌ 抓取「{acct['name']}」失败: {e}", file=sys.stderr)

    print(f"\n共抓取 {len(all_articles)} 篇文章", file=sys.stderr)

    if not all_articles:
        print("  ⚠️  未获取到任何文章", file=sys.stderr)
        sys.exit(1)

    # ── JSON 输出 ──
    output_data = []
    for art in all_articles:
        output_data.append({
            "title":     art.get("title", ""),
            "author":    art.get("author", art.get("name", "")),
            "content":   art.get("content", ""),
            "url":       art.get("url", ""),
            "timestamp": art.get("timestamp", 0),
            "name":      art.get("name", ""),   # 公众号标识
        })

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 结果写入 {args.output}", file=sys.stderr)
    elif args.dry_run or args.test:
        # test/dry-run 时输出到 stdout
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # 默认：输出 JSON 到 stdout
        print(json.dumps(output_data, ensure_ascii=False, indent=2))

    # ── HTML 更新（非 test/dry-run 模式，且有 HTML 文件时）──
    if not args.test and not args.dry_run and os.path.exists(HTML_PATH):
        backup_path = f"{HTML_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(HTML_PATH, backup_path)
        print(f"  备份 HTML: {os.path.basename(backup_path)}", file=sys.stderr)

        count = update_html(HTML_PATH, all_articles, accounts_map, target_date_str)
        if count > 0:
            verify_divs(HTML_PATH)
            git_push(count, target_date_str)

        # 更新状态
        state = load_state()
        new_links = [a["url"] for a in all_articles if a.get("url")]
        state["published_links"] = list(
            set(state.get("published_links", [])) | set(new_links)
        )[-500:]
        state["last_run"] = datetime.now().isoformat()
        save_state(state)

    print(f"[DONE]", file=sys.stderr)


if __name__ == "__main__":
    main()
