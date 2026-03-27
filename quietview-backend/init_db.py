#!/usr/bin/env python3
"""
init_db.py - QuietView 数据库初始化脚本
首次部署或本地开发时执行：python init_db.py
"""

import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "content.db")


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # ---------- articles ----------
    # module: invest | ai | growth
    # sub_module: daily_brief | industry_voice | deep_read | miao | diary | thought ...
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            module      TEXT    NOT NULL,
            sub_module  TEXT    NOT NULL,
            title       TEXT    NOT NULL DEFAULT '',
            content     TEXT    NOT NULL DEFAULT '',
            source_url  TEXT             DEFAULT NULL,
            publish_time TEXT            DEFAULT NULL,   -- ISO8601 or YYYY-MM-DD
            is_public   INTEGER NOT NULL DEFAULT 1,      -- 0=private 1=public
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_module
        ON articles (module, sub_module, publish_time DESC)
    """)

    # ---------- market_data ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    NOT NULL UNIQUE,   -- e.g. sh000001
            name        TEXT    NOT NULL,          -- e.g. 上证指数
            data_json   TEXT    NOT NULL DEFAULT '{}',
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_market_code
        ON market_data (code)
    """)

    # ---------- daily_brief ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_brief (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            brief_type  TEXT    NOT NULL,          -- e.g. invest | ai | growth
            content     TEXT    NOT NULL DEFAULT '',
            brief_date  TEXT    NOT NULL,          -- YYYY-MM-DD
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            UNIQUE (brief_type, brief_date)        -- 每天每类型只保留一份
        )
    """)

    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_brief_date
        ON daily_brief (brief_date DESC, brief_type)
    """)

    conn.commit()
    conn.close()
    print(f"[init_db] 数据库初始化完成：{db_path}")


if __name__ == "__main__":
    init_db()
