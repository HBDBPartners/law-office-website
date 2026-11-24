# HBDB Partners Website

Source for the HBDB Partners (해법동반 법률사무소) website at https://hbdbpartners.com.

## Editing pages

The HTML files in the repository root are generated. Do not edit them directly.

- `_src/pages/` holds the body of each page, with its settings (title, description, language pair, menu) at the top.
- `_src/partials/` holds the shared header and footer for Korean and English.
- `_src/build.py` combines them into the HTML files in the repository root.

After editing anything in `_src/`, run the following and commit both the source and the generated files.

```bash
python3 _src/build.py
```

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
