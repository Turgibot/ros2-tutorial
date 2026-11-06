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

// Header switches (Python/C++ and Docker/Local): only on pages that have matching blocks.
// Each choice is remembered across lessons. A block is <div class="lang py"> or <div class="env docker">.
(function () {
  var bar = document.createElement('div');
  bar.className = 'switches';
  function make(cls, key, label, options) {
    if (!document.querySelector('.' + cls)) return;
    var cur = options[0][0];
    try { var v = localStorage.getItem(key); options.forEach(function (o) { if (o[0] === v) cur = v; }); } catch (e) {}
    var box = document.createElement('div');
    box.className = 'langsw';
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', label);
    var buttons = {};
    function apply(v) {
      document.body.setAttribute('data-' + key, v);
      for (var k in buttons) buttons[k].setAttribute('aria-pressed', k === v ? 'true' : 'false');
      try { localStorage.setItem(key, v); } catch (e) {}
    }
    options.forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = p[1];
      b.addEventListener('click', function () { apply(p[0]); });
      buttons[p[0]] = b; box.appendChild(b);
    });
    bar.appendChild(box);
    apply(cur);
  }
  make('env', 'env', 'Where ROS 2 runs', [['docker', 'Docker'], ['local', 'Local install']]);
  make('lang', 'lang', 'Programming language', [['py', 'Python'], ['cpp', 'C++']]);
  if (bar.children.length) document.querySelector('header.site').appendChild(bar);
})();
