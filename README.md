mailserver-admin
================

This application manages *domains*, *users* and *aliases* of a mail server.

This has been tested with **dovecot**, using either mysql or postgresql database.

The main goal was to enhance/replace [Jeffrey Boehm’s PHP mailserver-admin application](https://github.com/jeboehm/mailserver-admin) because I didn’t want to have a mail server administration application in PHP and I wanted to have administration account per domain.

Environment variables
---------------------

- `DJANGO_SECRET_KEY`: at least 40 characters. Should be specified for production.
- `DJANGO_DEBUG`: default `False`. Set to `True` to enable debug toolbar, more logs and static files served.
- `DJANGO_LOG_LEVEL`: default to `WARNING` (`INFO` if `DJANGO_DEBUG`).
- `DJANGO_RUNSERVER_LOG_LEVEL`: default to `INFO` (`DEBUG` if `DJANGO_DEBUG`). Used only when run with `runserver` or `runserver_plus`.
- `DJANGO_TZ`: timezone, defaut to `UTC`.
- `DJANGO_DB_TYPE`: `postgres` or `mysql`, default to `mysql`.
- `DJANGO_DB_HOST`: database hostname, default to `db` (for use in docker-compose).
- `DJANGO_DB_PORT`: database port, default to empty (default port).
- `DJANGO_DB_NAME`: database name, default to `mailserver`.
- `DJANGO_DB_USER`: database user, default to `mailserver`.
- `DJANGO_DB_PASSWORD`: database password, default to `changeme`.

VirtualEnv and Dependencies
---------------------------

Use:

```sh
pipenv sync
```

To install dependencies. 

Installation
------------

You should also install a database driver,  either `mysqlclient` or `psycopg2-binary`:

```sh
pipenv run pip install mysqlclient
```

Define the required environment variables then:

```sh
pipenv run ./manage.py migrate
pipenv run ./manage.py createsuperuser
pipenv run ./manage.py collectstatic
```

You can now server the application using any **WSGI** server pointing to the `config/wsgi.py` or `config/asgi.py` file. Don’t forget to also serve `favicon.ico` file and `static/` folder.

Alternatively, you can test the application with `pipenv run ./manage.py runserver_plus` but this should only be used for testing/development.
