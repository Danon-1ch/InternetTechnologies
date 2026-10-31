# TaskFlow API

REST API для управления задачами команды. Хранит данные в PostgreSQL, схема создаётся миграциями Alembic, приложение и БД запускаются через Docker Compose.

**Стек:** Python 3.12 · FastAPI · PostgreSQL 16 · SQLAlchemy 2 · Alembic · Docker Compose.

---

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

После старта:

- API — http://localhost:8000
- Swagger UI — http://localhost:8000/docs
- Health-check — http://localhost:8000/health

Миграции Alembic применяются автоматически при запуске контейнера `api`.

Остановить:

```bash
docker compose down
```

Данные PostgreSQL сохраняются в именованном volume `pgdata`. Флаг `-v` удаляет и контейнеры, и данные:

```bash
docker compose down -v
```

---

## Переменные окружения

Все секреты читаются из `.env` (в репозиторий не попадает). Шаблон — `.env.example`:

```dotenv
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=change-me
POSTGRES_DB=taskflow
DATABASE_URL=postgresql+psycopg2://taskflow:change-me@db:5432/taskflow
```

Внутри Docker Compose хост БД — `db` (имя сервиса), а не `localhost`.

---

## Структура проекта

```
.
├── app/
│   ├── main.py            # приложение, /health, подключение роутеров
│   ├── config.py          # настройки из окружения
│   ├── database.py        # engine, Session, Base, зависимость get_db
│   ├── models.py          # 5 ORM-моделей
│   ├── schemas.py         # Pydantic-схемы (Create/Update/Read)
│   └── routers/           # CRUD-роутеры по ресурсам
├── alembic/
│   └── versions/          # миграции
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Модель данных

Пять таблиц: `users`, `projects`, `labels`, `tasks`, `comments`.

- Роли: `operator`, `admin`.
- Статусы задачи: `open`, `in_progress`, `done`.
- Приоритеты: `low`, `medium`, `high`.
- Цвет метки — `#RRGGBB`.

Каскады:

| Связь | При удалении родителя |
|---|---|
| `tasks.project_id → projects.id` | удалить задачи |
| `tasks.assignee_id → users.id` | обнулить исполнителя |
| `tasks.label_id → labels.id` | обнулить метку |
| `comments.task_id → tasks.id` | удалить комментарии |
| `comments.author_id → users.id` | запретить удаление автора |

---

## API

Для каждого ресурса — пять операций.

| Метод | URL | Успех |
|---|---|---|
| `GET` | `/v1/{resource}` | 200 |
| `GET` | `/v1/{resource}/{id}` | 200 |
| `POST` | `/v1/{resource}` | 201 |
| `PATCH` | `/v1/{resource}/{id}` | 200 |
| `DELETE` | `/v1/{resource}/{id}` | 204 |

`{resource}` — `users`, `projects`, `labels`, `tasks`, `comments`.

Дополнительно:

- `GET /health` — проверяет подключение к БД.
- `GET /v1/tasks?project_id=1&status=open` — фильтр задач.
- `GET /v1/comments?task_id=1` — фильтр комментариев.
- `GET /docs` — интерактивная документация.

Коды ошибок: `404` — запись не найдена, `422` — невалидные данные, `409` — нарушение уникальности или внешнего ключа.

---

## Примеры запросов

Создать пользователя:

```bash
curl -X POST http://localhost:8000/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","display_name":"Alice","role":"admin"}'
```

Ответ `201 Created`:

```json
{
  "id": 1,
  "email": "alice@example.com",
  "display_name": "Alice",
  "role": "admin",
  "created_at": "2026-10-14T13:00:16.019Z"
}
```

Создать задачу:

```bash
curl -X POST http://localhost:8000/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"title":"Ship it","priority":"high"}'
```

Ответ `201 Created`:

```json
{
  "id": 1,
  "project_id": 1,
  "assignee_id": null,
  "label_id": null,
  "title": "Ship it",
  "description": null,
  "status": "open",
  "priority": "high",
  "created_at": "2026-10-14T13:05:11.412Z",
  "updated_at": "2026-10-14T13:05:11.412Z"
}
```

Список задач с фильтрами:

```bash
curl "http://localhost:8000/v1/tasks?project_id=1&status=open"
```

Изменить статус задачи:

```bash
curl -X PATCH http://localhost:8000/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}'
```

Удалить проект (задачи и комментарии удалятся каскадом):

```bash
curl -X DELETE http://localhost:8000/v1/projects/1
```

Проверка БД:

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "database": "up"}
```

---

## Миграции

Применяются автоматически при `docker compose up`. Вручную — из контейнера:

```bash
docker compose exec api alembic current
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade base
```

Полный цикл проверки:

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic downgrade base
docker compose exec api alembic upgrade head
```

Создание новой миграции (локально, нужен Python с зависимостями и запущенный `db`):

```bash
alembic revision --autogenerate -m "описание изменения"
```

Схема меняется только миграциями — `Base.metadata.create_all()` не используется.