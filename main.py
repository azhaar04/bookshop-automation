import json
import os
import time

from automation.browser import open_browser, scroll_to_top
from automation.vision import locate_search_box, find_book_result, extract_ean_upc
from automation.controller import click_at, type_text, press_enter
import config
import pyautogui


def load_books():
    with open(config.BOOKS_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    books = load_books()
    results = {}

    open_browser()
    screen_width, screen_height = pyautogui.size()
    results_region = (0, config.RESULTS_REGION_TOP_OFFSET, screen_width, screen_height - config.RESULTS_REGION_TOP_OFFSET)

    for i, book in enumerate(books):
        print(f"\n[INFO] === Book {i + 1}/{len(books)}: {book['title']} ===")

        if i > 0:
            scroll_to_top()

        search_box_position = locate_search_box()
        if not click_at(search_box_position):
            results[book["title"]] = {
                "authors": book["authors"],
                "EAN/UPC": None,
                "note": "Search box not found"
            }
            continue

        type_text(f"{book['title']} by {book['authors']}")
        press_enter()
        time.sleep(config.SEARCH_RESULT_WAIT)

        position = find_book_result(
            title_keyword=book["title_keyword"],
            author_keyword=book["author_keyword"],
            region=results_region
        )

        if position is None:
            results[book["title"]] = {
                "authors": book["authors"],
                "EAN/UPC": None,
                "note": "Book not found in search results"
            }
            continue

        click_at(position)
        time.sleep(config.BOOK_PAGE_WAIT)

        ean_upc = extract_ean_upc()
        results[book["title"]] = {
            "authors": book["authors"],
            "EAN/UPC": ean_upc
        }

    os.makedirs(os.path.dirname(config.OUTPUT_PATH), exist_ok=True)
    with open(config.OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"\n[INFO] Results saved to {config.OUTPUT_PATH}")


if __name__ == "__main__":
    main()
