#!/usr/bin/env bash
#
# deploy.sh — one-shot deployment for the School-app Django project.
#
# Serves the app via Gunicorn (managed by systemd) behind Nginx on
#   http://34.229.200.54/
#
# Usage (on the Ubuntu server, from inside the repo):
#   sudo ./deploy.sh
#
# Re-runnable: updates dependencies, migrations, static files and configs.
#
# Optional overrides (environment variables):
#   APP_USER=ubuntu        # OS user that runs Gunicorn
#   SERVER_NAME=34.229.200.54
#   PYTHON_BIN=python3
#
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_USER="${APP_USER:-${SUDO_USER:-$(whoami)}}"
SERVER_NAME="${SERVER_NAME:-34.229.200.54}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SERVICE_NAME="gunicorn"
NGINX_SITE="school-app"

echo "============================================================"
echo " Deploying School-app"
echo "   App directory : $APP_DIR"
echo "   Run as user   : $APP_USER"
echo "   Server name   : $SERVER_NAME"
echo "============================================================"

if [[ "$EUID" -ne 0 ]]; then
    echo "ERROR: this script must run as root. Re-run with: sudo ./deploy.sh" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------
echo "==> [1/6] Installing system packages (python3-venv, nginx)..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx

# ---------------------------------------------------------------------------
# 2. Virtualenv + Python dependencies
# ---------------------------------------------------------------------------
echo "==> [2/6] Creating virtualenv and installing requirements..."
if [[ ! -d "$APP_DIR/venv" ]]; then
    sudo -u "$APP_USER" "$PYTHON_BIN" -m venv "$APP_DIR/venv"
fi
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# ---------------------------------------------------------------------------
# 3. Migrations + static files
# ---------------------------------------------------------------------------
echo "==> [3/6] Applying migrations and collecting static files..."
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" migrate --noinput
sudo -u "$APP_USER" "$APP_DIR/venv/bin/python" "$APP_DIR/manage.py" collectstatic --noinput

# ---------------------------------------------------------------------------
# 4. Permissions
#    Gunicorn runs as $APP_USER (owns the DB and files). Nginx (www-data) only
#    needs to read the collected static + media, and traverse into $APP_DIR.
# ---------------------------------------------------------------------------
echo "==> [4/6] Setting ownership and permissions..."
mkdir -p "$APP_DIR/media" "$APP_DIR/staticfiles"
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
chmod o+x "$APP_DIR"                                   # allow Nginx to traverse in
chmod -R a+rX "$APP_DIR/staticfiles" "$APP_DIR/media"  # public read for Nginx

# ---------------------------------------------------------------------------
# 5. systemd service for Gunicorn
# ---------------------------------------------------------------------------
echo "==> [5/6] Installing + starting Gunicorn systemd service..."
sed -e "s|__APP_DIR__|$APP_DIR|g" \
    -e "s|__APP_USER__|$APP_USER|g" \
    "$APP_DIR/deploy/gunicorn.service" > "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME" >/dev/null 2>&1 || true
systemctl restart "$SERVICE_NAME"

# ---------------------------------------------------------------------------
# 6. Nginx site
# ---------------------------------------------------------------------------
echo "==> [6/6] Installing + enabling Nginx site..."
sed -e "s|__APP_DIR__|$APP_DIR|g" \
    -e "s|__SERVER_NAME__|$SERVER_NAME|g" \
    "$APP_DIR/deploy/nginx.conf" > "/etc/nginx/sites-available/${NGINX_SITE}"
ln -sf "/etc/nginx/sites-available/${NGINX_SITE}" "/etc/nginx/sites-enabled/${NGINX_SITE}"
rm -f /etc/nginx/sites-enabled/default   # stop the default page shadowing our site
nginx -t
systemctl restart nginx
systemctl enable nginx >/dev/null 2>&1 || true

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
cat <<EOF

============================================================
 ✅ Deployment complete
    Visit:  http://$SERVER_NAME/
            http://$SERVER_NAME/admin/   (create a superuser first)
============================================================
 Create an admin user:
   sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/manage.py createsuperuser

 Handy commands:
   sudo systemctl status $SERVICE_NAME
   sudo journalctl -u $SERVICE_NAME -f
   sudo systemctl restart $SERVICE_NAME

 IMPORTANT: open TCP port 80 in your cloud firewall / EC2 security group.
============================================================
EOF
