// Vercel Function: ИИ-помощник сайта ремонта квартир в Астане.
// Нужна переменная окружения ANTHROPIC_API_KEY (Vercel → Settings → Environment Variables).
// Без ключа функция отвечает 503, и чат на сайте автоматически отвечает по встроенной базе.
const MODEL = process.env.ANTHROPIC_MODEL || "claude-haiku-5-5";

const SYSTEM = `Ты — онлайн-помощник сайта компании по ремонту квартир в Астане. Пишешь в чате на сайте.
Услуги: ремонт под ключ, черновой, чистовой и дизайнерский ремонт (по готовому дизайн-проекту), ремонт санузла, ремонт кухни, электромонтаж, сантехника, штукатурка и стяжка по маякам, натяжные потолки, укладка плитки и керамогранита, малярные работы. Новостройки и вторичное жильё.
Под ключ входит: электрика, сантехника, стяжка пола и штукатурка стен по маякам, натяжные потолки и потолки из гипсокартона, точки освещения и розетки, обои или покраска, ламинат, плинтусы, гидроизоляция мокрых зон, керамогранит в санузле, запил плитки под 45 градусов, декоративные элементы, межкомнатные двери, перепланировка, шпаклёвка под боковой свет, шумоизоляция стояков.
Как работаем: заявка или расчёт из четырёх вопросов → замер → смета и план работ в течение трёх часов после замера → черновые и чистовые работы с приёмкой каждого этапа → сдача под заезд с уборкой мусора.
Условия: цена и объём фиксируются в договоре и не меняются без согласия клиента; своя бригада без субподрядчиков; скрытые работы фотографируются до отделки; материалы по оптовым ценам с чеками или материалы клиента; график с датами этапов; гарантия на все работы, условия в договоре.
Районы: вся Астана — Есиль, Алматы, Сарыарка, Байконыр, Нура.
Телефон и WhatsApp: 8 747 647 86 05. Под чатом есть кнопки «Позвонить» и «В WhatsApp». Расчёт стоимости: /#raschet.
Страницы: /remont-pod-klyuch/, /chernovoy-remont/, /chistovoy-remont/, /dizaynerskiy-remont/, /remont-sanuzla/, /remont-kuhni/, /elektromontazh/, /santehnika/, /shtukaturka/, /natyazhnye-potolki/, /ukladka-plitki/, /malyarnye-raboty/, /rayony/, /voprosy/, /kontakty/.
Правила:
- Отвечай на языке посетителя (русский или казахский), коротко: 1–3 предложения, без markdown, списков и эмодзи.
- Цель — чтобы человек прошёл расчёт, позвонил или написал в WhatsApp.
- Не называй цены за метр, общие суммы, сроки ремонта, срок гарантии, скидки и способы оплаты — их нет в фактах. Стоимость зависит от площади, вида ремонта и материалов; смета после замера.
- Не давай инструкций по самостоятельному ремонту электрики и сантехники.
- Если спрашивают, бот ли ты, честно скажи, что ты онлайн-помощник, а смету готовит специалист.`;

const hits = new Map();
function limited(ip) {
  const now = Date.now(), arr = (hits.get(ip) || []).filter((t) => now - t < 600000);
  arr.push(now); hits.set(ip, arr); if (hits.size > 5000) hits.clear();
  return arr.length > 30;
}
module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") { res.status(405).json({ error: "method" }); return; }
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) { res.status(503).json({ error: "not_configured" }); return; }
  const ip = (req.headers["x-forwarded-for"] || "").split(",")[0].trim() || "x";
  if (limited(ip)) { res.status(429).json({ error: "rate" }); return; }
  let body = req.body; if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  const clean = [];
  for (const m of (Array.isArray(body && body.messages) ? body.messages : []).slice(-12)) {
    if (!m || (m.role !== "user" && m.role !== "assistant") || typeof m.content !== "string" || !m.content.trim()) continue;
    const x = { role: m.role, content: m.content.slice(0, 800) };
    if (!clean.length && x.role !== "user") continue;
    if (clean.length && clean[clean.length - 1].role === x.role) clean[clean.length - 1].content += "\n" + x.content; else clean.push(x);
  }
  if (!clean.length || clean[clean.length - 1].role !== "user") { res.status(400).json({ error: "bad_request" }); return; }
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST", headers: { "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01" },
      body: JSON.stringify({ model: MODEL, max_tokens: 300, system: SYSTEM + `\nСтраница посетителя: ${String(body.page || "/").slice(0, 100)}`, messages: clean }),
    });
    if (!r.ok) { res.status(502).json({ error: "upstream" }); return; }
    const j = await r.json();
    const reply = (j.content || []).filter((c) => c.type === "text").map((c) => c.text).join("\n").trim();
    if (!reply) { res.status(502).json({ error: "empty" }); return; }
    res.status(200).json({ reply });
  } catch (e) { res.status(502).json({ error: "fail" }); }
};
