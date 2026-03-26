#!/usr/bin/env python3
"""
quietview 全量数据抓取脚本
用于 GitHub Actions 定时执行

输出：data/YYYYMMDD.json
结构：
  voice      - 投资·行业声音（微信5公众号）
  news       - 投资·行业资讯（财联社）
  ai_voice   - AI·行业声音（量子位 + 机器之心 + arxiv cs.AI/cs.LG）
  miao_notice - 喵子判断

环境变量（GitHub Actions Secrets）：
  WX_TOKEN, WX_COOKIE
"""

import os
import re
import sys
import json
import subprocess
from datetime import datetime, timezone, timedelta

# ── 时区 ──────────────────────────────────────────────────────────────────────
CST = timezone(timedelta(hours=8))

# ── 微信公众号配置 ─────────────────────────────────────────────────────────────
ACCOUNTS = [
    {"name": "财躺平",            "biz": "MzUyNTU4NzY5MA==", "color": "rgba(224,123,57,.12)", "text_color": "#e07b39"},
    {"name": "卓哥投研笔记",      "biz": "Mzk0MzY0OTU5Ng==", "color": "rgba(46,125,50,.1)",   "text_color": "#2e7d32"},
    {"name": "中金点睛",          "biz": "MzI3MDMzMjg0MA==", "color": "rgba(21,101,192,.1)",  "text_color": "#1565c0"},
    {"name": "方伟看十年",        "biz": "MzU5OTAzMDg1OQ==", "color": "rgba(106,27,154,.1)",  "text_color": "#6a1b9a"},
    {"name": "刘煜辉的高维宏观",  "biz": "MzYzNzAzODcwNw==", "color": "rgba(198,40,40,.1)",   "text_color": "#c62828"},
]

# ── 财联社分类关键词 ───────────────────────────────────────────────────────────
CATEGORY_MAP = {
    "部委动态": ["国务院", "发改委", "财政部", "央行", "证监会", "银保监", "工信部", "商务部",
                 "国家能源局", "部委", "政策", "政府", "国办", "国资委", "人民银行", "外汇局"],
    "A股走势":  ["A股", "沪指", "深证", "创业板", "科创板", "涨停", "跌停", "板块", "龙头",
                 "上交所", "深交所", "北交所", "股价", "市值", "净利润", "营业收入", "分红", "回购"],
    "国际市场": ["美股", "纳斯达克", "标普", "道指", "港股", "恒指", "日经", "欧股", "美联储",
                 "欧洲央行", "加息", "降息", "利率", "原油", "黄金", "美元", "汇率"],
    "科技AI":   ["AI", "人工智能", "大模型", "芯片", "半导体", "光模块", "算力", "GPU", "英伟达",
                 "OpenAI", "谷歌", "微软", "Meta", "苹果", "华为", "数据中心"],
    "地缘局势": ["伊朗", "以色列", "俄罗斯", "乌克兰", "中东", "导弹", "战争", "冲突", "制裁",
                 "关税", "特朗普", "北约", "军事", "袭击"],
    "国内经济": ["GDP", "CPI", "PPI", "PMI", "出口", "进口", "贸易", "外资", "消费", "地产",
                 "房价", "房地产", "新能源", "电动车", "就业"],
}

# ── 噪音关键词（AI新闻过滤） ──────────────────────────────────────────────────
NOISE_KEYWORDS = [
    'javascript', 'cookie', '登录', '注册', 'login', 'sign up',
    'subscribe', '订阅', 'menu', '导航', 'footer', 'header',
    'about', 'contact', '联系我们', 'image ', 'img ', 'icon '
]


# ══════════════════════════════════════════════════════════════════════════════
# 模块 1：微信公众号（投资·行业声音）
# ══════════════════════════════════════════════════════════════════════════════

def load_wx_cookie():
    """
    优先从环境变量 WX_COOKIE（完整 cookie 字符串）读取。
    fallback 到本地 ~/.openclaw/weibo/cookies.env，
    从 WX_SLAVE_SID / WX_SLAVE_USER / WX_BIZUIN 字段构造 cookie。
    """
    token = os.environ.get('WX_TOKEN', '').strip()
    cookie = os.environ.get('WX_COOKIE', '').strip()

    if not cookie:
        cookie_file = os.path.expanduser('~/.openclaw/weibo/cookies.env')
        if os.path.exists(cookie_file):
            env_map = {}
            with open(cookie_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    env_map[k.strip()] = v.strip()
            # 支持完整 cookie 字段
            if env_map.get('WX_COOKIE'):
                cookie = env_map['WX_COOKIE']
            elif env_map.get('WX_SLAVE_SID'):
                sid  = env_map.get('WX_SLAVE_SID', '')
                user = env_map.get('WX_SLAVE_USER', '')
                biz  = env_map.get('WX_BIZUIN', '')
                cookie = f"slave_sid={sid}; slave_user={user}; bizuin={biz}"
            if not token and env_map.get('WX_TOKEN'):
                token = env_map['WX_TOKEN']

    return token, cookie


def fetch_wx_articles(biz, cookie, count=3):
    """通过微信公众号文章列表接口（getmsg）获取最新文章"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.45",
        "Referer": f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124",
        "Cookie": cookie,
    }

    # Step 1: 访问主页拿 appmsg_token
    import urllib.request
    profile_url = f"https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz={biz}&scene=124"
    req = urllib.request.Request(profile_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        profile_html = resp.read().decode('utf-8', errors='ignore')

    token_m = re.search(r'"appmsg_token"\s*:\s*"([^"]+)"', profile_html)
    if not token_m:
        if 'verify' in profile_html.lower() or '验证' in profile_html:
            raise RuntimeError("Cookie 已过期，需要重新登录")
        raise RuntimeError("无法提取 appmsg_token")

    appmsg_token = token_m.group(1)

    # Step 2: 获取文章列表
    api_url = (
        f"https://mp.weixin.qq.com/mp/profile_ext"
        f"?action=getmsg&__biz={biz}&f=json&offset=0&count={count}"
        f"&is_ok=1&scene=124&uin=777&key=777&pass_ticket=&wxtoken="
        f"&appmsg_token={appmsg_token}&x5=0"
    )
    req2 = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(req2, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8', errors='ignore'))

    if data.get('ret') != 0:
        raise RuntimeError(f"API ret={data.get('ret')}, msg={data.get('msg')}")

    msg_list = json.loads(data.get('general_msg_list', '{}')).get('list', [])
    return msg_list


def parse_wx_articles(msg_list, account):
    """解析微信消息列表 → voice 格式"""
    results = []
    for msg in msg_list:
        comm = msg.get('comm_msg_info', {})
        app = msg.get('app_msg_ext_info', {})
        if not app:
            continue
        title = app.get('title', '').strip()
        if not title:
            continue
        digest = app.get('digest', '').strip()
        link = app.get('content_url', '').replace('\\/', '/')
        ts = comm.get('datetime', 0)
        time_str = datetime.fromtimestamp(ts, CST).strftime('%H:%M') if ts else ''

        results.append({
            'source': account['name'],
            'title': title,
            'link': link,
            'digest': digest[:150] if digest else title[:80],
            'time': time_str,
            'color': account['color'],
            'text_color': account['text_color'],
            '_ts': ts,
        })
        # 子文章
        for sub in app.get('multi_app_msg_item_list', []):
            st = sub.get('title', '').strip()
            sl = sub.get('content_url', '').replace('\\/', '/')
            sd = sub.get('digest', '').strip()
            if st and sl:
                results.append({
                    'source': account['name'],
                    'title': st,
                    'link': sl,
                    'digest': sd[:150] if sd else st[:80],
                    'time': time_str,
                    'color': account['color'],
                    'text_color': account['text_color'],
                    '_ts': ts,
                })
    return results


def get_voice():
    """抓取全部微信公众号，返回按时间倒序的 voice 列表"""
    print("── 微信公众号（投资·行业声音）──")
    token, cookie = load_wx_cookie()
    if not cookie:
        print("  ⚠️  无 WX_COOKIE，跳过微信抓取")
        return []

    all_articles = []
    for acc in ACCOUNTS:
        try:
            msgs = fetch_wx_articles(acc['biz'], cookie, count=3)
            arts = parse_wx_articles(msgs, acc)
            # 只取最新1篇
            arts.sort(key=lambda x: x.get('_ts', 0), reverse=True)
            if arts:
                all_articles.append(arts[0])
            print(f"  ✅ {acc['name']}: {len(arts)} 篇，取最新1篇")
        except Exception as e:
            print(f"  ⚠️  {acc['name']} 失败: {e}")

    # 全部按时间倒序
    all_articles.sort(key=lambda x: x.get('_ts', 0), reverse=True)
    # 移除内部字段
    for a in all_articles:
        a.pop('_ts', None)

    print(f"  共 {len(all_articles)} 条")
    return all_articles


# ══════════════════════════════════════════════════════════════════════════════
# 模块 2：财联社（投资·行业资讯）
# ══════════════════════════════════════════════════════════════════════════════

def classify_item(text):
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in text for kw in keywords):
            return cat
    return "综合"


def fetch_cls_news(limit=15):
    """抓取财联社电报，返回 news 格式列表"""
    print("── 财联社（投资·行业资讯）──")
    import urllib.request

    # 优先：直连财联社解析 __NEXT_DATA__
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.cls.cn/",
        }
        req = urllib.request.Request("https://www.cls.cn/telegraph", headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if m:
            next_data = json.loads(m.group(1))
            tele_list = (next_data.get('props', {}).get('initialState', {})
                         .get('telegraph', {}).get('telegraphList', []))
            if tele_list:
                print(f"  ✅ 直连财联社成功，{len(tele_list)} 条原始数据")
                items = _parse_cls_json(tele_list, limit)
                print(f"  筛选后 {len(items)} 条")
                return items
    except Exception as e:
        print(f"  ⚠️  直连失败({e})，改用 Jina 代理")

    # 备用：Jina
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30", "https://r.jina.ai/https://www.cls.cn/telegraph"],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode == 0 and result.stdout.strip():
            items = _parse_cls_markdown(result.stdout, limit)
            print(f"  ✅ Jina 代理成功，{len(items)} 条")
            return items
    except Exception as e:
        print(f"  ⚠️  Jina 代理失败: {e}")

    print("  ⚠️  财联社全部方式失败，返回空")
    return []


def _parse_cls_json(tele_list, limit=15):
    items = []
    for item in tele_list:
        content = item.get('content', '').strip()
        title_raw = item.get('title', '').strip()
        ctime = item.get('ctime', 0)
        level = item.get('level', 'C')
        reading = item.get('reading_num', 0)
        sharing = item.get('share_num', 0)

        if not content or len(content) < 10:
            continue

        if title_raw:
            title = title_raw[:60]
            body = re.sub(r'^【[^】]+】', '', content).strip()
            body = re.sub(r'^财联社\d+月\d+日电，?', '', body).strip()
        else:
            m = re.match(r'【([^】]+)】(.*)', content, re.DOTALL)
            if m:
                title, body = m.group(1)[:60], m.group(2).strip()
                body = re.sub(r'^财联社\d+月\d+日电，?', '', body).strip()
            else:
                clean = re.sub(r'^财联社\d+月\d+日电，?', '', content).strip()
                title = clean[:38] + ('…' if len(clean) > 38 else '')
                body = clean

        time_str = datetime.fromtimestamp(ctime, CST).strftime('%H:%M') if ctime else datetime.now(CST).strftime('%H:%M')
        importance = reading + sharing * 5 + (5000 if level == 'A' else 1000 if level == 'B' else 0)

        items.append({
            'title': title,
            'body': body[:150] if body else '',
            'time': time_str,
            'source': '财联社',
            'tag': classify_item(title + ' ' + content),
            '_importance': importance,
        })

    # 按重要性排序，取 top N
    items.sort(key=lambda x: x['_importance'], reverse=True)
    items = items[:limit]
    # 按时间顺序还原
    items.sort(key=lambda x: x['time'])
    for it in items:
        it.pop('_importance', None)
    return items


def _parse_cls_markdown(content, limit=15):
    items = []
    lines = content.split('\n')
    i = 0
    while i < len(lines) and len(items) < limit:
        line = lines[i].strip()
        tm = re.match(r'^(\d{2}:\d{2})(?::\d{2})?$', line)
        if tm:
            time_str = tm.group(1)
            i += 1
            parts = []
            while i < len(lines):
                nl = lines[i].strip()
                if re.match(r'^\d{2}:\d{2}', nl):
                    break
                if re.match(r'^阅$', nl) or re.match(r'^\d+\.\d+[WwKk万千]$', nl):
                    i += 1
                    continue
                if nl:
                    parts.append(nl)
                i += 1
            text = ' '.join(parts).strip()
            if len(text) < 10:
                continue
            m = re.match(r'【([^】]+)】(.*)', text, re.DOTALL)
            if m:
                title, body = m.group(1)[:60], m.group(2).strip()
            else:
                clean = text.strip()
                title = clean[:38] + ('…' if len(clean) > 38 else '')
                body = clean
            items.append({
                'title': title,
                'body': body[:150],
                'time': time_str,
                'source': '财联社',
                'tag': classify_item(text),
            })
        else:
            i += 1
    return items


# ══════════════════════════════════════════════════════════════════════════════
# 模块 2B：微博（刘煜辉）
# ══════════════════════════════════════════════════════════════════════════════

def get_weibo_voice():
    """抓取刘煜辉微博最新3条，返回 voice 格式列表"""
    print("── 微博（刘煜辉）──")
    sub = os.environ.get('WEIBO_SUB', '').strip()
    subp = os.environ.get('WEIBO_SUBP', '').strip()

    # fallback 到本地文件
    if not sub:
        cookie_file = os.path.expanduser('~/.openclaw/weibo/cookies.env')
        if os.path.exists(cookie_file):
            with open(cookie_file, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip()
                    if k == 'WEIBO_SUB':
                        sub = v
                    elif k == 'WEIBO_SUBP':
                        subp = v

    if not sub:
        print("  ⚠️  无 WEIBO_SUB，跳过微博抓取")
        return []

    import urllib.request
    uid = '2337530130'
    url = (f'https://m.weibo.cn/api/container/getIndex'
           f'?type=uid&value={uid}&containerid=107603{uid}')
    headers = {
        'User-Agent': ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'
                       ' AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
                       ' MicroMessenger/8.0.44 WeChat/iPhone'),
        'Cookie': f'SUB={sub}; SUBP={subp}',
        'Referer': f'https://m.weibo.cn/u/{uid}',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  ⚠️  微博请求失败: {e}")
        return []

    cards = data.get('data', {}).get('cards', [])
    results = []
    now = datetime.now(CST)

    for card in cards:
        mblog = card.get('mblog', {})
        if not mblog:
            continue
        text_raw = mblog.get('text', '')
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text_raw).strip()
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) < 10:
            continue

        created = mblog.get('created_at', '')
        # 解析微博时间（格式如 "Thu Mar 26 12:34:56 +0800 2026"）
        try:
            from email.utils import parsedate
            import time as _time
            parsed = parsedate(created)
            if parsed:
                ts = _time.mktime(parsed)
                time_str = datetime.fromtimestamp(ts, CST).strftime('%H:%M')
            else:
                time_str = now.strftime('%H:%M')
        except Exception:
            time_str = now.strftime('%H:%M')

        title = text[:60] + ('…' if len(text) > 60 else '')
        body = text[:200]
        link = f"https://weibo.com/{uid}/{mblog.get('bid', '')}"

        results.append({
            'source': '刘煜辉',
            'title': title,
            'digest': body,
            'link': link,
            'time': time_str,
            'color': 'rgba(198,40,40,.1)',
            'text_color': '#c62828',
        })
        if len(results) >= 3:
            break

    print(f"  ✅ 刘煜辉微博: {len(results)} 条")
    return results


# ══════════════════════════════════════════════════════════════════════════════
# 模块 3：AI 行业声音（量子位 + 机器之心 + arxiv cs.AI/cs.LG）
# ══════════════════════════════════════════════════════════════════════════════

def jina_fetch(url, timeout=30):
    """通过 Jina 代理抓取页面，返回 markdown 文本"""
    result = subprocess.run(
        ["curl", "-s", "--max-time", str(timeout), f"https://r.jina.ai/{url}"],
        capture_output=True, text=True, timeout=timeout + 5
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"jina 抓取失败: {result.stderr[:100]}")
    return result.stdout


def is_noise(title):
    if len(title) < 10:
        return True
    tl = title.lower()
    return any(kw in tl for kw in NOISE_KEYWORDS) or re.match(r'^(image\s+\d+|img\s*\d*)[:\s]', tl)


def _parse_links_generic(content, source, limit=10):
    """从 jina markdown 中提取 [title](url) 链接"""
    now = datetime.now(CST)
    news_list, seen = [], set()
    pattern = re.compile(r'\[([^\]]{10,300})\]\((https?://[^\)]{10,})\)')
    for title, url in pattern.findall(content):
        title = title.strip()
        if title in seen or is_noise(title):
            continue
        seen.add(title)
        news_list.append({
            'title': title[:200],
            'body': '',
            'time': now.strftime('%H:%M'),
            'source': source,
            'link': url,
        })
        if len(news_list) >= limit:
            break
    return news_list


def fetch_qbitai(limit=10):
    """量子位"""
    print("  [量子位] 抓取中...")
    try:
        content = jina_fetch("https://www.qbitai.com")
        news = _parse_links_generic(content, "量子位", limit)
        print(f"  [量子位] ✅ {len(news)} 条")
        return news
    except Exception as e:
        print(f"  [量子位] ⚠️  失败: {e}")
        return []


def fetch_jiqizhixin(limit=10):
    """机器之心"""
    print("  [机器之心] 抓取中...")
    try:
        content = jina_fetch("https://www.jiqizhixin.com")
        now = datetime.now(CST)
        news_list, seen = [], set()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if len(news_list) >= limit:
                break
            line = line.strip()
            if not line or is_noise(line) or line.startswith(('#', '!', 'URL', 'Markdown', 'Title:')):
                continue
            # 下一非空行
            next_ne = ''
            for j in range(i + 1, min(i + 4, len(lines))):
                c = lines[j].strip()
                if c:
                    next_ne = c
                    break
            is_article = (
                next_ne in ('今天', '昨天') or
                re.match(r'^\d{4}[-/]\d{2}[-/]\d{2}', next_ne) or
                re.match(r'^\d{1,2}月\d{1,2}日', next_ne)
            )
            if is_article and line not in seen and len(line) >= 10:
                seen.add(line)
                news_list.append({
                    'title': line[:200],
                    'body': '',
                    'time': now.strftime('%H:%M'),
                    'source': '机器之心',
                    'link': 'https://www.jiqizhixin.com',
                })
        if not news_list:
            news_list = _parse_links_generic(content, "机器之心", limit)
        print(f"  [机器之心] ✅ {len(news_list)} 条")
        return news_list
    except Exception as e:
        print(f"  [机器之心] ⚠️  失败: {e}")
        return []


def fetch_arxiv(limit=5):
    """arxiv cs.AI + cs.LG 各取 limit 篇，合并去重"""
    print("  [arxiv] 抓取中...")
    now = datetime.now(CST)
    results, seen = [], set()

    for cat in ['cs.AI', 'cs.LG']:
        try:
            content = jina_fetch(f"https://arxiv.org/list/{cat}/recent", timeout=30)
            abs_pattern = re.compile(r'https://arxiv\.org/abs/(\d{4}\.\d{4,5})')
            abs_positions = [(m.start(), m.group(0)) for m in abs_pattern.finditer(content)]

            SKIP = {'artificial intelligence', 'cs.ai', 'cs.lg', 'recent',
                    'machine learning', 'authors and titles', 'quick links', 'new changes'}
            title_pattern = re.compile(r'Title:\s*([^\n]{10,300})', re.MULTILINE)
            count = 0
            for tm in title_pattern.finditer(content):
                if count >= limit:
                    break
                title = tm.group(1).strip()
                if title in seen or title.lower() in SKIP or len(title) < 10:
                    continue
                # 向前找最近的 abs URL
                best_url = f"https://arxiv.org/list/{cat}/recent"
                for pos, url in reversed(abs_positions):
                    if pos < tm.start():
                        best_url = url
                        break
                seen.add(title)
                results.append({
                    'title': title[:250],
                    'body': '',
                    'time': now.strftime('%H:%M'),
                    'source': f'arxiv {cat}',
                    'link': best_url,
                })
                count += 1
            print(f"  [arxiv {cat}] ✅ {count} 条")
        except Exception as e:
            print(f"  [arxiv {cat}] ⚠️  失败: {e}")

    return results


def get_ai_voice():
    """整合 AI 行业声音"""
    print("── AI·行业声音 ──")
    ai_voice = []
    ai_voice.extend(fetch_qbitai(limit=10))
    ai_voice.extend(fetch_jiqizhixin(limit=10))
    ai_voice.extend(fetch_arxiv(limit=5))
    print(f"  共 {len(ai_voice)} 条 AI 资讯")
    return ai_voice


# ══════════════════════════════════════════════════════════════════════════════
# 模块 4：喵子判断
# ══════════════════════════════════════════════════════════════════════════════

def generate_miao_notice(voice, news, ai_voice, now):
    """
    基于当日 voice / news / ai_voice 内容，模板生成喵子点评。
    风格：一针见血大白话，≤100字，≤2句，带喵子视角。
    不调 LLM，用标题关键词拼接。
    """

    # 抽取最有价值的标题：voice 优先（有时间戳），news 次之，ai_voice 补充
    top_titles = []
    if voice:
        top_titles.append(voice[0]['title'][:30])
    if news:
        top_titles.append(news[0]['title'][:30])
    if not top_titles and ai_voice:
        top_titles.append(ai_voice[0]['title'][:30])

    total = len(voice) + len(news) + len(ai_voice)
    date_str = now.strftime('%Y.%m.%d %H:%M')

    # 挑关键词触发不同模板
    all_text = ' '.join(top_titles)

    if any(kw in all_text for kw in ['特朗普', '关税', '制裁', '战争', '地缘']):
        template = f"地缘博弈又添新变量：{top_titles[0] if top_titles else ''}。喵子建议仓位别贪，留子弹等机会。"
    elif any(kw in all_text for kw in ['AI', '大模型', '芯片', '算力', 'GPU']):
        template = f"AI浪头还在：{top_titles[0] if top_titles else ''}。喵子提醒，技术叙事估值贵，耐心等回调。"
    elif any(kw in all_text for kw in ['美联储', '加息', '降息', '利率', '货币']):
        template = f"货币政策牵一发：{top_titles[0] if top_titles else ''}。喵子说，流动性才是行情的底色，盯紧它。"
    elif any(kw in all_text for kw in ['A股', '沪指', '涨停', '牛市', '反弹']):
        template = f"A股情绪来了：{top_titles[0] if top_titles else ''}。喵子建议情绪高峰别追，低位布局才是正解。"
    elif any(kw in all_text for kw in ['黄金', '原油', '大宗', '商品']):
        template = f"大宗市场有动静：{top_titles[0] if top_titles else ''}。喵子提示，避险情绪来了要跟，但别上杠杆。"
    elif total == 0:
        template = "今日数据抓取较少，喵子暂无特别判断。盘面平静，持股待涨。"
    else:
        if top_titles:
            template = f"今日焦点：{top_titles[0]}。共收录 {total} 条资讯，喵子提醒保持独立判断，不跟风。"
        else:
            template = f"今日共收录 {total} 条资讯，市场信息量正常。喵子建议按既定策略执行，勿因短期噪音频繁操作。"

    # 截断到 100 字
    content = template[:100]

    return {
        'content': content,
        'label': f'🐱 喵子告知 · {date_str}',
    }


# ══════════════════════════════════════════════════════════════════════════════
## 主程序
# ══════════════════════════════════════════════════════════════════════════════

def main():
    now = datetime.now(CST)
    date_str = now.strftime('%Y%m%d')
    print(f"{'='*60}")
    print(f"  quietview 全量抓取  {now.strftime('%Y.%m.%d %H:%M')} CST")
    print(f"{'='*60}")

    # 1. 微信公众号（投资·行业声音）
    voice = get_voice()

    # 1B. 微博（刘煜辉）补充进 voice
    voice.extend(get_weibo_voice())

    # 2. 财联社（投资·行业资讯）
    news = fetch_cls_news(limit=15)

    # 3. AI 行业声音
    ai_voice = get_ai_voice()

    # 4. 喵子判断
    print("── 喵子判断 ──")
    miao_notice = generate_miao_notice(voice, news, ai_voice, now)
    print(f"  ✅ {miao_notice['content'][:40]}…")

    # 5. 写入 JSON
    data = {
        'date': date_str,
        'generated_at': now.isoformat(),
        'voice': voice,
        'news': news,
        'ai_voice': ai_voice,
        'miao_notice': miao_notice,
    }

    os.makedirs('data', exist_ok=True)
    out_path = f'data/{date_str}.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  ✅ 写入 {out_path}")
    print(f"  voice    : {len(voice)} 条")
    print(f"  news     : {len(news)} 条")
    print(f"  ai_voice : {len(ai_voice)} 条")
    print(f"  miao_notice: {miao_notice['label']}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
