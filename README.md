# cody-site

Personal profile and credentials page for **cody.sentinelowl.tech**. Plain static HTML/CSS with no framework and no external fonts or CDNs.

| File | Purpose |
|---|---|
| `certs.json` | All data: LinkedIn, GitHub, Microsoft Learn and Trailblazer links, certs, "also completed" items |
| `template.html` + `build.py` | `build.py` renders every cert into `index.html` and syncs the CSP hash in `_headers` |
| `index.html` | Generated output (commit it) |
| `styles.css` | Light, executive theme |
| `app.js` | Progressive enhancement: issuer filter chips + search. Without JS, everything still shows. |
| `assets/profile.jpg` | Profile photo (currently an initials placeholder) |
| `favicon.svg`, `_headers` | Icon and Cloudflare Pages security headers |

## Add a cert
Add an object to `certs` in `certs.json`:
```json
{ "name": "AWS Certified Cloud Practitioner", "issuer": "Amazon Web Services",
  "date": "2026-11-01", "url": "https://www.credly.com/badges/<id>", "category": "Cloud" }
```
- `name`, `issuer`, `url` are required; `date` (YYYY-MM-DD) and `category` are optional.
- Certs are grouped by issuer (issuers with the most certs come first), then by category. A new issuer automatically gets its own section and filter chip.
- To control category order, edit `CATEGORY_ORDER` in `build.py` (anything not listed sorts alphabetically after it).

Then run `python3 build.py` and commit `index.html` and `_headers`.

## Profile photo
Replace `assets/profile.jpg` with a square JPG (at least 400×400) and run `python3 build.py`. The build adds a content-hash query string, so caches pick up the new photo.

## CSP
`_headers` allows only same-origin scripts plus the hash of the inline JSON-LD block. `build.py` recomputes that hash on every build, so don't hand-edit it.

## Preview locally
`python3 build.py && python3 -m http.server 8080`, then open http://localhost:8080

## Deploy to Cloudflare Pages
1. Push this folder to a GitHub repo (e.g. `cody-site`).
2. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git → choose the repo.
3. Build command: `python3 build.py` (or leave it empty, since `index.html` is committed). Build output directory: `/`.
4. After the first deploy, go to the project's Custom domains and add `cody.sentinelowl.tech`. If `sentinelowl.tech` is a zone in the same Cloudflare account, the CNAME record is created automatically.

CLI alternative: `npx wrangler pages deploy . --project-name cody-site`.
