# Django Project Deployment on Ubuntu VPS with Gunicorn and Nginx

This document provides a complete step-by-step guide for deploying a Django project (`project` with app `app`) using **Gunicorn** and **Nginx** on an Ubuntu VPS, such as HostingRaja or AWS EC2.

---

## 1. Prerequisites

* Ubuntu VPS with SSH access
* Python 3.12 installed
* MySQL database configured
* Project structure:

```
/var/www/interview-repo/
├── project/      # Django project
├── app/          # Django app
├── manage.py
├── requirements.txt
├── media/
├── static/
```

* Installed packages:

```bash
sudo apt update && sudo apt install python3 python3-venv python3-pip nginx git build-essential pkg-config python3-dev default-libmysqlclient-dev -y
```

---

## 2. Set Folder Ownership

```bash
sudo chown -R ubuntu:www-data /var/www/interview-repo
sudo chmod -R 755 /var/www/interview-repo
cd /var/www/interview-repo
```

---

## 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn mysqlclient
```

---

## 5. Configure Environment Variables

Create `.env` file:

```bash
nano .env
```

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

## 6. Apply Migrations and Collect Static Files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

---

## 7. Test Gunicorn

```bash
gunicorn project.wsgi:application --bind 0.0.0.0:8000
```

* Check: `http://16.171.165.101:8000`
* Stop server with `Ctrl + C`

---

## 8. Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/project.service
```

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

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start project
sudo systemctl enable project
sudo systemctl status project
```

---

## 9. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/project
```

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

Enable site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/project /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 10. Open HTTP Port on VPS

* EC2 Security Group / HostingRaja Firewall:

  * Inbound rule: TCP 80 → Source 0.0.0.0/0

---

## 11. Test Deployment

Open browser:

```
http://16.171.165.101/
```

✅ Your Django site should be live via **Nginx → Gunicorn → Django**

---

## 12. Optional: Enable HTTPS

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d 16.171.165.101
```

---

### ✅ Deployment Flow Summary

```
Browser → Nginx → Gunicorn → project/wsgi.py (application) → Django → MySQL → Response
```

* Nginx serves static/media files directly
* Gunicorn communicates with Django via `wsgi.py`
* MySQL handles database operations
* Response goes back to user via Gunicorn → Nginx

```
```
