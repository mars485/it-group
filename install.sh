#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker не найден. Установите Docker / Docker Compose в ZimaOS и запустите установщик ещё раз." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Не найден Docker Compose v2. Проверьте установку Docker Compose в ZimaOS." >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Для подготовки .env нужен python3." >&2
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

read -r -p "Домен сайта (оставьте пустым для http://IP-СЕРВЕРА:8000): " DOMAIN
DOMAIN=$(DOMAIN="$DOMAIN" python3 -c 'import os; print(os.environ["DOMAIN"].strip().removeprefix("https://").removeprefix("http://").strip("/"))')
if [[ "$DOMAIN" == *"/"* || "$DOMAIN" == *" "* ]]; then
  echo "Введите только домен, например site.example.ru, без пути." >&2
  exit 1
fi

if [ -n "$DOMAIN" ]; then
  SITE_URL="https://$DOMAIN"
  ALLOWED_HOSTS="$DOMAIN,localhost,127.0.0.1"
  CSRF_TRUSTED_ORIGINS="https://$DOMAIN"
  SECURE_SSL_REDIRECT="True"
else
  SITE_URL="http://localhost:8000"
  ALLOWED_HOSTS="localhost,127.0.0.1"
  CSRF_TRUSTED_ORIGINS=""
  SECURE_SSL_REDIRECT="False"
fi

SECRET_KEY=$(python3 - <<'PY'
import secrets
from pathlib import Path

for line in Path(".env").read_text(encoding="utf-8").splitlines():
    if line.startswith("SECRET_KEY="):
        current = line.partition("=")[2].strip()
        if current and current != "replace-me":
            print(current)
            raise SystemExit
print(secrets.token_urlsafe(48))
PY
)
export SITE_URL ALLOWED_HOSTS CSRF_TRUSTED_ORIGINS SECURE_SSL_REDIRECT SECRET_KEY
python3 - <<'PY'
import os
from pathlib import Path

path = Path(".env")
values = {
    "SECRET_KEY": os.environ["SECRET_KEY"],
    "DEBUG": "False",
    "ALLOWED_HOSTS": os.environ["ALLOWED_HOSTS"],
    "CSRF_TRUSTED_ORIGINS": os.environ["CSRF_TRUSTED_ORIGINS"],
    "SITE_URL": os.environ["SITE_URL"],
    "SECURE_SSL_REDIRECT": os.environ["SECURE_SSL_REDIRECT"],
    "SQLITE_PATH": "/app/data/db.sqlite3",
    "MEDIA_ROOT": "/app/media",
}
keys = set(values)
remaining = [
    line for line in path.read_text(encoding="utf-8").splitlines()
    if not any(line.startswith(key + "=") for key in keys)
]
path.write_text("\n".join([*(f"{key}={value}" for key, value in values.items()), *remaining]).rstrip() + "\n", encoding="utf-8")
path.chmod(0o600)
PY

echo "Собираю и запускаю сайт..."
docker compose up -d --build
echo
echo "IT GROUP запущен: $SITE_URL"
echo "Админ-панель: $SITE_URL/admin/"
echo "Создать администратора: docker compose exec web python manage.py createsuperuser"
echo "Логи: docker compose logs -f web"
echo "С HTTPS-доменом направьте reverse proxy (например, Nginx Proxy Manager) на порт 8000."
