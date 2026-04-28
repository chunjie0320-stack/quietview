#!/bin/bash
# Buddy 早安截图 — 5个状态拼图发给女王大人
set -e

HTML="http://localhost:9988/buddy-pixel-demo.html"
OUT="/tmp/buddy-morning"
mkdir -p "$OUT"

# 确保 http server 在跑
if ! curl -s "$HTML" > /dev/null 2>&1; then
  cd /root/.openclaw/workspace
  python3 -m http.server 9988 &
  sleep 2
fi

# 用 agent-browser 截5个状态
states=("idle:😌 待机" "happy:🎉 开心" "confused:🤔 困惑" "sleeping:😴 睡觉" "peeking:👀 偷看")
for item in "${states[@]}"; do
  key="${item%%:*}"
  label="${item##*:}"
  agent-browser open "$HTML" 2>/dev/null
  agent-browser wait --load networkidle 2>/dev/null
  agent-browser screenshot "$OUT/${key}.png" 2>/dev/null || true
done

echo "截图完成：$OUT/"
