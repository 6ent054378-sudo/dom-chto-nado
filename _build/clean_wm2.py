#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Удаление водяного знака: диффузионное заполнение (без scipy/cv2)."""
import os
import numpy as np
from PIL import Image

SRC = "/tmp/pool3"
X0, X1 = 0.598, 0.797
Y0, Y1 = 0.740, 0.830


def box3(a):
    """Среднее по 3x3 соседям (внутренние пиксели)."""
    s = np.zeros_like(a)
    s[1:-1, 1:-1] = (a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:]
                     + a[:-2, :-2] + a[:-2, 2:] + a[2:, :-2] + a[2:, 2:]
                     + 4.0 * a[1:-1, 1:-1]) / 12.0
    return s


def remove_watermark(path, out, width=1400, quality=68, iters=160):
    im = Image.open(path).convert("RGB")
    w0, h0 = im.size
    if w0 > 1500:
        im = im.resize((1500, round(h0 * 1500 / w0)), Image.LANCZOS)
    w, h = im.size
    a = np.asarray(im).astype(np.float32)

    x0, x1 = int(X0 * w), int(X1 * w)
    y0, y1 = int(Y0 * h), int(Y1 * h)

    # маска только «светлых» пикселей логотипа (он светлее фона),
    # плюс полное заполнение внутренней части надписи
    reg = a[y0:y1, x0:x1]
    lum = reg.mean(axis=2)
    thr = max(120.0, np.percentile(lum, 62))
    mask = np.zeros((h, w), dtype=bool)
    mask[y0:y1, x0:x1] = lum > thr

    # расширяем маску: за светлыми пикселями тёмный «контур» букв
    m = mask.copy()
    for _ in range(3):
        m[1:-1, 1:-1] |= (mask[:-2, 1:-1] | mask[2:, 1:-1] | mask[1:-1, :-2]
                          | mask[1:-1, 2:] | mask[:-2, :-2] | mask[:-2, 2:]
                          | mask[2:, :-2] | mask[2:, 2:])
        mask = m.copy()

    if not m.any():
        im.save(out, "WEBP", quality=quality, method=5)
        return

    # итеративная диффузия: заполняем пустые пиксели средним соседей
    cur = a.copy()
    wm = m[..., None]
    for _ in range(iters):
        avg = box3(cur)
        cur = np.where(wm, avg, cur)

    # мягкое сглаживание границы маски
    out_im = Image.fromarray(np.clip(cur, 0, 255).astype(np.uint8))
    if out_im.width > width:
        out_im = out_im.resize((width, round(out_im.height * width / out_im.width)), Image.LANCZOS)
    out_im.save(out, "WEBP", quality=quality, method=5)


if __name__ == "__main__":
    os.makedirs("/tmp/clean", exist_ok=True)
    n = 0
    for d in sorted(os.listdir(SRC)):
        p = os.path.join(SRC, d)
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            src = os.path.join(p, f)
            im = Image.open(src)
            w, h = im.size
            if w / h < 1.4:
                continue
            stem = f.rsplit(".", 1)[0]
            remove_watermark(src, f"/tmp/clean/{d}__{stem}.webp", 1400, 72)
            n += 1
    print("очищено:", n)
