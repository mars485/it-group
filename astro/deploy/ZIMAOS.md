# ZimaOS: прямая загрузка и безопасный предпросмотр

GitHub Actions собирает сайт и публикует предварительную версию в GitHub Releases:
https://github.com/mars485/it-group/releases/tag/site-preview-latest

## Скачать и обновить одной командой

Подключитесь по SSH к ZimaOS. Создайте каталог, затем загрузите скрипт из ветки astro-migration и запустите:

```sh
sudo mkdir -p /DATA/AppData/it-group-preview
sudo chown "$(id -u):$(id -g)" /DATA/AppData/it-group-preview
curl -fL https://raw.githubusercontent.com/mars485/it-group/astro-migration/astro/deploy/update-preview.sh -o /DATA/AppData/it-group-preview/update-preview.sh
sh /DATA/AppData/it-group-preview/update-preview.sh
```

Скрипт скачивает https://github.com/mars485/it-group/releases/download/site-preview-latest/it-group-site.tar.gz, проверяет наличие index.html, переносит новую версию в /DATA/AppData/it-group-preview/site и сохраняет предыдущую в site.previous. Не запускайте этот скрипт, пока первый GitHub Actions Release не завершится успешно.

Для локального предпросмотра, если установлен Python 3:

```sh
cd /DATA/AppData/it-group-preview/site
python3 -m http.server 18001 --bind 127.0.0.1
```

На компьютере создайте SSH-туннель:

```sh
ssh -L 18001:127.0.0.1:18001 ainur@192.168.1.160
```

Откройте http://127.0.0.1:18001. Публичную публикацию отложите до подключения защищённого webhook CRM и утверждения политики обработки персональных данных.
