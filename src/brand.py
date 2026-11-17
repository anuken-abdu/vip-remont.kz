# -*- coding: utf-8 -*-
"""Логотип и иконки вкладки. Запуск: python3 src/brand.py
- orig/brand/logo.png — логотип на прозрачном фоне (горизонтальный) → assets/logo.webp (на сайте вместо текстового логотипа)
- orig/brand/icon.png — квадратная иконка 512×512 → favicon.ico (16/32/48), favicon-32.png, apple-touch-icon.png, icon-192/512.png
Пока файлов нет — делается временная круглая иконка с буквами VR."""
import struct, io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent; O = ROOT / "orig" / "brand"; A = ROOT / "assets"

def logo():
    f = O / "logo.png"
    if not f.exists(): return None
    im = Image.open(f).convert("RGBA"); box = im.getbbox(); im = im.crop(box)
    h = 96; w = round(im.width * h / im.height)                     # 2,4× от высоты 40 px на сайте
    im.resize((w, h), Image.LANCZOS).save(A / "logo.webp", "WEBP", quality=92, method=6)
    return w, h

def temp_icon():
    """Временная иконка: синий круг сайта, буквы VR шрифтом сайта (Manrope)."""
    from fontTools.ttLib import TTFont
    ttf = ROOT / "orig" / "_manrope.ttf"
    if not ttf.exists():
        t = TTFont(A / "fonts" / "manrope-latin-wght-normal.woff2"); t.flavor = None; t.save(ttf)
    s = 1024; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=(36, 80, 255, 255))
    fnt = ImageFont.truetype(str(ttf), 430)
    try: fnt.set_variation_by_axes([800])
    except Exception: pass
    d.text((s / 2, s / 2 + 8), "VR", font=fnt, fill=(255, 255, 255, 255), anchor="mm")
    ttf.unlink()
    return im.resize((512, 512), Image.LANCZOS)

def icons():
    f = O / "icon.png"
    im = Image.open(f).convert("RGBA") if f.exists() else temp_icon()
    data = []
    for s in (16, 32, 48):
        b = io.BytesIO(); im.resize((s, s), Image.LANCZOS).save(b, "PNG"); data.append((s, b.getvalue()))
    hdr = struct.pack("<HHH", 0, 1, len(data)); off = 6 + 16 * len(data); ent = b""
    for s, dd in data: ent += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(dd), off); off += len(dd)
    (A / "favicon.ico").write_bytes(hdr + ent + b"".join(dd for _, dd in data))
    im.resize((32, 32), Image.LANCZOS).save(A / "favicon-32.png")
    for n, s in (("icon-192.png", 192), ("icon-512.png", 512)): im.resize((s, s), Image.LANCZOS).save(A / n, optimize=True)
    bg = Image.new("RGBA", (180, 180), (15, 27, 45, 255)); bg.alpha_composite(im.resize((164, 164), Image.LANCZOS), (8, 8))   # iPhone не любит прозрачность
    bg.convert("RGB").save(A / "apple-touch-icon.png", optimize=True)
    return "свои" if f.exists() else "временные"

if __name__ == "__main__":
    print("логотип:", logo() or "текстовый (orig/brand/logo.png нет)"); print("иконки:", icons())
