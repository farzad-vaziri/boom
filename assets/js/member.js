/* نشر بوم — membership: sign-up / login (Supabase Auth) and full-book downloads.
   Access rule (enforced by Supabase, not by this file):
   a file can be downloaded if member level >= book access_level.
   Book access_level: 0 public, 1 members, 2 full members.  Member level: 1 basic, 2 full. */
(function () {
  var SUPABASE_URL = 'https://vknekntbmnlkeawuaoca.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_Wx0KPMtnPckLGwLRf-UcVg_lXyagkhH'; // public key, safe in the browser
  var BUCKET = 'books';
  var LINK_SECONDS = 300; // download links expire after 5 minutes

  if (!window.supabase || !window.supabase.createClient) return;
  var arrivedFromSignupLink = /type=signup/.test(location.hash); // read before Supabase clears the address
  var sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

  var ICON = {
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    download: '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 21h14"/>',
    lock: '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
  };
  function icon(n) { return '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">' + ICON[n] + '</svg>'; }
  function here() { return location.href.split('#')[0]; }

  var state = { user: null, level: 0, newsletter: false };
  var LEVEL_NAME = { 1: 'پایه', 2: 'کامل' };

  /* ---------- error messages ---------- */
  function errText(e) {
    var code = (e && (e.code || e.error_code)) || '';
    var msg = ((e && e.message) || '').toLowerCase();
    if (code === 'invalid_credentials' || msg.indexOf('invalid login') > -1) return 'ایمیل یا رمز عبور درست نیست.';
    if (code === 'email_not_confirmed' || msg.indexOf('not confirmed') > -1) return 'ایمیل شما هنوز تأیید نشده است. روی پیوند تأییدی که برایتان فرستاده‌ایم بزنید.';
    if (code === 'user_already_exists' || msg.indexOf('already registered') > -1) return 'با این ایمیل پیش‌تر ثبت‌نام شده است. لطفاً وارد شوید.';
    if (code === 'weak_password' || msg.indexOf('password should') > -1) return 'رمز عبور باید دست‌کم ۶ نویسه باشد.';
    if (code === 'same_password') return 'رمز تازه باید با رمز پیشین فرق داشته باشد.';
    if (code === 'email_address_invalid' || msg.indexOf('invalid format') > -1) return 'ایمیل واردشده درست نیست.';
    if (code.indexOf('rate_limit') > -1 || (e && e.status === 429) || msg.indexOf('rate limit') > -1) return 'درخواست‌ها بیش از اندازه بوده است. چند دقیقه‌ی دیگر دوباره تلاش کنید.';
    return 'خطایی پیش آمد. لطفاً دوباره تلاش کنید.';
  }

  /* ---------- modal ---------- */
  var modal = document.createElement('div');
  modal.className = 'auth-modal';
  modal.hidden = true;
  modal.innerHTML =
    '<div class="auth-backdrop" data-close></div>' +
    '<div class="auth-dialog" role="dialog" aria-modal="true" aria-labelledby="auth-title">' +
    '<button class="icon-btn auth-close" type="button" data-close aria-label="بستن">×</button>' +

    '<form class="auth-view" data-view="login" novalidate>' +
      '<h2 id="auth-title">ورود به نشر بوم</h2>' +
      '<label>ایمیل<input type="email" name="email" autocomplete="email" dir="ltr" required></label>' +
      '<label>رمز عبور<input type="password" name="password" autocomplete="current-password" dir="ltr" required></label>' +
      '<p class="auth-error" role="alert"></p>' +
      '<button class="btn-gold" type="submit">ورود</button>' +
      '<p class="auth-links"><a href="#" data-go="forgot">رمز عبور را فراموش کرده‌اید؟</a></p>' +
      '<p class="auth-switch">حساب ندارید؟ <a href="#" data-go="signup">ثبت‌نام کنید</a></p>' +
    '</form>' +

    '<form class="auth-view" data-view="signup" novalidate hidden>' +
      '<h2>ثبت‌نام در نشر بوم</h2>' +
      '<label>ایمیل<input type="email" name="email" autocomplete="email" dir="ltr" required></label>' +
      '<label>رمز عبور<input type="password" name="password" autocomplete="new-password" dir="ltr" minlength="6" required><small>دست‌کم ۶ نویسه</small></label>' +
      '<label class="auth-check"><input type="checkbox" name="newsletter"><span>می‌خواهم خبرنامه‌ی نشر بوم را با ایمیل دریافت کنم.<small>هر زمان بخواهید می‌توانید از «حساب من» آن را لغو کنید.</small></span></label>' +
      '<p class="auth-error" role="alert"></p>' +
      '<button class="btn-gold" type="submit">ساخت حساب</button>' +
      '<p class="auth-switch">حساب دارید؟ <a href="#" data-go="login">وارد شوید</a></p>' +
    '</form>' +

    '<form class="auth-view" data-view="forgot" novalidate hidden>' +
      '<h2>بازیابی رمز عبور</h2>' +
      '<p class="auth-note">ایمیل حساب‌تان را بنویسید تا پیوند ساختن رمز تازه را برایتان بفرستیم.</p>' +
      '<label>ایمیل<input type="email" name="email" autocomplete="email" dir="ltr" required></label>' +
      '<p class="auth-error" role="alert"></p>' +
      '<button class="btn-gold" type="submit">فرستادن پیوند</button>' +
      '<p class="auth-switch"><a href="#" data-go="login">بازگشت به ورود</a></p>' +
    '</form>' +

    '<form class="auth-view" data-view="reset" novalidate hidden>' +
      '<h2>رمز عبور تازه</h2>' +
      '<label>رمز تازه<input type="password" name="password" autocomplete="new-password" dir="ltr" minlength="6" required><small>دست‌کم ۶ نویسه</small></label>' +
      '<p class="auth-error" role="alert"></p>' +
      '<button class="btn-gold" type="submit">ذخیره‌ی رمز تازه</button>' +
    '</form>' +

    '<div class="auth-view" data-view="msg" hidden>' +
      '<h2 class="msg-title"></h2><p class="auth-note msg-text"></p>' +
      '<button class="btn-gold" type="button" data-close>باشه</button>' +
    '</div>' +

    '<div class="auth-view" data-view="account" hidden>' +
      '<h2>حساب من</h2>' +
      '<dl class="account-info"><dt>ایمیل</dt><dd class="acc-email" dir="ltr"></dd><dt>نوع عضویت</dt><dd class="acc-level"></dd></dl>' +
      '<label class="auth-check"><input type="checkbox" class="acc-news"><span>دریافت خبرنامه‌ی نشر بوم با ایمیل</span></label>' +
      '<p class="auth-error" role="alert"></p>' +
      '<button class="btn-ghost" type="button" data-action="logout">خروج از حساب</button>' +
    '</div>' +
    '</div>';
  document.body.appendChild(modal);

  var lastFocus = null;
  function view(name) {
    modal.querySelectorAll('.auth-view').forEach(function (v) {
      var on = v.getAttribute('data-view') === name;
      v.hidden = !on;
      if (on) { var err = v.querySelector('.auth-error'); if (err) err.textContent = ''; }
    });
    var v = modal.querySelector('[data-view="' + name + '"]');
    var first = v && v.querySelector('input:not([type=checkbox]), button');
    if (first) setTimeout(function () { first.focus(); }, 30);
  }
  function open(name) {
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.documentElement.classList.add('auth-open');
    view(name);
  }
  function close() {
    modal.hidden = true;
    document.documentElement.classList.remove('auth-open');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  function message(title, text) {
    modal.querySelector('.msg-title').textContent = title;
    modal.querySelector('.msg-text').textContent = text;
    if (modal.hidden) open('msg'); else view('msg');
  }
  function busy(form, on) {
    var b = form.querySelector('button[type=submit]');
    if (b) { b.disabled = on; b.classList.toggle('is-busy', on); }
  }
  function showErr(form, text) { form.querySelector('.auth-error').textContent = text; }

  modal.addEventListener('click', function (e) {
    var t = e.target.closest('[data-close],[data-go],[data-action]');
    if (!t) return;
    e.preventDefault();
    if (t.hasAttribute('data-close')) close();
    else if (t.hasAttribute('data-go')) {
      // carry the typed email across views
      var from = modal.querySelector('.auth-view:not([hidden]) input[name=email]');
      var to = modal.querySelector('[data-view="' + t.getAttribute('data-go') + '"] input[name=email]');
      if (from && to && from.value) to.value = from.value;
      view(t.getAttribute('data-go'));
    }
    else if (t.getAttribute('data-action') === 'logout') {
      sb.auth.signOut().then(close);
    }
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !modal.hidden) close(); });

  /* login */
  modal.querySelector('[data-view="login"]').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target, email = f.email.value.trim(), pw = f.password.value;
    if (!email || !pw) return showErr(f, 'ایمیل و رمز عبور را بنویسید.');
    busy(f, true);
    sb.auth.signInWithPassword({ email: email, password: pw }).then(function (r) {
      busy(f, false);
      if (r.error) return showErr(f, errText(r.error));
      f.reset(); close();
    });
  });

  /* sign-up */
  modal.querySelector('[data-view="signup"]').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target, email = f.email.value.trim(), pw = f.password.value;
    if (!email || !pw) return showErr(f, 'ایمیل و رمز عبور را بنویسید.');
    if (pw.length < 6) return showErr(f, 'رمز عبور باید دست‌کم ۶ نویسه باشد.');
    busy(f, true);
    sb.auth.signUp({
      email: email, password: pw,
      options: { emailRedirectTo: here(), data: { newsletter: f.newsletter.checked } }
    }).then(function (r) {
      busy(f, false);
      if (r.error) return showErr(f, errText(r.error));
      f.reset();
      if (r.data && r.data.session) return close(); // email confirmation switched off
      message('ایمیل‌تان را ببینید', 'پیوند تأیید به ' + email + ' فرستاده شد. برای فعال شدن حساب، روی پیوند داخل ایمیل بزنید. اگر ایمیل را نمی‌بینید، پوشه‌ی هرزنامه (Spam) را هم نگاه کنید.');
    });
  });

  /* forgot password */
  modal.querySelector('[data-view="forgot"]').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target, email = f.email.value.trim();
    if (!email) return showErr(f, 'ایمیل را بنویسید.');
    busy(f, true);
    sb.auth.resetPasswordForEmail(email, { redirectTo: here() }).then(function (r) {
      busy(f, false);
      if (r.error) return showErr(f, errText(r.error));
      message('ایمیل‌تان را ببینید', 'اگر حسابی با ' + email + ' وجود داشته باشد، پیوند ساختن رمز تازه برایش فرستاده شد.');
    });
  });

  /* new password (after clicking the recovery link) */
  modal.querySelector('[data-view="reset"]').addEventListener('submit', function (e) {
    e.preventDefault();
    var f = e.target, pw = f.password.value;
    if (pw.length < 6) return showErr(f, 'رمز عبور باید دست‌کم ۶ نویسه باشد.');
    busy(f, true);
    sb.auth.updateUser({ password: pw }).then(function (r) {
      busy(f, false);
      if (r.error) return showErr(f, errText(r.error));
      f.reset();
      message('رمز تازه ذخیره شد', 'از این پس با رمز تازه وارد شوید.');
    });
  });

  /* newsletter on/off */
  var newsBox = modal.querySelector('.acc-news');
  newsBox.addEventListener('change', function () {
    var v = newsBox.checked, accErr = modal.querySelector('[data-view="account"] .auth-error');
    accErr.textContent = '';
    newsBox.disabled = true;
    sb.from('members').update({ newsletter: v }).eq('id', state.user.id).then(function (r) {
      newsBox.disabled = false;
      if (r.error) { newsBox.checked = !v; accErr.textContent = errText(r.error); return; }
      state.newsletter = v;
    });
  });

  /* ---------- header button ---------- */
  var authBtn = document.getElementById('auth-btn');
  function paintHeader() {
    if (!authBtn) return;
    authBtn.querySelector('.lbl').textContent = state.user ? 'حساب من' : 'ورود | ثبت‌نام';
    authBtn.setAttribute('aria-label', state.user ? 'حساب من' : 'ورود یا ثبت‌نام');
    authBtn.classList.toggle('is-member', !!state.user);
  }
  if (authBtn) authBtn.addEventListener('click', function () {
    if (!state.user) return open('login');
    modal.querySelector('.acc-email').textContent = state.user.email || '';
    modal.querySelector('.acc-level').textContent = LEVEL_NAME[state.level] || '—';
    newsBox.checked = !!state.newsletter;
    open('account');
  });

  /* ---------- full-book download box (book pages) ---------- */
  var box = document.querySelector('.full-access');
  var book = null; // {access_level, pdf_path}
  function loadBook() {
    if (!box) return Promise.resolve();
    return sb.from('books').select('access_level,pdf_path').eq('slug', box.getAttribute('data-slug')).maybeSingle()
      .then(function (r) { book = r.data || null; });
  }
  function paintBox() {
    if (!box || !book || !book.pdf_path) { if (box) box.hidden = true; return; }
    var need = book.access_level, have = state.user ? state.level : 0, html;
    if (have >= need) {
      html = '<button class="btn-gold" type="button" data-dl>' + icon('download') + 'دریافت کامل کتاب (PDF)</button>' +
        (need > 0 ? '<p class="fa-note">شما به نسخه‌ی کامل این کتاب دسترسی دارید.</p>' : '<p class="fa-note">نسخه‌ی کامل این کتاب برای همه رایگان است.</p>');
    } else if (!state.user) {
      html = '<button class="btn-ghost" type="button" data-login>' + icon('lock') + 'ورود برای دریافت کامل کتاب</button>' +
        '<p class="fa-note">' + (need === 1
          ? 'نسخه‌ی کامل این کتاب ویژه‌ی اعضای نشر بوم است. عضویت رایگان است؛ کافی است ثبت‌نام کنید.'
          : 'نسخه‌ی کامل این کتاب ویژه‌ی اعضای کامل نشر بوم است.') + '</p>';
    } else {
      html = '<span class="btn-ghost is-locked" aria-disabled="true">' + icon('lock') + 'ویژه‌ی اعضای کامل</span>' +
        '<p class="fa-note">عضویت شما «' + (LEVEL_NAME[have] || '—') + '» است و نسخه‌ی کامل این کتاب ویژه‌ی اعضای کامل است.</p>';
    }
    box.innerHTML = html + '<p class="auth-error" role="alert"></p>';
    box.hidden = false;
  }
  if (box) box.addEventListener('click', function (e) {
    if (e.target.closest('[data-login]')) return open('login');
    var b = e.target.closest('[data-dl]');
    if (!b || b.disabled) return;
    var err = box.querySelector('.auth-error');
    err.textContent = '';
    b.disabled = true; b.classList.add('is-busy');
    sb.storage.from(BUCKET).createSignedUrl(book.pdf_path, LINK_SECONDS, { download: book.pdf_path })
      .then(function (r) {
        b.disabled = false; b.classList.remove('is-busy');
        if (r.error || !r.data) { err.textContent = 'دریافت فایل ممکن نشد. لطفاً دوباره تلاش کنید.'; return; }
        location.href = r.data.signedUrl;
      });
  });

  /* ---------- session ---------- */
  function loadMember() {
    if (!state.user) { state.level = 0; state.newsletter = false; return Promise.resolve(); }
    return sb.from('members').select('level,newsletter').eq('id', state.user.id).maybeSingle().then(function (r) {
      state.level = (r.data && r.data.level) || 1;
      state.newsletter = !!(r.data && r.data.newsletter);
    });
  }
  function refresh(session) {
    state.user = session ? session.user : null;
    paintHeader();
    return loadMember().then(paintBox);
  }

  var bookReady = loadBook();
  var lastUid;
  sb.auth.onAuthStateChange(function (event, session) {
    if (event === 'PASSWORD_RECOVERY') { setTimeout(function () { open('reset'); }, 0); }
    var uid = session ? session.user.id : null;
    if (event === 'TOKEN_REFRESHED' && uid === lastUid) return;
    lastUid = uid;
    // run outside the auth callback (Supabase advises against awaiting inside it)
    setTimeout(function () {
      bookReady.then(function () { return refresh(session); }).then(function () {
        if (event === 'SIGNED_IN' && arrivedFromSignupLink) {
          arrivedFromSignupLink = false;
          message('خوش آمدید', 'حساب شما فعال شد و اکنون وارد شده‌اید.');
        }
      });
    }, 0);
  });
})();
