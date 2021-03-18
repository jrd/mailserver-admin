mailserver-admin
================

To be used with [Jeffrey Boehm’s mail server](https://github.com/jeboehm/docker-mailserver).

It’s a complete rewrite of [PHP mailserver-admin application](https://github.com/jeboehm/mailserver-admin) but in Django and with some additional features.

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
