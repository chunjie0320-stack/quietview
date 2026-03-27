# quietview GitHub Actions 配置手册

## 一次性配置：GitHub Secrets

在 GitHub 仓库页面操作：
Settings → Secrets and variables → Actions → New repository secret

需要添加2个 Secret：

| Name | Value | 说明 |
|------|-------|------|
| WX_TOKEN | 你的微信后台 token | mp.weixin.qq.com 地址栏 URL 里的 token= 参数 |
| WX_COOKIE | 完整 cookie 字符串 | slave_sid=...;slave_user=...;bizuin=... |

## 当前 token（2026-03-26）
WX_TOKEN=962183803
WX_COOKIE=（从 /root/.openclaw/weibo/wx_cookies.env 的 WX_COOKIE 字段获取）

## Token 过期处理
- 症状：GitHub Actions 失败，邮件提示 workflow failed
- 解法：重新登录 mp.weixin.qq.com，从地址栏拿新 token，更新 Secrets
- 频率：约每2-4周过期一次

## 定时触发时间（北京时间）
- 08:00
- 12:00
- 18:00

## 手动触发
GitHub 仓库 → Actions → Fetch Quietview Data → Run workflow

---

## ⚠️ 待处理：PAT workflow scope 授权

当前 Personal Access Token（PAT）只有 `repo` scope，无法推送 `.github/workflows/` 目录下的文件。

**需要女王大人手动操作（一次性）：**

1. 打开 https://github.com/settings/tokens
2. 找到当前使用的 Token（名称可能是 quietview 或类似名称）
3. 点击 Edit → 勾选 `workflow` scope → 点击 Update token
4. 复制新生成的 token 值（只显示一次！）
5. 告诉喵子新的 token，喵子来更新 git remote 配置

**或者：**
1. 打开 https://github.com/settings/tokens/new
2. 新建 token，勾选 `repo` + `workflow` 两个 scope
3. 复制 token，告诉喵子

**workflow 文件已经准备好：**
- 本地路径：`/root/.openclaw/workspace/.github/workflows/fetch-data.yml`
- 获得新 token 后，喵子一条命令即可完成推送

---

## 访问地址
- Cloudflare Pages：https://quietview.pages.dev
- GitHub Pages（备选）：https://chunjie0320-stack.github.io/quietview
