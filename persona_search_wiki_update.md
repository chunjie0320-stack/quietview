# 画像驱动的个性化搜索 Demo — 完整文档

> 本文记录「画像驱动的个性化搜索 Demo v3」的完整算法逻辑、测试用例、Persona API 使用规范及 Skill 打包说明。
> 
> **Demo 访问地址**：`http://33.230.16.210:8899/persona_demo_v3.html`（沙箱环境，需访问喵子的 OpenClaw 控制台）

---

## 一、Demo 概述

### 核心思路

同一搜索关键词（如"汉堡"），对不同用户画像返回不同排序结果：

- 白领女性 → 优先健康、有机食材
- 程序员 → 优先性价比、低价
- 在校学生 → 极致低价优先
- 中年商务 → 优先高品质、高档食材

### 技术路径

```
用户选择 → 触发 Persona RAG API → 获取真实标签 → 映射画像权重 → 商品评分排序 → 差异化结果展示
```

---

## 二、Persona 标签 API 规范

### ✅ 有效接口（RAG 语义搜索）

```
GET https://persona.sankuai.com/api/v2/ai/rag/dutvs/assets/searchAll
    ?query=<自然语言描述>
    &assetTypes=label
    &idType=1
```

**认证**：SSO Cookie（浏览器登录 persona.sankuai.com 后自动携带）

**返回示例**：
```json
{
  "data": {
    "results": [
      {
        "labelId": "12345",
        "labelName": "价格敏感用户",
        "similarityScore": 0.87,
        "labelDesc": "近30天内偏好低价商品的用户"
      }
    ]
  }
}
```

### ❌ 无效接口（对自然语言查询返回空结果）

```
PUT /api/v2/tcs/label/list   ← 仅支持精确 ID 查询，不支持自然语言
```

### 各用户的 Persona 查询词

| 用户 | 查询词列表 |
|------|-----------|
| 小美（白领女性）| `外卖偏好`, `健康饮食偏好`, `品质消费` |
| 阿强（程序员）| `价格敏感度`, `高频下单用户`, `外卖消费频次` |
| 学妹（在校学生）| `价格敏感度`, `学生消费`, `优惠券使用` |
| 老王（中年商务）| `高消费用户`, `品质偏好`, `商务消费` |

---

## 三、个性化评分算法

### 3.1 用户画像权重定义

```javascript
const USERS = {
  xiaomei: {
    name: '小美', emoji: '👩‍💼', desc: '白领女性',
    priceWeight: 0.3,   // 价格敏感度低
    healthWeight: 0.8,  // 高度关注健康
    qualityWeight: 0.7, // 注重品质
    labelQueries: ['外卖偏好', '健康饮食偏好', '品质消费'],
    categoryBonus: { '沙拉': 0.3, '轻食': 0.2 }
  },
  aqiang: {
    name: '阿强', emoji: '👨‍💻', desc: '程序员',
    priceWeight: 0.8,   // 高度价格敏感
    healthWeight: 0.3,
    qualityWeight: 0.5,
    labelQueries: ['价格敏感度', '高频下单用户', '外卖消费频次'],
    categoryBonus: { '汉堡': 0.15, '炸鸡': 0.1 }
  },
  xuemei: {
    name: '学妹', emoji: '👩‍🎓', desc: '在校学生',
    priceWeight: 0.9,   // 极致价格敏感
    healthWeight: 0.4,
    qualityWeight: 0.3,
    labelQueries: ['价格敏感度', '学生消费', '优惠券使用'],
    categoryBonus: { '奶茶': 0.1 }
  },
  laowang: {
    name: '老王', emoji: '👔', desc: '中年商务',
    priceWeight: 0.2,
    healthWeight: 0.6,
    qualityWeight: 0.8, // 极致品质偏好
    labelQueries: ['高消费用户', '品质偏好', '商务消费'],
    categoryBonus: { '沙拉': 0.15, '米饭': 0.1 }
  }
};
```

### 3.2 评分公式

```javascript
function scoreProduct(product, user) {
  let score = product.baseScore;  // 基础分 0.1~1.0
  
  // 健康加成：healthScore × healthWeight × 0.3
  score += product.healthScore * user.healthWeight * 0.3;
  
  // 价格惩罚：priceLevel(1~3) 越高 × priceWeight 越大 → 降权越多
  score -= (product.priceLevel - 1) * user.priceWeight * 0.25;
  
  // 品质加成：qualityScore × qualityWeight × 0.2
  score += product.qualityScore * user.qualityWeight * 0.2;
  
  // 品类偏好加成
  score += (user.categoryBonus[product.category] || 0);
  
  // 随机扰动（±0.05，模拟真实推荐系统的随机性）
  score += (Math.random() - 0.5) * 0.1;
  
  return Math.max(0, Math.min(1, score));
}
```

### 3.3 商品维度定义

每个 mock 商品携带以下属性：

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 商品名称 | 藜麦牛肉汉堡 |
| `price` | 价格（元）| 38 |
| `priceLevel` | 价格档次 1~3 | 2（中等）|
| `healthScore` | 健康分 0~1 | 0.85 |
| `qualityScore` | 品质分 0~1 | 0.8 |
| `baseScore` | 基础分 0~1 | 0.7 |
| `category` | 品类 | 汉堡 |
| `tags` | 标签数组 | `['高蛋白', '低脂']` |

---

## 四、测试用例

### 4.1 搜索词：「汉堡」

**预期**：健康用户排出低脂/全谷物选项，价格敏感用户排出低价套餐

| 排名 | 小美（健康优先）| 阿强（价格优先）| 学妹（极致省钱）| 老王（品质优先）|
|------|----------------|----------------|----------------|----------------|
| 🥇 1 | 藜麦牛肉汉堡 ¥38（健康0.9）| 麦辣鸡腿堡套餐 ¥19.9 | 麦辣鸡腿堡套餐 ¥19.9 | 招牌芝士厚牛堡 ¥42 |
| 🥈 2 | 黑麦全谷物素食堡 ¥35 | 经典双层牛肉堡 ¥25 | 经典双层牛肉堡 ¥25 | 藜麦牛肉汉堡 ¥38 |
| 🥉 3 | 经典双层牛肉堡 ¥25 | 藜麦牛肉汉堡 ¥38 | 招牌芝士厚牛堡 ¥42 | 黑麦全谷物素食堡 ¥35 |

### 4.2 搜索词：「奶茶」

| 排名 | 小美 | 阿强 | 学妹 |
|------|------|------|------|
| 🥇 1 | 抹茶燕麦拿铁 ¥28（健康茶饮）| 原味珍珠奶茶大杯 ¥6 | 原味珍珠奶茶大杯 ¥6 |
| 🥈 2 | 黑糖珍珠波波奶茶 ¥22 | 黑糖珍珠波波奶茶 ¥22 | 芋泥爆珠珍珠 ¥18 |
| 🥉 3 | 原味珍珠奶茶大杯 ¥6 | 芋泥爆珠珍珠 ¥18 | 黑糖珍珠波波奶茶 ¥22 |

### 4.3 搜索词：「沙拉」

| 排名 | 小美 | 老王 | 学妹 |
|------|------|------|------|
| 🥇 1 | 牛油果鸡胸肉沙拉 ¥48（双重加成）| 帝王蟹沙拉 ¥88（顶级品质）| 蔬菜水果沙拉 ¥32（最低价）|
| 🥈 2 | 蔬菜水果沙拉 ¥32 | 牛油果鸡胸肉沙拉 ¥48 | 牛油果鸡胸肉沙拉 ¥48 |

### 4.4 搜索词：「炸鸡」

| 排名 | 小美 | 阿强 |
|------|------|------|
| 🥇 1 | 香烤鸡腿排（低脂烤制）| 香脆炸鸡桶10件 ¥39.9（超值）|
| 🥈 2 | 麦辣鸡腿堡套餐 | 麦辣鸡腿堡套餐 ¥19.9 |

---

## 五、Demo 页面结构

### 布局说明（三栏）

```
┌─────────────┬─────────────────────────────┬──────────────┐
│ 左栏：APP   │ 中栏：画像控制              │ 右栏：行为   │
│ 模拟预览    │                              │ 数据记录     │
│             │ [👩‍💼小美][👨‍💻阿强][👩‍🎓学妹][👔老王] │             │
│ ┌─────────┐ │                              │ ■ 行为记录   │
│ │ 🍜美团  │ │ Persona 画像标签（真实接口）│              │
│ │ 外卖    │ │ [标签卡片...]                │ ■ 会话统计   │
│ │─────────│ │                              │ 搜索 商品    │
│ │ 🔍搜索  │ │ 偏好权重可视化              │ 次数 点击    │
│ │─────────│ │ 健康 ████░░ 0.8             │              │
│ │ 商品列表 │ │ 价格 ██░░░░ 0.3             │ ■ 偏好推断   │
│ │         │ │ 品质 ████░░ 0.7             │              │
│ │         │ │                              │              │
│ │─────────│ │ 快速搜索: 汉堡 奶茶 沙拉   │              │
│ │🏠🔍🛒👤│ │ 行为增强推荐                │              │
│ └─────────┘ │                              │              │
└─────────────┴─────────────────────────────┴──────────────┘
```

### 手机模拟区规格
- 外框：270×自适应，黑色圆角边框，border-radius: 40px
- 屏幕：246px 宽 × 534px 高（iPhone 14 Pro 比例 ~2.17:1）
- 顶部刘海：80px × 8px
- 底部导航：首页/发现/订单/我的

---

## 六、Skill 文件

### 文件清单

| 文件 | 说明 | 大小 |
|------|------|------|
| `persona-search-demo-skill/SKILL.md` | Skill 主说明文档 | ~7KB |
| `persona-search-demo-skill/references/persona_demo_v3.html` | Demo 页面（含全部代码）| ~80KB |
| `persona-search-demo-skill/references/session_persona_search_demo_20260322.jsonl` | 完整对话 Session | ~1.5MB |
| `persona-search-demo-skill.zip` | 打包文件 | 640KB |

### 安装方式

将 `persona-search-demo-skill/` 目录放到 `~/.openclaw/skills/` 下即可激活。

### Skill 类型分类（依据 skill 规范）

| 类型 | 对应规范分类 |
|------|-------------|
| 数据获取与分析 | 类型3：接入 Persona API 获取用户画像标签 |
| 库与 API 参考 | 类型1：Persona label search API 使用规范 |
| 业务流程自动化 | 类型4：个性化搜索 Demo 生成流程 |

---

## 七、Session 记录

**Session 文件**：`session_persona_search_demo_20260322.jsonl`  
**消息数**：293 条  
**时间范围**：2026-03-22（完整对话过程）  
**内容涵盖**：需求分析 → API 探索 → Demo v1/v2/v3 迭代 → 手机尺寸优化

---

*本页由喵子自动生成 · 2026-03-22*
