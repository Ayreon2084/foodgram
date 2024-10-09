## **Проект "Foodgram".**
---

Проект доступен по следующим адресам:
- https://foodgramm.servebeer.com/
- 89.169.165.78:8000

### **Документация:**

- Загрузить на [сайт](https://redocly.github.io/redoc/) файл openapi-schema.yml из директории, находящейся в корневой директории проекта:

```sh {"id":"01J9RE8JX0VV941MMB28MZ4DYV"}
./docs/openapi-schema.yml
```

### **Описание:**

На сайте пользователи могут:
- Просматривать рецепты.
- Публиковать, редактировать и удалять свои рецепты.
- Подписываться на публикации других пользователей.
- Добавлять рецепты в список избранного.
- Добавлять рецепты в список покупок. 
- Скачивать файл со списком покупок с необходимыми ингредиентами и их количеством.

### **Технологии:**

- [Django 3.2.16](https://docs.djangoproject.com/en/5.0/releases/3.2.16/)
- [Django Debug Toolbar 3.8.1](https://pypi.org/project/django-debug-toolbar/3.8.1/)
- [Django Filter 23.1](https://pypi.org/project/django-filter/23.1/)
- [Django REST Framework 3.12.4](https://www.django-rest-framework.org/community/release-notes/#312x-series)
- [Django REST Framework SimpleJWT 4.8.0](https://pypi.org/project/djangorestframework-simplejwt/4.8.0/)
- [Djoser 2.1.0](https://pypi.org/project/djoser/2.1.0/)
- [Gunicorn 20.1.0](https://docs.gunicorn.org/en/20.1.0/)
- [Isort 5.13.2](https://pycqa.github.io/isort/)
- [Pillow 9.0.0](https://pypi.org/project/pillow/9.0.0/)
- [Psycopg2 2.9.3](https://pypi.org/project/psycopg2/2.9.3/)
- [Python 3.9.13](https://www.python.org/downloads/release/python-3913/)

### **Деплой:**

- [Пошаговая инструкция](https://github.com/Ayreon2084/foodgram/blob/main/DEPLOY.md)

### **Примеры запросов:**

#### **1. POST | Создание рецепта:**
**http://127.0.0.1:8000/api/recipes/**


Request:

```sh {"id":"01J9REFRJP1NHFGG5AX81R8RG7"}
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Response:

```sh {"id":"01J9REG169EWGD7DYBFBT7AQP6"}
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "^w\\z",
    "first_name": "Вася",
    "last_name": "Иванов",
    "is_subscribed": false,
    "avatar": "http://foodgram.example.org/media/users/image.png"
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "text": "string",
  "cooking_time": 1
}
```

#### **2. POST | Подписка на пользователя:**
**http://127.0.0.1:8000/api/users/{id}/subscribe/**

Response:

```sh {"id":"01J9RENSNKYQJ4TNRHWXBRDKSE"}
{
  "email": "user@example.com",
  "id": 0,
  "username": "^w\\z",
  "first_name": "Вася",
  "last_name": "Иванов",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.png",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0,
  "avatar": "http://foodgram.example.org/media/users/image.png"
}
```

#### **3. POST | Подписка на пользователя:**
**http://127.0.0.1:8000/api/users/{id}/shopping_cart/**

Response:

```sh {"id":"01J9RERT821TT8292DRK1PQZC4"}
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.png",
  "cooking_time": 1
}
```

### **Автор:**

- Разработчик: [Alexander Zhukov](https://github.com/Ayreon2084)

