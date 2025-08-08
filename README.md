# FimiGymTrenBot (minimal, stable)

Телеграм-бот для учёта воды, веса, шагов, тренировок и добавок.
Без сторонних Telegram-библиотек — только `Flask` + `requests`. Это делает развёртывание на Render максимально стабильным.

## Быстрый старт на Render
1) Создай репозиторий и загрузите эти 4 файла: `app.py`, `requirements.txt`, `Procfile`, `README.md`.
2) На render.com → New Web Service → привяжи репозиторий.
3) Настройки:
   - Runtime: Python 3
   - Start Command: (оставь пустым, Render возьмёт из Procfile)
   - Instance Type: Free
4) Env Vars:
   - `BOT_TOKEN` = токен бота от BotFather
   - `WEBHOOK_PATH` = `webhook` (по умолчанию)
   - `WEBHOOK_URL` = публичный URL твоего сервиса на Render + `/webhook`  
     пример: `https://fimagymtrenbot.onrender.com/webhook`
5) Deploy.
6) Когда сервис «Live», открой в браузере:  
   `https://<твой-домен>.onrender.com/set_webhook` — зарегистрировать вебхук.
7) В Telegram напиши боту `/start`.
