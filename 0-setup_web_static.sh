#!/usr/bin/env bash
# Prepare the web_static directories, ownership, and Nginx alias on Ubuntu.

sudo_cmd=()
if [ "$(id -u)" -ne 0 ]; then
    sudo_cmd=(sudo)
fi

umask 022

if ! command -v nginx >/dev/null 2>&1; then
    "${sudo_cmd[@]}" apt-get update
    "${sudo_cmd[@]}" apt-get install -y nginx
fi

"${sudo_cmd[@]}" mkdir -p /data/web_static/releases/test /data/web_static/shared
"${sudo_cmd[@]}" tee /data/web_static/releases/test/index.html >/dev/null <<'HTML'
<html>
  <head>
  </head>
  <body>
    Holberton School
  </body>
</html>
HTML

"${sudo_cmd[@]}" rm -f /data/web_static/current
"${sudo_cmd[@]}" ln -s /data/web_static/releases/test /data/web_static/current
"${sudo_cmd[@]}" chmod 755 /data /data/web_static /data/web_static/releases \
    /data/web_static/releases/test /data/web_static/shared
"${sudo_cmd[@]}" chmod 644 /data/web_static/releases/test/index.html
"${sudo_cmd[@]}" chown -hR ubuntu:ubuntu /data

"${sudo_cmd[@]}" mkdir -p /etc/nginx/snippets /etc/nginx/sites-available \
    /etc/nginx/sites-enabled
"${sudo_cmd[@]}" tee /etc/nginx/snippets/hbnb_static.conf >/dev/null <<'NGINX'
location = /hbnb_static {
    return 301 /hbnb_static/;
}

location /hbnb_static/ {
    alias /data/web_static/current/;
    index index.html;
}
NGINX

nginx_site=/etc/nginx/sites-available/default
if ! "${sudo_cmd[@]}" test -f "$nginx_site"; then
    "${sudo_cmd[@]}" tee "$nginx_site" >/dev/null <<'NGINX'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /var/www/html;
    index index.html index.htm;
    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}
NGINX
fi

# Remove our previous configuration before inserting one include per server.
"${sudo_cmd[@]}" sed -i \
    '/# BEGIN hbnb_static/,/# END hbnb_static/d;\|^[[:space:]]*include /etc/nginx/snippets/hbnb_static\.conf;[[:space:]]*$|d' \
    "$nginx_site"
"${sudo_cmd[@]}" sed -i \
    '/^[[:space:]]*server[[:space:]]*{/a\    include /etc/nginx/snippets/hbnb_static.conf;' \
    "$nginx_site"
"${sudo_cmd[@]}" ln -sfn "$nginx_site" /etc/nginx/sites-enabled/default

if "${sudo_cmd[@]}" nginx -t; then
    "${sudo_cmd[@]}" service nginx restart
fi

exit 0
