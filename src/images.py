# -*- coding: utf-8 -*-
"""Фото → WebP 480/800/1200 без EXIF и геолокации. Запуск: python3 src/images.py
- orig/hero/pc.jpg, mob.jpg    — главный фон: ПК 16:9 (от 1920 px), телефон 4:5 (от 1080 px)
- orig/portfolio/<объект>/*.jpg — фото объектов портфолио, папки obekt-a … obekt-t (первое фото по алфавиту — обложка)
- orig/uslugi/<адрес-услуги>.jpg — главное фото услуги (карточка и страница), например remont-kuhni.jpg
- orig/rukovoditel.jpg         — фото руководителя (вертикальное)
Vercel ничего не пересжимает — берёт готовые файлы из assets/img/."""
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parent.parent; O = ROOT / "orig"; A = ROOT / "assets" / "img"
EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".avif"}

def save(src, out_base, ratio, sizes=(480, 800, 1200), q=80):
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")             # поворот по EXIF, затем метаданные выбрасываем
        w = max(sizes); im = ImageOps.fit(im, (w, round(w / ratio)), Image.LANCZOS)
        clean = Image.new("RGB", im.size); clean.paste(im)          # новый объект — без EXIF/GPS
        out_base.parent.mkdir(parents=True, exist_ok=True)
        for s in sizes: clean.resize((s, round(s / ratio)), Image.LANCZOS).save(f"{out_base}-{s}.webp", "WEBP", quality=q, method=6)

def slug(name): return "".join(c if c.isalnum() or c == "-" else "-" for c in name.lower()).strip("-")

def main():
    n = 0
    for f in sorted((O / "uslugi").glob("*")):
        if f.suffix.lower() in EXT: save(f, A / "uslugi" / slug(f.stem), 3 / 2); n += 1
    for f in sorted((O / "hero").glob("*")):                       # pc.jpg (16:9) и mob.jpg (4:5)
        if f.suffix.lower() in EXT and f.stem in ("pc", "mob"):
            save(f, A / "hero" / f.stem, 16 / 9 if f.stem == "pc" else 4 / 5, (800, 1200, 1920) if f.stem == "pc" else (480, 800), q=78); n += 1
    for d in sorted((O / "portfolio").glob("*")):                   # папка на объект: orig/portfolio/obekt-a/*.jpg
        if d.is_dir():
            for f in sorted(d.glob("*")):
                if f.suffix.lower() in EXT: save(f, A / "portfolio" / d.name / slug(f.stem), 4 / 3); n += 1
    for f in O.glob("rukovoditel.*"):
        if f.suffix.lower() in EXT: save(f, A / "rukovoditel", 4 / 5, (480, 800)); n += 1
    print("фото обработано:", n)

if __name__ == "__main__":
    main()
