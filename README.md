# JWT Auth Project

Проект на Django с JWT аутентификацией, ролями и правами доступа.

## Функционал

- Регистрация и вход пользователей через email и пароль
- JWT-аутентификация
- "Мягкое удаление аккаунта"
- Система ролей: Moderator, User
- Ограничения доступа на основе ролей
- Swagger документация API

## Структура прав доступа
Каждому пользователю назначается роль, а ролям присваиваются разрешенные действия над ресурсами

### Роли
- User - базовая модель пользователя
- Moderator - модель пользователя имеющая расширенные права

### Ресурсы:
- Profile - профиль
- NewFeed - новостная лента

### Разрешения к ресурсам
| Роль      | Просмотр | Создание | Редактирование | Удаление |
|-----------|----------|----------|----------------|----------|
| User      | ✅        | ❌        | ❌              | ❌        |
| Moderator | ✅        | ✅        | ✅              | ✅        |


Каждое действие проверяется через `has_permission()`

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Ilya-Tretyak/jws_auth_project
   cd jws_auth_project
   ```
2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv env
   source env/bin/activate   # Linux/Mac
   env\Scripts\activate      # Windows
   ```
3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```
   
4. Выполните миграции и инициализируйте роли и права:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py create_test_users
   ```
   Создаются пользователи:

| email        | first_name | last_name    | password     |
|--------------|------------|--------------|--------------|
| mod@mail.ru  | Илья       | Модератор    | modpassword  |
| user@mail.ru | Илья       | Пользователь | userpassword |
   
5. Запустите сервер:

   ```bash
   python manage.py runserver
   ```
   
## API

Swagger доступен по адресу: http://127.0.0.1:8000/swagger/

### Регистрация

`POST /api/auth/register/`  
Параметры: 'email', 'first_name', 'last_name', 'password', 'password2'

### Вход (Login)

`POST /api/auth/login/`  
Проверяет есть ли в бд истекшие токены в БД.
Возвращает JWT токены (access_token и refresh_token).

### Обновление access-токена

`POST /api/auth/refresh/`
Возвращает JWT токен (access_token).

### Выход (Logout)

`POST /api/auth/logout/`
Удаляет refresh токен из базы, возвращает `204 No Content`

### Профиль пользователя

- `GET /api/auth/user/` — просмотр профиля (доступно для всех ролей)
- `PUT /api/auth/user/` — редактирование профиля (доступно для всех ролей)
- `DELETE /api/auth/user/` — "мягкое" удаление аккаунта (активность false)

### Назначение ролей

-`POST api/auth/user/<int:user_id>/roles/`
Модератор имеет возможность изменять роли пользователей с помощью API.

### Новостная лента

- `GET /api/auth/feed/` — просмотр новостей (только для модераторов и пользователей)
- `POST /api/auth/feed/` — создание новости (только для модераторов)
- `DELETE /api/auth/feed/{post_id}/` — удаление новости по ID (только для модераторов)

## Авторизация

Все запросы, кроме регистрации и логина, требуют заголовок:
    `Authorization: Bearer <JWT_TOKEN>`
