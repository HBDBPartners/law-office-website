"""사이트 페이지 조립 스크립트.

_src/pages의 페이지 본문과 _src/partials의 머리글·바닥글을 합쳐 저장소 루트에 HTML과 sitemap.xml을 만듦.
저장소 루트의 HTML은 조립 결과라서 직접 수정하지 않고, 원본을 수정한 뒤 다시 조립함.

실행: python3 _src/build.py
확인만: python3 _src/build.py --check  (조립 결과와 현재 HTML이 다르면 파일 이름을 알리고 실패로 끝남)
"""

import datetime
import hashlib
import html
import pathlib
import re
import string
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://hbdbpartners.com"

# 캐시 버전에 반영하는 파일: HTML이 ?v를 붙여 부르는 파일이며, 내용이 변경되면 ?v 값도 변경되어 브라우저가 새 파일을 받음
# CSS가 부르는 그림(icon.svg, arrow-external.svg), 사진, assets/fonts의 글꼴 파일에는 ?v가 붙지 않으므로, 교체할 때는 파일 이름을 변경함
VERSIONED = ["style.css", "menu.js", "scrollbar.js", "hero.js", "contact-map.js", "logo-ko.svg", "logo-en.svg"]

# 페이지 설정에 쓸 수 있는 이름과 구역 이름: 오타를 오류로 알리기 위한 목록
KEYS = {"lang", "title", "description", "path", "alt", "other", "nav", "hero", "layout", "main_class", "noindex"}
SECTIONS = {"head", "main", "after"}
NAVS = {"practice", "people", "contact"}

# sitemap 순서: 한글 뒤 영문, 각 언어 안에서는 첫 화면·업무분야·구성원·연락처·개인정보 처리방침 순
SITEMAP_SECTIONS = ["", "practice", "people", "contact", "privacy"]

# 명조(Noto Serif KR)만 불러오는 글꼴 연결: 영문 페이지와 머리글·바닥글 없는 404에 씀
FONTS_SERIF_ONLY = "family=Noto+Serif+KR:wght@500;600"

LANG = {
    "ko": {
        "site_name": "해법동반 법률사무소",
        "locale": "ko_KR",
        "image_alt": "해법동반 법률사무소 라운지와 회의실",
        "fonts": "family=Noto+Sans+KR:wght@400;600&family=Noto+Serif+KR:wght@500;600",
        "og_note": "<!-- 카카오톡·메신저 등에 링크를 보낼 때 뜨는 제목·설명·사진 -->\n",
    },
    "en": {
        "site_name": "HBDB Partners",
        "locale": "en_US",
        "image_alt": "The lounge and meeting rooms at HBDB Partners",
        "fonts": FONTS_SERIF_ONLY,
        "og_note": "",
    },
}

# 첫 화면 동작 전 화면을 가리는 표시를 붙이고, 3초 안에 동작이 시작되지 않으면 떼어 마지막 화면을 보임
# 첫 화면 동작이 기다리는 글꼴은 CSS를 읽기 전에 미리 받기 시작함
# 마루부리는 한글 첫 화면에만 쓰므로 한글 홈에서만 미리 받음
HERO_PRELOAD = {
    "ko": ["KimjungchulMyungjo-Light-hero.woff2", "MaruBuri-Regular-ksx1001.woff2"],
    "en": ["KimjungchulMyungjo-Light-hero.woff2"],
}
HERO_SCRIPTS = (
    '<script>document.documentElement.classList.add("js");setTimeout(function(){var m=document.querySelector(".motto");'
    'if(m&&!m.classList.contains("ready"))document.documentElement.classList.remove("js")},3000)</script>\n'
    '<script src="/assets/hero.js?v=$v" defer></script>\n'
)


def with_version(text, v):
    """글 안의 $v만 캐시 버전으로 치환함.

    스크립트의 ${...} 같은 다른 $ 표기는 유지함.
    """
    return re.sub(r"\$v(?!\w)", v, text)


def version():
    """캐시 버전 값: 대상 파일 내용의 해시 앞 8자리."""
    h = hashlib.sha1()
    for name in VERSIONED:
        h.update((ROOT / "assets" / name).read_bytes())
    return h.hexdigest()[:8]


def read_page(path):
    """페이지 원본을 설정(--- 사이)과 구역(<!-- @이름 --> 아래)으로 나눔."""
    text = path.read_text(encoding="utf-8")
    _, head, body = text.split("---\n", 2)
    meta = {}
    for line in head.splitlines():
        if line.strip():
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    parts = {}
    name = None
    for line in body.splitlines(keepends=True):
        if line.startswith("<!-- @"):
            name = line.strip()[6:-4].strip()
            parts[name] = ""
        elif name:
            parts[name] += line
        elif line.strip():
            fail(path, "첫 구역 표시(<!-- @main --> 등) 앞에 내용이 있음")
    check_page(path, meta, parts)
    # 제목·설명은 원본에 글자 그대로 쓰고, HTML 속성에 넣을 수 있게 여기서 변환함(& → &amp;, " → &quot;)
    for key in ("title", "description"):
        if key in meta:
            meta[key] = html.escape(meta[key], quote=True)
    return meta, parts


def fail(path, message):
    sys.exit(f"{path.relative_to(SRC)}: {message}")


def check_page(path, meta, parts):
    """설정·구역 이름의 오타와 빠진 필수 항목을 알리고 조립을 멈춤."""
    for key in meta.keys() - KEYS:
        fail(path, f"알 수 없는 설정 이름 「{key}」")
    for name in parts.keys() - SECTIONS:
        fail(path, f"알 수 없는 구역 이름 「{name}」(쓸 수 있는 이름: head, main, after)")
    required = ["lang", "title"] if meta.get("layout") == "bare" else ["lang", "title", "description", "path"]
    for key in required:
        if key not in meta:
            fail(path, f"필수 설정 「{key}」 항목이 없음")
    if "main" not in parts:
        fail(path, "본문 구역 <!-- @main -->이 없음")
    if meta["lang"] not in LANG:
        fail(path, f"lang은 ko 또는 en이어야 함: {meta['lang']}")
    if meta.get("nav", "practice") not in NAVS:
        fail(path, f"nav는 practice, people, contact 중 하나여야 함: {meta['nav']}")
    if "--" in meta.get("noindex", ""):
        fail(path, "noindex 설명에는 주석을 끊는 「--」를 쓸 수 없음")


def share_tags(meta, info, url):
    """카카오톡·메신저 등에 링크를 보낼 때 뜨는 제목·설명·사진(og 태그)."""
    return "".join([
        info["og_note"],
        '<meta property="og:type" content="website">\n',
        f'<meta property="og:site_name" content="{info["site_name"]}">\n',
        f'<meta property="og:locale" content="{info["locale"]}">\n',
        f'<meta property="og:title" content="{meta["title"]}">\n',
        f'<meta property="og:description" content="{meta["description"]}">\n',
        f'<meta property="og:url" content="{url}">\n',
        f'<meta property="og:image" content="{SITE}/assets/og-image.jpg">\n',
        '<meta property="og:image:width" content="1200">\n',
        '<meta property="og:image:height" content="630">\n',
        f'<meta property="og:image:alt" content="{info["image_alt"]}">\n',
        '<meta name="twitter:card" content="summary_large_image">\n',
    ])


def head(meta, parts, v, source):
    lang = meta["lang"]
    info = LANG[lang]
    bare = meta.get("layout") == "bare"
    out = [
        "<!DOCTYPE html>\n",
        f"<!-- 조립 결과 파일: 수정은 _src/pages/{source} 원본에서 하고 python3 _src/build.py로 다시 조립함 -->\n",
        f'<html lang="{lang}">\n',
        "<head>\n",
        '<meta charset="UTF-8">\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
        f"<title>{meta['title']}</title>\n",
        '<link rel="icon" href="/favicon.ico" sizes="48x48">\n',
        '<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">\n',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n',
    ]
    if "description" in meta:
        out.append(f'<meta name="description" content="{meta["description"]}">\n')
    if "noindex" in meta:
        out.append(f"<!-- {meta['noindex']} -->\n")
        out.append('<meta name="robots" content="noindex">\n')
    if not bare:
        url = SITE + meta["path"]
        out.append(f'<link rel="canonical" href="{url}">\n')
        if "alt" in meta:
            ko, en = (meta["path"], meta["alt"]) if lang == "ko" else (meta["alt"], meta["path"])
            out.append(f'<link rel="alternate" hreflang="ko" href="{SITE}{ko}">\n')
            out.append(f'<link rel="alternate" hreflang="en" href="{SITE}{en}">\n')
            out.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}{ko}">\n')
        out.append(share_tags(meta, info, url))
    fonts = FONTS_SERIF_ONLY if bare else info["fonts"]
    out += [
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n',
        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">\n',
    ]
    out.append(f'<link rel="stylesheet" href="/assets/style.css?v={v}">\n')
    if not bare:
        out.append(f'<script src="/assets/menu.js?v={v}" defer></script>\n')
        out.append(f'<script src="/assets/scrollbar.js?v={v}" defer></script>\n')
    if meta.get("hero") == "yes":
        for font in HERO_PRELOAD[lang]:
            out.append(f'<link rel="preload" href="/assets/fonts/{font}" as="font" type="font/woff2" crossorigin>\n')
        out.append(with_version(HERO_SCRIPTS, v))
    out.append(with_version(parts.get("head", ""), v))
    out.append("</head>\n")
    return "".join(out)


def partial(name, **values):
    text = (SRC / "partials" / name).read_text(encoding="utf-8")
    return string.Template(text).substitute(**values)


def build_page(src, v):
    """조립한 HTML과 페이지 설정을 돌려줌."""
    meta, parts = read_page(src)
    lang = meta["lang"]
    bare = meta.get("layout") == "bare"
    main_open = f'<main class="{meta["main_class"]}">' if "main_class" in meta else "<main>"
    source = src.relative_to(SRC / "pages").as_posix()
    out = [head(meta, parts, v, source), "<body>\n\n"]
    if not bare:
        current = {f"cur_{n}": (' aria-current="page"' if meta.get("nav") == n else "") for n in ("practice", "people", "contact")}
        # 언어 짝이 없는 페이지의 언어 전환 버튼은 상대 언어 첫 화면으로 연결
        other = meta.get("other") or meta.get("alt") or ("/en/" if lang == "ko" else "/")
        out.append(partial(f"header-{lang}.html", v=v, other=other, **current))
        out.append("\n")
    out += [main_open, "\n", with_version(parts["main"], v), "</main>\n\n"]
    if not bare:
        out.append(partial(f"footer-{lang}.html"))
        out.append("\n")
    if "after" in parts:
        out.append(with_version(parts["after"], v))
    out.append("</body>\n</html>\n")
    return "".join(out), meta


def check_fonts(pages):
    """글꼴 파일 확인: 미리 받기 목록의 파일이 없으면 중단하고, 마루부리 서브셋에 없는 한글은 알림."""
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    for font in sorted({f for fonts in HERO_PRELOAD.values() for f in fonts}):
        if not (ROOT / "assets" / "fonts" / font).exists() or font not in css:
            sys.exit(f"미리 받기 글꼴 파일 {font}: assets/fonts에 없거나 style.css에서 쓰지 않음")
    # 마루부리 파일은 KS X 1001 한글 2,350자만 담으므로 그 밖의 한글을 찾음
    for src in pages + sorted((SRC / "partials").glob("*.html")):
        rare = sorted({c for c in src.read_text(encoding="utf-8") if "가" <= c <= "힣" and not _in_ksx1001(c)})
        if rare:
            print(f"마루부리에 없는 한글: {''.join(rare)} ({src.relative_to(SRC)}), 해당 글자는 Noto Serif KR로 표시됨")


def _in_ksx1001(char):
    # 파이썬 EUC-KR 변환은 2,350자 밖의 한글을 8바이트 조합형으로 변환하므로 2바이트인 경우만 2,350자로 판정함
    try:
        return len(char.encode("euc-kr")) == 2
    except UnicodeEncodeError:
        return False


def stray_html(outputs):
    """원본이 없는 HTML: 원본 페이지를 지운 뒤 남은 예전 조립 결과일 수 있음."""
    found = set()
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        # 밑줄·마침표로 시작하는 최상위 폴더는 GitHub Pages가 공개하지 않으므로 검사에서 제외함
        if not rel.parts[0].startswith(("_", ".")):
            found.add(rel)
    return sorted(found - outputs)


def sitemap_order(path):
    """sitemap에서 페이지가 놓일 순서: 언어, 메뉴 순서, 목록 페이지 먼저, 주소 순."""
    parts = path.strip("/").split("/")
    lang = 1 if parts[0] == "en" else 0
    if lang:
        parts = parts[1:]
    section = parts[0] if parts and parts[0] else ""
    rank = SITEMAP_SECTIONS.index(section) if section in SITEMAP_SECTIONS else len(SITEMAP_SECTIONS)
    return (lang, rank, len(parts), path)


def sitemap(entries):
    """검색엔진에 알릴 주소 목록.

    마지막 수정일은 이번에 조립 결과가 달라진 페이지만 오늘 날짜로 변경하고 나머지는 이전 값을 유지함.
    """
    dest = ROOT / "sitemap.xml"
    old = dest.read_text(encoding="utf-8") if dest.exists() else ""
    previous = dict(re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", old))
    today = datetime.date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>\n', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n']
    for path, changed in sorted(entries, key=lambda e: sitemap_order(e[0])):
        url = SITE + path
        lastmod = today if changed or url not in previous else previous[url]
        lines.append(f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod></url>\n")
    lines.append("</urlset>\n")
    return "".join(lines), old


def build_pages(pages, v, check):
    """원본 페이지를 조립해 기존 결과와 비교하고, 확인 모드가 아니면 달라진 파일만 씀.

    돌려주는 값: 결과 파일 경로 모음, 달라진 파일 목록, sitemap 항목(주소, 달라짐 여부)
    """
    outputs = set()
    changed = []
    entries = []
    for src in pages:
        rel = src.relative_to(SRC / "pages")
        outputs.add(rel)
        dest = ROOT / rel
        page, meta = build_page(src, v)
        differs = not (dest.exists() and dest.read_text(encoding="utf-8") == page)
        # 검색에 넣는 페이지만 sitemap에 올림(404·검색 제외 페이지 빠짐)
        if "path" in meta and "noindex" not in meta:
            entries.append((meta["path"], differs))
        if not differs:
            continue
        changed.append(rel)
        if not check:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page, encoding="utf-8")
    return outputs, changed, entries


def main():
    check = "--check" in sys.argv[1:]
    v = version()
    pages = sorted((SRC / "pages").rglob("*.html"))
    outputs, changed, entries = build_pages(pages, v, check)
    xml, old_xml = sitemap(entries)
    if xml != old_xml:
        changed.append(pathlib.Path("sitemap.xml"))
        if not check:
            (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    check_fonts(pages)
    for rel in stray_html(outputs):
        print(f"원본 없는 HTML: {rel} (원본을 지웠다면 이 파일도 지울 것)")
    if check:
        for rel in changed:
            print(f"조립 결과와 다름: {rel}")
        print(f"확인 {len(pages)}개 페이지, 다른 파일 {len(changed)}개")
        sys.exit(1 if changed else 0)
    print(f"{len(pages)}개 페이지 조립, 변경된 파일 {len(changed)}개, 캐시 버전 {v}")


if __name__ == "__main__":
    main()
