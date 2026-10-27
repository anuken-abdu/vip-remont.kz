/* Ремонт квартир, Астана: меню, «назад/наверх», расчёт стоимости, онлайн-помощник, учёт звонков и WhatsApp в Google Ads */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var CFG = window.RK || {}, body = document.body, root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var PH = CFG.phone || "", WAN = CFG.wa || "";
  function waLink(t) { return "https://wa.me/" + WAN + "?text=" + encodeURIComponent(t); }
  function lock() { root.classList.toggle("lock", body.classList.contains("nav-open") || (body.classList.contains("chat-open") && window.innerWidth < 600)); }

  /* ---------- меню ---------- */
  var burger = $(".burger");
  function setNav(o) { body.classList.toggle("nav-open", o); lock(); if (burger) burger.setAttribute("aria-expanded", o ? "true" : "false"); }
  if (burger) burger.addEventListener("click", function () { setNav(!body.classList.contains("nav-open")); });
  $$(".nav a").forEach(function (a) { a.addEventListener("click", function () { setNav(false); }); });
  window.addEventListener("resize", function () { if (window.innerWidth >= 1100 && body.classList.contains("nav-open")) setNav(false); });

  /* ---------- конверсии ---------- */
  var ADS = CFG.ads || [], last = {};
  function conv(ev) {
    if (!window.gtag) return;
    var now = Date.now(); if (last[ev] && now - last[ev] < 1500) return; last[ev] = now;
    try {
      window.gtag("event", ev === "call" ? "phone_click" : "whatsapp_click");
      var label = ev === "call" ? ADS[1] : ADS[2];
      if (ADS[0] && label) window.gtag("event", "conversion", { send_to: ADS[0] + "/" + label });
    } catch (e) {}
  }
  document.addEventListener("click", function (e) { var a = e.target.closest && e.target.closest("[data-ev]"); if (a) conv(a.getAttribute("data-ev")); });

  /* ---------- назад / наверх ---------- */
  var bBack = $(".fl-back"), bTop = $(".fl-top");
  if (bBack) {
    bBack.hidden = location.pathname === "/";
    bBack.addEventListener("click", function () {
      var same = false; try { same = document.referrer && new URL(document.referrer).host === location.host; } catch (e) {}
      if (same && history.length > 1) { history.back(); return; }
      var cr = $$(".crumbs a"); location.href = cr.length ? cr[cr.length - 1].getAttribute("href") : "/";
    });
  }
  if (bTop) bTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });
  var tick = false;
  function onScroll() { tick = false; if (bTop) bTop.hidden = (window.pageYOffset || root.scrollTop) < 500; }
  window.addEventListener("scroll", function () { if (!tick) { tick = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- расчёт стоимости: 4 вопроса → WhatsApp ---------- */
  var qz = $("#qz");
  if (qz) {
    var qs = $$(".qz-q", qz), done = $(".qz-done", qz), prev = $(".qz-prev", qz), bar = $(".qz-bar i", qz), hint = $(".qz-hint", qz), cur = 0;
    function show(i) {
      cur = i;
      qs.forEach(function (q, k) { q.hidden = k !== i; });
      done.hidden = i < qs.length;
      prev.hidden = i === 0 || i >= qs.length;
      hint.hidden = i >= qs.length;
      bar.style.width = Math.round(Math.min(i + 1, qs.length) / qs.length * 100) + "%";
      if (i >= qs.length) {
        var ans = qs.map(function (q) { var c = $("input:checked", q); return c ? c.value : ""; });
        var leg = qs.map(function (q) { return q.querySelector("legend").lastChild.textContent.trim(); });
        $(".qz-sum", qz).textContent = ans.filter(Boolean).join(" · ");
        var t = "Здравствуйте! Хочу рассчитать стоимость ремонта.\n" + leg.map(function (l, k) { return l + " " + (ans[k] || "—"); }).join("\n");
        $(".qz-send", qz).href = waLink(t);
      }
    }
    qs.forEach(function (q, k) {
      $$("input", q).forEach(function (inp) {
        inp.addEventListener("change", function () { setTimeout(function () { show(k + 1); }, 180); });
      });
    });
    prev.addEventListener("click", function () { if (cur > 0) show(cur - 1); });
    $(".qz-re", qz).addEventListener("click", function () { $$("input", qz).forEach(function (i) { i.checked = false; }); show(0); });
    // если вид ремонта предвыбран на странице услуги — второй вопрос пропускаем, когда до него дойдём
    var pre = $$("input:checked", qs[1] || qz).length > 0;
    if (pre) {
      $$("input", qs[0]).forEach(function (inp) { inp.addEventListener("change", function () { setTimeout(function () { if (cur === 1 && $$("input:checked", qs[1]).length) show(2); }, 200); }); });
    }
    show(0);
  }

  /* ================= онлайн-помощник ================= */
  var chat = $("#chat"), fab = $(".fl-chat"), cb = $("#chatB"), cq = $("#chatQ"), cf = $("#chatF"), ci = $("#chatI"), waBtn = $("#chatWa");
  if (!chat) return;
  var hist = [], started = false, busy = false, apiOk = true;
  function openChat() {
    chat.hidden = false; body.classList.add("chat-open"); lock(); fab.setAttribute("aria-expanded", "true");
    if (!started) { started = true; say("Здравствуйте! Я онлайн-помощник. Подскажу по видам ремонта, этапам и расчёту стоимости. Какую квартиру планируете ремонтировать?", QUICK); }
    if (window.innerWidth > 767) setTimeout(function () { ci.focus(); }, 50);
  }
  function closeChat() { if (chat.hidden) return; chat.hidden = true; body.classList.remove("chat-open"); lock(); fab.setAttribute("aria-expanded", "false"); fab.focus(); }
  fab.addEventListener("click", function () { chat.hidden ? openChat() : closeChat(); });
  $(".chat-x").addEventListener("click", closeChat);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { setNav(false); closeChat(); } });

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function linkify(s) {
    return esc(s).replace(/(\/(?:[a-z\-]+\/)+(?:#raschet)?|\/#raschet)/g, '<a href="$1">$1</a>')
      .replace(/(8 747 647 86 05|\+7 747 647 86 05)/g, '<a href="tel:' + CFG.tel + '" data-ev="call">$1</a>');
  }
  function add(role, text) { var m = document.createElement("div"); m.className = "msg " + (role === "u" ? "msg-u" : "msg-b"); m.innerHTML = role === "u" ? esc(text) : linkify(text); cb.appendChild(m); cb.scrollTop = cb.scrollHeight; }
  function dots() { var t = document.createElement("div"); t.className = "msg msg-b dots"; t.innerHTML = "<i></i><i></i><i></i>"; cb.appendChild(t); cb.scrollTop = cb.scrollHeight; return t; }
  function say(text, quick) { var t = dots(); setTimeout(function () { t.remove(); add("b", text); hist.push({ role: "assistant", content: text }); setQuick(quick); updWa(); }, Math.min(1200, 350 + text.length * 4)); }
  var QUICK = ["Сколько стоит ремонт?", "Что входит в под ключ?", "Ремонт санузла", "Как быстро смета?", "Своя бригада?"];
  function setQuick(list) {
    cq.innerHTML = "";
    (list || QUICK).forEach(function (q) { var b = document.createElement("button"); b.type = "button"; b.textContent = q; b.addEventListener("click", function () { ask(q); }); cq.appendChild(b); });
  }
  function updWa() {
    var u = hist.filter(function (h) { return h.role === "user"; }).map(function (h) { return h.content; }).join(". ");
    waBtn.href = waLink("Здравствуйте! Интересует ремонт квартиры." + (u ? " " + u.slice(0, 600) : ""));
  }
  function ask(text) {
    text = String(text || "").trim(); if (!text || busy) return;
    add("u", text); hist.push({ role: "user", content: text }); cq.innerHTML = ""; updWa();
    var local = kb(text);
    if (local && local.instant) return say(local.a, local.q);
    if (!apiOk) return say((local || FALLBACK).a, (local || FALLBACK).q);
    busy = true; var t = dots();
    var ctrl = window.AbortController ? new AbortController() : null, timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 12000);
    fetch("/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ messages: hist.slice(-12), page: location.pathname }), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (j) { if (!j.reply) throw new Error("empty"); clearTimeout(timer); t.remove(); add("b", j.reply); hist.push({ role: "assistant", content: j.reply }); setQuick(local && local.q); updWa(); busy = false; })
      .catch(function () { clearTimeout(timer); t.remove(); apiOk = false; busy = false; var r = local || FALLBACK; say(r.a, r.q); });
  }
  cf.addEventListener("submit", function (e) { e.preventDefault(); var v = ci.value; ci.value = ""; ask(v); });

  /* ---------- база ответов (работает и без ИИ) ---------- */
  var CALL = "Позвоните " + PH + " или нажмите «В WhatsApp» под чатом.";
  var FALLBACK = { a: "Точно ответим после замера. " + CALL + " Расскажите о квартире: новостройка или вторичка, площадь и какой ремонт нужен.", q: ["Сколько стоит ремонт?", "Пройти расчёт"] };
  var KB = [
    { k: ["привет", "здравств", "добрый", "салем", "сәлем"], instant: 1, a: "Здравствуйте! Расскажите о квартире: новостройка или вторичка, площадь и какой ремонт планируете." },
    { k: ["спасибо", "рахмет"], instant: 1, a: "Пожалуйста! Если будут вопросы — " + CALL },
    { k: ["бот", "робот", "живой", "человек"], instant: 1, a: "Я онлайн-помощник сайта. Смету готовит специалист после замера — " + CALL },
    { k: ["пройти расчет", "расчет", "рассчитать", "калькулятор", "квиз"], instant: 1, a: "Ответьте на четыре вопроса в блоке расчёта: /#raschet — ответы уйдут в WhatsApp, и мы подготовим расчёт." },
    { k: ["стоим", "цена", "сколько стоит", "почем", "почём", "прайс", "тенге", "₸", "квадрат", "м2", "м²", "дорого", "бюджет"], a: "Стоимость зависит от площади, вида ремонта и материалов. Пройдите расчёт из четырёх вопросов (/#raschet) или напишите в WhatsApp — после замера подготовим смету, цена фиксируется в договоре.", q: ["Как быстро смета?", "Что входит в под ключ?"] },
    { pri: 2, k: ["под ключ", "что входит", "полный ремонт", "комплекс"], a: "В ремонт под ключ входят электрика, сантехника, стяжка и штукатурка по маякам, потолки, отделка стен, ламинат и плинтусы, гидроизоляция и керамогранит в санузле, двери, уборка мусора. Полный перечень — /remont-pod-klyuch/.", q: ["Сколько стоит ремонт?", "Своя бригада?"] },
    { k: ["черновой", "черновая", "стяжк", "штукатур", "маяк"], a: "Черновой ремонт: электрика, сантехника, стяжка и штукатурка по маякам, перегородки, гидроизоляция. Подробнее — /chernovoy-remont/." },
    { k: ["чистовой", "чистовая", "отделк", "обои", "покраск", "ламинат"], a: "Чистовой ремонт: шпаклёвка, покраска или обои, потолки, ламинат, плинтусы, плитка и двери. Подробнее — /chistovoy-remont/." },
    { k: ["дизайн", "проект"], a: "Делаем ремонт по готовому дизайн-проекту: сложные потолки, скрытый свет, стены под боковой свет, запил плитки под 45 градусов. Подробнее — /dizaynerskiy-remont/." },
    { pri: 2, k: ["санузел", "санузл", "ванн", "туалет", "плитк", "керамогранит"], a: "Ремонт санузла под ключ: сантехника, гидроизоляция, керамогранит на стены и пол, запил под 45 градусов, короб и шумоизоляция стояков. Подробнее — /remont-sanuzla/." },
    { pri: 2, k: ["кухн"], a: "Ремонт кухни: перенос розеток и выводов воды под гарнитур и технику, выравнивание стен, плитка или фартук, потолок и свет. Подробнее — /remont-kuhni/." },
    { k: ["электри", "проводк", "розетк", "щиток"], a: "Электромонтаж: разводка, щиток, розетки, выключатели и точки освещения. Проводку фотографируем до закрытия стен. Подробнее — /elektromontazh/." },
    { k: ["сантех", "труб", "канализ", "инсталляц"], a: "Сантехника: разводка воды и канализации, установка сантехники и инсталляций, шумоизоляция стояков. Подробнее — /santehnika/." },
    { k: ["потолок", "потолк", "натяжн"], a: "Монтируем натяжные потолки и потолки из гипсокартона. Подробнее — /natyazhnye-potolki/." },
    { k: ["смет", "быстро", "срок смет", "когда смет"], a: "Смету и план работ готовим в течение трёх часов после замера." },
    { k: ["срок", "сколько длится", "сколько времени", "как долго"], a: "Срок зависит от площади и вида ремонта. Перед стартом составляем график с датами каждого этапа — его увидите вместе со сметой." },
    { k: ["бригад", "субподряд", "мастер", "кто делает"], a: "Работает своя бригада: электрики, сантехники и отделочники. Без субподрядчиков." },
    { k: ["материал", "закуп", "чек"], a: "Можем закупить материалы по оптовым ценам и показать чеки или работать с вашими материалами." },
    { k: ["гарант"], a: "На все работы даём гарантию, условия прописываем в договоре." },
    { k: ["договор", "фиксир", "не изменится", "подорож"], a: "Смета и объём работ фиксируются в договоре. Стоимость не меняется без вашего согласия." },
    { k: ["контрол", "приемк", "приёмк", "фото"], a: "Вы принимаете каждый этап, а скрытые работы — электрику и сантехнику — мы фотографируем до отделки." },
    { k: ["замер", "выезд", "район", "есиль", "левый берег", "правый берег", "сарыарк", "байконур", "байконыр", "нура", "алматин"], a: "Выезжаем на замер в любой район Астаны: Есиль, Алматы, Сарыарка, Байконыр и Нура. Договоритесь о времени: " + PH + "." },
    { k: ["новостро", "черновой отдел", "белая коробк", "вторичк", "вторичн", "старый фонд"], a: "Ремонтируем и новостройки, и вторичное жильё. В новостройке обычно начинаем с черновых работ, во вторичке — с демонтажа. Детали уточним на замере." },
    { k: ["коммерч", "офис", "магазин", "помещени"], a: "Про ремонт коммерческого помещения уточните по телефону " + PH + " — расскажите о площади и задаче." },
    { k: ["оплат", "kaspi", "каспи", "рассроч", "наличн", "этапам оплат"], a: "Порядок оплаты прописываем в договоре — уточните на замере или по телефону " + PH + "." },
    { k: ["номер", "телефон", "контакт", "whatsapp", "ватсап", "позвон"], instant: 1, a: "Телефон и WhatsApp: " + PH + ". Кнопки «Позвонить» и «В WhatsApp» — под чатом." },
  ];
  function kb(text) {
    var t = " " + text.toLowerCase().replace(/ё/g, "е") + " ", best = null, sc = 0;
    KB.forEach(function (it) { var s = 0; it.k.forEach(function (k) { if (t.indexOf(k.replace(/ё/g, "е")) > -1) s += k.length; }); s *= it.pri || 1; if (s > sc) { sc = s; best = it; } });
    return best ? { a: best.a, q: best.q, instant: best.instant } : null;
  }
})();
