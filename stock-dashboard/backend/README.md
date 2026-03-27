# A股信息驾驶舱 - 后端

项目ID: opc-20260321-001

## 快速启动

```bash
cd /root/.openclaw/workspace/stock-dashboard/backend
pip3 install -r requirements.txt
python app.py
```

服务启动后监听 `http://0.0.0.0:5001`，同时后台预热所有股票行情缓存。

## API接口

### GET /api/market — 大盘数据
```json
{
  "success": true,
  "data": {
    "indices": [
      {"code": "000001.SH", "name": "上证指数", "price": 3957.05, "change": -49.78, "pct_chg": -1.24},
      {"code": "000688.SH", "name": "科创50", "price": 1318.31, "change": -20.8, "pct_chg": -1.55}
    ],
    "market_stats": {"up": 6, "down": 14, "flat": 0, "note": "基于自选股统计（共20只）"},
    "sectors": {
      "电力设备": {"pct_chg": -2.115, "stock_count": 12},
      "固态电池": {"pct_chg": -0.37, "stock_count": 8}
    }
  },
  "timestamp": "2026-03-21T15:01:29...."
}
```

### GET /api/stocks — 股票列表实时行情
返回所有20只股票，按电力设备/固态电池分组。
字段：symbol, name, price, change, pct_chg, volume, amount, high, low, open, prev_close, time, group

### GET /api/kline?symbol=603308&period=daily&count=60 — K线数据
- period: `daily`（日K）或 `minute`（5分钟K，最近一个交易日）
- 返回字段: date, open, close, high, low, volume, ma5, ma10, ma20, boll_upper, boll_mid, boll_lower

### GET /api/news?symbol=603308&limit=20 — 个股新闻
- level: `major`（重大）/ `normal`（研报）/ `industry`（行业）

### GET /api/announcements — 公告走马灯
- 返回所有自选股最近5条公告/新闻
- 主接口：巨潮资讯；备用：东方财富新闻

## 缓存策略
| 接口 | TTL |
|------|-----|
| 实时行情 | 60秒 |
| K线数据 | 5分钟 |
| 新闻/公告 | 10分钟 |

## 数据源可用性（当前环境）

| akshare接口 | 状态 | 说明 |
|-------------|------|------|
| `stock_individual_spot_xq` | ✅ 可用 | 雪球，实时行情 |
| `stock_zh_a_minute` | ✅ 可用 | 新浪，分钟/日K |
| `stock_news_em` | ✅ 可用 | 东方财富，新闻 |
| `stock_zh_a_disclosure_report_cninfo` | ⚠️ 不稳定 | 巨潮，公告（有时超时，自动降级到新闻） |
| `stock_zh_a_spot_em` | ❌ 不可用 | 东方财富push服务不可达 |
| `stock_zh_a_hist` | ❌ 不可用 | 东方财富push服务不可达 |
| `stock_zh_index_spot_em` | ❌ 不可用 | 东方财富push服务不可达 |
