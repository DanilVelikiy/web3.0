# Нулевой шаг. Поднять django+postgers+gunicorn+nginx

## Зависимости
Обновление пакетов
```sh
sudo apt update
```
установка пакетов 
```sh
sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl
```
## Создадим БД и аккаунт в PostgreSQL
```sh
sudo -u postgres psql
```
```sh
CREATE DATABASE myproject;
```
```sh
CREATE USER root WITH PASSWORD 'password';
```
Чтобы упростить дальнейшую работу, сразу зададим ряд настроек. Например, изменим кодировку на UTF-8, зададим схему изоляции транзакций «read committed», установим часовой пояс:
```sh
ALTER ROLE root SET client_encoding TO 'utf8';
ALTER ROLE root SET default_transaction_isolation TO 'read committed';
ALTER ROLE root SET timezone TO 'UTC';
```
Теперь для нового пользователя надо открыть доступ на администрирование БД:
```sh
GRANT ALL PRIVILEGES ON DATABASE myproject TO root;
```
выход
```sh
\q
```


## Создадим виртуальную среду Python


Теперь пришло время для установки Django, Gunicorn и адаптера psycopg2 PostgreSQL:
```sh
pip install django gunicorn psycopg2-binary
```

## Сделаем свой проект Django и настроим его

Нахожусь я в папке `www-data`

```sh
django-admin startproject django_server /home/danil/www-data/
```

В конфигурационном файле
```sh
sudo vim settings.py
```
прописать хосты в settings.py
```sh
ALLOWED_HOSTS = ['ds4life.ru', '192.168.1.110', 'localhost']
```

прописать БД в settings.py
```sh
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'myproject',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

Остается в «хвосте» внести параметр, фиксирующий место, где хранить статичные файлы. Это понадобится для Nginx, который мы настроим в паре с PostgreSQL.
```sh
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
```

## Завершим задачу настройки

Миграции
```sh
python3 manage.py makemigrations
```

```sh
python3 manage.py migrate
```

Создание суперпользователя администрирующего проект
```sh
python3 manage.py createsuperuser
```
Пользователь например как в системе

Если планируется собирать весь статичный контент в одной папке,собрать их в папку командой:
```sh
python3 manage.py collectstatic
```

возможность подключения в брандмауэре UFW:
```sh
sudo ufw allow 8000
```

Запуск сервер  Django
```sh
python3 manage.py runserver 0.0.0.0:8000
```

И сервер будет доступен по адресу
```sh
http://localhost:8000/
```

## Файлы сокета и systemd для Gunicorn

`gunicorn.service` в папке `/etc/systemd/system`
```sh
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=danil
Group=adm     
WorkingDirectory=/home/danil/www-data    
ExecStart=/home/danil/www-data/venv/bin/gunicorn \            
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
	  --chdir /home/danil/www-data \
          django_server.wsgi:application

Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Запуск службы
```sh
sudo systemctl start gunicorn.socket
```

Разрешить автозапуск
```sh
sudo systemctl enable gunicorn.socket
```

Перечитать службы
```sh
sudo systemctl daemon-reload
```

Рестарт службы
```sh
sudo systemctl restart gunicorn
```

Проверка статуса
```sh
sudo systemctl status gunicorn.socket
```

Посмотреть журнал
```sh
sudo journalctl -u gunicorn
```

## Nginx как прокси для Gunicorn

Создать и открыть модуль
```sh
sudo nvim /etc/nginx/sites-available/www-data
```

Наполнение
```sh
server {
    listen 80;
    server_name 127.0.0.1 ds4life.ru www.ds4life.ru;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/danil/www-data;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Активировать его путем привязки к папке sites-enabled:
```sh
sudo ln -s /etc/nginx/sites-available/www-data /etc/nginx/sites-enabled
```

Добавить пользователя www-data в группу текущего пользователя
```sh
sudo usermod -a -G ${USER} www-data
```

Перезапустить веб-сервер:
```sh
sudo systemctl restart nginx
```
# Источник
```sh
https://timeweb.cloud/tutorials/django/kak-ustanovit-django-nginx-i-gunicorn-na-virtualnyj-server
```

