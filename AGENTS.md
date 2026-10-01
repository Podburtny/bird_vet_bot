# AGENTS.md — Bird Vet Bot (проект «Турист»)

## Что это
Telegram-бот `@tourist_bird_vet_bot` — ИИ-консультант по домашней птице (куры, перепела)
для хозяйства на загородном участке «Турист». Пользователи — только по whitelist
(владелец + папа). Принимает текст, фото (в т.ч. альбомы) и голосовые; ведёт «кейсы»
(новый кейс после `CASE_TIMEOUT_HOURS` тишины) и профиль хозяйства.

Знания и состояние проекта — в Obsidian:
`/Users/podburtny/Documents/Mike Brain/Жизнь/Загородная жизнь/Турист/00 Project.md`
и `Bird Vet Bot.md` рядом. Документы — `~/Library/CloudStorage/SynologyDrive-Drive/Турист/`.

## Стек
Python 3.11, aiogram 3 (long polling), SQLAlchemy 2 + SQLite, фото на локальном диске,
OpenRouter (ответы `anthropic/claude-sonnet-4.5`, резюме `google/gemini-2.0-flash`,
распознавание голоса `google/gemini-2.5-flash`), ffmpeg для голосовых, Sentry опционально.

## Структура
| Путь | Назначение |
|---|---|
| `main.py` | точка входа: логирование, Sentry, middlewares, роутеры, polling |
| `bot.py`, `config.py`, `database.py` | бот/диспетчер, настройки из `.env` (pydantic-settings), SQLAlchemy-сессия |
| `handlers/` | команды, кнопки, текст, фото, голос, неподдерживаемые типы |
| `services/` | кейсы, LLM, фото, резюме, буфер альбомов |
| `llm/` | клиент OpenRouter, сборка контекста, системные промпты |
| `repositories/`, `models/` | доступ к БД и модели (users, cases, messages, attachments) |
| `storage/` | локальное хранилище фото (`DATA_DIR/photos/<user>/<case>/`) |
| `middlewares/` | whitelist-доступ и логирование |
| `ui/` | клавиатуры |
| `deploy.sh`, `bird-vet-bot.service` | деплой на VPS (rsync + systemd) |

## Запуск локально
```bash
python3.11 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env   # заполнить TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY
venv/bin/python main.py
```
Нужен ffmpeg (`brew install ffmpeg`).

## Деплой
VPS `146.103.108.114` (тот же, что art-curator), изолированно: код `/opt/bird-vet-bot`,
env `/etc/bird-vet-bot/env`, unit `bird-vet-bot`. Обновление — `./deploy.sh`
(первичная установка — см. README). Данные (SQLite + фото) — в `DATA_DIR` на сервере.

## Тесты
Автотестов нет. Проверка — запуск локально с тестовым ботом и ручной прогон:
текст, фото, альбом, голосовое, кнопка «Новый кейс».

## Ветки
Рабочая ветка — `v2-local-storage` (её код задеплоен). `main` отстаёт: версия с Supabase.

## Соглашения
- Секреты только в `.env` / `/etc/bird-vet-bot/env`; никогда в Git и в Obsidian.
- Ответы бота — на русском, HTML-разметка Telegram, без markdown.
- После законченного этапа: проверить, закоммитить, `git push`; обновить `00 Project.md`
  (журнал) и `Bird Vet Bot.md` в Obsidian, если изменилось поведение или деплой.
