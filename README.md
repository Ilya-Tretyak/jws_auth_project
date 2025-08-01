# JWT Auth Project

Проект на Django с JWT аутентификацией, ролями и правами доступа.

## Функционал

- Регистрация и вход пользователей через email и пароль
- JWT-аутентификация
- Роли: **Moderator** и **User**
- Ресурсы: **Profile** и **NewsFeed**
- Права доступа:
  - Оба роли могут читать, редактировать и "мягко" удалять профиль
  - Оба роли могут читать записи в новостной ленте
  - Только модератор может создавать, редактировать и удалять записи в новостной ленте
- Swagger документация API

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/твой_ник/my-django-auth-project.git
   cd my-django-auth-project
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
   
5. Запустите сервер:

   ```bash
   python manage.py runserver
   ```
   
## Документация API

Swagger доступен по адресу: http://127.0.0.1:8000/swagger/

### Регистрация

`POST /api/auth/register/`  
Параметры: 'email', 'first_name', 'last_name', 'password', 'password2'

### Вход (логин)

`POST /api/auth/login/`  
Возвращает JWT токен.

### Профиль пользователя

- `GET /api/auth/user/` — просмотр профиля (доступно для всех ролей)
- `PUT /api/auth/user/` — редактирование профиля (доступно для всех ролей)
- `DELETE /api/auth/user/` — "мягкое" удаление аккаунта (активность false)

### Новостная лента

- `GET /api/auth/feed/` — просмотр новостей (только для модераторов и пользователей)
- `POST /api/auth/feed/` — создание новости (только для модераторов)
- `DELETE /api/auth/feed/{post_id}/` — удаление новости по ID (только для модераторов)

## Авторизация

Все запросы, кроме регистрации и логина, требуют заголовок:
    `Authorization: Bearer <JWT_TOKEN>`
