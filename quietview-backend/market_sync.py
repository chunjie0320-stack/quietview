#!/usr/bin/env python3
"""
market_sync.py - 行情数据同步脚本（akshare）
可通过 Railway Cron 或本地 crontab 定时执行：
    0 */2 * * * cd /app && python market_sync.py

支持的标的：
    - 上证指数  sh000001
    - 科创50    sh000688
    - VIX       （通过 akshare stock_us_fear_index 获取）
    - 纳斯达克  （可扩展）

执行后将最新数据写入 market_data 表。
"""

import os
import json
import sqlite3
import traceback
from datetime import datetime

try:
    import akshare as ak
except ImportError:
    ak = None

DB_PATH = os.environ.get("DB_PATH", "content.db")


def upsert_market(conn: sqlite3.Connection, code: str, name: str, data: dict):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """
        INSERT INTO market_data (code, name, data_json, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(code)
        DO UPDATE SET name=excluded.name,
                      data_json=excluded.data_json,
                      updated_at=excluded.updated_at
        """,
        (code, name, json.dumps(data, ensure_ascii=False), now),
    )


def fetch_a_index(symbol: str) -> dict:
    """获取 A 股指数日线数据（最近 90 天）"""
    df = ak.stock_zh_index_daily(symbol=symbol)
    df = df.tail(90)
    return {
        "latest": {
            "close": float(df["close"].iloc[-1]),
            "change_pct": round(
                (df["close"].iloc[-1] - df["close"].iloc[-2])
                / df["close"].iloc[-2]
                * 100,
                2,
            ),
        },
        "history": [
            {"date": str(r["date"]), "close": float(r["close"]), "open": float(r["open"])}
            for _, r in df.iterrows()
        ],
    }


def fetch_vix() -> dict:
    """获取 VIX 历史数据（最近 90 天）"""
    df = ak.stock_us_fear_index()
    df = df.tail(90)
    return {
        "latest": {"close": float(df["close"].iloc[-1])},
        "history": [
            {"date": str(r["date"]), "close": float(r["close"])}
            for _, r in df.iterrows()
        ],
    }


def sync():
    if ak is None:
        print("[market_sync] akshare 未安装，跳过同步")
        return

    conn = sqlite3.connect(DB_PATH)

    targets = [
        ("sh000001", "上证指数", fetch_a_index, "sh000001"),
        ("sh000688", "科创50",   fetch_a_index, "sh000688"),
        ("vix",      "VIX恐慌指数", fetch_vix,  None),
    ]

    for code, name, fetcher, arg in targets:
        try:
            data = fetcher(arg) if arg else fetcher()
            upsert_market(conn, code, name, data)
            print(f"[market_sync] ✓ {name} ({code})")
        except Exception:
            print(f"[market_sync] ✗ {name} ({code}) 同步失败：")
            traceback.print_exc()

    conn.commit()
    conn.close()
    print("[market_sync] 同步完成")


if __name__ == "__main__":
    sync()
