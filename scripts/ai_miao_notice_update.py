#!/usr/bin/env python3
"""
AI 行业声音 · 喵子告知更新脚本

职责：
  1. 读取当天 YYYYMMDD.json 中的 ai_voice[]
  2. 调 AI API 生成「AI喵子告知」
  3. dedup_append 写 ai_miao_notice[]（以 label 去重，新的在前）
  4. save_day_data → update_date_index → git_push

触发：
  - 被 fetch_all.py 末尾调用（抓完 ai_voice 后自动触发）
  - 或 cron 独立触发（8/12/18/22点）

用法：
  python3 ai_miao_notice_update.py             # 正常运行
  python3 ai_miao_notice_update.py --dry-run   # 只打印，不写文件
  python3 ai_miao_notice_update.py --no-push   # 不 git push（被 fetch_all 调用时用）
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


# ── Prompt 构建 ────────────────────────────────────────────────────────────────

def build_ai_notice_prompt(ai_voice_list: list, slot_label: str) -> str:
    if ai_voice_list:
        items_text = "\n".join(
            f"· [{v.get('source', '来源')}] {v.get('title', '')}：{v.get('body', v.get('digest', ''))[:100]}"
            for v in ai_voice_list[:20]  # 最多取前20条防超token
        )
    else:
        items_text = "（暂无AI行业动态）"

    return f"""你是喵子，一只资深产品+投资视角的三花猫AI助手，文风简练有料。

现在是 {slot_label}，请基于以下 AI 行业声音，写一段「喵子AI告知」：
- 梳理今日 AI 行业最值得关注的 1-3 个动态
- 分析其产品/商业/技术含义，给出喵子的判断
- 风格：一针见血，大白话优先，100-200字，不超过3段

【AI行业声音】
{items_text}

直接输出告知内容，不要任何前缀或解释。"""


# ── API 调用（复用 miao_notice_update 的逻辑）──────────────────────────────────

def _load_api_config() -> tuple:
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


def generate_ai_notice(ai_voice_list: list, slot_label: str) -> str:
    try:
        prompt  = build_ai_notice_prompt(ai_voice_list, slot_label)
        content = call_ai(prompt)
        if content:
            return content
    except Exception as e:
        print(f"  [generate_ai_notice] error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    return "（喵子暂时无法生成AI告知：AI接口连接失败）"


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    dry_run  = "--dry-run" in sys.argv
    no_push  = "--no-push" in sys.argv
    now      = datetime.now()
    slot_label = now.strftime("%Y.%m.%d %H:%M")
    date_str   = now.strftime("%Y%m%d")

    print(f"[{slot_label}] AI喵子告知更新开始...")

    try:
        day_data = load_or_create_day_data(date_str)
        ai_voice = day_data.get("ai_voice", [])

        print(f"  AI行业声音条数: {len(ai_voice)}")

        if not ai_voice:
            print("  ⚠️ 暂无AI行业声音，跳过生成")
            return

        notice_content = generate_ai_notice(ai_voice, slot_label)
        print(f"  生成内容: {notice_content[:80]}...")

        new_entry = {
            "content": notice_content,
            "label":   f"🐱 喵子AI告知 · {slot_label}",
        }

        if dry_run:
            print(f"[dry-run] would write ai_miao_notice to data/{date_str}.json")
            print(f"  label: {new_entry['label']}")
            print(f"  content: {notice_content[:100]}")
            return

        existing = day_data.get("ai_miao_notice", [])
        if isinstance(existing, dict):
            existing = [existing]

        day_data["ai_miao_notice"] = dedup_append(
            existing, [new_entry], key="label"
        )
        day_data["generated_at"] = datetime.now().isoformat()

        save_day_data(date_str, day_data)
        print(f"  ✅ JSON ai_miao_notice 更新完成: data/{date_str}.json")

        update_date_index(date_str)

        if not no_push:
            git_push(f"auto: AI喵子告知更新 {slot_label}")
            print(f"[{slot_label}] ✅ 完成（含git push）")
        else:
            print(f"[{slot_label}] ✅ 完成（跳过git push，由调用方统一push）")

    except Exception as e:
        print(f"[{slot_label}] ❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
