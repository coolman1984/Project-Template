/* One-page application.
 * It displays approved results. It never recalculates a trusted number:
 * every value here comes from dashboard.json exactly as the engine proved it.
 */
(function () {
  "use strict";

  var KEY = new URLSearchParams(window.location.search).get("k") || "";
  var state = { lang: "en", data: null, dashboard: null, polling: null };

  var T = {
    en: {
      skip: "Skip to content", print: "Print", process: "Process",
      filesHeading: "1. Add your files", resultHeading: "2. Your result",
      proofHeading: "3. Proof the numbers are right", insightsHeading: "Highlights",
      attentionHeading: "Rows needing attention", historyHeading: "Previous runs",
      dropzone: "Drag your Excel files here, or press to choose them",
      technicalDetail: "Technical detail (for support)", download: "Download as CSV",
      whereFrom: "Where did the data come from?", emptyHeading: "No result yet",
      emptyBody: "Add your files above and press Process.",
      expected: "This report expects: ", noFiles: "No files added yet.",
      needFiles: "Add at least one file first.", working: "Working…",
      rowsRead: "Rows read", rowsAccepted: "Rows used", rowsAttention: "Rows needing attention",
      rowsScope: "Rows out of scope", finished: "Finished", remove: "Remove",
      safe: "Your previous results were not changed.",
      check: "Check", expectedCol: "Expected", actual: "Actual", difference: "Difference",
      status: "Status", file: "File", row: "Row", reason: "Reason", value: "Value",
      run: "Run", when: "When", used: "Rows used", message: "Result",
      attentionNote: "These rows were not used in the totals. Fix them in the source file and process again.",
      source: "Source", hash: "Fingerprint", size: "Size",
      idle: "Ready", footer: "Everything runs on this computer. Nothing is sent anywhere."
    },
    ar: {
      skip: "تخطي إلى المحتوى", print: "طباعة", process: "معالجة",
      filesHeading: "١. أضف ملفاتك", resultHeading: "٢. النتيجة",
      proofHeading: "٣. إثبات صحة الأرقام", insightsHeading: "أبرز النقاط",
      attentionHeading: "صفوف تحتاج مراجعة", historyHeading: "التشغيلات السابقة",
      dropzone: "اسحب ملفات إكسل هنا، أو اضغط لاختيارها",
      technicalDetail: "تفاصيل فنية (للدعم)", download: "تنزيل CSV",
      whereFrom: "من أين جاءت البيانات؟", emptyHeading: "لا توجد نتيجة بعد",
      emptyBody: "أضف ملفاتك بالأعلى ثم اضغط معالجة.",
      expected: "هذا التقرير يتوقع: ", noFiles: "لم تتم إضافة ملفات بعد.",
      needFiles: "أضف ملفاً واحداً على الأقل.", working: "جارٍ العمل…",
      rowsRead: "الصفوف المقروءة", rowsAccepted: "الصفوف المستخدمة",
      rowsAttention: "صفوف تحتاج مراجعة", rowsScope: "صفوف خارج النطاق",
      finished: "انتهى", remove: "إزالة",
      safe: "لم تتغير نتائجك السابقة.",
      check: "الفحص", expectedCol: "المتوقع", actual: "الفعلي", difference: "الفرق",
      status: "الحالة", file: "الملف", row: "الصف", reason: "السبب", value: "القيمة",
      run: "التشغيل", when: "الوقت", used: "الصفوف المستخدمة", message: "النتيجة",
      attentionNote: "لم تُستخدم هذه الصفوف في المجاميع. صححها في الملف المصدر ثم أعد المعالجة.",
      source: "المصدر", hash: "البصمة", size: "الحجم",
      idle: "جاهز", footer: "كل شيء يعمل على هذا الجهاز. لا يتم إرسال أي شيء."
    }
  };

  function t(key) { return (T[state.lang] && T[state.lang][key]) || T.en[key] || key; }
  function $(id) { return document.getElementById(id); }
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text !== undefined && text !== null) { setText(node, text); }
    return node;
  }

  /* A page in Arabic still shows English text - a metric title, a file name, a
   * message the engine wrote. dir="auto" lets the browser decide the direction
   * of each individual string, so a full stop never jumps to the wrong end. */
  function setText(node, text) {
    node.textContent = text === null || text === undefined ? "" : String(text);
    node.setAttribute("dir", "auto");
    return node;
  }
  function clear(node) { while (node.firstChild) { node.removeChild(node.firstChild); } }

  function _set(id, text) { return setText($(id), text); }

  function api(path, options) {
    var separator = path.indexOf("?") === -1 ? "?" : "&";
    return fetch(path + separator + "k=" + encodeURIComponent(KEY), options || {})
      .then(function (response) {
        if (!response.ok && response.status !== 409) { throw new Error("HTTP " + response.status); }
        return response.json();
      });
  }

  /* ---------- formatting (display only) ---------- */
  function formatValue(value, format, unit) {
    if (value === null || value === undefined) { return "—"; }
    var locale = state.lang === "ar" ? "ar-EG" : "en-US";
    var text;
    if (format === "money") {
      text = Number(value).toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    } else if (format === "integer") {
      text = Number(value).toLocaleString(locale, { maximumFractionDigits: 0 });
    } else if (format === "percent") {
      text = Number(value).toLocaleString(locale, { maximumFractionDigits: 1 }) + "%";
    } else if (typeof value === "number") {
      text = Number(value).toLocaleString(locale, { maximumFractionDigits: 2 });
    } else {
      return String(value);
    }
    return unit ? text + " " + unit : text;
  }

  function formatWhen(value) {
    return value ? String(value).replace("T", " ") : "";
  }

  function formatBytes(bytes) {
    if (bytes < 1024) { return bytes + " B"; }
    if (bytes < 1048576) { return (bytes / 1024).toFixed(0) + " KB"; }
    return (bytes / 1048576).toFixed(1) + " MB";
  }

  /* ---------- files ---------- */
  function renderFiles() {
    var list = $("file-list");
    clear(list);
    var files = (state.data && state.data.inbox) || [];
    if (!files.length) {
      list.appendChild(el("li", "muted", t("noFiles")));
    } else {
      files.forEach(function (file) {
        var item = el("li");
        item.appendChild(el("span", null, file.name + " · " + formatBytes(file.size_bytes)));
        var button = el("button", "remove", "✕");
        button.type = "button";
        button.setAttribute("aria-label", t("remove") + " " + file.name);
        button.addEventListener("click", function () {
          api("/api/files/remove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: file.name })
          }).then(function (result) { state.data.inbox = result.inbox; renderFiles(); });
        });
        item.appendChild(button);
        list.appendChild(item);
      });
    }
    var expected = (state.data && state.data.expected_files) || [];
    _set("files-expected", t("expected") + expected.map(function (source) {
      return source.title + " (" + source.patterns.join(", ") + ")";
    }).join(" · "));
    $("process-button").disabled = !files.length;
    _set("process-hint", files.length ? "" : t("needFiles"));
  }

  function uploadFiles(fileList) {
    var files = Array.prototype.slice.call(fileList);
    if (!files.length) { return; }
    Promise.all(files.map(function (file) {
      return new Promise(function (resolve) {
        var reader = new FileReader();
        reader.onload = function () {
          var base64 = String(reader.result).split(",")[1] || "";
          resolve({ name: file.name, content_base64: base64 });
        };
        reader.readAsDataURL(file);
      });
    })).then(function (payload) {
      return api("/api/files", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ files: payload })
      });
    }).then(function (result) {
      state.data.inbox = result.inbox;
      renderFiles();
      if (result.errors && result.errors.length) { showError(result.errors[0]); }
    });
  }

  /* ---------- run ---------- */
  function setProgress(progress) {
    var wrap = $("progress-wrap");
    wrap.hidden = !progress.busy && progress.percent === 0;
    $("progress-fill").style.width = progress.percent + "%";
    $("progress-bar").setAttribute("aria-valuenow", String(progress.percent));
    _set("progress-text", progress.busy
      ? progress.percent + "% · " + progress.message
      : (progress.message || ""));
    $("process-button").disabled = progress.busy || !(state.data.inbox || []).length;
  }

  function poll() {
    api("/api/progress").then(function (progress) {
      setProgress(progress);
      if (progress.busy) { return; }
      window.clearInterval(state.polling);
      state.polling = null;
      refresh().then(function () {
        if (progress.result && progress.result.error) { showError(progress.result.error); }
      });
    });
  }

  function process() {
    hideError();
    api("/api/process", { method: "POST", headers: { "Content-Type": "application/json" },
                          body: "{}" })
      .then(function (result) {
        if (!result.started) { _set("process-hint", result.reason || ""); return; }
        setProgress({ busy: true, percent: 1, message: t("working") });
        if (state.polling) { window.clearInterval(state.polling); }
        state.polling = window.setInterval(poll, 700);
      });
  }

  /* ---------- errors ---------- */
  function showError(error) {
    _set("error-heading", error.what_happened || "");
    $("error-safe").textContent = error.trusted_data_safe === false ? "" : t("safe");
    _set("error-action", error.next_action || "");
    _set("error-code", error.support_code || "");
    _set("error-detail", error.detail || "");
    $("error-card").hidden = false;
    $("error-card").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function hideError() { $("error-card").hidden = true; }

  /* ---------- rendering the result ---------- */
  function renderStatus(status, message) {
    var pill = $("status-pill");
    pill.className = "pill pill-" + (status || "idle");
    pill.textContent = status ? status + (message ? "" : "") : t("idle");
  }

  function renderKpis(kpis) {
    var section = $("kpi-section");
    clear(section);
    kpis.forEach(function (kpi) {
      var card = el("div", "kpi");
      card.appendChild(el("div", "title", kpi.title));
      card.appendChild(el("div", "value", formatValue(kpi.value, kpi.format, kpi.unit)));
      if (kpi.subtitle) { card.appendChild(el("div", "muted", kpi.subtitle)); }
      section.appendChild(card);
    });
  }

  function renderChart(chart) {
    var card = el("section", "card");
    card.appendChild(el("h2", null, chart.title));
    var points = chart.points || [];
    if (!points.length) { card.appendChild(el("p", "muted", "—")); return card; }

    var width = 720, barHeight = 26, gap = 10, labelWidth = 150;
    var height = points.length * (barHeight + gap) + 10;
    var max = Math.max.apply(null, points.map(function (p) { return Math.abs(Number(p.value) || 0); })) || 1;

    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 " + width + " " + height);
    svg.setAttribute("class", "chart");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", chart.title);

    points.forEach(function (point, index) {
      var y = index * (barHeight + gap) + 5;
      var value = Number(point.value) || 0;
      var barWidth = Math.max(2, (Math.abs(value) / max) * (width - labelWidth - 120));

      var label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", "0"); label.setAttribute("y", String(y + barHeight * 0.7));
      label.textContent = point.label;
      svg.appendChild(label);

      var rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", String(labelWidth)); rect.setAttribute("y", String(y));
      rect.setAttribute("width", String(barWidth)); rect.setAttribute("height", String(barHeight));
      rect.setAttribute("rx", "4"); rect.setAttribute("class", "bar");
      var title = document.createElementNS("http://www.w3.org/2000/svg", "title");
      title.textContent = point.label + ": " + formatValue(value, chart.format, chart.unit);
      rect.appendChild(title);
      svg.appendChild(rect);

      var valueLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
      valueLabel.setAttribute("x", String(labelWidth + barWidth + 8));
      valueLabel.setAttribute("y", String(y + barHeight * 0.7));
      valueLabel.setAttribute("class", "value-label");
      valueLabel.textContent = formatValue(value, chart.format, chart.unit);
      svg.appendChild(valueLabel);
    });
    card.appendChild(svg);
    card.appendChild(exportLink(chart.id));
    return card;
  }

  function exportLink(metricId) {
    var link = el("a", "ghost", t("download"));
    link.href = "/api/export/" + encodeURIComponent(metricId) + ".csv?k=" + encodeURIComponent(KEY);
    link.setAttribute("download", "");
    return link;
  }

  function renderTable(table) {
    var card = el("section", "card");
    card.appendChild(el("h2", null, table.title));
    var scroll = el("div", "table-scroll");
    var node = el("table");
    var head = el("thead");
    var headRow = el("tr");
    (table.columns || []).forEach(function (column, index) {
      var cell = el("th", isNumericColumn(table, index) ? "number" : null, column);
      headRow.appendChild(cell);
    });
    head.appendChild(headRow);
    node.appendChild(head);
    var body = el("tbody");
    (table.rows || []).forEach(function (row) {
      var tr = el("tr");
      row.forEach(function (value, index) {
        var numeric = typeof value === "number";
        tr.appendChild(el("td", numeric ? "number" : null,
                          numeric ? formatValue(value, "number") : (value === null ? "—" : value)));
      });
      body.appendChild(tr);
    });
    node.appendChild(body);
    scroll.appendChild(node);
    card.appendChild(scroll);
    card.appendChild(exportLink(table.id));
    return card;
  }

  function isNumericColumn(table, index) {
    return (table.rows || []).some(function (row) { return typeof row[index] === "number"; });
  }

  function fillTable(tableId, columns, rows, classFor) {
    var node = $(tableId);
    var head = node.querySelector("thead");
    var body = node.querySelector("tbody");
    clear(head); clear(body);
    var headRow = el("tr");
    columns.forEach(function (column) { headRow.appendChild(el("th", null, column)); });
    head.appendChild(headRow);
    rows.forEach(function (row) {
      var tr = el("tr");
      row.forEach(function (value, index) {
        tr.appendChild(el("td", classFor ? classFor(row, index) : null,
                          value === null || value === undefined ? "—" : value));
      });
      body.appendChild(tr);
    });
  }

  function render() {
    var data = state.dashboard;
    $("empty-state").hidden = !!data;
    $("result").hidden = !data;
    if (!data) { renderStatus(null); return; }

    var title = data.project.title[state.lang] || data.project.title.en || data.project.name;
    document.title = title;
    _set("project-title", title);
    _set("project-purpose", data.project.purpose || "");
    renderStatus(data.run.status);
    _set("run-message", data.run.message || "");

    var facts = $("run-facts");
    clear(facts);
    [[t("rowsRead"), data.run.rows.read], [t("rowsAccepted"), data.run.rows.accepted],
     [t("rowsAttention"), data.run.rows.needs_attention], [t("rowsScope"), data.run.rows.out_of_scope],
     [t("finished"), formatWhen(data.run.finished_at)]].forEach(function (pair) {
      var group = el("div");
      group.appendChild(el("dt", null, pair[0]));
      group.appendChild(el("dd", null, typeof pair[1] === "number"
        ? formatValue(pair[1], "integer") : (pair[1] || "—")));
      facts.appendChild(group);
    });

    renderKpis(data.kpis || []);

    var insights = data.insights || [];
    $("insights-section").hidden = !insights.length;
    var list = $("insights-list");
    clear(list);
    insights.forEach(function (insight) {
      var item = el("li", insight.severity || "info");
      item.appendChild(el("strong", null, insight.title));
      if (insight.body) { item.appendChild(el("span", null, insight.body)); }
      list.appendChild(item);
    });

    var charts = $("charts-section");
    clear(charts);
    (data.charts || []).forEach(function (chart) { charts.appendChild(renderChart(chart)); });

    var tables = $("tables-section");
    clear(tables);
    (data.tables || []).forEach(function (table) { tables.appendChild(renderTable(table)); });

    var attention = data.attention || { total: 0, rows: [] };
    $("attention-section").hidden = !attention.total;
    if (attention.total) {
      _set("attention-note", t("attentionNote") +
        (attention.total > attention.shown
          ? " (" + attention.shown + "/" + attention.total + ")" : ""));
      fillTable("attention-table", [t("file"), t("row"), t("reason")],
        attention.rows.map(function (row) { return [row.file_name, row.excel_row, row.message]; }));
      $("attention-export").href = "/api/export/attention.csv?k=" + encodeURIComponent(KEY);
      $("attention-export").textContent = t("download");
    }

    fillTable("reconciliation-table",
      [t("source"), t("check"), t("expectedCol"), t("actual"), t("difference"), t("status")],
      (data.reconciliation || []).map(function (check) {
        return [check.source_id, check.check, check.expected, check.actual, check.difference,
                check.status];
      }),
      function (row, index) { return index === 5 ? "status-" + row[5] : null; });

    var lineage = $("lineage");
    clear(lineage);
    (data.run.files || []).forEach(function (file) {
      var line = el("p", "mono", file.file_name + " · " + formatBytes(file.size_bytes) +
                    " · " + file.sha256.slice(0, 16) + "…");
      lineage.appendChild(line);
    });

    fillTable("history-table", [t("when"), t("status"), t("used"), t("message")],
      (data.history || []).map(function (run) {
        return [formatWhen(run.finished_at || run.started_at), run.status, run.rows_clean,
                run.message];
      }),
      function (row, index) { return index === 1 ? "status-" + row[1] : null; });
  }

  function applyLanguage() {
    document.documentElement.lang = state.lang;
    document.documentElement.dir = state.lang === "ar" ? "rtl" : "ltr";
    document.querySelectorAll("[data-i18n]").forEach(function (node) {
      node.textContent = t(node.getAttribute("data-i18n"));
    });
    $("lang-toggle").textContent = state.lang === "ar" ? "English" : "العربية";
    $("footer-note").textContent = t("footer");
    renderFiles();
    render();
  }

  function refresh() {
    return api("/api/state").then(function (data) {
      state.data = data;
      state.dashboard = data.dashboard;
      if (!state.userChoseLanguage && data.project && data.project.language) {
        state.lang = data.project.language === "ar" ? "ar" : "en";
      }
      applyLanguage();
      setProgress(data.progress);
      if (data.progress.busy && !state.polling) {
        state.polling = window.setInterval(poll, 700);
      }
    });
  }

  /* ---------- wiring ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    var dropzone = $("dropzone");
    var input = $("file-input");
    dropzone.addEventListener("click", function () { input.click(); });
    dropzone.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); input.click(); }
    });
    ["dragenter", "dragover"].forEach(function (name) {
      dropzone.addEventListener(name, function (event) {
        event.preventDefault(); dropzone.classList.add("over");
      });
    });
    ["dragleave", "drop"].forEach(function (name) {
      dropzone.addEventListener(name, function (event) {
        event.preventDefault(); dropzone.classList.remove("over");
      });
    });
    dropzone.addEventListener("drop", function (event) {
      uploadFiles(event.dataTransfer.files);
    });
    input.addEventListener("change", function () { uploadFiles(input.files); input.value = ""; });
    $("process-button").addEventListener("click", process);
    $("print-button").addEventListener("click", function () { window.print(); });
    $("lang-toggle").addEventListener("click", function () {
      state.lang = state.lang === "ar" ? "en" : "ar";
      state.userChoseLanguage = true;
      applyLanguage();
    });
    refresh();
  });
})();
