#!/bin/bash
# update_site.sh
# 完整更新流程：抓取数据 → 注入HTML → git push
# 用法：bash update_site.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$WORKSPACE_DIR/data/update_log.txt"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 开始更新 ====="

# 确保 data 目录存在
mkdir -p "$WORKSPACE_DIR/data"

# 1. 抓取投资行业资讯
echo "[step 1/4] 抓取 investment_news..."
python3 "$SCRIPT_DIR/fetch_investment_news.py"

# 2. 抓取AI行业声音
echo "[step 2/4] 抓取 ai_news..."
python3 "$SCRIPT_DIR/fetch_ai_news.py"

# 3. 注入HTML
echo "[step 3/4] 注入内容到 HTML..."
python3 "$SCRIPT_DIR/inject_content.py"

# 4. push到GitHub
echo "[step 4/4] push 到 GitHub..."
bash "$SCRIPT_DIR/push_to_github.sh"

# 写更新日志
echo "$(date '+%Y-%m-%d %H:%M') 更新完成" >> "$LOG_FILE"
echo "===== 全部完成 ====="
