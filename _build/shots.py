#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скриншот-обход всех блоков сайта (десктоп + мобайл)."""
import subprocess, os, time, sys

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8903/index.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/shots"
SESSION = sys.argv[3] if len(sys.argv) > 3 else "ihQ"
SECTIONS = ["1", "3", "27", "15", "28", "32", "29", "4", "8", "24", "10", "5",
            "16", "31", "30", "12", "14", "22", "7", "6", "23", "26"]
os.makedirs(OUT, exist_ok=True)


def ab(*args):
    return subprocess.run(["agent-browser", "--session", SESSION] + list(args),
                          capture_output=True, text=True).stdout.strip()


def js(code):
    return ab("eval", code)


ab("open", URL, "--viewport", "1440x900")
time.sleep(5)
js("localStorage.setItem('cookieConsentAt',String(Date.now()));"
   "sessionStorage.setItem('cookieConsentShown','1');"
   "var c=document.getElementById('cookie-notice');if(c)c.remove();"
   "document.querySelector('[data-video-sticky-close]')?.click();'ok'")
time.sleep(1)

for n in SECTIONS:
    js("(function(){var s=document.querySelector('.section-%s');if(!s)return 0;"
       "s.scrollIntoView();window.scrollBy(0,-70);return 1})()" % n)
    time.sleep(1.3)
    ab("screenshot", f"{OUT}/s{n}.png")

ab("set", "viewport", "390", "844")
time.sleep(1)
for n in SECTIONS:
    js("(function(){var s=document.querySelector('.section-%s');if(!s)return 0;"
       "s.scrollIntoView();window.scrollBy(0,-60);return 1})()" % n)
    time.sleep(1.0)
    ab("screenshot", f"{OUT}/m{n}.png")

print("готово:", len(os.listdir(OUT)), "файлов")
