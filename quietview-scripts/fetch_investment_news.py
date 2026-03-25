#!/usr/bin/env python3
"""
fetch_investment_news.py
抓取A股/财经资讯，三级降级策略：
  Level 1: jina代理抓财联社电报
  Level 2: akshare东方财富新闻
  Level 3: 返回空列表，不报错
输出：/root/.openclaw/workspace/data/investment_news.json
"""

import json
import os
import re
import subprocess
from datetime import datetime

OUTPUT_PATH = "/root/.openclaw/workspace/data/investment_news.json"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


def fetch_cls_via_jina() -> list:
    """Level 1: 通过 jina 代理抓取财联社电报，取前20条"""
    print("[Level 1] 尝试抓取财联社 via jina...")
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30",
             "https://r.jina.ai/https://www.cls.cn/telegraph"],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode != 0 or not result.stdout.strip():
            raise ValueError("curl 返回空或失败")

        content = result.stdout
        news_list = []

        # 财联社电报格式解析：寻找标题+时间+内容块
        # jina返回markdown格式，每条电报通常有时间戳和正文
        # 匹配形如 "HH:MM" 或 "MM-DD HH:MM" 的时间行
        pattern = re.compile(
            r'(?:#+\s*)?(\d{1,2}:\d{2}(?::\d{2})?|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})'
            r'[^\n]*\n(.*?)(?=\n(?:#+\s*)?\d{1,2}:\d{2}|\Z)',
            re.DOTALL
        )

        today = datetime.now().strftime("%Y-%m-%d")
        matches = pattern.findall(content)

        for i, (time_str, body) in enumerate(matches[:20]):
            body = body.strip()
            # 取第一行作为标题，其余作为摘要
            lines = [l.strip() for l in body.split('\n') if l.strip()]
            title = lines[0] if lines else body[:80]
            summary = ' '.join(lines[1:3]) if len(lines) > 1 else title

            # 清理markdown标记
            title = re.sub(r'\[.*?\]\(.*?\)', '', title).strip()
            summary = re.sub(r'\[.*?\]\(.*?\)', '', summary).strip()

            if not title:
                continue

            news_list.append({
                "time": f"{today} {time_str}" if len(time_str) <= 8 else time_str,
                "title": title[:200],
                "summary": summary[:500] if summary else title[:200],
                "source": "财联社",
                "url": "https://www.cls.cn/telegraph"
            })

        # 如果正则没匹配到，尝试备用解析
        if not news_list:
            news_list = _parse_jina_fallback(content, "财联社", "https://www.cls.cn/telegraph", limit=20)

        print(f"[Level 1] 财联社抓取成功，共 {len(news_list)} 条")
        return news_list

    except Exception as e:
        print(f"[Level 1] 财联社抓取失败: {e}")
        return []


def _parse_jina_fallback(content: str, source: str, base_url: str, limit: int = 20) -> list:
    """通用jina内容备用解析：提取markdown链接和段落"""
    news_list = []
    today = datetime.now().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M")

    # 提取所有markdown链接 [title](url)
    link_pattern = re.compile(r'\[([^\]]{10,200})\]\((https?://[^\)]+)\)')
    matches = link_pattern.findall(content)

    seen_titles = set()
    for title, url in matches:
        title = title.strip()
        if title in seen_titles or len(title) < 10:
            continue
        if any(skip in title.lower() for skip in ['javascript', 'cookie', '登录', '注册', 'login']):
            continue
        seen_titles.add(title)
        news_list.append({
            "time": f"{today} {now_time}",
            "title": title[:200],
            "summary": title[:200],
            "source": source,
            "url": url
        })
        if len(news_list) >= limit:
            break

    # 如果链接也没有，按段落分割
    if not news_list:
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 20]
        for para in paragraphs[:limit]:
            first_line = para.split('\n')[0].strip()
            first_line = re.sub(r'^#+\s*', '', first_line)
            if len(first_line) < 10:
                continue
            news_list.append({
                "time": f"{today} {now_time}",
                "title": first_line[:200],
                "summary": para[:500],
                "source": source,
                "url": base_url
            })

    return news_list


def fetch_eastmoney_via_akshare() -> list:
    """Level 2: akshare 东方财富新闻"""
    print("[Level 2] 尝试 akshare 东方财富新闻...")
    try:
        import akshare as ak
        df = ak.stock_news_em()
        news_list = []
        for _, row in df.head(20).iterrows():
            news_list.append({
                "time": str(row.get("发布时间", datetime.now().strftime("%Y-%m-%d %H:%M"))),
                "title": str(row.get("新闻标题", ""))[:200],
                "summary": str(row.get("新闻内容", ""))[:500],
                "source": "东方财富",
                "url": str(row.get("新闻链接", "https://finance.eastmoney.com"))
            })
        print(f"[Level 2] 东方财富抓取成功，共 {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"[Level 2] akshare 失败: {e}")
        return []


def main():
    news = []

    # Level 1
    news = fetch_cls_via_jina()

    # Level 2
    if not news:
        news = fetch_eastmoney_via_akshare()

    # Level 3: 空列表，不报错
    if not news:
        print("[Level 3] 所有来源失败，输出空列表")

    output = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "count": len(news),
        "news": news
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！共 {len(news)} 条财经资讯 → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
