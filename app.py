from flask import Flask, request
import os
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

app = Flask(name)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана")
bot = Bot(token=TOKEN)

@app.route("/" + TOKEN, methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True) or {}
    msg = data.get("message") or {}
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = (msg.get("text") or "").strip()

    if not chat_id:
        return "ok"

    # Простая логика ответов — расширим позже
    if text.lower() in ("/start", "старт", "привет"):
        bot.send_message(chat_id=chat_id, text=(
            "Привет! Я FimiGymTrenBot. "
            "Напиши 'прогресс' — покажу пример ответа. "
            "Полная программа и напоминания подключатся после деплоя. 💪"
        ))
    elif text.lower() == "прогресс":
        bot.send_message(chat_id=chat_id, text="Прогресс: держим курс на гранит 💎")
    else:
        bot.send_message(chat_id=chat_id, text="Команда принята. Скоро всё автоматизируем.")

    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "FimiGymTrenBot OK"
