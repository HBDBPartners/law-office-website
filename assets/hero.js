// 첫 화면 사무소명 동작
// 「해법」 「동반」 두 줄에 문구가 한 글자씩 나타났다가 사라진 뒤, 「동반」이 「해법」 옆으로 올라가고 「법률사무소」와 소개 문단이 나타남
(function () {
  var text = document.querySelector('.hero-text');
  var motto = document.querySelector('.motto');
  var lead = document.querySelector('.hero .lead');
  if (!text || !motto || !lead) return;

  function show() {
    motto.classList.add('ready');
    lead.classList.add('in');
  }

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    show();
    return;
  }

  var ln1 = motto.querySelector('.ln1');
  var ln2 = motto.querySelector('.ln2');
  var db = motto.querySelector('.db');
  var office = motto.querySelector('.office');
  var p1 = motto.querySelector('.p1');
  var p2 = motto.querySelector('.p2');

  // 글자마다 감싸서 한 글자씩 켤 수 있게 함
  function split(el) {
    var out = [];
    [].slice.call(el.children).forEach(function (part) {
      var t = part.textContent;
      part.textContent = '';
      for (var i = 0; i < t.length; i++) {
        var c = document.createElement('span');
        c.className = 'c';
        c.textContent = t[i];
        part.appendChild(c);
        out.push(c);
      }
    });
    return out;
  }

  // 한 글자씩 나타냄
  function type(chars, ms, done) {
    var i = 0;
    (function step() {
      if (i >= chars.length) { if (done) done(); return; }
      chars[i++].classList.add('on');
      setTimeout(step, ms);
    })();
  }

  function later(ms, fn) { setTimeout(fn, ms); }

  // 웹 글꼴을 받은 뒤 시작해 높이를 정확히 잼
  var fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  fontsReady.then(start);

  function start() {
    // 대기 시간이 길어 이미 마지막 화면이 표시된 경우 동작하지 않음
    if (!document.documentElement.classList.contains('js')) return;

    var c1 = split(p1);
    var c2 = split(p2);

    // 시작 화면과 마지막 화면 중 높은 쪽에 맞춰 문구 영역 높이를 고정해 위치가 흔들리지 않게 함
    var endH = text.offsetHeight;
    motto.classList.add('anim');
    office.style.display = 'none';
    ln2.insertBefore(db, p2);
    var startH = text.offsetHeight;
    text.style.minHeight = Math.max(endH, startH) + 'px';
    motto.classList.add('ready');

    // 1단계: 두 문구를 차례로 한 글자씩 표시
    later(500, function () {
      type(c1, 55, function () {
        later(250, function () {
          type(c2, 55, function () {

            // 2단계: 읽을 시간을 둔 뒤 두 문구가 함께 서서히 사라짐
            later(2600, function () {
              p1.classList.add('out');
              p2.classList.add('out');
              later(650, moveUp);
            });
          });
        });
      });
    });

    // 3단계: 「동반」이 곡선을 그리며 「해법」 옆으로 올라감
    // 오른쪽으로 먼저 간 뒤 위로 휘는 곡선이라 「해법」 위를 지나가지 않음
    function moveUp() {
      p1.style.display = 'none';
      p2.style.display = 'none';

      var a = db.getBoundingClientRect();
      ln1.insertBefore(db, office);
      office.style.display = '';
      ln2.style.display = 'none';
      var b = db.getBoundingClientRect();
      var dx = a.left - b.left;
      var dy = a.top - b.top;

      // 3차 베지어 곡선 위의 점을 스무 구간으로 나눠 이동 경로로 사용
      var frames = [];
      for (var i = 0; i <= 20; i++) {
        var t = i / 20;
        var u = 1 - t;
        var x = u * u * u * dx;
        var y = u * u * u * dy + 3 * u * u * t * dy + 3 * u * t * t * dy * 0.35;
        frames.push({ transform: 'translate(' + x.toFixed(2) + 'px,' + y.toFixed(2) + 'px)' });
      }
      var anim = db.animate(frames, { duration: 1000, easing: 'cubic-bezier(.45,.05,.35,1)' });

      // 4단계: 「동반」이 거의 다 올라갔을 때부터 「법률사무소」와 소개 문단이 함께 나타남
      later(800, function () {
        office.classList.add('in');
        lead.classList.add('in');
      });

      // 창 크기가 바뀌면 고정한 높이를 풀어 다시 맞춤
      anim.onfinish = function () {
        window.addEventListener('resize', function () { text.style.minHeight = ''; }, { once: true });
      };
    }
  }
})();
