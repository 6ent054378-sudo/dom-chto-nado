#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Точечные правки оставшихся мест + пересборка слайдера section-29."""
import re, sys
sys.path.insert(0, "/tmp/work")
import importlib
b = importlib.import_module("build_lib") if False else None

SEC = "/tmp/work/sec"
LOG = []


def flexpat(text):
    t = re.sub(r"(?i)<br\s*/?>", " ", text)
    words = t.split()
    return r"(?:\s|<br\s*/?>)+".join(re.escape(w) for w in words)


def reinsert_br(matched, new):
    if "<br" in new.lower():
        return new
    parts = re.split(r"(?i)<br\s*/?>", matched)
    idxs, cnt = [], 0
    for i, p in enumerate(parts):
        if i > 0:
            idxs.append(cnt)
        cnt += len(p.split())
    out = new.split()
    for pos in sorted(idxs, reverse=True):
        if 0 < pos < len(out):
            out.insert(pos, "<br>")
    return " ".join(out)


def rep(c, old, new, label=""):
    c2, n = re.subn(flexpat(old), lambda m: reinsert_br(m.group(0), new), c)
    if n == 0:
        LOG.append(("MISS", label or old[:70]))
    elif n > 1:
        LOG.append(("MULTI x%d" % n, label or old[:70]))
    return c2


def load(n):
    return open(f"{SEC}/{n}.html", encoding="utf-8").read()


def save(n, c):
    open(f"{SEC}/{n}.html", "w", encoding="utf-8").write(c)


def match_div_end(c, start):
    """Индекс </div>, закрывающего div, начинающийся в start."""
    i = start
    depth = 0
    for m in re.finditer(r"<div\b|</div>", c[start:]):
        tok = m.group(0)
        if tok == "</div>":
            depth -= 1
            if depth == 0:
                return start + m.end()
        else:
            depth += 1
    return -1


# ============================ 5 ============================
c = load(5)
c = rep(c, "Строгое следование технологии", "Строгое следование технологии", "s5.t1")
c = rep(c, "Работаем строго по технологическим картам. Мы делаем все «по уму», чтобы ремонт служил долгие годы",
        "Работаем строго по технологическим картам и СП 15.13330, 17.13330, 70.13330. Мы делаем все «по уму», чтобы дом служил долгие годы", "s5.d1")
c = rep(c, "Идеально ровные стены и пол", "Идеально ровная кладка", "s5.t2")
c = rep(c, "Каждая стена, угол и шов – выверены лазерным уровнем, чтобы финишное покрытие легло ровно и выглядело безупречно при любом освещении, а напольное покрытие не хрустело и не разъезжалось со временем",
        "Каждый ряд блока, угол и шов – выверены лазерным уровнем: клеевой шов не более 3 мм, вертикальность рядов в пределах ±5 мм на этаж, а стена со временем не повело и не потрескалась", "s5.d2")
c = rep(c, "Чистая работа - наша визитная карточка", "Чистая работа - наша визитная карточка", "s5.t3")
c = rep(c, "Зазоры и стыки сведены идеально: плитка и панели сходятся без щелей, а швы выглядят как единая линия",
        "Зазоры и стыки сведены идеально: отмостка, примыкание кровли и ввод коммуникаций выглядят как единая система, а скрытые работы зафиксированы фотоотчётом", "s5.d3")
save(5, c)

# ============================ 10 (списки <li>) ============================
c = load(10)
BRANDS = {
    "Ravak": "Bonolit", "Boheme": "Ytong", "LEMARK": "Aeroc", "MELANA": "LITECOM",
    "D&K": "марка D400", "ALCa PLAST": "толщина 375–400 мм", "RGW": "ГОСТ 31360", "ASTRA FORM": "без усадки",
    "Lotten": "Bergauf", "KZTO": "Mapei", "Royal": "Ceresit", "Thermo": "Weber",
    "Italon": "монолитный ж/б", "Kerama marazzi": "заводские ЖБ плиты",
    "Colisium Gres": "фиброармопояс", "Гранитея": "анкерные связи",
    "Clix": "Rockwool", "Pergo": "Пеноплэкс", "quick Step": "Техноэласт", "Planker": "паробарьер",
    "WESTSTYLE": "металлочерепица", "HOLZ": "мягкая кровля", "RADADOORS": "водосток", "ESTET": "снегозадержание",
    "Duluxe, Flugger": "VEKA", "ORDO DECOR": "REHAU", "ARTPOLE": "Profile",
    "AFFRESCO": "панорамные", "WALL STREET": "входная группа", "FACTURA": "москитные сетки",
}
for old, new in BRANDS.items():
    c = rep(c, f"<li>{old}</li>", f"<li>{new}</li>", f"s10.{old}")
save(10, c)

# ============================ 30 (gantt в комментариях) ============================
c = load(30)
c = rep(c, "Разработка документации", "Геология участка", "s30.g1")
c = rep(c, "Черновые работы", "Рабочая документация", "s30.g1b")
c = rep(c, "Чистовые работы", "Смета и договор", "s30.g1c")
c = rep(c, "Клининг", "Договор и график платежей", "s30.g1d")
c = rep(c, "Проектирование мебели", "Фундамент", "s30.g2")
c = rep(c, "Производство мебели", "Кладка стен", "s30.g2b")
c = rep(c, "Сборка", "Перекрытия и армопояс", "s30.g2c")
c = rep(c, "Подбор тканей и дизайн", "Окна и двери", "s30.g3")
c = rep(c, "Пошив текстиля", "Сети и вентиляция", "s30.g3b")
c = rep(c, "Повес", "Отделка и уборка", "s30.g3c")
c = rep(c, 'alt="Ремонт"', 'alt="Проект"', "s30.alt1")
c = rep(c, 'alt="Мебель"', 'alt="Строительство"', "s30.alt2")
c = rep(c, 'alt="Текстиль"', 'alt="Инженерия и отделка"', "s30.alt3")
save(30, c)

# ============================ 22 ============================
c = load(22)
c = rep(c, "Регулярные фото- и видеоотчёты", "Регулярные фото- и видеоотчёты", "s22.1")
c = rep(c, "Чат в мессенджере", "Чат в мессенджере", "s22.2")
c = rep(c, "для оперативной связи с дизайнером и прорабом", "для оперативной связи с инженером и прорабом", "s22.2b")
c = rep(c, "на встрече дизайнер и прораб показывают выполненные работы и фиксируют детали",
        "на встрече инженер и прораб показывают выполненные работы и фиксируют детали", "s22.3")
save(22, c)

# ============================ 6 ============================
c = load(6)
c = rep(c, "Экосистема «Как Надо» –", "Команда idealhome77 –", "s6.t")
c = rep(c, "более 23 лет", "более 13 лет", "s6.t2")
c = rep(c, "опыта в создании интерьеров", "опыта в строительстве домов", "s6.t3")
save(6, c)

# ============================ 26 ============================
c = load(26)
c = rep(c, "Пн — Пт, 9:00 — 18:00", "Пн — Пт, 9:00 — 20:00", "s26.time")
c = rep(c, "Сб, 10:00 — 16:00", "Сб, 10:00 — 17:00", "s26.time2")
save(26, c)

# ============================ 29: пересборка главного слайдера ============================
TYP = [("Одинцово", 1), ("Соколово", 2), ("Уматово", 3),
       ("Истра", 4), ("Губкино", 5), ("Миллениум", 6)]
c = load(29)
anchor = c.find('<div class="section-29__main-slider swiper" data-section-29-main>')
if anchor < 0:
    LOG.append(("MISS", "s29.anchor"))
else:
    ww = c.find('<div class="swiper-wrapper">', anchor)
    end = match_div_end(c, ww)
    blocks = []
    for name, n in TYP:
        items = [f"b{n}obl"] + [f"b{n}-{k}" for k in range(1, 7)]
        cells = []
        for im in items:
            cells.append(
                f'''<div class="swiper-slide"><a href="./assets/projects/{name}/{im}.webp" data-fancybox="section29-gallery-{n}"
\t\t\t\t\t\t\t\t\t\t\tclass="section-29__slide _adaptive-pic _radius20"><img class="section-29__img-lazy" data-src="./assets/projects/{name}/{im}.webp" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3C/svg%3E"
\t\t\t\t\t\t\t\t\t\t\talt="{name}"><span class="section-15__label">{name}</span></a>
\t\t\t\t\t\t\t\t</div>''')
        blocks.append(
            f'''<div class="swiper-slide">
\t\t\t\t\t\t<div class="section-29__inner-slider swiper" data-section-29-inner data-section-29-inner-index="{n-1}">
\t\t\t\t\t\t\t<div class="swiper-wrapper">
\t\t\t\t\t\t\t\t{chr(10).join(cells)}
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t\t<div class="section-29__inner-nav">
\t\t\t\t\t\t\t\t<button type="button" class="section-29__inner-arrow _slider-arrow-dark section-29__inner-arrow_prev swiper-button-prev" aria-label="Назад"></button>
\t\t\t\t\t\t\t\t<button type="button" class="section-29__inner-arrow _slider-arrow-dark section-29__inner-arrow_next swiper-button-next" aria-label="Вперёд"></button>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t</div>
\t\t\t\t\t</div>''')
    new = "\n" + "\n".join(blocks) + "\n\t\t\t\t\t\t\t"
    c = c[:ww + len('<div class="swiper-wrapper">')] + new + c[end - len("</div>"):]
    print("s29: главный слайдер пересобран")
save(29, c)

print("\n===== ПРОПУСКИ =====")
miss = [x for x in LOG if x[0] == "MISS"]
for t in LOG:
    print(f"  {t[0]}: {t[1]}")
print("пропусков:", len(miss))
