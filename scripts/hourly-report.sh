#!/bin/bash

# 读取任务看板
BOARD_FILE="/root/.openclaw/workspace/data/task-board.md"
CONTENT=$(cat "$BOARD_FILE")

# 格式化消息
MSG="📋 **整点任务汇报** "
MSG+="$CONTENT"

# 发送到大象
curl -s -X POST "http://127.0.0.1:18080/message/send" \
  -H "Content-Type: application/json" \
  -d "{
    \"channel\": \"daxiang\",
    \"target\": \"single_522265\",
    \"message\": \"$MSG\"
  }"

echo "Report sent at $(date)"
