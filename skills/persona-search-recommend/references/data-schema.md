# Data Schema

## USERS — 用户 Persona 对象

```js
const USERS = {
  xiaomei: {
    name: '小美', emoji: '👩‍💼', desc: '白领女性',
    priceWeight: 0.3,    // 价格敏感度（0=不在乎价格，1=极度敏感）
    healthWeight: 0.8,   // 健康偏好（0=无所谓，1=只选健康）
    qualityWeight: 0.7,  // 品质偏好（0=随便，1=只选高分商家）
    labelQueries: ['外卖偏好', '健康饮食偏好', '品质消费'],  // 画像标签展示用，不影响算法
    categoryBonus: { '沙拉': 0.3, '轻食': 0.2 }            // 品类额外加成
  },
  aqiang: {
    name: '阿强', emoji: '👨‍💻', desc: '程序员',
    priceWeight: 0.8, healthWeight: 0.3, qualityWeight: 0.5,
    labelQueries: ['价格敏感度', '高频下单用户', '外卖消费频次'],
    categoryBonus: { '汉堡': 0.15, '炸鸡': 0.1 }
  },
  xuemei: {
    name: '学妹', emoji: '👩‍🎓', desc: '在校学生',
    priceWeight: 0.9, healthWeight: 0.4, qualityWeight: 0.3,
    labelQueries: ['价格敏感度', '学生消费', '优惠券使用'],
    categoryBonus: { '奶茶': 0.1 }
  },
  laowang: {
    name: '老王', emoji: '👔', desc: '商务人士',
    priceWeight: 0.2, healthWeight: 0.6, qualityWeight: 0.8,
    labelQueries: ['高消费用户', '品质偏好', '商务消费'],
    categoryBonus: { '沙拉': 0.15, '米饭': 0.1 }
  }
};
```

## PRODUCTS — 商品数组字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | number | 唯一 ID |
| `name` | string | 商品名 |
| `shop` | string | 商家名 |
| `emoji` | string | 图标（可换为图片 URL） |
| `price` | number | 实际价格 |
| `priceLevel` | 1/2/3 | 1=低价(<20)，2=中价，3=高价(>50) |
| `healthScore` | 0-1 | 健康度 |
| `qualityScore` | 0-1 | 品质/评分 |
| `baseScore` | 0-1 | 基础热度 |
| `category` | string | 品类（需与 categoryBonus key 一致） |
| `tags` | string[] | 展示标签（也参与搜索匹配） |
| `searchKeys` | string[] | 搜索关键词 |

### 示例商品

```js
const PRODUCTS = [
  {
    id: 1, name: '藜麦牛肉汉堡', shop: '绿厨坊', emoji: '🍔',
    price: 38, priceLevel: 2,
    healthScore: 0.9, qualityScore: 0.8, baseScore: 0.70,
    category: '汉堡', tags: ['高蛋白', '低卡'], searchKeys: ['汉堡', '牛肉']
  },
  {
    id: 10, name: '牛油果鸡胸肉沙拉', shop: '轻食研究所', emoji: '🥗',
    price: 48, priceLevel: 3,
    healthScore: 0.95, qualityScore: 0.85, baseScore: 0.68,
    category: '沙拉', tags: ['健康', '高蛋白'], searchKeys: ['沙拉', '牛油果', '鸡胸']
  }
];
```

## 搜索匹配逻辑

```js
const matched = PRODUCTS.filter(p =>
  p.name.includes(kw) ||
  p.category.includes(kw) ||
  p.searchKeys.some(k => k.includes(kw) || kw.includes(k)) ||
  p.tags.some(t => t.includes(kw))
);
```

## 行为日志结构（用于偏好推断面板）

```js
behaviorClicks.push({
  type: 'click',        // 'click' | 'search'
  productId: p.id,
  productName: p.name,
  category: p.category,
  timestamp: Date.now()
});
```
统计各品类点击频次 → 推断用户实时偏好（在"行为偏好推断"面板展示）。
