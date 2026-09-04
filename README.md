# School Management System — Django

A Django app (project `project`, app `app`) for managing students, teachers,
classes and attendance. It runs on **SQLite** and is served in production by
**Gunicorn** behind **Nginx** on `http://34.229.200.54/`.

```
Browser → Nginx (:80) → Gunicorn (127.0.0.1:8000) → project/wsgi.py → Django → SQLite
```

Nginx serves `/static/` and `/media/` directly from disk; everything else is
proxied to Gunicorn.

---

## Project structure

```
School-app/
├── app/                 # Django app (models, views, templates, migrations)
├── project/             # Django project (settings, urls, wsgi, asgi)
├── deploy/
│   ├── gunicorn.conf.py # Gunicorn settings (workers, bind, logging)
│   ├── gunicorn.service # systemd unit template
│   └── nginx.conf       # Nginx site template
├── deploy.sh            # one-shot server setup script
├── manage.py
├── requirements.txt
├── db.sqlite3           # SQLite database
├── media/               # uploaded files (student photos)
└── .env                 # environment configuration
```

---

## 1. Quick deploy (recommended)

On the Ubuntu server (e.g. the EC2 instance at `34.229.200.54`):

```bash
# Recommended location — its parent (/var/www) is readable by Nginx.
sudo mkdir -p /var/www
sudo chown "$USER":"$USER" /var/www
git clone <your-repo-url> /var/www/school-app
cd /var/www/school-app

# Review .env, then run the installer.
sudo ./deploy.sh
```

`deploy.sh` is idempotent and does everything:

1. Installs `python3-venv`, `pip` and `nginx`.
2. Creates `venv/` and installs `requirements.txt`.
3. Runs `migrate` and `collectstatic`.
4. Sets ownership/permissions for Nginx.
5. Installs and starts the `gunicorn` systemd service.
6. Installs and enables the Nginx site, then reloads Nginx.

Then create an admin user and open the site:

```bash
sudo -u "$USER" /var/www/school-app/venv/bin/python manage.py createsuperuser
```

* App:   `http://34.229.200.54/`
* Admin: `http://34.229.200.54/admin/`

> **Open port 80** in your cloud firewall / EC2 security group
> (Inbound: TCP 80, Source `0.0.0.0/0`).

Override defaults if needed:

```bash
sudo APP_USER=ubuntu SERVER_NAME=34.229.200.54 ./deploy.sh
```

---

## 2. Configuration (`.env`)

```env
SECRET_KEY="change-me-to-a-long-random-string"
DEBUG=False
ALLOWED_HOSTS=34.229.200.54,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://34.229.200.54

# SQLite needs no server or credentials. Optional custom path:
# SQLITE_PATH=/var/www/school-app/db.sqlite3
```

Generate a fresh secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Settings load `.env` automatically via `python-dotenv`, so the same values are
used by Gunicorn, `manage.py`, and the dev server.

---

## 3. Manual deployment (without deploy.sh)

<details>
<summary>Step-by-step equivalent</summary>

```bash
# System packages
sudo apt update && sudo apt install -y python3 python3-venv python3-pip nginx

# App
cd /var/www/school-app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Database + static
python manage.py migrate
python manage.py collectstatic --noinput

# Gunicorn systemd service (fill in the placeholders)
sudo sed -e "s|__APP_DIR__|/var/www/school-app|g" \
         -e "s|__APP_USER__|ubuntu|g" \
         deploy/gunicorn.service | sudo tee /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn

# Nginx site
sudo sed -e "s|__APP_DIR__|/var/www/school-app|g" \
         -e "s|__SERVER_NAME__|34.229.200.54|g" \
         deploy/nginx.conf | sudo tee /etc/nginx/sites-available/school-app
sudo ln -sf /etc/nginx/sites-available/school-app /etc/nginx/sites-enabled/school-app
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
```

</details>

---

## 4. Local development

```bash
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. To see full error pages and admin styling
locally, set `DEBUG=True` in `.env` (dev only — keep it `False` on the server).

---

## 5. Operations

```bash
sudo systemctl status gunicorn        # service state
sudo journalctl -u gunicorn -f        # live application logs
sudo systemctl restart gunicorn       # after code changes
sudo nginx -t && sudo systemctl reload nginx
```

After pulling new code:

```bash
cd /var/www/school-app
sudo ./deploy.sh                      # re-installs deps, migrates, collects static, restarts
```

---

## Notes

* **Database:** SQLite (`db.sqlite3`). It lives on the server and is not
  overwritten by `deploy.sh`. Back it up by copying the file.
* **Static/CSS:** the UI uses Tailwind via CDN, so no build step is required.
  `collectstatic` gathers Django admin assets into `staticfiles/`.
* **HTTPS:** the site is served over plain HTTP. A bare IP cannot get a
  Let's Encrypt certificate; add a domain name first if you need TLS.
