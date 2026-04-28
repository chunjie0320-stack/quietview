---
name: meituan-ui-spec-v2
description: 美团营销活动会场UI设计规范 v2（rem单位版，面向代码生成）。当用户需要生成、开发、评审营销活动会场页面、营销组件（如券组件、商卡、按钮、Tab导航、底部导航等）的代码或UI稿时，必须严格遵循此规范。适用场景包括：(1) 生成营销活动会场页面代码，(2) 开发单个营销UI组件，(3) 评审或修复营销页面的视觉/布局问题，(4) 实现综合大促、日常活动、品牌活动等营销场域的界面。与旧版（meituan-ui-spec）的区别：本版使用rem单位、包含美团新数字字体文件、有精确CSS数值约束、禁止Emoji，适合直接生成可运行代码；旧版使用px/pt描述，适合设计决策参考。
---

# 美团营销活动会场 UI 规范

本规范适用于美团**营销场域**：综合大促活动、日常活动、品牌活动。所有代码生成必须 **100% 遵循**以下规范。

## 适配说明

本规范基于 **750px 设计稿**（对应 375pt 逻辑宽度的 2x 标注），所有尺寸使用 **rem 单位**。

**换算规则**：设计稿 px 值 ÷ 100 = rem 值（即 1rem = 设计稿 100px）

生成代码时需在 HTML 中引入以下适配脚本，根据屏幕宽度动态设置根 font-size：

```javascript
(function () {
  var docEl = document.documentElement;
  function setRemUnit() {
    var clientWidth = docEl.clientWidth || window.innerWidth;
    docEl.style.fontSize = (clientWidth / 7.5) + 'px';
  }
  setRemUnit();
  window.addEventListener('resize', setRemUnit);
})();
```

> 原理：在 375px 宽度设备上，根 font-size = 375 / 7.5 = 50px，则 0.24rem = 12px（物理像素），正好是设计稿 24px 的一半（2x 还原）。

## 核心约束

1. **字体**：中文使用苹方/思源黑体，数字价格使用美团新数字字体
2. **价格颜色**：统一 `#FF2D19`
3. **一级文字色**：`#111111`
4. **二级文字色**：`#555555`
5. **三级文字色**：`#888888`
6. **按钮辅助色底色**：`#FFF1F0`
7. **页边距**：0.24rem
8. **同一卡片最多1个深色标签**

## ⚠️ 易错强制约束（生成代码前必读）

### 1. 文字色只能使用以下四档，禁止使用任何其他色值
```
一级文字色：#111111  → 标题、主要内容
二级文字色：#555555  → 次要内容、商家辅助信息
三级文字色：#888888  → 辅助信息、时间、距离
四级文字色：#999999  → 最弱信息层
```
❌ 禁止使用 #333333、#666666、#222222 等规范外色值

### 2. font-weight 中文字重映射（必须使用数值，禁止用汉字描述）
```
常规  → font-weight: 400
中粗  → font-weight: 600
中黑  → font-weight: 900
```
⚠️ 商家标题、商品标题规范写的是「中黑」= font-weight: 900，不是 600

### 3. 美团新数字字体适用范围（¥符号也必须使用）
价格区域内**所有字符**（含 ¥ 符号、数字、小数点）都必须使用 MTNewDigital：
```css
/* 价格容器、¥符号、金额数字，统一设置 */
font-family: "MTNewDigital", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
font-variant-numeric: tabular-nums;
```
❌ 不能只给数字加字体，¥ 符号单独走苹方

### 4. 禁止使用 Emoji 表情
生成的所有 HTML/CSS/JS 代码中，**严禁**在页面可见内容里使用 Emoji 表情字符（如 🌸🎁🔥💥 等）。
图标、装饰元素必须使用以下替代方案：
- SVG 图标
- CSS 图形（border-radius、伪元素等）
- 图片资源（img 标签或 background-image）

❌ 禁止：`<span>🌸</span>`、`content: "🎉"`、任何 Unicode Emoji 字符直接写入 HTML

## 参考文档导航

根据生成内容，读取对应的参考文档：

| 需求 | 参考文档 |
|------|---------|
| 会场整体结构、页面布局 | [09-page-structure.md](references/09-page-structure.md) + [01-overview.md](references/01-overview.md) |
| 字体/文字规范 | [02-typography.md](references/02-typography.md) |
| 栅格/间距/圆角/图片比例 | [03-layout.md](references/03-layout.md) |
| 领券/优惠券组件 | [04-coupon-component.md](references/04-coupon-component.md) |
| 按钮（常规/促销） | [05-button.md](references/05-button.md) |
| 标签（价格标签/状态标签/榜单标签） | [06-tags.md](references/06-tags.md) |
| 底部导航/Tab/悬浮按钮 | [07-navigation.md](references/07-navigation.md) |
| 商卡/商品卡/商家卡 | [08-merchant-card.md](references/08-merchant-card.md) |

## 生成代码的强制规则

生成任何营销会场或组件代码时：

1. **先读取相关参考文档**，再生成代码
2. **字号必须精确**：不得随意更改规范中的字号、字重、颜色
3. **间距必须精确**：页边距0.24rem，组件标题上下左边距0.24rem，商家信息间距0.12rem
4. **圆角必须按场景选择**：大卡片0.24rem、中等卡片0.16rem、小卡片0.12rem
5. **按钮颜色必须区分场景**：强化场景用强色，弱化场景用 `#FFF1F0` 底色
6. **券金额超过2位数时**字号从0.6rem降为0.54rem
7. **三列及以上商卡**，辅助信息和标签二选一
8. **榜单标签（旗帜形态）** 仅用于榜单组件

## 快速参考

### 关键字号（括号内为对应 CSS font-weight 值）

```
楼层标题:      0.36rem  font-weight:600(中粗)  #111111
组件标题:      0.32rem  font-weight:600(中粗)  #111111
商家标题(主):  0.32rem  font-weight:900(中黑)  #111111
商品标题(主):  0.32rem  font-weight:900(中黑)  #111111
商品标题(双列):0.28rem  font-weight:900(中黑)  #111111
商品标题(三列):0.24rem  font-weight:900(中黑)  #555555
价格(主推):    0.4rem   MTNewDigital           #FF2D19
价格(列表):    0.36rem  MTNewDigital           #FF2D19
辅助信息:      0.22rem  font-weight:400(常规)  #555555/#888888
底部导航文字:  0.2rem   font-weight:400(常规)
Tab文字:       0.32rem(一级) / 0.24rem(二级)
底部规则正文:  0.24rem  font-weight:400(常规)
```

### 关键圆角
```
大卡片(单列/双列): 0.24rem
中等卡片(三列): 0.16rem
小卡片/图片/输入框: 0.12rem
图片叠加标签右上角: 0.12rem
```

### 关键间距
```
页面左右边距: 0.24rem
组件标题上下左边距: 0.24rem
商家信息元素间距: 0.12rem
底部导航悬浮型左右: 0.24rem，上下: 0.18rem
底部规则容器宽: 7.02rem，上下左右边距: 0.24rem
```
