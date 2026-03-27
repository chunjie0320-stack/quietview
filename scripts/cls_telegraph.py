#!/usr/bin/env python3
"""
财联社电报"加红"新闻抓取器
抓取 https://www.cls.cn/telegraph 中"加红"tab下的重要资讯
"""

import requests
import hashlib
import time
import json
import sys
import re
from datetime import datetime

class CLSTelegraph:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://www.cls.cn/telegraph',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.base_url = "https://www.cls.cn/nodeapi/telegraphList"

    def _sign(self, params_str):
        """生成API签名: SHA1 -> MD5"""
        sha1 = hashlib.sha1(params_str.encode('utf-8')).hexdigest()
        return hashlib.md5(sha1.encode('utf-8')).hexdigest()

    def fetch(self, last_time=None, rn=50):
        """
        获取电报新闻
        返回 roll_data 列表
        """
        if last_time is None:
            last_time = int(time.time())

        app = 'CailianpressWeb'
        os_val = 'web'
        sv = '7.7.5'

        params_str = f'app={app}&last_time={last_time}&os={os_val}&rn={rn}&sv={sv}'
        sign = self._sign(params_str)
        url = f'{self.base_url}?{params_str}&sign={sign}'

        resp = self.session.get(url, headers=self.headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if 'data' not in data or 'roll_data' not in data['data']:
            return []
        return data['data']['roll_data']

    def fetch_red(self, pages=3):
        """
        获取多页数据，筛选"加红"新闻 (level='A' 或 modified_level 等高优先级标记)
        """
        all_news = []
        last_time = None
        for i in range(pages):
            items = self.fetch(last_time=last_time)
            if not items:
                break
            all_news.extend(items)
            last_time = items[-1].get('ctime')
            if i < pages - 1:
                time.sleep(0.5)
        
        # 筛选加红：level='A' 表示重要(加红)
        red_news = [n for n in all_news if n.get('level') == 'A']
        return red_news

    @staticmethod
    def classify(news_item):
        """
        对新闻分类：行业进展 / 国际局势 / 国家政策 / 战争局势 / 美股走势
        返回分类列表（可多标签），如果是个股消息返回空列表（过滤掉）
        """
        title = news_item.get('title', '') or ''
        content = news_item.get('content', '') or ''
        text = title + content

        # 过滤个股消息
        stock_patterns = [
            r'涨停', r'跌停', r'[A-Z]{2,}\d{6}', r'个股', r'龙虎榜',
            r'大宗交易', r'股东减持', r'股东增持', r'限售股', r'解禁',
        ]
        # 不要过于激进地过滤，只过滤明显的个股消息
        
        categories = []
        
        # 行业进展
        industry_kw = ['行业', '产业', '芯片', '半导体', '新能源', '锂电', '光伏', '储能',
                       'AI', '人工智能', '大模型', '机器人', '自动驾驶', '医药', '生物',
                       '消费', '汽车', '地产', '房地产', '钢铁', '煤炭', '石油', '天然气',
                       '5G', '云计算', '量子', '航天', '航空', '军工', '农业', '食品',
                       '电商', '互联网', '金融科技', '区块链', '元宇宙', '算力', 'DeepSeek',
                       '供应链', '制造业', 'PMI', '出口', '进口', '贸易数据']
        if any(kw in text for kw in industry_kw):
            categories.append('行业进展')

        # 国际局势
        intl_kw = ['美国', '欧洲', '日本', '韩国', '东盟', '中东', '联合国', 
                   '关税', '制裁', '外交', '贸易战', '地缘', '北约', 'G7', 'G20',
                   '特朗普', '拜登', '普京', '泽连斯基', '马克龙', 'EU',
                   '国际', '全球', '外资', '出海']
        if any(kw in text for kw in intl_kw):
            categories.append('国际局势')

        # 国家政策
        policy_kw = ['国务院', '央行', '财政部', '发改委', '证监会', '银保监', '工信部',
                     '政策', '监管', 'LPR', '降准', '降息', '利率', '货币政策',
                     '财政', '税收', '减税', '补贴', '规划', '纲要', '十四五',
                     '两会', '政府工作报告', '中央经济', '常委会', '国常会',
                     '住建部', '交通部', '商务部', '科技部', '教育部', '自然资源']
        if any(kw in text for kw in policy_kw):
            categories.append('国家政策')

        # 战争局势
        war_kw = ['俄乌', '乌克兰', '俄罗斯', '战争', '军事', '导弹', '无人机',
                  '冲突', '停火', '战场', '以色列', '巴勒斯坦', '哈马斯', '黎巴嫩',
                  '真主党', '胡塞', '红海', '台海', '南海', '朝鲜', '核武']
        if any(kw in text for kw in war_kw):
            categories.append('战争局势')

        # 美股走势
        us_kw = ['美股', '纳斯达克', '道琼斯', '标普500', 'S&P', '美债', '美元',
                 '苹果', '谷歌', '微软', '英伟达', '特斯拉', '亚马逊', 'Meta',
                 '华尔街', '美联储', 'Fed', '鲍威尔', '非农', 'CPI', 'PCE',
                 '纳指', '道指', '标普', '美国国债', '10年期', '收益率']
        if any(kw in text for kw in us_kw):
            categories.append('美股走势')

        return categories if categories else None

    @staticmethod
    def format_time(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

    @staticmethod
    def format_date(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    def get_filtered_news(self, pages=5):
        """获取并过滤分类后的加红新闻"""
        red_news = self.fetch_red(pages=pages)
        result = []
        for item in red_news:
            cats = self.classify(item)
            if cats is None:
                continue  # 跳过无分类（可能是个股）
            result.append({
                'title': item.get('title', ''),
                'content': (item.get('content', '') or '').strip(),
                'time': self.format_time(item.get('ctime', 0)),
                'timestamp': item.get('ctime', 0),
                'categories': cats,
                'images': [img.get('url', '') for img in (item.get('images', []) or []) if img.get('url')],
                'subjects': self._parse_subjects(item.get('subjects', '')),
            })
        return result

    def _parse_subjects(self, subjects):
        if not subjects:
            return []
        if isinstance(subjects, list):
            return [s.get('subject_name', '') or s.get('name', '') for s in subjects if isinstance(s, dict)]
        if isinstance(subjects, str):
            try:
                parsed = json.loads(subjects)
                if isinstance(parsed, list):
                    return [s.get('subject_name', '') or s.get('name', '') for s in parsed if isinstance(s, dict)]
            except:
                pass
        return []


def main():
    """CLI入口"""
    import argparse
    parser = argparse.ArgumentParser(description='财联社电报加红新闻抓取')
    parser.add_argument('--pages', type=int, default=5, help='抓取页数')
    parser.add_argument('--json', action='store_true', help='输出JSON格式')
    args = parser.parse_args()

    cls = CLSTelegraph()
    news = cls.get_filtered_news(pages=args.pages)
    
    if args.json:
        print(json.dumps(news, ensure_ascii=False, indent=2))
    else:
        for item in news:
            cats = ' | '.join(item['categories'])
            print(f"[{item['time']}] [{cats}] {item['title'] or item['content'][:80]}")
            if item['images']:
                print(f"  📷 {len(item['images'])} 张图片")
            print()


if __name__ == '__main__':
    main()
