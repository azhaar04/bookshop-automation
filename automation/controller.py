import pyautogui
import time
import config

def click_at(point):
    if point is None:
        print("[WARNING] Cannot click — no coordinate provided.")
        return False

    pyautogui.click(point)
    print(f"[INFO] Clicked at: {point}")
    time.sleep(0.5)
    return True


def type_text(text):
    pyautogui.typewrite(text, interval=config.TYPE_INTERVAL)
    print(f"[INFO] Typed: {text}")


def press_enter():
    pyautogui.press("enter")
    print("[INFO] Pressed Enter.")