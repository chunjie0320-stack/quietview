#!/usr/bin/env python3
"""
quietview AI 行业声音全量抓取脚本（C方案 — JSON-only）

职责：只写 data/YYYYMMDD.json 的 ai_voice[] 字段，不碰 index.html。
追加去重模式（不覆盖写入）。

数据源：
  - 量子位 (qbitai.com)
  - 机器之心 (jiqizhixin.com)
  - arxiv cs.AI / cs.LG
  - The Verge AI  (RSS: https://www.theverge.com/rss/ai-artificial-intelligence/index.xml)
  - TechCrunch AI (feed: https://techcrunch.com/feed/  过滤 category 含 artificial-intelligence)

用法：
  python3 fetch_all.py             # 正常运行
  python3 fetch_all.py --dry-run   # 只打印，不写文件
"""

import os
import re
import sys
import json
import subprocess
import xml.etree.ElementTree as ET
import urllib.request
from datetime import datetime, timezone, timedelta

# ── 公共工具 ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    load_or_create_day_data, save_day_data,
    dedup_append, update_date_index, git_push,
)

# ── 时区 ──────────────────────────────────────────────────────────────────────
CST = timezone(timedelta(hours=8))

# ── 噪音关键词 ────────────────────────────────────────────────────────────────
NOISE_KEYWORDS = [
    "javascript", "cookie", "登录", "注册", "login", "sign up",
    "subscribe", "订阅", "menu", "导航", "footer", "header",
    "about", "contact", "联系我们", "image ", "img ", "icon ",
]


# ── 工具函数 ──────────────────────────────────────────────────────────────────

def is_noise(title: str) -> bool:
    if len(title) < 10:
        return True
    tl = title.lower()
    return any(kw in tl for kw in NOISE_KEYWORDS) or re.match(r"^(image\s+\d+|img\s*\d*)[:\s]", tl)


def today_str_cst() -> str:
    return datetime.now(CST).strftime("%Y%m%d")


def jina_fetch(url: str, timeout: int = 30) -> str:
    """通过 Jina 代理抓取页面，返回 markdown 文本"""
    result = subprocess.run(
        ["curl", "-s", "--max-time", str(timeout), f"https://r.jina.ai/{url}"],
        capture_output=True, text=True, timeout=timeout + 5,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"jina 抓取失败: {result.stderr[:100]}")
    return result.stdout


# ── Fetch 函数（每个都含当天自然日过滤）─────────────────────────────────────────

def fetch_qbitai(limit: int = 10) -> list:
    """量子位 — 只保留今天（Asia/Shanghai）发布的文章"""
    print("  [量子位] 抓取中...")
    try:
        content = jina_fetch("https://www.qbitai.com")
        now = datetime.now(CST)
        today_compact = now.strftime("%Y%m%d")
        today_slash   = now.strftime("%Y/%m/%d")

        news_list, seen = [], set()
        pattern = re.compile(
            r"\[([^\]]{10,300})\]\((https?://(?:www\.)?qbitai\.com/(\d{8})/[^\)]+)\)"
        )
        for title, url, art_date in pattern.findall(content):
            if len(news_list) >= limit:
                break
            if art_date != today_compact:
                continue
            title = title.strip()
            if title in seen or is_noise(title):
                continue
            seen.add(title)
            news_list.append({
                "title":  title[:200],
                "body":   "",
                "time":   today_slash,
                "source": "量子位",
                "link":   url,
            })
        print(f"  [量子位] ✅ {len(news_list)} 条（仅今日）")
        return news_list
    except Exception as e:
        print(f"  [量子位] ⚠️  失败: {e}")
        return []


def fetch_jiqizhixin(limit: int = 10) -> list:
    """机器之心 — 只保留今天（Asia/Shanghai）发布的文章"""
    print("  [机器之心] 抓取中...")
    try:
        content = jina_fetch("https://www.jiqizhixin.com")
        now        = datetime.now(CST)
        today_str  = now.strftime("%Y/%m/%d")

        news_list, seen = [], set()
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if len(news_list) >= limit:
                break
            line = line.strip()
            if not line or is_noise(line) or line.startswith(("#", "!", "URL", "Markdown", "Title:")):
                continue
            # 下一非空行用于判断日期
            next_ne = ""
            for j in range(i + 1, min(i + 4, len(lines))):
                c = lines[j].strip()
                if c:
                    next_ne = c
                    break
            is_today = next_ne == "今天"
            if not is_today:
                date_m = re.match(r"^(\d{4})[-/](\d{2})[-/](\d{2})", next_ne)
                if date_m:
                    art_date  = f"{date_m.group(1)}/{date_m.group(2)}/{date_m.group(3)}"
                    is_today  = (art_date == today_str)
                date_m2 = re.match(r"^(\d{1,2})月(\d{1,2})日", next_ne)
                if date_m2:
                    is_today = (int(date_m2.group(1)) == now.month and
                                int(date_m2.group(2)) == now.day)
            if is_today and line not in seen and len(line) >= 10:
                seen.add(line)
                news_list.append({
                    "title":  line[:200],
                    "body":   "",
                    "time":   today_str,
                    "source": "机器之心",
                    "link":   "https://www.jiqizhixin.com",
                })
        print(f"  [机器之心] ✅ {len(news_list)} 条（仅今日）")
        return news_list
    except Exception as e:
        print(f"  [机器之心] ⚠️  失败: {e}")
        return []


def fetch_arxiv(limit: int = 5) -> list:
    """arxiv cs.AI + cs.LG 各取 limit 篇，只取最新批次"""
    print("  [arxiv] 抓取中...")
    now        = datetime.now(CST)
    today_yymm = now.strftime("%y%m")
    results, seen = [], set()

    SKIP = {"artificial intelligence", "cs.ai", "cs.lg", "recent",
            "machine learning", "authors and titles", "quick links", "new changes"}

    for cat in ["cs.AI", "cs.LG"]:
        try:
            content = jina_fetch(f"https://arxiv.org/list/{cat}/recent", timeout=30)

            # 取第一批（最新）提交内容
            submission_positions = [m.start() for m in re.finditer(r"Submissions from", content)]
            if len(submission_positions) >= 2:
                block = content[submission_positions[0]:submission_positions[1]]
            elif len(submission_positions) == 1:
                block = content[submission_positions[0]:]
            else:
                block = content

            abs_pattern  = re.compile(r"https://arxiv\.org/abs/(\d{4}\.\d{4,5})")
            abs_positions = [(m.start(), m.group(0), m.group(1)[:4])
                             for m in abs_pattern.finditer(block)]

            title_pattern = re.compile(r"Title:\s*([^\n]{10,300})", re.MULTILINE)
            count = 0
            for tm in title_pattern.finditer(block):
                if count >= limit:
                    break
                title = tm.group(1).strip()
                if title in seen or title.lower() in SKIP or len(title) < 10:
                    continue
                best_url, paper_yymm = f"https://arxiv.org/list/{cat}/recent", None
                for pos, url, yymm in reversed(abs_positions):
                    if pos < tm.start():
                        best_url, paper_yymm = url, yymm
                        break
                if paper_yymm and paper_yymm != today_yymm:
                    continue
                seen.add(title)
                results.append({
                    "title":  title[:250],
                    "body":   "",
                    "time":   now.strftime("%Y/%m/%d"),
                    "source": f"arxiv {cat}",
                    "link":   best_url,
                })
                count += 1
            print(f"  [arxiv {cat}] ✅ {count} 条（仅最新批次）")
        except Exception as e:
            print(f"  [arxiv {cat}] ⚠️  失败: {e}")

    return results


def fetch_verge_ai(limit: int = 8) -> list:
    """
    The Verge AI — 通过官方 RSS 抓取，只保留今天（Asia/Shanghai）发布的文章。
    RSS: https://www.theverge.com/rss/ai-artificial-intelligence/index.xml
    """
    print("  [The Verge AI] 抓取中（RSS）...")
    RSS_URL = "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
    now       = datetime.now(CST)
    today     = now.date()

    try:
        req = urllib.request.Request(
            RSS_URL,
            headers={"User-Agent": "Mozilla/5.0 (compatible; quietview-bot/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            xml_bytes = resp.read()

        root = ET.fromstring(xml_bytes)
        ATOM_NS = "http://www.w3.org/2005/Atom"

        # Atom feed (<entry>) or RSS feed (<item>)
        # 注意：命名空间必须用 {ns}tag 格式，不能用 ns prefix 在 findall
        entries = (root.findall(f"{{{ATOM_NS}}}entry") or
                   root.findall(f".//{{{ATOM_NS}}}entry") or
                   root.findall(".//item"))
        news_list, seen = [], set()

        for entry in entries:
            if len(news_list) >= limit:
                break

            # Title
            title_el = entry.find(f"{{{ATOM_NS}}}title") or entry.find("title")
            title = (title_el.text or "").strip() if title_el is not None else ""
            if not title or is_noise(title) or title in seen:
                continue

            # Link
            link_el = entry.find(f"{{{ATOM_NS}}}link") or entry.find("link")
            if link_el is None:
                continue
            link = link_el.get("href") or (link_el.text or "").strip()
            if not link:
                continue

            # Published date
            pub_el = (entry.find(f"{{{ATOM_NS}}}published") or
                      entry.find(f"{{{ATOM_NS}}}updated") or
                      entry.find("pubDate") or
                      entry.find("published") or
                      entry.find("updated"))
            pub_text = (pub_el.text or "").strip() if pub_el is not None else ""

            pub_date = None
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%dT%H:%M:%SZ", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub_text, fmt)
                    pub_date = dt.astimezone(CST).date()
                    break
                except ValueError:
                    continue

            # 严格当天过滤
            if pub_date is None or pub_date != today:
                continue

            seen.add(title)
            news_list.append({
                "title":  title[:200],
                "body":   "",
                "time":   now.strftime("%Y/%m/%d"),
                "source": "The Verge",
                "link":   link,
            })

        print(f"  [The Verge AI] ✅ {len(news_list)} 条（仅今日）")
        return news_list
    except Exception as e:
        print(f"  [The Verge AI] ⚠️  失败: {e}")
        return []


def fetch_techcrunch_ai(limit: int = 8) -> list:
    """
    TechCrunch AI — 通过 RSS feed 抓取，过滤 category 含 artificial-intelligence 的条目，
    只保留今天（Asia/Shanghai）发布的文章。
    Feed: https://techcrunch.com/feed/
    """
    print("  [TechCrunch AI] 抓取中（RSS）...")
    FEED_URL  = "https://techcrunch.com/feed/"
    now       = datetime.now(CST)
    today     = now.date()

    try:
        req = urllib.request.Request(
            FEED_URL,
            headers={"User-Agent": "Mozilla/5.0 (compatible; quietview-bot/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            xml_bytes = resp.read()

        root  = ET.fromstring(xml_bytes)
        items = root.findall(".//item")
        news_list, seen = [], set()

        for item in items:
            if len(news_list) >= limit:
                break

            # Category filter: 必须含 artificial-intelligence
            cats = [c.text or "" for c in item.findall("category")]
            if not any("artificial-intelligence" in c.lower() or
                       "artificial intelligence" in c.lower()
                       for c in cats):
                continue

            # Title
            title_el = item.find("title")
            title = (title_el.text or "").strip() if title_el is not None else ""
            if not title or is_noise(title) or title in seen:
                continue

            # Link
            link_el = item.find("link")
            link = (link_el.text or "").strip() if link_el is not None else ""
            if not link:
                continue

            # Published date
            pub_el   = item.find("pubDate")
            pub_text = (pub_el.text or "").strip() if pub_el is not None else ""
            pub_date = None
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
                try:
                    dt = datetime.strptime(pub_text, fmt)
                    pub_date = dt.astimezone(CST).date()
                    break
                except ValueError:
                    continue

            # 严格当天过滤
            if pub_date is None or pub_date != today:
                continue

            seen.add(title)
            news_list.append({
                "title":  title[:200],
                "body":   "",
                "time":   now.strftime("%Y/%m/%d"),
                "source": "TechCrunch",
                "link":   link,
            })

        print(f"  [TechCrunch AI] ✅ {len(news_list)} 条（仅今日）")
        return news_list
    except Exception as e:
        print(f"  [TechCrunch AI] ⚠️  失败: {e}")
        return []


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    dry_run  = "--dry-run" in sys.argv
    now      = datetime.now(CST)
    date_str = now.strftime("%Y%m%d")
    now_str  = now.strftime("%Y.%m.%d %H:%M")

    print(f"{'='*60}")
    print(f"  quietview AI 声音全量抓取  {now_str} CST（JSON-only）")
    print(f"{'='*60}")

    # 1. 抓取各数据源
    ai_voice = []
    ai_voice.extend(fetch_qbitai(limit=10))
    ai_voice.extend(fetch_jiqizhixin(limit=10))
    ai_voice.extend(fetch_arxiv(limit=5))
    ai_voice.extend(fetch_verge_ai(limit=8))
    ai_voice.extend(fetch_techcrunch_ai(limit=8))

    total = len(ai_voice)
    print(f"\n  共 {total} 条 AI 资讯（当天）")

    if dry_run:
        print(f"[dry-run] would write {total} ai_voice items to data/{date_str}.json")
        for it in ai_voice[:5]:
            print(f"  [{it.get('source')}] {it.get('title','')[:60]}")
        return

    # 2. 追加去重写入（不覆盖已有数据）
    day_data = load_or_create_day_data(date_str)
    before   = len(day_data.get("ai_voice", []))
    day_data["ai_voice"] = dedup_append(
        day_data.get("ai_voice", []), ai_voice, key="link"
    )
    after    = len(day_data["ai_voice"])
    day_data["generated_at"] = datetime.now().isoformat()

    save_day_data(date_str, day_data)
    print(f"\n  ✅ data/{date_str}.json 更新完成")
    print(f"     ai_voice: {before} → {after} 条（新增 {after - before}）")

    # 3. 更新日期索引
    update_date_index(date_str)

    # 4. git push（只推 data/）
    git_push(f"auto: AI声音更新 {now_str} ({total}条)")
    print(f"  ✅ 完成 {now_str}")


if __name__ == "__main__":
    main()
