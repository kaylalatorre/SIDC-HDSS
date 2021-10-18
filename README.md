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
