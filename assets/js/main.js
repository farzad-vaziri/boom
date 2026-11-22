(function () {
  // theme toggle
  var root = document.documentElement;
  var btn = document.querySelector('.theme-toggle');
  if (btn) btn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('boom-theme', next); } catch (e) {}
  });

  // hero carousel
  var hero = document.querySelector('.hero');
  if (hero) {
    var slides = hero.querySelectorAll('.slide');
    var dots = hero.querySelectorAll('.hero-dots button');
    var i = 0, timer;
    function go(n) {
      slides[i].classList.remove('active'); dots[i].classList.remove('active');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('active'); dots[i].classList.add('active');
    }
    function auto() { clearInterval(timer); timer = setInterval(function () { go(i + 1); }, 6500); }
    hero.querySelector('.hero-arrow.next').addEventListener('click', function () { go(i + 1); auto(); });
    hero.querySelector('.hero-arrow.prev').addEventListener('click', function () { go(i - 1); auto(); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { go(k); auto(); }); });
    var x0 = null;
    hero.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener('touchend', function (e) {
      if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) { go(dx > 0 ? i + 1 : i - 1); auto(); }
    });
    auto();
  }

  // search page
  var results = document.getElementById('search-results');
  if (results && window.BOOM_BOOKS) {
    var params = new URLSearchParams(location.search);
    var q = (params.get('q') || '').trim();
    var input = document.querySelector('.page-search input');
    if (input) input.value = q;
    document.querySelectorAll('.search input').forEach(function (el) { el.value = q; });
    var norm = function (s) { return (s || '').replace(/[ةۀ]/g, 'ه').replace(/ي/g, 'ی').replace(/ك/g, 'ک').replace(/‌/g, ' ').toLowerCase(); };
    var nq = norm(q);
    var hits = !nq ? window.BOOM_BOOKS : window.BOOM_BOOKS.filter(function (b) { return norm(b.search).indexOf(nq) > -1; });
    var title = document.getElementById('search-title');
    if (title) title.textContent = q ? 'نتیجه‌های جست‌وجو برای «' + q + '»' : 'همه‌ی آثار';
    if (!hits.length) { results.innerHTML = '<p class="empty">اثری پیدا نشد.</p>'; return; }
    results.innerHTML = hits.map(function (b) {
      return '<a class="book-card" href="' + b.url + '"><div class="cover"><img src="' + b.cover + '" alt="' + b.title + '" loading="lazy"></div><div><strong>' + b.title + '</strong><span>' + b.author + '</span></div></a>';
    }).join('');
  }

  // library sort
  var sort = document.getElementById('lib-sort');
  if (sort) sort.addEventListener('change', function () {
    var grid = document.getElementById('lib-grid');
    var items = Array.prototype.slice.call(grid.children);
    items.sort(function (a, b) {
      if (sort.value === 'title') return a.dataset.title.localeCompare(b.dataset.title, 'fa');
      if (sort.value === 'old') return a.dataset.date - b.dataset.date;
      return b.dataset.date - a.dataset.date;
    });
    items.forEach(function (el) { grid.appendChild(el); });
  });
})();
