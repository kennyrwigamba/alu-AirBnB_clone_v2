#!/usr/bin/env bash
# Set up the directory tree and Nginx configuration for web_static.

if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

$SUDO apt-get update -y >/dev/null 2>&1
$SUDO apt-get install -y nginx >/dev/null 2>&1

$SUDO mkdir -p \
    /data/web_static/releases/test \
    /data/web_static/shared

printf '%s\n' '<html><body>Web static is working!</body></html>' |
    $SUDO tee /data/web_static/releases/test/index.html >/dev/null

$SUDO rm -f /data/web_static/current
$SUDO ln -s /data/web_static/releases/test /data/web_static/current

$SUDO chown -R ubuntu:ubuntu /data

NGINX_SITE="/etc/nginx/sites-available/default"
LOCATION_START="        # BEGIN hbnb_static"
LOCATION_END="        # END hbnb_static"

if $SUDO test -f "$NGINX_SITE"; then
    $SUDO sed -i "/$LOCATION_START/,/$LOCATION_END/d" "$NGINX_SITE"
    $SUDO sed -i "/^[[:space:]]*location \\/[[:space:]]*{/i\\
$LOCATION_START\\
        location /hbnb_static/ {\\
            alias /data/web_static/current/;\\
        }\\
$LOCATION_END\\
" "$NGINX_SITE"
fi

$SUDO nginx -t >/dev/null 2>&1
$SUDO service nginx restart >/dev/null 2>&1

exit 0
