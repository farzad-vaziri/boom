# نشر بوم — Boom Publishing website

Static Persian (RTL) site served by GitHub Pages at https://farzad-vaziri.github.io/boom/

- `index.html`, `books/`, `category/`, `people/`, `tags/`, `library.html`, `search.html`, `about.html` — generated pages
- `assets/` — CSS, JS, Vazirmatn font (OFL licence), logo, covers, 2-page sample PDFs and previews
- `_build/` — `books.json` (book data taken from the .docx files), `prep.py` (covers and samples), `build.py` (page generator)

To rebuild after editing `_build/books.json` (for example, filling in the `price` field):

    python3 _build/build.py _build/books.json .
