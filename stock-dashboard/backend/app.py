#!/usr/bin/env python3
"""
A股信息驾驶舱 - Flask后端
项目: opc-20260321-001
技术栈: Flask + akshare + 简单内存缓存
端口: 5001
"""

import time
import json
import logging
import threading
from datetime import datetime, date
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeout

import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

import akshare as ak

# ─────────────────────────────────────────
# 初始化
# ─────────────────────────────────────────
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# 股票池（固定）
# ─────────────────────────────────────────
STOCKS = {
    "电力设备": [
        {"symbol": "603308", "name": "应流股份",  "market": "SH"},
        {"symbol": "000400", "name": "许继电气",  "market": "SZ"},
        {"symbol": "603530", "name": "神马电力",  "market": "SH"},
        {"symbol": "600268", "name": "国电南自",  "market": "SH"},
        {"symbol": "600406", "name": "国电南瑞",  "market": "SH"},
        {"symbol": "601126", "name": "四方股份",  "market": "SH"},
        {"symbol": "688676", "name": "金盘科技",  "market": "SH"},
        {"symbol": "002028", "name": "思源电气",  "market": "SZ"},
        {"symbol": "002885", "name": "京泉华",    "market": "SZ"},
        {"symbol": "600089", "name": "特变电工",  "market": "SH"},
        {"symbol": "603191", "name": "望变电气",  "market": "SH"},
        {"symbol": "301130", "name": "新特电气",  "market": "SZ"},
    ],
    "固态电池": [
        {"symbol": "688005", "name": "容百科技",  "market": "SH"},
        {"symbol": "002074", "name": "国轩高科",  "market": "SZ"},
        {"symbol": "688170", "name": "德龙激光",  "market": "SH"},
        {"symbol": "920522", "name": "纳科诺尔",  "market": "BJ"},  # 北交所
        {"symbol": "301662", "name": "宏工科技",  "market": "SZ"},
        {"symbol": "603200", "name": "上海洗霸",  "market": "SH"},
        {"symbol": "300450", "name": "先导智能",  "market": "SZ"},
        {"symbol": "688499", "name": "利元亨",    "market": "SH"},
    ],
}

# 所有股票列表（扁平化）
ALL_STOCKS = []
for group, stocks in STOCKS.items():
    for s in stocks:
        ALL_STOCKS.append({**s, "group": group})

# XQ symbol映射 (e.g. 603308 -> SH603308)
def xq_symbol(s: dict) -> str:
    m = s["market"]
    if m == "BJ":
        return f"BJ{s['symbol']}"
    return f"{m}{s['symbol']}"

# ─────────────────────────────────────────
# 内存缓存
# ─────────────────────────────────────────
_cache = {}
_cache_lock = threading.Lock()


def cache_get(key):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() < entry["expires"]:
            return entry["data"]
    return None


def cache_set(key, data, ttl):
    with _cache_lock:
        _cache[key] = {"data": data, "expires": time.time() + ttl}


def cached(ttl_seconds):
    """装饰器：对函数结果做TTL缓存，key = 函数名+args+kwargs"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = f"{fn.__name__}:{args}:{sorted(kwargs.items())}"
            cached_val = cache_get(key)
            if cached_val is not None:
                return cached_val
            result = fn(*args, **kwargs)
            cache_set(key, result, ttl_seconds)
            return result
        return wrapper
    return decorator


# ─────────────────────────────────────────
# 统一响应格式
# ─────────────────────────────────────────
def ok(data):
    return jsonify({
        "success": True,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })


def err(msg, code=500):
    return jsonify({
        "success": False,
        "error": str(msg),
        "timestamp": datetime.now().isoformat()
    }), code


# ─────────────────────────────────────────
# 数据获取层（带缓存）
# ─────────────────────────────────────────

@cached(ttl_seconds=60)
def fetch_spot(xq_sym: str) -> dict:
    """获取单只股票/指数实时行情（雪球）"""
    df = ak.stock_individual_spot_xq(symbol=xq_sym)
    row = dict(zip(df["item"], df["value"]))
    return row


# 保留别名，兼容旧引用
fetch_index_spot = fetch_spot


def safe_float(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except (TypeError, ValueError):
        return default


def spot_to_quote(raw: dict, symbol: str, name: str) -> dict:
    """把雪球spot数据标准化"""
    return {
        "symbol":   symbol,
        "name":     name,
        "price":    safe_float(raw.get("现价")),
        "change":   safe_float(raw.get("涨跌")),
        "pct_chg":  safe_float(raw.get("涨幅")),
        "volume":   safe_float(raw.get("成交量")),
        "amount":   safe_float(raw.get("成交额")),
        "high":     safe_float(raw.get("最高")),
        "low":      safe_float(raw.get("最低")),
        "open":     safe_float(raw.get("今开")),
        "prev_close": safe_float(raw.get("昨收")),
        "time":     str(raw.get("时间", "")),
    }


@cached(ttl_seconds=300)   # 5分钟
def fetch_daily_kline(sina_symbol: str, count: int) -> list:
    """
    日K线：使用新浪分钟K线数据（stock_zh_a_minute），
    按日聚合得到日K，再计算技术指标。
    sina_symbol: sh603308 / sz000400
    """
    try:
        df = ak.stock_zh_a_minute(symbol=sina_symbol, period="60", adjust="")
    except Exception as e:
        logger.warning(f"fetch_daily_kline failed for {sina_symbol}: {e}")
        return []

    if df.empty:
        return []

    df["day"] = pd.to_datetime(df["day"])
    df["date_only"] = df["day"].dt.date

    # 按日聚合
    agg = df.groupby("date_only").agg(
        open=("open", "first"),
        close=("close", "last"),
        high=("high", "max"),
        low=("low", "min"),
        volume=("volume", "sum"),
        amount=("amount", "sum"),
    ).reset_index().rename(columns={"date_only": "date"})
    agg = agg.sort_values("date").tail(count)

    # 计算技术指标
    close = agg["close"].astype(float)
    agg["ma5"]  = close.rolling(5,  min_periods=1).mean().round(4)
    agg["ma10"] = close.rolling(10, min_periods=1).mean().round(4)
    agg["ma20"] = close.rolling(20, min_periods=1).mean().round(4)

    # BOLL（20日，2倍标准差）
    boll_mid = close.rolling(20, min_periods=1).mean()
    boll_std = close.rolling(20, min_periods=1).std(ddof=0).fillna(0)
    agg["boll_upper"] = (boll_mid + 2 * boll_std).round(4)
    agg["boll_mid"]   = boll_mid.round(4)
    agg["boll_lower"] = (boll_mid - 2 * boll_std).round(4)

    agg["date"] = agg["date"].astype(str)
    return agg.to_dict(orient="records")


@cached(ttl_seconds=300)   # 5分钟
def fetch_minute_kline(sina_symbol: str) -> list:
    """分钟K线（最近一个交易日，5分钟），新浪数据源"""
    try:
        df = ak.stock_zh_a_minute(symbol=sina_symbol, period="5", adjust="")
    except Exception as e:
        logger.warning(f"fetch_minute_kline failed for {sina_symbol}: {e}")
        return []

    if df.empty:
        return []

    df["day"] = pd.to_datetime(df["day"])
    last_day = df["day"].dt.date.max()
    df = df[df["day"].dt.date == last_day].copy()

    close = df["close"].astype(float)
    df["ma5"]  = close.rolling(5,  min_periods=1).mean().round(4)
    df["ma10"] = close.rolling(10, min_periods=1).mean().round(4)
    df["ma20"] = close.rolling(20, min_periods=1).mean().round(4)

    boll_mid = close.rolling(20, min_periods=1).mean()
    boll_std = close.rolling(20, min_periods=1).std(ddof=0).fillna(0)
    df["boll_upper"] = (boll_mid + 2 * boll_std).round(4)
    df["boll_mid"]   = boll_mid.round(4)
    df["boll_lower"] = (boll_mid - 2 * boll_std).round(4)

    df = df.rename(columns={"day": "date"})
    df["date"] = df["date"].astype(str)
    cols = ["date", "open", "close", "high", "low", "volume",
            "ma5", "ma10", "ma20", "boll_upper", "boll_mid", "boll_lower"]
    return df[cols].to_dict(orient="records")


@cached(ttl_seconds=600)   # 10分钟
def fetch_news(symbol: str, limit: int) -> list:
    """个股新闻（东方财富）"""
    try:
        df = ak.stock_news_em(symbol=symbol)
    except Exception as e:
        logger.warning(f"fetch_news failed for {symbol}: {e}")
        return []

    if df.empty:
        return []

    results = []
    major_kw   = ["业绩预告", "重组", "停牌", "重大合同"]
    normal_kw  = ["研报", "评级"]

    for _, row in df.head(limit).iterrows():
        title = str(row.get("新闻标题", ""))
        level = "industry"
        for kw in major_kw:
            if kw in title:
                level = "major"
                break
        if level == "industry":
            for kw in normal_kw:
                if kw in title:
                    level = "normal"
                    break

        results.append({
            "title":  title,
            "source": str(row.get("文章来源", "")),
            "time":   str(row.get("发布时间", "")),
            "url":    str(row.get("新闻链接", "")),
            "level":  level,
        })
    return results


@cached(ttl_seconds=600)   # 10分钟
def fetch_announcements_for(symbol: str, stock_name: str, count: int = 5) -> list:
    """
    获取单只股票最近公告/重要新闻。
    主接口：巨潮资讯（cninfo）
    备用接口：东方财富新闻过滤（当cninfo超时时）
    """
    important_kw = ["重大", "停牌", "重组", "业绩预告", "分红", "增发", "配股", "回购",
                    "公告", "协议", "合同", "募资"]

    # 主接口：巨潮资讯
    try:
        today = date.today().strftime("%Y%m%d")
        year_ago = date(date.today().year - 1, date.today().month, date.today().day).strftime("%Y%m%d")
        import signal as _signal

        def _timeout(sig, frm):
            raise TimeoutError("cninfo timeout")
        _signal.signal(_signal.SIGALRM, _timeout)
        _signal.alarm(8)  # 8秒超时

        df = ak.stock_zh_a_disclosure_report_cninfo(
            symbol=symbol,
            start_date=year_ago,
            end_date=today
        )
        _signal.alarm(0)

        if not df.empty:
            results = []
            for _, row in df.head(count).iterrows():
                title = str(row.get("公告标题", ""))
                is_imp = any(kw in title for kw in important_kw)
                results.append({
                    "symbol":       symbol,
                    "name":         str(row.get("简称", stock_name)),
                    "title":        title,
                    "time":         str(row.get("公告时间", "")),
                    "url":          str(row.get("公告链接", "")),
                    "is_important": is_imp,
                    "source":       "cninfo",
                })
            return results

    except Exception as e:
        logger.warning(f"fetch_announcements_for cninfo {symbol}: {e}, 降级到新闻")

    # 备用接口：东方财富新闻
    try:
        df = ak.stock_news_em(symbol=symbol)
        if df.empty:
            return []
        results = []
        for _, row in df.head(count).iterrows():
            title = str(row.get("新闻标题", ""))
            is_imp = any(kw in title for kw in important_kw)
            results.append({
                "symbol":       symbol,
                "name":         stock_name,
                "title":        title,
                "time":         str(row.get("发布时间", "")),
                "url":          str(row.get("新闻链接", "")),
                "is_important": is_imp,
                "source":       "eastmoney_news",
            })
        return results
    except Exception as e:
        logger.warning(f"fetch_announcements_for news fallback {symbol}: {e}")
        return []


def sina_sym(s: dict) -> str:
    """转换为新浪格式 symbol：SH→sh, SZ→sz, BJ→bj"""
    return s["market"].lower() + s["symbol"]


# ─────────────────────────────────────────
# API 路由
# ─────────────────────────────────────────

def fetch_all_spots_parallel(stock_list: list, timeout: float = 8.0) -> dict:
    """并发获取多只股票行情，timeout秒内返回已完成结果"""
    results = {}

    def _fetch(s):
        try:
            raw = fetch_spot(xq_symbol(s))
            return s["symbol"], raw
        except Exception as e:
            logger.warning(f"spot parallel fail {s['symbol']}: {e}")
            return s["symbol"], None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_fetch, s): s for s in stock_list}
        for future in as_completed(futures, timeout=timeout):
            try:
                sym, raw = future.result()
                results[sym] = raw
            except Exception:
                pass

    return results


@app.route("/api/market", methods=["GET"])
def api_market():
    """
    大盘数据：
    - 上证指数、科创50 实时行情
    - 全市场涨跌家数（用自选股统计近似全市场，真实全市场需东方财富接口）
    - 电力设备/固态电池板块平均涨跌幅
    并发拉取所有行情，控制在 3 秒内
    """
    try:
        # 并发拉取指数 + 所有自选股
        index_stocks = [
            {"symbol": "000001", "name": "上证指数", "market": "SH", "group": "_index"},
            {"symbol": "000688", "name": "科创50",   "market": "SH", "group": "_index"},
        ]
        all_to_fetch = index_stocks + ALL_STOCKS
        spot_map = fetch_all_spots_parallel(all_to_fetch, timeout=8.0)

        def index_item(sym, code, name):
            raw = spot_map.get(sym, {}) or {}
            return {
                "code":    code,
                "name":    name,
                "price":   safe_float(raw.get("现价")),
                "change":  safe_float(raw.get("涨跌")),
                "pct_chg": safe_float(raw.get("涨幅")),
            }

        indices = [
            index_item("000001", "000001.SH", "上证指数"),
            index_item("000688", "000688.SH", "科创50"),
        ]

        # 统计涨跌家数 & 板块涨跌幅
        up_count = 0
        down_count = 0
        flat_count = 0
        group_pct = {"电力设备": [], "固态电池": []}

        for s in ALL_STOCKS:
            raw = spot_map.get(s["symbol"])
            if not raw:
                continue
            pct = safe_float(raw.get("涨幅"))
            if pct > 0:
                up_count += 1
            elif pct < 0:
                down_count += 1
            else:
                flat_count += 1
            group_pct[s["group"]].append(pct)

        sectors = {}
        for grp, pcts in group_pct.items():
            avg = round(sum(pcts) / len(pcts), 4) if pcts else 0.0
            sectors[grp] = {"pct_chg": avg, "stock_count": len(pcts)}

        data = {
            "indices":      indices,
            "market_stats": {
                "up":   up_count,
                "down": down_count,
                "flat": flat_count,
                "note": "基于自选股统计（共20只）",
            },
            "sectors": sectors,
        }
        return ok(data)

    except Exception as e:
        logger.exception("api_market error")
        return err(str(e))


@app.route("/api/stocks", methods=["GET"])
def api_stocks():
    """所有自选股实时行情，按板块分组，并发获取"""
    try:
        spot_map = fetch_all_spots_parallel(ALL_STOCKS, timeout=8.0)

        result = {}
        for group, stocks in STOCKS.items():
            group_data = []
            for s in stocks:
                raw = spot_map.get(s["symbol"])
                if raw:
                    q = spot_to_quote(raw, s["symbol"], s["name"])
                    q["group"] = group
                    group_data.append(q)
                else:
                    group_data.append({
                        "symbol":  s["symbol"],
                        "name":    s["name"],
                        "group":   group,
                        "error":   "fetch failed",
                        "price":   None,
                        "pct_chg": None,
                    })
            result[group] = group_data

        return ok(result)

    except Exception as e:
        logger.exception("api_stocks error")
        return err(str(e))


@app.route("/api/kline", methods=["GET"])
def api_kline():
    """
    K线数据
    ?symbol=603308&period=daily|minute&count=60
    """
    symbol = request.args.get("symbol", "603308").strip()
    period = request.args.get("period", "daily").strip().lower()
    count  = int(request.args.get("count", 60))

    # 找对应市场
    stock_info = next((s for s in ALL_STOCKS if s["symbol"] == symbol), None)
    if not stock_info:
        # 不在股票池里也尝试：默认SH
        stock_info = {"symbol": symbol, "name": symbol, "market": "SH", "group": "unknown"}

    sina = sina_sym(stock_info)

    try:
        if period == "minute":
            data = fetch_minute_kline(sina)
        else:
            data = fetch_daily_kline(sina, count)

        return ok({
            "symbol": symbol,
            "name":   stock_info.get("name", symbol),
            "period": period,
            "count":  len(data),
            "klines": data,
        })

    except Exception as e:
        logger.exception("api_kline error")
        return err(str(e))


@app.route("/api/news", methods=["GET"])
def api_news():
    """
    个股新闻
    ?symbol=603308&limit=20
    """
    symbol = request.args.get("symbol", "603308").strip()
    limit  = min(int(request.args.get("limit", 20)), 50)

    try:
        news = fetch_news(symbol, limit)
        return ok({
            "symbol": symbol,
            "count":  len(news),
            "news":   news,
        })
    except Exception as e:
        logger.exception("api_news error")
        return err(str(e))


@app.route("/api/announcements", methods=["GET"])
def api_announcements():
    """
    所有自选股公告走马灯（每股最近5条）
    并发拉取，做10分钟缓存，首次请求较慢（约15-30秒）
    """
    try:
        all_ann = []
        errors = []

        def _fetch_ann(s):
            return fetch_announcements_for(s["symbol"], s["name"], count=5)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(_fetch_ann, s): s for s in ALL_STOCKS}
            for future in as_completed(futures, timeout=60):
                s = futures[future]
                try:
                    ann = future.result()
                    all_ann.extend(ann)
                except Exception as e:
                    errors.append({"symbol": s["symbol"], "error": str(e)})

        # 按时间倒序
        all_ann.sort(key=lambda x: x.get("time", ""), reverse=True)

        resp = {
            "count":         len(all_ann),
            "announcements": all_ann,
        }
        if errors:
            resp["errors"] = errors

        return ok(resp)

    except Exception as e:
        logger.exception("api_announcements error")
        return err(str(e))


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


# ─────────────────────────────────────────
# 后台缓存预热
# ─────────────────────────────────────────

def warmup_cache():
    """启动后台预热：并发拉取所有行情，填充缓存"""
    logger.info("开始预热缓存...")
    index_stocks = [
        {"symbol": "000001", "name": "上证指数", "market": "SH", "group": "_index"},
        {"symbol": "000688", "name": "科创50",   "market": "SH", "group": "_index"},
    ]
    all_to_fetch = index_stocks + ALL_STOCKS
    try:
        spot_map = fetch_all_spots_parallel(all_to_fetch, timeout=30.0)
        logger.info(f"缓存预热完成: {len(spot_map)}/{len(all_to_fetch)} 只")
    except Exception as e:
        logger.warning(f"缓存预热失败: {e}")


# ─────────────────────────────────────────
# 启动
# ─────────────────────────────────────────
if __name__ == "__main__":
    logger.info("A股信息驾驶舱后端启动，端口 5001")
    logger.info(f"股票池: {len(ALL_STOCKS)} 只")

    # 后台线程预热缓存（不阻塞主线程启动）
    warmup_thread = threading.Thread(target=warmup_cache, daemon=True)
    warmup_thread.start()

    app.run(host="0.0.0.0", port=5001, debug=False)
