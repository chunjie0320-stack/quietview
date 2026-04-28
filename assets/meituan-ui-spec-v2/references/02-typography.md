# 美团营销活动 - 文字规范

## ⚠️ 字重 CSS 映射（必须严格使用数值）

| 规范用语 | CSS font-weight 值 | 适用场景 |
|---------|-------------------|----------|
| 常规 | `400` | 正文、辅助信息、导航文字 |
| 中粗 | `600` | 楼层标题、组件标题、Tab选中态 |
| 中黑 | `900` | 商家标题、商品标题 |

> ❌ 禁止将「中黑」写成 `font-weight: 600`，两者视觉差异显著

## ⚠️ 文字颜色只允许四档（禁止使用规范外色值）

| 档位 | 色值 | 适用场景 |
|------|------|----------|
| 一级 | `#111111` | 标题、商品名、主要内容 |
| 二级 | `#555555` | 次要标题、商家辅助信息、券名称 |
| 三级 | `#888888` | 距离、时间、门槛信息、辅助说明 |
| 四级 | `#999999` | 最弱层级信息 |

> ❌ 禁止使用 `#333333`、`#666666`、`#222222` 等规范外灰色

---

## 字族

### 系统字体
App 页面中文、西文信息优先使用系统默认字体：
- **iOS**：苹方简体（`PingFang SC`）
- **Android**：思源黑体（`Noto Sans SC`，中文）/ Roboto（西文）

**CSS 写法**：
```css
font-family: "PingFang SC", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif;
```

### 美团新数字字体
共三款字重，建议应用于需重点突出的数字信息，如价格、时间、公里数等。

**字体文件路径**（已存放于 skill assets）：
```
assets/fonts/MTNewDigitalDisplay-Regular.otf   → font-weight: 400
assets/fonts/MTNewDigitalDisplay-Medium.otf    → font-weight: 500
assets/fonts/MTNewDigitalDisplay-Bold.otf      → font-weight: 700
```

**CSS 引入方式（生成代码时必须包含以下 @font-face）**：
```css
@font-face {
  font-family: "MTNewDigital";
  src: url("assets/fonts/MTNewDigitalDisplay-Regular.otf") format("opentype");
  font-weight: 400;
}
@font-face {
  font-family: "MTNewDigital";
  src: url("assets/fonts/MTNewDigitalDisplay-Medium.otf") format("opentype");
  font-weight: 500;
}
@font-face {
  font-family: "MTNewDigital";
  src: url("assets/fonts/MTNewDigitalDisplay-Bold.otf") format("opentype");
  font-weight: 700;
}
```

**使用方式**：价格区域内**所有字符**（¥符号、数字、小数点）统一设置，不能只给数字加字体：
```css
/* ✅ 正确：¥符号和数字都在同一个容器上设置，或分别设置相同字体 */
font-family: "MTNewDigital", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
font-variant-numeric: tabular-nums;
```
```css
/* ❌ 错误：¥符号走苹方，数字走MTNewDigital，字体不一致 */
.price-symbol { font-family: "PingFang SC"; }  /* 错误！ */
.price-value  { font-family: "MTNewDigital"; } /* 只给数字加不够 */
```

---

## 模块标题（楼层/组件标题）

| 用途 | 字号 | 字重 | 颜色 | 说明 |
|------|------|------|------|------|
| 楼层条文案 | 0.36rem | 中粗 | #111111 | 可使用苹方体/美团体，不做倾斜处理 |
| 组件标题名称 | 0.32rem | 中粗 | #111111 | 默认苹方体，不做倾斜处理，文案默认居左，上下左边距0.24rem |

---

## 商家标题

| 字号 | 字重 | 颜色 | 应用场景 |
|------|------|------|----------|
| 0.32rem | 中黑 | #111111 | 单独商家、商家带品场景 |
| 0.28rem | 常规 | #111111 | 品带商家 |
| 0.22rem | 常规 | #555555 | 商家辅助信息 |

---

## 商品标题

| 字号 | 字重 | 颜色 | 应用场景 |
|------|------|------|----------|
| 0.32rem | 中黑 | #111111 | 1行1结构 |
| 0.28rem | 中黑 | #111111 | 1行2结构、店带1个品结构 |
| 0.24rem | 中黑/常规 | #555555 | 1行3结构、1行N结构 |

---

## 决策信息字符

| 字号 | 字重 | 颜色 | 应用场景 |
|------|------|------|----------|
| 0.22rem / 0.2rem | 常规 | #555555 / #888888 / #999999 | 地址/距离/配送费、起送价/配送时间等 |

---

## 数字字体（价格）

| 规格 | 字号 | 相同大小组合 | 不同大小组合 | 应用场景 |
|------|------|-------------|-------------|----------|
| 超大 | 0.6rem | ¥72.88 | ¥72⁸⁸ | 重点价格，POI页面、商品详情页、头部价格 |
| 超大 | 0.48rem | ¥72.88 | ¥72.88 | 订单价格，购物车、结算页底部控件 |
| 超大 | 0.44rem | ¥72.88 | ¥72.388 | 头部价格，外卖选规格页 |
| 大 | 0.4rem | ¥72.88 | ¥72.88 | 商品列表、商品卡片价格 |
| 大 | 0.36rem | ¥72.88 | ¥72.88 | 商品列表、商品卡片价格 |
| 大 | 0.32rem | ¥72.88 | ¥72.88 | 商品列表、商品卡片价格 |
| 中 | 0.3rem | ¥72.88 | ¥72.88 | 商品列表、商品卡片价格 |
| 中 | 0.28rem | ¥72.88 | ¥72.88 | 商品列表、商品卡片价格 |
| 中 | 0.26rem | ¥72.88 | — | 非主要价格信息（仅相同大小组合） |
| 小 | 0.24rem | ¥72.88 | — | 非主要价格信息（仅相同大小组合） |
| 小 | 0.22rem | ¥72.88 | — | 非主要价格信息（仅相同大小组合） |
| 小 | 0.2rem | ¥72.88 | — | 非主要价格信息（仅相同大小组合） |

> 价格字体用色统一：**#FF2D19**
