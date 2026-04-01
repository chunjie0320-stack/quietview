#!/usr/bin/env python3
"""
utils.py — quietview 后端公共工具模块

深模块原则：宽接口背后隐藏实现细节。
调用者只需传 date_str；所有路径、锁、原子写入均在此处封装。
"""

import json
import os
import sys
import subprocess
from datetime import datetime

# ── 常量 ──────────────────────────────────────────────────────────────────────

REPO_DIR    = "/root/.openclaw/workspace"
DATA_DIR    = os.path.join(REPO_DIR, "data")
COOKIES_ENV = "/root/.openclaw/workspace/weibo/cookies.env"

# ── 空结构模板 ────────────────────────────────────────────────────────────────

def _empty_day(date_str: str) -> dict:
    """返回含 7 个字段的空日结构，符合架构文档 Schema 3.1"""
    return {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "news": [],
        "voice": [],
        "ai_voice": [],
        "miao_notice": [],
        "diary": None,
        "miao_thoughts": [],
    }


# ── 核心 IO 函数 ───────────────────────────────────────────────────────────────

def load_or_create_day_data(date_str: str) -> dict:
    """
    读取 data/YYYYMMDD.json；不存在或 JSON 损坏时返回空结构。
    保留 diary / miao_thoughts 字段，其他字段按需补齐。
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{date_str}.json")

    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # 补齐可能缺失的字段（向前兼容）
            template = _empty_day(date_str)
            for key, default in template.items():
                if key not in data:
                    data[key] = default
            return data
        except json.JSONDecodeError as e:
            print(f"[utils] ⚠️  {path} JSON 损坏（{e}），创建空结构", file=sys.stderr)

    return _empty_day(date_str)


def save_day_data(date_str: str, data: dict) -> None:
    """
    原子写入 data/YYYYMMDD.json：
      1. 先写 .bak 备份（覆盖旧备份，只保留最近一份）
      2. 写入 .tmp 临时文件
      3. os.rename() 原子替换目标文件

    保证写入中断不会损坏目标文件。
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    target  = os.path.join(DATA_DIR, f"{date_str}.json")
    tmp     = target + ".tmp"
    bak     = target + ".bak"

    # Step 1: 写备份（只保留最近一份，不用时间戳避免磁盘堆积）
    if os.path.exists(target):
        import shutil
        shutil.copy2(target, bak)

    # Step 2: 写临时文件
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(payload)

    # Step 3: 原子 rename
    os.rename(tmp, target)


def dedup_append(existing: list, new_items: list, key: str) -> list:
    """
    追加去重：以 key 字段为唯一标识，新条目插入头部，已存在的跳过。

    返回合并后的列表（新的在前，旧的在后）。
    与架构文档 5.1 一致：added + existing 顺序。
    """
    seen = {item[key] for item in existing if item.get(key)}
    added = [item for item in new_items if item.get(key) and item[key] not in seen]
    return added + existing


def update_date_index(date_str: str) -> None:
    """
    维护 data/index.json：
      - 确保 date_str 在 dates 数组中
      - dates 保持倒序（最新在前）
      - 原子写入防止并发损坏
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    index_path = os.path.join(DATA_DIR, "index.json")
    tmp_path   = index_path + ".tmp"

    # 读取现有 index
    if os.path.exists(index_path):
        try:
            with open(index_path, encoding="utf-8") as f:
                idx = json.load(f)
        except Exception:
            idx = {"dates": []}
    else:
        idx = {"dates": []}

    dates = idx.get("dates", [])
    if date_str not in dates:
        dates.append(date_str)

    # 倒序排列（纯字符串比较即可，格式 YYYYMMDD 天然可比）
    dates = sorted(set(dates), reverse=True)

    idx["dates"] = dates
    idx["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    payload = json.dumps(idx, ensure_ascii=False, indent=2)
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(payload)
    os.rename(tmp_path, index_path)

    print(f"[utils] index.json 更新完成，dates={dates[:3]}...", file=sys.stderr)


def git_push(msg: str) -> None:
    """
    git add data/ && git commit -m msg && git push
    使用 git_lock.py 的全局锁防止并发冲突。
    调用者不需要感知锁的细节。
    """
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    from git_lock import git_push_with_lock
    git_push_with_lock(REPO_DIR, msg, files_to_add=["data/"])
