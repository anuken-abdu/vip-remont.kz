# -*- coding: utf-8 -*-
"""Картинка для соцсетей и мессенджеров 1200×630 через Playwright. Запуск: python3 src/og.py"""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import BRAND, PHONE_DISPLAY
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; A = ROOT / "assets"
font = lambda f: (A / "fonts" / f).as_uri()
logo = f'<img class="l" src="{(A / "logo.webp").as_uri()}">' if (A / "logo.webp").exists() else '<div class="l">VIP<i>Remont</i></div>'
OG = f"""<html><head><style>
@font-face{{font-family:M;src:url({font('manrope-cyrillic-wght-normal.woff2')});font-weight:200 800}}@font-face{{font-family:M;src:url({font('manrope-latin-wght-normal.woff2')});font-weight:200 800;unicode-range:U+0000-00FF}}
body{{margin:0;width:1200px;height:630px;font-family:M;color:#fff;position:relative;overflow:hidden;
background:radial-gradient(120% 90% at 85% 10%,#5b7bff 0%,rgba(91,123,255,0) 55%),radial-gradient(90% 80% at 10% 100%,#2450ff 0%,rgba(36,80,255,0) 60%),linear-gradient(135deg,#0d1650,#1b2f9e)}}
.l{{position:absolute;left:80px;top:64px;font-size:36px;font-weight:800;letter-spacing:-1px;height:48px}}.l i{{font-style:normal;font-weight:600}}
img.l{{height:56px}}
h1{{position:absolute;left:76px;top:170px;margin:0;font-size:80px;line-height:1.04;font-weight:800;letter-spacing:-2.5px;width:1000px}}
.f{{position:absolute;left:80px;bottom:66px;font-size:27px;font-weight:600;width:1040px;line-height:1.45}}
</style></head><body>{logo}
<h1>Ремонт квартир в Астане — от косметического до элитного</h1>
<div class="f">Смета за 3 часа после замера · цена в договоре · своя бригада<br><b>{PHONE_DISPLAY}</b></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    fd, tmp = tempfile.mkstemp(suffix=".html"); os.write(fd, OG.encode()); os.close(fd)
    pg.goto(Path(tmp).as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
    pg.screenshot(path=str(A / "og.png")); os.unlink(tmp); b.close()
print("og.png готова")
