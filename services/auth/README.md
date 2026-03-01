# Auth Service | Whybist

Микросервис авторизации и управления учетными записями пользователей для проекта Whybist. Отвечает за безопасное хранение данных пользователей, хэширование паролей и выпуск JWT-токенов.

## Стек технологий
* **Фреймворк:** FastAPI
* **База данных:** PostgreSQL (асинхронный драйвер `asyncpg`)
* **ORM & Миграции:** SQLAlchemy 2.0 + Alembic
* **Аутентификация:** JWT (JSON Web Tokens), bcrypt
* **Валидация:** Pydantic V2

## Переменные окружения (.env)
Для запуска сервиса локально, создайте файл `.env` в корне сервиса:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/whybist_auth
SECRET_KEY=your-secret-jwt-key
```
## Запуск для разработки

    Установите зависимости (используется Poetry):
    poetry install --no-root

    Примените миграции БД:
    poetry run alembic upgrade head

    Запуск:
    poetry run uvicorn app.service:app --reload --port 8001

Swagger UI будет доступен по адресу: http://localhost:8001/docs  
Основные эндпоинты

    POST /register — Регистрация нового пользователя

    POST /login — Авторизация (получение Access & Refresh токенов)

    GET /me — Получение данных текущего пользователя

    PATCH /me — Обновление email или username

    POST /me/change-password — Смена пароля