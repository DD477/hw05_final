[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)


# Проект "Yatube"

## Описание:
Cоциальная сеть для публикации личных дневников.
Сервис позволяет:
-   регистрироваться, восстанавливать пароль по почте;
-   создавать личную страницу, для публикации записей;
-   создавать и редактировать свои записи;
-   просматривать страницы других авторов;
-   комментировать записи других авторов;
-   подписываться на авторов;
-   записи можно отправлять в определённую группу;
-   модерация записей, работа с пользователями, создание групп осуществляется через панель администратора;


## Оглавление

* [Как запустить проект](#как-запустить-проект)
* [Необходимый софт](#необходимый-софт)
* [Использованные технологии](#использованные-технологии)


## Как запустить проект:
- Клонировать репозиторий 
   ```sh
   git clone https://github.com/DD477/hw05_final.git
   ```
- Перейти в папку с проектом
   ```sh
   cd hw05_final.git
   ```
- Cоздать и активировать виртуальное окружение
   ```sh
   python3 -m venv venv
   ```
   ```sh
   source venv/bin/activate
   ```
- Обновить менеджер пакетов (pip)
   ```sh
   pip install --upgrade pip
   ```
- Установить зависимости из файла requirements.txt
   ```sh
   pip install -r requirements.txt
   ```
- Создать миграции
  ```sh
  python ./yatube/manage.py makemigrations
  python ./yatube/manage.py migrate
  ```
- Создать суперпользователя 
  ```sh
  python ./yatube/manage.py createsuperuser
  ```
- Запустить сервера
  ```sh
  python ./yatube/manage.py runserver
  ```
- Сайт запуститься по адресу http://127.0.0.1:8000

## Необходимый софт:
- [Python](https://www.python.org/) 3.8.10 или выше

## Использованные технологии:
- [Django](https://www.djangoproject.com/) 3.2.3
- [Pillow](https://pillow.readthedocs.io/en/stable/) 9.2.0
- [sorl-thumbnail](https://pypi.org/project/sorl-thumbnail/) 12.7.0
- [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/) 3.2.4

## Автор:
[Dmitry Dobrodeev](https://github.com/DD477)

## Лицензия:
- MIT
