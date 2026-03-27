---
name: persona-search-recommend
description: >
  代码脚手架类 Skill：生成基于用户画像（Persona 标签 + 历史行为）的个性化搜索推荐 Demo HTML 原型。
  触发词：个性化搜索 Demo、画像推荐 Demo、搜索落地页原型、用户画像驱动推荐、persona 搜索 Demo、
  帮我做搜索推荐 Demo、基于用户标签推荐商品、搜索历史+结果页 Demo。
  产出：一个可直接在浏览器打开的单文件 HTML，包含搜索落地页、搜索历史、个性化搜索结果三个交互页面，
  以及右侧可切换用户画像的控制面板，支持实时展示不同 Persona 下的推荐排序差异。
---

# Persona Search & Recommend Demo Scaffold

## 快速生成 Demo

1. 复制 `assets/demo-template/index.html` 到目标路径
2. 按需替换 `USERS` 和 `PRODUCTS` 数据（见 `references/data-schema.md`）
3. 直接用浏览器打开，无需构建工具

## 核心推荐算法（勿改动，保持在 index.html 中）

```js
function scoreProduct(product, user) {
  let s = product.baseScore;
  s += product.healthScore * user.healthWeight * 0.3;
  s -= (product.priceLevel - 1) * user.priceWeight * 0.25;
  s += product.qualityScore * user.qualityWeight * 0.2;
  s += (user.categoryBonus[product.category] || 0);
  s += (Math.random() - 0.5) * 0.06;  // 轻微随机扰动，避免结果完全固化
  return Math.max(0, Math.min(1, s));
}
```

## 自定义扩展

- **换用户 Persona**：修改 `USERS` 对象，调整三个权重（0=不敏感，1=高度敏感）和 `categoryBonus`
- **换商品库**：修改 `PRODUCTS` 数组，需包含 `priceLevel(1-3)`、`healthScore`、`qualityScore`、`searchKeys`
- **接入真实数据**：将 `PRODUCTS` 替换为 API 返回数组，`scoreProduct` 函数保持不变
- **UI 调整**：参考 `references/ui-patterns.md`

## 参考文件

- `references/data-schema.md` — USERS/PRODUCTS 完整字段规范 + 示例数据
- `references/ui-patterns.md` — 搜索栏/商品卡/历史标签/排名徽章 CSS 规范
- `assets/demo-template/index.html` — 完整可运行模板（开箱即用）
