#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Переписывает квиз (секция 32 + модальное окно) под строительство домов."""
import re, sys

SEC = "/tmp/work/sec"
LOG = []


def rep(c, old, new, label="", n_expect=1):
    pat = re.escape(old)
    pat = re.sub(r"(\\ )+", r"\\s+", pat)
    pat = pat.replace("\\\n", r"\\s+").replace("\n", r"\\s+")
    pat = pat.replace("\\\t", r"\\s+").replace("\t", r"\\s+")
    c2, n = re.subn(pat, lambda m: new, c)
    if n != n_expect:
        LOG.append((f"n={n} (ожидалось {n_expect})", label or old[:70]))
    return c2


def quiz(c):
    # --- заголовки ---
    c = rep(c, "Пройдите тест за 1&nbsp;минуту", "Пройдите тест за 1&nbsp;минуту", "q.title")
    c = rep(c, "стоимость вашего будущего ремонта", "стоимость вашего будущего дома", "q.title2")
    c = rep(c, "После прохождения теста вы получите:", "После прохождения теста вы получите:", "q.sub")
    c = rep(c, "Расчет стоимости <br> вашего ремонта", "Расчёт стоимости <br> вашего дома", "q.b1")
    c = rep(c, "Матрас One Premier <br> в подарок", "Эскиз и 3D-визуализация <br> в подарок", "q.b2")
    c = rep(c, "Бесплатную <br> консультацию", "Бесплатную <br> консультацию инженера", "q.b3")

    # --- шаг 1 ---
    c = rep(c, "01. Где планируете ремонт?", "01. Какой дом планируете построить?", "q.s1")
    c = rep(c, 'name="question1" value="Дом / коттедж"', 'name="question1" value="Одноэтажный дом"', "q.s1v1")
    c = rep(c, 'alt="Дом / коттедж"', 'alt="Одноэтажный дом"', "q.s1a1")
    c = rep(c, '<span class="section-32__option-label">Дом / коттедж</span>', '<span class="section-32__option-label">Одноэтажный дом</span>', "q.s1l1")
    c = rep(c, 'name="question1" value="Новостройка"', 'name="question1" value="Двухэтажный дом"', "q.s1v2")
    c = rep(c, 'alt="Новостройка"', 'alt="Двухэтажный дом"', "q.s1a2")
    c = rep(c, '<span class="section-32__option-label">Новостройка</span>', '<span class="section-32__option-label">Двухэтажный дом</span>', "q.s1l2")

    # --- шаг 2: район ---
    c = rep(c, "02. В каком ЖК планируете ремонт?", "02. В каком районе Подмосковья будете строить?", "q.s2")
    c = rep(c, '<option value="">Выберите ЖК</option>', '<option value="">Выберите район</option>', "q.s2o0")
    c = rep(c, '<option value="ЖК Континент">ЖК Континент</option>', '<option value="Истринский р-н">Истринский р-н</option>', "q.s2o1")
    c = rep(c, '<option value="ЖК Созвездие">ЖК Созвездие</option>', '<option value="Красногорский р-н">Красногорский р-н</option>', "q.s2o2")
    c = rep(c, '<option value="Резиденция Holms">Резиденция Holms</option>', '<option value="Одинцовский р-н">Одинцовский р-н</option>', "q.s2o3")
    c = rep(c, '<option value="Urban-квартал Svoboda">Urban-квартал Svoboda</option>', '<option value="Подольский р-н">Подольский р-н</option>', "q.s2o4")
    c = rep(c, '<option value="ЖК Норвуд">ЖК Норвуд</option>', '<option value="Чеховский р-н">Чеховский р-н</option>', "q.s2o5")
    c = rep(c, '<option value="ЖК Апгрейд">ЖК Апгрейд</option>', '<option value="Домодедовский р-н">Домодедовский р-н</option>', "q.s2o6")
    c = rep(c, '<option value="Квартал 55">Квартал 55</option>', '<option value="Наро-Фоминский р-н">Наро-Фоминский р-н</option>', "q.s2o7")
    c = rep(c, '<option value="ЖК Академия">ЖК Академия</option>', '<option value="Волоколамский р-н">Волоколамский р-н</option>', "q.s2o8")
    c = rep(c, '<option value="ЖК Zenlife">ЖК Zenlife</option>', '<option value="Звенигородский р-н">Звенигородский р-н</option>', "q.s2o9")
    c = rep(c, '<option value="ЖК Lake Town">ЖК Lake Town</option>', '<option value="Дмитровский р-н">Дмитровский р-н</option>', "q.s2o10")
    c = rep(c, '<option value="ЖК Парк Рояль">ЖК Парк Рояль</option>', '<option value="Ленинградское ш., до 30 км">Ленинградское ш., до 30 км</option>', "q.s2o11")
    c = rep(c, '<option value="Другой ЖК">Другой ЖК</option>', '<option value="Другой район">Другой район</option>', "q.s2o12")
    c = rep(c, '<span class="section-32__custom-select-value">Выберите ЖК</span>', '<span class="section-32__custom-select-value">Выберите район</span>', "q.s2ph")

    # --- шаг 3: площадь ---
    c = rep(c, "03. Какая площадь помещения?", "03. Какая площадь дома?", "q.s3")
    for old, new in [("20-40 кв.м", "80-120 кв.м"), ("40-50 кв.м", "120-150 кв.м"),
                     ("50-70 кв.м", "150-180 кв.м"), ("70-85 кв.м", "180-220 кв.м"),
                     ("85-100 кв.м", "220-260 кв.м"), ("Более 100 кв.м", "Более 260 кв.м")]:
        c = rep(c, f'value="{old}"', f'value="{new}"', f"q.s3v-{old}", n_expect=2)
        c = rep(c, f"<span>{old}</span>", f"<span>{new}</span>", f"q.s3l-{old}", n_expect=2)

    # --- шаг 4: комплектация ---
    c = rep(c, "04. Какой стиль вам больше нравится?", "04. Какая комплектация вас интересует?", "q.s4")
    for old, new in [("Современный", "Коробка"), ("Лофт", "Тёплый контур"),
                     ("Классика", "White-box"), ("Скандинавский", "Под ключ"),
                     ("Затрудняюсь ответить", "Затрудняюсь ответить")]:
        c = rep(c, f'value="{old}"', f'value="{new}"', f"q.s4v-{old}", n_expect=2)
        c = rep(c, f'alt="{old}"', f'alt="{new}"', f"q.s4a-{old}", n_expect=2)
        c = rep(c, f'class="section-32__option-label">{old}</span>', f'class="section-32__option-label">{new}</span>',
                f"q.s4l-{old}", n_expect=2)
    c = rep(c, 'alt="Затрудняюсь"', 'alt="Затрудняюсь ответить"', "q.s4a-z")

    # --- шаг 5: сроки ---
    c = rep(c, "05. Как скоро планируете ремонт?", "05. Когда планируете начать строительство?", "q.s5")
    for old, new in [("Как можно скорее", "В ближайший месяц"),
                     ("Через 2-3 недели", "Через 1-3 месяца"),
                     ("Через месяц", "Через 3-6 месяцев"),
                     ("Через несколько месяцев", "Через полгода и позже"),
                     ("Не знаю точно", "Пока изучаю")]:
        c = rep(c, f'value="{old}"', f'value="{new}"', f"q.s5v-{old}", n_expect=2)
        c = rep(c, f"<span>{old}</span>", f"<span>{new}</span>", f"q.s5l-{old}", n_expect=2)

    # --- форма ---
    c = rep(c, "Напишите ваш телефон,<b> чтобы мы отправили вам расчет <br> стоимости, а также",
            "Напишите ваш телефон,<b> чтобы мы отправили вам расчёт <br> стоимости, а также", "q.f1")
    c = rep(c, "Получить расчет стоимости + закрепить подарок", "Получить расчёт стоимости + закрепить подарок", "q.f2", n_expect=2)
    c = rep(c, 'name="from" value="Получить расчет стоимости + закрепить подарок"',
            'name="from" value="Получить расчёт стоимости дома + закрепить подарок"', "q.f3", n_expect=2)
    c = rep(c, 'name="from" value="Получить расчет стоимости + закрепить подарок"',
            'name="from" value="Получить расчёт стоимости дома + закрепить подарок"', "q.f3b")
    return c


# --- секция 32 ---
p = f"{SEC}/32.html"
c = open(p, encoding="utf-8").read()
c = quiz(c)
open(p, "w", encoding="utf-8").write(c)

# --- модальное окно квиза в TAIL ---
p = f"{SEC}/FOOTER.html"
c = open(p, encoding="utf-8").read()
if 'data-quiz-step="0"' in c:
    c = quiz(c)
    open(p, "w", encoding="utf-8").write(c)
    print("модалка квиза: переписана")
else:
    LOG.append(("MISS", "quiz-modal"))

print("\n===== ПРОПУСКИ =====")
for t in LOG:
    print("  ", t[0], ":", t[1])
print("пропусков:", len(LOG))
