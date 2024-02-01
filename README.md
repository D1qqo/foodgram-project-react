# Foodgram описание:

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

# Стек используемых технологий:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL

# Команды для разворачивания проекта на сервере:

Создать и запустить контейнеры Docker:
```
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

Создать суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

Собрать статику:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
```

# Автор backend:

Казачков Эдуард
