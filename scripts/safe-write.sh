#!/bin/bash
# safe-write.sh - 原子化写入脚本，防止并发冲突
# 用法: safe-write.sh <target_file> <data_json>
# 示例: safe-write.sh data/20260603.json '{"key":"value"}'

set -euo pipefail

target="$1"
data="$2"
lock_file="${target}.lock"

if [ -z "$target" ] || [ -z "$data" ]; then
  echo "用法: safe-write.sh <target_file> <data_json>" >&2
  exit 1
fi

# 1. 加锁
if [ -f "$lock_file" ]; then
  echo "⚠️ 锁文件存在，目标文件可能被其他进程写入中: $lock_file"
  echo "等待10秒后重试..."
  sleep 10
  if [ -f "$lock_file" ]; then
    echo "❌ 锁仍存在，跳过写入（避免并发冲突）"
    exit 0
  fi
fi

touch "$lock_file"
trap 'rm -f "$lock_file"' EXIT

# 2. 读现有数据（如果文件存在且是合法JSON）
if [ -f "$target" ] && [ -s "$target" ]; then
  if python3 -c "import json; json.load(open('$target'))" 2>/dev/null; then
    existing=$(cat "$target")
  else
    echo "⚠️ 目标文件不是合法JSON，直接覆盖"
    existing=""
  fi
else
  existing=""
fi

# 3. 原子化写入：合并→写临时文件→rename替换
python3 -c "
import json, sys

existing = sys.stdin.read() if '$existing' else ''
new_data_str = '''$data'''

# 解析现有数据
if existing.strip():
    existing_data = json.loads(existing)
else:
    existing_data = {}

# 解析新数据
try:
    new_data = json.loads(new_data_str)
except json.JSONDecodeError:
    print('❌ 新数据不是合法JSON，跳过', file=sys.stderr)
    sys.exit(1)

# 合并（简单浅合并，可根据需要改为深合并）
merged = {**existing_data, **new_data}

# 写临时文件
temp = '$target.tmp'
with open(temp, 'w') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

# 原子替换
import os
os.rename(temp, '$target')
print('✅ 原子写入成功: $target')
" <<< "$existing"

# 4. 写入后校验
if python3 -c "import json; json.load(open('$target'))" 2>/dev/null; then
  echo "✅ 写入后校验通过"
else
  echo "❌ 写入后校验失败，文件可能损坏"
  exit 1
fi

echo "✅ safe-write 完成: $target"
