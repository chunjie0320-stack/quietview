# 美食热点搜索 Demo

AI 驱动的美食内容选题引擎，支持自然语言输入、热点气泡图、品类下钻分析。

## 快速开始

**1. 修改配置**

打开 `config.js`，将 `FRIDAY_APP_ID` 改为你自己的 Friday AppId：

```js
window.FOODSEARCH_CONFIG = {
  FRIDAY_APP_ID: 'your_app_id_here',  // ← 改这里
  API_BASE: 'http://localhost:8080',
};
```

**2. 安装依赖**

```bash
pip install -r requirements.txt
playwright install chromium  # 首次运行需要（可选，用于接入小红书真实数据）
```

**3. 启动服务**

```bash
python app.py
```

**4. 打开浏览器**

访问 http://localhost:8080

---

## 功能说明

- **Step 1 输入**：自然语言描述需求，AI 自动识别地域/品类/人群/季节/目标
- **Step 2 热点分析**：动态生成气泡图（商业化潜力 × 内容创作难度），点击气泡下钻
- **Step 4 选题方案**：基于热点数据生成选题建议
- **Step 5 内容预览**：商业化供给清单或内容型文章预览

---

## 接入真实小红书数据（二选一）

系统启动时自动检测 Cookie，有效时优先抓取真实帖子数据，否则降级到 AI 生成。

**Cookie 查找顺序：**
1. `cookies/xhs.json`（项目内，优先）
2. `~/.openclaw/xiaohongshu-cookies.json`（沙箱全局路径，自动 fallback）

---

### 方式一：自动登录（推荐，Mac 本地运行）

```bash
python setup_xhs.py
```

会打开有界面的浏览器窗口，登录小红书后回到终端按回车，自动保存 Cookie 到 `cookies/xhs.json`。

---

### 方式二：手动贴 Cookie（服务器 / 沙箱环境）

将你的小红书 Cookie 保存到 `cookies/xhs.json`（格式参考 `cookies/xhs.json.example`）：

```json
{
  "a1": "你的 a1 cookie 值",
  "web_session": "你的 web_session cookie 值"
}
```

**如何获取：**
1. Chrome 打开 https://www.xiaohongshu.com 并登录
2. F12 → Application → Cookies → `https://www.xiaohongshu.com`
3. 找到 `a1` 和 `web_session`，复制 Value 填入

---

## Friday AppId 获取

访问 https://friday.sankuai.com 申请应用，获取 AppId。

---

## 后端接口说明

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/parse` | POST | AI 意图识别，输入自然语言，返回结构化参数 |
| `/api/topics` | POST | 生成热点气泡图数据（6-8 个品类） |
| `/api/drill` | POST | 品类下钻，返回供给/选题/文案数据 |

---

## 注意事项

- 需要 Python 3.10+
- 首次启动如果 FRIDAY_APP_ID 未配置，接口会返回错误，前端会降级到本地关键词匹配
- playwright 相关依赖仅在有 `cookies/xhs.json` 时才会实际使用
