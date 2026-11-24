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
Images loaded from the CSS (`icon.svg`, `arrow-external.svg`) and photos have no `?v=` query. When replacing one of them, give the new file a new name.
