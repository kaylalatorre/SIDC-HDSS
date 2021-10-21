# SIDC-HDSS
SIDC-HDSS is a web application with features to help the cooperative with farm biosecurity management, hogs health tracking, disease tracking, and decision support. 

# Setting Up the Project Locally

## Setup Linux Environment
Linux username: tsongzzz

Step 1: POWERSHELL >  initial wsl setup

```powershell
wsl --install
```

Step 2: POWERSHELL > install Ubuntu

```powershell
wsl --install -d Ubuntu
```

Step 3: BASH > add python repository

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

Step 4: BASH > get things up to date

```bash
sudo apt update
sudo apt upgrade
```

Step 5: BASH > get python3.9

```bash
sudo apt install python3.9 python3.9-venv python3.9-dev
```

## Setup Github on VS Code

Step 1: BASH > check if Git is installed

```bash
git --version
```

Step 2: BASH > setup Git config file

```bash
git config --global user.name "Your Name"
git config --global user.email "yourEmail@example.com"
```

Step 3: BASH > Open VS Code to make sure extensions are installed

```bash
code .
```
> GitHub Pull Requests and Issues https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github
>
> Remote - WSL https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl

Step 4: CODE > Clone Repository: <https://github.com/kaylalatorre/SIDC-HDSS.git>
> Ctrl + Shift + P > Search Git: Clone > Clone from Github > Enter Repository URL

## Setup Conda Virtual Environment

Step 1: BASH > Install Conda

```bash
bash /location/of/Miniconda3-latest-Linux-x86_64.sh
```

> Download Miniconda from <https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh>
>
> Anaconda can also be used but Miniconda is smaller
>
> If conda is not activated:
> 
> ```bash
> eval "$(/home/tsongzzz/miniconda3/bin/conda shell.bash hook)"
> ```

Step 2: BASH > Add Conda Forge to channels

```bash
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
```

Step 3: BASH > create virtual environment

```bash
conda create -p ~/SIDC-HDSS/venv uWSGI Python Django djangorestframework GeoPandas PostGis psycopg2
```

>Can also use:
>
>```bash
>conda create -p ~/SIDC-HDSS/venv --file venv.txt
>```

Step 4.1: BASH > activate project environment

```bash
conda activate /home/tsongzzz/SIDC-HDSS/venv
```

>Can also be activated by running
>
>```bash
>conda activate ./venv # inside the project directory
>```

[OPTIONAL] Step 4.2: BASH > export project environment package list

```bash
conda list --explicit > venv.txt
```

## Setup Nginx

Step 1: BASH > install then start nginx to make sure it works properly in <http://localhost:80>

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
### Skip to step 8 if pulled files in this repository

Step 1: BASH > create a new Django project

```bash
django-admin.py startproject src
```

> rename to app

Step 2: BASH > apply initial migrations

```bash
python manage.py migrate
```

Step 3: BASH > test if Django is running properly with uWSGI <http://localhost:8000>

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
cp /etc/nginx/uwsgi_params /home/tsongzzz/SIDC-HDSS/app/
```

Step 6: FILE > create src_nginx.conf in /app

```bash
# src_nginx.conf

# the upstream component nginx needs to connect to
upstream django {
    server unix:///home/tsongzzz/SIDC-HDSS/app/src.sock; # for a file socket
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
        alias /home/tsongzzz/SIDC-HDSS/app/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /home/tsongzzz/SIDC-HDSS/app/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     /home/tsongzzz/SIDC-HDSS/app/uwsgi_params; # the uwsgi_params file you installed
    }
}
```

Step 7: FILE > create src_uwsgi.ini

```bash
# src_uwsgi.ini file
[uwsgi]

# Django-related settings
# the base directory (full path)
chdir           = /home/tsongzzz/SIDC-HDSS/app
# Django's wsgi file
module          = src.wsgi
# the virtualenv (full path)
home            = /home/tsongzzz/SIDC-HDSS/venv

# process-related settings
# master
master          = true
# maximum number of worker processes
processes       = 10
# the socket (use the full path to be safe
socket          = /home/tsongzzz/SIDC-HDSS/app/src.sock
# ... with appropriate permissions - may be needed
chmod-socket    = 664
# clear environment on exit
vacuum          = true
```


Step 8.1: BASH > symlink 'src_nginx.conf' to '/etc/nginx/sites-enabled/'

```bash
sudo ln -s /home/tsongzzz/SIDC-HDSS/app/src_nginx.conf /etc/nginx/sites-enabled/
```

> verify symlink

```bash
cat /etc/nginx/sites-enabled/src_nginx.conf
```

[OPTIONAL] Step 8.2: BASH > copy 'src_nginx.conf' to '/etc/nginx/sites-available/'

```bash
sudo cp /home/tsongzzz/SIDC-HDSS/app/src_nginx.conf /etc/nginx/sites-available/
```

> verify copy

```bash
cat /etc/nginx/sites-available/src_nginx.conf
```

Step 9: BASH > restart nginx

```bash
sudo /etc/init.d/nginx restart
```

Step 10: BASH > Verify if Django + uWSGI + nginx is running

```bash
uwsgi --socket src.sock --module src.wsgi --chmod-socket=664
```

Step 11: BASH > run application through src_uwsgi.ini

```bash
uwsgi --ini src_uwsgi.ini
```

Step 12: Go to <http://localhost:8000> to test if working
