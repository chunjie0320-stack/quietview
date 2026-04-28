# 任务中心 AI Native Demo

> 美团营销任务中心 AI Native 改造的交互 Demo —— 基于用户画像实现千人千面的任务会场。

## 🚀 本地运行

直接用浏览器打开即可，无需任何服务端：

```
双击打开 demo/task_center_v3.html
```

> 推荐使用 Chrome / Edge，分辨率 ≥ 1440px 体验最佳。Demo 内含 AI 对话功能，需美团内网环境访问 Friday API。

## 📁 目录结构

```
task-center-project/
├── README.md                           # 本文件
├── demo/
│   └── task_center_v3.html             # 主 Demo（单文件 HTML，可直接浏览器打开）
├── design-system/                      # 设计系统文档
│   ├── SKILL.md                        # task-center-design Skill 完整定义
│   ├── task-atoms-snapshot.yaml        # 原子化要素字典
│   ├── task-visual-rules-snapshot.yaml # 视觉规则
│   └── ui-spec-summary.md             # UI 规范总结
├── references/                         # 参考实现
│   ├── sign-in-component.css           # 高达签到组件样式
│   └── sign-in-component.js            # 高达签到组件逻辑
└── screenshots/                        # Demo 截图
    ├── v3-sign-closeup.png             # 签到组件特写
    ├── v3-sign-fixed.png               # 签到修复版
    ├── v3-trio-sign-upgrade.png        # 三人群差异化会场
    └── v3-iphone-sign.png             # iPhone 端效果
```

### 各目录说明

| 目录 | 用途 |
|------|------|
| `demo/` | 可运行的交互 Demo，浏览器直接打开 |
| `design-system/` | AI 生成营销组件所依据的设计系统文档，Skill + 原子要素 + 视觉规则 + UI规范 |
| `references/` | 从高达素材库提取的真实线上组件代码，作为样式参考基准 |
| `screenshots/` | Demo 各阶段截图，用于展示和评审 |

## 🎨 设计系统

设计系统由三层文档构成，自底向上：

1. **task-atoms-snapshot.yaml**（原子要素字典）
   - 定义最小粒度的 UI 要素：签到日历、进度条、优惠券卡片、红包雨等
   - 每个原子包含：名称、适用意图、视觉描述、交互规则

2. **task-visual-rules-snapshot.yaml**（视觉规则）
   - 定义颜色、字号、间距、圆角、动效等全局视觉规范
   - 确保不同原子组合后风格一致

3. **ui-spec-summary.md**（UI 规范总结）
   - 串联原子与规则，说明组件组合方式、布局逻辑、响应式策略
   - 面向 AI Agent 的 Prompt 友好格式，便于自动生成代码

**SKILL.md** 则是 AI Agent 的完整指令文件，定义了如何根据活动意图（签到/下单/助力/浏览等）自动调用上述三层文档生成符合美团营销视觉体系的 C 端组件代码。

## ⚙️ 技术说明

- **架构**：单文件 HTML，内嵌全部 CSS + JavaScript，零依赖零构建
- **AI 对话**：接入 Friday API（AppId = `22037445065107296341`），支持流式对话，用于运营工作台的 AI 助手功能
- **用户画像**：内置多个虚拟用户 Persona（王小花-流失召回、李大明-价格敏感、张梅-品类探索），点击切换即可预览差异化会场
- **双视角**：
  - **用户视角** — 模拟 C 端用户看到的任务会场（签到有礼、优惠券、AI推荐文案等）
  - **运营工作台** — 运营人员配置界面 + AI 对话助手

## 📋 版本

- Demo 版本：v3（2026-04-14）
- 基于 task-center-design Skill 生成
