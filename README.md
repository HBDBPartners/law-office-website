# HBDB Partners Website

Source for the HBDB Partners (해법동반 법률사무소) website at https://hbdbpartners.com.

## Editing pages

The HTML files in the repository root are generated. Do not edit them directly.

- `_src/pages/` holds the body of each page, with its settings (title, description, language pair, menu) at the top. Write the title and description as plain text (for example `M&A`); the build escapes them. The build stops with the file name if a setting name or a section name (`head`, `main`, `after`) is misspelled or a required setting is missing.
- `_src/partials/` holds the shared header and footer for Korean and English.
- `_src/build.py` combines them into the HTML files in the repository root.

After editing anything in `_src/`, run the following and commit both the source and the generated files.

```bash
python3 _src/build.py
```

To check without writing, run the following. It lists generated files that differ from the source (for example, a file edited by hand) and exits with an error if there are any.

```bash
python3 _src/build.py --check
```

The build also lists HTML files that have no source page, such as a page whose source was deleted.

`sitemap.xml` is generated too. It lists every page that has a `path` setting and no `noindex` setting. A page's `lastmod` becomes the build date only when its generated HTML changes; otherwise the previous date is kept.

## Local development

From the repository folder, run the following and open `http://localhost:8000`.

```bash
python3 -m http.server 8000
```

## Deployment

Published with GitHub Pages. Pushing to `main` updates the site. The custom domain is set in `CNAME`.
`_config.yml` keeps this README out of the published site.

## Cache version

Every page links `style.css`, the scripts and the logo SVGs with a `?v=` query so that browsers fetch new files after a deployment.
`_src/build.py` sets it to a hash of those files, so it changes only when one of them changes. Run the build after editing anything in `assets/`.
Images loaded from the CSS (`icon.svg`, `arrow-external.svg`), photos and the font files in `assets/fonts/` have no `?v=` query. When replacing one of them, give the new file a new name and update every place that refers to it.

## Photos

The first-screen photo is served as `office-lounge.webp`, with `office-lounge.jpg` as the fallback for browsers without WebP. After replacing the JPEG, make the WebP from it:

```bash
cwebp -q 85 -m 6 assets/office-lounge.jpg -o assets/office-lounge.webp
```

Member photos are stored at 480 px wide, which covers the largest display size (136 px) on screens with three times the pixel density.

## Fonts

The site serves its own font files from `assets/fonts/` so that every device shows the same fonts. Korean body text (Noto Sans KR, Noto Serif KR) still comes from Google Fonts.

| File | Used for | Contents | Source | License |
|---|---|---|---|---|
| `KimjungchulMyungjo-Light-hero.woff2` | 「해법동반」, 「법률사무소」 and 「HBDB Partners」 on the first screen | Only those characters | [KimjungchulMyungjo-Light.woff2](https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2302_01@1.0/KimjungchulMyungjo-Light.woff2) | `LICENSE-KimjungchulMyungjo.txt` |
| `MaruBuri-Regular-ksx1001.woff2` | Menu, language switch, first-screen phrases and introduction (Korean pages) | The 2,350 common Hangul syllables of KS X 1001, Latin letters and common symbols | [MaruBuri-Regular.woff2](https://hangeul.pstatic.net/hangeul_static/webfont/MaruBuri/MaruBuri-Regular.woff2) | `LICENSE-MaruBuri.txt` |
| `STIXTwoText-latin.woff2` | English pages, and Latin letters and digits on Korean pages | Latin characters, weights 400 to 700 | Google Fonts (STIX Two Text, latin subset) | `LICENSE-STIXTwoText.txt` |

The build stops if a font listed for preloading in `_src/build.py` (`HERO_PRELOAD`) is missing from `assets/fonts/` or not used in `style.css`. It also lists any Hangul in the page sources that is outside the 2,350 characters; those characters are shown in Noto Serif KR instead of MaruBuri.

To remake a subset file, download the original from the source above into a folder outside the repository, then run `pyftsubset` with `uv` (fonttools and brotli are fetched for the run only). For the first-screen font:

```bash
uv run --with fonttools --with brotli pyftsubset KimjungchulMyungjo-Light.woff2 --text="해법동반법률사무소HBDBPartners " --layout-features='*' --name-IDs='*' --name-languages='*' --flavor=woff2 --output-file=KimjungchulMyungjo-Light-hero.woff2
```

For MaruBuri, first write the character list, then run the same command with `--text-file`:

```bash
python3 -c "import itertools; s=''.join(c for a,b in itertools.product(range(0xB0,0xC9),range(0xA1,0xFF)) for c in [bytes([a,b]).decode('euc-kr','ignore')] if '가'<=c<='힣'); e=''.join(map(chr,[*range(0x20,0x7F),*range(0xA0,0x100),*range(0x2010,0x2027),*range(0x3000,0x3020),*range(0x3131,0x318F),0x203B])); open('chars.txt','w').write(s+e)"
```

```bash
uv run --with fonttools --with brotli pyftsubset MaruBuri-Regular.woff2 --text-file=chars.txt --layout-features='*' --name-IDs='*' --name-languages='*' --flavor=woff2 --output-file=MaruBuri-Regular-ksx1001.woff2
```

Give a remade file a new name, then update `style.css` and, for the first-screen fonts, `HERO_PRELOAD` in `_src/build.py`.
