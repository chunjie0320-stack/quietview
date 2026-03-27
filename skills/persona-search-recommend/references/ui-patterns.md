# UI Patterns — Persona Search & Recommend Demo

## 设计风格

- **字体**：`-apple-system, 'PingFang SC', sans-serif`，`-webkit-font-smoothing: antialiased`
- **配色**：橙色主题 `#FF6B35`（主色）/ `#FF8C00`（hover）/ `#F2F2F7`（背景）
- **圆角**：手机外框 40px / 卡片 12-16px / 标签 20px（全圆）/ 按钮 24px（胶囊）
- **阴影**：`box-shadow: 0 2px 8px rgba(0,0,0,.08)` 轻薄风格

## 布局结构

```
整体布局（flex row）
├── 手机预览区（左，固定宽 360px）
│   ├── page-home（首页：搜索触发区 + 推荐列表）
│   └── page-search（搜索页：搜索栏 + 初始态/结果态）
└── 右侧面板区（右，flex-col，宽 280px）
    ├── 切换用户面板
    ├── PERSONA 画像面板（标签展示）
    ├── 偏好权重面板（进度条）
    ├── 快速搜索面板
    ├── 跨用户对比面板（可选）
    └── 行为记录 + 偏好推断面板
```

## 关键 UI 组件

### 搜索触发区（首页）

```html
<div class="home-search-trigger" id="btn-to-search">
  <span class="search-icon">🔍</span>
  <span class="s-placeholder" id="search-trigger-text">搜索美食…</span>
  <span class="s-hot" id="search-trigger-hot">搜索</span>
</div>
```
- placeholder 根据当前用户动态更新（如"小美在搜索…沙拉？"）
- s-hot 按钮橙色背景，圆角胶囊

### 搜索栏（搜索页）

```html
<div class="search-header">
  <button class="search-back-btn" id="btn-back-home">←</button>
  <div class="search-input-wrap">
    <span class="search-icon">🔍</span>
    <input type="text" id="search-input" placeholder="搜索美食、商家…">
  </div>
  <button class="search-submit-btn" id="btn-search-submit">搜索</button>
</div>
```

### 历史搜索标签

```html
<div class="history-tags" id="history-tags">
  <!-- 动态渲染 -->
  <span class="history-tag" onclick="fillSearch('汉堡')">汉堡</span>
</div>
```
- 最多保留 8 条
- 点击自动填充并触发搜索
- 清空按钮：`<span class="clear-btn" id="btn-clear-history">清空</span>`

### 商品卡片

```html
<div class="product-card rank-1" onclick="clickProduct(id, name)">
  <div class="product-img-wrap">🥗</div>
  <div class="product-body">
    <div class="product-name">牛油果鸡胸肉沙拉</div>
    <div class="product-shop">轻食研究所</div>
    <div class="product-tags">
      <span class="product-tag health">健康</span>
      <span class="product-tag health">高蛋白</span>
    </div>
  </div>
  <div class="product-right">
    <div class="product-price"><span class="unit">¥</span>48</div>
    <div class="product-rating">★ 4.9</div>
    <div class="rank-badge">#1</div>  <!-- 前3名显示 -->
  </div>
</div>
```

**标签颜色规则**：
- 健康类（健康/低卡/低脂/素食/高蛋白/低糖）→ 绿色背景
- 优惠类（超值/经济/超便宜）→ 橙色背景
- 其他 → 灰色背景

**排名徽章**：
- #1 → 橙色 `#FF6B35`
- #2 → 钢蓝 `#5B8AF5`
- #3 → 绿色 `#52C41A`

### 权重进度条（右侧面板）

```html
<div class="weight-row">
  <span class="weight-label">💰 价格敏感</span>
  <div class="weight-bar-bg">
    <div class="weight-bar" style="width: 30%"></div>  <!-- priceWeight * 100% -->
  </div>
  <span class="weight-val">0.3</span>
</div>
```

### 搜索结果标题区

```html
<div class="result-header">
  <span class="result-title" id="result-title">搜索结果</span>
  <span class="result-persona-badge" id="result-persona-badge">👩‍💼 小美视角</span>
</div>
```
- persona-badge 提示当前是哪个用户的个性化排序

## 交互状态

| 状态 | 触发 | 显示 |
|------|------|------|
| 初始态 | 进入搜索页 | 历史搜索 + 热门搜索 |
| 结果态 | 提交搜索词 | 商品结果列表 + persona badge |
| 空结果 | 无匹配商品 | 提示"没有找到相关商品" |
| 未选用户 | 搜索但未切换用户 | input placeholder 变红提示 |

## CSS 关键变量

```css
:root {
  --primary: #FF6B35;
  --primary-dark: #E85A2A;
  --bg: #F2F2F7;
  --card-bg: #FFFFFF;
  --text-primary: #1C1C1E;
  --text-secondary: #8E8E93;
  --border: rgba(0,0,0,.06);
  --radius-card: 14px;
  --radius-tag: 20px;
}
```
