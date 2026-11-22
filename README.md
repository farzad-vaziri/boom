# نشر بوم — Boom Publishing website

Static Persian (RTL) site served by GitHub Pages at https://farzad-vaziri.github.io/boom/

- `index.html`, `books/`, `category/`, `people/`, `tags/`, `library.html`, `search.html`, `about.html` — generated pages
- `assets/` — CSS, JS, Vazirmatn font (OFL licence), logo, covers, 2-page sample PDFs and previews
- `_build/` — `books.json` (book data taken from the .docx files), `prep.py` (covers and samples), `build.py` (page generator)

Membership (Supabase project `boom`, London): `assets/js/member.js` handles sign-up/login and full-book downloads; `assets/js/vendor/supabase.js` is supabase-js v2 (MIT). Book levels live in the Supabase `books` table (0 public, 1 members, 2 full members); member levels in `members` (1 basic, 2 full). The full PDFs are in the private `books` storage bucket as `<slug>.pdf`.

To rebuild after editing `_build/books.json` (for example, filling in the `price` field):

    python3 _build/build.py _build/books.json .
