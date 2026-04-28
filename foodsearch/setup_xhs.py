#!/usr/bin/env python3
"""
setup_xhs.py
用 playwright 打开小红书登录页，用户扫码/账密登录后自动保存 Cookie。
适用于 Mac 本地运行（需要有界面）。

Usage:
  python setup_xhs.py
"""

from playwright.sync_api import sync_playwright
import json, os


def setup_xhs_cookie():
    print("=" * 50)
    print("🍠 小红书 Cookie 自动获取工具")
    print("=" * 50)
    print("正在打开小红书登录页...")
    print("请在弹出的浏览器窗口中完成登录（扫码或账密均可）")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 必须有界面
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto("https://www.xiaohongshu.com")

        input("👉 登录完成后，回到此终端按回车保存 Cookie...")

        cookies = context.cookies()
        browser.close()

    # 提取关键字段
    cookie_map = {c["name"]: c["value"] for c in cookies}
    a1 = cookie_map.get("a1", "")
    web_session = cookie_map.get("web_session", "")

    if not a1 or not web_session:
        print()
        print("⚠️  未检测到 a1 / web_session，可能登录未完成。")
        print("   请重新运行 setup_xhs.py 并确保在浏览器中完成登录。")
        return

    os.makedirs("cookies", exist_ok=True)

    # 保存简化格式（与 xhs-fetch-with-cookie.py 兼容）
    simplified = {"a1": a1, "web_session": web_session}
    with open("cookies/xhs.json", "w", encoding="utf-8") as f:
        json.dump(simplified, f, ensure_ascii=False, indent=2)

    print()
    print(f"✅ Cookie 已保存到 cookies/xhs.json")
    print(f"   a1:          {a1[:10]}...{a1[-4:]}")
    print(f"   web_session: {web_session[:10]}...{web_session[-4:]}")
    print()
    print("现在可以启动服务：python app.py")


if __name__ == "__main__":
    setup_xhs_cookie()
