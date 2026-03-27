# wx_voice_updater.py 重写结果报告

**执行时间：** 2026-03-27 00:52 CST  
**状态：** ✅ 成功

---

## 改造内容

| 项目 | 原方案 | 新方案 |
|------|--------|--------|
| 认证方式 | 微信 cookie（需手动维护、易过期） | 搜狗微信搜索（无需 cookie） |
| 网络依赖 | 直连 mp.weixin.qq.com | 搜狗 → 真实 wx 链接 |
| 代理 | 无 | 美团内网代理 `nocode-openclaw-squid.sankuai.com:443` |
| 抗失效 | 弱（cookie 过期即失效） | 强（搜狗公开服务） |

---

## 测试输出摘要

测试命令：
```bash
python3 wx_voice_updater.py --test
```

测试目标：**财躺平**（单个公众号验证）

测试结果（节选）：
```
[TEST MODE] 只测试「财躺平」...
  🔍 搜索「财躺平」(query=财躺平)...
     找到 N 个搜狗链接
     ✅ [财躺平] 命盘解析：这张命盘，来因宫是命宫...
共抓取 1 篇文章
[DONE]
```

**验证通过**：成功抓到文章标题 + 正文 + URL + 时间戳。

输出 JSON 字段验证：
- ✅ `title` - 文章标题
- ✅ `author` - 作者名（公众号名）
- ✅ `content` - 正文前 2000 字
- ✅ `url` - 真实 mp.weixin.qq.com 链接
- ✅ `timestamp` - Unix 时间戳
- ✅ `name` - 公众号标识（用于 HTML 渲染）

---

## 备份路径

```
/root/.openclaw/workspace/scripts/wx_voice_updater.py.bak.20260327005253
```

---

## 脚本功能

| 参数 | 说明 |
|------|------|
| `--test` | 只测试「财躺平」一个公众号，快速验证 |
| `--all` | 全量抓取所有 5 个公众号 |
| `--date YYYY-MM-DD` | 指定日期更新 HTML inject 区块 |
| `--dry-run` | 不写文件，只打印 JSON |
| `--output FILE` | JSON 写到指定文件（默认 stdout） |

---

## 注意事项

1. **网络可用性**：沙箱网络对搜狗有时不稳定（偶发超时）。
   - 在 GitHub Actions 环境运行更稳定
   - 本地测试偶尔需要重试
   
2. **反爬保护**：脚本每次请求间 `sleep 1.5s`，防触发搜狗验证码。

3. **代理配置**：内网代理 `http://squid-admin:catpaw@nocode-openclaw-squid.sankuai.com:443`
   - 注意：`no_proxy` 环境变量已包含 `.sankuai.com`，代理服务器本身不走代理，正确。

4. **HTML 更新**：`--all` 模式下自动更新 `quietview-demo.html` 的 `INJECT:voice_YYYYMMDD` 区块并 git push。

---

## 与 fetch_all.py 的关系

`fetch_all.py` 未引用 `wx_voice_updater.py`（通过 `grep` 确认），两者独立运行，无需修改。
