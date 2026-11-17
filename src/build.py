# -*- coding: utf-8 -*-
"""Генератор сайта VIP Remont: src/ → dist/. Запуск: python3 src/build.py
Тексты и данные — src/data.py. Фото — orig/ → python3 src/images.py. Логотип и иконки — orig/brand/ → python3 src/brand.py."""
import json, re, shutil, sys, html, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import *

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
VER = "1811262"
E = html.escape
SV = {s["slug"]: s for s in SERVICES}
CATN = {c: n for c, n, _ in CATS}
WA = f"https://wa.me/{WA_NUMBER}"
def wa(text): return WA + "?text=" + urllib.request.quote(text)
HELLO = "Здравствуйте! Хочу рассчитать ремонт."
POLICY = "/politika/"

# ---------------------------------------------------------------- служебные значки интерфейса (меню, звонок, стрелки — только функции)
_P = {
 "phone": '<path d="M5 3h4l2 5-3 2a11 11 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
 "up": '<path d="M12 20V5M5 12l7-7 7 7"/>', "back": '<path d="M20 12H5M12 5l-7 7 7 7"/>',
 "x": '<path d="M5 5l14 14M19 5L5 19"/>', "menu": '<path d="M3 7h18M3 12h18M3 17h18"/>',
 "send": '<path d="M3 11l18-8-8 18-2-8z"/>', "arr": '<path d="M5 12h14M13 6l6 6-6 6"/>', "down": '<path d="M6 9l6 6 6-6"/>',
 "l": '<path d="M15 5l-7 7 7 7"/>', "r": '<path d="M9 5l7 7-7 7"/>',
 "head": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h3v6H5a1 1 0 0 1-1-1zM20 14h-3v6h2a1 1 0 0 0 1-1z"/><path d="M17 20c0 1.2-1.8 2-4 2"/>',
}
def ic(n): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_P[n]}</svg>'
WA_IC = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.2-.2.3-.8 1-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5.3-.5c.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm8.4-18.2A11.8 11.8 0 0 0 1.7 17.8L0 24l6.4-1.7A11.8 11.8 0 0 0 24 12a11.7 11.7 0 0 0-3.6-8.4z"/></svg>'

# ---------------------------------------------------------------- фото: показываются, когда файлы есть; иначе — аккуратная заглушка того же размера
IMG = ROOT / "assets" / "img"
def _has(p): return (ROOT / p.lstrip("/")).with_name(Path(p).name + "-800.webp").exists()
def pic(p, alt, sizes, w, h, eager=False, ss=(480, 800, 1200), cls=""):
    if p and _has(p):
        pr = 'fetchpriority="high"' if eager else 'loading="lazy"'
        sset = ", ".join(f"{p}-{s}.webp {s}w" for s in ss)
        return f'<img{" class=" + chr(34) + cls + chr(34) if cls else ""} src="{p}-800.webp" srcset="{sset}" sizes="{sizes}" alt="{E(alt)}" width="{w}" height="{h}" {pr} decoding="async">'
    return f'<span class="noph{" " + cls if cls else ""}" role="img" aria-label="{E(alt)}"></span>'
def svc_img(slug): return f"/assets/img/uslugi/{slug}"
def pf_photos(slug):
    d = IMG / "portfolio" / slug
    return [f"/assets/img/portfolio/{slug}/{f.name[:-9]}" for f in sorted(d.glob("*-800.webp"))] if d.exists() else []
def boss_img(): return "/assets/img/rukovoditel"
def has_logo(): return (ROOT / "assets" / "logo.webp").exists()
def hero_pic(alt):
    """Главный фон: отдельные фото для ПК (16:9) и телефона (4:5)."""
    pc, mob = IMG / "hero" / "pc-1200.webp", IMG / "hero" / "mob-800.webp"
    if not pc.exists(): return '<span class="hero-bg noph" aria-hidden="true"></span>', ""
    src_m = f'<source media="(max-width: 767px)" srcset="/assets/img/hero/mob-480.webp 480w, /assets/img/hero/mob-800.webp 800w" sizes="100vw">' if mob.exists() else ""
    h = (f'<picture class="hero-bg">{src_m}<img src="/assets/img/hero/pc-1200.webp" srcset="/assets/img/hero/pc-800.webp 800w, /assets/img/hero/pc-1200.webp 1200w, /assets/img/hero/pc-1920.webp 1920w" '
         f'sizes="100vw" alt="{E(alt)}" width="1920" height="1080" fetchpriority="high" decoding="async"></picture>')
    pre = (f'<link rel="preload" as="image" href="/assets/img/hero/mob-800.webp" imagesrcset="/assets/img/hero/mob-480.webp 480w, /assets/img/hero/mob-800.webp 800w" imagesizes="100vw" media="(max-width: 767px)">\n' if mob.exists() else "") + \
          f'<link rel="preload" as="image" href="/assets/img/hero/pc-1200.webp" imagesrcset="/assets/img/hero/pc-800.webp 800w, /assets/img/hero/pc-1200.webp 1200w, /assets/img/hero/pc-1920.webp 1920w" imagesizes="100vw"{" media=" + chr(34) + "(min-width: 768px)" + chr(34) if mob.exists() else ""}>\n'
    return h, pre

# ---------------------------------------------------------------- общее
def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s*\n\s*", "", s)
    return re.sub(r"\s*([{};,>])\s*", r"\1", s).replace(";}", "}")
CSS = minify_css((ROOT / "src" / "styles.css").read_text(encoding="utf-8"))

def conv_js():
    if not (GADS_ID and GADS_LABEL): return ""
    return ("<script>\n  function gtag_report_conversion(url) {\n    var done = false;\n    var callback = function () { if (done) return; done = true; if (typeof(url) != 'undefined') { window.location = url; } };\n"
            f"    if (typeof gtag === 'function') {{ gtag('event', 'conversion', {{ 'send_to': '{GADS_ID}/{GADS_LABEL}', 'event_callback': callback }}); }}\n"
            "    setTimeout(callback, 800);\n    return false;\n  }\n</script>\n")
def gtag():
    if not TAG_ID: return ""
    return ("<!-- Google tag (gtag.js) -->\n"
            f'<script async src="https://www.googletagmanager.com/gtag/js?id={TAG_ID}"></script>\n'
            "<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag('js', new Date());\n\n"
            f"  gtag('config', '{TAG_ID}');\n" + (f"  gtag('config', '{TAG_GA}');\n" if TAG_GA else "") + "</script>\n")

def org():
    return {"@type": "HomeAndConstructionBusiness", "@id": SITE_URL + "/#org", "name": BRAND, "url": SITE_URL + "/", "telephone": PHONE_TEL,
            "description": "Ремонт квартир, домов и коммерческих помещений в Астане: под ключ, капитальный, косметический, дизайнерский и элитный ремонт, все виды отделочных работ.",
            "image": SITE_URL + "/assets/og.png", "logo": SITE_URL + "/assets/icon-512.png",
            "address": {"@type": "PostalAddress", "addressLocality": CITY, "addressCountry": "KZ"},
            "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
            "areaServed": [{"@type": "City", "name": CITY}] + [{"@type": "AdministrativeArea", "name": f"район {d['name']}, {CITY}"} for d in DISTRICTS],
            "employee": {"@type": "Person", "name": DIRECTOR, "jobTitle": "Руководитель компании"}, "currenciesAccepted": "KZT", "sameAs": [WA],
            "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Услуги", "itemListElement": [
                {"@type": "OfferCatalog", "name": cn, "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["h1"], "url": f"{SITE_URL}/{s['slug']}/"}} for s in SERVICES if s["cat"] == c]} for c, cn, _ in CATS]}}
def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}
def faq_ld(faq): return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

def logo():
    inner = ('<img src="/assets/logo.webp" alt="" width="200" height="48" decoding="async">' if has_logo() else '<b>VIP<i>Remont</i></b>')
    return f'<a class="logo" href="/" aria-label="{BRAND} — на главную">{inner}</a>'

NAV = [("Услуги", "/uslugi/"), ("Элитный ремонт", "/elitnyy-remont/"), ("Портфолио", "/portfolio/"), ("Цены", "/ceny/"), ("О компании", "/o-kompanii/"), ("Контакты", "/kontakty/")]
MORE = [("Районы", "/rayony/"), ("Статьи", "/stati/"), ("Вопросы", "/voprosy/")]
def header(cur):
    cols = ""
    for c, cn, _ in CATS:
        links = "".join(f'<a href="/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES if s["cat"] == c)
        cols += f'<div class="mg-c mg-{c}"><p class="mg-t">{cn}</p><div>{links}</div></div>'
    nav = ""
    for n, u in NAV:
        on = cur == u or (u == "/uslugi/" and cur.strip("/") in SV and cur != "/elitnyy-remont/")
        a = f'<a href="{u}"{" aria-current=page" if on else ""}>{n}</a>'
        nav += (f'<div class="dd">{a}<button type="button" class="dd-b" aria-expanded="false" aria-label="Открыть все услуги">{ic("down")}</button>'
                f'<div class="mg"><div class="w mg-in">{cols}</div></div></div>') if u == "/uslugi/" else a
    acc = "".join(f'<details><summary>{cn}</summary><div>' + "".join(f'<a href="/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES if s["cat"] == c) + "</div></details>" for c, cn, _ in CATS)
    dnav = '<a href="/">Главная</a>' + "".join(f'<a href="{u}">{n}</a>' + (f'<div class="d-acc">{acc}</div>' if u == "/uslugi/" else "") for n, u in NAV + MORE)
    return f'''<a class="skip" href="#main">К содержимому</a>
<header class="hd"><div class="w hd-in">
{logo()}
<nav class="nav" aria-label="Главное меню">{nav}</nav>
<div class="hd-r"><a class="hd-tel" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
<a class="hd-ic" href="tel:{PHONE_TEL}" aria-label="Позвонить {PHONE_DISPLAY}">{ic("phone")}</a>
<button class="burger" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="drawer">{ic("menu")}</button></div>
</div></header>
<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Меню" hidden><div class="d-p">
<div class="d-x">{logo()}<button type="button" data-close aria-label="Закрыть меню">{ic("x")}</button></div>
<nav aria-label="Меню">{dnav}</nav>
<div class="d-bt"><a class="btn" href="tel:{PHONE_TEL}">{ic("phone")}Позвонить</a><a class="btn line" href="{wa(HELLO)}" target="_blank" rel="noopener">{WA_IC}WhatsApp</a></div>
</div></div>'''

def footer():
    col = lambda c: "".join(f'<a href="/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES if s["cat"] == c)
    nav = "".join(f'<a href="{u}">{n}</a>' for n, u in NAV[2:] + MORE)
    return f'''<footer class="ft"><div class="w">
<div class="ft-top"><div class="ft-a">{logo()}<p>Ремонт квартир, домов и коммерческих помещений в Астане — от косметического до элитного. Своя бригада, цена в договоре.</p>
<a class="ft-tel" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><a href="{wa(HELLO)}" target="_blank" rel="noopener">Написать в WhatsApp</a></div>
<div><p class="ft-h">{CATN["vid"]}</p>{col("vid")}</div>
<div><p class="ft-h">{CATN["obj"]}</p>{col("obj")}<p class="ft-h ft-h2">{CATN["stil"]}</p>{col("stil")}</div>
<div><p class="ft-h">{CATN["pom"]}</p>{col("pom")}<p class="ft-h ft-h2">Компания</p>{nav}<a href="{POLICY}">Политика конфиденциальности</a></div></div>
<div class="ft-rab"><p class="ft-h">{CATN["rab"]}</p><div>{col("rab")}</div></div>
<div class="bt"><span>© {BRAND}, {CITY}</span><a href="https://www.anuken.kz" target="_blank" rel="noopener">Разработка и продвижение Anuken.kz</a></div>
</div></footer>'''

CHAT_Q = ["Сколько стоит ремонт?", "Делаете элитный ремонт?", "Как быстро будет смета?", "Кто закупает материалы?"]
def flo():
    q = "".join(f"<button type=button>{x}</button>" for x in CHAT_Q)
    return f'''<div class="flo">
<a class="sm" href="/" data-back aria-label="Назад" title="Назад">{ic("back")}</a>
<button class="sm" type="button" data-top hidden aria-label="Наверх" title="Наверх">{ic("up")}</button>
<button class="flo-c" type="button" data-chat aria-label="Онлайн-консультант">{ic("head")}<span>Консультант</span></button>
</div>
<template id="chat-t"><section class="chat" id="chat" aria-label="Онлайн-консультант">
<div class="chat-h"><span class="av">{ic("head")}</span><span><b>Консультант {BRAND}</b><small>ИИ-помощник · ответит по ремонту</small></span><button type="button" data-chat-x aria-label="Закрыть чат">{ic("x")}</button></div>
<div class="chat-l" aria-live="polite"></div>
<div class="chat-q">{q}</div>
<form class="chat-f"><label class="sr" for="cq">Ваш вопрос</label><input id="cq" name="q" autocomplete="off" placeholder="Ваш вопрос" maxlength="500"><button type="submit" aria-label="Отправить">{ic("send")}</button></form>
<a class="chat-w" href="{wa(HELLO)}" target="_blank" rel="noopener">{WA_IC}Написать мастеру в WhatsApp</a>
</section></template>
<template id="lb-t"><div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Фото объекта"><button type="button" class="lb-x" data-lb-x aria-label="Закрыть">{ic("x")}</button>
<button type="button" class="lb-n lb-p" data-lb-p aria-label="Предыдущее фото">{ic("l")}</button><figure><img alt=""><figcaption></figcaption></figure><button type="button" class="lb-n lb-nx" data-lb-n aria-label="Следующее фото">{ic("r")}</button></div></template>'''

SITEMAP = []; LONG = []
_SHORT = r"(?<![\w ])(в|во|и|с|со|к|ко|о|об|у|а|на|по|за|от|до|из|не|без|для|при|под|над|или|но|что|как)\s(?=\S)"
def _t(m):
    t = m.group(0)
    t = re.sub(r"(?<=\d) (?=\d{3}\b)", " ", t).replace(" м²", " м²")
    t = re.sub(_SHORT, lambda x: x.group(1) + " ", t, flags=re.I)
    return t.replace(" —", " —")
def typo(h):
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", h, flags=re.S)
    return "".join(p if p.startswith(("<script", "<style")) else re.sub(r"(?<=>)[^<]+", _t, p) for p in parts)

def page(path, title, desc, body, cur="", ld=None, noindex=False, og_type="website", preload=""):
    if len(title) > 60 or len(desc) > 160: LONG.append((path, len(title), len(desc)))
    url = SITE_URL + (path if path != "/404.html" else "/")
    cfg = json.dumps({"wa": WA_NUMBER, "tel": PHONE_TEL, "phone": PHONE_DISPLAY, "hello": HELLO}, ensure_ascii=False)
    graph = [org(), {"@type": "WebSite", "@id": SITE_URL + "/#site", "url": SITE_URL + "/", "name": BRAND, "inLanguage": "ru"}] + (ld or [])
    doc = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
{gtag()}<script>document.documentElement.className+=" js"</script>
{conv_js()}<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{f'<meta name="google-site-verification" content="{GSC_META}" />' + chr(10) if GSC_META else ""}<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{"" if path == "/404.html" else f'<link rel="canonical" href="{url}">'}
{'<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="{og_type}"><meta property="og:locale" content="ru_KZ"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}/assets/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{SITE_URL}/assets/og.png">
<meta name="geo.region" content="KZ-AST"><meta name="geo.placename" content="{CITY}"><meta name="geo.position" content="{GEO[0]};{GEO[1]}"><meta name="ICBM" content="{GEO[0]}, {GEO[1]}">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/manrope-cyrillic-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
{preload}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>
</head>
<body>
{header(cur or path)}
<main id="main">
{body}
</main>
{footer()}
{flo()}
<script>window.__C={cfg}</script>
<script src="/assets/app.js?v={VER}" defer></script>
</body>
</html>
'''
    head, sep, rest = doc.partition("<body>")
    doc = head + sep + typo(rest)
    if GADS_ID and GADS_LABEL:
        doc = re.sub(r'<a ([^>]*?)href="tel:([^"]+)"', lambda m: f'<a {m.group(1)}href="tel:{m.group(2)}" onclick="return gtag_report_conversion(&#39;tel:{m.group(2)}&#39;)"', doc)
        doc = re.sub(r'<a ([^>]*?)href="(https://wa\.me/[^"]+)"', lambda m: f'<a {m.group(1)}href="{m.group(2)}" onclick="gtag_report_conversion()"', doc)
    out = DIST / path.strip("/") / "index.html" if path != "/404.html" else DIST / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    if path != "/404.html" and not noindex: SITEMAP.append(path)

# ---------------------------------------------------------------- блоки
def crumbs(items, light=False):
    out = []
    for i, (n, u) in enumerate(items):
        out.append(f'<span aria-current="page">{E(n)}</span>' if i == len(items) - 1 else f'<a href="{u}">{E(n)}</a><span aria-hidden="true">/</span>')
    return f'<nav class="crumbs{" lt" if light else ""}" aria-label="Хлебные крошки">{"".join(out)}</nav>'

def sh(title, sub="", tag="h2", link=None):
    l = f'<a class="more" href="{link[1]}">{link[0]}{ic("arr")}</a>' if link else ""
    return f'<div class="sh"><div><{tag}>{title}</{tag}>{f"<p>{sub}</p>" if sub else ""}</div>{l}</div>'

def quiz(vid="", ray="", ctx=""):
    fs = ""
    for i, (key, q, opts) in enumerate(QUIZ):
        pre = vid if key == "vid" else ray if key == "ray" else ""
        o = "".join(f'<label><input type="radio" name="{key}" value="{E(x)}"{" checked" if x == pre else ""}><span>{E(x)}</span></label>' for x in opts)
        fs += f'<fieldset class="qs{" on" if i == 0 else ""}"><legend>{q}</legend><div class="opts">{o}</div></fieldset>'
    return f'''<form class="qz" id="qz" novalidate data-ctx="{E(ctx)}">
<div class="qz-bar" aria-hidden="true"><i></i></div>
{fs}<fieldset class="qs qs-f"><legend>Куда прислать ответ?</legend>
<label>Имя<input name="name" autocomplete="given-name" placeholder="Как к вам обращаться"></label>
<label>Телефон<input name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 7__ ___ __ __" required></label>
<label class="full">Что нужно сделать<textarea name="desc" rows="2" placeholder="Коротко о задаче — по желанию"></textarea></label>
<button class="btn full" type="submit">{WA_IC}Отправить в WhatsApp</button>
<small class="full">Нажимая кнопку, вы соглашаетесь с <a href="{POLICY}">политикой конфиденциальности</a>.</small></fieldset>
<div class="qz-nav"><button type="button" class="lnk" data-prev disabled>{ic("back")}Назад</button><button type="button" class="btn sm2" data-next>Дальше{ic("arr")}</button></div>
</form>'''

def calc(vid="", ray="", ctx="", title="Рассчитаем стоимость ремонта"):
    """Секция расчёта — одна на странице, на неё ведут кнопки первого экрана."""
    return f'''<section class="calc" id="raschet"><div class="w calc-in">
<div class="calc-t"><h2>{title}</h2><p>Ответьте на четыре вопроса — мастер свяжется, договорится о замере и подготовит смету за три часа после него.</p>
<ul class="ticks"><li>Цена фиксируется в договоре</li><li>Своя бригада без субподрядчиков</li><li>Гарантия на все работы</li></ul></div>
<div>{quiz(vid, ray, ctx)}</div></div></section>'''

def facts_row(n=4): return '<ul class="frow">' + "".join(f"<li><b>{h}</b><span>{p}</span></li>" for h, p in FACTS[:n]) + "</ul>"
def facts_grid(): return '<dl class="fg">' + "".join(f"<div><dt>{E(h)}</dt><dd>{E(p)}</dd></div>" for h, p in FACTS) + "</dl>"
def steps_html(): return '<ol class="steps">' + "".join(f"<li><h3>{E(h)}</h3><p>{E(p)}</p></li>" for h, p in STEPS) + "</ol>"
def factors_html(): return '<dl class="fg fg2">' + "".join(f"<div><dt>{E(h)}</dt><dd>{E(p)}</dd></div>" for h, p in PRICE_FACTORS) + "</dl>"
def faq_html(faq): return '<div class="faq">' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq) + "</div>"

def card(s, sizes="(max-width: 599px) 86vw, (max-width: 1023px) 45vw, 30vw", big=False):
    return (f'<a class="pc{" big" if big else ""}" href="/{s["slug"]}/">{pic(svc_img(s["slug"]), s["h1"], sizes, 1200, 900)}'
            f'<span class="pc-t"><b>{s["name"]}</b><span>{s["short"]}</span></span></a>')
def cards(slugs, cls="pcs", bento=False):
    return f'<div class="{cls}">' + "".join(card(SV[x], big=bento and i == 0) for i, x in enumerate(slugs)) + "</div>"

def catalog(filters=True):
    """Все услуги по категориям; на ПК — вкладки-фильтры."""
    tabs = '<div class="tabs" role="tablist" aria-label="Категории услуг"><button type="button" role="tab" aria-selected="true" data-f="all">Все</button>' + \
           "".join(f'<button type="button" role="tab" aria-selected="false" data-f="{c}">{cn}</button>' for c, cn, _ in CATS) + "</div>" if filters else ""
    g = lambda c: f'<div class="cg" data-c="{c}"><h3>{CATN[c]}</h3><ul>' + "".join(f'<li><a href="/{s["slug"]}/"><b>{s["name"]}</b><span>{s["short"]}</span></a></li>' for s in SERVICES if s["cat"] == c) + "</ul></div>"
    groups = f'<div class="cgc">{g("vid")}</div><div class="cgc">{g("obj")}{g("stil")}</div><div class="cgc">{g("pom")}</div><div class="cgc cgw">{g("rab")}</div>'
    return f'<div class="cat" data-cat>{tabs}<div class="cgs">{groups}</div></div>'

def pf_card(p, sizes="(max-width: 599px) 100vw, (max-width: 1023px) 50vw, 25vw"):
    ph = pf_photos(p["slug"]); s = SV.get(p["svc"])
    data = json.dumps([f"{x}-1200.webp" for x in ph]) if ph else "[]"
    img = pic(ph[0] if ph else "", p["title"] + " — ремонт в Астане, VIP Remont", sizes, 1200, 900)
    return (f'<figure class="pf"><button type="button" class="pf-o" data-lb=\'{E(data)}\' data-t="{E(p["title"])}" aria-label="Открыть фото: {E(p["title"])}"{"" if ph else " disabled"}>{img}</button>'
            f'<figcaption><b>{E(p["title"])}</b>{svc_link(s)}</figcaption></figure>')
def svc_link(s): return f'<a href="/{s["slug"]}/">{s["h1"]}</a>' if s else ""

def pf_grid(items): return '<div class="pfs">' + "".join(pf_card(p) for p in items) + "</div>"

def boss():
    return f'''<section class="s"><div class="w bs"><div class="bs-i">{pic(boss_img(), DIRECTOR + " — руководитель " + BRAND, "(max-width: 767px) 90vw, 40vw", 800, 1000, ss=(480, 800))}</div>
<div class="bs-t"><p class="ey">Руководитель компании</p><h2>{DIRECTOR}</h2>
<p class="lead">Отвечает за смету, договор и сроки на каждом объекте. По вопросам ремонта можно написать или позвонить напрямую.</p>
<div class="act"><a class="btn" href="{wa("Здравствуйте, Серик! Хочу обсудить ремонт.")}" target="_blank" rel="noopener">{WA_IC}Написать в WhatsApp</a><a class="lnk" href="/o-kompanii/">О компании{ic("arr")}</a></div></div></div></section>'''

def districts_html(cur=""):
    return '<ul class="dl">' + "".join(f'<li><a href="/rayony/{d["slug"]}/"><b>{d["name"]}</b><span>{d["note"]}</span></a></li>' for d in DISTRICTS if d["slug"] != cur) + "</ul>"
def articles_html(skip=""):
    return '<div class="arts">' + "".join(f'<a class="ar" href="/stati/{a["slug"]}/"><b>{E(a["title"])}</b><span>{E(a["lead"])}</span><i>Читать{ic("arr")}</i></a>' for a in ARTICLES if a["slug"] != skip) + "</div>"

def phero(cr, h1, lead, img="", alt="", btn2=None, extra=""):
    """Первый экран внутренних страниц: фото услуги на фоне (или фирменный градиент)."""
    bg = pic(img, alt or h1, "100vw", 1200, 900, eager=True, cls="ph-bg") if img else '<span class="ph-bg noph" aria-hidden="true"></span>'
    b2 = f'<a class="btn wl" href="{btn2[1]}">{btn2[0]}</a>' if btn2 else ""
    return f'''<section class="phero">{bg}<div class="w phero-in">{crumbs(cr, True)}
<h1>{h1}</h1><p class="lead">{lead}</p><div class="act"><a class="btn" href="#raschet">Рассчитать стоимость</a>{b2}</div>{extra}</div></section>'''

# ---------------------------------------------------------------- страницы
def build_home():
    bg, pre = hero_pic("Ремонт квартиры в Астане — интерьер после ремонта VIP Remont")
    elite = SV["elitnyy-remont"]
    stl = "".join(f'<li><a href="/{s["slug"]}/">{s["name"]}{ic("arr")}</a></li>' for s in SERVICES if s["cat"] == "stil")
    body = f"""<section class="hero">{bg}<div class="w hero-in">
<h1>Ремонт квартир в&nbsp;Астане — от&nbsp;косметического до&nbsp;элитного</h1>
<p class="lead">VIP Remont делает ремонт квартир, домов и коммерческих помещений в Астане: под ключ, дизайнерский и элитный, санузлы, кухни и все виды отделочных работ. Своя бригада, смета за три часа после замера, цена фиксируется в договоре.</p>
<div class="act"><a class="btn" href="#raschet">Рассчитать стоимость</a><a class="btn wl" href="/portfolio/">Смотреть работы</a></div>
</div><div class="w hero-f">{facts_row()}</div></section>
<section class="s"><div class="w">{sh("Виды ремонта", "Подберём формат под задачу и бюджет — от обновления отделки до ремонта премиум-класса.", link=("Все услуги", "/uslugi/"))}{cards(HOME_VID, "bento row", True)}</div></section>
<section class="s elite"><div class="w el-in"><div class="el-i">{pic(svc_img("elitnyy-remont"), elite["h1"], "(max-width: 1023px) 100vw, 50vw", 1200, 900)}</div>
<div class="el-t"><p class="ey">Премиум-класс</p><h2>Элитный ремонт</h2><p class="lead">{elite["lead"]}</p>
<ul class="ticks">{"".join(f"<li>{x}</li>" for x in elite["inc"][:6])}</ul>
<div class="act"><a class="btn" href="/elitnyy-remont/">Подробнее об элитном ремонте</a></div>
<p class="el-s">Ремонт в стиле</p><ul class="stl">{stl}</ul></div></div></section>
<section class="s"><div class="w">{sh("Ремонт помещений", "Если нужен ремонт одной комнаты, кухни или санузла.")}{cards(HOME_POM, "pcs six row")}</div></section>
<section class="s soft"><div class="w">{sh("Наши работы", "Объекты в Астане: квартиры, дома и коммерция.", link=("Все работы", "/portfolio/"))}{pf_grid(PORTFOLIO[:8])}</div></section>
<section class="s"><div class="w">{sh("Почему с нами спокойно", "Всё, что обещаем, записываем в договор.")}{facts_grid()}</div></section>
<section class="s soft"><div class="w">{sh("Как проходит ремонт", "От заявки до сдачи квартиры под заезд.")}{steps_html()}</div></section>
<section class="s"><div class="w">{sh("Все услуги", "Виды ремонта, объекты, помещения, стили и отдельные работы.")}{catalog()}</div></section>
{calc(ctx="Главная")}
{boss()}
<section class="s soft"><div class="w two"><div>{sh("Частые вопросы", link=("Все вопросы", "/voprosy/"))}{faq_html(COMMON_FAQ[:6])}</div>
<div>{sh("Работаем по всей Астане", link=("Районы", "/rayony/"))}{districts_html()}</div></div></section>
<section class="s"><div class="w">{sh("Статьи о ремонте", link=("Все статьи", "/stati/"))}{articles_html()}</div></section>"""
    page("/", "Ремонт квартир в Астане под ключ — VIP Remont",
         "Ремонт квартир в Астане: под ключ, капитальный, дизайнерский и элитный. Своя бригада, смета за 3 часа после замера, цена фиксируется в договоре.",
         body, "/", [faq_ld(COMMON_FAQ[:6])], preload=pre)

def build_services_index():
    cr = [("Главная", "/"), ("Услуги", "/uslugi/")]
    secs = ""
    for i, (c, cn, sub) in enumerate(CATS):
        sl = [s["slug"] for s in SERVICES if s["cat"] == c]
        secs += f'<section class="s{" soft" if i % 2 else ""}" id="{c}"><div class="w">{sh(cn, sub)}{cards(sl, "pcs")}</div></section>'
    body = f"""{phero(cr, "Услуги по ремонту в Астане", "Все виды ремонта квартир, домов и коммерческих помещений в Астане — от косметического до элитного, а также отдельные отделочные работы. Своя бригада, цена в договоре.", svc_img("remont-pod-klyuch"))}
{secs}{calc(ctx="Услуги")}"""
    items = {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/{s['slug']}/", "name": s["h1"]} for i, s in enumerate(SERVICES)]}
    page("/uslugi/", "Услуги по ремонту квартир в Астане | VIP Remont",
         "Все виды ремонта в Астане: под ключ, капитальный, косметический, дизайнерский, элитный, санузлы, кухни, стили интерьера и отдельные работы.", body, "/uslugi/", [crumbs_ld(cr), items])

def build_services():
    for s in SERVICES:
        path = f"/{s['slug']}/"
        cr = [("Главная", "/"), ("Услуги", "/uslugi/"), (s["name"], path)]
        inc = "".join(f"<li>{x}</li>" for x in s["inc"])
        prep = "".join(f"<li>{x}</li>" for x in s["prep"])
        faq = s["faq"] + [q for q in COMMON_FAQ if q[0] in ("Как быстро будет смета?", "Даёте гарантию?", "Кто закупает материалы?")][: max(0, 5 - len(s["faq"]))]
        pf = [p for p in PORTFOLIO if p["svc"] == s["slug"]]
        pf += [p for p in PORTFOLIO if p not in pf and SV[p["svc"]]["cat"] == s["cat"]][: max(0, 4 - len(pf))]
        pf += [p for p in PORTFOLIO if p not in pf][: max(0, 4 - len(pf))]
        same = [x["slug"] for x in SERVICES if x["cat"] == s["cat"] and x["slug"] != s["slug"]][:4]
        if len(same) < 4: same += [x for x in HOME_VID if x != s["slug"] and x not in same][: 4 - len(same)]
        msg = f"Здравствуйте! Интересует: {s['name'].lower()}."
        pf_sec = f'<section class="s pt0"><div class="w">{sh("Наши работы", link=("Всё портфолио", "/portfolio/"))}{pf_grid(pf[:4])}</div></section>'
        body = f"""{phero(cr, s["h1"], s["lead"], svc_img(s["slug"]), btn2=("Смотреть работы", "/portfolio/"))}
<section class="s sm-t"><div class="w">{facts_row()}</div></section>
<section class="s"><div class="w split"><div>{sh("Что входит", "Точный перечень работ для вашего объекта фиксируем в смете.")}</div><ul class="ticks cols">{inc}</ul></div></section>
{pf_sec}
<section class="s soft"><div class="w">{sh("Как проходит работа", "Смета за три часа после замера, приёмка каждого этапа.")}{steps_html()}</div></section>
<section class="s"><div class="w two"><div>{sh("Как подготовиться", "Это ускорит замер и смету.")}<ul class="ticks">{prep}</ul>
<p class="ask">Остались вопросы? <a href="{wa(msg)}" target="_blank" rel="noopener">Напишите мастеру в WhatsApp</a></p></div>
<div>{sh("Вопросы")}{faq_html(faq)}</div></div></section>
{calc(QUIZ_VID.get(s["slug"], "Отдельные работы" if s["cat"] == "rab" else ""), ctx=s["name"])}
<section class="s"><div class="w">{sh("Смотрите также", link=("Все услуги", "/uslugi/"))}{cards(same, "pcs four row")}</div></section>"""
        t = s["title"] or (f"{s['h1']} | {BRAND}" if len(s["h1"]) + len(BRAND) + 3 <= 60 else s["h1"])
        d = f"{s['short']}. {s['h1']}: смета за 3 часа после замера, цена фиксируется в договоре, своя бригада."
        if len(d) > 160: d = f"{s['h1']}: {s['short'].lower()}. Смета за 3 часа после замера, цена в договоре."
        if len(d) > 160: d = f"{s['h1']}. Смета за 3 часа после замера, цена в договоре, своя бригада."
        srv = {"@type": "Service", "name": s["h1"], "serviceType": s["name"], "description": s["lead"], "provider": {"@id": SITE_URL + "/#org"},
               "areaServed": {"@type": "City", "name": CITY}, "url": SITE_URL + path, "image": SITE_URL + "/assets/og.png"}
        page(path, t, d, body, path, [crumbs_ld(cr), srv, faq_ld(faq)])

def build_portfolio():
    cr = [("Главная", "/"), ("Портфолио", "/portfolio/")]
    body = f"""{phero(cr, "Портфолио: наши работы в Астане", "Фото объектов VIP Remont в Астане: квартиры под ключ, элитный и дизайнерский ремонт, санузлы, кухни, дома и коммерческие помещения. Нажмите на фото, чтобы посмотреть объект целиком.", pf_photos(PORTFOLIO[0]["slug"])[0] if pf_photos(PORTFOLIO[0]["slug"]) else "")}
<section class="s"><div class="w">{pf_grid(PORTFOLIO)}</div></section>
{calc(ctx="Портфолио", title="Хотите так же? Рассчитаем стоимость")}"""
    page("/portfolio/", "Портфолио — фото ремонта квартир в Астане | VIP Remont",
         "Фото наших работ в Астане: ремонт квартир под ключ, элитный и дизайнерский ремонт, санузлы, кухни, дома и офисы.", body, "/portfolio/", [crumbs_ld(cr)])

def build_prices():
    cr = [("Главная", "/"), ("Цены", "/ceny/")]
    faq = [COMMON_FAQ[0], COMMON_FAQ[1], ("Может ли цена вырасти во время ремонта?", "Нет. Стоимость и объём работ фиксируются в договоре и меняются только с вашего согласия."), COMMON_FAQ[4]]
    body = f"""{phero(cr, "Цены на ремонт квартир в Астане", "Стоимость ремонта в Астане зависит от площади, вида ремонта, состояния объекта и материалов. Точную смету готовим за три часа после замера, и цена фиксируется в договоре.", svc_img("kapitalnyy-remont"))}
<section class="s"><div class="w split"><div>{sh("От чего зависит цена", "Поэтому мы не публикуем цену «за метр», которая потом вырастет.")}</div>{factors_html()}</div></section>
<section class="s soft"><div class="w">{sh("Как получить точную смету")}{steps_html()}</div></section>
<section class="s"><div class="w split"><div>{sh("Вопросы о цене")}</div>{faq_html(faq)}</div></section>
{calc(ctx="Цены")}"""
    page("/ceny/", "Цены на ремонт квартир в Астане | VIP Remont",
         "От чего зависит стоимость ремонта квартиры в Астане и как получить точную смету: замер, смета за 3 часа, цена фиксируется в договоре.", body, "/ceny/", [crumbs_ld(cr), faq_ld(faq)])

def build_districts():
    cr = [("Главная", "/"), ("Районы", "/rayony/")]
    body = f"""{phero(cr, "Ремонт квартир по районам Астаны", "VIP Remont делает ремонт во всех районах Астаны: Есиль, Алматы, Сарыарка, Байконыр и Нура. Выезжаем на замер, смету готовим за три часа.", svc_img("remont-v-novostroyke"))}
<section class="s"><div class="w">{districts_html()}</div></section>
<section class="s soft"><div class="w">{sh("Что делаем в любом районе", link=("Все услуги", "/uslugi/"))}{cards(HOME_VID[:6], "pcs six row")}</div></section>{calc(ctx="Районы")}"""
    page("/rayony/", "Ремонт квартир по районам Астаны | VIP Remont",
         "Ремонт квартир в районах Есиль, Алматы, Сарыарка, Байконыр и Нура. Замер, смета за 3 часа, цена в договоре. Своя бригада.", body, "/rayony/", [crumbs_ld(cr)])
    for d in DISTRICTS:
        path = f"/rayony/{d['slug']}/"; crd = cr + [(d["name"], path)]
        lead = f"Ремонт квартир в {d['gen']} Астаны: под ключ, капитальный, дизайнерский и элитный, санузлы и кухни. {d['note']}"
        body = f"""{phero(crd, f"Ремонт квартир в {d['gen']}", lead, svc_img("remont-pod-klyuch"))}
<section class="s"><div class="w">{sh(f"Ремонт в {d['gen']}", "Выезжаем на замер, смету готовим в течение трёх часов.")}{cards(HOME_VID[:6], "pcs six row")}</div></section>
<section class="s soft"><div class="w">{sh("Почему с нами спокойно")}{facts_grid()}</div></section>
{calc(ray=d["name"], ctx="Район " + d["name"])}
<section class="s"><div class="w">{sh("Другие районы")}{districts_html(d["slug"])}</div></section>"""
        sl = {"@type": "Service", "name": f"Ремонт квартир в {d['gen']} Астаны", "provider": {"@id": SITE_URL + "/#org"},
              "areaServed": {"@type": "AdministrativeArea", "name": f"район {d['name']}, {CITY}"}, "url": SITE_URL + path}
        t = f"Ремонт квартир в {d['gen']} Астаны | VIP Remont"
        if len(t) > 60: t = f"Ремонт квартир в {d['gen']} Астаны"
        page(path, t, f"Ремонт квартир в {d['gen']} Астаны: под ключ, дизайнерский, элитный, санузлы, кухни. Смета за 3 часа после замера.", body, path, [crumbs_ld(crd), sl])

def build_faq():
    cr = [("Главная", "/"), ("Вопросы", "/voprosy/")]
    seen, faq = set(), []
    for q, a in COMMON_FAQ + [x for s in SERVICES for x in s["faq"]]:
        if q not in seen: seen.add(q); faq.append((q, a))
    body = f"""{phero(cr, "Вопросы о ремонте квартир", "Ответы на частые вопросы о ремонте в Астане: смета, цена в договоре, сроки, материалы, гарантия, элитный ремонт и контроль работ.", svc_img("chistovoy-remont"))}
<section class="s"><div class="w narrow">{faq_html(faq)}</div></section>{calc(ctx="Вопросы")}"""
    page("/voprosy/", "Вопросы о ремонте квартир в Астане | VIP Remont",
         "Ответы на вопросы о ремонте в Астане: смета, цена в договоре, материалы, гарантия, элитный ремонт, приёмка этапов, районы работы.", body, "/voprosy/", [crumbs_ld(cr), faq_ld(faq)])

MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
def build_articles():
    cr = [("Главная", "/"), ("Статьи", "/stati/")]
    body = f"""{phero(cr, "Статьи о ремонте квартир", "Полезное о ремонте в Астане: цена и смета, элитный ремонт, черновой и чистовой этапы, новостройки, стили интерьера и приёмка работ.", svc_img("dizayn-interera"))}
<section class="s"><div class="w">{articles_html()}</div></section>"""
    page("/stati/", "Статьи о ремонте квартир в Астане | VIP Remont", "Статьи о ремонте: цена и смета, элитный ремонт, черновой и чистовой ремонт, новостройки, стили интерьера, приёмка работ.", body, "/stati/", [crumbs_ld(cr)])
    y, m, dd = ARTICLE_DATE.split("-"); human = f"{int(dd)} {MONTHS[int(m) - 1]} {y}"
    for a in ARTICLES:
        path = f"/stati/{a['slug']}/"; cra = cr + [(a["title"], path)]
        secs = "".join(f"<h2>{E(h)}</h2><ul class='ticks'>" + "".join(f"<li>{E(x)}</li>" for x in li) + "</ul>" for h, li in a["body"])
        links = " · ".join(f'<a href="{u}">{n}</a>' for n, u in a["links"])
        body = f"""<section class="s art-s"><div class="w">{crumbs(cra)}<article class="art"><h1>{E(a["h1"])}</h1><p class="dt"><time datetime="{ARTICLE_DATE}">{human}</time> · {BRAND}</p>
<p class="lead">{E(a["lead"])}</p>{secs}<p class="rel">Смотрите также: {links}</p></article></div></section>
{calc(ctx="Статья")}
<section class="s"><div class="w">{sh("Другие статьи")}{articles_html(a["slug"])}</div></section>"""
        art = {"@type": "Article", "headline": a["h1"], "description": a["desc"], "datePublished": ARTICLE_DATE, "dateModified": ARTICLE_DATE, "inLanguage": "ru",
               "author": {"@id": SITE_URL + "/#org"}, "publisher": {"@id": SITE_URL + "/#org"}, "mainEntityOfPage": SITE_URL + path, "image": SITE_URL + "/assets/og.png"}
        t = a["title"] if len(a["title"]) + len(BRAND) + 3 > 60 else f"{a['title']} | {BRAND}"
        page(path, t, a["desc"], body, "/stati/", [crumbs_ld(cra), art], og_type="article")

def build_about():
    cr = [("Главная", "/"), ("О компании", "/o-kompanii/")]
    body = f"""{phero(cr, "О компании VIP Remont", f"VIP Remont — ремонт квартир, домов и коммерческих помещений в Астане. Работаем своей бригадой, фиксируем цену в договоре и сдаём объект под заезд. Руководитель компании — {DIRECTOR}.", svc_img("elitnyy-remont"))}
{boss()}
<section class="s soft"><div class="w">{sh("Как мы работаем")}{facts_grid()}</div></section>
<section class="s"><div class="w">{sh("Этапы ремонта")}{steps_html()}</div></section>
{calc(ctx="О компании")}"""
    page("/o-kompanii/", "О компании VIP Remont — ремонт квартир в Астане", f"VIP Remont: своя бригада, смета за 3 часа после замера, цена в договоре, гарантия. Руководитель — {DIRECTOR}.", body, "/o-kompanii/", [crumbs_ld(cr)])

def build_contacts():
    cr = [("Главная", "/"), ("Контакты", "/kontakty/")]
    ct = f'''<dl class="ct"><div><dt>Телефон и WhatsApp</dt><dd><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></dd></div><div><dt>WhatsApp</dt><dd><a href="{wa(HELLO)}" target="_blank" rel="noopener">Написать сообщение</a></dd></div>
<div><dt>Руководитель</dt><dd>{DIRECTOR}</dd></div><div><dt>Где работаем</dt><dd>Вся Астана: Есиль, Алматы, Сарыарка, Байконыр, Нура</dd></div></dl>'''
    body = f"""{phero(cr, "Контакты", f"{BRAND} — ремонт квартир в Астане. Звоните или пишите в WhatsApp: ответим на вопросы и договоримся о замере в любом районе города.", svc_img("remont-kuhni"))}
<section class="s"><div class="w">{ct}</div></section>{calc(ctx="Контакты")}"""
    page("/kontakty/", "Контакты — ремонт квартир в Астане | VIP Remont",
         f"Ремонт квартир в Астане: {PHONE_DISPLAY}, WhatsApp. Выезжаем на замер во все районы города, смета за 3 часа.", body, "/kontakty/", [crumbs_ld(cr)])

def build_privacy():
    body = f"""<section class="s art-s"><div class="w">{crumbs([("Главная", "/"), ("Политика конфиденциальности", POLICY)])}<div class="art"><h1>Политика конфиденциальности</h1>
<h2>Какие данные мы получаем</h2><p>Имя, номер телефона и ответы о ремонте, которые вы указываете в форме или пишете в WhatsApp, а также вопросы в онлайн-чате.</p>
<h2>Зачем</h2><p>Чтобы ответить на заявку, договориться о замере и подготовить смету. Мы не продаём и не передаём ваши данные третьим лицам, кроме случаев, предусмотренных законодательством Республики Казахстан.</p>
<h2>Как отправляются данные</h2><p>Форма не хранит данные на сайте: заявка открывается в WhatsApp, и вы сами отправляете сообщение. Вопросы в чате обрабатываются только для ответа.</p>
<h2>Аналитика</h2><p>Сайт может использовать Google Analytics и Google Ads для подсчёта посещений и обращений. Эти сервисы используют файлы cookie; их можно отключить в настройках браузера.</p>
<h2>Связь</h2><p>Вопросы о данных — по телефону <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> или в WhatsApp.</p></div></div></section>"""
    page(POLICY, "Политика конфиденциальности | VIP Remont", "Как VIP Remont обрабатывает данные из формы расчёта и онлайн-чата.", body)

def build_404():
    body = f"""<section class="s p404"><div class="w"><p class="ey">Ошибка 404</p><h1>Такой страницы нет</h1><p class="lead">Возможно, адрес изменился. Перейдите на главную или напишите нам — подскажем.</p>
<div class="act"><a class="btn" href="/">На главную</a><a class="btn line" href="{wa(HELLO)}" target="_blank" rel="noopener">{WA_IC}WhatsApp</a></div></div></section>"""
    page("/404.html", f"Страница не найдена | {BRAND}", "Страница не найдена.", body, noindex=True)

AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai", "PerplexityBot", "Perplexity-User",
           "Google-Extended", "Googlebot", "Applebot", "Applebot-Extended", "Bingbot", "DuckAssistBot", "YouBot", "CCBot", "Meta-ExternalAgent", "MistralAI-User"]
def build_meta():
    bots = "".join(f"User-agent: {b}\nAllow: /\nDisallow: /api/\n\n" for b in AI_BOTS)
    (DIST / "robots.txt").write_text(f"{bots}User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    def pri(p): return "1.0" if p == "/" else "0.9" if p.strip("/") in SV else "0.7" if p in ("/uslugi/", "/ceny/", "/portfolio/") or p.startswith("/rayony/") else "0.6"
    sm = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{ARTICLE_DATE}</lastmod><priority>{pri(p)}</priority></url>" for p in SITEMAP)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (DIST / "site.webmanifest").write_text(json.dumps({"name": f"{BRAND} — ремонт квартир в Астане", "short_name": BRAND, "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#2450ff",
        "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False), encoding="utf-8")
    svc = "\n\n".join(f"### {cn}\n" + "\n".join(f"- {s['h1']} ({s['short'].lower()}): {SITE_URL}/{s['slug']}/" for s in SERVICES if s["cat"] == c) for c, cn, _ in CATS)
    llms = f"""# {BRAND} — ремонт квартир в Астане

> Ремонт квартир, домов и коммерческих помещений в Астане (Казахстан): под ключ, капитальный, косметический, евроремонт, черновой, предчистовой и чистовой, дизайнерский и элитный ремонт, ремонт санузлов и кухонь, стили интерьера и все виды отделочных работ. Своя бригада без субподрядчиков, смета за три часа после замера, цена фиксируется в договоре, гарантия на все работы.

## Контакты
- Телефон и WhatsApp: {PHONE_DISPLAY}
- Руководитель: {DIRECTOR}
- География: вся Астана — Есиль, Алматы, Сарыарка, Байконыр, Нура
- Портфолио: {SITE_URL}/portfolio/

## Как мы работаем
""" + "\n".join(f"- {h}: {p}" for h, p in FACTS) + "\n\n## Этапы\n" + "\n".join(f"- {h}: {p}" for h, p in STEPS) + f"\n\n## Услуги\n\n{svc}\n\n## От чего зависит цена\n" + \
    "\n".join(f"- {h}: {p}" for h, p in PRICE_FACTORS) + "\nЦены на сайте не публикуются: точная смета — после замера, в течение трёх часов.\n\n## Статьи\n" + \
    "\n".join(f"- {a['title']}: {SITE_URL}/stati/{a['slug']}/" for a in ARTICLES) + "\n\n## Частые вопросы\n" + "\n".join(f"- {q} {a}" for q, a in COMMON_FAQ) + "\n"
    (DIST / "llms.txt").write_text(llms, encoding="utf-8")

def build_chat_data():
    sv = [{"s": s["slug"], "n": s["name"], "d": s["short"], "u": f"/{s['slug']}/", "k": CHAT_ALIASES[s["slug"]]} for s in SERVICES]
    f = dict(FACTS)
    t = {
        "hi": "Здравствуйте! Я онлайн-консультант VIP Remont. Спросите о видах ремонта, смете или сроках — отвечу сразу, а точный расчёт сделает мастер после замера.",
        "price": "Стоимость зависит от площади, вида ремонта, состояния объекта и материалов. Точную смету готовим в течение трёх часов после замера, и цена фиксируется в договоре.",
        "smeta": f["Смета за 3 часа после замера"] + " Чтобы договориться о замере, напишите в WhatsApp или позвоните " + PHONE_DISPLAY + ".",
        "team": f["Своя бригада"], "ctrl": f["Приёмка каждого этапа"] + " " + f["График с датами этапов"], "mat": f["Материалы с чеками"],
        "gar": "Гарантия даётся на все работы, условия прописываем в договоре.",
        "srok": "Сроки зависят от площади и объёма работ. До старта составляем график с датами каждого этапа — точные сроки будут в плане после замера.",
        "area": "Работаем по всей Астане: Есиль, Алматы, Сарыарка, Байконыр и Нура, выезжаем и в пригород.",
        "pf": "Фото наших объектов — в разделе «Портфолио». Нажмите на фото, чтобы посмотреть объект целиком.",
        "svc": "{n}: {d}. Подробнее — на странице услуги, точную смету подготовим после замера.",
        "def": "Подскажу по видам ремонта, смете, материалам и срокам. Точный расчёт мастер сделает после замера — напишите в WhatsApp или позвоните " + PHONE_DISPLAY + ".",
        "call": "Позвонить", "wa": "В WhatsApp", "typing": "Печатает…", "q": "Вопрос", "pfl": "Портфолио",
    }
    (DIST / "assets" / "chat.json").write_text(json.dumps({"sv": sv, "t": t}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copyfile(ROOT / "src" / "app.js", DIST / "assets" / "app.js")
    if (ROOT / "assets" / "favicon.ico").exists(): shutil.copyfile(ROOT / "assets" / "favicon.ico", DIST / "favicon.ico")
    build_home(); build_services_index(); build_services(); build_portfolio(); build_prices(); build_districts(); build_faq(); build_articles()
    build_about(); build_contacts(); build_privacy(); build_404(); build_meta(); build_chat_data()
    print("страниц:", len(SITEMAP) + 1, "| услуг:", len(SERVICES), "| объектов с фото:", sum(1 for p in PORTFOLIO if pf_photos(p["slug"])), "из", len(PORTFOLIO))
    for p, t, d in LONG: print(f"  длинный title/description: {p} title={t} desc={d}")

if __name__ == "__main__":
    main()
