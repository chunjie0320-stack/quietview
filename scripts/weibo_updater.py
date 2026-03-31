#!/usr/bin/env python3
"""
刘煜辉微博抓取脚本 v2
抓取微博 UID=2337530130 今天的帖子，写入当天的 HTML panel
"""
import json
import os
import re
import sys
import shutil
import urllib.request
from datetime import datetime, timezone, timedelta

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(WORKSPACE, "index.html")
COOKIES_PATH = os.path.join(WORKSPACE, "weibo", "cookies.env")

CST = timezone(timedelta(hours=8))


def load_env(path):
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except Exception as e:
        print(f"⚠️ 读取 cookies.env 失败: {e}", file=sys.stderr)
    return env


def fetch_weibo_today(uid, sub_cookie, subp_cookie, date_start, date_end):
    url = (f"https://m.weibo.cn/api/container/getIndex"
           f"?uid={uid}&type=uid&value={uid}&containerid=107603{uid}&count=10&page=1")
    req = urllib.request.Request(url)
    req.add_header("Cookie", f"SUB={sub_cookie}; SUBP={subp_cookie}")
    req.add_header("User-Agent",
                   "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                   "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148")
    req.add_header("Referer", "https://m.weibo.cn/")

    posts = []
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read().decode("utf-8"))
        cards = data.get("data", {}).get("cards", [])
        for card in cards:
            mblog = card.get("mblog", {})
            if not mblog:
                continue
            created_at = mblog.get("created_at", "")
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(created_at)
                ts = int(dt.timestamp())
            except Exception:
                continue
            if ts < date_start or ts >= date_end:
                continue
            text = re.sub(r'<[^>]+>', '', mblog.get("text", "")).strip()
            mid = mblog.get("mid", mblog.get("id", ""))
            posts.append({
                "source": "刘煜辉微博",
                "title": text[:60] + ("..." if len(text) > 60 else ""),
                "digest": text[:200],
                "link": f"https://m.weibo.cn/status/{mid}",
                "time": datetime.fromtimestamp(ts, tz=CST).strftime("%H:%M"),
                "color": "rgba(198,40,40,.1)",
                "text_color": "#c62828",
            })
    except Exception as e:
        print(f"  ⚠️ 微博请求失败: {e}", file=sys.stderr)
    return posts


def build_tl_item(post):
    return (
        f'<div class="tl-item">'
        f'<span class="tl-tag" style="background:{post["color"]};color:{post["text_color"]}">'
        f'{post["source"]}</span>'
        f'<a class="tl-title" href="{post["link"]}" target="_blank">{post["title"]}</a>'
        f'{"<p class=tl-body>" + post["digest"] + "</p>" if post.get("digest") and post["digest"] != post["title"] else ""}'
        f'</div>\n'
    )


def update_html(date_str, posts, html_path):
    """把微博帖子追加到当天的行业声音 panel"""
    if not posts:
        print("  📭 今天没有新微博帖子")
        return False

    backup = html_path + ".bak." + datetime.now(CST).strftime("%Y%m%d%H%M%S")
    shutil.copy2(html_path, backup)

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    panel_id = f"timeline-voice-{date_str}"
    marker = f'id="{panel_id}"'
    if marker not in html:
        print(f"  ⚠️ 找不到 panel #{panel_id}，跳过")
        return False

    # 在 panel 内容区末尾插入新条目（在 </div> 前）
    new_items = "".join(build_tl_item(p) for p in posts)

    # 找到 panel 的第一个 </div> 前插入
    pos = html.find(marker)
    close_pos = html.find("</div>", pos)
    if close_pos == -1:
        print("  ⚠️ 找不到闭合 div")
        return False

    html = html[:close_pos] + new_items + html[close_pos:]

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  ✅ 插入 {len(posts)} 条微博帖子到 {panel_id}")
    return True


def main():
    env = load_env(COOKIES_PATH)
    sub = env.get("WEIBO_SUB", "")
    subp = env.get("WEIBO_SUBP", "")
    uid = env.get("WEIBO_TARGET_UID", "2337530130")

    if not sub or not subp:
        print("❌ 缺少微博 Cookie (WEIBO_SUB / WEIBO_SUBP)", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(CST)
    date_str = now.strftime("%Y%m%d")
    day_start = int(datetime(now.year, now.month, now.day, tzinfo=CST).timestamp())
    day_end = day_start + 86400

    print(f"🔍 抓取刘煜辉微博 {date_str}...")
    posts = fetch_weibo_today(uid, sub, subp, day_start, day_end)
    print(f"  获取到 {len(posts)} 条")

    if posts and os.path.exists(HTML_PATH):
        changed = update_html(date_str, posts, HTML_PATH)
        if changed:
            # git commit + push
            import subprocess
            subprocess.run(
                ["git", "-C", WORKSPACE, "add", "index.html"],
                check=True
            )
            result = subprocess.run(
                ["git", "-C", WORKSPACE, "diff", "--cached", "--quiet"],
                capture_output=True
            )
            if result.returncode != 0:
                subprocess.run(
                    ["git", "-C", WORKSPACE, "commit",
                     "-m", f"auto: 刘煜辉微博更新 {date_str} ({len(posts)}条)"],
                    check=True
                )
                subprocess.run(["git", "-C", WORKSPACE, "push"], check=True)
                print(f"  ✅ git push 完成")
            else:
                print("  ℹ️ 无新内容需要提交")
    else:
        print("  📭 无新内容或 HTML 文件不存在")


if __name__ == "__main__":
    main()
