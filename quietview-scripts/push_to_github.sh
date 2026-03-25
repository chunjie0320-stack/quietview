#!/bin/bash
# push_to_github.sh
# 将更新后的HTML push到GitHub

set -e

cd /root/.openclaw/workspace

# 检查是否有变更
if git diff --quiet quietview-demo.html; then
    echo "[info] quietview-demo.html 无变更，跳过 push"
    exit 0
fi

git add quietview-demo.html
git commit -m "auto: update content $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo "[done] push 完成"
