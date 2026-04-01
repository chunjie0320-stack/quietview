#!/usr/bin/env python3
"""
财联社行业资讯定时抓取脚本
每2小时更新 index.html 中的行业资讯区块
支持三种抓取方式：
  1. 直连财联社，解析 Next.js __NEXT_DATA__ JSON（最佳）
  2. Jina 代理抓取 Markdown 格式（备用）
"""

import re
import sys
import json
import os
import subprocess
import urllib.request
import shutil
from datetime import datetime
from html.parser import HTMLParser

HTML_PATH = "/root/.openclaw/workspace/index.html"
REPO_DIR  = "/root/.openclaw/workspace"

JINA_URL  = "https://r.jina.ai/https://www.cls.cn/telegraph"
CLS_URL   = "https://www.cls.cn/telegraph"

# 分类关键词映射
CATEGORY_MAP = {
    "部委动态": ["国务院", "发改委", "财政部", "央行", "证监会", "银保监", "工信部", "商务部",
                 "国家能源局", "部委", "政策", "政府", "国办", "国资委", "人民银行", "外汇局",
                 "市场监管", "海关", "税务", "国家市场"],
    "A股走势":  ["A股", "沪指", "深证", "创业板", "科创板", "涨停", "跌停", "板块", "龙头",
                 "上交所", "深交所", "北交所", "股价", "市值", "ST", "退市", "上市公司",
                 "净利润", "营业收入", "派息", "分红", "回购", "公告"],
    "国际市场": ["美股", "纳斯达克", "标普", "道指", "港股", "恒指", "日经", "欧股", "美联储",
                 "欧洲央行", "日元", "美元", "欧元", "汇率", "加息", "降息", "利率", "原油",
                 "铜价", "美国", "欧洲", "日本", "英国", "黄金", "银价", "铂金", "期货",
                 "波罗的海", "布伦特", "WTI"],
    "科技AI":   ["AI", "人工智能", "大模型", "芯片", "半导体", "光模块", "算力", "GPU", "英伟达",
                 "OpenAI", "谷歌", "微软", "Meta", "苹果", "华为", "CPO", "光纤", "数据中心",
                 "Token", "LLM", "transformer"],
    "地缘局势": ["伊朗", "以色列", "俄罗斯", "乌克兰", "中东", "导弹", "战争", "冲突", "制裁",
                 "关税", "特朗普", "北约", "叙利亚", "巴以", "哈马斯", "霍尔木兹", "以军",
                 "乌军", "俄军", "军事", "打击", "袭击"],
    "国内经济": ["GDP", "CPI", "PPI", "PMI", "出口", "进口", "贸易", "外资", "消费", "地产",
                 "房价", "房地产", "新能源", "电动车", "比亚迪", "宁德时代", "锂电",
                 "个体工商户", "就业", "创业"],
}


def fetch_cls_json():
    """优先尝试直连财联社，解析 __NEXT_DATA__ JSON；失败则用 Jina"""
    headers_direct = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.cls.cn/",
    }
    # 尝试直连
    try:
        from datetime import date
        today = date.today()
        req = urllib.request.Request(CLS_URL, headers=headers_direct)
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                html_content = resp.read().decode('utf-8', errors='ignore')
                # 提取 __NEXT_DATA__ JSON
                m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_content, re.DOTALL)
                if m:
                    next_data = json.loads(m.group(1))
                    tele_list = next_data.get('props', {}).get('initialState', {}).get(
                        'telegraph', {}).get('telegraphList', [])
                    if tele_list:
                        # 检查今日数据量，不足5条则降级到Jina（__NEXT_DATA__可能是静态缓存）
                        today_count = sum(
                            1 for item in tele_list
                            if item.get('ctime') and datetime.fromtimestamp(item['ctime']).date() == today
                        )
                        if today_count >= 5:
                            print(f"  ✅ 直连财联社成功，解析到 {len(tele_list)} 条（今日{today_count}条）")
                            return tele_list, 'json'
                        else:
                            print(f"  ⚠️  直连数据今日只有{today_count}条（可能是静态缓存），降级到 Jina")
    except Exception as e:
        print(f"  ⚠️  直连失败({e})，改用 Jina 代理")

    # Jina 代理（返回 Markdown）
    jina_req = urllib.request.Request(
        JINA_URL,
        headers={"User-Agent": "Mozilla/5.0", "Accept": "text/plain"},
    )
    with urllib.request.urlopen(jina_req, timeout=30) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
    print(f"  ✅ Jina 代理抓取成功，内容长度：{len(content)}")
    return content, 'markdown'


def parse_json_items(tele_list):
    """从财联社 JSON 数据中提取资讯条目（只保留今天的）"""
    from datetime import date
    today = date.today()
    items = []
    for item in tele_list:
        content = item.get('content', '').strip()
        title_raw = item.get('title', '').strip()
        ctime = item.get('ctime', 0)
        share_num = item.get('share_num', 0)
        reading_num = item.get('reading_num', 0)
        level = item.get('level', 'C')  # A/B/C 重要性

        if not content or len(content) < 10:
            continue

        # 只保留今天的数据
        if ctime:
            item_date = datetime.fromtimestamp(ctime).date()
            if item_date != today:
                continue

        # 提取标题：优先用 title 字段，其次从 content 中的【】提取
        if title_raw:
            title = title_raw[:50]
            # 清理正文
            body = re.sub(r'^【[^】]+】', '', content).strip()
            body = re.sub(r'^财联社\d+月\d+日电，?', '', body).strip()
        else:
            # 从 content 提取标题
            m = re.match(r'【([^】]+)】(.*)', content, re.DOTALL)
            if m:
                title = m.group(1)[:50]
                body = m.group(2).strip()
                body = re.sub(r'^财联社\d+月\d+日电，?', '', body).strip()
            else:
                # 无标题，用 content 前40字
                clean = re.sub(r'^财联社\d+月\d+日电，?', '', content).strip()
                if len(clean) <= 40:
                    title = clean
                    body = ""
                else:
                    title = clean[:38] + "…"
                    body = clean

        # 时间：从 ctime 转换
        if ctime:
            dt = datetime.fromtimestamp(ctime)
            time_str = dt.strftime("%H:%M")
        else:
            time_str = datetime.now().strftime("%H:%M")

        # 分类
        category = classify_item(title + ' ' + content)

        # 阅读量过滤
        importance = reading_num + share_num * 5
        if level == 'B':
            importance += 1000
        elif level == 'A':
            importance += 5000

        # 构造原文链接：优先用 content_id，其次 id，兜底用电报页
        content_id = item.get('content_id') or item.get('id')
        article_url = f'https://www.cls.cn/detail/{content_id}' if content_id else 'https://www.cls.cn/telegraph'

        items.append({
            'time': time_str,
            'tag': category,
            'title': title,
            'body': body[:150] if body else '',
            'source': '财联社',
            'source_url': article_url,
            'url': article_url,
            'link': article_url,
            'importance': importance,
            'level': level,
        })

    return items


def parse_cls_markdown(content):
    """解析 Jina 返回的 Markdown 格式财联社电报"""
    items = []

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 匹配时间行 HH:MM:SS
        time_match = re.match(r'^(\d{2}:\d{2}:\d{2})$', line)
        if time_match:
            time_str = time_match.group(1)[:5]  # HH:MM
            i += 1
            content_lines = []
            while i < len(lines):
                next_line = lines[i].strip()
                if re.match(r'^\d{2}:\d{2}:\d{2}$', next_line):
                    break
                # 跳过"阅 X.XXW"等行
                if re.match(r'^阅$', next_line) or re.match(r'^\d+\.\d+[WwKk万千]$', next_line):
                    i += 1
                    continue
                if next_line:
                    content_lines.append(next_line)
                i += 1

            if not content_lines:
                continue

            full_text = ' '.join(content_lines)
            title_match = re.match(r'\*\*【([^】]+)】\*\*\s*(.*)', full_text)
            if title_match:
                title = title_match.group(1)[:50]
                body = title_match.group(2).strip()
            else:
                clean = re.sub(r'\*\*', '', full_text)
                clean = re.sub(r'财联社\d+月\d+日电，?', '', clean)
                if len(clean) <= 40:
                    title = clean
                    body = ""
                else:
                    title = clean[:38] + "…"
                    body = clean

            body = re.sub(r'\*\*', '', body)
            body = re.sub(r'财联社\d+月\d+日电，?', '', body)
            body = body.strip()

            if len(title) < 5:
                continue

            category = classify_item(title + ' ' + body)

            items.append({
                'time': time_str,
                'tag': category,
                'title': title,
                'body': body[:150] if body else '',
                'source': '财联社',
                'source_url': 'https://www.cls.cn/telegraph',
                'url': 'https://www.cls.cn/telegraph',
                'link': 'https://www.cls.cn/telegraph',
                'importance': 0,
                'level': 'C',
            })
        else:
            i += 1

    return items


def classify_item(text):
    """根据关键词分类"""
    scores = {}
    for cat, keywords in CATEGORY_MAP.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return "市场动态"


def select_top_items(items, max_count=15):
    """按重要性选取，按分类均衡"""
    if not items:
        return []

    # 按 importance 排序
    items_sorted = sorted(items, key=lambda x: -x.get('importance', 0))

    selected = []
    cat_count = {}
    max_per_cat = 4

    for item in items_sorted:
        cat = item['tag']
        if cat_count.get(cat, 0) < max_per_cat and len(selected) < max_count:
            selected.append(item)
            cat_count[cat] = cat_count.get(cat, 0) + 1

    # 如果分类过滤导致数量不足，补充剩余
    remaining = [it for it in items_sorted if it not in selected]
    for item in remaining:
        if len(selected) >= max_count:
            break
        selected.append(item)

    return selected[:max_count]


def items_to_html(items):
    """将资讯列表转为 tl-item HTML"""
    if not items:
        return ""

    html_parts = []
    for item in items:
        source_html = f'<a class="tl-source" href="{item["source_url"]}" target="_blank">→ {item["source"]}</a>'
        body_part = ''
        if item.get('body'):
            body_part = f'<div class="tl-body">{_escape_html(item["body"])}</div>\n                '

        html_parts.append(
            f'\n<div class="tl-item">\n'
            f'                <div class="tl-dot"></div>\n'
            f'                <div class="tl-time">{_escape_html(item["time"])}</div>\n'
            f'                <div class="tl-tag">{_escape_html(item["tag"])}</div>\n'
            f'                <div class="tl-title">{_escape_html(item["title"])}</div>\n'
            f'                {body_part}{source_html}\n'
            f'              </div>'
        )

    return ''.join(html_parts)


def _escape_html(s):
    if not s:
        return ''
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;'))


def update_html(html_path, items, date_str=None):
    """
    替换 HTML 中当天日期的 INJECT:news_YYYYMMDD 区块。
    date_str: YYYYMMDD（默认取今天）
    严格按日期写入对应 panel，不再使用全局 investment_news 标记。
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    items_html = items_to_html(items)
    count = len(items)

    inject_key = f"news_{date_str}"
    pattern = re.compile(
        r'(<!-- INJECT:' + inject_key + r' -->)(.*?)(<!-- /INJECT:' + inject_key + r' -->)',
        re.DOTALL
    )
    if not pattern.search(html):
        # 兼容旧全局标记（迁移期容错）
        old_pattern = r'(<!-- INJECT:investment_news -->)(.*?)(<!-- /INJECT:investment_news -->)'
        old_n = re.search(old_pattern, html, re.DOTALL)
        if old_n:
            print(f"  ⚠️  未找到 INJECT:{inject_key}，使用旧全局标记（兼容模式）", file=sys.stderr)
            def make_replacer(items_str):
                def replacer(m):
                    return m.group(1) + items_str + '\n              ' + m.group(3)
                return replacer
            new_html, _ = re.subn(old_pattern, make_replacer(items_html), html, flags=re.DOTALL)
            # 更新旧 badge
            new_html = re.sub(
                r'(<span class="col-count-badge" id="news-count">)[^<]*(</span>)',
                rf'\g<1>· {count}\g<2>',
                new_html
            )
        else:
            print(f"❌ 未找到 INJECT:{inject_key} 也未找到全局标记，终止", file=sys.stderr)
            sys.exit(1)
    else:
        def replacer(m):
            return m.group(1) + '\n' + items_html + '\n              ' + m.group(3)
        new_html = pattern.sub(replacer, html)
        # 更新当天 badge
        new_html = re.sub(
            r'(<span class="col-count-badge" id="news-count-' + date_str + r'">)[^<]*(</span>)',
            rf'\g<1>· {count}\g<2>',
            new_html
        )

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"  ✅ HTML 更新完成（{date_str}），共 {count} 条资讯")
    return count


def verify_divs(html_path):
    """div 自查，确保 depth=0"""
    class DivCounter(HTMLParser):
        def __init__(self):
            super().__init__()
            self.depth = 0

        def handle_starttag(self, tag, attrs):
            if tag == 'div':
                self.depth += 1

        def handle_endtag(self, tag):
            if tag == 'div':
                self.depth -= 1

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    counter = DivCounter()
    counter.feed(html)

    if counter.depth != 0:
        raise ValueError(f"div depth={counter.depth}，不为0！终止push")
    print(f"  ✅ div depth 自查通过 (depth=0)")


def git_push(item_count):
    """git commit + push（走全局锁防并发冲突）"""
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from git_lock import git_push_with_lock
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
    msg = f"auto: 行业资讯更新 {now_str} ({item_count}条)"
    git_push_with_lock(REPO_DIR, msg, files_to_add=['index.html', 'data/'])


def main():
    now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
    print(f"[{now_str}] 财联社行业资讯更新开始...")

    # 备份
    backup_path = f"{HTML_PATH}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(HTML_PATH, backup_path)
    print(f"  备份: {os.path.basename(backup_path)}")

    try:
        # 1. 抓取
        data, fmt = fetch_cls_json()

        # 2. 解析
        if fmt == 'json':
            items = parse_json_items(data)
        else:
            items = parse_cls_markdown(data)

        print(f"  解析到 {len(items)} 条原始资讯")

        if not items:
            print("  ⚠️  未解析到任何资讯，保持原内容不变")
            return

        # 3. 筛选
        top_items = select_top_items(items, max_count=15)
        print(f"  筛选后 {len(top_items)} 条")

        # 4. 更新 JSON（主数据源）
        date_str = datetime.now().strftime("%Y%m%d")
        json_path = os.path.join(REPO_DIR, "data", f"{date_str}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                day_data = json.load(f)
        else:
            day_data = {"date": date_str, "generated_at": datetime.now().isoformat(), "voice": [], "news": [], "ai_voice": [], "miao_notice": []}
        # 去掉 importance/level 字段后写入
        clean_items = [{k: v for k, v in item.items() if k not in ('importance', 'level', 'source_url')} for item in top_items]
        day_data["news"] = clean_items
        day_data["generated_at"] = datetime.now().isoformat()
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(day_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ JSON 更新完成: data/{date_str}.json ({len(clean_items)}条)")

        # 5. 更新 HTML（严格写入当天日期的 panel）
        count = update_html(HTML_PATH, top_items, date_str=date_str)

        # 6. div 自查
        verify_divs(HTML_PATH)

        # 7. git push
        git_push(count)

        print(f"[{now_str}] ✅ 完成")

    except Exception as e:
        print(f"[{now_str}] ❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
