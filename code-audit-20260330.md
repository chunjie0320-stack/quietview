# 代码安全审查报告 — quietview 脚本全量扫描

**审查时间：** 2026-03-30  
**审查范围：** `/root/.openclaw/workspace/scripts/` 下全部 7 个 Python 文件  
**审查人：** 喵子代码质检 SubAgent  

---

## miao_notice_update.py

**状态：⚠️ 有风险（已修复的3处确认安全，但仍有3个新风险点）**

### 风险点

#### ✅ 已修复（确认安全）
今日修复的3处 `html.find('}', ...)` 截断问题已不存在于当前代码中。
当前 NAV_DATA 操作均使用正则完整匹配模式：
```python
re.search(r"\{ id: 'daily-brief-\d{8}', label: '[^']+', panel: '[^']+' \}", html)
```
这是完整匹配，**不会**截断产生 `{ {` 双括号。✅

#### ⚠️ 风险1：L315 — NAV_DATA label 10月会生成「010月」
**行号：** 315  
**问题：** `label_month = date_str[4:6].lstrip('0')` 后拼接 `'0' + label_month`，导致10月（'10'）去掉前导0后还是'10'，最终生成 `'010月'`，破坏JS字符串。

```python
# 当前代码（有bug）
label_month = date_str[4:6].lstrip('0')   # '10' -> '10'
label_day = date_str[6:].lstrip('0')       # '01' -> '1'
new_nav = f"{{ id: 'daily-brief-{date_str}', label: '0{label_month}月{label_day}日', ... }}"
# 结果：label: '010月1日'  ← NAV_DATA JS语法错误风险
```

**当前影响：** 3月日期正常（`'0' + '3' = '03'`），**10月以后会出错**。
**优先级：** 中（9月底触发，约6个月后）  
**建议修复：**
```python
# 直接用原始字段，不做 lstrip
label_month = date_str[4:6]   # '03', '10'
label_day   = date_str[6:]    # '30', '01'
new_nav = f"{{ id: 'daily-brief-{date_str}', label: '{label_month}月{label_day}日', panel: '{panel_id}' }}"
```

#### ⚠️ 风险2：L557-558 — index.html 重复添加到 git files 列表
**行号：** 557-558  
**问题：** `files.append("index.html")` 连续出现两次，重复 git add 同一文件。

```python
if html_changed:
    files.append("index.html")
    files.append("index.html")  # ← 多余的重复行
```

**影响：** 功能上无害（git add 同一文件两次等于一次），但是代码质量问题，可能掩盖其他意图。  
**优先级：** 低  
**建议修复：** 删除重复的一行。

#### ⚠️ 风险3：ensure_html_panel / ensure_ai_voice_panel / ensure_miao_panel — 写文件前无备份
**行号：** 338, 436, 511, 544  
**问题：** 三个 `ensure_*` 函数在写 `index.html` 前均**没有备份**。`cls_news_updater.py` 和 `wx_voice_updater.py` 都有 `shutil.copy2` 备份，唯独 `miao_notice_update.py` 的这四处直接写文件。

```python
# 无备份保护：
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
```

**影响：** div自查（HTMLParser）会阻止坏写入，但如果div自查通过而内容实际有误，无法回滚。  
**优先级：** 低（div自查兜底，但缺乏一致性）  
**建议修复：** 在每个 `ensure_*` 函数写文件前加：
```python
import shutil
shutil.copy2(html_path, html_path + f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
```

### HTML结构安全
- ✅ `ensure_html_panel` 中 `new_section` 的 `<!-- INJECT:voice_{date_str} -->` 和 `<!-- /INJECT:voice_{date_str} -->` 成对出现
- ✅ 所有 `ensure_*` 函数均有 HTMLParser div深度自查，depth≠0时抛出 ValueError 阻止写入
- ✅ `esc()` 函数正确处理 `&`, `<`, `>` 转义
- ✅ f-string 中的 miao_content 经过 esc() 运行时处理，不会被 f-string 解析花括号（因为内容是运行时字符串）

---

## cls_news_updater.py

**状态：⚠️ 有风险（1处 re.subn 注入隐患）**

### 风险点

#### ⚠️ 风险1：L334 — re.subn replacement 直接拼接 items_html，存在反斜杠/回引用注入风险
**行号：** 334  
**问题：** `replacement = rf'\g<1>{items_html}\n              \g<3>'`，其中 `items_html` 是从外部数据生成的HTML字符串，若新闻标题/正文含有 `\g<N>` 、`\1` 等字符串（如标题包含正则字面量），会被 `re.sub` 解释为反向引用，导致替换结果错乱。

```python
pattern = r'(<!-- INJECT:investment_news -->)(.*?)(<!-- /INJECT:investment_news -->)'
replacement = rf'\g<1>{items_html}\n              \g<3>'   # ← 危险！items_html可能含特殊字符
new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)
```

**实际触发场景：** 财联社标题中出现 `\1`、`\g<1>` 等字符串（极低概率，但实际测试已验证注入会发生）。  
**优先级：** 中  
**建议修复：** 使用 `re.escape` 或改用函数式 replacement：
```python
# 方案1：函数式替换（最安全）
def make_replacement(items_html_str):
    def replacer(m):
        return m.group(1) + items_html_str + '\n              ' + m.group(3)
    return replacer

new_html, n = re.subn(pattern, make_replacement(items_html), html, flags=re.DOTALL)

# 方案2：使用 re.escape 保护 items_html
safe_html = items_html.replace('\\', '\\\\')
replacement = rf'\g<1>{safe_html}\n              \g<3>'
```

### 其他检查
- ✅ `_escape_html()` 正确处理 `&`, `<`, `>`, `"` 转义
- ✅ 写文件前有 `shutil.copy2` 备份（L395-396）
- ✅ 写文件后有 `verify_divs()` HTMLParser div深度自查
- ✅ re.sub 中 `\g<1>` 和 `\g<2>` 的用法在更新 badge 处（L341）是安全的（因为 replacement 里是字面量 `· {count}`，不含用户数据）
- ✅ 无 `html.find('}')` 截断操作

---

## wx_voice_updater.py

**状态：⚠️ 有风险（2处问题）**

### 风险点

#### ❌ 风险1：L318-319 — re.sub replacement 直接拼接用户数据，会发生回引用注入
**行号：** 318-319  
**问题：** `pattern.sub(r'\g<1>' + new_inner + r'\3', content)` 中，`new_inner` 包含从外部API获取的声音标题/摘要，若标题含 `\g<1>` 字符串，Python 的 re 引擎会将其解释为第一个捕获组，导致插入内容被替换为标记本身（INJECT注释内容）。

```python
new_inner = '\n' + '\n'.join(items_html) + '\n'
new_content = pattern.sub(
    r'\g<1>' + new_inner + r'\3',   # ← 危险！new_inner是用户可控内容
    content
)
```

**验证：** 已通过实测证实，当 `new_inner` 含 `\g<1>` 时，会将 `\g<1>` 替换为 INJECT 标记内容，破坏 HTML 结构。  
**优先级：** 高（外部数据直接注入，虽概率低但后果严重）  
**建议修复：** 同 cls_news_updater.py，改用函数式替换：
```python
def replacer(m):
    return m.group(1) + new_inner + m.group(3)

new_content = pattern.sub(replacer, content)
```

#### ⚠️ 风险2：L330-339 — div深度自查使用 line.count 方案，会把注释中的 `<div>` 也计入
**行号：** 330-339  
**问题：** 用 `line.count('<div') - line.count('</div')` 计算 div 深度，HTML 注释（`<!-- ... <div> ... -->`）中的 `<div>` 也会被计入，可能误报 depth≠0。

```python
# 当前代码（不准确）
for line in new_content.splitlines():
    depth += line.count('<div') - line.count('</div')
```

**实测：** HTML注释 `<!-- comment with <div> inside -->` 会使 line.count 多计1个 div，导致误以为 depth=1。  
**影响：** 可能发生"虚假健康"（注释中有 `<div>` 抵消了真实的不平衡），也可能触发"误报回滚"（注释中有 `<div>` 但实际HTML正常）。  
**优先级：** 中  
**建议修复：** 改用 `html.parser.HTMLParser`，与其他脚本保持一致：
```python
from html.parser import HTMLParser
class DivCounter(HTMLParser):
    def __init__(self): super().__init__(); self.depth = 0
    def handle_starttag(self, t, a):
        if t == 'div': self.depth += 1
    def handle_endtag(self, t):
        if t == 'div': self.depth -= 1

counter = DivCounter()
counter.feed(new_content)
if counter.depth != 0:
    # 回滚
```

### 其他检查
- ✅ `esc()` 函数正确转义 `&`, `<`, `>`, `"`
- ✅ 写文件前有 `shutil.copy2` 备份（L323-325）
- ✅ 无 `html.find('}')` 截断操作

---

## fetch_all.py

**状态：✅ 安全**

### 检查结果
- ✅ **不操作 index.html**：脚本只写 `data/YYYYMMDD.json`（L713），不涉及HTML操作
- ✅ **无 NAV_DATA 操作**：不插入JS NAV_DATA
- ✅ **无危险 HTML 拼接**：所有 HTML 标签相关操作都是数据抓取时的 re.sub 文本清理（去标签），不是生成HTML
- ✅ **re.sub 安全**：`re.sub(r'<[^>]+>', '', text_raw)` 是纯正则替换，replacement 是字面量 `''`，无用户数据注入
- ✅ **无 html.find('}') 截断**

**风险点：** 无

---

## check_health.py

**状态：✅ 安全**

### 检查结果
- ✅ **只读不写**：脚本只读取 `index.html` 和 JSON 文件做检查，不写文件
- ✅ **HTMLParser 正确使用**：div 深度检查用 `HTMLParser`，不用 line.count
- ✅ **无危险模式**：无 HTML 拼接、无 NAV_DATA 操作
- ✅ **INJECT 标记检查**：主动检查 `INJECT:voice_{date}` 标记是否存在，会在缺失时警告

**风险点：** 无

---

## cls_telegraph.py

**状态：✅ 安全**

### 检查结果
- ✅ **不操作 index.html**：纯数据抓取脚本，只输出 JSON 或打印，不写 HTML
- ✅ **无 NAV_DATA 操作**
- ✅ **无危险 HTML 拼接**
- ✅ **re.sub/正则安全**：仅用于 `_parse_subjects` 解析，无用户数据注入到 HTML

**风险点：** 无

---

## git_lock.py

**状态：✅ 安全**

### 检查结果
- ✅ **subprocess 安全**：所有 git 命令均用列表形式（无 `shell=True`），无命令注入风险
- ✅ **有僵尸锁清理**：180秒超时自动清除僵尸锁
- ✅ **有 pull --rebase**：防止并发 push 冲突
- ✅ **有 force-with-lease fallback**：rebase 失败时有降级处理

**风险点：** 无

---

## 总结表

| 文件 | 状态 | 问题 | 行号 | 优先级 |
|------|------|------|------|--------|
| `wx_voice_updater.py` | ⚠️ | `re.sub` replacement 直接拼接用户数据，`\g<N>` 回引用注入（已实测） | L318-319 | 🔴 高 |
| `cls_news_updater.py` | ⚠️ | `re.subn` replacement 直接拼接 items_html，存在同类注入隐患 | L334 | 🟡 中 |
| `miao_notice_update.py` | ⚠️ | `label_month lstrip('0')` 后拼 `'0'` 前缀，10月会生成 `'010月'` | L315 | 🟡 中（9月后触发） |
| `wx_voice_updater.py` | ⚠️ | div深度自查用 `line.count`，注释中 `<div>` 会被误计 | L330-339 | 🟡 中 |
| `miao_notice_update.py` | ⚠️ | 3个 `ensure_*` 函数写文件前无备份 | L338/436/511/544 | 🟢 低 |
| `miao_notice_update.py` | ⚠️ | `index.html` 重复添加到 git files 列表 | L557-558 | 🟢 低 |

### 修复优先级排序

1. **🔴 立即修复** — `wx_voice_updater.py` L318-319：re.sub 函数式替换
2. **🟡 近期修复** — `cls_news_updater.py` L334：re.subn 函数式替换  
3. **🟡 近期修复** — `miao_notice_update.py` L315：label_month 拼接逻辑修正（9月底前修完）
4. **🟡 近期修复** — `wx_voice_updater.py` L330：div深度自查改用 HTMLParser
5. **🟢 可选修复** — `miao_notice_update.py` 三个 ensure_* 函数加备份
6. **🟢 清理** — `miao_notice_update.py` L558 删除重复的 `files.append("index.html")`

### 关于今日根因（`{ {` 双括号）已修复验证

- ✅ 当前代码中**不存在** `html.find('}')` 截断后拼接 HTML/JS 的模式
- ✅ NAV_DATA 操作均使用完整正则匹配 `{ id: '...', label: '...', panel: '...' }`
- ✅ 今日已修复的3处确认已完全清除

---

*报告生成：2026-03-30 | 执行：只读审查，未修改任何代码*
