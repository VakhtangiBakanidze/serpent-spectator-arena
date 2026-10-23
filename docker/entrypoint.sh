#!/bin/sh
set -eu

: "${PORT:=80}"
export PORT

envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
