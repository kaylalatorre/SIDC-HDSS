# SIDC-HDSS

SIDC-HDSS is a web application with features to help the cooperative with farm biosecurity management, hogs health tracking, disease tracking, and decision support.

## Setting Up the Project Locally

### Setup Linux Environment

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

### Setup Github on VS Code

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

> GitHub Pull Requests and Issues <https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github>
>
> Remote - WSL <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl>

Step 4: CODE > Clone Repository: <https://github.com/kaylalatorre/SIDC-HDSS.git>
> Ctrl + Shift + P > Search Git: Clone > Clone from Github > Enter Repository URL

### Setup Conda Virtual Environment

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
conda create -p ~/SIDC-HDSS/venv uWSGI Python Django djangorestframework GeoPandas geopy PostGis psycopg2 twilio python-dotenv
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

### Setup Nginx

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

### Setup Django

Step 1: BASH > symlink 'src_nginx.conf' to '/etc/nginx/sites-enabled/'

```bash
sudo ln -s /home/tsongzzz/SIDC-HDSS/app/src_nginx.conf /etc/nginx/sites-enabled/
```

> verify symlink

```bash
cat /etc/nginx/sites-enabled/src_nginx.conf
```

_OPTIONAL_ Step 1.1: BASH > copy 'src_nginx.conf' to '/etc/nginx/sites-available/'

```bash
sudo cp /home/tsongzzz/SIDC-HDSS/app/src_nginx.conf /etc/nginx/sites-available/
```

> verify copy

```bash
cat /etc/nginx/sites-available/src_nginx.conf
```

Step 2: BASH > restart nginx

```bash
sudo /etc/init.d/nginx restart
```

Step 3: BASH > Verify if Django + uWSGI + nginx is running

```bash
uwsgi --socket src.sock --module src.wsgi --chmod-socket=664
```

Step 4: BASH > run application through src_uwsgi.ini

```bash
uwsgi --ini src_uwsgi.ini
```

Step 12: Go to <http://localhost:8000> to test if working

## Setup Database

See DB setup documentation [DBSETUP](/DBSETUP.md)

## Running the Project Locally

_If conda is not activated:_ ```eval "$(/home/tsongzzz/miniconda3/bin/conda shell.bash hook)"```

1. Go to the project directory `cd ~/SIDC-HDSS/`
2. Activate the conda environment `conda activate ./venv`
3. Go to the app directory `cd app`
4. **In a separate terminal:** Start the PosgreSQL service and Apache2 server (for pgAdmin)

    ```bash
    sudo service postgresql start
    sudo service apache2 start
    ```

5. Start nginx `sudo /etc/init.d/nginx start`
6. `uwsgi --ini src_uwsgi.ini`
7. Go to <http://localhost:8000>

## Authors

Catahan, Anna Kumiko  
Go, Kurt Patrick  
Latorre, Kayla Dwynett  
Manzano, Ninna Robyn
