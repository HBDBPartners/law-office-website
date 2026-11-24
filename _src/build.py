"""사이트 페이지 조립 스크립트.

_src/pages의 페이지 본문과 _src/partials의 머리글·바닥글을 합쳐 저장소 루트에 HTML을 만듦.
저장소 루트의 HTML은 조립 결과라서 직접 고치지 않고, 원본을 고친 뒤 다시 조립함.

실행: python3 _src/build.py
"""

import hashlib
import pathlib
import string

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://hbdbpartners.com"

# 캐시 버전에 반영하는 파일: 이 파일들의 내용이 바뀌면 ?v 값이 바뀌어 브라우저가 새 파일을 받음
VERSIONED = ["style.css", "menu.js", "scrollbar.js", "hero.js", "contact-map.js", "logo-ko.svg", "logo-en.svg"]

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
HERO_SCRIPTS = (
    '<script>document.documentElement.classList.add("js");setTimeout(function(){var m=document.querySelector(".motto");'
    'if(m&&!m.classList.contains("ready"))document.documentElement.classList.remove("js")},3000)</script>\n'
    '<script src="/assets/hero.js?v=$v" defer></script>\n'
)


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
        if line.startswith("<!-- @") and line.rstrip().endswith("-->"):
            name = line.strip()[6:-4].strip()
            parts[name] = ""
        elif name:
            parts[name] += line
    return meta, parts


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
    if not bare:
        out.append('<link rel="stylesheet" href="https://hangeul.pstatic.net/hangeul_static/css/maru-buri.css">\n')
    out.append(f'<link rel="stylesheet" href="/assets/style.css?v={v}">\n')
    if not bare:
        out.append(f'<script src="/assets/menu.js?v={v}" defer></script>\n')
        out.append(f'<script src="/assets/scrollbar.js?v={v}" defer></script>\n')
    if meta.get("hero") == "yes":
        out.append(string.Template(HERO_SCRIPTS).substitute(v=v))
    out.append(parts.get("head", ""))
    out.append("</head>\n")
    return "".join(out)


def partial(name, **values):
    text = (SRC / "partials" / name).read_text(encoding="utf-8")
    return string.Template(text).substitute(**values)


def build_page(src, v):
    meta, parts = read_page(src)
    lang = meta["lang"]
    bare = meta.get("layout") == "bare"
    main_open = f'<main class="{meta["main_class"]}">' if "main_class" in meta else "<main>"
    source = src.relative_to(SRC / "pages").as_posix()
    out = [head(meta, parts, v, source), "<body>\n\n"]
    if not bare:
        current = {f"cur_{n}": (' aria-current="page"' if meta.get("nav") == n else "") for n in ("practice", "people", "contact")}
        out.append(partial(f"header-{lang}.html", v=v, other=meta.get("other", meta.get("alt")), **current))
        out.append("\n")
    out += [main_open, "\n", parts["main"], "</main>\n\n"]
    if not bare:
        out.append(partial(f"footer-{lang}.html"))
        out.append("\n")
    if "after" in parts:
        out.append(string.Template(parts["after"]).substitute(v=v))
    out.append("</body>\n</html>\n")
    return "".join(out)


def main():
    v = version()
    pages = sorted((SRC / "pages").rglob("*.html"))
    for src in pages:
        rel = src.relative_to(SRC / "pages")
        dest = ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(build_page(src, v), encoding="utf-8")
    print(f"{len(pages)}개 페이지 조립, 캐시 버전 {v}")


if __name__ == "__main__":
    main()
