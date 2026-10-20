"use strict";

/*
 * idealhome77 — отправка заявок.
 *
 * Что настроить перед запуском:
 *   1. WEBHOOK_URL — адрес, принимающий заявку (Telegram-бот, CRM, Cloudflare Worker).
 *      Пока он пустой, сайт работает в демо-режиме: заявка собирается, показывается
 *      экран «Спасибо», но никуда не уходит. Пустые заявки не теряются молча.
 *   2. YANDEX_METRIKA_ID — номер счётчика Яндекс.Метрики (0 = не подключён).
 *   3. ym_client_id в целях Метрики формируется автоматически.
 *
 * JSON нагрузки: name, phone, channel, answers, utm, page, sentAt.
 */

const WEBHOOK_URL = "";
const YANDEX_METRIKA_ID = 0;
const SUCCESS_TITLE = "Спасибо! Заявка отправлена.";
const SUCCESS_TEXT =
  "Инженер idealhome77 перезвонит в течение 15 минут в рабочее время и пришлёт предварительную смету.";

document.addEventListener("DOMContentLoaded", function () {
  const UTM_KEYS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
  ];

  function readUtmFromUrl() {
    const params = new URLSearchParams(window.location.search || "");
    const utm = {};
    UTM_KEYS.forEach(function (k) {
      const v = params.get(k);
      if (v !== null && v !== "") utm[k] = v;
    });
    return utm;
  }

  function readUtmFromSessionStorage() {
    const utm = {};
    UTM_KEYS.forEach(function (k) {
      const v = sessionStorage.getItem(k);
      if (v !== null && v !== "") utm[k] = v;
    });
    return utm;
  }

  function persistUtmToSessionStorage(utm) {
    if (!utm) return;
    UTM_KEYS.forEach(function (k) {
      if (utm[k]) sessionStorage.setItem(k, utm[k]);
    });
  }

  function getUtmForSubmit() {
    const fromUrl = readUtmFromUrl();
    persistUtmToSessionStorage(fromUrl);
    return Object.assign({}, readUtmFromSessionStorage(), fromUrl);
  }

  persistUtmToSessionStorage(readUtmFromUrl());

  function getInputsNumbersValue(input) {
    return input.value.replace(/\D/g, "");
  }

  function validatePhoneNumber(input) {
    return getInputsNumbersValue(input).length === 11;
  }

  function formValidate(form) {
    let error = 0;
    const formRequired = form.querySelectorAll("._required");
    deleteErrorClassOnInputs(formRequired);
    for (let index = 0; index < formRequired.length; index++) {
      const input = formRequired[index];
      if (input.getAttribute("type") === "checkbox" && input.checked === false) {
        formAddError(input);
        error++;
      } else if (input.value === "") {
        formAddError(input);
        error++;
      }
    }
    return error;
  }

  function deleteErrorClassOnInputs(inputs) {
    for (let i = 0; i < inputs.length; i++) formRemoveError(inputs[i]);
  }

  function formAddError(input) {
    input.parentElement.classList.add("_error");
    input.classList.add("_error");
  }

  function formRemoveError(input) {
    input.parentElement.classList.remove("_error");
    input.classList.remove("_error");
  }

  function getSubmitText(el) {
    if (!el) return "";
    if (el.tagName === "INPUT") return el.value != null ? el.value : "";
    return el.innerHTML != null ? el.innerHTML : "";
  }

  function setSubmitLoading(el) {
    if (!el) return;
    if (el.tagName === "INPUT") {
      el.value = "Отправка формы...";
    } else {
      el.innerHTML = "Отправка формы...";
    }
    el.disabled = true;
  }

  function resetSubmit(el, originalText) {
    if (!el) return;
    if (el.tagName === "INPUT") {
      el.value = originalText;
    } else {
      el.innerHTML = originalText;
    }
    el.disabled = false;
  }

  function showSuccess(form) {
    const wrap = document.createElement("div");
    wrap.className = "form__success";
    wrap.innerHTML =
      '<div class="form__success-icon">' +
      '<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">' +
      '<path d="M5 14.5L11 20.5L23 8" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg></div>" +
      '<p class="form__success-title">' + SUCCESS_TITLE + "</p>" +
      '<p class="form__success-text">' + SUCCESS_TEXT + "</p>";
    form.innerHTML = "";
    form.appendChild(wrap);
  }

  function collectAnswers(form) {
    const answers = {};
    form.querySelectorAll("input[type=radio]:checked, select").forEach(function (el) {
      if (!el.name) return;
      if (el.type === "radio") {
        answers[el.name] = el.value;
      } else if (el.tagName === "SELECT") {
        answers[el.name] = el.value;
      }
    });
    return answers;
  }

  document.addEventListener("submit", function (event) {
    const form = event.target;
    if (!form || !form.classList.contains("form-submit")) return;
    event.preventDefault();

    const phoneInput = form.querySelector('input[type="tel"]');
    if (phoneInput && !validatePhoneNumber(phoneInput)) {
      formAddError(phoneInput);
      alert("Пожалуйста, введите полный номер телефона (+7 (XXX) XXX-XX-XX)");
      return;
    }

    if (formValidate(form) !== 0) {
      alert("Заполните обязательные поля");
      return;
    }

    const btnSubmit = form.querySelector('button[type="submit"]');
    const originalButtonText = getSubmitText(btnSubmit);
    setSubmitLoading(btnSubmit);
    form.classList.add("_sending");

    const formData = new FormData(form);
    formData.append(
      "newToken",
      Date.now().toString(36) + Math.random().toString(36).substr(2),
    );

    const utm = getUtmForSubmit();
    UTM_KEYS.forEach(function (k) {
      if (utm[k]) formData.append(k, utm[k]);
    });

    const payload = {
      name: formData.get("name") || "",
      phone: formData.get("phone") || "",
      channel: formData.get("messenger") || "Телефон",
      from: formData.get("from") || "",
      answers: collectAnswers(form),
      utm: utm,
      page: window.location.pathname + window.location.search,
      sentAt: new Date().toISOString(),
    };

    function finishOk() {
      form.reset();
      showSuccess(form);
    }

    // Демо-режим: бэкенд не подключён — показываем подтверждение, данные в консоль
    if (!WEBHOOK_URL) {
      console.log("[idealhome77] WEBHOOK_URL не задан — заявка не отправлена:", payload);
      window.setTimeout(finishOk, 400);
      return;
    }

    fetch(WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return finishOk();
      })
      .catch(function (error) {
        console.error("Ошибка отправки заявки:", error);
        alert("Не удалось отправить заявку. Позвоните нам: +7 495 120-77-77");
        resetSubmit(btnSubmit, originalButtonText);
      })
      .finally(function () {
        form.classList.remove("_sending");
      });
  });
});
