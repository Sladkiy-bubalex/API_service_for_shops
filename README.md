# API для работы с магазином

## Техническая документация

Документация API находится в файле [здесь](backend_service/Entry_points.md)

## Запуск проекта

Для запуска проекта необходимо выполнить следующие шаги:

1. Установить зависимости:
```bash
pip install -r requirements.txt
```

2. Создать базу данных PostgreSQL [инструкция тут](https://postgrespro.ru/docs/postgresql/15/app-createdb)
3. В корне проект создать файл .env и ввести данные для подключения к базе данных в формате:
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=
SECRET_KEY=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```
4. Заполнить данные для подключения к базе данных в файле .env
5. Определить эл.почту для отправки писем и знанести в переменную EMAIL_HOST_USER в файле .env
6. Создать SMTP пароль в почтовом сервисе [пример для mail.ru](https://help.mail.ru/mail/mailer/password/)
7. Занести данные в переменные EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_PASSWORD в файле .env

8. Создать таблицы в базе данных:
```bash
python manage.py migrate
```

9. Запустить сервер:
```bash
python manage.py runserver
```

## Стэк технологий

- Python 3.12
- Django 5.2
- Django REST framework 3.14
- Django-filter 25.1
- PyJWT 2.10.1
