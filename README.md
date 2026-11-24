# HBDB Partners Website

Source for the HBDB Partners (해법동반 법률사무소) website at https://hbdbpartners.com.

## Local development

From the repository folder, run the following and open `http://localhost:8000`.

```bash
python3 -m http.server 8000
```

## Deployment

Published with GitHub Pages. Pushing to `main` updates the site. The custom domain is set in `CNAME`.

## Cache version

Every page links `style.css`, the scripts and the logo SVGs with a `?v=YYYYMMDD` query so that browsers fetch new files after a deployment.
When any of those files changes, replace the version in all HTML files before merging to `main`.
When HTML class names change together with the CSS, replace it in the same commit, because a browser that keeps the old CSS breaks the new HTML.
For a second change on the same day, add a number such as `?v=20261124.2`.

```bash
git ls-files '*.html' | xargs sed -i '' -E 's/\?v=[0-9.]+/?v=YYYYMMDD/g'
```
