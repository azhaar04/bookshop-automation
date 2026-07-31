# test_browser.py
# test_vision.py

import time
from automation.browser import open_browser
from automation.vision import locate_search_box

open_browser()
time.sleep(1)

result = locate_search_box()
print("Result:", result)