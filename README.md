# SIDC-Hogs-Disease-Surveillance

Backend Setup Instructions

## Setup Linux Environment

Step 1. POWERSHELL >  initial wsl setup

```powershell
wsl --install
```

Step 2. POWERSHELL > install Ubuntu

```powershell
wsl --install -d Ubuntu
```

Step 3. BASH > add python repository

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

Step 4. BASH > get things up to date

```bash
sudo apt update
sudo apt upgrade
```

Step 5. BASH > get python3.9

```bash
sudo apt install python3.9 python3.9-venv python3.9-dev
```

## Setup Github on VS Code

Step 1. BASH > check if Git is installed

```bash
git --version
```

Step 2. BASH > setup Git config file

```bash
git config --global user.name "Your Name"
git config --global user.email "yourEmail@example.com"
```

Step 3. BASH > Open VS Code and make sure Github extension is installed

```bash
code .
```

Step 4. CODE > Clone Repository: <https://github.com/kaylalatorre/SIDC-Hogs-Disease-Surveillance.git>

```text
Ctrl + Shift + P
```

## Setup Conda Virtual Environment

Step 1. BASH > Install Conda

```bash
bash /location/of/Miniconda3-latest-Linux-x86_64.sh
```

> Download Miniconda from <https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh>
>
>Anaconda can also be used but Miniconda is smaller

Step 2. BASH > Add Conda Forge to channels

```bash
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
```

Step 3. BASH > create virtual environment

```bash
conda create -p ~/SIDC-Hogs-Disease-Surveillance/venv uWSGI Python Django djangorestframework GeoPandas PostGis psycopg2
```

>Can also use:
>
>```bash
>conda create -p ~/SIDC-Hogs-Disease-Surveillance/venv --file venv.txt
>```

Step 4. BASH > activate project environment

```bash
conda activate /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/venv
```

>Can also be activated by running
>
>```bash
>conda activate ./venv inside the project directory
>```

Step 5. BASH > export project environment package list [OPTIONAL]

```bash
conda list --explicit > venv.txt
```

## Setup Nginx

Step 1. BASH > install then start nginx to make sure it works properly in <http://localhost:80>

```bash
sudo apt install nginx
sudo /etc/init.d/nginx start
```

Step 2: BASH > add nginx to user group and vise versa

```bash
sudo usermod -a -G tsongzzz www-data
sudo usermod -a -G www-data tsongzzz 
```

Step 3: BASH > restart nginx

```bash
sudo /etc/init.d/nginx restart
```

## Setup Django

Step 1: BASH > create a new Django project

```bash
django-admin.py startproject src
```

> rename to backend

Step 2: BASH > apply initial migrations

```bash
python manage.py migrate
```

Step 3: BASH > test if Django is running properly with uWSGI http://localhost:8000

```bash
uwsgi --http :8000 --module src.wsgi
```

Step 4: PYTHON - BASH > Define static file directory in settings.py then collect

```python
import os
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
```

```bash
python manage.py collectstatic
```

Step 5: BASH > copy uwsgi_params to project folder

```bash
cp /etc/nginx/uwsgi_params /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/
```

Step 6: FILE > create src_nginx.conf in ./backend/

```bash
# src_nginx.conf

# the upstream component nginx needs to connect to
upstream django {
    server unix:///home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/mysite.sock; # for a file socket
    # server 127.0.0.1:8001; # for a web port socket
}

# configuration of the server
server {
    # the port your site will be served on
    listen      8000;
    # the domain name it will serve for
    server_name localhost; # substitute your machine's IP address or FQDN
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    # Django media
    location /media  {
        alias /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/uwsgi_params; # the uwsgi_params file you installed
    }
}
```

Step 7: BASH > symlink 'src_nginx.conf' to '/etc/nginx/sites-available/' and '/etc/nginx/sites-enabled/'

```bash
sudo ln -s /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/src_nginx.conf /etc/nginx/sites-available/
sudo ln -s /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/src_nginx.conf /etc/nginx/sites-enabled/
```

> verify symlink

```bash
cat /etc/nginx/sites-available/src_nginx.conf
cat /etc/nginx/sites-enabled/src_nginx.conf
```

Step 8: BASH > Verify if Django + uWSGI + nginx is running

```bash
uwsgi --socket mysite.sock --module mysite.wsgi --chmod-socket=664
```

Step 9: FILE > create src_uwsgi.ini

```bash
# src_uwsgi.ini file
[uwsgi]

# Django-related settings
# the base directory (full path)
chdir           = /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend
# Django's wsgi file
module          = src.wsgi
# the virtualenv (full path)
home            = /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/venv

# process-related settings
# master
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = /home/tsongzzz/SIDC-Hogs-Disease-Surveillance/backend/mysite.sock
# ... with appropriate permissions - may be needed
chmod-socket    = 664
# clear environment on exit
vacuum          = true
```

Step 9: BASH > run application through src_uwsgi.ini

```bash
uwsgi --ini src_uwsgi.ini
```
