#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Нейтральные аватары вместо фотографий реальных людей."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/img"
FONT_BOLD = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/fonts/Montserrat-SemiBold.woff2"
FONT_RG = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/fonts/Montserrat-Regular.woff2"

BASE = (53, 70, 62)      # #35463e
ACCENT = (191, 111, 60)  # #bf6f3c


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def avatar(initials, dst, size=700, bg=BASE, fg=(255, 255, 255), ring=True):
    im = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(im)
    # мягкий диагональный градиент
    for i in range(size):
        t = i / size
        light = (76, 103, 90)  # #4c675a
        col = tuple(int(bg[k] + (light[k] - bg[k]) * t) for k in range(3))
        d.line([(0, i), (size, i)], fill=col)
    if ring:
        d.ellipse([size * .07, size * .07, size * .93, size * .93],
                  outline=ACCENT, width=max(2, size // 90))
    f = font(FONT_BOLD, int(size * .34))
    bbox = d.textbbox((0, 0), initials, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1] + size * .02),
           initials, font=f, fill=fg)
    im.save(dst, "WEBP", quality=86, method=5)
    return im


if __name__ == "__main__":
    jobs = [
        ("sec6-1.webp", "АГ"),   # Артём Гаврилов — руководитель
        ("sec6-2.webp", "МН"),   # Марина Никитина — финдиректор
        ("sec6-3.webp", "ДК"),   # Дмитрий Ковалёв — руководитель проектов
        ("manager.webp", "АГ"),  # менеджер в модалке звонка
    ]
    for name, ini in jobs:
        avatar(ini, os.path.join(OUT, name))
        print("аватар:", name, ini)
