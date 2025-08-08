try:
                ml = int(t.split()[1])
                add_log("water_ml", ml)
                bot.send_message(chat_id, f"Вода записана: +{ml} мл 💧")
            except Exception:
                bot.send_message(chat_id, "Формат: /вода 250")
        elif t.startswith("/вес"):
            try:
                kg = float(t.split()[1].replace(",", "."))
                add_log("weight", kg)
                bot.send_message(chat_id, f"Вес записан: {kg} кг ✅")
            except Exception:
                bot.send_message(chat_id, "Формат: /вес 88.6")
        elif t in ("/сегодня", "сегодня"):
            bot.send_message(chat_id, training_today_text(), reply_markup=kb_training(), parse_mode="Markdown")
        else:
            bot.send_message(chat_id, "Команда получена. Доступно: /сегодня, /steps N, /вода ML, /вес KG")

    elif cbq:
        chat_id = cbq["message"]["chat"]["id"]
        mid = cbq["message"]["message_id"]
        data = cbq.get("data", "")
        if data == "train:done":
            mark_done("training_done")
            bot.edit_message_text("Тренировка отмечена ✅", chat_id, mid)
        elif data == "steps:done":
            mark_done("steps_done_flag")
            bot.edit_message_text("Ходьба за день отмечена 👣", chat_id, mid)
        elif data.startswith("water:+"):
            ml = 250 if data.endswith("250") else 500
            add_log("water_ml", ml)
            bot.edit_message_text(f"Вода: +{ml} мл 💧", chat_id, mid)
        elif data.startswith("supp:"):
            kind = data.split(":", 1)[1]
            s = load_state()
            day = today_key()
            s.setdefault(day, {}).setdefault("supp", []).append(kind)
            save_state(s)
            bot.edit_message_text("💊 Приём добавки отмечен", chat_id, mid)
        # answer callback
        try:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                          data={"callback_query_id": cbq["id"]}, timeout=10)
        except Exception:
            pass

    return "ok"

@app.route("/", methods=["GET"])
def root():
    return "FimiGymTrenBot up"
