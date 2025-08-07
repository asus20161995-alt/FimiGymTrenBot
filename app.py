
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)

@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        bot.sendMessage(chat_id=chat_id, text="Привет! Это бот FimiGymTrenBot. Скоро начнем тренировку!")
    return "ok"

@app.route('/')
def index():
    return "Бот работает!"

if __name__ == '__main__':
    app.run()
