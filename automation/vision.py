import pyautogui
import config

def locate_search_box():
    print("[INFO] Locating search box...")
    center = pyautogui.locateCenterOnScreen(
        config.SEARCH_BOX_TEMPLATE,
        confidence=config.CONFIDENCE
    )

    if center:
        print(f"[INFO] Search box found at: {center}")
    else:
        print("[WARNING] Search box not found on screen.")

    return center