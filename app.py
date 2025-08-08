# -*- coding: utf-8 -*-
import os
import json
from flask import Flask, request, jsonify
import requests
from datetime import datetime, date

# ====== Config ======
BOT_TOKEN = os.getenv("BOT_TOKEN")  # REQUIRED: your bot token from BotFather
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "webhook")  # you can change it if you like
STATE_FILE = os.getenv("STATE_FILE", "state.json")   # local JSON storage (ephemeral on free tiers)

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None

app = Flask(__name__)

# ====== Utilities ======
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(data):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def send_message(chat_id: int, text: str, reply_markup=None, parse_mode=None):
    if not TELEGRAM_API:
        return
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        requests.post(f"{TELEGRAM_API}/sendMessage", data=payload, timeout=10)
    except Exception:
        pass

def build_main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "✅ Отметить тренировку", "callback_data": "training_done"}],
            [{"text": "🚶 Отметить шаги (сегодня)", "callback_data": "steps_done"}],
            [{"text": "💧 +250 мл воды", "callback_data": "water:+250"},
             {"text": "💧 +500 мл", "callback_data": "water:+500"}],
            [{"text": "💊 Креатин", "callback_data": "supp:creatine"},
             {"text": "💊 ZMA+D3", "callback_data": "supp:zma"},
             {"text": "💊 Карнитин", "callback_data": "supp:carnitine"}],
        ]
    }

def add_log(chat_id, kind, value):
    data = load_state()
    uid = str(chat_id)
    today = str(date.today())
    user = data.setdefault(uid, {})
    day = user.setdefault(today, {})
    day.setdefault(kind, [])
    day[kind].append(value)
    save_state(data)

def today_summary(chat_id):
    data = load_state()
    uid = str(chat_id)
    today = str(date.today())
    day = data.get(uid, {}).get(today, {})
    if not day:
        return "Сегодня записей пока нет."
    lines = [f"📊 Отчёт за {today}"]
    w = sum(day.get("water_ml", [])) if "water_ml" in day else 0
    steps = len(day.get("steps_done", []))
    tr = len(day.get("training_done", []))
    weight = day.get("weight", [])
    supp = day.get("supp", [])
    if weight:
        lines.append(f"⚖️ Вес: {weight[-1]} кг")
    lines.append(f"💧 Вода: {w} мл")
    lines.append(f"🚶 Отмечено шагов (факт): {steps} раз")
    lines.append(f"🏋️ Тренировки: {tr} раз")
    if supp:
        lines.append("💊 Добавки: " + ", ".join(supp))
    return "\n".join(lines)

# ====== Routes ======
@app.route("/", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "FimiGymTrenBot", "time": datetime.utcnow().isoformat()})

@app.route(f"/{WEBHOOK_PATH}", methods=["POST"])
def telegram_webhook():
    if not BOT_TOKEN:
        return jsonify({"ok": False, "error": "BOT_TOKEN is missing"}), 500

    update = request.get_json(force=True, silent=True) or {}
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = (msg.get("text") or "").strip()

        if text.startswith("/start"):
            welcome = (
                "Привет! Я твой фитнес-бот 🦾\n"
                "Кнопки ниже помогут отмечать воду, шаги, тренировки и добавки.\n\n"
                "Можно слать текстом:\n"
                "• вода 250\n"
                "• вес 88.6\n"
                "• шаги готово\n"
                "• тренировка готово\n"
                "• добавка креатин\n"
                "Команда: /stats — показать отчёт за сегодня."
            )
            send_message(chat_id, welcome, reply_markup=build_main_keyboard())
            return "ok"

        lower = text.lower()

        if lower.startswith("вода"):
            try:
                ml = int(float(lower.split()[1]))
                add_log(chat_id, "water_ml", ml)
                send_message(chat_id, f"💧 Вода записана: +{ml} мл", reply_markup=build_main_keyboard())
            except Exception:
                send_message(chat_id, "Формат: 'вода 250'")
            return "ok"

        if lower.startswith("вес"):
            try:
                kg = float(lower.split()[1].replace(",", "."))
                add_log(chat_id, "weight", kg)
                send_message(chat_id, f"⚖️ Вес записан: {kg} кг", reply_markup=build_main_keyboard())
            except Exception:
                send_message(chat_id, "Формат: 'вес 88.6'")
            return "ok"

        if "шаги" in lower:
            add_log(chat_id, "steps_done", True)
            send_message(chat_id, "🚶 Отмечено: шаги за день ✅", reply_markup=build_main_keyboard())
            return "ok"

        if "трениров" in lower:
            add_log(chat_id, "training_done", True)
            send_message(chat_id, "🏋️ Отмечено: тренировка выполнена ✅", reply_markup=build_main_keyboard())
            return "ok"

        if lower.startswith("добавка"):
            kind = lower.replace("добавка", "").strip()
            add_log(chat_id, "supp", kind or "unknown")
            send_message(chat_id, f"💊 Приём добавки отмечен: {kind}", reply_markup=build_main_keyboard())
            return "ok"

        if lower.startswith("/stats"):
            send_message(chat_id, today_summary(chat_id), reply_markup=build_main_keyboard(), parse_mode="HTML")
            return "ok"

        send_message(chat_id, "Не понял. Нажми кнопку ниже или используй формат: 'вода 250', 'вес 88.6'.",
                     reply_markup=build_main_keyboard())
        return "ok"

    if "callback_query" in update:
        cq = update["callback_query"]
        chat_id = cq["message"]["chat"]["id"]
        data = cq.get("data") or ""

        if data == "training_done":
            add_log(chat_id, "training_done", True)
            send_message(chat_id, "🏋️ Тренировка отмечена ✅", reply_markup=build_main_keyboard())
        elif data == "steps_done":
            add_log(chat_id, "steps_done", True)
            send_message(chat_id, "🚶 Шаги за день отмечены ✅", reply_markup=build_main_keyboard())
        elif data.startswith("water:"):
            try:
                ml = int(data.split(":")[1].replace("+",""))
                add_log(chat_id, "water_ml", ml)
                send_message(chat_id, f"💧 Вода записана: +{ml} мл", reply_markup=build_main_keyboard())
            except Exception:
                send_message(chat_id, "Ошибка записи воды.", reply_markup=build_main_keyboard())
        elif data.startswith("supp:"):
            kind = data.split(":", 1)[1]
            add_log(chat_id, "supp", kind)
            send_message(chat_id, f"💊 Добавка отмечена: {kind}", reply_markup=build_main_keyboard())
        else:
            send_message(chat_id, "Окей.", reply_markup=build_main_keyboard())

        return jsonify({"ok": True})

    return jsonify({"ok": True})

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Open once after deploy:
    Set env WEBHOOK_URL to your Render URL + /<WEBHOOK_PATH>
    Example: https://fimi-xxxxx.onrender.com/webhook
    """
    if not BOT_TOKEN:
        return "BOT_TOKEN is not set", 500
    url = os.getenv("WEBHOOK_URL")
    if not url:
        return "Please set WEBHOOK_URL env var to your public https://.../<WEBHOOK_PATH>", 400
    r = requests.get(f"{TELEGRAM_API}/setWebhook", params={"url": url}, timeout=10)
    try:
        data = r.json()
    except Exception:
        data = {"status_code": r.status_code, "text": r.text}
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
