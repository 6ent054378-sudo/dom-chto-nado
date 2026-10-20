#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Мок-документов: договор, акт приёмки, гарантийный сертификат (страница-демо)."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/img"
FB = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/fonts/Montserrat-SemiBold.woff2"
FR = "/Users/admin/Desktop/work/01_project/marketing/gazobeton/сases/idealhome77/assets/fonts/Montserrat-Regular.woff2"

W, H = 1240, 1754  # A4 при 150 dpi
PAPER = (252, 251, 248)
INK = (44, 48, 46)
GREY = (150, 154, 152)
ACCENT = (191, 111, 60)


def f(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def doc(title, subtitle, rows, footer, path):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    fb, fr, fs = f(FB, 30), f(FR, 20), f(FR, 15)

    # рамка
    d.rectangle([40, 40, W - 40, H - 40], outline=(222, 220, 214), width=2)

    # шапка
    d.text((100, 110), "idealhome77", font=fb, fill=ACCENT)
    d.text((100, 150), "Дома из газобетона под ключ · Москва и МО", font=fs, fill=GREY)
    d.line([(100, 190), (W - 100, 190)], fill=(225, 223, 217), width=2)

    # заголовок
    d.text((100, 250), title, font=f(FB, 42), fill=INK)
    d.text((100, 310), subtitle, font=fs, fill=GREY)

    y = 400
    for label, value in rows:
        d.text((100, y), label, font=fs, fill=GREY)
        d.text((430, y - 4), value, font=fr, fill=INK)
        d.line([(100, y + 34), (W - 100, y + 34)], fill=(233, 231, 226), width=1)
        y += 78

    # блок подписей
    y += 120
    d.text((100, y), footer[0], font=f(FB, 22), fill=INK)
    y += 60
    d.line([(100, y + 60), (420, y + 60)], fill=(190, 190, 186), width=2)
    d.line([(700, y + 60), (W - 100, y + 60)], fill=(190, 190, 186), width=2)
    d.text((100, y + 72), "Заказчик", font=fs, fill=GREY)
    d.text((700, y + 72), "Подрядчик · ООО «АйдиалХоум77»", font=fs, fill=GREY)

    # печать
    d.ellipse([W - 330, H - 320, W - 150, H - 140], outline=(214, 196, 186), width=3)
    d.ellipse([W - 315, H - 305, W - 165, H - 155], outline=(214, 196, 186), width=2)
    d.text((W - 288, H - 252), "ДОГОВОР", font=f(FB, 20), fill=(196, 176, 164))
    d.text((W - 300, H - 218), "ПОДПИСАН", font=f(FB, 20), fill=(196, 176, 164))

    im.save(path, "WEBP", quality=82, method=5)
    return im


# 1. Договор подряда
doc("Договор подряда", "№ 77/2026 · г. Подольск, 12 марта 2026 г.", [
    ("Заказчик", "Иванов И. И. (пример оформления)"),
    ("Подрядчик", "ООО «АйдиалХоум77», ИНН 5047 739 501"),
    ("Объект", "Дом 156 м², Истринский р-н, д. Козино"),
    ("Комплектация", "Под ключ (тёплый контур + инженерия + отделка)"),
    ("Цена по договору", "11 940 000 ₽ — фиксируется, не меняется"),
    ("Срок строительства", "6 месяцев с даты подписания"),
    ("Оплата", "4 этапа, по факту приёмки каждого"),
    ("Гарантия", "15 лет на конструктив, 3 года на инженерию"),
], ("Подписи сторон",), f"{OUT}/IMG_4420.webp")

# 2. Акт приёмки этапа
doc("Акт приёмки этапа", "Этап 2 «Кладка стен и перекрытия» · 18 июля 2026 г.", [
    ("Объект", "Дом 128 м², Красногорский р-н, с. Знаменское"),
    ("Выполнено", "Кладка газобетона D400, шов до 3 мм; армопояс по периметру"),
    ("Объём", "1 250 м³ кладки, 42 м³ монолитного армопояса"),
    ("Отклонения", "Не выявлены, замеры в пределах ±5 мм на этаж"),
    ("Приёмка", "Подписана заказчиком, замечаний нет"),
    ("Следующий этап", "Кровля и контур"),
], ("Подписи сторон",), f"{OUT}/IMG_4421.webp")

# 3. Гарантийный сертификат
doc("Гарантийный сертификат", "На конструктив дома · действителен 15 лет", [
    ("Объект", "Дом 96 м², Подольский р-н, д. Козино"),
    ("Конструктив", "Фундамент, стены, армопояс, перекрытия, кровля"),
    ("Гарантийный срок", "15 лет с даты подписания акта приёмки"),
    ("Обслуживание", "Реакция на обращение — 3 рабочих дня"),
    ("Контакты сервиса", "+7 495 120-77-99, info@idealhome77.ru"),
    ("Демонстрационный образец", "Не является юридическим документом"),
], ("Подписи сторон",), f"{OUT}/IMG_4422.webp")

print("документы готовы")
