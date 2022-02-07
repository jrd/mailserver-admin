mailserver-admin
================

This application manages *domains*, *users* and *aliases* of a mail server.

This has been tested with **dovecot**, using either mysql or postgresql database.

The main goal was to enhance/replace [Jeffrey Boehm’s PHP mailserver-admin application](https://github.com/jeboehm/mailserver-admin) because I didn’t want to have a mail server administration application in PHP and I wanted to have administration account per domain.

Environment variables
---------------------

Required:

- `DJANGO_SECRET_KEY`: at least 40 characters. Should be specified for production.
- `DJANGO_DB_TYPE`: `postgres` or `mysql`, default to `mysql`.
- `DJANGO_DB_HOST`: database hostname, default to `db` (for use in docker-compose).
- `DJANGO_DB_PORT`: database port, default to empty (default port).
- `DJANGO_DB_NAME`: database name, default to `mailserver`.
- `DJANGO_DB_USER`: database user, default to `mailserver`.
- `DJANGO_DB_PASSWORD`: database password, default to `changeme`.

Optional:
- `DJANGO_DEBUG`: default `False`. Set to `True` to enable debug toolbar, more logs and static files served.
- `DJANGO_LOG_LEVEL`: default to `WARNING` (`INFO` if `DJANGO_DEBUG`).
- `DJANGO_RUNSERVER_LOG_LEVEL`: default to `INFO` (`DEBUG` if `DJANGO_DEBUG`). Used only when run with `runserver` or `runserver_plus`.
- `DJANGO_TZ`: timezone, defaut to `UTC`.
- `DJANGO_WEBMAIL_URL`: webmail url to show in the footer, default to no link.
- `DJANGO_VENDOR_NAME`: any vendor name you want to appear on the footer, default to *Sources*.
- `DJANGO_VENDOR_URL`: any url you want to be linked to your vendor name, default to this repository url. Set to empty to disable the link.
- `DJANGO_HIDE_VERSION`: default `False` if `DJANGO_DEBUG` else `True`. Set to `True` to hide the `mailserver-admin` version.

Install from Docker Hub
-----------------------

Using `docker` directly:
```sh
docker run --name msa \
    -p 80:80 \
    -e DJANGO_SECRET_KEY=12345678901234567890abcdefghijklmnopqrstuvwxyz \
    -e DJANGO_DB_TYPE=mysql \
    -e DJANGO_DB_PASSWORD=pwd \
    --link yourmariadb:db \
    jrdasm/mailserver-admin:<version>
docker exec -ti msa pipenv run ./manage.py createsuperuser
```

Of course this is simple using `docker-compose`:
```yaml
...
services:
    db:
        image: mariadb
        environment:
            - "MYSQL_RANDOM_ROOT_PASSWORD=yes"
            - "MYSQL_DATABASE=mailserver"
            - "MYSQL_USER=mailserver"
            - "MYSQL_PASSWORD=pwd"
    ...
    msa:
        image: jrdasm/mailserver-admin:<version>
        environment:
            - "DJANGO_SECRET_KEY=12345678901234567890abcdefghijklmnopqrstuvwxyz"
            - "DJANGO_DB_TYPE=mysql"
            - "DJANGO_DB_NAME=mailserver"
            - "DJANGO_DB_USER=mailserver"
            - "DJANGO_DB_PASSWORD=pwd"
        ports:
            - "80:80"
...
```

```sh
docker-compose exec msa pipenv run ./manage.py createsuperuser
```

Install from PyPi
-----------------

### VirtualEnv and Dependencies

Minium python version is **3.9**.

Use:

```sh
pipenv install mailserver-admin
```

to install it without any database backend.

If you want to install the `mysql` or `postgresql` database backend alongside, use for instance:

```sh
pipenv install mailserver-admin[mysql]
```

### Configuration

Define the required environment variables then:

```sh
export DJANGO_SETTINGS_MODULE=mailserveradmin.config.settings
pipenv run django migrate
pipenv run django createsuperuser
```

You can use `pipenv run django migrate --fake-initial` if you already have a mysql or postgresql database with existing schema/data.

You can now server the application using any **WSGI** server pointing to `$(VISUAL='readlink -f' pipenv open mailserveradmin|tail -n1)/config/wsgi.py`.

Don’t forget to also serve static ressources located at `$(VISUAL='readlink -f' pipenv open mailserveradmin|tail -n1)/to_serve` folder.

You can of course make symlinks to those locations to simplify configuration.

Install from sources
--------------------

### VirtualEnv and Dependencies

Use:

```sh
pipenv sync -d
```

to install dependencies. Default python version is **3.9**.

### Installation

You should also install a database driver, either `mysqlclient` or `psycopg2-binary`:

```sh
pipenv run pip install mysqlclient
```

### Configuration

Define the required environment variables then:

```sh
pipenv run ./manage.py migrate
pipenv run ./manage.py createsuperuser
pipenv run ./manage.py collectstatic
```

You can now server the application using any **WSGI** server pointing to the `config/wsgi.py` file.

Don’t forget to also serve the `static/` folder.

Alternatively, you can test the application with `pipenv run ./manage.py runserver_plus` but this should only be used for testing/development.
