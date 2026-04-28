"""
foodsearch 后端服务
FastAPI + uvicorn，端口 8080
提供三个 AI 接口：/api/parse、/api/topics、/api/drill
静态文件服务：index.html、config.js
"""

import os
import re
import json
import asyncio
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ─────────────────────────────────────────
# 读取 Friday AppId
# ─────────────────────────────────────────
def get_friday_app_id() -> str:
    """优先读环境变量，其次从 config.js 提取"""
    env_val = os.environ.get("FRIDAY_APP_ID", "")
    if env_val:
        return env_val
    config_path = Path(__file__).parent / "config.js"
    if config_path.exists():
        text = config_path.read_text(encoding="utf-8")
        m = re.search(r"FRIDAY_APP_ID\s*:\s*['\"]([^'\"]+)['\"]", text)
        if m:
            return m.group(1)
    return ""


FRIDAY_API_URL = "https://aigc.sankuai.com/v1/openai/native/chat/completions"
FRIDAY_MODEL = "LongCat-Flash-Chat"

BASE_DIR = Path(__file__).parent

# Cookie 查找路径：优先项目内 cookies/xhs.json，其次沙箱全局路径
_COOKIE_CANDIDATES = [
    BASE_DIR / "cookies" / "xhs.json",
    Path.home() / ".openclaw" / "xiaohongshu-cookies.json",
]

def _find_cookie_file() -> Path | None:
    for p in _COOKIE_CANDIDATES:
        if p.exists():
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if d.get("a1") and d.get("web_session"):
                    return p
            except Exception:
                pass
    return None

COOKIE_FILE: Path | None = _find_cookie_file()

# ─────────────────────────────────────────
# xhs 是否可用
# ─────────────────────────────────────────
def has_xhs_cookie() -> bool:
    return _find_cookie_file() is not None


# ─────────────────────────────────────────
# xhs 抓取（playwright，超时 5s 降级）
# ─────────────────────────────────────────
async def fetch_xhs_titles(keyword: str, max_count: int = 5) -> list[str]:
    """用 playwright 抓取 xhs 搜索结果标题，失败返回空列表"""
    try:
        loop = asyncio.get_event_loop()
        titles = await asyncio.wait_for(
            loop.run_in_executor(None, _sync_fetch_xhs, keyword, max_count),
            timeout=5.0,
        )
        return titles
    except Exception as exc:
        print(f"[xhs] 抓取失败，降级：{exc}")
        return []


def _sync_fetch_xhs(keyword: str, max_count: int) -> list[str]:
    """
    同步 playwright 抓取（在线程池中执行）。
    逻辑完全复用 scripts/xhs-fetch-with-cookie.py（已验证可用）。
    """
    import time
    import re as _re
    from playwright.sync_api import sync_playwright

    cf = _find_cookie_file()
    if not cf:
        return []
    cookies_data = json.loads(cf.read_text(encoding="utf-8"))
    results: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        context.add_cookies([
            {"name": "a1",          "value": cookies_data["a1"],          "domain": ".xiaohongshu.com", "path": "/"},
            {"name": "web_session", "value": cookies_data["web_session"], "domain": ".xiaohongshu.com", "path": "/"},
        ])
        page = context.new_page()
        try:
            url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51"
            page.goto(url, timeout=30000, wait_until="networkidle")
            time.sleep(3)  # 同原脚本等 3 秒

            # 检查是否登录态失效（同原脚本）
            if "登录" in page.title() or page.url.startswith("https://www.xiaohongshu.com/login"):
                print("[xhs] Cookie 已过期", flush=True)
                return []

            # 主选择器（同原脚本）
            cards = page.query_selector_all(
                'section.note-item, .search-result-item, [class*="note-item"]'
            )
            print(f"[xhs] 找到 {len(cards)} 个卡片", flush=True)

            for card in cards[:max_count]:
                try:
                    title_el = card.query_selector('a.title span, .title, [class*="title"]')
                    title = title_el.inner_text().strip() if title_el else ""
                    if title:
                        results.append(title)
                except Exception:
                    pass

            # 备用选择器：从 a[href*="/explore/"] 取标题（同原脚本）
            if not results:
                note_links = page.query_selector_all('a[href*="/explore/"]')
                for link in note_links[:max_count]:
                    span = link.query_selector("span")
                    title = span.inner_text().strip() if span else link.inner_text().strip()
                    if title and len(title) > 3:
                        results.append(title)

        except Exception as e:
            print(f"[xhs-playwright] {e}", flush=True)
        finally:
            browser.close()

    return results


# ─────────────────────────────────────────
# Friday API 调用
# ─────────────────────────────────────────
async def call_friday(system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
    """调用 Friday LLM，返回模型回复文本"""
    app_id = get_friday_app_id()
    if not app_id:
        raise ValueError("FRIDAY_APP_ID 未配置，请修改 config.js 或设置环境变量")

    headers = {
        "Authorization": f"Bearer {app_id}",
        "Content-Type": "application/json",
    }
    body = {
        "model": FRIDAY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(FRIDAY_API_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        # 去掉可能的 markdown code block
        content = re.sub(r"^```[a-z]*\n?", "", content)
        content = re.sub(r"\n?```$", "", content).strip()
        return content


# ─────────────────────────────────────────
# FastAPI 应用
# ─────────────────────────────────────────
app = FastAPI(title="foodsearch")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── 静态文件：index.html / config.js ───
@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/config.js")
async def serve_config():
    return FileResponse(BASE_DIR / "config.js", media_type="application/javascript")


# ─── /api/parse ───
@app.post("/api/parse")
async def api_parse(request: Request):
    """AI 意图识别：地域/品类/人群/季节/目标/补充"""
    try:
        body = await request.json()
        text = body.get("text", "").strip()
        if not text:
            return JSONResponse({"error": "text 不能为空"}, status_code=400)

        system_prompt = (
            "你是一个美食热点分析助手。用户输入自然语言描述，你需要识别以下参数并严格以JSON格式返回（不要有任何多余文字）：\n"
            "- region: 地域，如\"北京\"\"上海\"\"全国\"，默认\"全国\"\n"
            "- goal: 目标类型，\"commercial\"=商业化会场/带货/运营，\"content\"=内容创作/选题/小红书。默认\"content\"\n"
            "- category: 品类方向，如\"火锅\"\"咖啡\"等，没提就返回\"美食（不限）\"\n"
            "- audience: 目标人群，如\"年轻女性\"\"家庭\"等，没提就返回\"不限\"\n"
            "- season: 季节/节气，如\"春季\"\"夏天\"\"清明\"等，没提就返回\"当前时节\"\n"
            "- extra: 其他补充意图（避坑/测评/探店/性价比/网红等），没有就返回\"无\"\n"
            "只返回JSON对象，不要任何解释和markdown代码块。"
        )

        content = await call_friday(system_prompt, text, max_tokens=300)
        result = json.loads(content)
        return JSONResponse(result)

    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"模型返回格式解析失败: {e}"}, status_code=500)
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            {"error": f"Friday API 调用失败: {e.response.status_code}"},
            status_code=502,
        )
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    except Exception as e:
        return JSONResponse({"error": f"服务异常: {str(e)}"}, status_code=500)


# ─── /api/topics ───
@app.post("/api/topics")
async def api_topics(request: Request):
    """生成气泡图话题数据（6-8 个品类）"""
    try:
        body = await request.json()
        region = body.get("region", "全国")
        category = body.get("category", "美食")
        season = body.get("season", "当前时节")
        goal = body.get("goal", "commercial")
        audience = body.get("audience", "不限")

        system_prompt = (
            "你是一个专业的美食内容运营专家和数据分析师。"
            "根据输入的条件，生成6-8个适合内容创作或商业化运营的美食热点品类。\n\n"
            "每个品类需包含以下字段：\n"
            "- name: 品类名称（简短，5字以内）\n"
            "- heat: 热度分值（1-100整数，根据当前真实热度判断）\n"
            "- x: 商业化潜力（0-1之间的小数，0=低，1=高）\n"
            "- y: 内容创作难度（0-1之间的小数，0=易，1=难）\n"
            "- tag: 标签类型，只能是以下之一：hot/rise/trend/niche/new\n"
            "- description: 一句话描述该品类的热点特征（20字以内）\n\n"
            "严格返回JSON数组，不要任何解释、markdown代码块或额外文字。\n"
            "示例格式：[{\"name\":\"烤鸭\",\"heat\":95,\"x\":0.85,\"y\":0.4,\"tag\":\"hot\",\"description\":\"北京最高热度，游客必打卡\"}]"
        )

        user_msg = (
            f"地域：{region}\n"
            f"品类方向：{category}\n"
            f"季节/时间：{season}\n"
            f"目标类型：{'商业化运营' if goal == 'commercial' else '内容创作'}\n"
            f"目标人群：{audience}\n\n"
            "请生成6-8个适合该场景的热门美食品类及其热度数据。"
        )

        # 如果有 xhs cookie，先尝试抓取相关数据（仅用于丰富语境，不强依赖）
        xhs_context = ""
        if has_xhs_cookie():
            try:
                keyword = f"{region} {category} 美食"
                titles = await fetch_xhs_titles(keyword, max_count=5)
                if titles:
                    xhs_context = "\n\n参考小红书实时热帖标题（供参考，不要直接使用）：\n" + "\n".join(
                        f"- {t}" for t in titles
                    )
            except Exception:
                pass

        content = await call_friday(system_prompt, user_msg + xhs_context, max_tokens=1500)
        topics = json.loads(content)

        # 数据校验与修正
        validated = []
        for item in topics:
            validated.append(
                {
                    "name": str(item.get("name", "未知品类"))[:10],
                    "heat": max(1, min(100, int(item.get("heat", 50)))),
                    "x": max(0.0, min(1.0, float(item.get("x", 0.5)))),
                    "y": max(0.0, min(1.0, float(item.get("y", 0.5)))),
                    "tag": item.get("tag", "trend") if item.get("tag") in ("hot", "rise", "trend", "niche", "new") else "trend",
                    "description": str(item.get("description", ""))[:50],
                }
            )

        return JSONResponse(validated)

    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"模型返回格式解析失败: {e}"}, status_code=500)
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            {"error": f"Friday API 调用失败: {e.response.status_code}"},
            status_code=502,
        )
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    except Exception as e:
        return JSONResponse({"error": f"服务异常: {str(e)}"}, status_code=500)


# ─── /api/drill ───
@app.post("/api/drill")
async def api_drill(request: Request):
    """品类下钻内容生成（小红书爆款风格）"""
    try:
        body = await request.json()
        category = body.get("category", "")
        region = body.get("region", "全国")
        goal = body.get("goal", "commercial")
        audience = body.get("audience", "不限")
        season = body.get("season", "当前时节")

        if not category:
            return JSONResponse({"error": "category 不能为空"}, status_code=400)

        # ── Step 1：先抓取真实 xhs 帖子标题（3-5条），作为风格参考 ──
        posts: list[str] = []
        if has_xhs_cookie():
            try:
                keyword = f"{region} {category}"
                posts = await fetch_xhs_titles(keyword, max_count=5)
            except Exception:
                pass

        # 真实标题拼入 user prompt 的风格参考段落
        xhs_style_hint = ""
        if posts:
            xhs_style_hint = (
                "\n\n以下是真实小红书热门帖子标题，请学习其语气和句式风格"
                "（不要复制原句，用于理解当前用户口味）：\n"
                + "\n".join(f"- {t}" for t in posts[:5])
            )

        # ── 小红书爆款 system prompt（两种 goal 共用） ──
        XHS_SYSTEM = (
            "你是一位资深小红书内容创作者，擅长美食探店类爆款内容。\n"
            "请根据提供的品类、城市、受众信息，生成小红书风格的内容。\n\n"
            "小红书爆款格式要求：\n"
            "- 标题：emoji开头 + 痛点/好奇/悬念 + 不超过25字，"
            "例如【🔥北京烤鸭踩雷指南 | 这3家坑死人不偿命】\n"
            "- 正文：口语化、分段短、emoji点缀（每段1-2个）、"
            "结尾加互动引导，例如【你们去过哪家？评论区告诉我！】\n"
            "- hashtags：8-12个，含品类词+城市词+场景词，"
            "例如[\"#北京美食\", \"#烤鸭推荐\", \"#探店打卡\"]\n"
            "- 篇幅：正文150-200字\n\n"
            "如果提供了真实小红书帖子标题作为参考，请学习其语气和句式，但不要复制原句。"
        )

        if goal == "commercial":
            system_prompt = (
                XHS_SYSTEM + "\n\n"
                "同时，你也是商业化内容策划专家，需要兼顾带货/转化目标。\n\n"
                "严格返回JSON对象，包含以下字段：\n"
                "- supply: 供给角度细分，数组，10条，每条是一个对象：\n"
                "  {name: 商家/SKU名称, tag: 核心标签, desc: 简介(30字), score: 评分如4.8}\n"
                "- prompt: 投放建议文案，字符串，100字以内\n"
                "- xhs_title: 小红书爆款标题，字符串，emoji开头不超过25字\n"
                "- xhs_body: 小红书正文，字符串，150-200字，口语化分段emoji点缀\n"
                "- xhs_tags: hashtag数组，8-12个\n\n"
                "不要任何解释和markdown代码块，直接返回JSON对象。"
            )
            user_msg = (
                f"品类：{category}\n"
                f"地域：{region}\n"
                f"目标人群：{audience}\n"
                f"季节：{season}\n"
                f"目标：商业化带货/转化"
                + xhs_style_hint
                + "\n\n请生成该品类的商业化供给内容、投放建议，以及一篇小红书爆款内容。"
            )
        else:
            system_prompt = (
                XHS_SYSTEM + "\n\n"
                "同时，你也是内容选题策划专家，擅长发现用户真实痛点和爆款选题方向。\n\n"
                "严格返回JSON对象，包含以下字段：\n"
                "- pain: 痛点洞察，数组，5条字符串，每条20字以内\n"
                "- topics: 选题建议，数组，10条字符串，小红书标题风格（emoji+悬念/痛点），每条25字以内\n"
                "- sample_post: 完整示例帖子，字符串，包含标题+正文+hashtags，正文150-200字\n"
                "- xhs_title: 最佳爆款标题（从topics中挑出最强一条），字符串\n"
                "- xhs_body: 对应正文，字符串，150-200字，口语化分段emoji点缀\n"
                "- xhs_tags: hashtag数组，8-12个\n\n"
                "不要任何解释和markdown代码块，直接返回JSON对象。"
            )
            user_msg = (
                f"品类：{category}\n"
                f"地域：{region}\n"
                f"目标人群：{audience}\n"
                f"季节：{season}\n"
                f"目标：内容创作/种草"
                + xhs_style_hint
                + "\n\n请生成该品类的内容选题方案，以及一篇小红书爆款示例帖子。"
            )

        content = await call_friday(system_prompt, user_msg, max_tokens=2500)
        result = json.loads(content)

        # 附加真实 xhs 帖子（供前端展示"参考热帖"）
        if posts:
            result["posts"] = posts

        return JSONResponse(result)

    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"模型返回格式解析失败: {e}"}, status_code=500)
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            {"error": f"Friday API 调用失败: {e.response.status_code}"},
            status_code=502,
        )
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    except Exception as e:
        return JSONResponse({"error": f"服务异常: {str(e)}"}, status_code=500)


# ─── /api/bubbles ───
@app.post("/api/bubbles")
async def api_bubbles(request: Request):
    """意图驱动的气泡图动态权重计算"""
    try:
        body = await request.json()
        goal = body.get("goal", "commercial")
        audience = body.get("audience", "不限")
        location = body.get("location", "全国")
        season = body.get("season", "当前时节")
        topic = body.get("topic", "美食")

        # 品类 ID 列表：优先用前端传入的 categories，否则用硬编码默认值
        categories_input = body.get("categories", [])
        if categories_input:
            CATEGORIES = [{"id": c["id"], "label": c.get("label", c["id"])} for c in categories_input]
        else:
            CATEGORIES = [
                {"id": "duck",    "label": "烤鸭 & 京味主食"},
                {"id": "hotpot",  "label": "涮肉 & 烤肉"},
                {"id": "bbq",     "label": "夜市 & 烤串"},
                {"id": "drinks",  "label": "饮品 & 咖啡"},
                {"id": "light",   "label": "轻食 & 健康"},
                {"id": "trendy",  "label": "新潮融合菜"},
            ]
        categories_str = "、".join([c["label"] for c in CATEGORIES])

        goal_label_map = {
            "commercial": "商业化运营（带货/GMV/转化）",
            "content":    "内容创作（种草/话题/UGC）",
        }
        goal_label = goal_label_map.get(goal, "商业化运营")

        axis_labels_map = {
            "commercial": {
                "x_label": "供给密度 × 客单价潜力",
                "y_label": "用户决策链路长度",
            },
            "content": {
                "x_label": "话题发酵速度 × UGC产出量",
                "y_label": "内容创作门槛",
            },
        }
        axis_labels = axis_labels_map.get(goal, axis_labels_map["commercial"])

        summary = f"{'商业化' if goal == 'commercial' else '内容型'}视角 × {location}{season} × {audience}"

        system_prompt = (
            "你是一个美食内容运营分析师。\n"
            "根据用户需求，对指定美食品类评分，输出结构化 JSON 数组。\n\n"
            "评分维度说明：\n"
            "- goal=commercial 时：\n"
            "  x = 供给密度 × 客单价潜力（0~1，越高越好）\n"
            "  y = 用户决策链路长度（链路短=高分，即 y 越高代表决策越快速）\n"
            "- goal=content 时：\n"
            "  x = 话题发酵速度 × UGC产出量（0~1，越高越活跃）\n"
            "  y = 内容创作门槛（门槛低=高分，即 y 越高代表越容易创作）\n\n"
            "每个品类输出：id、label、x(0~1)、y(0~1)、size(0~100)、reason(一句话，20字以内)\n"
            "只输出 JSON 数组，不要任何说明、注释或 markdown 代码块。\n"
            "示例：[{\"id\":\"duck\",\"label\":\"烤鸭 & 京味主食\",\"x\":0.85,\"y\":0.70,\"size\":92,\"reason\":\"供给密集，决策链路短，转化快\"}]"
        )

        user_msg = (
            f"目标={goal_label}，地域={location}，人群={audience}，时间={season}，主题={topic}\n"
            f"品类（按顺序对应 id）：\n"
            + "\n".join([f"- id={c['id']}, label={c['label']}" for c in CATEGORIES])
            + "\n\n请对以上品类评分，输出 JSON 数组。"
        )

        content = await call_friday(system_prompt, user_msg, max_tokens=1000)
        bubbles_raw = json.loads(content)

        # 数据校验与修正
        validated_bubbles = []
        id_set = {c["id"] for c in CATEGORIES}
        label_map = {c["id"]: c["label"] for c in CATEGORIES}

        for item in bubbles_raw:
            item_id = str(item.get("id", ""))
            if item_id not in id_set:
                continue
            validated_bubbles.append({
                "id":     item_id,
                "label":  item.get("label", label_map.get(item_id, item_id)),
                "x":      round(max(0.0, min(1.0, float(item.get("x", 0.5)))), 3),
                "y":      round(max(0.0, min(1.0, float(item.get("y", 0.5)))), 3),
                "size":   max(1, min(100, int(item.get("size", 50)))),
                "reason": str(item.get("reason", ""))[:60],
            })

        # 若 AI 返回不完整，补全缺失品类
        returned_ids = {b["id"] for b in validated_bubbles}
        for c in CATEGORIES:
            if c["id"] not in returned_ids:
                validated_bubbles.append({
                    "id":     c["id"],
                    "label":  c["label"],
                    "x":      0.5,
                    "y":      0.5,
                    "size":   50,
                    "reason": "数据待更新",
                })

        return JSONResponse({
            "bubbles":     validated_bubbles,
            "axis_labels": axis_labels,
            "summary":     summary,
        })

    except json.JSONDecodeError as e:
        return JSONResponse({"error": f"模型返回格式解析失败: {e}"}, status_code=500)
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            {"error": f"Friday API 调用失败: {e.response.status_code}"},
            status_code=502,
        )
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=503)
    except Exception as e:
        return JSONResponse({"error": f"服务异常: {str(e)}"}, status_code=500)


@app.post("/api/report")
async def api_report(request: Request):
    body = await request.json()
    goal = body.get("goal", "内容型")
    region = body.get("region", "全国")
    category = body.get("category", "")
    audience = body.get("audience", "不限")
    season = body.get("season", "当前时节")
    topics = body.get("topics", [])
    selected_topic = body.get("selected_topic", "")
    pains = body.get("pains", [])

    topics_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(topics)])
    pains_text = "、".join(pains) if pains else "待分析"

    system_prompt = """你是一位资深内容运营策略师，擅长美食垂类内容选题分析。
请根据用户提供的选题背景，输出完整的选题报告，严格使用 JSON 格式：
{
  "summary": "整体分析摘要（100-200字，口语化，有具体观点）",
  "topics": [
    {
      "title": "选题标题",
      "reason": "推荐理由（30字内）",
      "execution": "执行建议（50字内，包括内容角度/配图建议/发布时机）"
    }
  ],
  "content_plan": "内容排期建议（3-5天，具体到每天做什么）",
  "kpi_estimation": "预期效果评估（互动率/传播预估，要具体数字）"
}
只输出 JSON，不要额外说明。"""

    user_msg = f"""会场目标：{goal}
地域：{region}
品类：{category}
目标人群：{audience}
时间季节：{season}
当前选定主题：{selected_topic}
选题列表：
{topics_text}
核心痛点：{pains_text}

请生成完整选题报告。"""

    try:
        content = await call_friday(system_prompt, user_msg, max_tokens=2000)
        json_match = re.search(r'\{[\s\S]+\}', content)
        if json_match:
            report_data = json.loads(json_match.group())
            return {"success": True, "report": report_data}
        else:
            return {"success": True, "report": {"summary": content, "topics": [], "content_plan": "", "kpi_estimation": ""}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# 启动
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("🍜 foodsearch 本地服务")
    print("=" * 50)
    app_id = get_friday_app_id()
    if not app_id:
        print("⚠️  警告：FRIDAY_APP_ID 未配置！请修改 config.js 中的 FRIDAY_APP_ID")
    else:
        masked = app_id[:8] + "..." + app_id[-4:]
        print(f"✅ Friday AppId: {masked}")
    xhs = has_xhs_cookie()
    print(f"{'✅' if xhs else '⚪'} 小红书 Cookie: {'已检测到，将抓取真实数据' if xhs else '未配置，使用 AI 生成数据'}")
    print(f"\n🌐 服务地址: http://localhost:8080")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
