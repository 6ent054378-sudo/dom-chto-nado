#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Удаление водяного знака «ЮРЖИЛСЕРВИС» с фасадных рендеров (белый фон).

Знак — светло-серый логотип, нарисованный поверх изображения. На рендерах он
лежит в нижней центральной части дома. Алгоритм:
  1) находим область знака по характерному светлому «тексту» внутри контура
     дома (ищем связную группу пикселей, которые светлее фона, но темнее
     чистого белого);
  2) заполняем область диффузией (как раньше) — на белом фоне это даёт
     ровную заливку без следов.
"""
import os, glob
import numpy as np
from PIL import Image, ImageFilter

IMG = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/img"


def box3(a):
    s = np.zeros_like(a)
    s[1:-1, 1:-1] = (a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:]
                     + a[:-2, :-2] + a[:-2, 2:] + a[2:, :-2] + a[2:, 2:]
                     + 4.0 * a[1:-1, 1:-1]) / 12.0
    return s


def find_watermark(im):
    """Ищет прямоугольник со знаком: в нижней половине, где много
    'светлых, но не белых' пикселей, собранных в плотную группу."""
    g = np.asarray(im.convert("L")).astype(np.float32)
    h, w = g.shape
    # зона: нижние 45% по высоте, центральные 60% по ширине
    y0, y1 = int(h * 0.55), h
    x0, x1 = int(w * 0.20), int(w * 0.80)
    reg = g[y0:y1, x0:x1]
    # «почти белый, но не белый» — ореол знака
    halo = (reg > 195) & (reg < 248)
    if halo.mean() < 0.004:
        return None
    ys, xs = np.nonzero(halo)
    if len(ys) < 200:
        return None
    # берём кластер по нижней четверти (знак стоит низко)
    yy = ys + y0
    q = np.percentile(yy, 78)
    sel = yy >= q
    if sel.sum() < 120:
        return None
    yy2 = yy[sel]; xx2 = xs[sel] + x0
    bx0, bx1 = int(xx2.min()), int(xx2.max())
    by0, by1 = int(yy2.min()), int(yy2.max())
    # расширяем на 12% от высоты знака (надписи «центр недвижимости и права» выше)
    pad = int((by1 - by0) * 0.75) + 8
    by0 = max(0, by0 - pad)
    bx0 = max(0, bx0 - 14)
    bx1 = min(w, bx1 + 14)
    by1 = min(h, by1 + 12)
    return bx0, by0, bx1, by1


def clean(path, out, iters=220):
    im = Image.open(path).convert("RGB")
    box = find_watermark(im)
    if not box:
        return False
    bx0, by0, bx1, by1 = box
    w, h = im.size
    a = np.asarray(im).astype(np.float32)
    region = a[by0:by1, bx0:bx1]
    lum = region.mean(axis=2)
    # маска: пиксели знака (светлые, но не чисто белые) + их тёмный контур
    thr = max(150.0, np.percentile(lum, 55))
    m = np.zeros((h, w), dtype=bool)
    m[by0:by1, bx0:bx1] = lum > thr
    # расширение маски на соседние тёмные пиксели (контур букв)
    mm = m.copy()
    for _ in range(2):
        mm[1:-1, 1:-1] |= (m[:-2, 1:-1] | m[2:, 1:-1] | m[1:-1, :-2] | m[1:-1, 2:]
                           | m[:-2, :-2] | m[:-2, 2:] | m[2:, :-2] | m[2:, 2:])
        m = mm.copy()
    if not m.any():
        return False
    cur = a.copy()
    wm = m[..., None]
    for _ in range(iters):
        avg = box3(cur)
        cur = np.where(wm, avg, cur)
    out_im = Image.fromarray(np.clip(cur, 0, 255).astype(np.uint8))
    out_im = out_im.filter(ImageFilter.GaussianBlur(radius=1.2))
    out_im.save(out, "WEBP", quality=66, method=5)
    return True


if __name__ == "__main__":
    n = 0
    for f in sorted(glob.glob(os.path.join(IMG, "a[1-6]-*.webp"))):
        im = Image.open(f).convert("L")
        if (np.asarray(im) > 235).mean() < 0.20:
            continue
        if clean(f, f):
            n += 1
            print("очищен:", os.path.basename(f))
    print("итого:", n)
