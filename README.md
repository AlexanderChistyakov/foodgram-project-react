#  [Foodgram][site_result]

## Фудграм - блог для пользователей, готовых делиться своими рецептами. 

## Блог включает в себя:

- Систему постов-рецептов.
- Базу ингредиентов, реализованных через отдельную модель.
- Модель тегов.
- Подписки пользователей на авторов.
- Добавление рецептов в избраное и в корзину. 
- Скачивание списка ингредиентов из корзины в txt-файл.

## Стек

Фудграм использует следующие доступные технологии:

- [Python] - язык бекенда приложения версии 3.9 и выше
- [DjangoFramework] - основной фреймворк приложения
- [DRF] - для реализации API
- [Djoser] - Регистрация и аутентификация пользователей
- [PostgreSQL] - Работа с базой данных
- [Frontend] - Фронт, предоставленный Практикумом


   [site_result]: <https://chstykv.webhop.me/>
   [DjangoFramework]: <https://docs.djangoproject.com/en/4.2/releases/3.2/>
   [DRF]: <https://www.django-rest-framework.org/t>
   [Frontend]: <https://github.com/yandex-praktikum/foodgram-project-react>
   [Djoser]: <https://djoser.readthedocs.io/en/latest/getting_started.html>
   [PostgreSQL]: <https://www.postgresql.org/>
   [Python]: <https://www.python.org/>


## Локальная установка и запуск приложения Фудграм

Для локальной разработки проекта проверьте версию [Python](https://www.python.org/), установленную в вашей операционной системе. Обновите Python до версии 3.9 и выше. Форкните [репозиторий Foodgram](https://github.com/AlexanderChistyakov/foodgram-project-react) в ваш гитхаб и следуйте инструкции ниже.

1. В терминале создайте папку проекта, перейдите в нее для клонирования репозитория.

```sh
git clone git@github.com:YourGitHubName/foodgram-project-react.git
```

2. Разверните виртуальное окружение

Windows:
```sh
python -m venv venv
```
Linux, MacOS:
```sh
python3 -m venv venv
```
Далее в инструкции будем использовать команду "python".

3. в директории с папкой venv активируйте виртуальное окружение

Windows:
```sh
source venv\Scripts\activate
```
Linux, MacOS:
```sh
source venv\bin\activate
```
4. Перейдите в папку с файлом requirements.txt и установите зависимости
```sh
pip install -r requirements.txt
```
5. В той же папке введите команды применения миграций проекта.
```sh
python manage.py makemigrations
python manage.py migrate
```
6. После применения миграций можно ввести команду создания суперпользователя и следовать указаниям терминала
```sh
python manage.py createsuper
```
7. Запуск локального сервера

```sh
python manage.py runserver
```

8. В адресной строке браузера наберите адрес API или админки и проверьте работу сайта

```sh
http://127.0.0.1:8000/api/
http://127.0.0.1:8000/admin/
```

## Разворачивание проекта в Docker на удаленном сервере

Деплой проекта на сервер происходит по этапам, описанным в файле .github\workflows\main.yml. Перед первым деплоем проекта необходимо в Secrets репозитория указать значения некоторых констант.


- Константы для settings проекта
```sh
ALLOWED_HOSTS
SECRET_KEY
DEBUG
```

- Аутентификация в Докере
```sh
DOCKER_PASSWORD
DOCKER_USERNAME
```
- Доступ к БД PostgreSQL
```sh
POSTGRES_DB
POSTGRES_PASSWORD
POSTGRES_USER
```
- Доступ к БД в Dockernetwork
```sh
DB_HOST
DB_NAME
DB_PORT
```
- Данные удаленного сервера
```sh
HOST
SSH_KEY
SSH_PASSPHRASE
USER
```
- ID пользователя в Telegram и токен телеграм-бота для сообщения об успешном деплое.
```sh
TELEGRAM_TO
TELEGRAM_TOKEN
```

Примеры значений переменных:
```sh
ALLOWED_HOSTS = localhost, 127.0.0.1, mysiteaddress.com
SECRET_KEY = ***
DEBUG = False

DOCKER_PASSWORD = ****
DOCKER_USERNAME = your_username

POSTGRES_DB = db
POSTGRES_PASSWORD = ***
POSTGRES_USER = pg_user

DB_HOST = db
DB_NAME = db
DB_PORT = 5432

HOST = IP-адрес сервера
SSH_KEY = публичный ключ
SSH_PASSPHRASE = ***
USER = server_user

TELEGRAM_TO = 123456789
TELEGRAM_TOKEN = ****
```

Инструкция main.yml предусматривает деплой проекта после каждого пуша изменений в репозиторий на гит. Первичный деплой проекта тоже происходит после этой команды

```sh
git push
```

> Первичное разворачивание контейнеров на сервере производится по инструкции в файле docker-compose.yml. 
> Далее каждый деплой изменений в проекте происходит по инструкции docker-compose.production.yml.
> Оба файла копируются на сервер автоматически после срабатывания скрипта из main.yml. 
> Файл .env с переменными окружения формируется по инструкции из main.yml, значения переменных берутся в Secrets.