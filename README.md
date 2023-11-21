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

# Первый шаг. Поднять титульную страничку.

Склонировать из гита титульную страницу в соответствующую папку в проекте
И сконфигурировать nginx 
```sh
sudo nvim /etc/nginx/sites-available/www-data
```

вот так
```sh
server {
    
    listen 80;
    server_name 127.0.0.1 ds4life.ru www.ds4life.ru;

    root /home/danil/www-data/web_titul;

    index index.html;

}
```

# Второй шаг. Поднять django веб-приложение с проектами (в процессе не все получается)

Создать веб приложение (все в активированной виртуально среде)
```sh
python manage.py startapp projects
```

добавить его в `django_server/settings.py` в `INSTALLED_APPS`
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'projects'
]
```

Прописать путь для шаблона базового
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["django_server/templates/"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },    
    },    
]

```

В основном `urls.py` добавить:
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('/projects', include('projects.urls')),
]
```

В `urls.py` веб приложения добавить
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.project_index, name="project_index"),
    path("<int:pk>/", views.project_detail, name='project_detail'),
]
```

В `views.py` веб приложения добавить
```python
from django.shortcuts import render
from projects.models import Project

def project_index(request):
    projects = Project.objects.all()
    context = {
        'projects': projects
    }

    return render(request, 'project_index.html', context)

def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    context = {
        'project': project
    }

    return render(request, 'project_detail.html', context)
```

В `models.py` веб приложения добавить
```python
from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    technology = models.CharField(max_length=20)
    image = models.FilePathField(path="/img")
    target = models.TextField(default=None, null=True)
    target = models.TextField(default=None , null=True)
    block_1_text = models.TextField(default=None, null=True)
    block_1_image = models.FilePathField(path="/img", default=None, null=True)
    block_2_text = models.TextField(default=None , null=True)
    block_2_image = models.FilePathField(path="/img" , default=None , null=True)
    block_3_text = models.TextField(default=None , null=True)
    block_3_image = models.FilePathField(path="/img" , default=None , null=True)
#    paragraph_txt_1 = models.TextField(default=None, null=True)
#    paragraph_img_1 = models.FilePathField(path="/img" , default=None , null=True)
    # сылку на гитхаб надо еще
```

Создать папку `templates` и в ней два файла шаблонов.
Перывй шаблон `project_detail.html` - шаблон даталей о конкретном проекте, описание и прочее
```python
{% extends "base.html" %}
{% load static %}
{% block page_content %}
<h1>{{ project.title }}</h1>
<div class="row"></div></div>
<div class="row">
    <div class="col-md-4">
        <h5>About the project:</h5>
        <p>{{ project.description }}</p>
        <br>
        <h5>Technology used:</h5>
        <p>{{ project.technology }}</p>
        <h5>Target:</h5>
        <p>{{ project.target }}</p>
    </div>
    <div class="col-md-8">
        <img src="{% static project.image %}" alt="" width="100%">
        <h5>Решение:</h5>
        <p>{{ project.block_1_text }}</p>
        <img src="{% static project.block_1_image %}" alt="" width="100%">
        <p>{{ project.block_2_text }}</p>
        <img src="{% static project.block_2_image %}" alt="" width="100%">
        <p>{{ project.block_3_text }}</p>
        <img src="{% static project.block_3_image %}" alt="" width="100%">
    </div>
</div>
{% endblock %}
```

Второй шаблон `project_index.html` - шаблон списка проектов
```python
{% extends "base.html" %}
{% block page_content %}
{% load static %}
<h1 class="brand"></h1>
<div class="row">
{% for project in projects %}
    <div class="landing-section col-md-4">
        <div class="card mb-2">
            <img class="card-img-top" src="{% static project.image %}">
            <div class="card-body">
                <h5 class="brand-text card-title">{{ project.title }}</h5>
                <p class="card-text">{{ project.description }}</p>
                <a href="{% url 'project_detail' project.pk %}"
                   class="btn btn-primary">
                    Read More
                </a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```

И еще должен быть шаблон `base.html` в `django_server/templates`
```python
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">


{% block page_content %}{% endblock %}

<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
```

Создать папку для статических файлов `static` и в ней для изображений `img` и в ней поместить изображения

Бэкап восстановлю в БД и проведу миграции


! ! ! НЕ РАБОТАЕТ ВОЗВРАЩАЕТ ПУСТУЮ СТРАНИЦУ 
`[17/Nov/2023 11:36:59] "GET /projects/ HTTP/1.1" 200 858`




