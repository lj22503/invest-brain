# desktop/tests/e2e_tauri_health.py
# Plan 5 任务 6：Tauri UI 上点 health_check → 返回 ok。


def test_health_check_button(tauri_app):
    """Tauri UI 上点 health_check → 返回 ok.

    假设：
    - tauri-driver 已启在 localhost:4444
    - Tauri 应用窗口已开
    - 在 /chat 路由（Plan 4 后的 in-app UI 路径）
    """
    page = tauri_app.new_page()
    page.goto("tauri://localhost/chat")
    # 等待侧栏 PacksBadge 加载完成（health_check 调用）
    # 成功条件：状态栏出现 "ok"
    page.wait_for_selector("text=ok", timeout=15_000)