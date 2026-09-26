# Перенос IT GROUP с ZimaOS на VPS

Цель: сайт `karpiev.ru` работает на VPS (Ubuntu/Debian) через Nginx и HTTPS. Nginx Proxy Manager на ZimaOS продолжает обслуживать остальные приложения, но больше не участвует в работе этого домена. Django в Docker доступен только на `127.0.0.1:18000` VPS. База SQLite, загруженные файлы и настройки админки переносятся вместе.

**До начала:** узнайте IPv4 VPS и SSH-пользователя; убедитесь, что исходный сайт открывается и контейнер ZimaOS работает. Подготовьте короткое окно обслуживания: после остановки старого контейнера и до завершения DNS-переключения формы будут недоступны. Не удаляйте старые Docker volumes до проверки нового сайта.

## 1. Подготовить VPS, пока ZimaOS обслуживает сайт

Войдите по SSH на VPS. Проверьте ОС, Docker, Compose и занятость портов:

```bash
cat /etc/os-release
sudo docker --version
sudo docker compose version
sudo ss -lntp
```

Если Docker/Compose отсутствуют, установите их по официальной инструкции для [Ubuntu](https://docs.docker.com/engine/install/ubuntu/) или [Debian](https://docs.docker.com/engine/install/debian/). Если порты 80 или 443 уже заняты, сначала выясните, какой сервис их использует; приведённая ниже установка Nginx рассчитана на свободные порты. Не заменяйте конфигурацию работающего VPS-прокси без проверки.

Получите отдельную копию репозитория (не затрагивая прежний каталог `~/apps/it-group`, если он есть):

```bash
sudo mkdir -p /srv/it-group
sudo chown "$(id -u):$(id -g)" /srv/it-group
git clone https://github.com/mars485/it-group.git /srv/it-group
cd /srv/it-group
sudo mkdir -p /srv/it-group-transfer
sudo chown "$(id -u):$(id -g)" /srv/it-group-transfer
chmod 700 /srv/it-group-transfer
```

Для текущего образа нужен Python 3.12 (он уже указан в Dockerfile). Заранее проверьте, что Docker может загрузить базовый образ:

```bash
sudo docker pull python:3.12-slim
```

Установите Nginx и Certbot, но пока **не** переключайте DNS:

```bash
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Проверьте, что входящие TCP 80 и 443 разрешены у VPS-провайдера/в его firewall. Порт 18000 извне открывать не нужно: Compose связывает его только с loopback VPS.

## 2. Остановить запись на ZimaOS и сделать финальную копию

На ZimaOS в каталоге `~/AppData/it-group` выполните команды **по одной**:

```bash
cd ~/AppData/it-group
mkdir -p ../it-group-transfer
chmod 700 ../it-group-transfer
cp .env ../it-group-transfer/.env
sudo env DOCKER_CONFIG=/DATA/AppData/docker-cli-config docker compose stop web
sudo env DOCKER_CONFIG=/DATA/AppData/docker-cli-config docker compose run --rm --no-deps -T -u 0 -v "$(cd .. && pwd)/it-group-transfer:/export" web sh -c 'cp /app/data/db.sqlite3 /export/db.sqlite3 && tar -C /app/media -czf /export/media.tar.gz .'
sudo chown "$(id -u):$(id -g)" ../it-group-transfer/db.sqlite3 ../it-group-transfer/media.tar.gz
chmod 600 ../it-group-transfer/.env ../it-group-transfer/db.sqlite3 ../it-group-transfer/media.tar.gz
ls -lh ../it-group-transfer/db.sqlite3 ../it-group-transfer/media.tar.gz
```

Команда `docker compose run` создаёт отдельный временный контейнер с теми же volumes, когда основной контейнер остановлен. Так SQLite копируется без одновременной записи. Файл `.env` и база содержат секреты и персональные данные. Папка переноса находится вне Git-репозитория; не публикуйте архив.

Передайте три файла на VPS по SSH. Замените `USER@VPS_IP` на реальные данные:

```bash
scp ../it-group-transfer/.env ../it-group-transfer/db.sqlite3 ../it-group-transfer/media.tar.gz USER@VPS_IP:/srv/it-group-transfer/
```

## 3. Восстановить данные на VPS

На VPS в `/srv/it-group`:

```bash
cd /srv/it-group
cp /srv/it-group-transfer/.env .env
chmod 600 .env /srv/it-group-transfer/.env /srv/it-group-transfer/db.sqlite3 /srv/it-group-transfer/media.tar.gz
nano .env
```

Сохраните исходный `SECRET_KEY`, SMTP/Telegram значения и существующие настройки. Проверьте или задайте:

```dotenv
DEBUG=False
ALLOWED_HOSTS=karpiev.ru
CSRF_TRUSTED_ORIGINS=https://karpiev.ru
SITE_URL=https://karpiev.ru
SECURE_SSL_REDIRECT=True
SQLITE_PATH=/app/data/db.sqlite3
MEDIA_ROOT=/app/media
```

Значения в админке, включая логотип, цвета, заявки и сохранённые токены, уже находятся в копии базы. Пример выше не заменяет весь `.env`: оставьте остальные существующие строки. Не выводите содержимое `.env` в чате или публичном журнале.

Соберите образ:

```bash
sudo docker compose -f compose.vps.yaml build web
```

Если сборка прерывается ошибкой DNS внутри Docker, а DNS самого VPS работает, используйте:

```bash
sudo docker build --network host -t itgroup-vps-web .
```

Восстановите базу и медиа в **новые** именованные volumes до первого запуска Django:

```bash
sudo docker compose -f compose.vps.yaml run --rm --no-deps -T -u 0 -v "/srv/it-group-transfer:/import:ro" web sh -c 'test -s /import/db.sqlite3 && cp /import/db.sqlite3 /app/data/db.sqlite3 && tar -C /app/media -xzf /import/media.tar.gz && chown -R 10001:10001 /app/data /app/media'
sudo docker compose -f compose.vps.yaml up -d --no-build
sudo docker compose -f compose.vps.yaml ps
sudo docker compose -f compose.vps.yaml logs --tail=100 web
```

Контейнер при старте сам применяет миграции и собирает статику. Проверьте SQLite и ответ приложения через loopback:

```bash
sudo docker compose -f compose.vps.yaml exec web python -c 'import sqlite3; print(sqlite3.connect("/app/data/db.sqlite3").execute("PRAGMA quick_check").fetchone()[0])'
curl -I -H 'Host: karpiev.ru' -H 'X-Forwarded-Proto: https' http://127.0.0.1:18000/
```

Ожидается `ok` и HTTP 200. Не запускайте `createsuperuser`: пользователи админки перенесены вместе с базой.

## 4. Nginx, DNS и HTTPS

На VPS установите конфигурацию из репозитория:

```bash
sudo cp deploy/nginx/it-group.conf /etc/nginx/sites-available/it-group
sudo ln -s /etc/nginx/sites-available/it-group /etc/nginx/sites-enabled/it-group
sudo nginx -t
sudo systemctl reload nginx
```

У DNS-провайдера смените A-запись `karpiev.ru` на IPv4 VPS. Если у домена есть AAAA-запись, обновите её на работающий IPv6 VPS или удалите, иначе часть посетителей может попадать на старый сервер. Подождите, пока домен начнёт разрешаться в новый адрес, затем на VPS получите сертификат:

```bash
sudo certbot --nginx -d karpiev.ru --redirect
sudo certbot renew --dry-run
```

Certbot должен иметь доступ к домену по TCP 80 для проверки и к 443 для HTTPS. Если используется `www.karpiev.ru`, сначала добавьте его DNS-запись и в `server_name`, а затем запросите сертификат с дополнительным `-d www.karpiev.ru`.

## 5. Проверить переключение и сохранить резерв

Проверьте `https://karpiev.ru/`, `/admin/`, логотип и страницу контактов. Отправьте одну тестовую заявку, убедитесь, что она появилась в админке VPS и дошли выбранные уведомления. Проверьте загрузку файла через форму. Посмотрите здоровье контейнера и логи:

```bash
cd /srv/it-group
sudo docker compose -f compose.vps.yaml ps
sudo docker compose -f compose.vps.yaml logs --tail=100 web
```

Старый контейнер ZimaOS пока оставьте остановленным, а volumes и защищённые файлы переноса сохраните как резерв. При сбое нового сайта можно временно вернуть старую DNS-запись и запустить старый контейнер; заявки, полученные на VPS после переключения, нужно отдельно выгрузить перед таким возвратом.

## Обновления после переноса

На VPS:

```bash
cd /srv/it-group
git pull --ff-only origin main
sudo docker compose -f compose.vps.yaml up -d --build
sudo docker compose -f compose.vps.yaml ps
```

База и медиа находятся в отдельных Docker volumes и переживают пересборку. Регулярно копируйте оба volumes за пределы VPS.
