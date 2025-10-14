# 🚀 Django Project Deployment Guide

This canvas version is a visual checklist-style guide for deploying a Django project on Ubuntu VPS with Gunicorn & Nginx.

---

## 1️⃣ Prerequisites

* 🖥️ Ubuntu VPS with SSH access
* 🐍 Python 3.12
* 🛢️ MySQL Database
* 📂 Project structure
* 📦 Required packages:

  ```bash
  sudo apt update && sudo apt install python3 python3-venv python3-pip nginx git build-essential pkg-config python3-dev default-libmysqlclient-dev -y
  ```

---

## 2️⃣ Folder Permissions

```bash
sudo chown -R ubuntu:www-data /var/www/interview-repo
sudo chmod -R 755 /var/www/interview-repo
cd /var/www/interview-repo
```

---

## 3️⃣ Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn mysqlclient
```

---

## 5️⃣ Environment Variables

`.env` file:

```env
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=16.171.165.101
MYSQL_DATABASE=your_db_name
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

---

## 6️⃣ Migrations & Static Files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## 7️⃣ Test Gunicorn

```bash
gunicorn project.wsgi:application --bind 0.0.0.0:8000
```

* 🌐 Check: `http://16.171.165.101:8000`
* ❌ Stop: `Ctrl + C`

---

## 8️⃣ Gunicorn Systemd Service

`/etc/systemd/system/project.service`

```ini
[Unit]
Description=Gunicorn daemon for Django project
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/interview-repo
ExecStart=/var/www/interview-repo/venv/bin/gunicorn --workers 3 --bind unix:/var/www/interview-repo/project.sock project.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start project
sudo systemctl enable project
sudo systemctl status project
```

---

## 9️⃣ Configure Nginx

`/etc/nginx/sites-available/project`

```nginx
server {
    listen 80;
    server_name 16.171.165.101;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/interview-repo;
    }

    location /media/ {
        root /var/www/interview-repo;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/interview-repo/project.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/project /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔓 Open HTTP Port

* EC2 Security Group / Firewall: `TCP 80` → Source `0.0.0.0/0`

---

## 🌐 Test Deployment

Open: `http://16.171.165.101/`

✅ Django site should be live (Nginx → Gunicorn → Django)

---

## 🔒 Optional HTTPS

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d 16.171.165.101
```

---

## 📝 Deployment Flow

```
Browser → Nginx → Gunicorn → project/wsgi.py → Django → MySQL → Response
```

* Nginx: serves static/media files
* Gunicorn: communicates with Django
* MySQL: database operations
* Response: Gunicorn → Nginx → Browser
