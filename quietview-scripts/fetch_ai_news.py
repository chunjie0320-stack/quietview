#!/usr/bin/env python3
"""
fetch_ai_news.py
抓取AI行业动态，三个来源独立抓取，失败跳过：
  - 量子位 (qbitai.com)       → 前10条
  - 机器之心 (jiqizhixin.com) → 前10条
  - arxiv cs.AI recent        → 前5条
输出：/root/.openclaw/workspace/data/ai_news.json
"""

import json
import os
import re
import subprocess
from datetime import datetime

OUTPUT_PATH = "/root/.openclaw/workspace/data/ai_news.json"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# 噪音关键词（过滤导航/广告等）
NOISE_KEYWORDS = [
    'javascript', 'cookie', '登录', '注册', 'login', 'sign up',
    'subscribe', '订阅', 'menu', '导航', 'footer', 'header',
    'about', 'contact', '联系我们', 'image ', 'img ', 'icon '
]


def jina_fetch(url: str, timeout: int = 30) -> str:
    """通过 jina 代理抓取目标页面，返回 markdown 文本"""
    jina_url = f"https://r.jina.ai/{url}"
    result = subprocess.run(
        ["curl", "-s", "--max-time", str(timeout), jina_url],
        capture_output=True, text=True, timeout=timeout + 5
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed (code {result.returncode}): {result.stderr[:200]}")
    if not result.stdout.strip():
        raise RuntimeError("curl returned empty content")
    return result.stdout


def is_noise(title: str) -> bool:
    """判断标题是否为噪音"""
    if len(title) < 10:
        return True
    t_lower = title.lower()
    if any(kw in t_lower for kw in NOISE_KEYWORDS):
        return True
    if re.match(r'^(image\s+\d+|img\s*\d*)[:\s]', t_lower):
        return True
    return False


def parse_links_generic(content: str, source: str, base_url: str, limit: int = 10) -> list:
    """通用：从 jina markdown 中提取 [title](url) 链接"""
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")
    news_list = []
    seen = set()

    link_pattern = re.compile(r'\[([^\]]{10,300})\]\((https?://[^\)]{10,})\)')
    for title, url in link_pattern.findall(content):
        title = title.strip()
        if title in seen or is_noise(title):
            continue
        seen.add(title)

        time_match = re.search(
            r'(\d{4}[-/]\d{2}[-/]\d{2}|\d{2}:\d{2})',
            content[max(0, content.find(title) - 50): content.find(title) + len(title) + 50]
        )
        time_str = time_match.group(1) if time_match else f"{today} {now_time}"

        news_list.append({
            "time": time_str,
            "title": title[:300],
            "summary": title[:300],
            "source": source,
            "url": url
        })
        if len(news_list) >= limit:
            break

    return news_list


# ─────────────────────────────────────────
# 量子位
# ─────────────────────────────────────────
def fetch_qbitai(limit: int = 10) -> list:
    """量子位：页面有完整文章链接，直接提取"""
    print("[量子位] 抓取中...")
    try:
        content = jina_fetch("https://www.qbitai.com")
        news = parse_links_generic(content, "量子位", "https://www.qbitai.com", limit=limit)
        print(f"[量子位] 成功，共 {len(news)} 条")
        return news
    except Exception as e:
        print(f"[量子位] 失败，跳过: {e}")
        return []


# ─────────────────────────────────────────
# 机器之心
# ─────────────────────────────────────────
def fetch_jiqizhixin(limit: int = 10) -> list:
    """
    机器之心：jina 渲染后无文章链接，格式为：
      标题文字\n今天\n标签...\n![img]
    通过"标题行后跟'今天'/'昨天'"规律识别文章。
    """
    print("[机器之心] 抓取中...")
    try:
        content = jina_fetch("https://www.jiqizhixin.com")
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")
        news_list = []
        seen = set()

        lines = content.split('\n')
        for i, line in enumerate(lines):
            if len(news_list) >= limit:
                break
            line = line.strip()
            if not line or is_noise(line) or line.startswith('#') or \
               line.startswith('!') or line.startswith('URL') or \
               line.startswith('Markdown') or line.startswith('Title:'):
                continue

            # 跳过空行找下一个非空行（标题和"今天"之间可能有空行）
            next_nonempty = ''
            for j in range(i + 1, min(i + 4, len(lines))):
                candidate = lines[j].strip()
                if candidate:
                    next_nonempty = candidate
                    break

            is_article = (
                next_nonempty in ('今天', '昨天') or
                re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}', next_nonempty) or
                re.match(r'^\d{1,2}月\d{1,2}日', next_nonempty)
            )
            if is_article and line not in seen and len(line) >= 10:
                seen.add(line)
                news_list.append({
                    "time": f"{today} {now_time}",
                    "title": line[:300],
                    "summary": line[:300],
                    "source": "机器之心",
                    "url": "https://www.jiqizhixin.com"
                })

        # 备用：链接解析
        if not news_list:
            news_list = parse_links_generic(
                content, "机器之心", "https://www.jiqizhixin.com", limit=limit
            )

        print(f"[机器之心] 成功，共 {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"[机器之心] 失败，跳过: {e}")
        return []


# ─────────────────────────────────────────
# arxiv cs.AI
# ─────────────────────────────────────────
def fetch_arxiv_ai(limit: int = 5) -> list:
    """
    arxiv cs.AI：jina 渲染保留了原始格式：
      [arXiv:XXXX.XXXXX](url "Abstract") ...
      Title: 论文标题
      作者...
    通过 Title: 行 + 向前匹配最近 abs URL 来提取。
    """
    print("[arxiv cs.AI] 抓取中...")
    try:
        content = jina_fetch("https://arxiv.org/list/cs.AI/recent")
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")
        news_list = []
        seen = set()

        # 跳过的页面级标题
        SKIP_TITLES = {
            'artificial intelligence', 'cs.ai', 'recent', 'authors and titles',
            'quick links', 'new changes'
        }

        # 收集所有 abs URL 的位置
        abs_url_pattern = re.compile(r'https://arxiv\.org/abs/(\d{4}\.\d{4,5})')
        abs_positions = [
            (m.start(), m.group(0)) for m in abs_url_pattern.finditer(content)
        ]

        # 遍历所有 Title: 行
        title_pattern = re.compile(r'Title:\s*([^\n]{10,300})', re.MULTILINE)
        for tm in title_pattern.finditer(content):
            if len(news_list) >= limit:
                break
            title = tm.group(1).strip()
            if title in seen or title.lower() in SKIP_TITLES or len(title) < 10:
                continue

            # 向前查找最近的 abs URL
            title_pos = tm.start()
            best_url = "https://arxiv.org/list/cs.AI/recent"
            for pos, url in reversed(abs_positions):
                if pos < title_pos:
                    best_url = url
                    break

            seen.add(title)
            news_list.append({
                "time": f"{today} {now_time}",
                "title": title[:300],
                "summary": title[:300],
                "source": "arxiv cs.AI",
                "url": best_url
            })

        print(f"[arxiv cs.AI] 成功，共 {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"[arxiv cs.AI] 失败，跳过: {e}")
        return []


# ─────────────────────────────────────────
# 主程序
# ─────────────────────────────────────────
def main():
    all_news = []

    # 三个来源独立抓，失败跳过
    all_news.extend(fetch_qbitai(limit=10))
    all_news.extend(fetch_jiqizhixin(limit=10))
    all_news.extend(fetch_arxiv_ai(limit=5))

    output = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(all_news),
        "news": all_news
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！共 {len(all_news)} 条AI资讯 → {OUTPUT_PATH}")
    print(f"   量子位:   {sum(1 for n in all_news if n['source'] == '量子位')} 条")
    print(f"   机器之心: {sum(1 for n in all_news if n['source'] == '机器之心')} 条")
    print(f"   arxiv:    {sum(1 for n in all_news if n['source'] == 'arxiv cs.AI')} 条")


if __name__ == "__main__":
    main()
