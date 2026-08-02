import webbrowser
import time
import pyautogui
import pygetwindow as gw
import config


def open_browser():
    print("[INFO] Launching browser...")
    webbrowser.open(config.BASE_URL)

    print(f"[INFO] Waiting {config.PAGE_LOAD_WAIT} seconds for page to load...")
    time.sleep(config.PAGE_LOAD_WAIT)

    try:
        window = gw.getActiveWindow()
        if window:
            window.maximize()
            print(f"[INFO] Maximized window: {window.title}")
        else:
            print("[WARNING] No active window detected.")
    except Exception as e:
        print(f"[WARNING] Failed to maximize window: {e}")

    time.sleep(1)
    print("[INFO] Browser opened and maximized.")


def scroll_to_top():
    print("[INFO] Scrolling back to top of page...")
    pyautogui.press('home')
    time.sleep(0.5)