# Bird Vet Bot

Telegram-бот (@tourist_bird_vet_bot) для консультаций по домашней птице (куры,
перепела и др.). Пользователи — по whitelist (владелец + папа).

## Стек

- Python 3.11+
- aiogram 3 (long polling — не нужны домен, nginx и открытые порты)
- SQLite (SQLAlchemy 2), схема создаётся автоматически при старте
- Фото — на локальном диске (`DATA_DIR/photos`), в модель уходят как base64 data URI
- OpenRouter: ответы `anthropic/claude-sonnet-4.5`, резюме `google/gemini-2.0-flash`
- Sentry (опционально)

## Локальный запуск

```bash
git clone https://github.com/Podburtny/bird_vet_bot.git
cd bird_vet_bot
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env      # заполнить TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY
venv/bin/python main.py
```

Модели, таймаут кейса и путь к данным настраиваются в `.env` (см. `.env.example`).
Ключ OpenRouter — отдельный, с лимитом расходов; в git не попадает (см. `.gitignore`).

## Установка на VPS (один раз)

Бот работает на том же VPS, что art-curator, но полностью изолирован: отдельная
папка, свой venv и systemd-unit, nginx не затрагивается.

```bash
ssh root@146.103.108.114
mkdir -p /opt/bird-vet-bot /etc/bird-vet-bot
# залить код в /opt/bird-vet-bot (rsync/git), создать venv и поставить зависимости
cd /opt/bird-vet-bot && python3 -m venv venv && venv/bin/pip install -r requirements.txt
# заполнить /etc/bird-vet-bot/env по образцу .env.example
cp bird-vet-bot.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now bird-vet-bot
```

Данные (SQLite + фото) лежат в `DATA_DIR` (по умолчанию `data/` внутри проекта) —
для бэкапа достаточно скопировать эту папку.

## Хранилище данных

- `cases`, `messages`, `attachments` — кейсы, переписка, ссылки на фото на диске.
- Фото не уходят ни в какое облако: файл сохраняется под `DATA_DIR/photos/<user>/<case>/`,
  а модели передаётся как base64 data URI.
