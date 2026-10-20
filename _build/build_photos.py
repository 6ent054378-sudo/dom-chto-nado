#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сбор и раскладка фото для сайта «Дом что надо».

Источники — только живые сайты строительных компаний:
  ge_pf / ge_obj — Газобетон-Эксперт (реальные объекты и ход стройки)
  gb_main        — GOODBUILD (простые дома; кадры с логотипом на фасаде отсекаются)
  gz / gz2       — Газ&Бетон (реальные объекты)
  az_port/az_main— ANTONOVDOM (простые дома)
  ks_main        — KeyStone (люди и объекты; люди отсекаются)

Правила:
  * без водяных знаков и чужих логотипов;
  * без людей (в разделе «Команда» — аватары-инициалы);
  * простые дома, без особняков;
  * одна картинка не встречается на сайте дважды (перцептивный хэш);
  * в одной галерее — один дом.
"""
import os, re, glob, json
import numpy as np
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

ROOT = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77"
IMG = os.path.join(ROOT, "assets/img")
PROJ = os.path.join(ROOT, "assets/projects")
POOL = "/tmp/pool6"

SOURCES = ["ge_pf", "ge_obj", "gb_main", "gz", "gz2", "az_port", "az_main", "ks_main"]

# кадры с промо-брендами и графикой
SKIP_NAMES = {
    # промо-баннеры, сертификаты, документы
    "ge_pf_006.jpg", "ge_pf_007.jpg", "ge_pf_230.jpg",
    "ge_obj_025.png", "ge_obj_026.png", "ge_obj_028.jpg", "ge_obj_029.jpg",
    "ge_obj_252.jpg", "ge_pf_228.png", "ge_pf_229.png",
    # люди
    "ge_pf_223.png", "ge_pf_225.png", "ge_pf_227.jpg", "ge_pf_369.jpeg",
    "ge_obj_007.jpg", "ge_obj_246.png", "ge_obj_249.png", "ge_obj_250.png", "ge_obj_251.png",
    "ks_main_001.webp", "ks_main_003.webp", "ks_main_004.webp", "ks_main_024.webp",
    "ks_main_025.webp", "ks_main_026.webp", "ks_main_027.webp",
    "gb_main_000.jpg", "gb_main_112.jpg", "gb_main_118.jpg", "gb_main_121.png",
    "antonov_main_023.png", "az_main_005.png", "az_main_023.png", "az_main_006.png",
    "ks_main_164.webp", "gz_018.jpg",
    "ge_pf_348.jpg", "ge_pf_349.jpg", "ge_pf_362.jpg", "ge_pf_404.jpg",
    "ge_pf_410.jpg", "ge_pf_412.jpg",
}

FONT_BOLD = os.path.join(ROOT, "assets/fonts/Montserrat-SemiBold.woff2")


def ah(p, n=10):
    a = np.asarray(Image.open(p).convert("L").resize((n, n))).astype(np.float32)
    return (a > a.mean()).ravel()


def dh(p, n=10):
    a = np.asarray(Image.open(p).convert("L").resize((n + 1, n))).astype(np.float32)
    return (a[:, 1:] > a[:, :-1]).ravel()


def same(h1, h2):
    return int(np.count_nonzero(h1[0] != h2[0])) < 4 and int(np.count_nonzero(h1[1] != h2[1])) < 4


def gb_logo(path):
    """Оценка доли логотипа GoodBuild (оранжевый) на фасаде."""
    try:
        im = Image.open(path).convert("RGB")
        w, h = im.size
        a = np.asarray(im.crop((0, int(h * .40), w, int(h * .98)))).astype(np.int32)
        r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
        orange = ((r > 195) & (g > 130) & (g < 200) & (b < 95)).sum()
        return orange / (a.shape[0] * a.shape[1])
    except Exception:
        return 9.0


def skin_ratio(im):
    w, h = im.size
    a = np.asarray(im.crop((0, 0, w, int(h * .5))).resize((48, 48))).astype(np.float32)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    m = (r > 95) & (g > 40) & (b > 20) & ((r - np.maximum(g, b)) > 15) & (np.abs(r - g) > 15)
    return float(m[:24].mean())


def analyse(path):
    try:
        im = Image.open(path).convert("RGB")
        w, h = im.size
        if w < 330 or h < 220:
            return None
        a = np.asarray(im).astype(np.float32)
        lum = a.mean(axis=2)
        if float((lum > 235).mean()) > 0.28:
            return None                                        # план / схема
        if float((lum > 225).mean()) > 0.42:
            return None                                        # документ / баннер
        if float((lum > 200).mean()) > 0.60 and float(np.abs(a[:, :, 0] - a[:, :, 2]).mean()) < 12:
            return None                                        # карта / схема
        q16 = (np.asarray(im.resize((120, 90))).astype(np.int32) // 16)
        if len(np.unique(q16[:, :, 0] * 256 + q16[:, :, 1] * 16 + q16[:, :, 2])) < 55:
            return None                                        # карта/схема
        if skin_ratio(im) > 0.12:
            return None                                        # человек
        flat = (np.asarray(im.resize((60, 60))).reshape(-1, 3).astype(np.int32) // 24)
        _, cnt = np.unique(flat[:, 0] * 4096 + flat[:, 1] * 64 + flat[:, 2], return_counts=True)
        if cnt.max() / len(flat) > 0.34:
            return None                                        # студийный фон
        if w >= 700:
            sky = lum[:int(h * .12)]
            green = (a[:, :, 1] > a[:, :, 0] + 6).mean()
            if sky.std() < 26 and green < 0.05:
                return None                                    # интерьер
        if "/gb_main/" in path and gb_logo(path) > 0.0015:
            return None                                        # логотип GoodBuild на фасаде
        sig = (np.asarray(im.resize((6, 6))).astype(np.float32) / 255.0).ravel()
        return {"f": path, "sig": sig, "size": w * h, "ah": (ah(path), dh(path))}
    except Exception:
        return None


cand = []
for d in SOURCES:
    for f in glob.glob(os.path.join(POOL, d, "*")):
        if not os.path.isfile(f) or os.path.basename(f) in SKIP_NAMES:
            continue
        info = analyse(f)
        if info:
            cand.append(info)
cand.sort(key=lambda c: -c["size"])
print("пул пригодных кадров:", len(cand))

used = []


def is_free(c):
    return not any(same(c["ah"], u) for u in used)


def occupy(c):
    used.append(c["ah"])


def group(items, n, dist):
    groups, taken = [], set()
    for i, it in enumerate(items):
        if i in taken:
            continue
        g = [i]
        taken.add(i)
        for j in range(i + 1, len(items)):
            if j in taken or len(g) >= n:
                continue
            if float(np.abs(it["sig"] - items[j]["sig"]).mean()) < dist:
                g.append(j)
                taken.add(j)
        if len(g) >= 3:
            groups.append(g)
    return groups


def fill(idx_group, n):
    files = []
    for j in idx_group:
        c = cand[j]
        if is_free(c):
            files.append(c)
            occupy(c)
    while len(files) < n:
        best = None
        for c in cand:
            if not is_free(c):
                continue
            d = min(float(np.abs(c["sig"] - cand[j]["sig"]).mean()) for j in idx_group)
            if best is None or d < best[0]:
                best = (d, c)
        if not best:
            break
        files.append(best[1])
        occupy(best[1])
    for c in files:
        occupy(c)
    return files[:n]


def save(src, dst, width=1200, quality=68):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    try:
        im = Image.open(src).convert("RGB")
    except Exception:
        return False
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=quality, method=5)
    return True


# ---------------- 6 объектов (реальная стройка) ----------------
build = [c for c in cand if any(s in c["f"] for s in ("/ge_pf/", "/ge_obj/", "/gz")) and not c["f"].endswith("kb_main_121.png")]
ready = [c for c in cand if c not in build]
print("стройка:", len(build), "готовые:", len(ready))

OBJ_GROUPS = group(build, 7, 0.34)
PROJ_GROUPS = group(ready, 7, 0.30)
print("групп объектов:", len(OBJ_GROUPS), "групп проектов:", len(PROJ_GROUPS))

for i, g in enumerate(OBJ_GROUPS[:6]):
    files = fill(g, 7)
    for k, c in enumerate(files):
        save(c["f"], os.path.join(IMG, (f"a{i+1}obl" if k == 0 else f"a{i+1}-{k}") + ".webp"), 1200, 66)
    print(f"  объект {i+1}: {len(files)}")

PROJ_NAMES = ["Одинцово", "Соколово", "Уматово", "Истра", "Губкино", "Миллениум"]
for i, g in enumerate(PROJ_GROUPS[:6]):
    files = fill(g, 7)
    d = os.path.join(PROJ, PROJ_NAMES[i])
    for k, c in enumerate(files):
        save(c["f"], os.path.join(d, (f"b{i+1}obl" if k == 0 else f"b{i+1}-{k}") + ".webp"), 1200, 66)
    print(f"  проект {PROJ_NAMES[i]}: {len(files)}")


# ---------------- прочие слоты ----------------
def take(n, big=False):
    out = []
    for c in cand:
        if not is_free(c):
            continue
        if big and c["size"] < 700 * 420:
            continue
        out.append(c)
        occupy(c)
        if len(out) >= n:
            break
    return out


GROUPS = [
    ("sec2-", 6, 1200, 68, True), ("sec27-", 5, 1100, 68, True), ("sec4-", 4, 1100, 68, True),
    ("sec5-", 3, 1100, 68, True), ("sec10-", 7, 1000, 66, False), ("sec14-", 3, 1200, 68, True),
    ("sec22-", 3, 900, 68, False), ("e", 17, 1100, 66, True), ("k", 14, 1100, 66, False),
    ("h", 12, 1200, 66, True), ("quiz4-", 5, 700, 64, False),
]
SINGLES = [
    ("sec1", 1920, 58, True), ("house", 1400, 66, True), ("phone1", 800, 70, False),
    ("phone2", 800, 70, False),
    ("d1-1", 1200, 70, True), ("d1-2", 1200, 70, True),
    ("d2-1", 1200, 70, True), ("d2-2", 1200, 70, True),
    ("d3-1", 1200, 70, True), ("d3-2", 1200, 70, True),
    ("sec30-1", 900, 66, False), ("sec30-2", 900, 66, False), ("sec30-3", 900, 66, False),
    ("steps1", 700, 66, False), ("steps2", 700, 66, False), ("steps3", 700, 66, False),
    ("sec30-sl", 900, 68, True),
    ("quiz1-1", 900, 66, True), ("quiz1-2", 900, 66, True), ("200", 900, 66, True),
]
for pref, n, w, q, big in GROUPS:
    files = take(n, big)
    for k, c in enumerate(files, start=1):
        save(c["f"], os.path.join(IMG, f"{pref}{k}.webp"), w, q)
    if len(files) < n:
        print("  ! не хватило:", pref, len(files), "/", n)
for name, w, q, big in SINGLES:
    files = take(1, big)
    if files:
        save(files[0]["f"], os.path.join(IMG, name + ".webp"), w, q)
    else:
        print("  ! нет картинки для", name)


# ---------------- фоны секций (CSS) ----------------
DARK = {"sec1.webp": (1920, 58, .55), "sec24.webp": (1920, 58, .45), "sec32.webp": (1920, 56, .5),
        "sec9.webp": (1600, 58, .6), "sec20.webp": (1600, 58, .6), "sec21.webp": (1600, 58, .6),
        "call-back.webp": (1200, 70, .8), "quiz-right.webp": (1000, 70, .95)}
PLAIN = {"thanks.webp": (1200, 68, 1.0)}
for name, spec in list(DARK.items()) + list(PLAIN.items()):
    w, q = spec[0], spec[1]
    bright = spec[2] if len(spec) > 2 else 1.0
    dst = os.path.join(IMG, name)
    if os.path.exists(dst):
        continue
    files = take(1, True)
    if not files:
        print("  ! нет фона для", name); continue
    im = Image.open(files[0]["f"]).convert("RGB")
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(bright)
    im.save(dst, "WEBP", quality=q, method=5)
    print("  фон:", name)


# ---------------- аватары вместо людей ----------------
def avatar(initials, dst, size=700):
    im = Image.new("RGB", (size, size), (53, 70, 62))
    d = ImageDraw.Draw(im)
    for i in range(size):
        t = i / size
        col = tuple(int((53, 70, 62)[k] + ((76, 103, 90)[k] - (53, 70, 62)[k]) * t) for k in range(3))
        d.line([(0, i), (size, i)], fill=col)
    d.ellipse([size * .07, size * .07, size * .93, size * .93], outline=(191, 111, 60), width=max(3, size // 70))
    try:
        f = ImageFont.truetype(FONT_BOLD, int(size * .34))
    except Exception:
        f = ImageFont.load_default()
    bbox = d.textbbox((0, 0), initials, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), initials, font=f, fill=(255, 255, 255))
    im.save(dst, "WEBP", quality=88, method=5)


for name, ini in [("sec6-1.webp", "АГ"), ("sec6-2.webp", "МН"), ("sec6-3.webp", "ДК"), ("manager.webp", "АГ")]:
    avatar(ini, os.path.join(IMG, name))
    print("  аватар:", name, ini)

print("готово")
