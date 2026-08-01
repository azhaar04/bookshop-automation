# config.py

import pytesseract

# --- Tesseract OCR Path ---
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- Target Website ---
BASE_URL = "https://bookshop.org/"

# --- File Paths ---
BOOKS_DATA_PATH = "data/books.json"
SEARCH_BOX_TEMPLATE = "templates/search_box.png"
OUTPUT_PATH = "output/result.json"

# --- Template Matching Confidence ---
CONFIDENCE = 0.8

# --- Timing Settings (seconds) ---
PAGE_LOAD_WAIT = 3         
SEARCH_RESULT_WAIT = 4
BOOK_PAGE_WAIT = 2         
TYPE_INTERVAL = 0.05      

# --- OCR Settings ---
OCR_PSM_MODE = "--psm 6"  

RESULTS_REGION_TOP_OFFSET = 450