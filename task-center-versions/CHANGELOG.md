# Task Center Demo — 版本记录

## 版本规范
- 每个版本归档一份完整HTML到 `task-center-versions/` 目录
- 文件名格式：`task_center_v{版本号}_{描述}.html`
- 当前工作文件始终为：`/root/.openclaw/workspace/task_center_v2.html`
- **修改前必须备份**（子agent铁律：先cp再动手）
- 原始bak文件保留在 `raw-backups/` 目录，按时间戳可追溯

---

## 版本线路图

```
V0 (39KB)  → V1.0 (45KB) → V1.5 (100KB) → V2.0 (167KB) → V2.5 (160KB) → V3.0 (188KB)
原始demo     基础框架       策略卡+监控骨架   完整功能        画像差异化       iPhone模拟器
2026-04-09   04-13 11:31    04-13 16:02      04-13 21:46     04-13 23:15      04-14 00:18
```

---

## V3.0 — 2026-04-14 00:18（当前版本 ✅）

**文件**：`task_center_v3.0_monitor_redesign.html`（5619行，188KB）

**新增**：
- 监控页重构：iPhone模拟器（Dynamic Island+状态栏+Home Indicator）
- venue风格C端页面（Banner→券包横滚→AI推荐区→商家卡片）
- 三画像数据驱动切换（muPersonas数组 + fade动效160ms/300ms）
- 运营视角四卡片网格（任务概览/执行状态/AI建议/行为预警）
- 监控页默认展示用户视角

**待办**：
- [ ] "玩法生产"页面调整（待女王大人确认具体需求）

---

## V2.5 — 2026-04-13 23:15

**文件**：`task_center_v2.5_persona_diff.html`（~4780行，160KB）

**新增**：
- C端画像差异化：王小花🧡流失召回 / 李大明💰价格敏感 / 张梅🔍品类探索
- 三手机并排布局（trio-phones-container flex）
- 运营视角内嵌用户视角子Tab三画像推送预览
- 监控页Tab顺序反转（用户视角优先）

---

## V2.0 — 2026-04-13 21:46（里程碑 ⭐）

**文件**：`task_center_v2.0_final.html`（4888行，167KB）

**核心功能**：
- AI对话式维度收集（Friday LongCat-Flash API）
- 四维度策略配置：目标/周期/人群/资产
- 自然语言策略卡（玩法流程+AI选择依据+激励策略+阶梯奖励）
- 执行参数区块（7个ep-*字段）+ 预算大进度条
- 监控页：运营视角+用户视角双Tab
- C端用户视角：王小花五子Tab（D1/D3/D5/D7/D5召回）
- AI动态建议卡 + 行为预警弹窗
- 二次确认Modal启动

---

## V1.5 — 2026-04-13 16:02

**文件**：`task_center_v1.5_strategy_monitor.html`（~2800行，100KB）

**核心功能**：
- 6维要素卡（🔴🟡🟢状态灯）+ 进度条
- 策略卡骨架（基础信息+策略推理）
- 监控页骨架（4张指标卡+运营/用户Tab）
- 用户视角3部手机（原始版：李小雨/王芳/张梅）

---

## V1.0 — 2026-04-13 11:31

**文件**：`task_center_v1.0_initial.html`（45KB）

**核心功能**：
- AI对话+右侧维度面板基础结构
- 示例卡片快速填充
- Friday API接入

---

## V0 — 2026-04-09

**文件**：`task_center_v0_demo_original.html`（39KB）

**说明**：最早的AI Native任务中心概念demo

---

## 历史分支（已归档）

| 文件 | 大小 | 说明 |
|------|------|------|
| `task_center_branch_v3_c-end.html` | 137KB | V3分支：C端行为事件修正+五一签到九宫格 |
| `task_center_branch_v4_early.html` | 74KB | V4分支：早期独立探索 |
| `task_center_ops_config_standalone.html` | 26KB | 运营配置页独立版 |

---

## 原始备份

`raw-backups/` 目录保留了所有25个时间戳备份文件，可按时间精确回滚。

---

_版本管理规则：改之前备份，改之后归档，回滚有据可查。_
