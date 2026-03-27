#!/usr/bin/env python3
"""
app.py - QuietView Flask 后端服务
quietview.me · 静静地观察自己，观察时间

部署：Railway (Procfile) 或本地 python app.py
环境变量：
    QUIETVIEW_API_KEY  写入接口鉴权 key（必须）
    DB_PATH            SQLite 路径，默认 content.db
    PORT               监听端口，默认 5000
    FLASK_ENV          development / production
"""

import os
import json
import sqlite3
import functools
from datetime import date, datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# ---------- 初始化 ----------

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_PATH = os.environ.get("DB_PATH", "content.db")
API_KEY  = os.environ.get("QUIETVIEW_API_KEY", "")


# ---------- 数据库工具 ----------

def get_db() -> sqlite3.Connection:
    """获取本次请求的 DB 连接（线程安全，用完自动关闭）"""
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        # WAL 模式：读写并发更友好
        db.execute("PRAGMA journal_mode=WAL")
    return db


@app.teardown_appcontext
def close_db(exc=None):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


def query(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    return get_db().execute(sql, params).fetchall()


def execute(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur


# ---------- 鉴权装饰器 ----------

def require_api_key(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not API_KEY:
            return jsonify({"error": "服务端未配置 QUIETVIEW_API_KEY"}), 500
        key = (
            request.headers.get("X-API-Key")
            or request.headers.get("Authorization", "").removeprefix("Bearer ")
        ).strip()
        if key != API_KEY:
            return jsonify({"error": "无效的 API Key"}), 401
        return f(*args, **kwargs)
    return wrapper


# ---------- 工具 ----------

def today_str() -> str:
    return date.today().isoformat()   # YYYY-MM-DD


def parse_date(val: str | None) -> str:
    """将 'today' 或 'YYYY-MM-DD' 统一转为 YYYY-MM-DD"""
    if not val or val.lower() == "today":
        return today_str()
    try:
        datetime.strptime(val, "%Y-%m-%d")
        return val
    except ValueError:
        return today_str()


def rows_to_list(rows) -> list[dict]:
    return [dict(r) for r in rows]


def ok(data, status: int = 200, **extra):
    payload = {"ok": True, "data": data}
    payload.update(extra)
    return jsonify(payload), status


def err(msg: str, code: int = 400) -> tuple:
    return jsonify({"ok": False, "error": msg}), code


# ---------- 确保数据库已初始化 ----------

def ensure_db():
    """应用启动时自动建表（避免每次部署前手动跑 init_db）"""
    from init_db import init_db
    init_db(DB_PATH)


# ==========================================================
#  API 路由
# ==========================================================


@app.get("/")
def index():
    return jsonify({"name": "quietview-api", "version": "1.0.0"})


# ----------------------------------------------------------
# GET /api/news?module=investment&date=today
# 返回指定模块当天的资讯列表（articles 表，sub_module=industry_voice 或其他）
# ----------------------------------------------------------

@app.get("/api/news")
def get_news():
    module = request.args.get("module", "invest")
    dt     = parse_date(request.args.get("date"))
    limit  = min(int(request.args.get("limit", 50)), 200)

    # 模块名归一化（前端可能传 investment，兼容处理）
    if module in ("investment", "invest"):
        module = "invest"

    rows = query(
        """
        SELECT id, module, sub_module, title, content, source_url,
               publish_time, is_public, created_at
        FROM articles
        WHERE module = ?
          AND is_public = 1
          AND (
              date(COALESCE(publish_time, created_at)) = ?
              OR publish_time LIKE ?
          )
        ORDER BY COALESCE(publish_time, created_at) DESC
        LIMIT ?
        """,
        (module, dt, f"{dt}%", limit),
    )
    return ok(rows_to_list(rows), date=dt, module=module, count=len(rows))


# ----------------------------------------------------------
# GET /api/market
# 返回全部行情数据（market_data 表）
# ----------------------------------------------------------

@app.get("/api/market")
def get_market():
    rows = query(
        "SELECT id, code, name, data_json, updated_at FROM market_data ORDER BY id"
    )
    result = []
    for r in rows:
        item = dict(r)
        try:
            item["data"] = json.loads(item.pop("data_json"))
        except (json.JSONDecodeError, TypeError):
            item["data"] = {}
        result.append(item)
    return ok(result)


# ----------------------------------------------------------
# GET /api/content?module=ai&sub=industry_voice
# 返回指定模块+子模块的内容列表（支持分页）
# ----------------------------------------------------------

@app.get("/api/content")
def get_content():
    module     = request.args.get("module", "")
    sub_module = request.args.get("sub", "")
    dt         = request.args.get("date")          # 可选，不传则不过滤日期
    page       = max(int(request.args.get("page", 1)), 1)
    page_size  = min(int(request.args.get("size", 20)), 100)
    offset     = (page - 1) * page_size

    sql_filters = ["is_public = 1"]
    params      = []

    if module:
        sql_filters.append("module = ?")
        params.append(module)
    if sub_module:
        sql_filters.append("sub_module = ?")
        params.append(sub_module)
    if dt:
        dt = parse_date(dt)
        sql_filters.append(
            "(date(COALESCE(publish_time, created_at)) = ? OR publish_time LIKE ?)"
        )
        params.extend([dt, f"{dt}%"])

    where = " AND ".join(sql_filters)
    count_row = query(f"SELECT COUNT(*) AS cnt FROM articles WHERE {where}", tuple(params))
    total = count_row[0]["cnt"] if count_row else 0

    params.extend([page_size, offset])
    rows = query(
        f"""
        SELECT id, module, sub_module, title, content, source_url,
               publish_time, is_public, created_at
        FROM articles
        WHERE {where}
        ORDER BY COALESCE(publish_time, created_at) DESC
        LIMIT ? OFFSET ?
        """,
        tuple(params),
    )
    return ok(
        rows_to_list(rows),
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size if total else 0,
    )


# ----------------------------------------------------------
# GET /api/diary?date=today
# 返回日记/思考/喵子内容（module=growth，sub_module in diary|thought|miao）
# ----------------------------------------------------------

@app.get("/api/diary")
def get_diary():
    dt         = parse_date(request.args.get("date"))
    sub_filter = request.args.get("sub")   # 可选：diary | thought | miao

    sql_filters = [
        "module = 'growth'",
        "is_public = 1",
        "(date(COALESCE(publish_time, created_at)) = ? OR publish_time LIKE ?)",
    ]
    params = [dt, f"{dt}%"]

    if sub_filter:
        sql_filters.append("sub_module = ?")
        params.append(sub_filter)

    where = " AND ".join(sql_filters)
    rows = query(
        f"""
        SELECT id, module, sub_module, title, content, source_url,
               publish_time, is_public, created_at
        FROM articles
        WHERE {where}
        ORDER BY COALESCE(publish_time, created_at) ASC
        """,
        tuple(params),
    )
    return ok(rows_to_list(rows), date=dt)


# ----------------------------------------------------------
# GET /api/content/modules
# 返回各模块有内容的日期列表（用于侧边栏导航）
# ----------------------------------------------------------

@app.get("/api/content/modules")
def get_content_modules():
    """
    返回结构：
    {
      "invest": {
        "daily_brief": ["2026-03-25", "2026-03-24", ...],
        "industry_voice": [...]
      },
      "ai": { ... },
      ...
    }
    """
    rows = query(
        """
        SELECT module,
               sub_module,
               date(COALESCE(publish_time, created_at)) AS dt,
               COUNT(*) AS cnt
        FROM articles
        WHERE is_public = 1
        GROUP BY module, sub_module, dt
        ORDER BY dt DESC
        """
    )

    result: dict = {}
    for r in rows:
        m, s, dt = r["module"], r["sub_module"], r["dt"]
        result.setdefault(m, {}).setdefault(s, []).append(dt)

    return ok(result)


# ----------------------------------------------------------
# POST /api/content   (需 API_KEY)
# 写入新内容到 articles 表
# Body (JSON):
#   module, sub_module, title, content, source_url?, publish_time?, is_public?
# ----------------------------------------------------------

@app.post("/api/content")
@require_api_key
def post_content():
    body = request.get_json(silent=True) or {}

    module     = (body.get("module") or "").strip()
    sub_module = (body.get("sub_module") or "").strip()
    title      = (body.get("title") or "").strip()
    content    = (body.get("content") or "").strip()

    if not module:
        return err("module 不能为空")
    if not sub_module:
        return err("sub_module 不能为空")
    if not content:
        return err("content 不能为空")

    source_url   = body.get("source_url")
    publish_time = body.get("publish_time") or today_str()
    is_public    = int(body.get("is_public", 1))

    cur = execute(
        """
        INSERT INTO articles (module, sub_module, title, content,
                              source_url, publish_time, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (module, sub_module, title, content, source_url, publish_time, is_public),
    )
    return ok({"id": cur.lastrowid}, message="写入成功"), 201


# ----------------------------------------------------------
# POST /api/brief   (需 API_KEY)
# 写入每日简报（daily_brief 表，同类型同日期覆盖写）
# Body: { brief_type, content, brief_date? }
# ----------------------------------------------------------

@app.post("/api/brief")
@require_api_key
def post_brief():
    body = request.get_json(silent=True) or {}

    brief_type = (body.get("brief_type") or "").strip()
    content    = (body.get("content") or "").strip()
    brief_date = parse_date(body.get("brief_date"))

    if not brief_type:
        return err("brief_type 不能为空")
    if not content:
        return err("content 不能为空")

    # INSERT OR REPLACE：同类型同日期覆盖更新
    cur = execute(
        """
        INSERT INTO daily_brief (brief_type, content, brief_date)
        VALUES (?, ?, ?)
        ON CONFLICT(brief_type, brief_date)
        DO UPDATE SET content = excluded.content,
                      created_at = datetime('now', 'localtime')
        """,
        (brief_type, content, brief_date),
    )
    return ok({"id": cur.lastrowid, "date": brief_date}, message="简报已更新"), 201


# ----------------------------------------------------------
# GET /api/brief?date=today&type=invest
# 读取每日简报（给前端消费）
# ----------------------------------------------------------

@app.get("/api/brief")
def get_brief():
    dt         = parse_date(request.args.get("date"))
    brief_type = request.args.get("type")

    sql_filters = ["brief_date = ?"]
    params      = [dt]
    if brief_type:
        sql_filters.append("brief_type = ?")
        params.append(brief_type)

    rows = query(
        f"""
        SELECT id, brief_type, content, brief_date, created_at
        FROM daily_brief
        WHERE {" AND ".join(sql_filters)}
        ORDER BY brief_type
        """,
        tuple(params),
    )
    return ok(rows_to_list(rows), date=dt)


# ==========================================================
#  启动入口
# ==========================================================

if __name__ == "__main__":
    ensure_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
