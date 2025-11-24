# Блог API - Django Backend

## Установка и запуск

### Вариант 1: Docker Compose (рекомендуется)

1. Клонируйте репозиторий или скопируйте файлы проекта

2. Запустите проект:
```bash
docker-compose up --build
```

3. Проект будет доступен по адресу: `http://localhost:8001`

4. Создайте суперпользователя для доступа к админ-панели:
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Админ-панель доступна по адресу: `http://localhost:8001/admin`

### Вариант 2: Локальная установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example`:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_HOST=localhost
DB_NAME=blogdb
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

3. Убедитесь, что PostgreSQL запущен и создана база данных `blogdb`

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация

#### Регистрация
```
POST /api/auth/register
Body: {
    "username": "user123",
    "password": "password123"
}
Response: {
    "token": "generated-token-here"
}
```

#### Вход
```
POST /api/auth/login
Body: {
    "username": "user123",
    "password": "password123"
}
Response: {
    "token": "generated-token-here"
}
```

### Статьи

#### Список статей
```
GET /api/articles
Response: [
    {
        "id": 1,
        "title": "Заголовок",
        "content": "Содержание",
        "author_id": 1,
        "author_username": "user123",
        "category": {...},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

#### Получить статью
```
GET /api/articles/{id}
Response: {
    "id": 1,
    "title": "Заголовок",
    ...
}
```

#### Создать статью
```
POST /api/articles
Headers: Authorization: Bearer <token>
Body: {
    "title": "Новая статья",
    "content": "Текст статьи",
    "category_id": 1  // опционально
}
```

#### Обновить статью
```
PUT /api/articles/{id}
Headers: Authorization: Bearer <token>
Body: {
    "title": "Обновленный заголовок",  // опционально
    "content": "Обновленный текст",     // опционально
    "category_id": 2                    // опционально
}
```

#### Удалить статью
```
DELETE /api/articles/{id}
Headers: Authorization: Bearer <token>
Response: {
    "success": true
}
```

### Комментарии

#### Список комментариев
```
GET /api/comments
Response: [
    {
        "id": 1,
        "article_id": 1,
        "article_title": "Заголовок статьи",
        "author_id": 1,
        "author_username": "user123",
        "content": "Текст комментария",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

#### Получить комментарий
```
GET /api/comments/{id}
```

#### Создать комментарий
```
POST /api/comments
Headers: Authorization: Bearer <token>
Body: {
    "article_id": 1,
    "content": "Текст комментария"
}
```

#### Обновить комментарий
```
PUT /api/comments/{id}
Headers: Authorization: Bearer <token>
Body: {
    "content": "Обновленный текст"
}
```

#### Удалить комментарий
```
DELETE /api/comments/{id}
Headers: Authorization: Bearer <token>
Response: {
    "success": true
}
```

## Тестирование

Запуск всех тестов:
```bash
python manage.py test
```


## Логирование

Логи записываются в файл `blog.log` и выводятся в консоль. Логируются:
- Регистрация и вход пользователей
- CRUD операции со статьями
- CRUD операции с комментариями
- Ошибки и предупреждения

## Примеры использования

### Регистрация и создание статьи

```bash
# Регистрация
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Сохраните полученный токен
TOKEN="your-token-here"

# Создание статьи
curl -X POST http://localhost:8001/api/articles \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Моя первая статья",
    "content": "Текст статьи здесь",
    "category_id": 1
  }'
```

### Получение списка статей

```bash
curl http://localhost:8001/api/articles
```

### Создание комментария

```bash
curl -X POST http://localhost:8001/api/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "article_id": 1,
    "content": "Отличная статья!"
  }'
```

## Примечания

- Токен авторизации можно передавать в заголовке `Authorization: Bearer <token>` или в body запроса как `{"token": "..."}`
- Пользователь может редактировать и удалять только свои статьи и комментарии
- Все публичные endpoints (GET) доступны без авторизации
- Для создания, обновления и удаления требуется авторизация

## Разработка

Для разработки рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
