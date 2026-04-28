#!/bin/bash
# Buddy 早安汇报 — 截5张图后用文字描述发给女王大人
set -e
OUT="/tmp/buddy-shots-$(date +%Y%m%d)"
mkdir -p "$OUT"
HTML="http://localhost:9988/buddy-pixel-demo.html"

# 确保 http server 在跑
if ! curl -s "$HTML" > /dev/null 2>&1; then
  cd /root/.openclaw/workspace
  python3 -m http.server 9988 &>/dev/null &
  sleep 2
fi

agent-browser open "$HTML"
agent-browser wait --load networkidle

for state in idle happy confused sleeping peeking; do
  agent-browser eval "go('${state}', null)"
  sleep 0.5
  agent-browser screenshot "$OUT/${state}.png"
done

echo "shots_ready:$OUT"
