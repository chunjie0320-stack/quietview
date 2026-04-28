#!/usr/bin/env python3
"""
用保存的Cookie抓取小红书搜索结果
支持返回帖子 URL（供后续深度抓取使用）

Usage:
  python3 xhs-fetch-with-cookie.py <keyword> [--max N]

Output:
  JSON array: [{title, author, likes, url}, ...]
"""
import json, sys, time, re, argparse
from playwright.sync_api import sync_playwright

COOKIE_FILE = '/root/.openclaw/xiaohongshu-cookies.json'

def load_cookies():
    with open(COOKIE_FILE) as f:
        return json.load(f)

def parse_args():
    parser = argparse.ArgumentParser(description="小红书搜索抓取")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument("--max", type=int, default=8, help="最大结果数（默认8）")
    return parser.parse_args()

def search_xhs(keyword, max_results=8):
    cookies_data = load_cookies()
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # 注入cookie
        context.add_cookies([
            {'name': 'a1', 'value': cookies_data['a1'], 'domain': '.xiaohongshu.com', 'path': '/'},
            {'name': 'web_session', 'value': cookies_data['web_session'], 'domain': '.xiaohongshu.com', 'path': '/'},
        ])
        
        page = context.new_page()
        
        try:
            url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51'
            print(f"[搜索] {keyword}", file=sys.stderr)
            page.goto(url, timeout=30000, wait_until='networkidle')
            time.sleep(3)
            
            # 检查是否需要登录
            if '登录' in page.title() or page.url.startswith('https://www.xiaohongshu.com/login'):
                print(f"[错误] Cookie已过期，需要重新获取", file=sys.stderr)
                return []
            
            # 抓取笔记卡片（同时获取 URL）
            cards = page.query_selector_all('section.note-item, .search-result-item, [class*="note-item"]')
            print(f"[找到] {len(cards)} 个卡片", file=sys.stderr)
            
            for card in cards[:max_results]:
                try:
                    # 标题
                    title_el = card.query_selector('a.title span, .title, [class*="title"]')
                    title = title_el.inner_text().strip() if title_el else ''
                    
                    # 作者
                    author_el = card.query_selector('.author, [class*="author"] span, .name')
                    author = author_el.inner_text().strip() if author_el else ''
                    
                    # 点赞数
                    like_el = card.query_selector('.like-wrapper span, [class*="like"] span, .count')
                    likes = like_el.inner_text().strip() if like_el else ''
                    
                    # ★ 新增：帖子 URL
                    note_url = ''
                    # 方式1：找 a[href*="/explore/"] 或 a[href*="/discovery/item/"]
                    link_el = card.query_selector('a[href*="/explore/"], a[href*="/discovery/item/"]')
                    if link_el:
                        href = link_el.get_attribute('href') or ''
                        if href:
                            note_url = href if href.startswith('http') else f'https://www.xiaohongshu.com{href}'
                    # 方式2：从 card 自身的 data-id 构造
                    if not note_url:
                        note_id = card.get_attribute('data-id') or card.get_attribute('id') or ''
                        if note_id and re.match(r'^[0-9a-f]{24}$', note_id):
                            note_url = f'https://www.xiaohongshu.com/explore/{note_id}'
                    
                    if title:
                        results.append({
                            'title': title,
                            'author': author,
                            'likes': likes,
                            'url': note_url
                        })
                except Exception as e:
                    print(f"[warn] 解析卡片出错: {e}", file=sys.stderr)
                    pass
            
            # 如果上面没拿到，尝试更宽泛的选择器
            if not results:
                # 尝试从 a[href*="/explore/"] 直接找
                note_links = page.query_selector_all('a[href*="/explore/"]')
                for link in note_links[:max_results]:
                    href = link.get_attribute('href') or ''
                    note_url = href if href.startswith('http') else f'https://www.xiaohongshu.com{href}'
                    # 找标题（就在 a 元素内部）
                    title_span = link.query_selector('span')
                    title = title_span.inner_text().strip() if title_span else link.inner_text().strip()
                    if title and len(title) > 3:
                        results.append({'title': title, 'author': '', 'likes': '', 'url': note_url})
                        
        except Exception as e:
            print(f"[错误] {e}", file=sys.stderr)
        finally:
            browser.close()
    
    return results

if __name__ == '__main__':
    args = parse_args()
    results = search_xhs(args.keyword, args.max)
    print(json.dumps(results, ensure_ascii=False, indent=2))
