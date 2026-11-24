// 스크롤하는 동안에만 스크롤바를 보이고, 멈춘 뒤 0.8초가 지나면 숨김
(function () {
  var root = document.documentElement;
  var timer;
  addEventListener('scroll', function () {
    root.classList.add('is-scrolling');
    clearTimeout(timer);
    timer = setTimeout(function () { root.classList.remove('is-scrolling'); }, 800);
  }, { passive: true });
})();
