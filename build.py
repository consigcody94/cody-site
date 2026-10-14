#!/usr/bin/env python3
"""Render certs.json into index.html (fully static; JS only adds filtering) and sync the CSP hash in _headers."""
import json, html, datetime, pathlib, re, hashlib, base64
from collections import OrderedDict
ROOT = pathlib.Path(__file__).parent
TRAILBLAZER = "https://www.salesforce.com/trailblazer/wyjwe4l24sutsgswf8"
# Optional display order for categories; anything else sorts alphabetically after these.
CATEGORY_ORDER = ["Agentforce", "AI Fundamentals", "Other", "Learning paths", "Modules", "Claude Platform & API", "Agents & MCP", "Claude Code", "AI Fluency"]
e = lambda s: html.escape(str(s), quote=True)
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def fmt(d):
    try: return datetime.date.fromisoformat(d).strftime("%b %-d, %Y")
    except ValueError: return d
def cat_key(c): return (CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else len(CATEGORY_ORDER), c)

def main():
    data = json.loads((ROOT / "certs.json").read_text())
    certs = data["certs"]
    by_issuer = OrderedDict()
    # issuers ordered by number of certs (desc), then name
    counts = {}
    for c in certs: counts[c["issuer"]] = counts.get(c["issuer"], 0) + 1
    for iss in sorted(counts, key=lambda i: (-counts[i], i)): by_issuer[iss] = {}
    for c in certs: by_issuer[c["issuer"]].setdefault(c.get("category") or "", []).append(c)

    out, chips = [], []
    for iss, cats in by_issuer.items():
        s = slug(iss)
        chips.append(f'          <option value="{s}">{e(iss)} ({counts[iss]})</option>')
        out.append(f'    <section class="issuer" data-issuer="{s}" aria-labelledby="iss-{s}">\n      <h3 id="iss-{s}">{e(iss)} <span class="n">{counts[iss]}</span></h3>')
        for cat in sorted(cats, key=cat_key):
            items = sorted(cats[cat], key=lambda c: (c.get("date", ""), c["name"]), reverse=True)
            out.append('      <div class="cat">')
            if cat: out.append(f'        <h4>{e(cat)}</h4>')
            out.append('        <ul class="list">')
            for c in items:
                d = c.get("date", "")
                out.append(f'          <li class="item" data-search="{e((c["name"]+" "+iss+" "+cat).lower())}"><a href="{e(c["url"])}" target="_blank" rel="noopener"><span class="name">{e(c["name"])}</span><span class="meta">{e(iss)}{" · <time datetime=\"%s\">%s</time>" % (e(d), e(fmt(d))) if d else ""}</span><span class="sr"> (opens in new tab)</span></a></li>')
            out.append('        </ul>\n      </div>')
        out.append('    </section>')

    also = ""
    if data.get("also_completed"):
        parts = [f'<a href="{e(a["url"])}" target="_blank" rel="noopener">{e(a["name"])}</a> ({e(a["issuer"])}{"; " + e(a["note"]).lower() if a.get("note") else ""})' for a in data["also_completed"]]
        also = f'    <p class="also">Also completed: {"; ".join(parts)}.</p>'

    jsonld = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": "Cody Churchwell",
        "jobTitle": "Founder", "worksFor": {"@type": "Organization", "name": "Sentinel Owl Technologies", "url": "https://sentinelowl.tech"},
        "url": "https://cody.sentinelowl.tech/", "image": "https://cody.sentinelowl.tech/assets/profile.jpg",
        "sameAs": [u for u in (data["linkedin"], data.get("github"), data.get("microsoft_learn"), data.get("trailblazer", TRAILBLAZER)) if u]}, separators=(",", ":"))
    photo = ROOT / "assets" / "profile.jpg"
    photov = hashlib.sha1(photo.read_bytes()).hexdigest()[:8] if photo.exists() else "0"

    t = (ROOT / "template.html").read_text()
    rep = {"{{GROUPS}}": "\n".join(out), "{{CHIPS}}": "\n".join(chips), "{{ALSO}}": also, "{{JSONLD}}": jsonld,
           "{{COUNT}}": str(len(certs)), "{{ISSUERS}}": str(len(counts)), "{{ISSUERS_S}}": "" if len(counts) == 1 else "s",
           "{{LINKEDIN}}": e(data["linkedin"]), "{{TRAILBLAZER}}": e(data.get("trailblazer", TRAILBLAZER)), "{{PHOTOV}}": photov, "{{GITHUB}}": e(data.get("github", "")), "{{MSLEARN}}": e(data.get("microsoft_learn", ""))}
    for k, v in rep.items(): t = t.replace(k, v)
    (ROOT / "index.html").write_text(t)

    # keep CSP in _headers in sync with the inline JSON-LD block
    h = base64.b64encode(hashlib.sha256(jsonld.encode()).digest()).decode()
    hp = ROOT / "_headers"
    hp.write_text(re.sub(r"'sha256-[^']*'", f"'sha256-{h}'", hp.read_text()))
    print(f"Built index.html: {len(certs)} credentials, {len(counts)} issuer(s); CSP hash sha256-{h}")

if __name__ == "__main__": main()
