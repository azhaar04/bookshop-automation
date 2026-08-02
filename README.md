# Bookshop.org EAN/UPC Automation

A Python script that finds books on [bookshop.org](https://bookshop.org/) and collects their
EAN/UPC value, using only what a human would see on screen — no Selenium, no Playwright, no
DOM/HTML access, no DevTools. It opens a real, visible browser, reads the page with OCR, and
controls the mouse/keyboard to search, click, and scroll.

`data/books.json` lists multiple books with a range of different covers and layouts, to check how
well the OCR matching holds up across them. Results for all of them are in `output/result.json`.

## How it works

1. **Open the browser** — opens the system's default browser and goes to `https://bookshop.org/`.
   Always a real, visible window, never headless.
2. **Find the search box** — takes a screenshot and locates the search box on screen using template
   matching (`templates/search_box.png`).
3. **Search** — clicks the search box and types `"<title> by <authors>"`.
4. **Pick the right result** — screenshots the results and runs OCR on them. Words are grouped into
   columns (one per book card) and lines. It looks for a title line with a keyword from the book's
   title, then checks a nearby line for a keyword from the author's name, and clicks that card.
5. **Get the EAN/UPC** — scrolls down the book's page a bit at a time, OCR-ing after each scroll,
   until it finds the EAN/UPC label and reads the number next to it.
6. **Next book** — scrolls back to the top and reuses the same search box (bookshop.org keeps a
   search box in the header on every page, and it's already empty after a search), instead of
   reloading the homepage each time.
7. **Save results** — writes everything to `output/result.json`.

## Setup

You need Python 3 and [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed.
This was built on Windows with Tesseract at `C:\Program Files\Tesseract-OCR\tesseract.exe` — change
the path in `config.py` if yours is somewhere else.

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

Don't touch the mouse or keyboard while it's running — it's controlling your actual browser window.
If a book can't be found, its entry just gets `"EAN/UPC": null` with a short note, and the script
keeps going instead of stopping.

To search for different books, edit `data/books.json`. Each entry needs one distinctive keyword
from the title and one from the author's name for the OCR matching — try to pick a word that won't
also show up in a different, similar book on the site.

## Known limitations

This is screenshot- and OCR-based, so it's tuned to the setup it was built on (Windows, this
screen's resolution, Microsoft Edge). On a different screen size or browser, the search box
template and the OCR region offsets in `config.py` might need to be redone. Since it reads the page
visually every time, an occasional OCR misread (like a blurry format label) can cause it to click
the wrong result — that's the trade-off of not touching the DOM at all.
