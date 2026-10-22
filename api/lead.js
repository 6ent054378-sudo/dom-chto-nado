"use strict";

/*
 * Приём заявок с сайта (Vercel Serverless Function, адрес: /api/lead).
 *
 * Переменные окружения (Vercel: Project Settings -> Environment Variables):
 *   TG_BOT_TOKEN     токен бота от @BotFather
 *   TG_CHAT_ID       id чата или канала, куда бот пишет заявки
 *   LEAD_WEBHOOK_URL необязательно: адрес CRM или другого приёмника, получит тот же JSON
 *
 * Если не задано ни одного получателя, функция отвечает 503 и сайт покажет номер телефона.
 */

const MAX_BODY = 20000;
const WINDOW_MS = 60 * 1000;
const MAX_PER_WINDOW = 5;
const hits = new Map();

function tooMany(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter(function (t) {
    return now - t < WINDOW_MS;
  });
  list.push(now);
  hits.set(ip, list);
  if (hits.size > 500) hits.clear();
  return list.length > MAX_PER_WINDOW;
}

function esc(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .slice(0, 500);
}

function digits(value) {
  return String(value || "").replace(/\D/g, "");
}

function buildText(lead, ip) {
  const lines = [];
  lines.push("<b>Новая заявка с сайта «Дом что надо»</b>");
  lines.push("");
  lines.push("Имя: " + (esc(lead.name) || "не указано"));
  lines.push("Телефон: " + esc(lead.phone));
  lines.push("Связь: " + (esc(lead.channel) || "Телефон"));
  if (lead.from) lines.push("Форма: " + esc(lead.from));

  const answers = lead.answers && typeof lead.answers === "object" ? lead.answers : {};
  const keys = Object.keys(answers).slice(0, 20);
  if (keys.length) {
    lines.push("");
    lines.push("<b>Ответы квиза</b>");
    keys.forEach(function (k) {
      lines.push(esc(k) + ": " + esc(answers[k]));
    });
  }

  const utm = lead.utm && typeof lead.utm === "object" ? lead.utm : {};
  const utmKeys = Object.keys(utm).slice(0, 10);
  if (utmKeys.length) {
    lines.push("");
    lines.push("<b>Источник</b>");
    utmKeys.forEach(function (k) {
      lines.push(esc(k) + ": " + esc(utm[k]));
    });
  }

  lines.push("");
  lines.push("Страница: " + esc(lead.page));
  lines.push("Время: " + esc(lead.sentAt));
  lines.push("IP: " + esc(ip));
  return lines.join("\n");
}

async function sendTelegram(text) {
  const token = process.env.TG_BOT_TOKEN;
  const chat = process.env.TG_CHAT_ID;
  if (!token || !chat) return null;
  const response = await fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chat,
      text: text,
      parse_mode: "HTML",
      disable_web_page_preview: true,
    }),
  });
  return response.ok;
}

async function sendWebhook(lead) {
  const url = process.env.LEAD_WEBHOOK_URL;
  if (!url) return null;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead),
  });
  return response.ok;
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method" });
  }

  let lead = req.body;
  if (typeof lead === "string") {
    if (lead.length > MAX_BODY) return res.status(413).json({ ok: false, error: "size" });
    try {
      lead = JSON.parse(lead);
    } catch (e) {
      return res.status(400).json({ ok: false, error: "json" });
    }
  }
  if (!lead || typeof lead !== "object") {
    return res.status(400).json({ ok: false, error: "body" });
  }

  // ловушка для ботов: настоящий посетитель это поле не заполняет
  if (lead.website) return res.status(200).json({ ok: true });

  if (digits(lead.phone).length !== 11) {
    return res.status(422).json({ ok: false, error: "phone" });
  }

  const forwarded = String(req.headers["x-forwarded-for"] || "");
  const ip = forwarded.split(",")[0].trim() || "unknown";
  if (tooMany(ip)) return res.status(429).json({ ok: false, error: "rate" });

  const results = [];
  try {
    results.push(await sendTelegram(buildText(lead, ip)));
    results.push(await sendWebhook(lead));
  } catch (e) {
    return res.status(502).json({ ok: false, error: "upstream" });
  }

  const configured = results.filter(function (r) {
    return r !== null;
  });
  if (!configured.length) return res.status(503).json({ ok: false, error: "not_configured" });
  if (!configured.some(Boolean)) return res.status(502).json({ ok: false, error: "upstream" });
  return res.status(200).json({ ok: true });
};
