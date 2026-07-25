#!/usr/bin/env bash
# Деплой bird-vet-bot на VPS: rsync кода, зависимости, рестарт сервиса.
# Первичная установка (venv, /etc/bird-vet-bot/env, ffmpeg, unit) — см. README.
set -euo pipefail
cd "$(dirname "$0")"

HOST="${DEPLOY_HOST:-root@146.103.108.114}"
DIR=/opt/bird-vet-bot

rsync -az --delete \
  --exclude '.git' --exclude 'venv' --exclude '.env' \
  --exclude 'data' --exclude '__pycache__' \
  ./ "$HOST:$DIR/"

ssh "$HOST" "set -e; cd $DIR; \
  [ -d venv ] || python3 -m venv venv; \
  venv/bin/pip install -q -r requirements.txt; \
  systemctl restart bird-vet-bot"

echo "Деплой завершён."
