# FimiGymTrenBot (Render-ready)

## Переменные окружения (Render → Environment)
- BOT_TOKEN — токен бота (обязателен)
- START_DATE — дата старта (YYYY-MM-DD), напр. 2025-08-09
- TIMEZONE — напр. Europe/Moscow
- (опц.) CHAT_ID — жёстко закрепить получателя
- (опц.) WEBHOOK_URL — если нужен кастомный URL (иначе возьмётся RENDER_EXTERNAL_URL)

## Render
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app

После деплоя бот сам выставит webhook на <RENDER_EXTERNAL_URL>/<BOT_TOKEN>.
Можно вручную открыть /setwebhook.
Команды: /start, /сегодня, /steps N, /вода ML, /вес KG.
