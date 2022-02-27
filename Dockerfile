# syntax=docker/dockerfile:1.3
FROM python:3.9-alpine3.15
LABEL maintainer="Cyrille Pontvieux <cyrille@enialis.net>"
RUN apk update && \
    apk upgrade && \
    apk add \
        gcc \
        git \
        libcap \
        linux-headers \
        mariadb-client \
        mariadb-dev \
        musl-dev \
        nginx \
        postgresql-client \
        postgresql-dev \
    && \
    pip3 install pipenv supervisor
# configure uwsgi
RUN mkdir -p /var/run/nginx && \
    chown -R nginx:nginx /var/run /run && \
    chmod -R ug=rwX,o= /var/run /run && \
    printf '\
[uwsgi]\n\
socket = /var/run/uwsgi.sock\n\
chmod-socket = 660\n\
enable-threads = true\n\
master = 1\n\
die-on-term = true\n\
hook-master-start = unix_signal:15 gracefully_kill_them_all\n\
wsgi-disable-file-wrapper = true\n\
if-env = VENV\n\
    virtualenv = %%(_)\n\
endif =\n\
env = LANG=en_US.UTF-8\n\
chdir = %s\n\
wsgi-file = %s\n\
touch-reload = %s\n\
' /var/www/app /var/www/app/mailserveradmin/config/wsgi.py /var/www/app/Pipfile.lock > /etc/uwsgi.ini && \
    mkdir -p /var/www/app && \
    chown nginx: /var/www/app
# configure nginx
RUN setcap 'cap_net_bind_service=+ep' /usr/sbin/nginx && \
    sed -ri 's/^user .*/daemon off;/' /etc/nginx/nginx.conf && \
    sed -ri '/^ *ssl_protocols /s/ TLSv1.1//' /etc/nginx/nginx.conf && \
    printf '\
server {\n\
    listen 80 default_server;\n\
    listen [::]:80 default_server;\n\
    location / {\n\
        include uwsgi_params;\n\
        uwsgi_pass unix:///var/run/uwsgi.sock;\n\
    }\n\
    location /static {\n\
        root %s/;\n\
    }\n\
}\n\
' /var/www/app > /etc/nginx/http.d/default.conf
# configure supervisor
RUN mkdir /var/log/supervisor && \
    chown nginx: /var/log/supervisor && \
    chmod ug=rwX /var/log/supervisor && \
    printf '\
[supervisord]\n\
logfile=/var/log/supervisor/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
childlogdir=/var/log/supervisor\n\
nodaemon=true\n\
\n\
[unix_http_server]\n\
file=/var/run/supervisor.sock\n\
\n\
[rpcinterface:supervisor]\n\
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n\
\n\
[supervisorctl]\n\
serverurl=unix:///var/run/supervisor.sock\n\
\n\
[program:uwsgi]\n\
command=%%(ENV_VENV)s/bin/uwsgi --ini /etc/uwsgi.ini\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
stopsignal=TERM\n\
\n\
[program:nginx]\n\
command=/usr/sbin/nginx\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
stopsignal=QUIT\n\
' > /etc/supervisord.conf && \
    chmod go=r /etc/supervisord.conf
# configure entrypoint
RUN printf '#!/bin/sh\n\
set -e\n\
prestart_files=$(find /etc/entrypoint.d -type f)\n\
[ -n "$prestart_files" ] && for f in $prestart_files; do\n\
  if [ -x "$f" ]; then\n\
    "$f"\n\
  elif [ -f "$f" ]; then\n\
    . "$f"\n\
  fi\n\
done || true\n\
exec "$@"\n\
' > /usr/local/bin/docker-entrypoint && \
    chmod +x /usr/local/bin/docker-entrypoint && \
    mkdir /etc/entrypoint.d
ENTRYPOINT ["/usr/local/bin/docker-entrypoint"]
CMD ["supervisord"]
RUN printf '\
cd /var/www/app\n\
export VENV=$(pipenv --venv) || true\n\
if [ -z "$DJANGO_SECRET_KEY" ] || [ -z "$DJANGO_DB_TYPE" ]; then\n\
  echo "DJANGO_SECRET_KEY and DJANGO_DB_TYPE should be defined" >&2\n\
  exit 1\n\
fi\n\
maxsec=120\n\
if [ "$DJANGO_DB_TYPE" = "postgres" ]; then\n\
  dbnosql="\\q"\n\
elif [ "$DJANGO_DB_TYPE" = "mysql" ]; then\n\
  dbnosql=""\n\
else\n\
  echo "DJANGO_DB_TYPE value not supported" >&2\n\
  exit 1\n\
fi\n\
echo "*** Wait for $DJANGO_DB_TYPE database to be ready (max ${maxsec} seconds)"\n\
for i in $(seq $maxsec); do\n\
  if echo "$dbnosql" | pipenv run ./manage.py dbshell 2>/dev/null; then\n\
    dbok=1\n\
    break\n\
  fi\n\
  sleep 1\n\
done\n\
if [ $dbok -eq 1 ]; then\n\
  pipenv run ./manage.py migrate\n\
else\n\
  echo "$dbnosql" | pipenv run ./manage.py dbshell\n\
fi\n\
' > /etc/entrypoint.d/00_app.env
USER nginx
WORKDIR /var/www/app
ARG GIT_URL=https://github.com/jrd/mailserver-admin.git
ARG GIT_TAG
LABEL version=$GIT_TAG
RUN git clone --branch "$GIT_TAG" --depth 1 "$GIT_URL" .
RUN rm -rf .git* .env
RUN PIPENV_VERBOSITY=-1 pipenv sync && \
    echo "*** Installing extra packages" && \
    grep '^[a-z]' Pipfile.extra | sed -r 's/ = "(.*)"/\1/' > reqs.txt && pipenv run pip install -r reqs.txt && rm reqs.txt && \
    pipenv run pip install uwsgi && \
    echo "*** Django Quick Check" && \
    pipenv run ./manage.py check --deploy && \
    echo "*** Django Collect Static" && \
    pipenv run ./manage.py collectstatic --clear --noinput -v 0
