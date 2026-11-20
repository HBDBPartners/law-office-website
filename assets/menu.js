// 머리글의 메뉴 버튼과 언어 전환 동작
(function () {
  var btn = document.querySelector('.burger');
  var nav = document.querySelector('.nav');

  if (btn && nav) {
    var set = function (open) {
      nav.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };

    btn.addEventListener('click', function () {
      set(!nav.classList.contains('open'));
    });

    // Esc 키로 닫기
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') set(false);
    });
  }

  // 남색 칸이 다른 언어 쪽으로 이동한 뒤 페이지 이동
  var lang = document.querySelector('.lang');
  var link = lang && lang.querySelector('a');
  if (link) {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    link.addEventListener('click', function (e) {
      if (reduce || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      lang.classList.add('move');
      setTimeout(function () { location.href = link.href; }, 240);
    });
  }
})();
