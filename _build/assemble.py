#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка index.html из отдельных файлов секций."""
import re, os

HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, "sections")
DST = os.path.abspath(os.path.join(HERE, "..", "index.html"))

ORDER = ["1", "3", "27", "15", "28", "32", "29", "4", "8", "24", "10", "5",
         "16", "31", "30", "12", "14", "22", "7", "6", "23", "26"]

head = open(os.path.join(SEC, "HEAD.html"), encoding="utf-8").read()
footer = open(os.path.join(SEC, "FOOTER.html"), encoding="utf-8").read()

parts = [head, "\n\t<main>\n\t\t<div class=\"wrapper\">\n"]
for n in ORDER:
    parts.append(open(os.path.join(SEC, f"{n}.html"), encoding="utf-8").read())
    parts.append("\n")
parts.append(footer)

html = "".join(parts)

html = html.replace('./assets/img/logo2.webp', './assets/img/logo-light.svg')

# счётчик Метрики клиента референса -> условный
METRIKA_OLD = """	ym(0, 'init', {
			webvisor: true,
			clickmap: true,
			referrer: document.referrer,
			url: location.href,
			accurateTrackBounce: true,
			trackLinks: true
		})"""
METRIKA_NEW = """	ym(window.IdealHomeMetrikaId, 'init', {
			webvisor: true,
			clickmap: true,
			referrer: document.referrer,
			url: location.href,
			accurateTrackBounce: true,
			trackLinks: true
		})"""
if METRIKA_OLD in html:
    html = html.replace(METRIKA_OLD, METRIKA_NEW)
html = html.replace("ym(88648559,", "ym(0,")
html = html.replace("https://mc.yandex.ru/watch/88648559", "https://mc.yandex.ru/watch/0")

KEYS = """	<!-- Ключи интеграций: заполнить перед запуском (см. README) -->
	<script>
		window.IdealHomeYandexMapsKey = "";   // API-ключ Яндекс.Карт
		window.IdealHomeMetrikaId = 0;         // ID счётчика Яндекс.Метрики
	</script>
</head>"""
if "IdealHomeYandexMapsKey" not in html:
    html = html.replace("</head>", KEYS, 1)

open(DST, "w", encoding="utf-8").write(html)
print("собрано:", DST, len(html), "байт")
for tag in ("div", "section", "main", "form"):
    o = len(re.findall(r"<%s\b" % tag, html))
    c = len(re.findall(r"</%s>" % tag, html))
    if o != c:
        print(f"  ! ДИСБАЛАНС {tag}: {o} / {c}")
print("  секций:", len(re.findall(r"<section class=", html)))
