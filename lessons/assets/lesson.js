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
