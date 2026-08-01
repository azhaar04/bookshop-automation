import time
from automation.browser import open_browser
from automation.vision import find_book_result, locate_search_box
from automation.controller import click_at, type_text, press_enter
import config
import pyautogui

open_browser()
time.sleep(1)
screen_width, screen_height = pyautogui.size()
results_region = (0, config.RESULTS_REGION_TOP_OFFSET, screen_width, screen_height - config.RESULTS_REGION_TOP_OFFSET)

search_box_position = locate_search_box()
if click_at(search_box_position):
    type_text("God Doesn't Relapse by Matt Grace ")
    press_enter()

time.sleep(config.SEARCH_RESULT_WAIT)

book_position = find_book_result(
    title_keyword="doesn't",
    author_keyword="Grace",
    region=results_region
)

print("Book found at:", book_position)

if book_position:
    click_at(book_position)