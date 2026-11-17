(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var CFG = window.__C || {};
  var WA_BASE = "https://wa.me/" + CFG.wa + "?text=";

  /* ---------- конверсии: ссылки tel: и wa.me получают onclick при сборке; здесь — форма и ссылки, созданные скриптом ---------- */
  function conv() { if (typeof window.gtag_report_conversion === "function") window.gtag_report_conversion(); }

  /* ---------- меню-панель ---------- */
  var drawer = $("#drawer"), burger = $(".burger");
  if (drawer && burger) {
    var shut = function (focus) { drawer.hidden = true; burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; if (focus) burger.focus(); };
    burger.addEventListener("click", function () { drawer.hidden = false; burger.setAttribute("aria-expanded", "true"); document.body.style.overflow = "hidden"; $("[data-close]", drawer).focus(); });
    $("[data-close]", drawer).addEventListener("click", function () { shut(true); });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", function () { shut(false); }); });
    drawer.addEventListener("click", function (e) { if (e.target === drawer) shut(true); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !drawer.hidden) shut(true); });
  }

  /* ---------- выпадающее меню «Услуги»: наведение, фокус и кнопка для касания ---------- */
  $$(".dd").forEach(function (dd) {
    var b = $(".dd-b", dd);
    b.addEventListener("click", function (e) { e.stopPropagation(); var on = !dd.classList.contains("on"); dd.classList.toggle("on", on); b.setAttribute("aria-expanded", on ? "true" : "false"); });
    document.addEventListener("click", function (e) { if (!dd.contains(e.target)) { dd.classList.remove("on"); b.setAttribute("aria-expanded", "false"); } });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") { dd.classList.remove("on"); b.setAttribute("aria-expanded", "false"); } });
  });

  /* ---------- выбор вида ремонта: вкладки (мышь, касание, стрелки) ---------- */
  $$("[data-tabs]").forEach(function (box) {
    var tabs = $$('[role="tab"]', box);
    var sel = function (t, focus) {
      tabs.forEach(function (x) {
        var on = x === t, p = document.getElementById(x.getAttribute("aria-controls"));
        x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1; if (p) p.classList.toggle("on", on);
      });
      if (focus) t.focus();
      if (t.scrollIntoView && window.innerWidth < 1024) { var l = t.parentNode; l.scrollTo({ left: t.offsetLeft - 16, behavior: "smooth" }); }
    };
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { sel(t); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, n = null;
        if (k === "ArrowRight" || k === "ArrowDown") n = tabs[(i + 1) % tabs.length];
        if (k === "ArrowLeft" || k === "ArrowUp") n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (n) { e.preventDefault(); sel(n, true); }
      });
    });
  });

  /* ---------- форма-расчёт: по одному вопросу, ответы уходят в WhatsApp ---------- */
  var qz = $("#qz");
  if (qz) {
    var steps = $$(".qs", qz), nav = $(".qz-nav", qz), prev = $("[data-prev]", qz), next = $("[data-next]", qz), bar = $(".qz-bar i", qz), at = 0;
    var el = qz.elements;
    
    var show = function (i, focus) {
      at = Math.max(0, Math.min(steps.length - 1, i));
      steps.forEach(function (s, k) { s.classList.toggle("on", k === at); });
      prev.disabled = at === 0;
      next.hidden = at === steps.length - 1;
      nav.style.justifyContent = at === steps.length - 1 ? "flex-start" : "";
      bar.style.width = Math.round(at / (steps.length - 1) * 100) + "%";
      if (focus) { var f = $("input:checked", steps[at]) || $("input, textarea", steps[at]); if (f && window.innerWidth > 767) f.focus({ preventScroll: true }); }
    };
    var keyAt = 0;   /* стрелки на клавиатуре тоже выбирают ответ — тогда не листаем, листает «Дальше» */
    qz.addEventListener("keydown", function (e) { if (/^Arrow/.test(e.key)) keyAt = Date.now(); });
    $$('input[type="radio"]', qz).forEach(function (r) {
      r.addEventListener("click", function () { if (Date.now() - keyAt < 300) return; var i = steps.indexOf(r.closest(".qs")); setTimeout(function () { if (at === i) show(i + 1, true); }, 220); });
    });
    prev.addEventListener("click", function () { show(at - 1, true); });
    next.addEventListener("click", function () { show(at + 1, true); });
    show(0, false); qz.classList.add("go");
    var val = function (n) { var r = $('input[name="' + n + '"]:checked', qz); return r ? r.value : "—"; };
    qz.addEventListener("submit", function (e) {
      e.preventDefault();
      var ph = el.phone.value.replace(/\D/g, "");
      if (ph.length < 10) { show(steps.length - 1, false); el.phone.setCustomValidity("Укажите номер телефона: не меньше 10 цифр"); el.phone.reportValidity(); return; }
      el.phone.setCustomValidity("");
      var t = "Здравствуйте! Хочу рассчитать ремонт." +
        "\nОбъект: " + val("obj") + "\nРемонт: " + val("vid") + "\nПлощадь: " + val("pl") + "\nРайон: " + val("ray") +
        (el.desc.value.trim() ? "\nЗадача: " + el.desc.value.trim() : "") +
        "\nИмя: " + (el.name.value.trim() || "—") + "\nТелефон: " + el.phone.value.trim() +
        (qz.dataset.ctx ? "\nСтраница: " + qz.dataset.ctx : "");
      conv();
      window.open(WA_BASE + encodeURIComponent(t), "_blank", "noopener");
      if (!$(".qz-ok", qz)) { var ok = document.createElement("p"); ok.className = "qz-ok full"; ok.setAttribute("role", "status"); ok.textContent = "Открыли WhatsApp — отправьте сообщение, и мастер свяжется с вами."; $(".qs-f", qz).appendChild(ok); }
    });
    el.phone.addEventListener("input", function () { el.phone.setCustomValidity(""); });
  }

  /* ---------- плавающие кнопки: назад, наверх ---------- */
  var top = $("[data-top]"), back = $("[data-back]");
  var onScroll = function () { if (top) top.hidden = window.scrollY < 600; };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  if (top) top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  if (back) {
    var same = document.referrer && document.referrer.indexOf(location.origin) === 0;
    back.hidden = location.pathname === "/" && !same;
    back.addEventListener("click", function (e) { if (same && history.length > 1) { e.preventDefault(); history.back(); } });
  }

  /* ---------- онлайн-консультант: окно строится при первом открытии; /api/chat (ИИ), без ключа — встроенный автоответчик.
     Услуги и ответы — /assets/chat.json. ИИ отмечает услуги кодами [[slug]] — под ответом появляются ссылки ---------- */
  var chat, list, flo = $(".flo"), hist = [], SV = [], CT = {}, loaded = null;
  var loadData = function () {
    if (!loaded) loaded = fetch("/assets/chat.json").then(function (r) { return r.json(); })
      .then(function (d) { SV = d.sv || []; CT = d.t || {}; return SV; }).catch(function () { loaded = null; return SV; });
    return loaded;
  };
  var ct = function (k, o) { return String(CT[k] || "").replace(/\{(\w+)\}/g, function (m, x) { return o && o[x] != null ? o[x] : m; }); };
  var FB = [
    [/смет|расч[её]т|замер/i, "smeta"], [/цен|стоим|сколько|прайс|тенге|₸|бюджет|дорого/i, "price"], [/срок|долго|сколько времени|дней|месяц|недел|когда законч/i, "srok"],
    [/материал|закуп|чек/i, "mat"], [/гарант/i, "gar"], [/бригад|субподряд|мастер|кто дела/i, "team"], [/контрол|приемк|приёмк|этап|фото|отч[её]т/i, "ctrl"],
    [/район|есиль|нура|сарыарк|байконыр|алматы|левый|правый|берег|выезж|пригород/i, "area"], [/портфол|работы посмотр|фото работ|примеры|ваши работы/i, "pf"]
  ];
  var scroll = function () { list.scrollTop = list.scrollHeight; };
  var add = function (t, who) { var d = document.createElement("div"); d.className = "msg " + (who || ""); d.textContent = t; list.appendChild(d); scroll(); return d; };
  var lastQ = function () { for (var i = hist.length - 1; i >= 0; i--) if (hist[i].role === "user") return hist[i].content; return ""; };
  var findSv = function (q) { var low = q.toLowerCase(); return SV.filter(function (s) { return new RegExp(s.k, "i").test(low); }); };
  var bySlug = function (x) { for (var i = 0; i < SV.length; i++) if (SV[i].s === x) return SV[i]; return null; };
  /* под каждым ответом: ссылки на упомянутые услуги + «Позвонить» и «В WhatsApp» */
  var actions = function (svs) {
    var q = lastQ(), box = document.createElement("div"); box.className = "msg-a";
    (svs || []).slice(0, 3).forEach(function (s) { var a = document.createElement("a"); a.className = "sv"; a.href = s.u; a.textContent = s.n; box.appendChild(a); });
    var tel = document.createElement("a"); tel.href = "tel:" + CFG.tel; tel.textContent = ct("call") || "Позвонить";
    var w = document.createElement("a"); w.href = WA_BASE + encodeURIComponent(CFG.hello + (q ? "\n" + (ct("q") || "Вопрос") + ": " + q : "")); w.target = "_blank"; w.rel = "noopener"; w.textContent = ct("wa") || "В WhatsApp";
    [tel, w].forEach(function (a) { a.addEventListener("click", function () { conv(); }); box.appendChild(a); });
    list.appendChild(box); scroll();
  };
  var pickSv = function (t) {
    var out = [], m, re = /\[\[([a-z0-9-]+)\]\]/g;
    while ((m = re.exec(t))) { var s = bySlug(m[1]); if (s && out.indexOf(s) < 0) out.push(s); }
    return out;
  };
  var strip = function (t) { return t.replace(/\s*\[\[[a-z0-9-]*\]\]/g, "").replace(/[ \t]+$/gm, "").trim(); };
  var local = function (q) {
    for (var j = 0; j < FB.length; j++) if (FB[j][0].test(q)) return { t: ct(FB[j][1]), s: findSv(q) };
    var hit = findSv(q);
    if (hit.length) return { t: ct("svc", { n: hit[0].n, d: hit[0].d.toLowerCase() }), s: hit };
    return { t: ct("def"), s: [] };
  };
  var reply = function (t, svs) { add(t); hist.push({ role: "assistant", content: t }); actions(svs); };
  var ask = function (q) {
    q = (q || "").trim(); if (!q) return;
    add(q, "u"); hist.push({ role: "user", content: q });
    var w = add(ct("typing") || "…", "t");
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    var fallback = function () { clearTimeout(to); loadData().then(function () { w.remove(); var a = local(q); reply(a.t, a.s); }); };
    Promise.all([loadData(), fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: hist.slice(-12), page: location.pathname }), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })])
      .then(function (res) {
        var d = res[1]; if (!d || !d.text) throw 0;
        clearTimeout(to); w.remove();
        var svs = pickSv(d.text); if (!svs.length) svs = findSv(q);
        reply(strip(d.text) || ct("def"), svs);
      })
      .catch(fallback);
  };
  var closeChat = function () { chat.hidden = true; if (flo) flo.hidden = false; var b = $("[data-chat]"); if (b) b.focus(); };
  var buildChat = function () {
    var t = $("#chat-t"); if (!t) return false;
    document.body.appendChild(t.content.cloneNode(true));
    chat = $("#chat"); list = $(".chat-l", chat);
    $("[data-chat-x]", chat).addEventListener("click", closeChat);
    $(".chat-f", chat).addEventListener("submit", function (e) { e.preventDefault(); var i = this.elements.q; ask(i.value); i.value = ""; });
    $$(".chat-q button", chat).forEach(function (b) { b.addEventListener("click", function () { ask(b.textContent); }); });
    $(".chat-w", chat).addEventListener("click", function () { conv(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && chat && !chat.hidden) closeChat(); });
    loadData().then(function () { add(ct("hi") || "Здравствуйте! Чем помочь?"); });
    return true;
  };
  var openChat = function () {
    if (!chat && !buildChat()) return;
    chat.hidden = false; if (flo) flo.hidden = true;
    setTimeout(function () { var i = $("input", chat); if (i && window.innerWidth > 767) i.focus(); }, 50);
  };
  $$("[data-chat]").forEach(function (b) { b.addEventListener("click", openChat); });
  /* ---------- каталог услуг: вкладки-фильтры по категориям ---------- */
  $$("[data-cat]").forEach(function (cat) {
    var tabBtns = $$(".tabs button", cat), groups = $$(".cg", cat);
    tabBtns.forEach(function (b) {
      b.addEventListener("click", function () {
        var f = b.getAttribute("data-f");
        tabBtns.forEach(function (x) { x.setAttribute("aria-selected", x === b ? "true" : "false"); });
        cat.classList.toggle("f", f !== "all");
        groups.forEach(function (g) { g.classList.toggle("on", g.getAttribute("data-c") === f); });
      });
    });
  });

  /* ---------- портфолио: просмотр всех фото объекта ---------- */
  var lb, lbImg, lbCap, lbList = [], lbAt = 0, lbTitle = "", lbFrom = null;
  var lbShow = function (i) { lbAt = (i + lbList.length) % lbList.length; lbImg.src = lbList[lbAt]; lbImg.alt = lbTitle; lbCap.textContent = lbTitle + (lbList.length > 1 ? ", фото " + (lbAt + 1) + " из " + lbList.length : ""); };
  var lbClose = function () { lb.hidden = true; document.body.style.overflow = ""; if (lbFrom) lbFrom.focus(); };
  var lbOpen = function (btn) {
    try { lbList = JSON.parse(btn.getAttribute("data-lb")) || []; } catch (e) { lbList = []; }
    if (!lbList.length) return;
    if (!lb) {
      var t = $("#lb-t"); if (!t) return;
      document.body.appendChild(t.content.cloneNode(true));
      lb = $("#lb"); lbImg = $("img", lb); lbCap = $("figcaption", lb);
      $("[data-lb-x]", lb).addEventListener("click", lbClose);
      $("[data-lb-p]", lb).addEventListener("click", function () { lbShow(lbAt - 1); });
      $("[data-lb-n]", lb).addEventListener("click", function () { lbShow(lbAt + 1); });
      lb.addEventListener("click", function (e) { if (e.target === lb) lbClose(); });
      document.addEventListener("keydown", function (e) {
        if (!lb || lb.hidden) return;
        if (e.key === "Escape") lbClose(); else if (e.key === "ArrowLeft") lbShow(lbAt - 1); else if (e.key === "ArrowRight") lbShow(lbAt + 1);
      });
      var sx = 0;
      lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
      lb.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) lbShow(lbAt + (dx < 0 ? 1 : -1)); });
    }
    lbFrom = btn; lbTitle = btn.getAttribute("data-t") || "";
    var many = lbList.length > 1;
    $("[data-lb-p]", lb).hidden = !many; $("[data-lb-n]", lb).hidden = !many;
    lb.hidden = false; document.body.style.overflow = "hidden"; lbShow(0); $("[data-lb-x]", lb).focus();
  };
  $$("[data-lb]").forEach(function (b) { b.addEventListener("click", function () { lbOpen(b); }); });
})();
