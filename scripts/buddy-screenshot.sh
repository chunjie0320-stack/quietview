#!/bin/bash
# Buddy 5状态截图，发送给女王大人
set -e
OUT="/tmp/buddy-shots"
mkdir -p "$OUT"
HTML="http://localhost:9988/buddy-pixel-demo.html"

# 确保 http server 在跑
if ! curl -s "$HTML" > /dev/null 2>&1; then
  cd /root/.openclaw/workspace
  python3 -m http.server 9988 &>/dev/null &
  sleep 2
fi

# 打开页面
agent-browser open "$HTML"
agent-browser wait --load networkidle

declare -A STATES
STATES=(
  ["idle"]="idle"
  ["happy"]="happy"
  ["confused"]="confused"
  ["sleeping"]="sleeping"
  ["peeking"]="peeking"
)

LABELS=("idle" "happy" "confused" "sleeping" "peeking")

for state in "${LABELS[@]}"; do
  agent-browser eval "go('${state}', null)"
  sleep 0.5
  agent-browser screenshot "$OUT/${state}.png"
  echo "✓ $state"
done

echo "截图完成，路径：$OUT/"
ls -la "$OUT/"
