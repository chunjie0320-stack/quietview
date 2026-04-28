#!/usr/bin/env python3
"""
trend-topic-generator — Phase 1: Trend Fetching
双层抓取策略：
  Phase 1a (广度) catclaw-search + XHS 搜索列表（标题/作者/点赞/URL）
  Phase 1b (深度) xhs-fetcher.mjs 对点赞 Top N 帖子深度抓取（正文+评论）

逆向保障：
  - 数据量 <10 条 → 自动扩词重试（换引擎/扩关键词）
  - Cookie 过期 → 明确报告，不静默跳过
  - 内容质量过滤 → 去除标题过短/明显广告内容
  - 全链路 data_quality 字段，透传给分析和输出层

Usage:
  python3 fetch_trends.py --industry "美食" --goal commercial --season "春季"
  python3 fetch_trends.py --industry "北京美食" --goal commercial --deep-xhs 3

Output:
  ~/.openclaw/logs/trends_<industry>_<timestamp>.json
"""

import argparse
import json
import subprocess
import sys
import os
import time
import re
from datetime import datetime
from pathlib import Path

# ── 参数解析 ──────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Fetch trend topics for a given industry")
parser.add_argument("--industry",   required=True)
parser.add_argument("--goal",       required=True, choices=["commercial", "content"])
parser.add_argument("--season",     default="")
parser.add_argument("--category",   default="")
parser.add_argument("--audience",   default="")
parser.add_argument("--deep-xhs",   type=int, default=0, dest="deep_xhs")
parser.add_argument("--min-results",type=int, default=10, dest="min_results",
                    help="数据量门槛，低于此值触发扩词重试（默认10）")
args = parser.parse_args()

# ── 输出路径 ──────────────────────────────────────────────────────
os.makedirs(os.path.expanduser("~/.openclaw/logs"), exist_ok=True)
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
safe_industry = args.industry.replace(" ", "_").replace("/", "_")
OUT_FILE = os.path.expanduser(f"~/.openclaw/logs/trends_{safe_industry}_{ts}.json")

# ── data_quality 追踪 ─────────────────────────────────────────────
data_quality = {
    "catclaw_search": {"count": 0, "status": "pending"},
    "xhs_search":     {"count": 0, "status": "skipped", "reason": ""},
    "xhs_deep":       {"count": 0, "status": "skipped", "reason": ""},
    "retry":          {"triggered": False, "reason": "", "added": 0},
    "filter":         {"removed": 0, "reason": ""},
    "warnings":       [],
}

# ── xhs-fetcher 路径检测 ──────────────────────────────────────────
XHS_FETCHER_SKILL_DIR = os.path.expanduser("~/.openclaw/skills/xhs-fetcher")
XHS_FETCHER_RUN_SH    = os.path.join(XHS_FETCHER_SKILL_DIR, "scripts", "run.sh")

def xhs_fetcher_available():
    if not os.path.exists(XHS_FETCHER_RUN_SH):
        return False, "run.sh 不存在"
    node_modules = os.path.expanduser(
        "~/.openclaw/workspace/skills/trend-topic-generator/node_modules"
    )
    if not os.path.exists(os.path.join(node_modules, "playwright")):
        return False, f"playwright node_modules 未安装（{node_modules}）"
    return True, ""

# ── 搜索关键词生成 ────────────────────────────────────────────────
def build_queries(industry, goal, season, category, audience, mode="primary"):
    """
    mode='primary'  : 第一轮搜索词（精准）
    mode='fallback' : 第二轮扩词（更宽泛，换引擎）
    """
    base = industry
    if category:
        base = f"{category} {industry}"
    if season and mode == "primary":
        base = f"{season} {base}"

    if goal == "commercial":
        if mode == "primary":
            queries = [
                f"小红书 {base} 推荐 好吃",
                f"小红书 {base} 热门 {season or ''}",
                f"小红书 {base} 种草 购买",
            ]
        else:
            # fallback：去掉小红书限定，扩大到全网，换关键词组合
            queries = [
                f"{industry} 热门推荐 {season or ''}",
                f"{industry} 流行趋势",
                f"{industry} 用户喜欢什么",
                f"小红书 {industry} 爆款",
            ]
    else:
        if mode == "primary":
            queries = [
                f"小红书 {base} 热门话题",
                f"小红书 {base} 爆文 {season or ''}",
                f"小红书 {base} 情感 故事",
            ]
        else:
            queries = [
                f"{industry} 话题 热度",
                f"{industry} 情感共鸣 内容",
                f"小红书 {industry} 高赞",
                f"{industry} 创作方向",
            ]

    if audience and mode == "primary":
        queries.append(f"小红书 {base} {audience}")

    return [q.strip() for q in queries]

# ── catclaw-search 抓取 ───────────────────────────────────────────
CATCLAW_SKILL = "/app/skills/catclaw-search/scripts/catclaw_search.py"

def catclaw_search(query, engine="bing", count=10):
    try:
        cmd = ["python3", CATCLAW_SKILL, "search", query, "-s", engine, "-n", str(count)]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            data = json.loads(out.stdout)
            return data if isinstance(data, list) else data.get("results", [])
    except Exception as e:
        print(f"[catclaw_search] 失败: {query} — {e}", file=sys.stderr)
    return []

def quality_filter(items, source=""):
    """过滤低质量内容：标题太短、明显广告"""
    before = len(items)
    filtered = []
    for item in items:
        title = item.get("title", "") or item.get("name", "") or ""
        # 过滤：标题<4字、纯英文数字、明显广告关键词
        if len(title) < 4:
            continue
        if re.match(r'^[a-zA-Z0-9\s\-_\.]+$', title):
            continue
        ad_keywords = ["广告", "点击领取", "限时优惠", "扫码", "私信我"]
        if any(kw in title for kw in ad_keywords):
            continue
        filtered.append(item)
    removed = before - len(filtered)
    if removed > 0:
        data_quality["filter"]["removed"] += removed
        data_quality["filter"]["reason"] += f"{source}过滤{removed}条; "
    return filtered

# ── Phase 1a: 主搜索 ─────────────────────────────────────────────
queries_primary = build_queries(args.industry, args.goal, args.season, args.category, args.audience, "primary")
print(f"[fetch_trends] 主搜索词 {len(queries_primary)} 条: {queries_primary}")

results_search = []
for q in queries_primary:
    items = catclaw_search(q)
    for item in items:
        item["_query"] = q
        item["_source"] = "catclaw-search"
    results_search.extend(items)
    time.sleep(0.5)

results_search = quality_filter(results_search, "catclaw-search")
print(f"[fetch_trends] catclaw-search 主搜: {len(results_search)} 条（过滤后）")
data_quality["catclaw_search"]["count"] = len(results_search)
data_quality["catclaw_search"]["status"] = "ok" if results_search else "empty"

# ── Phase 1a: XHS 搜索列表 ───────────────────────────────────────
XHS_SCRIPT  = os.path.expanduser("~/.openclaw/workspace/scripts/xhs-fetch-with-cookie.py")
XHS_COOKIES = os.path.expanduser("~/.openclaw/xiaohongshu-cookies.json")
results_xhs = []

if os.path.exists(XHS_COOKIES) and os.path.exists(XHS_SCRIPT):
    data_quality["xhs_search"]["status"] = "attempting"
    xhs_keywords = [args.industry]
    if args.category:
        xhs_keywords.append(f"{args.category} {args.industry}")
    if args.season:
        xhs_keywords.append(f"{args.season} {args.industry}")

    for kw in xhs_keywords:
        try:
            out = subprocess.run(
                ["python3", XHS_SCRIPT, kw],
                capture_output=True, text=True, timeout=60
            )
            if out.returncode == 0 and out.stdout.strip():
                items = json.loads(out.stdout)
                if isinstance(items, list):
                    for item in items:
                        item["_query"] = kw
                        item["_source"] = "xhs-playwright"
                    results_xhs.extend(items)
                    print(f"[fetch_trends] XHS '{kw}': {len(items)} 条")
                else:
                    msg = f"XHS返回格式异常({type(items).__name__})"
                    data_quality["warnings"].append(msg)
                    print(f"[fetch_trends] ⚠️ {msg}", file=sys.stderr)
            else:
                stderr_lower = (out.stderr or "").lower()
                if "cookie" in stderr_lower or "过期" in stderr_lower or "登录" in stderr_lower:
                    msg = "XHS Cookie已过期，小红书直连数据不可用"
                    data_quality["xhs_search"]["status"] = "cookie_expired"
                    data_quality["xhs_search"]["reason"] = msg
                    data_quality["warnings"].append(msg)
                    print(f"[fetch_trends] ⚠️ {msg}")
                    break
                else:
                    msg = f"XHS '{kw}' 抓取失败: {out.stderr[:100]}"
                    data_quality["warnings"].append(msg)
                    print(f"[fetch_trends] ⚠️ {msg}", file=sys.stderr)
        except Exception as e:
            msg = f"XHS 抓取异常: {e}"
            data_quality["warnings"].append(msg)
            print(f"[fetch_trends] ⚠️ {msg}", file=sys.stderr)
        time.sleep(1)

    results_xhs = quality_filter(results_xhs, "xhs-search")
    data_quality["xhs_search"]["count"] = len(results_xhs)
    if data_quality["xhs_search"]["status"] == "attempting":
        data_quality["xhs_search"]["status"] = "ok" if results_xhs else "empty"
else:
    reason = "Cookie文件不存在" if not os.path.exists(XHS_COOKIES) else "抓取脚本不存在"
    data_quality["xhs_search"]["reason"] = reason
    print(f"[fetch_trends] 跳过XHS直连: {reason}")

total_1a = len(results_search) + len(results_xhs)
print(f"[fetch_trends] Phase 1a 合计: {total_1a} 条")

# ── 数据量门槛检查 + 自动扩词重试 ────────────────────────────────
results_retry = []
if total_1a < args.min_results:
    msg = f"数据量不足（{total_1a} < {args.min_results}），触发扩词重试"
    print(f"\n[fetch_trends] ⚠️ {msg}")
    data_quality["retry"]["triggered"] = True
    data_quality["retry"]["reason"] = msg

    queries_fallback = build_queries(
        args.industry, args.goal, args.season, args.category, args.audience, "fallback"
    )
    print(f"[fetch_trends] 扩词 {len(queries_fallback)} 条（换引擎: baidu）: {queries_fallback}")

    for q in queries_fallback:
        # 先试 baidu，再试 bing 以免完全相同
        for engine in ["baidu", "bing"]:
            items = catclaw_search(q, engine=engine, count=8)
            if items:
                for item in items:
                    item["_query"] = q
                    item["_source"] = f"catclaw-{engine}-retry"
                results_retry.extend(items)
                break
        time.sleep(0.3)

    results_retry = quality_filter(results_retry, "retry")
    data_quality["retry"]["added"] = len(results_retry)
    print(f"[fetch_trends] 扩词重试补充: {len(results_retry)} 条")

    if total_1a + len(results_retry) < 5:
        warn = f"扩词后仍只有 {total_1a + len(results_retry)} 条，数据严重不足；行业可能太冷门或关键词太窄，建议换更通用的关键词"
        data_quality["warnings"].append(warn)
        print(f"[fetch_trends] 🔴 {warn}")
else:
    print(f"[fetch_trends] 数据量充足（{total_1a} >= {args.min_results}），无需重试")

all_1a = results_search + results_xhs + results_retry

# ── Phase 1b: XHS 深度抓取 ───────────────────────────────────────
results_xhs_deep = []

def parse_likes(likes_str):
    if not likes_str:
        return 0
    match = re.match(r'^([\d.]+)\s*万?$', likes_str.strip())
    if match:
        num = float(match.group(1))
        return int(num * 10000) if '万' in likes_str else int(num)
    return 0

def run_xhs_fetcher(note_url, out_dir):
    try:
        work_dir = os.path.expanduser(
            "~/.openclaw/workspace/skills/trend-topic-generator"
        )
        cmd = ["bash", XHS_FETCHER_RUN_SH, note_url,
               "--out", out_dir, "--with-comments", "--no-upload-sankuai"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=work_dir)
        return result.returncode == 0, result.stderr[:500] if result.returncode != 0 else ""
    except Exception as e:
        return False, str(e)

if args.deep_xhs > 0 and results_xhs:
    avail, reason = xhs_fetcher_available()
    if not avail:
        msg = f"xhs-fetcher 不可用: {reason}（提示：cd ~/.openclaw/workspace/skills/trend-topic-generator && npm install playwright sharp）"
        data_quality["xhs_deep"]["status"] = "unavailable"
        data_quality["xhs_deep"]["reason"] = msg
        data_quality["warnings"].append(msg)
        print(f"[fetch_trends] ⚠️ {msg}")
    else:
        xhs_with_url = [r for r in results_xhs if r.get("url")]
        xhs_with_url.sort(key=lambda x: parse_likes(x.get("likes", "")), reverse=True)
        top_posts = xhs_with_url[:args.deep_xhs]

        if not top_posts:
            msg = "XHS搜索结果无URL，无法深度抓取（搜索脚本可能未返回URL）"
            data_quality["xhs_deep"]["status"] = "no_url"
            data_quality["xhs_deep"]["reason"] = msg
            data_quality["warnings"].append(msg)
            print(f"[fetch_trends] ⚠️ {msg}")
        else:
            deep_out = os.path.expanduser(f"~/.openclaw/logs/xhs-deep-{ts}")
            os.makedirs(deep_out, exist_ok=True)
            success_count = 0

            for i, post in enumerate(top_posts):
                url = post["url"]
                print(f"[fetch_trends] [{i+1}/{len(top_posts)}] 深度抓取: {post.get('title','')[:30]}...")
                ok, err = run_xhs_fetcher(url, deep_out)
                if ok:
                    note_id_match = re.search(r'/explore/([0-9a-f]+)', url)
                    if note_id_match:
                        note_json = os.path.join(deep_out, f"xhs-{note_id_match.group(1)}", "note.json")
                        if os.path.exists(note_json):
                            with open(note_json) as f:
                                note_data = json.load(f)
                            results_xhs_deep.append({
                                "_source": "xhs-fetcher-deep",
                                "_original_title": post.get("title", ""),
                                "_original_likes": post.get("likes", ""),
                                "url": url,
                                "title": note_data.get("title", ""),
                                "body": note_data.get("body", ""),
                                "comments": note_data.get("comments", []),
                                "comment_count": len(note_data.get("comments", [])),
                            })
                            success_count += 1
                            print(f"[fetch_trends]   ✅ 正文:{len(note_data.get('body',''))}字 评论:{len(note_data.get('comments',[]))}条")
                else:
                    msg = f"深度抓取失败(帖子{i+1}): {err[:100]}"
                    data_quality["warnings"].append(msg)
                    print(f"[fetch_trends]   ❌ {err[:100]}")
                time.sleep(2)

            data_quality["xhs_deep"]["count"]  = len(results_xhs_deep)
            data_quality["xhs_deep"]["status"] = "ok" if results_xhs_deep else "all_failed"
            if not results_xhs_deep:
                data_quality["warnings"].append("深度抓取全部失败，分析将仅基于搜索列表")
                print("[fetch_trends] ⚠️ 深度抓取全部失败，分析将仅基于搜索列表数据")

elif args.deep_xhs > 0 and not results_xhs:
    msg = "XHS搜索无结果，跳过深度抓取"
    data_quality["xhs_deep"]["reason"] = msg
    print(f"[fetch_trends] ⚠️ {msg}")

# ── 汇总输出 ─────────────────────────────────────────────────────
total_final = len(all_1a)
data_quality["total"] = total_final
data_quality["data_completeness"] = (
    "充足(>20条)" if total_final >= 20 else
    "一般(10-20条)" if total_final >= 10 else
    "不足(<10条，选题置信度偏低，建议补充参数)"
)
data_quality["has_deep_content"] = len(results_xhs_deep) > 0

output = {
    "meta": {
        "industry":  args.industry,
        "goal":      args.goal,
        "season":    args.season,
        "category":  args.category,
        "audience":  args.audience,
        "queries":   queries_primary,
        "timestamp": datetime.now().isoformat(),
    },
    "results": all_1a,
    "xhs_deep_results": results_xhs_deep,
    "data_quality": data_quality,
    "summary": {
        "catclaw_search_count": len(results_search),
        "xhs_search_count":     len(results_xhs),
        "retry_count":          len(results_retry),
        "xhs_deep_count":       len(results_xhs_deep),
        "total":                total_final,
    }
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[fetch_trends] ✅ 完成")
print(f"  catclaw-search:  {len(results_search)} 条")
print(f"  XHS 搜索列表:   {len(results_xhs)} 条")
print(f"  扩词重试补充:   {len(results_retry)} 条")
print(f"  XHS 深度抓取:   {len(results_xhs_deep)} 篇")
print(f"  合计:           {total_final} 条")
if data_quality["warnings"]:
    print(f"\n⚠️  警告 ({len(data_quality['warnings'])} 条):")
    for w in data_quality["warnings"]:
        print(f"   · {w}")
print(f"\n  输出文件: {OUT_FILE}")
print(f"OUTPUT_FILE={OUT_FILE}")
