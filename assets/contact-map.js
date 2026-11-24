// 연락처 페이지의 네이버 지도
// 사무소 위치에 로고 표식을 두고, 페이지를 스크롤할 때 지도가 확대되지 않게 함
// 표식 아래 뾰족한 끝이 위치를 가리키도록 맞춤
(function () {
  var el = document.getElementById('office-map');
  if (!el || !window.naver || !naver.maps) return;

  // 테헤란로 138 성홍타워 좌표
  var office = new naver.maps.LatLng(37.49964, 127.03430);

  var map = new naver.maps.Map(el, {
    center: office,
    zoom: 16,
    scrollWheel: false,
    zoomControl: true,
    zoomControlOptions: { position: naver.maps.Position.TOP_RIGHT, style: naver.maps.ZoomControlStyle.SMALL }
  });

  // 표식은 끝이 좌표를 가리키므로 원이 지도 가운데에 오도록 지도를 표식 높이의 절반만큼 내림
  map.panBy(new naver.maps.Point(0, -18));

  new naver.maps.Marker({
    position: office,
    map: map,
    title: document.documentElement.lang === 'en' ? 'HBDB Partners' : '해법동반 법률사무소',
    icon: {
      content: '<div class="map-pin" aria-hidden="true"><span class="map-pin-logo"></span></div>',
      size: new naver.maps.Size(32, 37),
      anchor: new naver.maps.Point(16, 37)
    }
  });
})();
