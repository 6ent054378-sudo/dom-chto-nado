#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сбор фото с живых сайтов строительных компаний.
Пул: /tmp/pool6 (постоянный зеркальный, пересобирается этим скриптом).
"""
import os, re, urllib.request, urllib.parse, sys

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pool6"
os.makedirs(OUT, exist_ok=True)


def get(url, timeout=40):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_html(url):
    try:
        return get(url).decode("utf-8", "ignore")
    except Exception as e:
        print("  !", url, e)
        return ""


def absu(base, u):
    return urllib.parse.urljoin(base, u.split("#")[0].replace("&amp;", "&"))


def all_images(base, html):
    out, seen = [], set()
    pats = [r'(?:data-original|data-lazy-src|data-src|data-lazy|data-bg|data-background|src|poster)\s*=\s*"([^"]+\.(?:webp|jpg|jpeg|png)(?:\?[^"]*)?)"',
            r'srcset\s*=\s*"([^"]+)"',
            r'(?:href|src)\s*=\s*"([^"]+\.(?:webp|jpg|jpeg|png)(?:\?[^"]*)?)"']
    for p in pats:
        for m in re.finditer(p, html, re.I):
            for q in re.split(r",\s*", m.group(1)):
                q = q.strip().split(" ")[0]
                if not q:
                    continue
                u = absu(base, q)
                if u in seen:
                    continue
                if re.search(r"(logo|icon|favicon|flag|qr|badge|sprite|placeholder|avatars/|brand|cookie)", u, re.I):
                    continue
                seen.add(u)
                out.append(u)
    return out


def big_variants(u):
    out = []
    if "/img_products/thumb_" in u:
        out.append(u.replace("/img_products/thumb_", "/img_products/"))
    if "/upload/resize_cache/webp/" in u:
        out.append(u.replace("/upload/resize_cache/webp/", "/upload/"))
    if "phpthumbof/cache/" in u:
        h = u.split("/cache/")[-1]
        out.append(u.split("/cache/")[0] + "/" + h.split(".")[0] + u.rsplit(".", 1)[-1])
    return out


def grab(u, dest):
    try:
        data = get(u, 50)
        if len(data) < 12000:
            return False
        open(dest, "wb").write(data)
        return True
    except Exception:
        return False


def run(tag, page, limit=120):
    h = get_html(page)
    if not h:
        return 0
    imgs = all_images(page, h)
    d = os.path.join(OUT, tag)
    os.makedirs(d, exist_ok=True)
    n = 0
    for i, u in enumerate(imgs):
        if n >= limit:
            break
        for c in big_variants(u) + [u]:
            ext = os.path.splitext(urllib.parse.urlparse(c).path)[1].lower() or ".jpg"
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                ext = ".jpg"
            dest = os.path.join(d, f"{tag}_{i:03d}{ext}")
            if os.path.exists(dest) and os.path.getsize(dest) > 12000:
                n += 1
                break
            if grab(c, dest):
                n += 1
                break
    print(f"  {tag}: {n}")
    return n


if __name__ == "__main__":
    JOBS = [
        ("ge_pf", "https://moscow.iz-gazobetona.ru/portfolio", 200),
        ("ge_obj", "https://moscow.iz-gazobetona.ru/", 120),
        ("gb_main", "https://goodbuild.pro/", 120),
        ("ks_main", "https://www.doma-iz-bloka.ru/", 70),
        ("az_port", "https://antonovdom.ru/portfolio/", 40),
        ("az_main", "https://antonovdom.ru/", 40),
        ("gz", "https://gzbtn.ru/photos", 60),
        ("gz2", "https://gzbtn.ru/", 40),
    ]
    tot = 0
    for tag, url, lim in JOBS:
        tot += run(tag, url, lim)
    print("ИТОГО:", tot)
