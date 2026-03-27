# QuietView 后端服务

> quietview.me · 静静地观察自己，观察时间

Flask + SQLite 极简后端，部署于 Railway。

---

## 文件结构

```
quietview-backend/
├── app.py           # Flask 主应用（所有路由）
├── init_db.py       # 数据库初始化（建表）
├── market_sync.py   # 行情数据同步脚本（akshare）
├── requirements.txt # Python 依赖
├── Procfile         # Railway 部署配置
├── .env.example     # 环境变量示例
└── README.md        # 本文件
```

---

## 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量
export QUIETVIEW_API_KEY=my-secret-key
export FLASK_ENV=development

# 3. 初始化数据库
python init_db.py

# 4. 启动服务
python app.py
# 访问 http://localhost:5000
```

---

## Railway 部署

1. 将本目录推送到 GitHub repo
2. 在 Railway 新建项目，关联 repo
3. 在 **Variables** 面板添加：
   - `QUIETVIEW_API_KEY` = 你的随机密钥
   - `DB_PATH` = `/data/content.db`（挂载 Volume 后使用，否则默认 `content.db`）
4. 添加 **Volume**，挂载到 `/data`（SQLite 持久化必须）
5. Railway 会自动运行 `Procfile` 中的 `release` 命令初始化数据库

> ⚠️ Railway 的免费套餐无持久化 Volume，重启后数据会丢失。必须挂载 Volume 才能持久保存 SQLite。

---

## API 文档

### 认证

写入接口需在 Header 中传递：
```
X-API-Key: {QUIETVIEW_API_KEY}
# 或
Authorization: Bearer {QUIETVIEW_API_KEY}
```

---

### GET /api/news

返回指定模块当天（或指定日期）的资讯列表。

| 参数     | 类型   | 默认    | 说明                         |
|--------|------|-------|----------------------------|
| module | str  | invest | invest / ai / growth       |
| date   | str  | today | today 或 YYYY-MM-DD         |
| limit  | int  | 50    | 最多 200                    |

```json
{
  "ok": true,
  "data": [
    { "id": 1, "module": "invest", "sub_module": "industry_voice",
      "title": "...", "content": "...", "source_url": null,
      "publish_time": "2026-03-25", "is_public": 1, "created_at": "..." }
  ],
  "date": "2026-03-25",
  "module": "invest",
  "count": 1
}
```

---

### GET /api/market

返回全部行情数据（由 `market_sync.py` 写入）。

```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "code": "sh000001",
      "name": "上证指数",
      "data": {
        "latest": { "close": 3258.47, "change_pct": 0.82 },
        "history": [{ "date": "2026-03-25", "close": 3258.47, "open": 3240.0 }]
      },
      "updated_at": "2026-03-25 10:00:00"
    }
  ]
}
```

---

### GET /api/content

分页获取指定模块+子模块内容列表。

| 参数   | 说明                              |
|------|----------------------------------|
| module | invest / ai / growth            |
| sub  | industry_voice / deep_read / miao / diary / thought 等 |
| date | 可选，过滤日期                    |
| page | 页码，默认 1                      |
| size | 每页条数，默认 20，最大 100       |

---

### GET /api/diary

返回 growth 模块当天的日记/思考/喵子内容。

| 参数 | 说明                              |
|----|----------------------------------|
| date | today 或 YYYY-MM-DD             |
| sub | 可选：diary / thought / miao     |

---

### GET /api/content/modules

返回各模块各子模块有内容的日期列表，供侧边栏导航使用。

```json
{
  "ok": true,
  "data": {
    "invest": {
      "daily_brief": ["2026-03-25", "2026-03-24"],
      "industry_voice": ["2026-03-25"]
    },
    "ai": { "industry_voice": ["2026-03-25"] }
  }
}
```

---

### POST /api/content  🔒

写入新内容到 articles 表。

```json
// Request Body
{
  "module": "invest",
  "sub_module": "industry_voice",
  "title": "标题（可选）",
  "content": "正文内容",
  "source_url": "https://...",
  "publish_time": "2026-03-25",
  "is_public": 1
}

// Response 201
{ "ok": true, "data": { "id": 42 }, "message": "写入成功" }
```

---

### POST /api/brief  🔒

写入（或覆盖）每日简报。同类型同日期会直接更新，不重复插入。

```json
// Request Body
{
  "brief_type": "invest",
  "content": "今日要点：...",
  "brief_date": "2026-03-25"
}

// Response 201
{ "ok": true, "data": { "id": 1, "date": "2026-03-25" }, "message": "简报已更新" }
```

---

### GET /api/brief

读取每日简报。

| 参数   | 说明                   |
|------|----------------------|
| date | today 或 YYYY-MM-DD  |
| type | 可选：invest / ai / growth |

---

## 行情同步

手动执行：
```bash
python market_sync.py
```

Railway Cron（每 2 小时）：
```
0 */2 * * * cd /app && python market_sync.py
```
