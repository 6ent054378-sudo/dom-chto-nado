#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Финальная сборка ассетов: проекты, недостающие изображения, favicon."""
import os, shutil, glob
from PIL import Image

OUT = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets"
IMG = os.path.join(OUT, "img")
A3 = "/tmp/pool"

TYP = [("Одинцово", "a3odincovo"), ("Соколово", "a3sokolovo"), ("Уматово", "a3umatovo"),
       ("Истра", "a3istra"), ("Губкино", "a3gubkino"), ("Миллениум", "a3millenium")]


def conv(src, dst, width=None, quality=70):
    if not os.path.exists(src):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
    if width and im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=5)
    return True


def pool_files(d):
    p = os.path.join(A3, d)
    return sorted(glob.glob(os.path.join(p, "*"))) if os.path.isdir(p) else []


# ---------- 1. Каталог типовых проектов ----------
for i, (name, pool) in enumerate(TYP, start=1):
    d = os.path.join(OUT, "projects", name)
    os.makedirs(d, exist_ok=True)
    fs = pool_files(pool)
    fs.sort(key=lambda f: -os.path.getsize(f))
    for j in range(7):
        if not fs:
            break
        src = fs[j % len(fs)]
        nm = f"b{i}obl" if j == 0 else f"b{i}-{j}"
        conv(src, os.path.join(d, nm + ".webp"), 1200, 68)
    print("проект", name, "->", len(os.listdir(d)))

# ---------- 2. Недостающие изображения ----------
# h1..h12 — выставочный дом
H_SRC = ["a3aprelevka", "a3ar01", "a3ar02", "a3ar03", "a3ar04", "a3ar05",
         "a3flamandia", "a3gubkino", "a3istra", "a3millenium", "a3renaissance", "a3sauna1"]
for i in range(1, 13):
    pool = H_SRC[(i - 1) % len(H_SRC)]
    fs = pool_files(pool)
    fs.sort(key=lambda f: -os.path.getsize(f))
    if fs:
        conv(fs[(i - 1) % len(fs)], os.path.join(IMG, f"h{i}.webp"), 1200, 68)

# k9..k14 — визуализации
K_SRC = ["a3ar01", "a3ar02", "a3ar03", "a3ar04", "a3ar05", "a3odincovo"]
for i in range(9, 15):
    pool = K_SRC[(i - 9) % len(K_SRC)]
    fs = pool_files(pool)
    fs.sort(key=lambda f: -os.path.getsize(f))
    if fs:
        conv(fs[(i - 9) % len(fs)], os.path.join(IMG, f"k{i}.webp"), 1100, 68)

# e13..e17 — галерея объектов
E_SRC = ["a3ar02", "a3ar03", "a3ar04", "a3ar05", "a3odincovo"]
for i in range(13, 18):
    pool = E_SRC[(i - 13) % len(E_SRC)]
    fs = pool_files(pool)
    fs.sort(key=lambda f: -os.path.getsize(f))
    if fs:
        conv(fs[(i - 13) % len(fs)], os.path.join(IMG, f"e{i}.webp"), 1100, 66)

# vid7..vid9 — превью видео-отзывов
for i in range(7, 10):
    pool = ["a3sokolovo", "a3odincovo", "a3millenium"][i - 7]
    fs = pool_files(pool)
    fs.sort(key=lambda f: -os.path.getsize(f))
    if fs:
        conv(fs[2], os.path.join(IMG, f"vid{i}.webp"), 800, 66)

# phone.webp — превью телефона с чатом
conv(os.path.join(A3, "a3odincovo", "a3odincovo_01.webp"), os.path.join(IMG, "phone.webp"), 800, 70)

# social.webp — og:image
conv(os.path.join(A3, "a3odincovo", "a3odincovo_00.webp"), os.path.join(IMG, "social.webp"), 1200, 70)

# ---------- 3. Favicon ----------
os.makedirs(os.path.join(IMG, "favicon"), exist_ok=True)
logo = Image.open(os.path.join(IMG, "logo.svg")).convert("RGBA") if False else None
fav = Image.new("RGBA", (512, 512), (53, 70, 62, 255))
try:
    import cairosvg  # noqa
except Exception:
    pass
# простой знак: домик терракотовой терракоты на тёмно-зелёном
from PIL import ImageDraw
d = ImageDraw.Draw(fav)
d.polygon([(256, 90), (430, 240), (82, 240)], fill=(191, 111, 60, 255))
d.rectangle([120, 240, 392, 420], fill=(255, 255, 255, 255))
d.rectangle([226, 320, 286, 420], fill=(53, 70, 62, 255))
fav.save(os.path.join(IMG, "favicon", "favicon-32x32.png"), "PNG")
fav.resize((32, 32), Image.LANCZOS).save(os.path.join(IMG, "favicon", "favicon-32x32.png"), "PNG")
fav.resize((16, 16), Image.LANCZOS).save(os.path.join(IMG, "favicon", "favicon-16x16.png"), "PNG")
fav.resize((180, 180), Image.LANCZOS).save(os.path.join(IMG, "favicon", "apple-touch-icon.png"), "PNG")
fav.resize((180, 180), Image.LANCZOS).save(os.path.join(IMG, "favicon", "apple-touch-icon.webp"), "WEBP", quality=90)
fav.resize((32, 32), Image.LANCZOS).save(os.path.join(IMG, "favicon", "favicon-32x32.webp"), "WEBP", quality=90)
fav.resize((16, 16), Image.LANCZOS).save(os.path.join(IMG, "favicon", "favicon-16x16.webp"), "WEBP", quality=90)

# ---------- 4. Удалить мусорные файлы (потерянное расширение) ----------
for f in glob.glob(os.path.join(IMG, "*")):
    base = os.path.basename(f)
    if os.path.isfile(f) and base.endswith("webp") and not base.endswith(".webp"):
        os.remove(f); print("удалён мусор:", base)

print("готово")
