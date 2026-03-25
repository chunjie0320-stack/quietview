#!/usr/bin/env python3
"""
fetch_market_data.py
抓取A股行情数据（最近30天日K线）：
  - 上证指数: 000001.SH (akshare symbol: sh000001)
  - 科创50:   000688.SH (akshare symbol: sh000688)
输出：/root/.openclaw/workspace/data/market_data.json
格式：{sh: [...], kc50: [...], updated_at: "YYYY-MM-DD HH:MM"}
"""

import json
import os
from datetime import datetime, timedelta

OUTPUT_PATH = "/root/.openclaw/workspace/data/market_data.json"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


def fetch_index_kline(symbol: str, name: str, days: int = 30) -> list:
    """
    用 akshare 抓取指数日K线数据
    symbol: 如 "sh000001"（上证）、"sh000688"（科创50）
    """
    try:
        import akshare as ak

        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days + 10)).strftime("%Y%m%d")

        # akshare 获取指数日K线
        df = ak.stock_zh_index_daily(symbol=symbol)

        if df is None or df.empty:
            print(f"[{name}] 返回空数据")
            return []

        # 过滤最近N天
        df = df.tail(days).copy()

        # 统一列名（akshare不同版本列名可能不同）
        col_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'date' in col_lower or '日期' in col_lower:
                col_map[col] = 'date'
            elif col_lower in ('open', '开盘', '今开'):
                col_map[col] = 'open'
            elif col_lower in ('high', '最高', '高'):
                col_map[col] = 'high'
            elif col_lower in ('low', '最低', '低'):
                col_map[col] = 'low'
            elif col_lower in ('close', '收盘', '今收'):
                col_map[col] = 'close'
            elif col_lower in ('volume', '成交量', '手'):
                col_map[col] = 'volume'

        df = df.rename(columns=col_map)

        result = []
        for _, row in df.iterrows():
            try:
                date_val = row.get('date', '')
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime("%Y-%m-%d")
                else:
                    date_str = str(date_val)[:10]

                result.append({
                    "date": date_str,
                    "open": round(float(row.get('open', 0)), 2),
                    "high": round(float(row.get('high', 0)), 2),
                    "low": round(float(row.get('low', 0)), 2),
                    "close": round(float(row.get('close', 0)), 2),
                    "volume": int(float(row.get('volume', 0)))
                })
            except (ValueError, TypeError) as e:
                print(f"[{name}] 行解析跳过: {e}")
                continue

        print(f"[{name}] 成功，共 {len(result)} 条K线")
        return result

    except ImportError:
        print(f"[{name}] akshare 未安装，跳过")
        return []
    except Exception as e:
        print(f"[{name}] 抓取失败: {e}")
        return []


def fetch_index_kline_alt(symbol_code: str, name: str, days: int = 30) -> list:
    """
    备用方案：akshare stock_zh_index_daily_em（东方财富版本）
    symbol_code: "000001"（不含sh前缀）
    """
    try:
        import akshare as ak
        df = ak.stock_zh_index_daily_em(symbol=symbol_code)

        if df is None or df.empty:
            return []

        df = df.tail(days).copy()

        result = []
        for _, row in df.iterrows():
            try:
                date_val = row.iloc[0] if len(row) > 0 else ''
                date_str = str(date_val)[:10] if date_val else ''

                result.append({
                    "date": date_str,
                    "open": round(float(row.get('开盘', row.get('open', 0))), 2),
                    "high": round(float(row.get('最高', row.get('high', 0))), 2),
                    "low": round(float(row.get('最低', row.get('low', 0))), 2),
                    "close": round(float(row.get('收盘', row.get('close', 0))), 2),
                    "volume": int(float(row.get('成交量', row.get('volume', 0))))
                })
            except Exception:
                continue

        print(f"[{name}-备用] 成功，共 {len(result)} 条K线")
        return result

    except Exception as e:
        print(f"[{name}-备用] 也失败: {e}")
        return []


def main():
    print("📊 开始抓取行情数据...")

    # 上证指数
    sh_data = fetch_index_kline("sh000001", "上证指数")
    if not sh_data:
        sh_data = fetch_index_kline_alt("000001", "上证指数")

    # 科创50
    kc50_data = fetch_index_kline("sh000688", "科创50")
    if not kc50_data:
        kc50_data = fetch_index_kline_alt("000688", "科创50")

    output = {
        "sh": sh_data,
        "kc50": kc50_data,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 完成！")
    print(f"   上证指数: {len(sh_data)} 条")
    print(f"   科创50:   {len(kc50_data)} 条")
    print(f"   → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
