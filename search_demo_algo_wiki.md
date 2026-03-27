# 搜索demo算法逻辑整理

> Demo 地址：persona_demo_v5.html（画像驱动的个性化搜索 Demo）
> 核心理念：**同词不同序** —— 相同关键词，不同用户画像，返回不同排序结果。

---

## 一、整体架构

```
用户画像（Persona标签 + 偏好权重）
        ↓
  关键词召回（多字段匹配）
        ↓
  个性化排序（scoreProduct 打分）
        ↓
  结果展示 + 跨用户对比
```

---

## 二、用户画像模型

每个用户由三个偏好权重 + 品类加成构成：

| 字段 | 说明 | 取值范围 |
|------|------|---------|
| `priceWeight` | 价格敏感度（越高越倾向低价） | 0.0 ~ 1.0 |
| `healthWeight` | 健康偏好（越高越倾向低卡/高蛋白） | 0.0 ~ 1.0 |
| `qualityWeight` | 品质偏好（越高越倾向高评分） | 0.0 ~ 1.0 |
| `categoryBonus` | 对特定品类的额外加成（来自历史行为偏好） | 0.0 ~ 0.3 |
| `labelQueries` | Persona 真实标签查询词（用于从画像接口拉取标签） | 字符串数组 |

### 示例用户画像

| 用户 | 价格敏感 | 健康偏好 | 品质偏好 | 品类加成 |
|------|---------|---------|---------|---------|
| 小美（白领女性） | 0.3 | 0.8 | 0.7 | 沙拉+0.3、轻食+0.2 |
| 阿强（程序员） | 0.8 | 0.3 | 0.5 | 汉堡+0.15、炸鸡+0.1 |
| 学妹（在校学生） | 0.9 | 0.4 | 0.3 | 奶茶+0.1 |
| 老王（商务人士） | 0.2 | 0.6 | 0.8 | 沙拉+0.15、米饭+0.1 |

---

## 三、商品数据结构

每个商品包含以下字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 商品名称 | 藜麦牛肉汉堡 |
| `shop` | 商家名称 | 绿厨坊 |
| `price` | 价格（元） | 38 |
| `priceLevel` | 价格档位（1=低价 / 2=中等 / 3=高端） | 2 |
| `healthScore` | 健康分（0~1，越高越健康） | 0.9 |
| `qualityScore` | 品质分（0~1，反映评分/口碑） | 0.8 |
| `baseScore` | 基础热度分（0~1，反映商品本身的通用热度） | 0.70 |
| `category` | 品类（汉堡/奶茶/沙拉/炸鸡/米饭/披萨） | 汉堡 |
| `tags` | 商品特征标签 | ['高蛋白','低卡'] |
| `searchKeys` | 搜索命中词（用于召回匹配） | ['汉堡','牛肉'] |

---

## 四、召回逻辑

搜索时对全量商品做多字段模糊匹配，命中任一条件即纳入候选集：

```javascript
const matched = PRODUCTS.filter(p =>
  p.name.includes(kw)          // 商品名包含关键词
  || p.category.includes(kw)   // 品类匹配
  || p.searchKeys.some(k => k.includes(kw) || kw.includes(k))  // 搜索词双向包含
  || p.tags.some(t => t.includes(kw))  // 标签匹配
);
```

**设计特点：**
- 双向包含匹配（`k.includes(kw) || kw.includes(k)`），兼顾短词和长词
- 多字段并联，召回率优先
- 当前为内存全量扫描，适合 Demo 场景

---

## 五、个性化排序算法（核心）

### 5.1 打分公式

```javascript
function scoreProduct(product, user) {
  let s = product.baseScore;

  // 健康加分：用户健康偏好 × 商品健康分 × 系数0.3
  s += product.healthScore * user.healthWeight * 0.3;

  // 价格惩罚：价格档位越高，价格敏感用户扣分越多
  s -= (product.priceLevel - 1) * user.priceWeight * 0.25;

  // 品质加分：用户品质偏好 × 商品品质分 × 系数0.2
  s += product.qualityScore * user.qualityWeight * 0.2;

  // 品类加成：来自用户历史行为的品类偏好
  s += (user.categoryBonus[product.category] || 0);

  // 随机扰动：防止排序完全固定，模拟真实噪声
  s += (Math.random() - 0.5) * 0.06;

  return Math.max(0, Math.min(1, s));  // 截断到 [0, 1]
}
```

### 5.2 各因子权重对比

| 因子 | 最大贡献 | 说明 |
|------|---------|------|
| baseScore | ~0.82 | 商品基础热度，占主导 |
| 健康加分 | +0.285（1×1×0.3）| 健康重度用户对高健康分商品提升明显 |
| 价格惩罚 | -0.50（2×1×0.25）| 极度价格敏感用户对高端商品大幅降权 |
| 品质加分 | +0.19（1×1×0.2）| 相对较小，作为辅助因子 |
| 品类加成 | +0~0.30 | 强个性化信号，上限最高 |
| 随机扰动 | ±0.03 | 引入轻微随机性 |

### 5.3 「同词不同序」效果示例

以搜索「沙拉」为例：

| 商品 | 小美（健康优先）排序 | 阿强（价格优先）排序 |
|------|------|------|
| 牛油果鸡胸肉沙拉（¥48，健康0.95） | 🥇 第1 | 🥉 第3 |
| 蔬菜水果沙拉（¥32，健康0.85） | 🥈 第2 | 🥇 第1 |
| 帝王蟹沙拉（¥88，品质0.95） | 🥉 第3 | 🥈 第2 |

---

## 六、首页推荐逻辑

首页「为你推荐」使用相同的 `scoreProduct` 函数，对全量商品打分排序，取 Top 8 展示：

```javascript
function renderHomeProducts() {
  const allScored = PRODUCTS
    .map(p => ({ ...p, score: scoreProduct(p, currentUser) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 8);
}
```

**无需关键词输入，纯画像驱动的推荐。**

---

## 七、跨用户对比模块

搜索后自动生成「跨用户对比」面板，将同一关键词在4个用户下的 Top3 结果并列展示，直观呈现排序差异：

```javascript
function updateComparison(kw, matched) {
  Object.entries(USERS).map(([uid, u]) => {
    const top = matched
      .map(p => ({ ...p, score: scoreProduct(p, u) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  });
}
```

---

## 八、行为偏好推断

用户点击商品后，系统实时统计行为，推断偏好：

- 统计各品类点击次数 → 生成「偏好XX(N次)」标签
- 若低价商品（priceLevel=1）点击 ≥ 2 次 → 标注「价格敏感」

> 当前为 Demo 内存态，刷新后重置。生产环境需持久化到用户行为库。

---

## 九、Persona 真实标签接入

每个用户切换时，调用 Persona 真实接口拉取画像标签：

```
GET https://persona.sankuai.com/api/v2/ai/rag/dutvs/assets/searchAll
  ?query=<labelQuery>
  &assetTypes=label
  &idType=1
```

- 每个用户有 2~3 个 `labelQueries`，并行拉取
- 结果展示在「Persona 画像标签」面板
- 需登录 persona.sankuai.com 后才能获取真实数据

---

## 十、扩展方向

| 方向 | 当前实现 | 生产建议 |
|------|---------|---------|
| 召回 | 内存全量遍历 | 倒排索引 / ES |
| 排序 | 线性加权公式 | LTR（Learning to Rank）模型 |
| 用户画像 | 静态预设权重 | 实时行为流计算 |
| 品类加成 | 硬编码 | 从点击/购买日志实时计算 |
| 随机扰动 | 固定幅度 ±0.03 | ε-greedy 探索策略 |
| A/B测试 | 无 | 按用户分桶实验不同权重 |
