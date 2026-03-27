#!/usr/bin/env python3
"""
微信公众号行业声音抓取脚本 v3（微信Cookie方案）
使用 mp.weixin.qq.com/cgi-bin/appmsg 接口，只取当天发布的文章。

目标公众号：
  - 财躺平          fakeid: MzUyNTU4NzY5MA==
  - 卓哥投研笔记    fakeid: Mzk0MzY0OTU5Ng==
  - 中金点睛        fakeid: MzI3MDMzMjg0MA==
  - 方伟看十年      fakeid: MzU5NzAzMDg1OQ==
  - 刘煜辉的高维宏观 fakeid: MzYzNzAzODcwNw==
+ 刘煜辉微博       UID: 2337530130

用法：
  python3 wx_voice_updater.py             # 更新今天的数据
  python3 wx_voice_updater.py --dry-run   # 只打印，不写文件
  python3 wx_voice_updater.py --date YYYYMMDD  # 指定日期
"""

import sys
import os
import json
import time
import subprocess
from datetime import datetime, timezone, timedelta

# ─── 配置 ─────────────────────────────────────────────────────────────────────

PROXY    = "http://squid-admin:catpaw@nocode-openclaw-squid.sankuai.com:443"
REPO_DIR = "/root/.openclaw/workspace"
COOKIES_ENV = "/root/.openclaw/weibo/cookies.env"
SLEEP_SEC = 1.0

ACCOUNTS = [
    {
        "name":       "财躺平",
        "fakeid":     "MzUyNTU4NzY5MA==",
        "color":      "rgba(224,123,57,.12)",
        "text_color": "#e07b39",
    },
    {
        "name":       "卓哥投研笔记",
        "fakeid":     "Mzk0MzY0OTU5Ng==",
        "color":      "rgba(46,125,50,.1)",
        "text_color": "#2e7d32",
    },
    {
        "name":       "中金点睛",
        "fakeid":     "MzI3MDMzMjg0MA==",
        "color":      "rgba(21,101,192,.1)",
        "text_color": "#1565c0",
    },
    {
        "name":       "方伟看十年",
        "fakeid":     "MzU5NzAzMDg1OQ==",
        "color":      "rgba(106,27,154,.1)",
        "text_color": "#6a1b9a",
    },
    {
        "name":       "刘煜辉的高维宏观",
        "fakeid":     "MzYzNzAzODcwNw==",
        "color":      "rgba(198,40,40,.1)",
        "text_color": "#c62828",
    },
]

# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def load_cookies():
    """从 cookies.env 加载微信 cookie"""
    env = {}
    with open(COOKIES_ENV) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def today_ts_range(date_str=None):
    """返回指定日期（Asia/Shanghai）的 unix timestamp 范围 [start, end)"""
    tz = timezone(timedelta(hours=8))
    if date_str:
        dt = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=tz)
    else:
        dt = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start = int(dt.timestamp())
    end   = start + 86400
    return start, end


def fetch_wx_articles(fakeid, cookie_str, token, proxy, date_start, date_end):
    """
    调微信公众号管理后台接口，分页拉取文章，返回当天发布的文章列表。
    每次拉5篇，直到遇到比 date_start 还早的文章则停止。
    """
    import urllib.request
    import urllib.error

    articles = []
    begin = 0
    count = 5
    max_pages = 10  # 最多翻10页，防止无限循环

    for _ in range(max_pages):
        url = (
            f"https://mp.weixin.qq.com/cgi-bin/appmsg"
            f"?action=list_ex&begin={begin}&count={count}"
            f"&fakeid={fakeid}&type=9&query=&token={token}"
            f"&lang=zh_CN&f=json&ajax=1"
        )
        req = urllib.request.Request(url)
        req.add_header("Cookie", cookie_str)
        req.add_header("Referer", "https://mp.weixin.qq.com/")
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

        # 设置代理
        proxy_handler = urllib.request.ProxyHandler({
            "http": proxy, "https": proxy
        })
        opener = urllib.request.build_opener(proxy_handler)

        try:
            resp = opener.open(req, timeout=15)
            data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  ⚠️  请求失败: {e}", file=sys.stderr)
            break

        if data.get("base_resp", {}).get("ret") != 0:
            print(f"  ⚠️  接口返回错误: {data.get('base_resp')}", file=sys.stderr)
            break

        items = data.get("app_msg_list", [])
        if not items:
            break

        found_old = False
        for item in items:
            create_time = item.get("create_time", 0)
            if create_time < date_start:
                found_old = True
                break
            if create_time < date_end:
                articles.append(item)

        if found_old:
            break

        begin += count
        time.sleep(SLEEP_SEC)

    return articles


def fetch_weibo_today(uid, sub_cookie, subp_cookie, proxy, date_start, date_end):
    """拉取微博用户今天的帖子"""
    import urllib.request

    url = f"https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=107603{uid}&count=10&page=1"
    req = urllib.request.Request(url)
    req.add_header("Cookie", f"SUB={sub_cookie}; SUBP={subp_cookie}")
    req.add_header("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15")
    req.add_header("Referer", "https://m.weibo.cn/")

    proxy_handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
    opener = urllib.request.build_opener(proxy_handler)

    posts = []
    try:
        resp = opener.open(req, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))
        cards = data.get("data", {}).get("cards", [])
        for card in cards:
            mblog = card.get("mblog", {})
            if not mblog:
                continue
            # 解析时间
            created_at = mblog.get("created_at", "")
            try:
                # 微博时间格式: "Thu Mar 27 10:30:00 +0800 2026"
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(created_at)
                ts = int(dt.timestamp())
            except Exception:
                continue

            if ts < date_start or ts >= date_end:
                continue

            # 清理正文html
            text = mblog.get("text", "")
            import re
            text = re.sub(r'<[^>]+>', '', text).strip()

            mid = mblog.get("mid", mblog.get("id", ""))
            posts.append({
                "source":     "刘煜辉微博",
                "title":      text[:60] + ("..." if len(text) > 60 else ""),
                "digest":     text[:200],
                "link":       f"https://m.weibo.cn/status/{mid}",
                "time":       datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=8))).strftime("%H:%M"),
                "color":      "rgba(198,40,40,.1)",
                "text_color": "#c62828",
            })
    except Exception as e:
        print(f"  ⚠️  微博请求失败: {e}", file=sys.stderr)

    return posts


def ensure_html_panel(date_str, html_path):
    """确保 HTML 里有当天的 panel（如果没有则插入）"""
    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    if f'id="panel-daily-brief-{date_str}"' in content:
        return  # 已存在

    # 从 miao_notice_update.py 里的逻辑一致，此处简化：只补 INJECT 标记
    # 实际 panel 由 miao_notice_update.py 的 ensure_html_panel 创建
    print(f"  ℹ️  panel-daily-brief-{date_str} 不存在，跳过 HTML 更新（由 miao_notice_update.py 创建）", file=sys.stderr)


def update_json_voice(date_str, voice_items, dry_run=False):
    """更新 data/YYYYMMDD.json 的 voice 字段"""
    json_path = os.path.join(REPO_DIR, "data", f"{date_str}.json")

    if os.path.exists(json_path):
        with open(json_path, encoding="utf-8") as f:
            day_data = json.load(f)
    else:
        day_data = {
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "voice": [], "news": [], "ai_voice": [], "miao_notice": []
        }

    # 兜底话术
    if not voice_items:
        voice_items = [{
            "source":     "",
            "title":      "今天还没有新文章哟 🐾",
            "digest":     "",
            "link":       "",
            "time":       "",
            "color":      "",
            "text_color": "#999",
        }]

    day_data["voice"] = voice_items
    day_data["generated_at"] = datetime.now().isoformat()

    if dry_run:
        print(f"[dry-run] voice {len(voice_items)} 条：", file=sys.stderr)
        for v in voice_items:
            print(f"  [{v.get('source','')}] {v.get('title','')[:60]} ({v.get('time','')})", file=sys.stderr)
        return json_path

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(day_data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ JSON voice 更新完成: data/{date_str}.json ({len(voice_items)}条)", file=sys.stderr)
    return json_path


def update_html_inject(date_str, voice_items, html_path, dry_run=False):
    """更新 HTML 里 INJECT:voice_{date_str} 区域"""
    import re

    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    inject_key = f"voice_{date_str}"
    pattern = re.compile(
        r'(<!-- INJECT:' + inject_key + r' -->)(.*?)(<!-- /INJECT:' + inject_key + r' -->)',
        re.DOTALL
    )

    if not pattern.search(content):
        print(f"  ⚠️  INJECT:{inject_key} 标记不存在，跳过 HTML 更新", file=sys.stderr)
        return False

    # 生成 HTML 片段
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    items_html = []
    for item in voice_items:
        parts = [
            '<div class="tl-item">',
            '  <div class="tl-dot"></div>',
        ]
        if item.get("time"):
            parts.append(f'  <div class="tl-time">{esc(item["time"])}</div>')
        if item.get("source"):
            style = f'background:{item.get("color","")};color:{item.get("text_color","")};'
            parts.append(f'  <div class="tl-tag" style="{style}">{esc(item["source"])}</div>')
        parts.append(f'  <div class="tl-title">{esc(item["title"])}</div>')
        if item.get("digest"):
            parts.append(f'  <div class="tl-body">{esc(item["digest"])}</div>')
        if item.get("link"):
            parts.append(f'  <a class="tl-source" href="{esc(item["link"])}" target="_blank">→ 阅读原文</a>')
        parts.append('</div>')
        items_html.append('\n'.join(parts))

    new_inner = '\n' + '\n'.join(items_html) + '\n'
    new_content = pattern.sub(
        r'\g<1>' + new_inner + r'\3',
        content
    )

    # 更新 badge
    badge_pattern = re.compile(r'(id="voice-count-' + date_str + r'">)[^<]*(</span>)')
    real_count = len([v for v in voice_items if v.get("source")])  # 不算兜底
    new_content = badge_pattern.sub(r'\g<1>· ' + str(real_count) + r'\2', new_content)

    if dry_run:
        print(f"[dry-run] HTML inject {inject_key}: {len(voice_items)} 条", file=sys.stderr)
        return True

    bak = html_path + ".bak." + datetime.now().strftime("%Y%m%d%H%M%S")
    import shutil
    shutil.copy2(html_path, bak)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # div depth 自查
    depth = 0
    max_depth = 0
    for line in new_content.splitlines():
        depth += line.count('<div') - line.count('</div')
        if depth > max_depth:
            max_depth = depth
    if depth != 0:
        print(f"  ⚠️  div depth 自查失败！depth={depth}，回滚", file=sys.stderr)
        shutil.copy2(bak, html_path)
        return False

    print(f"  ✅ HTML inject 更新完成: {inject_key}", file=sys.stderr)
    return True


def git_push(date_str, count, dry_run=False):
    if dry_run:
        print("[dry-run] 跳过 git push", file=sys.stderr)
        return
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
    msg = f"auto: 行业声音更新 {date_str} {now_str} ({count}条)"
    subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO_DIR)
    if result.returncode == 0:
        print("  ℹ️  无变更，跳过 commit", file=sys.stderr)
        return
    subprocess.run(["git", "commit", "-m", msg], cwd=REPO_DIR, check=True)
    # pull --rebase 防止冲突
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=REPO_DIR, check=False)
    subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
    print(f"  ✅ git push 完成: {msg}", file=sys.stderr)


# ─── 主流程 ───────────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv
    date_str = None
    for arg in sys.argv[1:]:
        if arg.startswith("--date="):
            date_str = arg.split("=", 1)[1]
        elif arg == "--date" and sys.argv.index(arg) + 1 < len(sys.argv):
            date_str = sys.argv[sys.argv.index(arg) + 1]

    tz = timezone(timedelta(hours=8))
    if date_str is None:
        date_str = datetime.now(tz).strftime("%Y%m%d")

    date_start, date_end = today_ts_range(date_str)
    print(f"▶ 抓取日期: {date_str} ({datetime.fromtimestamp(date_start, tz)} ~ {datetime.fromtimestamp(date_end, tz)})", file=sys.stderr)

    # 加载 cookie
    env = load_cookies()
    slave_sid  = env.get("WX_SLAVE_SID", "")
    slave_user = env.get("WX_SLAVE_USER", "")
    token      = env.get("WX_TOKEN", "")
    weibo_sub  = env.get("WEIBO_SUB", "")
    weibo_subp = env.get("WEIBO_SUBP", "")
    weibo_uid  = env.get("WEIBO_TARGET_UID", "2337530130")

    cookie_str = f"slave_user={slave_user}; slave_sid={slave_sid}"

    all_voice = []

    # 抓微信各公众号
    for acct in ACCOUNTS:
        print(f"  📰 抓取: {acct['name']} ...", file=sys.stderr)
        try:
            articles = fetch_wx_articles(
                fakeid=acct["fakeid"],
                cookie_str=cookie_str,
                token=token,
                proxy=PROXY,
                date_start=date_start,
                date_end=date_end,
            )
            print(f"    → {len(articles)} 篇", file=sys.stderr)
            for art in articles:
                ts = art.get("create_time", 0)
                all_voice.append({
                    "source":     acct["name"],
                    "title":      art.get("title", ""),
                    "digest":     art.get("digest", "")[:200],
                    "link":       art.get("link", ""),
                    "time":       datetime.fromtimestamp(ts, tz=tz).strftime("%H:%M") if ts else "",
                    "color":      acct["color"],
                    "text_color": acct["text_color"],
                })
        except Exception as e:
            print(f"    ⚠️  {acct['name']} 抓取异常: {e}", file=sys.stderr)
        time.sleep(SLEEP_SEC)

    # 抓刘煜辉微博
    print(f"  📰 抓取: 刘煜辉微博 ...", file=sys.stderr)
    try:
        weibo_posts = fetch_weibo_today(
            uid=weibo_uid,
            sub_cookie=weibo_sub,
            subp_cookie=weibo_subp,
            proxy=PROXY,
            date_start=date_start,
            date_end=date_end,
        )
        print(f"    → {len(weibo_posts)} 条", file=sys.stderr)
        all_voice.extend(weibo_posts)
    except Exception as e:
        print(f"    ⚠️  微博抓取异常: {e}", file=sys.stderr)

    # 按时间排序（倒序，最新在前）
    def sort_key(v):
        t = v.get("time", "")
        return t if t else "00:00"
    all_voice.sort(key=sort_key, reverse=True)

    print(f"\n📊 今日行业声音共 {len(all_voice)} 条", file=sys.stderr)

    # 更新 JSON
    html_path = os.path.join(REPO_DIR, "index.html")
    update_json_voice(date_str, all_voice, dry_run=dry_run)

    # 更新 HTML inject
    update_html_inject(date_str, all_voice if all_voice else [{
        "source": "", "title": "今天还没有新文章哟 🐾",
        "digest": "", "link": "", "time": "", "color": "", "text_color": "#999",
    }], html_path, dry_run=dry_run)

    # git push
    git_push(date_str, len(all_voice), dry_run=dry_run)


if __name__ == "__main__":
    main()
