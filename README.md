# Ремонт квартир — Астана (сайт)

Статический сайт: генератор `src/build.py` → папка `dist/` (уже собрана). Хостинг — Vercel (настройки в `vercel.json`).

## Деплой
1. Залить проект в GitHub → импортировать в Vercel.
2. Vercel → Settings → Environment Variables: `ANTHROPIC_API_KEY` — для ИИ-чата (без ключа чат отвечает по встроенной базе).
3. Подключить домен (с www) и указать его в `src/data.py` → `SITE`, пересобрать.

## Что поменять в `src/data.py`, затем `python3 src/build.py`
- `BRAND`, `SITE`, `PHONE`/`PHONE_LOCAL`/`TEL`/`WA` — название, домен, телефон.
- `HOURS`, `INSTAGRAM` — если есть (пусто = не выводится).
- `GA_ID`, `GADS_ID`, `GADS_CALL_LABEL`, `GADS_WA_LABEL` — теги Google и метки конверсий.
После смены названия/телефона: `python3 src/render_brand.py`, затем `python3 src/build.py`.

## Логотип и фото
См. `images/README.txt` — блоки появляются автоматически после добавления файлов и пересборки.
