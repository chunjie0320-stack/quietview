---
name: trend-topic-generator
description: 热点选题生成器。给定行业/场景，自动抓取小红书热点内容并生成选题建议，输出 HTML 可视化 + Markdown 选题卡。适用于运营制定内容主题、会场策划、选题发散等场景。触发条件：用户说"帮我找XXX的热点/选题/内容方向"、"我想做XXX内容会场"、"帮我分析XXX行业的热点"、"生成选题"、"内容选题"、"热点洞察"等。核心输入：会场目标（商业化/内容型，唯一必填）+ 行业/场景（必填）+ 时间季节/品类/受众（均选填）。数据源：catclaw-search + 小红书 playwright+cookie。
---

# trend-topic-generator

运营选题灵感工具：从"我不知道该做什么主题"→"这几个选题可以考虑"。

---

## 输入规格

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| **会场目标** | ✅ 必填 | `commercial`（商业化/带货转化）或 `content`（内容型/心智种草） | "我想做春季美食商业化会场" |
| **行业/场景** | ✅ 必填 | 自然语言描述即可 | 北京美食、亲子活动、美妆护肤 |
| 时间/季节 | 选填 | 有→约束范围；无→系统默认当前时节 | 春季、五一、母亲节 |
| 品类方向 | 选填 | 有→约束品类；无→全品类发散 | 咖啡、甜品、亲子餐厅 |
| 用户人群 | 选填 | 有→约束受众；无→不限 | 年轻女性、上班族、宝妈 |

**会场目标是唯一必填项**，因为它决定后续所有数据分析和选题生成的策略走向：
- **商业化**：有品类/SKU对应，目的是转化下单，选题强调"买什么/怎么买/值不值"
- **内容型**：以情绪/故事/话题为主，目的是心智占领，选题强调"情感共鸣/趋势讨论"

---

## 逆向保障机制

| 层次 | 场景 | 处理方式 |
|------|------|----------|
| **输入层** | 行业太宽泛 | 暂由 Claude 提示细化（后续可加验证） |
| **数据层** | catclaw 返回空 | data_quality 标记 empty，触发扩词重试 |
| **数据层** | XHS Cookie 过期 | 明确报告 cookie_expired，不静默跳过 |
| **数据层** | 数据量 < 10条 | 自动扩词换引擎（baidu）重试，补充差量 |
| **数据层** | 扩词后仍 < 5条 | 输出红色警告"行业太冷门，建议换关键词" |
| **数据层** | 内容质量差 | 过滤标题<4字、纯英文、广告关键词 |
| **数据层** | XHS 深度抓取全失败 | 分析报告标注"仅基于搜索列表，无评论数据" |
| **输出层** | 选题数量 < 3个 | HTML+MD 均显示警示 banner |
| **输出层** | HTML div 不平衡 | 自查报错并以非0退出，便于调用方检测 |
| **输出层** | HTML/MD 任一生成失败 | 各自独立错误，不互相影响 |

所有警告和质量指标汇总在 `data_quality` 字段，透传给分析层（Claude）和输出层（HTML banner）。

---

## 三阶段执行流程

### Phase 1：语义解析 + 热点抓取

1. 从用户自然语言输入中解析出结构化参数（industry / goal / season / category / audience）
2. 运行抓取脚本：
   ```bash
   # 标准模式（搜索列表）
   python3 <skill_dir>/scripts/fetch_trends.py \
     --industry "北京美食" \
     --goal commercial \
     --season "春季" \
     --audience "年轻女性"

   # 深度模式（搜索列表 + Top3帖子正文+评论）
   python3 <skill_dir>/scripts/fetch_trends.py \
     --industry "北京美食" \
     --goal commercial \
     --season "春季" \
     --deep-xhs 3
   ```
3. 脚本自动：
   - 生成多条搜索词（商业化/内容型各一套策略）
   - **Phase 1a**：catclaw-search（Bing）+ XHS playwright搜索列表（标题/作者/点赞/**URL**）
   - **Phase 1b**（`--deep-xhs N`时）：对XHS点赞Top N帖子调用xhs-fetcher深度抓取正文+评论
   - 输出 JSON 到 `~/.openclaw/logs/trends_<industry>_<timestamp>.json`

> ⚠️ catclaw-search 脚本路径参考 catclaw-search skill；若 skill 路径不存在，改用 Claude 直接调用 web_search + catclaw-search skill。

### Phase 2：分析 + 选题生成（Claude 执行）

读取 Phase 1 输出的 JSON，进行以下分析（由 Claude 直接完成，不依赖额外脚本）：

**数据字段说明**：
- `results`：catclaw-search + XHS 搜索列表（标题/作者/点赞/URL），用于宏观话题洞察
- `xhs_deep_results`：XHS 深度抓取（正文/评论），若存在则用于微观痛点挖掘

**分析步骤**：

1. **去重 + 聚类**：合并相似内容，识别重复话题
2. **热度信号提取**：找出高频词、带热度数据的内容（浏览量/互动量等）
3. **评论情绪分析**（当 `xhs_deep_results` 非空时）：
   - 提取评论中的高频词、情绪倾向（正面/负面/中性）
   - 识别用户真实痛点（"好难找/太贵/想要但找不到"等）
   - 评论里的需求信号可直接转化为选题角度
4. **按目标分策略**：
   - 商业化：筛选"有品类对应+可带货性强"的热点
   - 内容型：筛选"情绪共鸣强+传播力高"的热点
5. **生成选题**：每个热点生成：
   - 选题标题（主方向）
   - 热度信号描述
   - 数据支撑（有数字更好）
   - 商业化角度 / 内容角度（按 goal 选择）
   - 3-5条示例标题
   - 气泡图坐标（commercial_score 0-100 / heat_score 0-100 / content_difficulty 0-100）
5. **整体洞察**：1-2段总结，点出行业最值得抓的机会

将分析结果写入：`~/.openclaw/logs/trends_analysis_<industry>_<timestamp>.json`

分析结果 JSON 格式：
```json
{
  "meta": { "industry": "...", "goal": "...", "season": "...", "category": "...", "audience": "..." },
  "topics": [
    {
      "title": "选题方向名",
      "heat_signal": "话题热度描述",
      "data_support": "具体数据",
      "commercial_angle": "（商业化时填）",
      "content_angle": "（内容型时填）",
      "examples": ["示例标题1", "示例标题2", "示例标题3"],
      "heat_score": 80,
      "commercial_score": 75,
      "content_difficulty": 40,
      "group": "分组名"
    }
  ],
  "insights": { "summary": "整体洞察文字" }
}
```

### Phase 3：输出生成

运行输出脚本，生成 HTML + Markdown 双输出：

```bash
python3 <skill_dir>/scripts/generate_output.py \
  --data ~/.openclaw/logs/trends_analysis_<industry>_<timestamp>.json \
  --out-dir /root/.openclaw/workspace
```

脚本输出：
- `topic_report_<industry>_<timestamp>.html`：气泡图 + 选题卡可视化
- `topic_cards_<industry>_<timestamp>.md`：纯文字选题卡（复制粘贴友好）

HTML 生成后必须执行 div depth 自查（脚本内置，检查 final_depth=0）。

---

## 数据源说明

### 双层 XHS 抓取策略

| 层次 | 来源 | 能力 | 说明 |
|------|------|------|------|
| catclaw-search（Bing） | 始终执行 | 搜索引擎结果 | 通用热点内容，稳定不依赖登录 |
| **Phase 1a** XHS 搜索列表 | Cookie 文件存在时 | 标题/作者/点赞/URL | playwright headless + cookie 注入，直连站内搜索 |
| **Phase 1b** XHS 深度抓取 | `--deep-xhs N > 0` 时触发 | **正文 + 评论（含回复）** | xhs-fetcher.mjs（Chrome CDP），对点赞 Top N 帖子深度挖掘 |

**两层的价值差异**：
- Phase 1a（广度）：快速掌握话题全貌，知道什么方向热
- Phase 1b（深度）：理解用户真实说了什么、痛点是什么、评论中的真实情绪

**启用深度抓取**（需 Chrome CDP 登录态）：
```bash
python3 fetch_trends.py --industry "北京美食" --goal commercial --deep-xhs 3
```

**深度抓取前置条件**：
1. xhs-fetcher skill 已安装（`~/.openclaw/skills/xhs-fetcher/`）
2. skill 目录下有 `node_modules/playwright`：
   ```bash
   cd ~/.openclaw/workspace/skills/trend-topic-generator
   npm install playwright sharp
   ```
3. Chrome 已有小红书登录态（`~/.xhs-browser-chrome-data/`）

> 首次深度抓取若 Chrome 无登录态，xhs-fetcher 会自动启动 Chrome 等待登录（约60秒）。

**文件路径**：
- Cookie 文件：`~/.openclaw/xiaohongshu-cookies.json`（a1 + web_session，有效期数天~数周）
- 搜索脚本：`~/.openclaw/workspace/scripts/xhs-fetch-with-cookie.py`（已支持返回 URL）
- 深度抓取 Skill：`~/.openclaw/skills/xhs-fetcher/scripts/run.sh`

---

## 交付规则（严格遵守）

- 上班时间：发文件路径，女王大人下载本地打开
- 在家时：发 HTML 截图
- **不得**通过大象 `message(media=文件)` 直接推送文件
- 汇报格式：先说结论（X个选题方向，Top3是...），再给路径

---

## 相关文件参考

- `references/pipeline.md`：完整 8 步流水线设计文档（含步骤③~⑧待开发部分）
- `references/data-strategy.md`：商业化 vs 内容型的数据源策略差异详解
