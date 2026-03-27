#!/bin/bash
# 喵子告知触发器 - cron 调用此脚本
# 发送消息给 openclaw 主 session，让喵子生成告知内容并更新网站

SLOT=$(date "+%Y.%m.%d %H:%M")
LOG="/root/.openclaw/logs/miao_notice.log"

echo "[${SLOT}] 触发喵子告知更新..." >> "$LOG"

# 发消息给主 session（daxiang channel）
# openclaw agent 会路由到当前活跃 session
openclaw agent --message "【系统定时任务】现在是 ${SLOT}，请执行喵子告知更新：
1. 读取 /root/.openclaw/workspace/quietview-demo.html 中的行业资讯(tl-title + tl-body)和行业声音(tl-tag + tl-title + tl-body)内容
2. 基于这些内容，以喵子风格写一段整理+判断+点评（100-200字，不超过3段，一针见血大白话）
3. 替换 #miao-notice 区块内容，label改为「🐱 喵子告知 · ${SLOT}」
4. div自查确认depth=0
5. git commit + push
完成后回复「喵子告知已更新 ${SLOT}」" >> "$LOG" 2>&1

echo "[${SLOT}] 消息已发送" >> "$LOG"
