#!/usr/bin/env python3
"""
微信公众号行业声音抓取脚本（C方案 — JSON-only）

职责：只写 data/YYYYMMDD.json 的 voice[] 字段，不碰 index.html。

目标公众号：
  - 财躺平          fakeid: MzUyNTU4NzY5MA==
  - 卓哥投研笔记    fakeid: Mzk0MzY0OTU5Ng==
  - 中金点睛        fakeid: MzI3MDMzMjg0MA==
  - 方伟看十年      fakeid: MzU5NzAzMDg1OQ==
  - 刘煜辉的高维宏观 fakeid: MzYzNzAzODcwNw==

用法：
  python3 wx_voice_updater.py             # 正常运行
  python3 wx_voice_updater.py --dry-run   # 只打印，不写文件
  python3 wx_voice_updater.py --date YYYYMMDD  # 指定日期
"""

import sys
import os
import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta

# ── 公共工具 ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    COOKIES_ENV,
    load_or_create_day_data, save_day_data,
    dedup_append, update_date_index, git_push,
)

# ── 配置 ──────────────────────────────────────────────────────────────────────

PROXY    = "http://squid-admin:catpaw@nocode-openclaw-squid.sankuai.com:443"
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


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def load_cookies() -> dict:
    """从 COOKIES_ENV 加载微信 cookie（路径从 utils 常量读取）"""
    env = {}
    with open(COOKIES_ENV) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def day_ts_range(date_str: str | None = None) -> tuple[int, int]:
    """
    返回指定日期在 Asia/Shanghai 自然日的 [start_ts, end_ts)。
    严格定义：当天 00:00:00+08:00 到次日 00:00:00+08:00。
    """
    tz = timezone(timedelta(hours=8))
    if date_str:
        dt = datetime.strptime(date_str, "%Y%m%d").replace(tzinfo=tz)
    else:
        dt = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    start = int(dt.timestamp())
    end   = start + 86400
    return start, end


def is_today(ts: int, date_start: int, date_end: int) -> bool:
    """严格校验 ts 是否落在当天 Asia/Shanghai 自然日范围内"""
    return date_start <= ts < date_end


def fetch_wx_articles(fakeid: str, cookie_str: str, token: str,
                      proxy: str, date_start: int, date_end: int) -> list:
    """
    调微信公众号管理后台 list_ex 接口，拉取当天发布的文章。
    遇到比 date_start 更早的文章立即停止翻页。
    """
    articles = []
    begin, count, max_pages = 0, 5, 10

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
        req.add_header("User-Agent",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

        proxy_handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
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
            # 严格日期过滤：不在当天范围内直接丢弃
            if is_today(create_time, date_start, date_end):
                articles.append(item)

        if found_old:
            break

        begin += count
        time.sleep(SLEEP_SEC)

    return articles


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    dry_run  = "--dry-run" in sys.argv
    date_str = None
    args     = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg.startswith("--date="):
            date_str = arg.split("=", 1)[1]
        elif arg == "--date" and i + 1 < len(args):
            date_str = args[i + 1]

    tz = timezone(timedelta(hours=8))
    if date_str is None:
        date_str = datetime.now(tz).strftime("%Y%m%d")

    date_start, date_end = day_ts_range(date_str)
    now_str = datetime.now(tz).strftime("%Y.%m.%d %H:%M")

    print(f"[{now_str}] 微信行业声音更新开始（JSON-only）, 日期: {date_str}",
          file=sys.stderr)
    print(f"  日期范围: [{date_start}, {date_end}) Asia/Shanghai", file=sys.stderr)

    # ── 加载 cookie ──────────────────────────────────────────────────────────
    env        = load_cookies()
    slave_sid  = env.get("WX_SLAVE_SID", "")
    slave_user = env.get("WX_SLAVE_USER", "")
    token      = env.get("WX_TOKEN", "")
    cookie_str = f"slave_user={slave_user}; slave_sid={slave_sid}"

    # ── 抓取5个公众号 ─────────────────────────────────────────────────────────
    all_voice = []
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
            print(f"    → {len(articles)} 篇（已过滤非当天）", file=sys.stderr)
            for art in articles:
                ts = art.get("create_time", 0)
                all_voice.append({
                    "source":     acct["name"],
                    "title":      art.get("title", ""),
                    "digest":     art.get("digest", "")[:200],
                    "link":       art.get("link", ""),
                    "time":       (datetime.fromtimestamp(ts, tz=tz).strftime("%H:%M") if ts else ""),
                    "timestamp":  ts,
                    "color":      acct["color"],
                    "text_color": acct["text_color"],
                })
        except Exception as e:
            print(f"    ⚠️  {acct['name']} 抓取异常: {e}", file=sys.stderr)
        time.sleep(SLEEP_SEC)

    # 按时间倒序（最新在前）
    all_voice.sort(key=lambda v: v.get("time", "00:00"), reverse=True)
    print(f"\n📊 今日行业声音共 {len(all_voice)} 条（严格当天）", file=sys.stderr)

    if dry_run:
        print(f"[dry-run] would write {len(all_voice)} voice items to data/{date_str}.json")
        for v in all_voice[:3]:
            print(f"  [{v['source']}] {v['title'][:50]}")
        return

    # ── 读取当天 JSON，追加去重写入 voice[] ───────────────────────────────────
    day_data = load_or_create_day_data(date_str)
    day_data["voice"] = dedup_append(
        day_data.get("voice", []), all_voice, key="link"
    )
    day_data["generated_at"] = datetime.now().isoformat()

    save_day_data(date_str, day_data)
    print(f"  ✅ JSON voice 更新完成: data/{date_str}.json ({len(day_data['voice'])}条)",
          file=sys.stderr)

    update_date_index(date_str)
    git_push(f"auto: 行业声音更新 {date_str} {now_str} ({len(all_voice)}条)")
    print(f"[{now_str}] ✅ 完成", file=sys.stderr)


if __name__ == "__main__":
    main()
