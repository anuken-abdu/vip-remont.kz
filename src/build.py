# -*- coding: utf-8 -*-
"""Генератор сайта ремонта квартир (Астана): python3 src/build.py → dist/"""
import html, json, pathlib, shutil, datetime
from urllib.parse import quote
from data import *

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
VER = "2810260100"
TODAY = datetime.date.today().isoformat()
E = lambda s: html.escape(str(s), quote=True)
def WA_URL(t="Здравствуйте! Хочу рассчитать стоимость ремонта квартиры."): return f"https://wa.me/{WA}?text=" + quote(t)
def nb(t): return t.replace(" в ", " в&nbsp;").replace(" и ", " и&nbsp;").replace(" под ", " под&nbsp;")
IMG = lambda rel: (ROOT / "images" / rel).exists()
SV = {s["slug"]: s for s in SERVICES}

def logo(cls="logo"):
    if IMG("logo.png"):
        return f'<a class="{cls}" href="/" aria-label="{BRAND} — на главную"><img src="/images/logo.png?v={VER}" alt="{BRAND}" height="44"></a>'
    return f'<a class="{cls}" href="/" aria-label="{BRAND} — на главную"><b>{BRAND}</b><small>Астана</small></a>'

NAV = [("/uslugi/", "Услуги"), ("/remont-pod-klyuch/", "Под ключ"), ("/#raschet", "Расчёт"), ("/rayony/", "Районы"), ("/voprosy/", "Вопросы"), ("/kontakty/", "Контакты")]

def cta(cls="", wa_text=None, calc=True):
    c = '<a class="btn btn-ac" href="#raschet">Рассчитать стоимость</a>' if calc else f'<a class="btn btn-ac" href="tel:{TEL}" data-ev="call">{PHONE_LOCAL}</a>'
    return f'<div class="cta {cls}">{c}<a class="btn btn-wa" href="{WA_URL(wa_text) if wa_text else WA_URL()}" target="_blank" rel="noopener" data-ev="wa">Написать в WhatsApp</a></div>'

def header(cur):
    items = "".join(f'<li><a href="{h}"{" aria-current=page" if h == cur else ""}>{n}</a></li>' for h, n in NAV)
    return f'''<a class="skip" href="#main">Перейти к содержанию</a>
<header class="hdr"><div class="wrap hdr-in">{logo()}
<nav class="nav" id="nav" aria-label="Основное меню"><ul>{items}</ul><div class="nav-x"><a class="btn btn-ac" href="tel:{TEL}" data-ev="call">Позвонить</a><a class="btn btn-wa" href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa">WhatsApp</a></div></nav>
<a class="hdr-ph" href="tel:{TEL}" data-ev="call">{PHONE_LOCAL}</a>
<button class="burger" type="button" aria-controls="nav" aria-expanded="false"><span class="b-o">Меню</span><span class="b-c">Закрыть</span></button></div></header>'''

def footer():
    sv = "".join(f'<li><a href="/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    ds = "".join(f'<li><a href="/rayony/{s}/">{n}</a></li>' for s, n, _ in DISTRICTS)
    ig = f'<li><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></li>' if INSTAGRAM else ""
    return f'''<footer class="ftr"><div class="wrap">
<div class="ftr-top"><p class="ftr-big">Рассчитаем ремонт вашей квартиры</p><a class="ftr-tel" href="tel:{TEL}" data-ev="call">{PHONE_LOCAL}</a></div>
<div class="ftr-g"><div class="ftr-a">{logo("logo logo-f")}<p>{LEAD}</p>{f'<p>{HOURS}</p>' if HOURS else ""}</div>
<div><h4>Услуги</h4><ul class="ftr-2">{sv}</ul></div><div><h4>Районы Астаны</h4><ul>{ds}</ul></div>
<div><h4>Связь</h4><ul><li><a href="tel:{TEL}" data-ev="call">Позвонить</a></li><li><a href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa">WhatsApp</a></li>{ig}<li><a href="/voprosy/">Вопросы</a></li><li><a href="/kontakty/">Контакты</a></li></ul></div></div>
<div class="ftr-b"><span>© {datetime.date.today().year} {BRAND}, Астана</span><a href="/politika/">Политика конфиденциальности</a><a href="{DEV_URL}" target="_blank" rel="noopener">Разработка сайта — {DEV_NAME}</a></div></div></footer>
<div class="mbar"><a class="btn btn-ac" href="tel:{TEL}" data-ev="call">Позвонить</a><a class="btn btn-wa" href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa">WhatsApp</a></div>
<div class="fl"><button class="fl-b fl-back" type="button" hidden>Назад</button><button class="fl-b fl-top" type="button" hidden>Наверх</button><button class="fl-b fl-chat" type="button" aria-controls="chat" aria-expanded="false">Задать вопрос</button></div>
<section class="chat" id="chat" role="dialog" aria-label="Онлайн-помощник" hidden><div class="chat-h"><div><b>Онлайн-помощник</b><small>Ответит на вопросы о ремонте</small></div><button class="chat-x" type="button">Закрыть</button></div>
<div class="chat-b" id="chatB" aria-live="polite"></div><div class="chat-q" id="chatQ"></div>
<div class="chat-cta"><a href="tel:{TEL}" data-ev="call">Позвонить</a><a href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa" id="chatWa">В WhatsApp</a></div>
<form class="chat-f" id="chatF" autocomplete="off"><label class="sr" for="chatI">Ваш вопрос</label><input id="chatI" type="text" maxlength="500" placeholder="Например: сколько стоит ремонт под ключ?"><button type="submit">Отправить</button></form></section>'''

ORG = {"@context": "https://schema.org", "@type": ["LocalBusiness", "HomeAndConstructionBusiness"], "@id": SITE + "/#org", "name": BRAND, "url": SITE + "/",
       "telephone": PHONE, "image": SITE + "/assets/img/og/home.jpg", "description": LEAD,
       "address": {"@type": "PostalAddress", "addressLocality": "Астана", "addressCountry": "KZ"},
       "areaServed": [{"@type": "City", "name": "Астана"}] + [{"@type": "AdministrativeArea", "name": f"Район {n}, Астана"} for _, n, _ in DISTRICTS],
       "knowsAbout": [s["name"] for s in SERVICES],
       "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Услуги", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": f'{SITE}/{s["slug"]}/'}} for s in SERVICES]},
       "contactPoint": {"@type": "ContactPoint", "telephone": PHONE, "contactType": "customer service", "availableLanguage": ["ru", "kk"]},
       "sameAs": [f"https://wa.me/{WA}"] + ([INSTAGRAM] if INSTAGRAM else [])}
if IMG("logo.png"): ORG["logo"] = SITE + "/images/logo.png"
def ld_crumbs(items): return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h} for i, (h, n) in enumerate(items)]}
def ld_faq(faq): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
def ld_svc(name, desc, url, area=None):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc, "serviceType": name, "provider": {"@id": SITE + "/#org"}, "url": SITE + url,
            "areaServed": area or {"@type": "City", "name": "Астана"}}

OG = {}
def page(url, title, desc, body, cur="", ld=(), crumbs=None, og_title=None):
    og = "home" if url in ("/", "/404/") else url.strip("/").replace("/", "-")
    if url != "/404/": OG[url] = (og, og_title or title.split(" — ")[0])
    lds = [ORG] + list(ld) + ([ld_crumbs([("/", "Главная")] + crumbs)] if crumbs else [])
    if url == "/": lds.append({"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/", "inLanguage": "ru"})
    tag = GA_ID or GADS_ID
    ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={tag}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());'
          + "".join(f'gtag("config","{x}");' for x in (GA_ID, GADS_ID) if x) + "</script>") if tag else ""
    cr = ""
    if crumbs:
        cr = '<nav class="crumbs" aria-label="Хлебные крошки"><ol><li><a href="/">Главная</a></li>' + "".join(
            f'<li><a href="{h}">{n}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{n}</li>' for i, (h, n) in enumerate(crumbs)) + "</ol></nav>"
    body = body.replace("<!--CRUMBS-->", cr)
    cfg = json.dumps({"ads": [GADS_ID, GADS_CALL_LABEL, GADS_WA_LABEL], "tel": TEL, "phone": PHONE_LOCAL, "wa": WA,
                      "districts": [n for _, n, _ in DISTRICTS], "svc": [[s["slug"], s["name"]] for s in SERVICES]}, ensure_ascii=False)
    full = SITE + url
    return f'''<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{ga}
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{full}"><meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#f2efe8"><meta name="geo.region" content="KZ-71"><meta name="geo.placename" content="Астана"><meta name="geo.position" content="51.128207;71.430411"><meta name="ICBM" content="51.128207, 71.430411">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_KZ"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{full}">
<meta property="og:image" content="{SITE}/assets/img/og/{og}.jpg?v={VER}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48"><link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/cormorant-garamond-cyrillic-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/onest-cyrillic-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/styles.css?v={VER}">
{"".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)}
</head><body>
{header(cur)}
<main id="main">
{body}
</main>
{footer()}
<script>window.RK={cfg};</script><script src="/assets/app.js?v={VER}" defer></script>
</body></html>'''

def write(url, content):
    p = DIST / "404.html" if url == "/404/" else (DIST / url.strip("/") / "index.html" if url != "/" else DIST / "index.html")
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")

# ---------- блоки ----------
def sec(title, inner, sub="", cls="", link=None, sid=""):
    lk = f'<a class="lnk" href="{link[1]}">{link[0]}</a>' if link else ""
    return f'''<section class="sec {cls}"{f' id="{sid}"' if sid else ""}><div class="wrap"><div class="sec-h"><h2>{title}</h2>{f"<p>{sub}</p>" if sub else ""}{lk}</div>{inner}</div></section>'''

def svc_index(exclude=None, groups=True):
    out = ""
    for g, gname in GROUPS:
        rows = "".join(f'<li><a href="/{s["slug"]}/"><span class="ix-n">{SERVICES.index(s)+1:02d}</span><span class="ix-t"><b>{s["name"]}</b><small>{s["lead"]}</small></span><span class="ix-m">Подробнее</span></a></li>'
                       for s in SERVICES if s["grp"] == g and s["slug"] != exclude)
        out += f'<div class="ix-g">{f"<h3>{gname}</h3>" if groups else ""}<ol class="ix">{rows}</ol></div>'
    return f'<div class="ix-w">{out}</div>'

def numbered(items, cls="nl"):
    return f'<ol class="{cls}">' + "".join(f'<li><span>{i+1:02d}</span>{E(x)}</li>' for i, x in enumerate(items)) + "</ol>"

def advantages(n=6):
    return '<div class="adv">' + "".join(f'<div class="adv-i"><span class="adv-n">{i+1:02d}</span><h3>{t}</h3><p>{x}</p></div>' for i, (t, x) in enumerate(ADVANTAGES[:n])) + "</div>"

def steps():
    return '<ol class="st">' + "".join(f'<li><span class="st-n">Этап {i+1}</span><h3>{t}</h3><p>{x}</p></li>' for i, (t, x) in enumerate(STEPS)) + "</ol>"

def faq_html(faq):
    return '<div class="faq">' + "".join(f'<details><summary><span>{q}</span><i aria-hidden="true"></i></summary><p>{a}</p></details>' for q, a in faq) + "</div>"

def quiz(pre=None):
    qs = ""
    for i, (q, opts) in enumerate(QUIZ):
        o = "".join(f'<label class="qz-o"><input type="radio" name="q{i}" value="{E(x)}"{" checked" if pre and x == pre and i == 1 else ""}><span>{x}</span></label>' for x in opts)
        qs += f'<fieldset class="qz-q" data-i="{i}"{"" if i == 0 else " hidden"}><legend><span class="qz-c">Вопрос {i+1} из {len(QUIZ)}</span>{q}</legend><div class="qz-os">{o}</div></fieldset>'
    return f'''<section class="sec qz-sec" id="raschet"><div class="wrap qz-w"><div class="qz-l"><h2>Рассчитать стоимость ремонта</h2><p>Ответьте на четыре вопроса — ответы уйдут в WhatsApp, а мы подготовим расчёт. Точную смету составим после замера, цена фиксируется в договоре.</p>
<p class="qz-alt">Удобнее голосом? <a href="tel:{TEL}" data-ev="call">{PHONE_LOCAL}</a></p></div>
<form class="qz" id="qz" novalidate><div class="qz-bar"><i style="width:25%"></i></div>{qs}
<div class="qz-done" hidden><p class="qz-c">Готово</p><p class="qz-sum"></p><a class="btn btn-wa qz-send" href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa">Отправить в WhatsApp</a><button type="button" class="qz-re">Пройти заново</button></div>
<div class="qz-nav"><button type="button" class="qz-prev" hidden>Назад</button><p class="qz-hint">Выберите вариант</p></div></form></div></section>'''

def portfolio():
    ph = sorted((ROOT / "images" / "portfolio").glob("*.jpg"))
    if not ph: return ""
    g = "".join(f'<figure><img src="/images/portfolio/{p.name}?v={VER}" alt="Ремонт квартиры в Астане — пример работы {i+1}" loading="lazy" decoding="async" width="800" height="600"></figure>' for i, p in enumerate(ph))
    return sec("Наши работы", f'<div class="pf">{g}</div>', "Квартиры, которые мы отремонтировали в Астане.")

def districts_html(cur=None):
    return '<ul class="ds">' + "".join(f'<li><a href="/rayony/{s}/"{" aria-current=page" if s == cur else ""}><b>{n}</b><span>Ремонт квартир {inn}</span></a></li>' for s, n, inn in DISTRICTS) + "</ul>"

def band(title="Обсудим ваш ремонт", sub="Позвоните или напишите в WhatsApp — договоримся о замере."):
    return f'''<section class="band"><div class="wrap band-in"><div><h2>{title}</h2><p>{sub}</p></div><div class="cta"><a class="btn btn-light" href="tel:{TEL}" data-ev="call">{PHONE_LOCAL}</a><a class="btn btn-wa" href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa">Написать в WhatsApp</a></div></div></section>'''

FACTS = [("Смета", "в течение трёх часов после замера"), ("Цена", "фиксируется в договоре"), ("Бригада", "своя, без субподрядчиков")]
def facts(): return '<dl class="facts">' + "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in FACTS) + "</dl>"

def side(photo, title, items, more=None):
    if photo and IMG(photo):
        return f'<figure class="hero-ph"><img src="/images/{photo}?v={VER}" alt="{E(title)}" width="900" height="1100" fetchpriority="high"></figure>'
    lk = f'<a href="{more[1]}">{more[0]}</a>' if more else ""
    return f'<aside class="hero-card"><p class="hc-t">{title}</p>{numbered(items, "hc-l")}{lk}</aside>'

def hero(h1, lead, side_html, crumbs=True, wa_text=None, home=False):
    return f'''<section class="hero{" hero-home" if home else ""}"><div class="wrap hero-in"><div class="hero-t">{"<!--CRUMBS-->" if crumbs else ""}<h1>{h1}</h1><p class="lead">{lead}</p>{cta("cta-l", wa_text=wa_text)}{facts()}</div>{side_html}</div></section>'''

# ---------- страницы ----------
def build_home():
    body = f'''{hero('Ремонт квартир в&nbsp;Астане <em>под&nbsp;ключ</em>', "Черновой, чистовой и дизайнерский ремонт, санузлы и кухни. Одна бригада, одна смета, сдача квартиры под заезд.",
                  side("hero.jpg", "Ремонт под ключ: что входит", TURNKEY[:7], ("Весь перечень работ", "/remont-pod-klyuch/")), crumbs=False, home=True)}
{sec("Услуги", svc_index(), "Ремонт квартиры целиком или отдельные работы — от электрики до покраски.", sid="uslugi")}
{sec("Что входит в ремонт под ключ", numbered(TURNKEY, "nl nl-3"), "Все работы — в одной смете и одном договоре.", "sec-dark", ("Подробнее о ремонте под ключ", "/remont-pod-klyuch/"))}
{sec("Почему с нами спокойно", advantages())}
{sec("Как мы работаем", steps(), "", "sec-alt")}
{quiz()}
{portfolio()}
{sec("Работаем по всей Астане", districts_html(), "Выезжаем на замер в любой район города.", link=("Все районы", "/rayony/"))}
{sec("Частые вопросы", faq_html(FAQ), "", "sec-alt", ("Все вопросы", "/voprosy/"))}
{band()}'''
    write("/", page("/", "Ремонт квартир в Астане под ключ — смета за 3 часа после замера",
                    f"Ремонт квартир под ключ в Астане: черновой, чистовой, дизайнерский ремонт, санузлы и кухни. Цена фиксируется в договоре. Тел. {PHONE_LOCAL}.",
                    body, "/", [ld_faq(FAQ)], og_title="Ремонт квартир в Астане под ключ"))

def build_services():
    body = f'''{hero("Услуги по ремонту квартир в&nbsp;Астане", "Ремонт квартиры под ключ или отдельные виды работ — выполняет своя бригада.", side(None, "Ремонт под ключ: что входит", TURNKEY[:7], ("Весь перечень работ", "/remont-pod-klyuch/")))}
{sec("Все услуги", svc_index())}{quiz()}{band()}'''
    write("/uslugi/", page("/uslugi/", "Услуги по ремонту квартир в Астане", f"Ремонт под ключ, черновой и чистовой ремонт, санузлы, кухни, электрика, сантехника, штукатурка, потолки, плитка. Тел. {PHONE_LOCAL}.",
                           body, "/uslugi/", crumbs=[("/uslugi/", "Услуги")], og_title="Услуги по ремонту квартир"))
    for s in SERVICES:
        url = f'/{s["slug"]}/'
        faq = s["faq"] + [FAQ[0], FAQ[1]]
        incl = sec("Что входит", numbered(s["inc"], "nl nl-2"), "Точный перечень работ фиксируем в смете после замера.") if IMG(f'uslugi/{s["slug"]}.jpg') else ""
        body = f'''{hero(nb(s["h1"]), s["lead"], side(f'uslugi/{s["slug"]}.jpg', "Что входит", s["inc"]), wa_text=f"Здравствуйте! Интересует: {s['name'].lower()}. Хочу рассчитать стоимость.")}
{incl}
{sec("Почему с нами спокойно", advantages())}
{sec("Как мы работаем", steps(), "", "sec-alt")}
{quiz(s["name"].replace("Ремонт под ключ", "Под ключ").replace("Черновой ремонт", "Черновой").replace("Чистовой ремонт", "Чистовой").replace("Дизайнерский ремонт", "Дизайнерский").replace("Ремонт санузла", "Санузел").replace("Ремонт кухни", "Кухня"))}
{sec("Вопросы", faq_html(faq))}
{sec("Другие услуги", svc_index(exclude=s["slug"]), "", "sec-alt")}
{band()}'''
        write(url, page(url, f'{s["h1"]} — цена в договоре', f'{s["lead"]} Тел. {PHONE_LOCAL}.', body, "/remont-pod-klyuch/" if s["slug"] == "remont-pod-klyuch" else "/uslugi/",
                        [ld_svc(s["h1"], s["lead"], url), ld_faq(faq)], crumbs=[("/uslugi/", "Услуги"), (url, s["name"])], og_title=s["h1"]))

def build_districts():
    body = f'''{hero("Ремонт квартир по районам Астаны", "Выезжаем на замер в любой район города. Выберите свой — на странице услуги и расчёт стоимости.", side(None, "Районы", [n for _, n, _ in DISTRICTS]))}
{sec("Районы", districts_html())}{sec("Услуги", svc_index(), "", "sec-alt")}{quiz()}{band()}'''
    write("/rayony/", page("/rayony/", "Ремонт квартир по районам Астаны", f"Ремонт квартир под ключ во всех районах Астаны: Есиль, Алматы, Сарыарка, Байконыр, Нура. Тел. {PHONE_LOCAL}.", body, "/rayony/",
                           crumbs=[("/rayony/", "Районы")], og_title="Ремонт квартир по районам Астаны"))
    for slug, n, inn in DISTRICTS:
        url = f"/rayony/{slug}/"
        h1 = f"Ремонт квартир {inn}, Астана"
        lead = f"Ремонт квартир под ключ {inn}: новостройки и вторичное жильё. Черновой, чистовой и дизайнерский ремонт, санузлы и кухни."
        fq = [(f"Выезжаете на замер {inn}?", f"Да, выезжаем на замер {inn} и по всей Астане. Договоритесь о времени по телефону {PHONE_LOCAL} или в WhatsApp."), FAQ[0], FAQ[1]]
        body = f'''{hero(nb(h1), lead, side(None, "Ремонт под ключ: что входит", TURNKEY[:7], ("Весь перечень работ", "/remont-pod-klyuch/")), wa_text=f"Здравствуйте! Нужен ремонт квартиры, район {n}.")}
{sec(f"Услуги {inn}", svc_index())}
{sec("Как мы работаем", steps(), "", "sec-alt")}
{quiz()}
{sec("Вопросы", faq_html(fq))}
{sec("Другие районы", districts_html(cur=slug), "", "sec-alt")}{band()}'''
        write(url, page(url, f"Ремонт квартир {inn} Астаны — под ключ", f"{lead} Тел. {PHONE_LOCAL}.", body, "/rayony/",
                        [ld_svc(h1, lead, url, {"@type": "AdministrativeArea", "name": f"Район {n}, Астана"}), ld_faq(fq)],
                        crumbs=[("/rayony/", "Районы"), (url, n)], og_title=f"Ремонт квартир: район {n}"))

def build_misc():
    allfaq = FAQ + [q for s in SERVICES for q in s["faq"]]
    body = f'''{hero("Вопросы о ремонте квартир", "Отвечаем на частые вопросы о стоимости, сроках, материалах и контроле ремонта.", side(None, "Коротко о главном", [f"{a} {b}" for a, b in FACTS]))}
{sec("Частые вопросы", faq_html(allfaq))}{quiz()}{band()}'''
    write("/voprosy/", page("/voprosy/", "Вопросы о ремонте квартир в Астане", "Сколько стоит ремонт квартиры, как быстро будет смета, кто закупает материалы, как проходит приёмка работ.", body, "/voprosy/",
                            [ld_faq(allfaq)], crumbs=[("/voprosy/", "Вопросы")], og_title="Вопросы о ремонте квартир"))
    rows = f'<li><span>Телефон</span><a href="tel:{TEL}" data-ev="call">{PHONE_LOCAL}</a></li><li><span>WhatsApp</span><a href="{WA_URL()}" target="_blank" rel="noopener" data-ev="wa">{PHONE_LOCAL}</a></li>'
    if INSTAGRAM: rows += f'<li><span>Instagram</span><a href="{INSTAGRAM}" target="_blank" rel="noopener">{INSTAGRAM.rstrip("/").split("/")[-1]}</a></li>'
    if HOURS: rows += f"<li><span>Режим работы</span><b>{HOURS}</b></li>"
    rows += "<li><span>Где работаем</span><b>Все районы Астаны</b></li>"
    body = f'''{hero("Контакты", "Позвоните или напишите в WhatsApp — договоримся о замере и подготовим смету.", side(None, "Как начать", [t for t, _ in STEPS[:3]]))}
{sec("Связаться", f'<ul class="ct">{rows}</ul>')}{quiz()}{sec("Районы", districts_html(), "", "sec-alt")}'''
    write("/kontakty/", page("/kontakty/", f"Контакты — ремонт квартир в Астане, {PHONE_LOCAL}", f"Ремонт квартир в Астане: {PHONE_LOCAL}, WhatsApp. Замер в любом районе города.", body, "/kontakty/",
                             crumbs=[("/kontakty/", "Контакты")], og_title="Контакты"))
    S = [("Какие данные мы получаем", "Если вы проходите расчёт, звоните или пишете в WhatsApp, мы видим ваш номер и сообщения, которые вы отправляете. Ответы расчёта передаются только в WhatsApp и на сайте не сохраняются."),
         ("Онлайн-помощник", "Вопросы, которые вы задаёте в чате, обрабатываются сервисом искусственного интеллекта, чтобы сформировать ответ. Не указывайте в чате лишних личных данных."),
         ("Зачем", "Чтобы связаться с вами, подготовить расчёт и выполнить ремонт."),
         ("Аналитика", "Сайт может использовать сервисы веб-аналитики Google, которые собирают обезличенные данные о посещениях и нажатиях."),
         ("Передача третьим лицам", "Мы не передаём ваши данные третьим лицам, кроме случаев, предусмотренных законодательством Республики Казахстан."),
         ("Обращения", f"По вопросам обработки данных: {PHONE_LOCAL}.")]
    body = f'''<section class="hero hero-sm"><div class="wrap"><!--CRUMBS--><h1>Политика конфиденциальности</h1></div></section>
<section class="sec"><div class="wrap prose">{"".join(f"<h2>{h}</h2><p>{t}</p>" for h, t in S)}</div></section>'''
    write("/politika/", page("/politika/", "Политика конфиденциальности", f"Политика обработки данных посетителей сайта {DOMAIN}.", body, crumbs=[("/politika/", "Политика конфиденциальности")]))
    body = f'''<section class="hero hero-sm"><div class="wrap"><h1>Страница не найдена</h1><p class="lead">Возможно, она была перемещена. Посмотрите услуги или свяжитесь с нами.</p>{cta(calc=False)}</div></section>{sec("Услуги", svc_index())}'''
    write("/404/", page("/404/", "Страница не найдена", "Страница не найдена.", body).replace('content="index,follow,max-image-preview:large"', 'content="noindex"'))

def build_meta():
    urls = list(OG)
    pr = lambda u: "1.0" if u == "/" else "0.9" if u.strip("/") in SV else "0.7"
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr(u)}</priority></url>\n" for u in urls)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n', encoding="utf-8")
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Bingbot", "YandexBot"]
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /api/\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    ll = [f"# {BRAND} — Астана", "", f"> {LEAD}", "", "## Главное", "- Город: Астана, все районы (Есиль, Алматы, Сарыарка, Байконыр, Нура)",
          f"- Телефон и WhatsApp: {PHONE_LOCAL} ({PHONE}), https://wa.me/{WA}",
          "- Стоимость: зависит от площади, вида ремонта и материалов; смета — в течение трёх часов после замера; цена фиксируется в договоре",
          f"- Расчёт стоимости онлайн: {SITE}/#raschet", "", "## Преимущества"] + [f"- {t}: {x}" for t, x in ADVANTAGES] + ["", "## Этапы"] + [f"{i+1}. {t} — {x}" for i, (t, x) in enumerate(STEPS)] + [""]
    for s in SERVICES:
        ll += [f"## [{s['h1']}]({SITE}/{s['slug']}/)", f"- {s['lead']}", "- Входит: " + "; ".join(s["inc"]), ""]
    ll += ["## Районы"] + [f"- [Район {n}]({SITE}/rayony/{s}/)" for s, n, _ in DISTRICTS] + ["", "## Частые вопросы"] + [f"- {q} {a}" for q, a in FAQ]
    (DIST / "llms.txt").write_text("\n".join(ll) + "\n", encoding="utf-8")
    (DIST / "site.webmanifest").write_text(json.dumps({"name": f"{BRAND} — Астана", "short_name": BRAND, "start_url": "/", "display": "browser", "background_color": "#f2efe8", "theme_color": "#f2efe8",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False), encoding="utf-8")
    (ROOT / "src" / "og_list.json").write_text(json.dumps(OG, ensure_ascii=False, indent=1), encoding="utf-8")

def build_assets():
    shutil.copytree(ROOT / "assets", DIST / "assets", dirs_exist_ok=True)
    shutil.copy(ROOT / "src" / "app.js", DIST / "assets" / "app.js")
    if (ROOT / "images").exists(): shutil.copytree(ROOT / "images", DIST / "images", dirs_exist_ok=True)
    for f in ("favicon.ico", "icon-192.png", "icon-512.png", "apple-touch-icon.png"):
        if (ROOT / "assets" / f).exists(): shutil.copy(ROOT / "assets" / f, DIST / f)

if __name__ == "__main__":
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    build_assets(); build_home(); build_services(); build_districts(); build_misc(); build_meta()
    print("pages:", len(OG) + 1)
