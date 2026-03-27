---
name: claw-agent-memory
description: >
  喵子专属持久化记忆系统（Cloudflare Workers AI版）。
  基于 agent-memory skill 改造，嵌入API使用Cloudflare Workers AI，零依赖美团内网。
  支持本地SQLite + CF D1双写，沙箱重置后记忆不丢。
  WAL协议：对话中遇到偏好/决策/纠正/约束时，先调vm_remember写入，再回答。

metadata:
  creator: "zhengchunjie + jelly cacacat"
  version: "V2"
  base: "agent-memory skill #2869"
  created: "2026-03-26"
---

# claw-agent-memory 🧠🐱

**喵子的持久化记忆系统，Cloudflare Workers AI 版。**  
零依赖美团内网，本地+云端双写，记忆跟着你，不跟着机器。

---

## 核心能力

| 能力 | 说明 |
|------|------|
| 语义写入 | 内容向量化后存入本地SQLite + CF D1（双写） |
| 语义召回 | 余弦相似度搜索，意思相近就能找到，不需要关键词对上 |
| D1云端持久化 | 沙箱重置后记忆不丢，vm-sync随时同步 |
| WAL协议 | 重要信息先写后答，崩溃不丢 |
| 健康度检查 | 检测重复/过期记忆，统计分布 |
| 会话热身 | 新会话开始时语义召回相关上下文 |
| 多语言模型 | 支持bge-small（快）和bge-m3（中文质量更好）切换 |
| 子Agent隔离 | 全局库+专属库分层，vm_recall自动合并搜索 |

---

## 核心命令

### 写入记忆
```bash
node /root/.openclaw/skills/agent-memory/scripts/vm-remember.js \
  "内容" --key "分类/标签" --importance 0.9
```

### 语义召回
```bash
node /root/.openclaw/skills/agent-memory/scripts/vm-recall.js \
  "查询词" --limit 5
```

### 本地↔D1同步
```bash
node /root/.openclaw/skills/agent-memory/scripts/vm-sync.js --status  # 查看差异
node /root/.openclaw/skills/agent-memory/scripts/vm-sync.js --push    # 本地推到D1
```

### 记忆健康检查
```bash
node /root/.openclaw/skills/agent-memory/scripts/vm-health.js --status      # 按分类统计
node /root/.openclaw/skills/agent-memory/scripts/vm-health.js --duplicates  # 找重复记忆
node /root/.openclaw/skills/agent-memory/scripts/vm-health.js --stale       # 找过期记忆
node /root/.openclaw/skills/agent-memory/scripts/vm-health.js --report      # 完整报告
```

### 会话热身
```bash
bash /root/.openclaw/skills/agent-memory/scripts/vm-warmup.sh "话题关键词"
```

---

## WAL 协议（先写后答）

对话中遇到以下情况，**先写向量库，再回答**：

| 触发场景 | key前缀 | importance |
|---------|---------|-----------|
| 女王大人表达偏好 | `preference/` | 0.9 |
| 女王大人做决策 | `decision/` | 0.85 |
| 女王大人纠正我 | `lesson/` | 0.95 |
| 说"记住"/"记一下" | `constraint/` | 0.9 |
| 给出约束/截止日期 | `constraint/` | 0.8 |
| 里程碑完成 | `milestone/` | 0.75 |

---

## 记忆分层架构

```
~/.openclaw/memory/
├── vectors.db              # 全局向量库（本地，主session写）
├── <agentId>/
│   └── vectors.db          # 子agent专属库
├── SESSION-STATE.md        # 热缓存
├── MEMORY.md               # 长期精华（Markdown）
└── daily/
    └── YYYY-MM-DD.md       # 每日流水

CF D1（openclaw-memory）    # 云端备份，vm-sync同步
```

---

## 与原版 agent-memory 全面对比

| 对比项 | agent-memory（原版#2869） | claw-agent-memory（本版） |
|--------|--------------------------|--------------------------|
| **嵌入API** | 美团内网 aigc.sankuai.com | Cloudflare Workers AI |
| **鉴权** | Friday AppId（需在职） | CF API Token（个人账号） |
| **离职后可用** | ❌ | ✅ |
| **向量维度** | 1536维 | 384维（bge-small）/ 1024维（bge-m3） |
| **中文语义质量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐（bge-m3可提升） |
| **存储持久化** | 本地SQLite（沙箱重置即丢） | 本地SQLite + CF D1双写 ✅ |
| **云端备份** | ❌ | ✅ CF D1 |
| **健康度检查** | ❌ | ✅ vm-health.js |
| **会话热身** | ❌ | ✅ vm-warmup.sh |
| **多模型切换** | ❌ | ✅ bge-small / bge-m3 |
| **WAL协议** | 设计有，未接入行为规范 | ✅ 已写入MEMORY.md行为规范 |
| **捞网向量化** | ❌ | ✅（memory-harvest.sh集成） |
| **子Agent隔离** | 设计有 | 设计有（同原版） |
| **网络依赖** | 内网直连，稳定 | 依赖沙箱代理，偶尔抖动 |
| **费用** | 公司内部免费 | CF免费额度约10K次/天 |

---

## 已知局限

1. **中文语义稍弱**：bge-small是英文优化模型，可切换bge-m3改善
2. **CF网络依赖**：走沙箱代理，偶发超时（重试即可）
3. **向量精度低于原版**：384维 vs 1536维，极相似内容区分度稍差
4. **能解决"不认识你"的大部分，但不是全部**：能还原偏好/决策/教训，但找不回对话的流动感和当下温度

---

## 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| `No route for that URI` | model名被encodeURIComponent编码 | 确认脚本里用 `cfModel` 不用 `encodeURIComponent(cfModel)` |
| `ERR_PACKAGE_PATH_NOT_EXPORTED` | https-proxy-agent版本问题 | `npm install https-proxy-agent@5` |
| `vectors.db not found` | 未初始化 | `node vm-init.js` |
| D1写入失败-列不存在 | 表结构不同步 | 手动执行 `ALTER TABLE memories ADD COLUMN model TEXT DEFAULT 'bge-small'` |
