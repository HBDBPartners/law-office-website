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
When any of those files changes, replace the date in all HTML files before merging to `main`.

```bash
git ls-files '*.html' | xargs sed -i '' 's/?v=20261124/?v=YYYYMMDD/g'
```
