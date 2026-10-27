"""Favicon и баннеры превью (assets/img/og/*.jpg). Запуск после build.py, затем build.py ещё раз."""
import base64, hashlib, json, pathlib, html
from PIL import Image
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent; A = ROOT / "assets"; OUT = A / "img" / "og"; OUT.mkdir(parents=True, exist_ok=True)
b64 = lambda p: base64.b64encode(p.read_bytes()).decode()
F = "".join(f'@font-face{{font-family:{n};font-weight:{w};font-style:{st};src:url(data:font/woff2;base64,{b64(A/"fonts"/f)})}}' for n, w, st, f in [
    ("S", 600, "normal", "playfair-display-cyrillic-500-normal.woff2"), ("SL", 600, "normal", "playfair-display-latin-500-normal.woff2"),
    ("S", 500, "italic", "playfair-display-cyrillic-500-italic.woff2"), ("SL", 500, "italic", "playfair-display-latin-500-italic.woff2"),
    ("O", 600, "normal", "golos-text-cyrillic-600-normal.woff2"), ("OL", 600, "normal", "golos-text-latin-600-normal.woff2")])
def og_html(t):
    size = 92 if len(t) <= 24 else 78 if len(t) <= 36 else 64
    return f'''<html><head><style>{F}body{{margin:0}}.b{{width:1200px;height:630px;position:relative;background:#f5efe7;color:#2b1f24;font-family:S,SL;overflow:hidden}}
.l{{position:absolute;left:72px;top:60px;font-size:34px;line-height:1}}.l small{{display:block;font-family:O,OL;font-size:15px;letter-spacing:.24em;text-transform:uppercase;color:#7a2e43;margin-top:8px}}
h1{{position:absolute;left:72px;right:300px;top:170px;margin:0;font-size:{size}px;line-height:1.02;font-weight:600;letter-spacing:-.01em}}
.r{{position:absolute;left:72px;right:292px;bottom:64px;border-top:2px solid #2b1f24;padding-top:22px;display:flex;justify-content:space-between;align-items:baseline;font-family:O,OL;font-size:22px;color:#5e4f55;letter-spacing:.04em}}
.r b{{font-family:S,SL;font-style:italic;font-weight:500;font-size:46px;color:#7a2e43;letter-spacing:0}}
.s{{position:absolute;right:0;top:0;width:220px;height:100%;background:#3b1d28}}.s i{{position:absolute;left:0;top:0;width:10px;height:100%;background:#7a2e43}}</style></head>
<body><div class="b"><div class="s"><i></i></div><div class="l">VIP Remont<small>Ремонт квартир · Астана</small></div><h1>{html.escape(t)}</h1><div class="r"><span>Смета после замера · цена в договоре</span><b>vip-remont.kz</b></div></div></body></html>'''
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 512, "height": 512})
    pg.set_content(f'<html><head><style>{F}</style></head><body style="margin:0"><div style="width:512px;height:512px;background:#7a2e43;color:#f5efe7;display:flex;align-items:center;justify-content:center;font-family:S,SL;font-weight:600;font-size:400px;line-height:1;padding-bottom:30px;font-style:italic">V</div></body></html>')
    pg.wait_for_timeout(200); pg.screenshot(path=str(A / "icon-512.png"))
    im = Image.open(A / "icon-512.png").convert("RGB")
    im.resize((192, 192), Image.LANCZOS).save(A / "icon-192.png"); im.resize((180, 180), Image.LANCZOS).save(A / "apple-touch-icon.png")
    im.save(A / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    OG = json.loads((ROOT / "src" / "og_list.json").read_text()); man_p = OUT / "manifest.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    pg2 = b.new_page(viewport={"width": 1200, "height": 630}); n = 0
    for url, (slug, title) in OG.items():
        key = hashlib.md5(("w1" + title).encode()).hexdigest()
        if man.get(slug) == key and (OUT / f"{slug}.jpg").exists(): continue
        pg2.set_content(og_html(title)); pg2.wait_for_timeout(120); pg2.screenshot(path=str(OUT / f"{slug}.jpg"), type="jpeg", quality=86); man[slug] = key; n += 1
    man_p.write_text(json.dumps(man, ensure_ascii=False, indent=1)); b.close()
print("og rendered", n)
