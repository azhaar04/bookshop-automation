import pyautogui
import config
import pytesseract
from pytesseract import Output

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


def find_book_result(title_keyword, author_keyword, region=None):
    """
    Searches the search-results grid for a card whose title matches
    `title_keyword` AND has a line just below it (in the same column)
    matching `author_keyword`.
    """
    print(f"[INFO] Looking for title '{title_keyword}' with author '{author_keyword}'...")

    if region:
        screenshot = pyautogui.screenshot(region=region)
        offset_x, offset_y = region[0], region[1]
    else:
        screenshot = pyautogui.screenshot()
        offset_x, offset_y = 0, 0

    data = pytesseract.image_to_data(
        screenshot,
        output_type=Output.DICT,
        config=config.OCR_PSM_MODE
    )

    words = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text:
            words.append({
                "text": text,
                "left": data['left'][i],
                "top": data['top'][i],
                "width": data['width'][i],
                "height": data['height'][i],
            })

    words.sort(key=lambda w: (w["top"], w["left"]))

    LINE_TOLERANCE = 10
    MAX_HORIZONTAL_GAP = 100

    lines = []
    current_line = []
    current_top = None
    prev_right = None

    for w in words:
        same_row = current_top is not None and abs(w["top"] - current_top) <= LINE_TOLERANCE
        close_enough = prev_right is not None and (w["left"] - prev_right) <= MAX_HORIZONTAL_GAP

        if same_row and close_enough:
            current_line.append(w)
        else:
            if current_line:
                lines.append(current_line)
            current_line = [w]
            current_top = w["top"]

        current_top = w["top"]
        prev_right = w["left"] + w["width"]

    if current_line:
        lines.append(current_line)

    line_info = []
    for line in lines:
        text = " ".join(w["text"] for w in line)
        left = min(w["left"] for w in line)
        top = min(w["top"] for w in line)
        width = max(w["left"] + w["width"] for w in line) - left
        height = max(w["height"] for w in line)
        line_info.append({"text": text, "left": left, "top": top, "width": width, "height": height})

    # --- geometric matching instead of index-based "next line" ---
    HORIZONTAL_ALIGN_TOLERANCE = 60   # same column allowance
    MAX_VERTICAL_GAP_TO_AUTHOR = 150  # allows for a wrapped 2nd title line + author line below

    title_candidates = [
        line for line in line_info
        if not line["text"].isupper() and title_keyword.lower() in line["text"].lower()
    ]

    for title_line in title_candidates:
        title_bottom = title_line["top"] + title_line["height"]

        for line in line_info:
            if line is title_line:
                continue

            same_column = abs(line["left"] - title_line["left"]) <= HORIZONTAL_ALIGN_TOLERANCE
            below_title = 0 <= (line["top"] - title_bottom) <= MAX_VERTICAL_GAP_TO_AUTHOR

            if same_column and below_title and author_keyword.lower() in line["text"].lower():
                x = offset_x + title_line["left"] + title_line["width"] // 2
                y = offset_y + title_line["top"] + title_line["height"] // 2
                print(f"[INFO] Confirmed: '{title_line['text']}' -> '{line['text']}'")
                return (x, y)

    print(f"[WARNING] No confident match for title '{title_keyword}' + author '{author_keyword}'.")
    return None