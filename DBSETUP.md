# Database Setup

## Installing PostgreSQL 14 and pgAdmin4

Step 1: BASH > Create repository configuration files

- PostgreSQL

 ```bash
 sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
 wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
 ```

- pgAdmin4

 ```bash
 sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'
 sudo curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
 ```

Step 2: BASH > Update package list

```bash
sudo apt update
sudo apt upgrade
```

Step 3: BASH > Install PostgreSQL and pgAdmin4

```bash
sudo apt install postgresql-14
sudo apt install pgadmin4-web
```

## Setup for PostgreSQL

Step 1: BASH > Install PostGIS

```bash
sudo apt install postgis postgresql-14-postgis-3
```

Step 2: BASH > Start `postgresql` service

```bash
sudo service postgresql start
```

Step 3: BASH > Login to user `postgres`

```bash
sudo -i -u postgres
```

Step 4: BASH > Run `psql` (PostgreSQL CLI)

```bash
psql
```

Step 5: BASH > Change password of user `postgres`

```bash
#while in psql
\password postgres
```

Step 6: BASH > Exit

```bash
\q
exit #logout from postgres user
```

## Setup for pgAdmin4

Step 1: BASH > Backup pgAdmin setup script

```bash
sudo cp /usr/pgadmin4/bin/setup-web.sh ~/setup-web.sh.bak #create a copy of the script in home dir
cp ~/setup-web.sh.bak ~/setup-web.sh #create another copy that will be used to overwrite original
```

Step 2: BASH > Modify setup script copy

```bash
code setup-web.sh #modify lines: 121, 139, and 146 in the copy that was created
```

> WSL uses `Sysvinit` instead of `Systemd` which means `Systemd` commands must be replaced with its corresponding [`Sysvinit` alternatives](https://fedoraproject.org/wiki/SysVinit_to_Systemd_Cheatsheet)
>
>```bash
>#setup-web.sh
>service ${APACHE} restart #@line 121
>chkconfig ${APACHE} on #@line 139
>service ${APACHE} start #@line 146
>```

Step 3: BASH > Overwrite the original setup script

```bash
sudo cp ~/setup-web.sh /usr/pgadmin4/bin/setup-web.sh #overwrite with the modified script
```

Step 4: BASH > Run the setup script

```bash
sudo /usr/pgadmin4/bin/setup-web.sh
```

- Email and password is only used for pgAdmin
- pgAdmin initializes after confirming password do not press `ENTER` or the web server will not be configured
  - can run the script again if this happens

Step 5 BASH > Access pgAdmin4 through browser

```bash
wslview http://$(hostname -I)/pgadmin4 #loading will take some time on initial access
```

- `hostname -I`: IP address of the Linux environment
- `wslview`: Opens default browser in Windows

## Nginx config

- pgAdmin4 setup script is set up with Apache and listens to port 80.
- Default config in `/etc/nginx/sites-enabled/default` listens to port 80 which will conflict with pgAdmin4, the simplest fix it to remove it with `sudo rm /etc/nginx/sites-enabled/default`.

```bash
sudo rm /etc/nginx/sites-enabled/default
```

- Other possible workarounds are to setup pgAdmin4 with Nginx or to change the ports either Nginx or Apache is listening to.

## Django settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': '<name>',
        'USER': '<user>',
        'PASSWORD': '<password>',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```
