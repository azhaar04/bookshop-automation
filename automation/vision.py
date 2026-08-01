import re
import bisect
import time

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


def _contains_word(text, keyword):
    return re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE) is not None


_FORMAT_KEYWORDS = {"paperback", "hardcover", "ebook", "audiobook"}
_ANCHOR_MIN_CONFIDENCE = 40


def _is_anchor_word(word):
    if word["conf"] < _ANCHOR_MIN_CONFIDENCE:
        return False

    return word["text"].strip().lower() in _FORMAT_KEYWORDS


def _detect_columns(words):
    BIN_SIZE = 15

    anchor_lefts = sorted(w["left"] for w in words if _is_anchor_word(w))

    anchors = []
    for left in anchor_lefts:
        b = round(left / BIN_SIZE) * BIN_SIZE
        if anchors and (b - anchors[-1]) <= BIN_SIZE:
            continue
        anchors.append(b)

    if not anchors:
        return []

    columns = [[] for _ in anchors]
    for w in words:
        idx = bisect.bisect_right(anchors, w["left"]) - 1
        columns[max(idx, 0)].append(w)

    return columns


def _build_lines(column_words):
    LINE_TOLERANCE = 10
    MAX_HORIZONTAL_GAP = 60  # words within one card sit close together

    column_words = sorted(column_words, key=lambda w: (w["top"], w["left"]))

    lines = []
    current_line = []
    current_top = None
    prev_right = None

    for w in column_words:
        same_row = current_top is not None and abs(w["top"] - current_top) <= LINE_TOLERANCE
        close_enough = prev_right is not None and (w["left"] - prev_right) <= MAX_HORIZONTAL_GAP

        if same_row and close_enough:
            current_line.append(w)
        else:
            if current_line:
                lines.append(current_line)
            current_line = [w]

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

    return line_info


def find_book_result(title_keyword, author_keyword, region=None):
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
                "conf": int(data['conf'][i]),
            })

    columns = _detect_columns(words)
    if not columns:
        print("[WARNING] Could not detect any result columns.")
        return None

    MAX_VERTICAL_GAP_TO_AUTHOR = 150  # allows for a wrapped 2nd title line + author line below

    column_matches = []

    for column_words in columns:
        line_info = _build_lines(column_words)

        title_candidates = [
            line for line in line_info
            if not line["text"].isupper() and _contains_word(line["text"], title_keyword)
        ]

        best_in_column = None
        best_gap = None

        for title_line in title_candidates:
            title_bottom = title_line["top"] + title_line["height"]

            for line in line_info:
                if line is title_line or line["text"].isupper():
                    continue

                gap = line["top"] - title_bottom
                if 0 <= gap <= MAX_VERTICAL_GAP_TO_AUTHOR and _contains_word(line["text"], author_keyword):
                    if best_gap is None or gap < best_gap:
                        x = offset_x + title_line["left"] + title_line["width"] // 2
                        y = offset_y + title_line["top"] + title_line["height"] // 2
                        best_in_column = (x, y, title_line["text"], line["text"])
                        best_gap = gap

        if best_in_column:
            column_matches.append(best_in_column)

    if not column_matches:
        print(f"[WARNING] No confident match for title '{title_keyword}' + author '{author_keyword}'.")
        return None

    if len(column_matches) > 1:
        matched_titles = ", ".join(f"'{m[2]}'" for m in column_matches)
        print(f"[WARNING] Keyword '{title_keyword}' matched {len(column_matches)} different "
              f"cards ({matched_titles}) — it may be too generic. Using the leftmost match.")

    x, y, title_text, author_text = column_matches[0]
    print(f"[INFO] Confirmed: '{title_text}' -> '{author_text}'")
    return (x, y)


_EAN_UPC_PATTERN = re.compile(
    r"EAN\s*/?\s*UPC[:\s]*((?:\d[\s\-]*){13})",
    re.IGNORECASE
)


def extract_ean_upc(max_scroll_attempts=8, scroll_amount=-600, scroll_wait=0.5):
    
    print("[INFO] Looking for EAN/UPC on the book page...")

    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(screen_width // 2, screen_height // 2)

    for attempt in range(max_scroll_attempts):
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot, config=config.OCR_PSM_MODE)

        match = _EAN_UPC_PATTERN.search(text)
        if match:
            ean_upc = re.sub(r"[\s\-]", "", match.group(1))
            print(f"[INFO] Found EAN/UPC: {ean_upc}")
            return ean_upc

        pyautogui.scroll(scroll_amount)
        time.sleep(scroll_wait)

    print("[WARNING] EAN/UPC not found after scrolling.")
    return None