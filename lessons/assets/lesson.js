// Adds a "Copy" button to every <pre class="cmd"> block. Expected-output blocks (pre.out) get none.
(function () {
  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    return ok;
  }
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; },
        function () { return fallbackCopy(text); });
    }
    return Promise.resolve(fallbackCopy(text));
  }
  document.querySelectorAll('pre.cmd').forEach(function (pre) {
    var btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'copy'; btn.textContent = 'Copy';
    btn.setAttribute('aria-label', 'Copy this command');
    btn.addEventListener('click', function () {
      var text = pre.querySelector('code').textContent.replace(/\n$/, '');
      copy(text).then(function (ok) {
        btn.textContent = ok ? 'Copied' : 'Press Ctrl+C';
        btn.classList.toggle('done', ok);
        setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('done'); }, 1800);
      });
    });
    pre.appendChild(btn);
  });
})();

// Python / C++ switch: only on pages that have .lang blocks. The choice is remembered across lessons.
(function () {
  if (!document.querySelector('.lang')) return;
  var lang = 'py';
  try { lang = localStorage.getItem('lang') === 'cpp' ? 'cpp' : 'py'; } catch (e) {}
  var box = document.createElement('div');
  box.className = 'langsw';
  box.setAttribute('role', 'group');
  box.setAttribute('aria-label', 'Programming language');
  var buttons = {};
  function apply(l) {
    document.body.setAttribute('data-lang', l);
    for (var k in buttons) buttons[k].setAttribute('aria-pressed', k === l ? 'true' : 'false');
    try { localStorage.setItem('lang', l); } catch (e) {}
  }
  [['py', 'Python'], ['cpp', 'C++']].forEach(function (p) {
    var b = document.createElement('button');
    b.type = 'button'; b.textContent = p[1];
    b.addEventListener('click', function () { apply(p[0]); });
    buttons[p[0]] = b; box.appendChild(b);
  });
  document.querySelector('header.site').appendChild(box);
  apply(lang);
})();
