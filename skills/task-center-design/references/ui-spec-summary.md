# ui-spec-summary.md
# 来源：task-center-ui-spec.md 关键约束提取（≤200行）
# 适用：AI 生成任务C端组件时注入的视觉规范约束

---

## 0. 适配方案（必须引入）

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
> 750px 设计稿，所有尺寸 rem，换算：设计稿px ÷ 100 = rem

---

## 1. 颜色规范

| 用途 | 色值 |
|------|------|
| 品牌主色 / 价格色 / 激活进度条 | `#FF2D19` |
| 弱化按钮底色 / 粉底券 | `#FFF1F0` |
| 文字一级（标题） | `#111111` |
| 文字二级（说明/门槛） | `#555555` |
| 文字三级（时间/进度辅助） | `#888888` |
| 文字四级（最弱/划线原价） | `#999999` |
| 已完成/禁用 | `#CCCCCC` |
| 卡片背景 | `#FFFFFF` |
| 未完成格/禁用底色 | `#F5F5F5` |

**❌ 禁止**：`#333333`、`#666666`、`#222222`；价格色不得偏离 `#FF2D19`。

---

## 2. 字体规范

```css
/* 正文中文 */
font-family: "PingFang SC", "Noto Sans SC", "Helvetica Neue", Arial, sans-serif;

/* 价格/数字（必须统一字体，¥符号和数字不得拆分走不同字体） */
font-family: "MTNewDigital", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
font-variant-numeric: tabular-nums;
```

| 用途 | 字号 | 字重 | 颜色 |
|------|------|------|------|
| 组件标题（"我的任务"） | `0.32rem` | 600 | `#111111` |
| 任务卡主标题 | `0.32rem` | **900** | `#111111` |
| 任务说明/门槛 | `0.22rem` | 400 | `#555555`/`#888888` |
| 辅助信息（进度/时间） | `0.2rem` | 400 | `#888888` |
| 奖励价格（核心，≤2位） | `0.6rem` | MTNewDigital | `#FF2D19` |
| 奖励价格（>2位数降档） | `0.54rem` | MTNewDigital | `#FF2D19` |
| 任务卡奖励 | `0.4rem` | MTNewDigital | `#FF2D19` |
| 签到格内奖励金额 | `0.24rem` | MTNewDigital | `#FF2D19` |

**❌ 禁止**：`font-weight:600` 代表中黑（中黑必须写 `900`）

---

## 3. 间距 & 圆角

| 名称 | 数值 |
|------|------|
| 页面左右边距 | `0.24rem` |
| 卡片内边距 | `0.24rem` |（双列以上：`0.16rem`）|
| 大卡片圆角（单列任务卡） | `0.24rem` |
| 中卡片圆角（三列/中型） | `0.16rem` |
| 小卡片/图片区/输入框 | `0.12rem` |
| 胶囊按钮圆角 | `0.24rem` |
| 营销描边标签圆角 | `0.06rem` |

---

## 4. 按钮规范（三态完整）

### 强化按钮（核心行动：任务完成领取、签到）
| 状态 | 底色 | 文字色 | 字号 | 字重 | 高度 |
|------|------|--------|------|------|------|
| 可点击 | `#FF2D19` | `#FFFFFF` | `0.32rem` | 600 | `0.8rem` |
| 禁用 | `#CCCCCC` | `#FFFFFF` | 同上 | 同上 | 同上 |

### 弱化按钮（任务列表卡内"去完成"）
| 状态 | 底色 | 文字色 | 字号 | 字重 | 高度 | 圆角 |
|------|------|--------|------|------|------|------|
| 可点击 | `#FFF1F0` | `#FF2D19` | `0.32rem` | 600 | `0.48rem` | `0.24rem` |
| 禁用 | `#F5F5F5` | `#999999` | 同上 | 同上 | 同上 | 同上 |

**❌ 按钮文案不得超过4个字**

---

## 5. 任务组件三态规范

### 5.1 下单任务卡（PROGRESS_BAR_TASK）
| 状态 | 标题色 | 进度条 | 按钮 |
|------|--------|--------|------|
| 默认（未开始） | `#111111` | 底色 `#F5F5F5`，0% | 弱化按钮"去完成" |
| 进行中 | `#111111` | 激活 `#FF2D19`，跟随% | 弱化按钮"继续完成" |
| 完成 | `#888888` | 满格 `#FF2D19` | 强化按钮"领取奖励"→领取后灰"已领取" |

### 5.2 签到格（SIGN_IN_CALENDAR）
| 状态 | 格底色 | 文字色 | 说明 |
|------|--------|--------|------|
| 已签到 | `#FF2D19` 或红浅色 | `#FFFFFF` | SVG 勾选图标 |
| 今日可签 | `#FFF1F0` 描边高亮 | `#FF2D19` | 强化按钮"立即签到"（h=`0.8rem`）|
| 未来/锁定 | `#F5F5F5` | `#CCCCCC` | 锁形SVG图标 |

签到格尺寸：约 `1.0rem × 1.12rem`，圆角 `0.12rem`

### 5.3 领券卡（奖励券展示）
| 状态 | 券底色 | 金额色 | 按钮 |
|------|--------|--------|------|
| 可领取 | `#FFF1F0` | `#FF2D19` | 强化/弱化按钮"立即领取" |
| 待解锁 | `#F5F5F5` | `#999999` | 灰色描边"去完成" |
| 已领取 | `#F5F5F5`，整体50%透明 | `#999999` | 灰色填充"已领取"（不可点）|

---

## 6. 快速参考 CSS

```css
/* 价格容器 */
.price {
  font-family: "MTNewDigital", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
  font-variant-numeric: tabular-nums;
  color: #FF2D19;
}

/* 弱化按钮 */
.btn-weak {
  background: #FFF1F0; color: #FF2D19;
  font-size: 0.32rem; font-weight: 600;
  height: 0.48rem; padding: 0 0.2rem;
  border-radius: 0.24rem; border: none;
}

/* 强化按钮 */
.btn-strong {
  background: #FF2D19; color: #FFFFFF;
  font-size: 0.32rem; font-weight: 600;
  height: 0.8rem; border-radius: 0.24rem; border: none;
}

/* 禁用态（通用） */
.btn-disabled {
  background: #CCCCCC; color: #FFFFFF; pointer-events: none;
}

/* 任务卡片容器 */
.task-card {
  background: #FFFFFF;
  border-radius: 0.24rem;
  padding: 0.24rem;
}

/* 营销描边标签 */
.tag-discount {
  height: 0.32rem; padding: 0 0.08rem;
  border: 1px solid #FFC6C1; border-radius: 0.06rem;
  color: #FF2D19; font-size: 0.22rem;
  display: inline-flex; align-items: center;
}
```

---

## 7. 禁止项清单（必须全部满足）

### 颜色
- ❌ 文字禁用 `#333333`、`#666666`、`#222222`（严格四档）
- ❌ 价格颜色必须 `#FF2D19`，不可偏离
- ❌ 弱化按钮底色仅 `#FFF1F0`

### 字体
- ❌ 中黑 = `font-weight: 900`，不得写 600
- ❌ ¥ 符号和数字必须同一字体（MTNewDigital）
- ❌ 价格容器必须含 `font-variant-numeric: tabular-nums`

### Emoji
- ❌ **严禁任何 Emoji**（🌸🎁🔥💥 等），包括 HTML/CSS 所有位置
- ✅ 替代方案：SVG图标、CSS图形、img标签

### 组件
- ❌ 旗帜标签（TOP1/2/3）仅限榜单组件，不得在任务卡用
- ❌ 同一卡片最多1个深色标签
- ❌ 三列及以上：辅助信息与标签二选一
- ❌ 按钮文案 > 4字
- ❌ 标签文案 > 4字
- ❌ 门槛信息 > 5字符

### 布局
- ❌ 组件标题不得倾斜
- ❌ 组件标题默认居左，不强制居中
