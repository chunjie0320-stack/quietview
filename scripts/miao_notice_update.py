#!/usr/bin/env python3
"""
喵子告知自动更新脚本（C方案 — JSON-only）

职责：
  1. 读取当天 YYYYMMDD.json 中的 news[] + voice[]
  2. 调 AI API 生成喵子告知
  3. dedup_append 写 miao_notice[]（以 label 去重，新的在前）
  4. save_day_data → update_date_index → git_push

触发时间：每天 06:00 / 10:00 / 14:00 / 18:00 / 22:00

用法：
  python3 miao_notice_update.py             # 正常运行
  python3 miao_notice_update.py --dry-run   # 只打印，不写文件
"""

import re
import sys
import json
import os
import urllib.request
from datetime import datetime

# ── 公共工具 ──────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import (
    load_or_create_day_data, save_day_data,
    dedup_append, update_date_index, git_push,
)


# ── 1. 提取告知素材 ───────────────────────────────────────────────────────────

def extract_context(data: dict) -> tuple[list, list]:
    """从 day_data 提取 news 和 voice 列表"""
    news  = data.get("news", [])
    voice = data.get("voice", [])
    return news, voice


# ── 2. 构建 Prompt ────────────────────────────────────────────────────────────

def build_prompt(news_list: list, voice_list: list, slot_label: str) -> str:
    news_text = (
        "\n".join(
            f"· {n.get('title', '')}：{n.get('body', '')[:80]}"
            for n in news_list
        )
        if news_list else "（暂无资讯）"
    )
    voice_text = (
        "\n".join(
            f"· [{v.get('source', '来源')}] {v.get('title', '')}：{v.get('digest', v.get('body', ''))[:80]}"
            for v in voice_list
        )
        if voice_list else "（暂无声音）"
    )
    return f"""你是喵子，一只资深投资视角+产品思维的三花猫AI助手，文风简练有料。

现在是{slot_label}，请基于以下行业资讯和行业声音，写一段「喵子告知」：
- 整理核心信息，找出关键信号
- 给出喵子自己的判断和点评
- 风格：一针见血，大白话优先，100-200字，不超过3段

【行业资讯】
{news_text}

【行业声音】
{voice_text}

直接输出告知内容，不要任何前缀或解释。"""


# ── 3. 调用 AI API ────────────────────────────────────────────────────────────

def _load_api_config() -> tuple[str, str, str, dict]:
    """
    加载 API 配置：
      1. 优先读环境变量 OPENCLAW_API_KEY / OPENCLAW_BASE_URL / OPENCLAW_MODEL
      2. fallback 到 ~/.openclaw/openclaw.json
    返回 (base_url, api_key, model_id, extra_headers)
    """
    api_key  = os.environ.get("OPENCLAW_API_KEY", "").strip()
    base_url = os.environ.get("OPENCLAW_BASE_URL", "").strip()
    model_id = os.environ.get("OPENCLAW_MODEL", "").strip()

    if not api_key:
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        provider = (cfg.get("models", {}).get("providers", {})
                    .get("kubeplex-maas", {}))
        base_url = base_url or provider.get("baseUrl", "https://mmc.sankuai.com/openclaw/v1")
        api_key  = api_key  or provider.get("apiKey",  "catpaw")
        model_id = model_id or (provider.get("models", [{}])[0].get("id", "catclaw-proxy-model"))
        extra_headers = provider.get("headers", {})
    else:
        base_url = base_url or "https://mmc.sankuai.com/openclaw/v1"
        model_id = model_id or "catclaw-proxy-model"
        extra_headers = {}

    return base_url, api_key, model_id, extra_headers


def call_ai(prompt: str) -> str:
    """调用 AI API，返回生成的文本内容"""
    base_url, api_key, model_id, extra_headers = _load_api_config()

    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "stream": False,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    headers.update(extra_headers)

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=payload, headers=headers, method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")

    # 处理 SSE 流式响应
    if raw.strip().startswith("data:"):
        chunks = []
        for line in raw.split("\n"):
            line = line.strip()
            if not line.startswith("data:"):
                continue
            json_str = re.sub(r"^data:data:", "", line)
            json_str = re.sub(r"^data:", "", json_str).strip()
            if json_str in ("[DONE]", ""):
                continue
            try:
                chunk = json.loads(json_str)
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                if delta.get("content"):
                    chunks.append(delta["content"])
            except Exception:
                continue
        return "".join(chunks).strip()
    else:
        data = json.loads(raw)
        return data["choices"][0]["message"]["content"].strip()


def generate_notice(news_list: list, voice_list: list, slot_label: str) -> str:
    """生成喵子告知，失败时返回友好的 fallback 文本"""
    try:
        prompt  = build_prompt(news_list, voice_list, slot_label)
        content = call_ai(prompt)
        if content:
            return content
    except Exception as e:
        print(f"  [generate_notice] error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    return "（喵子暂时无法生成告知：AI接口连接失败）"


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    dry_run    = "--dry-run" in sys.argv
    now        = datetime.now()
    slot_label = now.strftime("%Y.%m.%d %H:%M")
    date_str   = now.strftime("%Y%m%d")

    print(f"[{slot_label}] 喵子告知更新开始（JSON-only）...")

    try:
        # 1. 读取当天 JSON（直接读，不再重复抓取）
        day_data = load_or_create_day_data(date_str)
        news_list, voice_list = extract_context(day_data)

        print(f"  资讯条数: {len(news_list)}, 声音条数: {len(voice_list)}")

        # 2. 生成喵子告知
        notice_content = generate_notice(news_list, voice_list, slot_label)
        print(f"  生成内容: {notice_content[:80]}...")

        new_entry = {
            "content": notice_content,
            "label":   f"🐱 喵子告知 · {slot_label}",
        }

        if dry_run:
            print(f"[dry-run] would write miao_notice to data/{date_str}.json")
            print(f"  label: {new_entry['label']}")
            print(f"  content: {notice_content[:100]}")
            return

        # 3. dedup_append 写 miao_notice[]（以 label 去重，新的在前）
        existing_notices = day_data.get("miao_notice", [])
        if isinstance(existing_notices, dict):
            existing_notices = [existing_notices]  # 兼容旧格式

        day_data["miao_notice"] = dedup_append(
            existing_notices, [new_entry], key="label"
        )
        day_data["generated_at"] = datetime.now().isoformat()

        # 4. 原子写入
        save_day_data(date_str, day_data)
        print(f"  ✅ JSON miao_notice 更新完成: data/{date_str}.json")

        # 5. 更新日期索引
        update_date_index(date_str)

        # 6. git push（只推 data/）
        git_push(f"auto: 喵子告知更新 {slot_label}")
        print(f"[{slot_label}] ✅ 完成")

    except Exception as e:
        print(f"[{slot_label}] ❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
