Лаба 3. Ansible

Три контейнера в одной сети: master с Ansible, nginx и app.
На целевых машинах изначально только Debian 12, Python и SSH.
Сам Nginx и всё для запуска приложения ставит плейбук.

Приложение с заметками на FastAPI, исходники в app/main.py.
В этой лабе используется SQLite, отдельная база не нужна.

Для запуска нужен Docker с Compose v2, у Docker Desktop — Linux-контейнеры.
Ansible на Windows ставить не надо, он работает внутри master.

**Запуск**

    git clone --branch lab3 https://github.com/DimeNiceTry/mipt_prac3.git
    cd mipt_prac3
    docker compose up -d --build --wait

После этого контейнеры доступны по SSH, но приложение ещё не развёрнуто.
Проверить соединение с чистыми машинами:

    docker compose exec -T master ansible managed -m ping

Деплой запускается с master:

    docker compose exec -T master ansible-playbook site.yml

В конце должны быть failed=0 и unreachable=0. Приложение откроется
на http://localhost:8083, Swagger — http://localhost:8083/docs.

    curl.exe -i http://localhost:8083/health
    docker compose ps

У /health ответ 200 и {"status":"ok"}. Команды для PowerShell;
в Linux вместо curl.exe обычный curl. Для Linux и Git Bash есть ещё
scripts/deploy.sh, он выполняет сборку стенда и запуск плейбука.

Что делают роли

- common проверяет Debian, Python и память, ставит общие пакеты и Supervisor.
- app ставит инструменты Python, создаёт пользователя notes, распаковывает
  приложение и ставит зависимости в venv. Настройки и start.sh берутся из шаблонов.
- nginx устанавливает Nginx, проверяет конфигурацию через nginx -t,
  настраивает проксирование на app:8080 и запускает процесс.

Архив приложения собирается на master из исходников. Для каждой версии
используется свой каталог в /opt/notes/releases, current указывает на выбранную
версию. Изменения файлов вызывают handlers для перезапуска нужного процесса.
Настройки имени приложения и внутреннего порта лежат в group_vars/all.yml.

Приложение запускается скриптом /opt/notes/start.sh от пользователя notes.
За процессом следит Supervisor. Здесь нет systemd, поэтому Supervisor
используется как менеджер процессов внутри учебных контейнеров.

Проверки

Повторить тот же плейбук:

    docker compose exec -T master ansible-playbook site.yml

При повторном запуске без изменений у обеих машин будет changed=0.
Если поменять исходники или шаблоны и повторить деплой, обновятся нужные файлы
и перезапустится соответствующий процесс.

В Swagger можно отправить POST /notes с {"text":"проверка ansible"},
а потом прочитать заметку через GET /notes.

Для проверки API, сети и запуска после перезапуска контейнера есть скрипт.
На машине нужен Python 3.10+, дополнительных библиотек для него не надо:

    python scripts/verify.py

Он добавит заметку, перезапустит app и проверит, что приложение снова отвечает,
а заметка сохранилась. SQLite хранится в томе notes_data.

Посмотреть процессы и конфигурацию:

    docker compose exec -T app supervisorctl status
    docker compose exec -T nginx supervisorctl status
    docker compose exec -T nginx nginx -t

При запуске Docker собирает только базовые SSH-машины и master.
Nginx, Supervisor, venv и приложение устанавливаются именно через Ansible.
Healthcheck целевых контейнеров проверяет готовность SSH; HTTP проверяется
отдельно плейбуком и через /health.

Ключ master создаётся при первом запуске и остаётся в отдельном Docker-томе.
Целевые машины получают только публичный ключ. Пароли для SSH отключены,
22 порт на хост не публикуется. Ключи хостов тоже сохраняются между пересозданиями.

Остановка:

    docker compose down

Тома с ключами и заметками сохранятся. После down контейнеры с установленными
пакетами будут удалены, поэтому после нового up нужно ещё раз выполнить плейбук.
Обычный docker compose restart сохраняет установленное ПО и запускает сервисы снова.

Если нужен полностью чистый стенд, docker compose down -v удалит и тома,
включая заметки и SSH-ключи.

По умолчанию наружу открыт только Nginx:8083. Если порт занят, можно поменять
HTTP_PORT в .env по примеру .env.example.

Скриншоты проверки:

- [контейнеры и /health](docs/screenshots/containers.png)
- [чистые машины и SSH](docs/screenshots/clean.png)
- [Ansible и повторный запуск](docs/screenshots/ansible.png)
- [запрос в Swagger](docs/screenshots/api.png)
