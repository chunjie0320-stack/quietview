#!/usr/bin/env python3
"""
财联社行业资讯定时抓取脚本（C方案 — JSON-only）

职责：只写 data/YYYYMMDD.json 的 news[] 字段，不碰 index.html。
支持三种抓取方式：
  1. 直连财联社，解析 Next.js __NEXT_DATA__ JSON（最佳）
  2. Jina 代理抓取 Markdown 格式（备用）

用法：
  python3 cls_news_updater.py             # 正常运行
  python3 cls_news_updater.py --dry-run   # 只打印，不写文件，不 git push
"""

import re
import sys
import json
import os
import urllib.request
from datetime import datetime, date

# ── 公共工具 ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    REPO_DIR, DATA_DIR,
    load_or_create_day_data, save_day_data,
    dedup_append, update_date_index, git_push,
)

JINA_URL = "https://r.jina.ai/https://www.cls.cn/telegraph"
CLS_URL  = "https://www.cls.cn/telegraph"

# ── 分类关键词映射 ─────────────────────────────────────────────────────────────
CATEGORY_MAP = {
    "部委动态": ["国务院", "发改委", "财政部", "央行", "证监会", "银保监", "工信部", "商务部",
                 "国家能源局", "部委", "政策", "政府", "国办", "国资委", "人民银行", "外汇局",
                 "市场监管", "海关", "税务"],
    "A股走势":  ["A股", "沪指", "深证", "创业板", "科创板", "涨停", "跌停", "板块", "龙头",
                 "上交所", "深交所", "北交所", "股价", "市值", "ST", "退市", "净利润",
                 "营业收入", "派息", "分红", "回购", "公告"],
    "国际市场": ["美股", "纳斯达克", "标普", "道指", "港股", "恒指", "日经", "欧股", "美联储",
                 "欧洲央行", "日元", "美元", "欧元", "汇率", "加息", "降息", "利率", "原油",
                 "铜价", "黄金", "银价", "期货", "布伦特", "WTI"],
    "科技AI":   ["AI", "人工智能", "大模型", "芯片", "半导体", "光模块", "算力", "GPU", "英伟达",
                 "OpenAI", "谷歌", "微软", "Meta", "苹果", "华为", "CPO", "数据中心", "LLM"],
    "地缘局势": ["伊朗", "以色列", "俄罗斯", "乌克兰", "中东", "导弹", "战争", "冲突", "制裁",
                 "关税", "特朗普", "北约", "叙利亚", "巴以", "哈马斯", "军事", "袭击"],
    "国内经济": ["GDP", "CPI", "PPI", "PMI", "出口", "进口", "贸易", "外资", "消费", "地产",
                 "房价", "房地产", "新能源", "电动车", "比亚迪", "宁德时代", "就业", "创业"],
}


# ── 抓取 ──────────────────────────────────────────────────────────────────────

def fetch_cls_json():
    """优先直连财联社，解析 __NEXT_DATA__ JSON；失败则 Jina 代理"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": "https://www.cls.cn/",
    }
    try:
        today = date.today()
        req = urllib.request.Request(CLS_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                html = resp.read().decode("utf-8", errors="ignore")
                m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
                if m:
                    next_data  = json.loads(m.group(1))
                    tele_list  = (next_data.get("props", {}).get("initialState", {})
                                  .get("telegraph", {}).get("telegraphList", []))
                    if tele_list:
                        today_count = sum(
                            1 for it in tele_list
                            if it.get("ctime") and datetime.fromtimestamp(it["ctime"]).date() == today
                        )
                        if today_count >= 5:
                            print(f"  ✅ 直连财联社成功（今日{today_count}条）")
                            return tele_list, "json"
                        else:
                            print(f"  ⚠️  直连数据今日只有{today_count}条，降级 Jina")
    except Exception as e:
        print(f"  ⚠️  直连失败({e})，改用 Jina")

    jina_req = urllib.request.Request(
        JINA_URL,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "text/plain"},
    )
    with urllib.request.urlopen(jina_req, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="ignore")
    print(f"  ✅ Jina 代理成功（{len(content)} 字符）")
    return content, "markdown"


# ── 解析 ──────────────────────────────────────────────────────────────────────

def classify_item(text: str) -> str:
    scores = {}
    for cat, keywords in CATEGORY_MAP.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[cat] = score
    return max(scores, key=scores.get) if scores else "市场动态"


def parse_json_items(tele_list: list) -> list:
    """从财联社 JSON 提取今日条目"""
    today = date.today()
    items = []
    for item in tele_list:
        content   = item.get("content", "").strip()
        title_raw = item.get("title", "").strip()
        ctime     = item.get("ctime", 0)
        level     = item.get("level", "C")
        reading   = item.get("reading_num", 0)
        sharing   = item.get("share_num", 0)

        if not content or len(content) < 10:
            continue
        if ctime and datetime.fromtimestamp(ctime).date() != today:
            continue

        if title_raw:
            title = title_raw[:60]
            body  = re.sub(r"^【[^】]+】", "", content).strip()
            body  = re.sub(r"^财联社\d+月\d+日电，?", "", body).strip()
        else:
            m = re.match(r"【([^】]+)】(.*)", content, re.DOTALL)
            if m:
                title = m.group(1)[:60]
                body  = m.group(2).strip()
                body  = re.sub(r"^财联社\d+月\d+日电，?", "", body).strip()
            else:
                clean = re.sub(r"^财联社\d+月\d+日电，?", "", content).strip()
                title = clean[:38] + ("…" if len(clean) > 38 else "")
                body  = clean

        time_str   = datetime.fromtimestamp(ctime).strftime("%H:%M") if ctime else datetime.now().strftime("%H:%M")
        importance = reading + sharing * 5 + (5000 if level == "A" else 1000 if level == "B" else 0)

        content_id  = item.get("content_id") or item.get("id")
        article_url = (f"https://www.cls.cn/detail/{content_id}"
                       if content_id else "https://www.cls.cn/telegraph")

        items.append({
            "time":       time_str,
            "tag":        classify_item(title + " " + content),
            "title":      title,
            "body":       body[:150] if body else "",
            "source":     "财联社",
            "link":       article_url,
            "_importance": importance,
        })
    return items


def parse_cls_markdown(content: str) -> list:
    """解析 Jina 返回的 Markdown 格式财联社电报"""
    items = []
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        time_match = re.match(r"^(\d{2}:\d{2}:\d{2})$", line)
        if time_match:
            time_str = time_match.group(1)[:5]
            i += 1
            content_lines = []
            while i < len(lines):
                nl = lines[i].strip()
                if re.match(r"^\d{2}:\d{2}:\d{2}$", nl):
                    break
                if re.match(r"^阅$", nl) or re.match(r"^\d+\.\d+[WwKk万千]$", nl):
                    i += 1
                    continue
                if nl:
                    content_lines.append(nl)
                i += 1
            if not content_lines:
                continue
            full_text   = " ".join(content_lines)
            title_match = re.match(r"\*\*【([^】]+)】\*\*\s*(.*)", full_text)
            if title_match:
                title = title_match.group(1)[:60]
                body  = title_match.group(2).strip()
            else:
                clean = re.sub(r"\*\*", "", full_text)
                clean = re.sub(r"财联社\d+月\d+日电，?", "", clean)
                title = clean[:38] + ("…" if len(clean) > 38 else "")
                body  = clean
            body = re.sub(r"\*\*", "", body)
            body = re.sub(r"财联社\d+月\d+日电，?", "", body).strip()
            if len(title) < 5:
                continue
            items.append({
                "time":       time_str,
                "tag":        classify_item(title + " " + body),
                "title":      title,
                "body":       body[:150] if body else "",
                "source":     "财联社",
                "link":       "https://www.cls.cn/telegraph",
                "_importance": 0,
            })
        else:
            i += 1
    return items


def select_top_items(items: list, max_count: int = 15) -> list:
    """按重要性选取，分类均衡"""
    if not items:
        return []
    items_sorted = sorted(items, key=lambda x: -x.get("_importance", 0))
    selected, cat_count = [], {}
    for item in items_sorted:
        cat = item["tag"]
        if cat_count.get(cat, 0) < 4 and len(selected) < max_count:
            selected.append(item)
            cat_count[cat] = cat_count.get(cat, 0) + 1
    remaining = [it for it in items_sorted if it not in selected]
    for item in remaining:
        if len(selected) >= max_count:
            break
        selected.append(item)
    return selected[:max_count]


# ── 字段清洗 ──────────────────────────────────────────────────────────────────

_STRIP_KEYS = {"importance", "level", "source_url", "url", "_importance"}

def clean_item(item: dict) -> dict:
    """删除禁止出现的字段，统一用 link"""
    return {k: v for k, v in item.items() if k not in _STRIP_KEYS}


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    dry_run  = "--dry-run" in sys.argv
    now_str  = datetime.now().strftime("%Y.%m.%d %H:%M")
    date_str = datetime.now().strftime("%Y%m%d")
    print(f"[{now_str}] 财联社行业资讯更新开始（JSON-only）...")

    try:
        # 1. 抓取
        data, fmt = fetch_cls_json()

        # 2. 解析
        items = parse_json_items(data) if fmt == "json" else parse_cls_markdown(data)
        print(f"  解析到 {len(items)} 条原始资讯")

        if not items:
            print("  ⚠️  未解析到任何资讯，保持原内容不变")
            return

        # 3. 筛选
        top_items = select_top_items(items, max_count=15)
        print(f"  筛选后 {len(top_items)} 条")

        # 4. 字段清洗（删掉 url/source_url/importance/level，统一用 link）
        clean_items = [clean_item(it) for it in top_items]

        if dry_run:
            print(f"[dry-run] would write {len(clean_items)} news items to data/{date_str}.json")
            for it in clean_items[:3]:
                print(f"  [{it.get('time')}] {it.get('title','')[:50]}")
            return

        # 5. 读取当天 JSON，追加去重写入 news[]
        day_data = load_or_create_day_data(date_str)
        day_data["news"] = dedup_append(
            day_data.get("news", []), clean_items, key="link"
        )
        day_data["generated_at"] = datetime.now().isoformat()

        # 6. 原子写入
        save_day_data(date_str, day_data)
        print(f"  ✅ JSON 更新完成: data/{date_str}.json ({len(day_data['news'])}条)")

        # 7. 更新日期索引
        update_date_index(date_str)

        # 8. git push（只推 data/）
        git_push(f"auto: 行业资讯更新 {now_str} ({len(clean_items)}条)")

        print(f"[{now_str}] ✅ 完成")

    except Exception as e:
        print(f"[{now_str}] ❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
