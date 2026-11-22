#!/usr/bin/env python3
"""Static site generator for نشر بوم. Reads books.json, writes HTML into the site folder."""
import json, os, html, re, sys
from collections import OrderedDict

DATA = sys.argv[1] if len(sys.argv) > 1 else 'books.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'site'
books = json.load(open(DATA, encoding='utf-8'))
books.sort(key=lambda b: -b['date_key'])
E = lambda s: html.escape(s or '', quote=True)
FA = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
fa = lambda n: str(n).translate(FA)

CATS = OrderedDict([
    ('plays', ('نمایشنامه', 'متن‌هایی برای صحنه؛ از درام پسامدرن تا نمایشنامه‌های اجتماعی', 'mask')),
    ('theatre-theory', ('نظریه‌ی تئاتر', 'اندیشیدن به صحنه، تصویر و تماشاگر', 'columns')),
    ('cinema', ('سینما', 'از اتاق تدوین تا تاریخ سینمای تجربی', 'film')),
    ('literature', ('ادبیات', 'داستان و شعر از ادبیات جهان', 'feather')),
    ('thought', ('اندیشه و جامعه', 'فرهنگ، اقتصاد و جهانی که در آن زندگی می‌کنیم', 'bulb')),
])

PEOPLE_SLUGS = {
    'تام استوپارد': 'tom-stoppard', 'احسان زیورعالم': 'ehsan-zivaralam', 'مسعود خانی': 'masoud-khani',
    'ویلم میدلکوپ': 'willem-middelkoop', 'محمد فتحی سردهایی': 'mohammad-fathi-sardahaei',
    'آرنولد وسکر': 'arnold-wesker', 'سیدهادی سیدسجادی': 'seyedhadi-seyedsajadi', 'جو کلهر': 'joe-kelleher',
    'دیوید آیوز': 'david-ives', 'دیوید ایوز': 'david-ives-2', 'والتر مرچ': 'walter-murch',
    'مارتین پوکنر': 'martin-puchner', 'امیر یغمایی': 'amir-yaghmaei', 'کریستینا پری رسی': 'cristina-peri-rossi',
    'استودیو متفه': 'studio-motafe',
}
ROLE_FA = {'author': 'نویسنده', 'translator': 'مترجم', 'editor': 'ویراستار', 'design': 'طراحی'}

ICONS = {
    'home': '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-6h4v6"/>',
    'mask': '<path d="M3 5c3 1.5 6 1.5 9 0v6a4.5 4.5 0 0 1-9 0z"/><path d="M12 9c3 1.5 6 1.5 9 0v6a4.5 4.5 0 0 1-9 0"/><path d="M6 9h.01M9 9h.01M15 14h.01M18 14h.01"/>',
    'columns': '<path d="M3 21h18M4 7h16M12 3 4 7M12 3l8 4"/><path d="M6 10v8M10 10v8M14 10v8M18 10v8"/>',
    'film': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 3v18M17 3v18M3 8h4M3 13h4M3 18h4M17 8h4M17 13h4M17 18h4"/>',
    'feather': '<path d="M20.2 12.2A6 6 0 0 0 11.8 3.8L5 10.6V19h8.4z"/><path d="M16 8 2 22M17.5 15H9"/>',
    'bulb': '<path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z"/>',
    'library': '<path d="M4 19.5V4.5A1.5 1.5 0 0 1 5.5 3H20v18H5.5A1.5 1.5 0 0 1 4 19.5z"/><path d="M4 19.5A1.5 1.5 0 0 1 5.5 18H20"/>',
    'users': '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="M16 3.5a4 4 0 0 1 0 9M22 21a7 7 0 0 0-4-6.3"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'moon': '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'right': '<path d="m9 6 6 6-6 6"/>', 'left': '<path d="m15 6-6 6 6 6"/>',
    'calendar': '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    'pages': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    'download': '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 21h14"/>',
    'eye': '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'share': '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    'send': '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
    'camera': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    'grid': '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    'lock': '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
}
def icon(name, cls='icon'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

# ---------- derived data ----------
people = OrderedDict()   # name -> {slug, roles:{role:set(book slugs)}}
def add_person(name, role, b):
    if not name: return
    p = people.setdefault(name, {'name': name, 'slug': PEOPLE_SLUGS.get(name, 'p%d' % len(people)), 'books': OrderedDict()})
    p['books'].setdefault(b['slug'], []).append(role)
for b in sorted(books, key=lambda b: b['date_key']):
    add_person(b.get('author'), 'author', b)
    if b.get('translator'): add_person(b['translator'], 'translator', b)
    for ed in b['editors']: add_person(ed, 'editor', b)
    if b.get('design'): add_person(b['design'], 'design', b)
by_slug = {b['slug']: b for b in books}

tags = OrderedDict()
for b in books:
    for t in b['tags']:
        tags.setdefault(t, []).append(b['slug'])
tag_slug = {t: 't%d' % (i + 1) for i, t in enumerate(tags)}
tags_by_pop = sorted(tags, key=lambda t: (-len(tags[t]), list(tags).index(t)))

def credits_line(b):
    s = E(b['author'])
    if b.get('translator'): s += '، ترجمه‌ی ' + E(b['translator'])
    return s

# ---------- layout ----------
def layout(title, body, depth=0, active=None, desc=None):
    r = '../' * depth
    nav_items = [('home', 'خانه', 'index.html', 'home')] + \
        [(k, v[0], f'category/{k}.html', v[2]) for k, v in CATS.items()] + \
        [('library', 'همه‌ی آثار', 'library.html', 'library'), ('people', 'پدیدآورندگان', 'people.html', 'users')]
    nav = ''.join(f'<li><a href="{r}{u}" class="{"active" if k == active else ""}">{icon(ic)}{E(lbl)}</a></li>' for k, lbl, u, ic in nav_items)
    nav += f'<li class="push"><a href="{r}about.html" class="accent {"active" if active == "about" else ""}">{icon("info")}درباره‌ی ما</a></li>'
    bottom = [('home', 'خانه', 'index.html', 'home'), ('library', 'آثار', 'library.html', 'grid'),
              ('search', 'جست‌وجو', 'search.html', 'search'), ('people', 'پدیدآورندگان', 'people.html', 'users'), ('about', 'درباره', 'about.html', 'info')]
    bnav = ''.join(f'<a href="{r}{u}" class="{"active" if k == active else ""}">{icon(ic)}{lbl}</a>' for k, lbl, u, ic in bottom)
    full_title = f'{title} | نشر بوم' if title != 'نشر بوم' else 'نشر بوم'
    return f'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc or 'نشر بوم؛ نمایشنامه، نظریه‌ی تئاتر، سینما، ادبیات و اندیشه.')}">
<link rel="icon" href="{r}assets/img/logo-dark.svg" type="image/svg+xml">
<link rel="preload" href="{r}assets/fonts/Vazirmatn.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/css/style.css">
<script>try{{var t=localStorage.getItem('boom-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
</head>
<body>
<header class="site-header">
  <div class="container header-top">
    <a class="brand" href="{r}index.html"><img class="logo-dark" src="{r}assets/img/logo-dark.svg" alt=""><img class="logo-light" src="{r}assets/img/logo-light.svg" alt="">نشر بوم</a>
    <form class="search" action="{r}search.html" role="search">
      <input type="search" name="q" placeholder="جست‌وجو در نشر بوم..." aria-label="جست‌وجو">
      <button type="submit" aria-label="جست‌وجو">{icon('search')}</button>
    </form>
    <div class="header-actions">
      <button class="btn-ghost auth-btn" type="button" id="auth-btn" aria-haspopup="dialog">{icon('user')}<span class="lbl">ورود | ثبت‌نام</span></button>
      <button class="icon-btn theme-toggle" type="button" aria-label="تغییر حالت روز و شب">{icon('moon', 'icon moon')}{icon('sun', 'icon sun')}</button>
    </div>
  </div>
  <nav class="main-nav"><div class="container"><ul>{nav}</ul></div></nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="container footer-cta">
    <div><h3>کتاب‌های نشر بوم را ورق بزنید</h3><p>برای هر اثر، نمونه‌ای از متن کتاب را رایگان ببینید.</p></div>
    <a class="btn-gold" href="{r}library.html">{icon('library')}همه‌ی آثار</a>
  </div>
  <div class="container footer-grid">
    <div class="footer-brand">
      <img class="logo-dark" src="{r}assets/img/logo-dark.svg" alt="نشر بوم"><img class="logo-light" src="{r}assets/img/logo-light.svg" alt="نشر بوم">
      <p>نشر بوم؛ خانه‌ی نمایشنامه، نظریه‌ی تئاتر، سینما، ادبیات و اندیشه.</p>
    </div>
    <div><h4>بیش‌تر بدانید</h4><ul>
      <li><a href="{r}people.html">پدیدآورندگان</a></li>
      <li><a href="{r}about.html">داستان ما</a></li>
      <li><a href="{r}about.html#collab">همکاری با ما</a></li>
      <li><a href="{r}about.html#contact">ارتباط با ما</a></li>
    </ul></div>
    <div><h4>همراه ما باشید</h4><ul class="social">
      <li>{icon('camera')}<b>اینستاگرام:</b> —</li>
      <li>{icon('send')}<b>تلگرام:</b> —</li>
      <li>{icon('mail')}<b>ایمیل:</b> —</li>
    </ul></div>
    <div><h4>خبرنامه‌ی نشر بوم</h4><p>تازه‌های نشر بوم را در ایمیل خود بخوانید.</p>
      <div class="newsletter"><input type="email" placeholder="ایمیل شما" disabled aria-label="ایمیل"><span class="btn-gold" aria-disabled="true">به‌زودی</span></div>
    </div>
  </div>
  <div class="copyright">© {fa(1405)} نشر بوم. تمامی حقوق محفوظ است.</div>
</footer>
<nav class="bottom-nav">{bnav}</nav>
<script src="{r}assets/js/main.js"></script>
<script src="{r}assets/js/vendor/supabase.js" defer></script>
<script src="{r}assets/js/member.js" defer></script>
</body>
</html>
'''

def cover_img(b, r, small=False, eager=False):
    src = f'{r}assets/covers/{b["slug"]}{"-sm" if small else ""}.jpg'
    return f'<img src="{src}" alt="{E("جلد " + b["title"])}"{"" if eager else " loading=lazy"}>'

def price_pill(b):
    return f'<span class="pill">{icon("lock")}{E(b["price"])}</span>' if b.get('price') else ''

def book_card(b, r):
    return f'<a class="book-card" href="{r}books/{b["slug"]}.html" data-title="{E(b["title"])}" data-date="{b["date_key"]}"><div class="cover">{cover_img(b, r, True)}</div><div><strong>{E(b["title"])}</strong><span>{E(b["author"])}</span>{price_pill(b)}</div></a>'

def shelf(title, sub, items, r, more=None):
    more_html = f'<a class="see-all" href="{more}">مشاهده‌ی همه{icon("left")}</a>' if more else ''
    sub_html = f'<p>{E(sub)}</p>' if sub else ''
    return f'''<section class="block"><div class="container">
<div class="sec-head"><div><h2>{E(title)}</h2>{sub_html}</div>{more_html}</div>
<div class="shelf-row">{"".join(book_card(b, r) for b in items)}</div>
</div></section>'''

def creator_html(p, r):
    roles = sorted({ROLE_FA[x] for rs in p['books'].values() for x in rs}, key=list(ROLE_FA.values()).index)
    return f'<a class="creator" href="{r}people/{p["slug"]}.html"><span class="avatar">{E(p["name"][0])}</span>{E(p["name"])}<small>{"، ".join(roles)}</small></a>'

def write(path, content):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full) or '.', exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)

# ---------- home ----------
def home():
    r = ''
    hero_books = books[:5]
    slides = ''
    for k, b in enumerate(hero_books):
        slides += f'''<div class="slide{" active" if k == 0 else ""}">
<div class="slide-bg" style="background-image:url('assets/covers/{b["slug"]}-sm.jpg')"></div>
<div class="container slide-inner">
  <div class="slide-text">
    <div class="slide-cat">{E(CATS[b["category"]][0])}</div>
    <h2 class="slide-title">{E(b["title"])}</h2>
    <div class="slide-credits">{credits_line(b)}</div>
    <p class="slide-excerpt">{E(b["about_book"][0])}</p>
    <a class="btn-gold" href="books/{b["slug"]}.html">مطالعه</a>
  </div>
  <a class="slide-cover" href="books/{b["slug"]}.html">{cover_img(b, r, eager=(k == 0))}</a>
</div></div>'''
    dots = ''.join(f'<button class="{"active" if k == 0 else ""}" aria-label="اسلاید {fa(k + 1)}"></button>' for k in range(len(hero_books)))
    hero = f'''<section class="hero"><div class="hero-track">{slides}</div>
<button class="hero-arrow prev" aria-label="قبلی">{icon("right")}</button><button class="hero-arrow next" aria-label="بعدی">{icon("left")}</button>
<div class="hero-dots">{dots}</div></section>'''

    feats = ''
    for b in books[:4]:
        feats += f'''<article class="feature">
<a class="cover" href="books/{b["slug"]}.html">{cover_img(b, r, True)}</a>
<div><div class="label">{E(CATS[b["category"]][0])}</div>
<h3><a href="books/{b["slug"]}.html">{E(b["title"])}</a></h3>
<div class="credits">{credits_line(b)}</div>
<p class="excerpt">{E(b["about_book"][0])}</p>
<div class="meta-row">{price_pill(b)}<span class="chip">{icon("calendar")}{E(b["date"])}</span><span class="chip">{icon("pages")}{fa(b["pages"])} صفحه</span></div></div>
</article>'''
    # editor's picks: oldest-first selection across categories, distinct from the 4 latest
    picks = [b for b in sorted(books, key=lambda b: b['date_key']) if b not in books[:4]][:5]
    rank = ''.join(f'<li><a href="books/{b["slug"]}.html"><span class="rank-num">{fa("%02d" % (k + 1))}</span><div><strong>{E(b["title"])}</strong><span>{E(b["author"])}</span></div><img src="assets/covers/{b["slug"]}-sm.jpg" alt="" loading="lazy"></a></li>' for k, b in enumerate(picks))
    cloud = ''.join(f'<a class="tag" href="tags/{tag_slug[t]}.html">{E(t)}</a>' for t in tags_by_pop[:16])
    latest = f'''<section class="block"><div class="container latest-grid">
<div><div class="sec-head"><div><h2>تازه‌های نشر بوم</h2></div><a class="see-all" href="library.html">مشاهده‌ی همه{icon("left")}</a></div>
<div class="feature-list">{feats}</div></div>
<aside><div class="side-card"><h3>پیشنهاد نشر بوم</h3><ol class="rank-list">{rank}</ol></div>
<div class="side-card"><h3>موضوع‌ها</h3><div class="tag-cloud">{cloud}</div></div></aside>
</div></section>'''

    shelves, small = '', []
    for k, (title, sub, _) in CATS.items():
        items = [b for b in books if b['category'] == k]
        if len(items) >= 3: shelves += shelf(title, sub, items, r, f'category/{k}.html')
        elif items: small.append((k, title, sub, items))
    if small:
        cols = ''.join(f'''<div class="mini-shelf"><div class="sec-head"><div><h2>{E(t)}</h2><p>{E(sb)}</p></div><a class="see-all" href="category/{k}.html">مشاهده‌ی همه{icon("left")}</a></div>
<div class="shelf-row">{"".join(book_card(b, r) for b in its)}</div></div>''' for k, t, sb, its in small)
        shelves += f'<section class="block"><div class="container mini-grid">{cols}</div></section>'

    creators = ''.join(creator_html(p, r) for p in people.values())
    creators_sec = f'''<section class="block"><div class="container">
<div class="sec-head"><div><h2>پدیدآورندگان</h2></div><a class="see-all" href="people.html">مشاهده‌ی همه{icon("left")}</a></div>
<div class="creators-row">{creators}</div></div></section>'''

    total_pages = sum(b['pages'] for b in books)
    stats = f'''<section class="pub-stats"><div class="container"><div class="stats-card">
<p>هر کتابی که این‌جا می‌بینید راهی طولانی را پشت‌سر گذاشته است: از انتخاب اثر تا ترجمه و ویرایشی که سطربه‌سطر سنجیده شده و جلدی که برای همان اثر طراحی شده است.</p>
<div class="stats"><div><b>{fa(len(books))}</b><span>اثر منتشرشده</span></div><div><b>{fa(len(people))}</b><span>پدیدآورنده</span></div><div><b>{fa(len(CATS))}</b><span>دسته‌بندی</span></div><div><b>{fa(f"{total_pages:,}").replace(",", "٬")}</b><span>صفحه</span></div></div>
</div></div></section>'''
    write('index.html', layout('نشر بوم', hero + latest + shelves + creators_sec + stats, 0, 'home'))

# ---------- book pages ----------
def person_link(name, r):
    return f'<a href="{r}people/{people[name]["slug"]}.html">{E(name)}</a>'

def book_page(b):
    r = '../'
    cat = CATS[b['category']]
    cr = f'<li><b>نویسنده</b>{person_link(b["author"], r)}</li>'
    if b.get('translator'): cr += f'<li><b>مترجم</b>{person_link(b["translator"], r)}</li>'
    if b['editors']: cr += f'<li><b>ویراستار</b>{" و ".join(person_link(e, r) for e in b["editors"])}</li>'
    if b.get('design'): cr += f'<li><b>طراحی</b>{person_link(b["design"], r)}</li>'
    about_book = ''.join(f'<p>{E(p)}</p>' for p in b['about_book'])
    about_author = ''.join(f'<p>{E(p)}</p>' for p in b['about_author'])
    tags_html = ''.join(f'<a class="tag" href="{r}tags/{tag_slug[t]}.html">#{E(t)}</a>' for t in b['tags'])
    sample = f'{r}assets/samples/{b["slug"]}-sample.pdf'
    related = [x for x in books if x['category'] == b['category'] and x is not b]
    others = related + [x for x in books if x not in related and x is not b]
    body = f'''<div class="page"><div class="container narrow">
<nav class="breadcrumb"><a href="{r}index.html">خانه</a>/<a href="{r}category/{b["category"]}.html">{E(cat[0])}</a>/<span>{E(b["title"])}</span></nav>
<article>
<div class="card book-hero">
  <div class="cover">{cover_img(b, r, eager=True)}</div>
  <div>
    <div class="label">{E(cat[0])}</div>
    <h1>{E(b["title"])}</h1>
    <ul class="credit-list">{cr}</ul>
    <div class="chips"><span class="chip">{icon("calendar")}{E(b["date"])}</span><span class="chip">{icon("pages")}{fa(b["pages"])} صفحه</span>{price_pill(b)}</div>
    <div class="book-actions"><a class="btn-gold" href="#sample">{icon("eye")}مطالعه‌ی نمونه</a><a class="btn-ghost" href="{sample}" download>{icon("download")}دریافت نمونه (PDF)</a></div>
    <div class="full-access" data-slug="{b["slug"]}" hidden aria-live="polite"></div>
  </div>
</div>
<div class="card"><h2>درباره‌ی <q>{E(b["title"])}</q></h2><div class="prose">{about_book}</div></div>
{f'<div class="card"><h2>درباره‌ی نویسنده</h2><div class="prose">{about_author}</div></div>' if about_author else ''}
<div class="card" id="sample"><h2>نمونه‌ی <q>{E(b["title"])}</q></h2><p class="sample-note">دو صفحه‌ی نخست کتاب</p>
<div class="sample-pages">{"".join(f'<a href="{sample}" target="_blank" rel="noopener"><img src="{r}assets/samples/{b["slug"]}-p-{n}.jpg" alt="صفحه‌ی {fa(n)}" loading="lazy"><span>صفحه‌ی {fa(n)}</span></a>' for n in (1, 2))}</div></div>
<div class="card"><h2>برچسب‌ها</h2><div class="tag-cloud">{tags_html}</div></div>
</article></div></div>
{shelf("آثار دیگر نشر بوم", None, others[:8], r, r + "library.html")}'''
    write(f'books/{b["slug"]}.html', layout(b['title'], body, 1, b['category'], b['about_book'][0][:160]))

# ---------- listing pages ----------
def listing(path, title, sub, items, depth, active, crumbs=None, toolbar=''):
    r = '../' * depth
    crumb = f'<nav class="breadcrumb"><a href="{r}index.html">خانه</a>/<span>{E(title)}</span></nav>'
    grid = ''.join(book_card(b, r) for b in items) or '<p class="empty">اثری در این بخش نیست.</p>'
    body = f'''<div class="page"><div class="container">{crumb}
<div class="sec-head"><div><h1 class="page-title">{E(title)}</h1>{f'<p class="page-sub">{E(sub)}</p>' if sub else ''}</div>{toolbar}</div>
<div class="book-grid" id="lib-grid">{grid}</div></div></div>'''
    write(path, layout(title, body, depth, active))

def all_pages():
    home()
    for b in books: book_page(b)
    for k, (title, sub, _) in CATS.items():
        listing(f'category/{k}.html', title, sub, [b for b in books if b['category'] == k], 1, k)
    tb = '<div class="toolbar"><select id="lib-sort" aria-label="مرتب‌سازی"><option value="new">تازه‌ترین</option><option value="old">قدیمی‌ترین</option><option value="title">عنوان</option></select></div>'
    listing('library.html', 'همه‌ی آثار', f'{fa(len(books))} اثر منتشرشده', books, 0, 'library', toolbar=tb)
    for t, slugs in tags.items():
        listing(f'tags/{tag_slug[t]}.html', '#' + t, f'{fa(len(slugs))} اثر', [by_slug[s] for s in slugs], 1, None)

    # people index
    body = f'''<div class="page"><div class="container"><nav class="breadcrumb"><a href="index.html">خانه</a>/<span>پدیدآورندگان</span></nav>
<div class="sec-head"><div><h1 class="page-title">پدیدآورندگان</h1><p class="page-sub">نویسندگان، مترجمان، ویراستاران و طراحان آثار نشر بوم</p></div></div>
<div class="people-grid">{"".join(creator_html(p, "") for p in people.values())}</div></div></div>'''
    write('people.html', layout('پدیدآورندگان', body, 0, 'people'))
    for p in people.values():
        r = '../'
        groups = OrderedDict()
        for s, roles in p['books'].items():
            for role in roles: groups.setdefault(role, []).append(by_slug[s])
        secs = ''
        for role in ROLE_FA:
            if role in groups:
                secs += f'<h2 style="font-size:19px;margin:28px 0 16px">{ROLE_FA[role]}</h2><div class="book-grid">{"".join(book_card(b, r) for b in sorted(groups[role], key=lambda b: -b["date_key"]))}</div>'
        bio = ''
        for b in books:
            if b['author'] == p['name'] and b['about_author']:
                bio = f'<div class="card" style="margin-top:24px"><div class="prose">{"".join(f"<p>{E(x)}</p>" for x in b["about_author"])}</div></div>'; break
        body = f'''<div class="page"><div class="container"><nav class="breadcrumb"><a href="{r}index.html">خانه</a>/<a href="{r}people.html">پدیدآورندگان</a>/<span>{E(p["name"])}</span></nav>
<div style="display:flex;align-items:center;gap:20px"><span class="avatar">{E(p["name"][0])}</span><div><h1 class="page-title">{E(p["name"])}</h1><p class="page-sub">{fa(len(p["books"]))} اثر در نشر بوم</p></div></div>
{bio}{secs}</div></div>'''
        write(f'people/{p["slug"]}.html', layout(p['name'], body, 1, 'people'))

    # search
    data = [{'title': b['title'], 'author': b['author'], 'url': f'books/{b["slug"]}.html', 'cover': f'assets/covers/{b["slug"]}-sm.jpg',
             'search': ' '.join([b['title'], b['author'], b.get('translator') or '', ' '.join(b['editors']), ' '.join(b['tags']), CATS[b['category']][0], ' '.join(b['about_book'])])} for b in books]
    body = f'''<div class="page"><div class="container"><nav class="breadcrumb"><a href="index.html">خانه</a>/<span>جست‌وجو</span></nav>
<form class="search page-search" action="search.html" style="max-width:none;margin:0 0 24px"><input type="search" name="q" placeholder="عنوان، نویسنده، مترجم یا موضوع..." aria-label="جست‌وجو"><button type="submit" aria-label="جست‌وجو">{icon("search")}</button></form>
<div class="sec-head"><div><h1 class="page-title" id="search-title">جست‌وجو</h1></div></div>
<div class="book-grid" id="search-results"></div></div></div>
<script>window.BOOM_BOOKS={json.dumps(data, ensure_ascii=False)};</script>'''
    write('search.html', layout('جست‌وجو', body, 0, 'search'))

    # about
    body = f'''<div class="page"><div class="container narrow"><nav class="breadcrumb"><a href="index.html">خانه</a>/<span>درباره‌ی ما</span></nav>
<div class="card"><h2>داستان ما</h2><div class="prose"><p>نشر بوم ناشری مستقل است که بر نمایشنامه، نظریه‌ی تئاتر، سینما، ادبیات و اندیشه تمرکز دارد. تا امروز {fa(len(books))} اثر با همراهی {fa(len(people))} پدیدآورنده منتشر کرده‌ایم.</p></div></div>
<div class="card" id="collab"><h2>همکاری با ما</h2><div class="prose"><p>—</p></div></div>
<div class="card" id="contact"><h2>ارتباط با ما</h2><ul class="credit-list social" style="margin:0"><li>{icon("camera")}<b>اینستاگرام:</b> —</li><li>{icon("send")}<b>تلگرام:</b> —</li><li>{icon("mail")}<b>ایمیل:</b> —</li></ul></div>
</div></div>'''
    write('about.html', layout('درباره‌ی ما', body, 0, 'about'))
    write('404.html', layout('صفحه پیدا نشد', '<div class="page"><div class="container narrow"><div class="card" style="text-align:center"><h2>صفحه پیدا نشد</h2><p><a class="btn-gold" href="index.html">بازگشت به خانه</a></p></div></div></div>', 0).replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<script>document.write(\'<base href="\' + (location.pathname.indexOf("/boom/") === 0 ? "/boom/" : "/") + \'">\')</script>', 1))
    write('.nojekyll', '')

all_pages()
print('built', len(books), 'books,', len(people), 'people,', len(tags), 'tags')
