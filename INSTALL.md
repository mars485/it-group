# Установка и настройка IT GROUP CMS

Инструкция относится к текущему проекту IT GROUP на Django. Она описывает установку на Linux/VPS или ZimaOS через Docker Compose, а также запуск на хостинге с поддержкой Python/WSGI.

> «Любой хостинг» технически невозможен: площадка должна разрешать запуск Django-приложений на Python 3.12+, установку зависимостей, выполнение команд миграции, работу WSGI/Gunicorn или предоставлять собственный Python Application Manager, хранить SQLite-файл и загруженные файлы. Если доступен только PHP-хостинг без Python/WSGI и фоновых процессов, этот проект там не запустится.

## 1. Что подготовить

Для работы с сайтом нужны:

- исходный код публичного репозитория [`mars485/it-group`](https://github.com/mars485/it-group). Для клонирования достаточно HTTPS; аккаунт GitHub, SSH-ключ и токен не нужны;
- домен, если сайт будет доступен по адресу вроде `site.ru`;
- сервер с Linux и Docker Engine + Docker Compose v2 — для рекомендуемого способа;
- доступ к DNS домена и настройке HTTPS/reverse proxy;
- почтовый SMTP-аккаунт, если уведомления о заявках должны приходить на email;
- Telegram-бот и ID чата, если уведомления должны приходить в Telegram.

Текущий проект использует Django 6.1.1, Python 3.12 в контейнере, Gunicorn, SQLite, WhiteNoise для статических файлов и Docker volumes для базы и загрузок. При изменении версий сверяйтесь с [матрицей поддержки Python/Django](https://docs.djangoproject.com/en/6.1/faq/install/) и [официальным руководством Django по развёртыванию](https://docs.djangoproject.com/en/6.1/howto/deployment/).

## 2. Рекомендуемый вариант: Docker на Linux или ZimaOS

### Шаг 1. Установить Docker и Compose

На сервере должны выполняться обе команды:

```bash
docker --version
docker compose version
```

Если команды не найдены, установите Docker Engine и плагин Compose по официальной [инструкции Docker](https://docs.docker.com/compose/install/). Для ZimaOS используйте его системный Docker. Если учётная запись не имеет доступа к Docker, запускайте команды через `sudo`.

### Шаг 2. Получить проект

Войдите на сервер по SSH и клонируйте публичный репозиторий по HTTPS:

```bash
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/mars485/it-group.git
cd it-group
```

Поскольку репозиторий публичный, авторизация GitHub для чтения исходного кода не требуется. Если `git` не установлен, скачайте ZIP-архив через страницу репозитория и загрузите его в каталог приложения. SSH-клонирование тоже возможно, но для публичного чтения ключ не нужен.

**Важно:** публичный репозиторий означает, что исходный код и история коммитов доступны всем. Не помещайте в него `.env`, пароли SMTP, Django `SECRET_KEY`, токены, базу данных, пользовательские загрузки и резервные копии. Для этого проекта `.env` и `db.sqlite3` исключены через `.gitignore`; секреты храните только на сервере или в защищённых переменных окружения. Если секрет когда-либо попал в Git, удаление файла в новом коммите не скроет его из истории — такой секрет нужно заменить.

### Шаг 3. Запустить автоустановщик

```bash
chmod +x install.sh
./install.sh
```

Введите домен в виде `site.example.ru` или публичный IPv4/IPv6 без пути. Для домена скрипт настроит адрес сайта и HTTPS-редирект (после этого требуется настроить DNS и reverse proxy). Для IP он включит тестовый HTTP-доступ на `http://IP:8000`; для публичного сайта с формами предпочтительны домен и HTTPS. Если оставить поле пустым, сайт будет доступен только локально по `http://localhost:8000`. Скрипт создаст `.env`, сгенерирует секрет Django, применит миграции при старте контейнера и соберёт статические файлы.

Если на ZimaOS Docker требует привилегий, запустите установщик от пользователя с доступом к Docker, например:

```bash
sudo env DOCKER_CONFIG=/DATA/AppData/docker-cli-config bash ./install.sh
```

Секреты и `.env` не добавляйте в GitHub. Установщик ставит права `600` на созданный `.env`.

### Шаг 4. Настроить DNS и HTTPS

Если вы указали домен, настройте DNS-запись `A` домена на публичный IP сервера. Если используется поддомен, настройте также запись `www` или `CNAME` по своей схеме DNS.

Установите reverse proxy с сертификатом HTTPS. В Nginx Proxy Manager создайте Proxy Host:

- **Domain Names:** ваш домен;
- **Scheme:** `http`;
- **Forward Hostname / IP:** IP сервера, на котором работает Docker;
- **Forward Port:** `8000`;
- **Websockets Support:** включить;
- на вкладке SSL запросить сертификат Let's Encrypt и включить **Force SSL**.

Направьте входящие порты `80` и `443` на сервер с reverse proxy. Не открывайте порт приложения `8000` в публичный интернет, если он нужен только прокси.

Установщик с доменом включает `SECURE_SSL_REDIRECT=True`, поэтому сначала добейтесь корректной работы HTTPS на прокси. Django получает признак HTTPS из заголовка `X-Forwarded-Proto`, который должен передаваться прокси.

Если используется другой прокси, передайте запрос на порт `8000` и как минимум заголовки `Host`, `X-Real-IP` и `X-Forwarded-Proto`. Django описывает настройки безопасности в [Deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).

### Шаг 5. Проверить контейнер

```bash
docker compose ps
docker compose logs -f web
```

Проверьте главную страницу и `/admin/`. При установке на IP откройте `http://IP-СЕРВЕРА:8000`; с доменом — `https://ваш-домен/` после настройки DNS и прокси. При пустом поле проверьте `http://localhost:8000` на самом сервере.

При запуске Docker-контейнер автоматически выполняет `migrate` и `collectstatic`. Если контейнер постоянно перезапускается, сначала проверьте журнал `docker compose logs --tail=200 web`.

### Шаг 6. Создать пользователя админки

```bash
docker compose exec web python manage.py createsuperuser
```

Введите имя пользователя, email и пароль. Затем войдите по адресу `https://ваш-домен/admin/`. Для локального теста без домена используйте `http://IP-СЕРВЕРА:8000/admin/`.

В разделе «Настройки сайта» суперпользователь может задать бренд, публичный URL, логотип, контакты, цвета, аналитику, отдельный email для заявок, SMTP, Telegram и CRM webhook. Email контактов отображается на сайте, а «Email для заявок» получает уведомления. Если они пустые, используется `CONTACT_EMAIL` из `.env`. Логотип (PNG, JPG или WebP до 2 МБ) хранится в томе медиа.

### Шаг 7. Подключить email, Telegram, CRM и аналитику

В «Настройках сайта» заполните «Email для заявок», SMTP-сервер, порт, режим STARTTLS или SSL, логин, пароль приложения и адрес отправителя. Для Telegram укажите токен бота и ID чата. При необходимости добавьте CRM webhook и ID Яндекс Метрики. Изменения применяются после сохранения, без пересоздания контейнера.

Если эти поля не заполнены, можно использовать прежние значения из `.env` на сервере:

```dotenv
CONTACT_EMAIL=mail@example.ru
DEFAULT_FROM_EMAIL=website@example.ru
EMAIL_HOST=smtp.example.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=mail@example.ru
EMAIL_HOST_PASSWORD=пароль_или_пароль_приложения
CRM_WEBHOOK_URL=
```

Параметры SMTP берите у почтового провайдера. При пустом SMTP-сервере в админке используется конфигурация SMTP из `.env`; при пустых токене и ID чата используется пара Telegram из `.env`. Если любой из пары заполнен в админке, укажите там оба. Email и Telegram можно отключить отдельными флажками. CRM webhook и публичный URL из админки имеют приоритет над значениями `.env`.

Пароль SMTP и токен бота в админке доступны только суперпользователю, сохраняются в базе данных и включаются в её резервную копию. После сохранения они не показываются в форме: пустое поле сохраняет секрет, а флажок удаления очищает его. Не публикуйте `.env`, резервную копию или секреты в переписке. Если SMTP не настроен, заявки всё равно сохраняются в админке.

После изменения `.env` пересоздайте контейнер:

```bash
docker compose up -d
```

### Шаг 8. Обновить сайт

Из каталога проекта:

```bash
git pull --ff-only
docker compose up -d --build
docker compose logs -f web
```

Перед обновлением рабочей CMS сделайте резервную копию базы и загруженных файлов.

## 3. Ручная установка на VPS без Docker

Этот способ подходит для Linux VPS, где есть Python 3.12+, SSH и возможность постоянно запускать WSGI-приложение через Gunicorn/systemd или панель управления Python-приложениями.

### Шаг 1. Установить Python и получить проект

```bash
python3.12 --version
mkdir -p ~/apps
cd ~/apps
git clone https://github.com/mars485/it-group.git
cd it-group
```

Публичный репозиторий можно клонировать без GitHub-аккаунта и SSH-ключа. Если провайдер не даёт исходящим подключениям обращаться к GitHub, загрузите ZIP-архив репозитория через панель хостинга.

### Шаг 2. Создать окружение и поставить зависимости

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 3. Настроить переменные окружения

```bash
cp .env.example .env
mkdir -p "$HOME/itgroup-data/media"
chmod 700 "$HOME/itgroup-data"
```

Откройте `.env` и задайте реальные значения. Пути `/app/data` и `/app/media` из образца предназначены для Docker, поэтому замените их на доступные для записи постоянные каталоги вашего аккаунта:

```dotenv
SECRET_KEY=ВСТАВЬТЕ_СЛУЧАЙНЫЙ_СЕКРЕТ
DEBUG=False
ALLOWED_HOSTS=site.example.ru,www.site.example.ru
CSRF_TRUSTED_ORIGINS=https://site.example.ru,https://www.site.example.ru
SITE_URL=https://site.example.ru
SECURE_SSL_REDIRECT=True
SQLITE_PATH=/home/USER/itgroup-data/db.sqlite3
MEDIA_ROOT=/home/USER/itgroup-data/media
```

Сгенерировать секрет можно командой:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(64))'
```

Замените `USER` на системное имя пользователя и проверьте абсолютные пути. Директории базы и медиа не должны находиться в публичной папке сайта.

`SECURE_SSL_REDIRECT=True` включайте только после того, как HTTPS уже работает на сервере или reverse proxy. В настройках этого проекта выставлен доверенный `X-Forwarded-Proto`; убедитесь, что ваш прокси действительно передаёт этот заголовок. Скопируйте SMTP-переменные из предыдущего раздела, если нужны email-уведомления.

### Уведомления о заявках

Email отправляется на отдельный адрес для заявок; если он не задан — на публичный email из админки, затем на `CONTACT_EMAIL`. SMTP задаётся в «Настройках сайта», а если поле сервера пустое — через `.env`: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` и `DEFAULT_FROM_EMAIL`.

Чтобы отправлять заявки в Telegram:

1. Создайте отдельного бота через [@BotFather](https://t.me/BotFather) и сохраните выданный токен в тайне.
2. Напишите боту `/start`. Для группового чата добавьте туда бота и отправьте любое сообщение.
3. Узнайте ID личного чата или группы через Telegram Bot API `getUpdates` с токеном своего бота.
4. Укажите токен и ID чата в «Настройках сайта» либо задайте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID` в серверном `.env`.

Настройки email и Telegram независимы: можно включить оба канала или оставить только один. Заявка всё равно сохраняется в админке, даже если сервис уведомлений временно недоступен. После изменения `.env` пересоздайте контейнер, чтобы он прочитал новые переменные. Не отправляйте токен бота и SMTP-пароль в GitHub или в переписке.

### Шаг 4. Создать базу и статические файлы

```bash
source .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Выполните рекомендации и разберите предупреждения `check --deploy` до публикации. Проверка не заменяет полноценную настройку HTTPS, резервного копирования и доступов.

### Шаг 5. Создать администратора

```bash
python manage.py createsuperuser
```

### Шаг 6. Запустить Gunicorn

Для проверки запуска из корня проекта:

```bash
.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
```

Не используйте `runserver` как production-сервер. Для постоянной работы на VPS настройте systemd-службу или используйте менеджер процессов провайдера. Пример systemd unit (замените пути и имя пользователя):

```ini
[Unit]
Description=IT GROUP Django site
After=network.target

[Service]
User=ВАШ_ПОЛЬЗОВАТЕЛЬ
Group=www-data
WorkingDirectory=/home/ВАШ_ПОЛЬЗОВАТЕЛЬ/apps/it-group
EnvironmentFile=/home/ВАШ_ПОЛЬЗОВАТЕЛЬ/apps/it-group/.env
ExecStart=/home/ВАШ_ПОЛЬЗОВАТЕЛЬ/apps/it-group/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Сохраните unit в `/etc/systemd/system/itgroup.service`, затем выполните:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now itgroup
sudo systemctl status itgroup
```

Настройте Nginx или другой reverse proxy на `127.0.0.1:8000` с HTTPS и заголовком `X-Forwarded-Proto`. Если у пользователя сервиса нет доступа к каталогу `.env`, базе, `MEDIA_ROOT` или статическим файлам, Gunicorn не сможет запустить сайт или сохранить заявки.

## 4. Установка на Python-хостинг через панель провайдера

Подходит только тариф, где провайдер явно поддерживает Django/Python 3.12 и даёт виртуальное окружение, переменные окружения, WSGI entry point, постоянную файловую систему, выполнение миграций и `collectstatic`, а также возможность перезапуска приложения.

Общий порядок в панели хостинга:

1. Создайте Python-приложение на версии Python 3.12 или совместимой.
2. Подключите публичный GitHub-репозиторий `https://github.com/mars485/it-group.git` (авторизация для чтения не нужна) или загрузите ZIP-архив через поддерживаемый механизм деплоя. Не включайте секреты и пользовательские данные в исходники.
3. Укажите корневой каталог проекта и создайте виртуальное окружение.
4. Установите зависимости из `requirements.txt`.
5. Укажите WSGI callable `config.wsgi.application` (иногда панель требует файл-переходник с `from config.wsgi import application`). Название поля и способ задать `PYTHONPATH` зависят от провайдера.
6. Добавьте переменные из `.env.example` в интерфейсе провайдера. В панели хостинга не всегда читается файл `.env`, поэтому задавайте настройки через раздел Environment Variables.
7. Для `SQLITE_PATH` и `MEDIA_ROOT` задайте постоянные writable-каталоги аккаунта. Не используйте `/app/data`, если провайдер не создал такой путь.
8. В терминале/консоли приложения выполните `python manage.py migrate --noinput`, `python manage.py collectstatic --noinput` и `python manage.py createsuperuser`.
9. Подключите домен, включите SSL-сертификат и проверьте, что платформа передаёт HTTPS-состояние приложению.
10. Перезапустите приложение и проверьте `/`, `/admin/`, отправку тестовой заявки и сохранение заявки в базе.

Провайдеры называют разделы по-разному; точные кнопки и формат WSGI-файла нужно брать в документации конкретного хостинга. Если на тарифе нет Python 3.12, WSGI/ASGI, консоли или постоянного хранилища, выберите VPS/Docker или Django-поддерживаемую платформу. Django работает через WSGI/ASGI-серверы, а встроенный `runserver` предназначен только для разработки ([официальное руководство](https://docs.djangoproject.com/en/6.1/howto/deployment/)).

## 5. Резервные копии

В Docker данные находятся в именованных томах: база SQLite — `/app/data`, загруженные файлы заявок — `/app/media`. Сначала сделайте согласованную копию SQLite через её встроенный backup API, затем скопируйте файл из контейнера:

```bash
mkdir -p backups
docker compose exec -T web python -c 'import sqlite3; src=sqlite3.connect("/app/data/db.sqlite3"); dst=sqlite3.connect("/tmp/itgroup-db-backup.sqlite3"); src.backup(dst); dst.close(); src.close()'
docker compose cp web:/tmp/itgroup-db-backup.sqlite3 ./backups/itgroup-db-backup.sqlite3
docker compose exec -T web tar -C /app/media -czf - . > ./backups/itgroup-media.tar.gz
```

Скопируйте каталог `backups` на другое устройство или облачное хранилище и проверьте восстановление на тестовом экземпляре. Не храните единственную резервную копию на том же сервере.

## 6. Частые проблемы

| Симптом | Что проверить |
|---|---|
| `DisallowedHost` | Домен/IP должны быть перечислены в `ALLOWED_HOSTS`; после изменения переменной перезапустите приложение. |
| Бесконечный редирект или HTTPS не открывается | Проверьте SSL на прокси, `SECURE_SSL_REDIRECT`, `CSRF_TRUSTED_ORIGINS` и передачу `X-Forwarded-Proto`. |
| 502 Bad Gateway | Проверьте, что контейнер/Gunicorn работает, а адрес и порт upstream указаны правильно (`8000` для Docker-схемы). |
| `/admin/` без стилей | Выполните `collectstatic`; в Docker это делает команда запуска контейнера. Убедитесь, что WhiteNoise включён и static URL не перехватывается прокси. |
| Нет уведомлений о заявках | Проверьте флажки уведомлений, email для заявок, SMTP-сервер, порт, режим TLS/SSL, логин, пароль, токен бота, ID чата и логи приложения. Сама заявка должна остаться в разделе «Заявки». |
| Не удаётся сохранить заявку или файл | Проверьте свободное место и права на каталог базы/медиа; в Docker — состояние томов. |
| `Permission denied` от Docker на ZimaOS | Запускайте Compose от пользователя с Docker-доступом или через `sudo`; на ZimaOS при необходимости задайте `DOCKER_CONFIG=/DATA/AppData/docker-cli-config`. |

## 7. Важные ограничения текущей конфигурации

- Этот проект использует SQLite и один контейнер приложения. Для высокой нагрузки, нескольких экземпляров сайта или большой параллельной записи нужно отдельно перевести базу на PostgreSQL и проверить хранение медиа.
- Docker volumes переживают пересоздание контейнера, но не заменяют отдельные резервные копии сервера.
- HTTPS, домен и SMTP настраиваются на стороне владельца сервера/провайдера. Публичный исходный код можно клонировать без авторизации; переменные окружения и пользовательские данные остаются на сервере.
- Перед публикацией проверьте `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, HTTPS и рекомендации `python manage.py check --deploy` по [чек-листу Django](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).

## Официальные документы

- [Установка Docker Compose](https://docs.docker.com/compose/install/)
- [Docker Compose в production](https://docs.docker.com/compose/how-tos/production/)
- [Как развернуть Django](https://docs.djangoproject.com/en/6.1/howto/deployment/)
- [Django: Deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/)
- [Django и поддерживаемые версии Python](https://docs.djangoproject.com/en/6.1/faq/install/)
