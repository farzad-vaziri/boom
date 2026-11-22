import zipfile,re,json,os,subprocess
from PIL import Image
from pypdf import PdfReader, PdfWriter
S='/mnt/user-data/uploads/boom'; O='/home/claude/site/assets'
BOOKS=[ # slug, docx, pdf, cover, category
('arcadia','آرکادیا.docx','آرکادیا.pdf','روی جلد آرکادیا.png','plays'),
('the-big-reset','بازتنظیم بزرگ.docx','بازتنظیم بزرگ ویراست دوم.pdf','روی جلد بازتنظیم بزرگ.png','thought'),
('the-rocking-horse-kid','بچۀ اسب گهواره‌ای.docx','بچه اسب گهواره‌ای.pdf','روی جلد بچۀ اسب گهواره‌ای.png','plays'),
('theatre-and-politics','تئاتر و سیاست.docx','تئاتر و سیاست.pdf','روی جلد تئاتر و سیاست.png','theatre-theory'),
('ancient-history','تاریخ باستان.docx','تاریخ باستان.pdf','روی جلد تاریخ باستان.png','plays'),
('in-the-blink-of-an-eye','در پلک‌زدنی.docx','در پلک‌زدنی.pdf','روی جلد در پلک‌زدنی.png','cinema'),
('culture','فرهنگ.docx','فرهنگ، داستان ما.pdf','روی جلد فرهنگ.jpg','thought'),
('experimental-film','فیلم تجربی.docx','فیلم تجربی.pdf','روی جلد فیلم تجربی.png','cinema'),
('signs-of-fear','نشانه‌های هراس.docx','نشانه‌های هراس.pdf','روی جلد نشانه‌های هراس.jpg','literature'),
('red-address','نشانی سرخ.docx','نشانی سرخ.pdf','روی جلد نشانی سرخ.png','plays'),
]
def text(p):
    x=zipfile.ZipFile(p).read('word/document.xml').decode()
    x=re.sub(r'<w:br[^>]*/>','',x); x=x.replace('</w:p>','').replace('<w:tab/>',' ')
    t=''.join(re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>|()',x) and [a or b for a,b in re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>|()',x)])
    import html; return html.unescape(t.replace('','\n'))
KEYS={'نویسنده:':'author','مترجم:':'translator','ویراستار:':'editor','اولین انتشار:':'date','طراحی:':'design','دربارة نویسنده:':'about_author','دربارة کتاب:':'about_book'}
fa=str.maketrans('0123456789٠١٢٣٤٥٦٧٨٩','۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹')
en=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')
MONTHS=['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند']
out=[]
for slug,dx,pdf,cov,cat in BOOKS:
    t=text(f'{S}/{dx}')
    pat='('+'|'.join(map(re.escape,KEYS))+'|#)'
    parts=re.split(pat,t)
    b={'slug':slug,'category':cat,'title':parts[0].strip().split('\n')[0].strip(),'tags':[],'price':''}
    i=1
    while i<len(parts):
        k,v=parts[i],parts[i+1]; i+=2
        if k=='#':
            tag=v.strip().split()[0] if v.strip() else ''
            if tag: b['tags'].append(tag.replace('_',' '))
        else:
            b[KEYS[k]]=re.sub(r'[ \t]+',' ',v).strip()
    # date
    d=re.sub(r'\s+',' ',b['date'].translate(en)); m=re.match(r'(\d+) (\S+) (\d+)',d)
    b['date']=f'{m[1]} {m[2]} {m[3]}'.translate(fa); b['date_key']=int(m[3])*10000+(MONTHS.index(m[2])+1)*100+int(m[1])
    for k in ('author','translator','editor','design'):
        if k in b: b[k]=b[k].split('\n')[0].strip()
    # people lists
    b['editors']=[x.strip() for x in re.split(r' و ',b.get('editor',''))] if b.get('editor') else []
    for k in ('about_author','about_book'):
        b[k]=[p.strip() for p in b.get(k,'').split('\n') if p.strip()]
    # pdf
    r=PdfReader(f'{S}/{pdf}'); b['pages']=len(r.pages)
    w=PdfWriter(); [w.add_page(r.pages[j]) for j in range(2)]
    with open(f'{O}/samples/{slug}-sample.pdf','wb') as f: w.write(f)
    # cover
    im=Image.open(f'{S}/{cov}').convert('RGB'); im.thumbnail((600,900),Image.LANCZOS)
    im.save(f'{O}/covers/{slug}.jpg',quality=84,optimize=True,progressive=True)
    im2=im.copy(); im2.thumbnail((300,450),Image.LANCZOS); im2.save(f'{O}/covers/{slug}-sm.jpg',quality=82,optimize=True)
    b['cover_ratio']=round(im.height/im.width,3)
    out.append(b)
json.dump(out,open('/home/claude/work/books.json','w'),ensure_ascii=False,indent=1)
for b in out: print(b['slug'],b['title'],'|',b.get('author'),'|',b.get('translator'),'|',b['editors'],'|',b['date'],b['tags'],b['pages'],len(b['about_author']),len(b['about_book']))
# sample page previews
import subprocess
for b in out:
    subprocess.run(['pdftoppm','-r','90','-jpeg','-jpegopt','quality=80',f'{O}/samples/{b["slug"]}-sample.pdf',f'{O}/samples/{b["slug"]}-p'],check=True)
