# Лабораторные работы по курсу ИТМО "Контейнеризация и оркестрация приложений"

Выполнили: Неронов Роман, Низамов Тимур — AI Talent Hub

## Описание тестового приложения

Чат-бот ИИ-персоны "Аристотель", который отвечает на вопросы по книге "Метафизика" и состоит из сервисов:

 - db: база данных PostgreSQL с расширением PGVector
 - db-migrate: выполнение миграций в среде python с помощью alembic
 - chatbot: обработчики событий чат-бота Telegram
 - qa: микросервис RAG-системы для ответов на вопросы по книге Аристотеля "Метафизика"

## Лабораторная работа 1

[[notion](https://jasper-cause-ce0.notion.site/1-Dockerfile-3e97af9ebae24703a4ada36bb3e62c9f)]

TODO: описание содержимого обоих докерфайлов - про плохие и хорошие практики, и почему они такими являются, + две плохие практики по использованию контейнеризации

### Замечание

в проекте собирается 3 контейнера с питоном внутри, при этом есть общие зависимости в трёх, надо чтобы три проекта собирались на базе образа, в котором предустановлены общие зависимости:
```txt
aiohttp
pgvector
psycopg2-binary
python-dotenv
sqlalchemy
```

## Лабораторная работа 2

[[notion](https://jasper-cause-ce0.notion.site/2-Docker-Compose-31e203f6dc7042a6aacde2e1e98c7b38)]

### Запуск проекта

```shell
docker compose up --build -d
```

### Описание файла Docker compose

[Docker-compose.yaml](./docker-compose.yaml) состоит из следующих **сервисов:**
- **db:**
  - Отвечает за базу данных PostgreSQL с расширением PGVector.
  - Использует образ `ragbot/db:latest`, построенный из директории `./db`.
  - Имя контейнера — `ragbot-db`.
  - Перезапускается при остановке, если только не был остановлен вручную.
  - Загружает переменные окружения из файла `.env`.
  - Маунтирует том `db-data` в директорию `/var/lib/postgresql/data` для хранения данных базы данных.
  - Использует сеть `ragbot-conn`.
  - Проверяет работоспособность базы данных с помощью команды `pg_isready`.

- **db-migrate:**
  - Отвечает за выполнение миграций в среде python с помощью alembic.
  - Использует образ `ragbot/db-migrate:latest`, построенный из `./db/Dockerfile-migrate`.
  - Имя контейнера — `ragbot-db-migrate`.
  - Не перезапускается.
  - Загружает переменные окружения из `.env`.
  - Зависит от сервиса `db` и запускается только после того, как `db` будет готов.
  - Использует сеть `ragbot-conn`.

- **qa:**
  - Сервис для модуля QA (Questions&Answers) — микросервиса RAG-системы для ответов на вопросы по книге Аристотеля "Метафизика".
  - Использует образ `ragbot/qa:latest`, построенный из `./qa`.
  - Имя контейнера — `ragbot-qa`.
  - Перезапускается при остановке.
  - Запускает команду `python main.py`.
  - Публикует порт 8080 на хост-машине.
  - Загружает переменные окружения из `.env`.
  - Зависит от сервисов `db` и `db-migrate`. Запускается после того, как `db` будет готов, и `db-migrate` успешно завершит свою работу.
  - Использует сеть `ragbot-conn`.

- **chatbot:**
  - Сервис с обработчиками событий чат-бота Telegram.
  - Использует образ `ragbot/chatbot:latest`, построенный из `./chatbot`.
  - Имя контейнера — `ragbot-chatbot`.
  - Перезапускается при остановке.
  - Запускает команду `python main.py`.
  - Загружает переменные окружения из `.env`.
  - Зависит от сервисов `db`, `qa` и `db-migrate`. Запускается после того, как `db` будет готов, `qa` запустится и `db-migrate` успешно завершит свою работу.
  - Использует сеть `ragbot-conn`.

**Том данных:**
- **db-data:**
  - Том для хранения данных базы данных PostgreSQL.

**Сеть:**
- **ragbot-conn:**
  - Сеть, используемая для связи между сервисами.

### Ответы на вопросы

> Можно ли ограничивать ресурсы (например, память или CPU) для сервисов в docker-compose.yml? Если нет, то почему, если да, то как?

Можно с помощью заданной для сервиса директивы `deploy`:

```yaml
    deploy:
        resources:
            limits:
              cpus: 0.50
              memory: 512M
```

Также можно задавать определённые ядра процессора, использование видеокарт и т.д.

> Как можно запустить только определенный сервис из docker-compose.yml, не запуская остальные?

С помощью команды `exec`, например:

```shell
docker-compose exec db
```

## Лабораторная работа 3

[[notion](https://jasper-cause-ce0.notion.site/3-Kubernetes-5c5ef516385442edb6db1162d02df95e)]

TODO:
- описание хода работы и скриншоты
- Ответы на доп. вопросы

## Лабораторная работа 4

[[notion](https://jasper-cause-ce0.notion.site/4-More-Kubernetes-e2690d6f8ae3419790b1e0f16f59142d)]

TODO: описание хода работы и скриншоты

## Полезные ссылки
 - notion курса: https://jasper-cause-ce0.notion.site/3b2e4b7180954cbbad6c0449db638d6b
