#!/bin/bash
# memory-harvest.sh - 扫描最近session JSONL，捞网漏记的memory
# 用法: bash memory-harvest.sh [分钟数]  默认35分钟

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
WORKSPACE="$HOME/.openclaw/workspace"
MINUTES=${1:-35}  # 默认扫35分钟
TODAY=$(TZ=Asia/Shanghai date +%Y-%m-%d)
MEMORY_FILE="$WORKSPACE/memory/$TODAY.md"
HARVEST_LOG="$WORKSPACE/data/harvest-$(TZ=Asia/Shanghai date +%Y%m%d-%H%M).log"

# vm-remember 路径
VM_REMEMBER="node /root/.openclaw/skills/agent-memory/scripts/vm-remember.js"

# 信号词（决策/发现/教训/指令/重要）
SIGNAL_WORDS="决定|改为|选择|放弃|确认|就用|发现|原来|终于|找到了|根本原因|搞清楚了|踩坑|注意|以后|记住|千万别|别忘了|关键|必须|重要|核心|红线"

# 偏好类信号词
PREF_WORDS="喜欢|不喜欢|习惯|风格|偏好|prefer|喜欢用|不想用|倾向|讨厌"
# 决策类信号词
DECISION_WORDS="决定|改为|选择|放弃|确认|就用|采用|不用|选A|选B"
# 教训类信号词
LESSON_WORDS="错了|不是|修正|踩坑|搞清楚了|根本原因|原来|纠正|不对|改正"

# 按内容自动分类返回 vm-remember 参数
classify_and_remember() {
    local content="$1"
    local key importance
    if echo "$content" | grep -qE "$PREF_WORDS"; then
        key="preference/harvest"
        importance="0.85"
    elif echo "$content" | grep -qE "$DECISION_WORDS"; then
        key="decision/harvest"
        importance="0.8"
    elif echo "$content" | grep -qE "$LESSON_WORDS"; then
        key="lesson/harvest"
        importance="0.9"
    else
        key="context/harvest"
        importance="0.7"
    fi
    # 截断内容到400字符，避免过长
    local short_content="${content:0:400}"
    echo "  → 写入向量库 [${key}] importance=${importance}" >&2
    HTTPS_PROXY=http://127.0.0.1:8118 $VM_REMEMBER "$short_content" \
        --key "$key" --importance "$importance" 2>&1 | tail -1 >&2
}

# 确保data目录存在
mkdir -p "$WORKSPACE/data"
mkdir -p "$WORKSPACE/memory"

# 找最近N分钟修改的JSONL
# 使用时间戳标记文件来判断"最近"
MARKER_FILE="/tmp/.harvest-marker"
recent_files=$(find "$SESSIONS_DIR" -name "*.jsonl" -newer "$MARKER_FILE" 2>/dev/null)

# 更新时间戳标记（在找文件之后更新，下次以此为基准）
touch "$MARKER_FILE"

if [ -z "$recent_files" ]; then
    echo "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S'): no recent sessions (marker: $(stat -c %y $MARKER_FILE 2>/dev/null || echo 'new'))" >> "$HARVEST_LOG"
    exit 0
fi

echo "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S'): scanning files: $(echo $recent_files | wc -w) file(s)" >> "$HARVEST_LOG"

hits=""
for f in $recent_files; do
    # 提取user和assistant的text消息，跳过toolCall/toolResult/thinking
    # JSONL每行是一个JSON对象，提取message.content中type==text的内容
    extracted=$(jq -r '
        select(.type == "message") |
        .message |
        select(.role == "user" or .role == "assistant") |
        .content[]? |
        select(.type == "text") |
        .text
    ' "$f" 2>/dev/null | grep -E "$SIGNAL_WORDS" | head -20)

    if [ -n "$extracted" ]; then
        hits="${hits}\n### 来自 $(basename $f)\n${extracted}\n"
    fi
done

if [ -n "$hits" ]; then
    # 确保memory文件存在
    if [ ! -f "$MEMORY_FILE" ]; then
        echo "# $TODAY Daily Notes" > "$MEMORY_FILE"
        echo "" >> "$MEMORY_FILE"
    fi

    # 追加捞网内容
    {
        echo ""
        echo "### $(TZ=Asia/Shanghai date +%H:%M) - 🕸️ 心跳捞网"
        echo -e "$hits"
    } >> "$MEMORY_FILE"

    echo "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S'): harvested content to $MEMORY_FILE" >> "$HARVEST_LOG"

    # ── 向量化：将每条命中内容写入向量库 ──────────────────────────────────
    echo "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S'): vectorizing harvested content..." >> "$HARVEST_LOG"
    vector_count=0
    while IFS= read -r line; do
        # 跳过空行和来源标题行
        if [ -z "$line" ] || echo "$line" | grep -qE "^###|^---"; then
            continue
        fi
        # 跳过太短的行（少于10字符）
        if [ "${#line}" -lt 10 ]; then
            continue
        fi
        classify_and_remember "$line"
        vector_count=$((vector_count + 1))
    done <<< "$(echo -e "$hits")"
    echo "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S'): vectorized $vector_count entries" >> "$HARVEST_LOG"
    echo "harvested (vectorized: $vector_count)"
else
    echo "$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M:%S'): scanned $(echo $recent_files | wc -w) file(s), nothing to harvest" >> "$HARVEST_LOG"
    echo "nothing to harvest"
fi
