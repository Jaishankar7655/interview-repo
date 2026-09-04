# 🚀 School App — AWS Ubuntu Deployment Guide (Gunicorn + Nginx)

Yeh guide aapko step-by-step batayegi ki kaise School App ko AWS EC2 Ubuntu instance pe **Gunicorn + Nginx** ke through deploy karna hai.

---

## 📋 Prerequisites

- AWS EC2 instance (Ubuntu 22.04 / 24.04 LTS)
- Public IP: `34.229.200.54`
- SSH access: `ssh -i your-key.pem ubuntu@34.229.200.54`
- Security Group mein Port **80** (HTTP) aur **22** (SSH) open hona chahiye

---

## Step 1: SSH into Server

```bash
ssh -i your-key.pem ubuntu@34.229.200.54
```

---

## Step 2: System Update & Dependencies Install

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y python3 python3-pip python3-venv nginx git
```

---

## Step 3: Project Clone Karo

```bash
# Project directory create karo
sudo mkdir -p /var/www/school-app
sudo chown ubuntu:ubuntu /var/www/school-app

# Git clone (ya SCP se copy karo)
cd /var/www/school-app
git clone https://github.com/Jaishankar7655/School-app.git .
```

> **Agar git clone nahi karna** toh local machine se SCP use karo:
> ```bash
> # Apni LOCAL machine se chalao (NOT server pe):
> scp -i your-key.pem -r ./* ubuntu@34.229.200.54:/var/www/school-app/
> ```

---

## Step 4: Virtual Environment Setup

```bash
cd /var/www/school-app

# Virtual environment create karo
python3 -m venv venv

# Activate karo
source venv/bin/activate

# Dependencies install karo
pip install -r requirements.txt
```

---

## Step 5: Environment File (.env) Configure Karo

`.env` file already project mein hai. Verify karo ki yeh values sahi hain:

```bash
nano /var/www/school-app/.env
```

```env
SECRET_KEY="4hzbwokBnDunxrWz4IPF-iX-6vDoqgIFl_mkU1KonBA"
DEBUG=False
ALLOWED_HOSTS=34.229.200.54,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://34.229.200.54
```

> ⚠️ **Production ke liye** naya random `SECRET_KEY` generate karo:
> ```bash
> python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

## Step 6: Django Setup (Migrate + Collectstatic)

```bash
cd /var/www/school-app
source venv/bin/activate

# Database tables create karo
python manage.py migrate

# Static files collect karo (Nginx serve karega)
python manage.py collectstatic --noinput

# Superuser banao (Admin panel ke liye)
python manage.py createsuperuser
```

---

## Step 7: Media Folder Permissions

```bash
# Media folder create karo (agar nahi hai)
mkdir -p /var/www/school-app/media/students
mkdir -p /var/www/school-app/media/teachers

# Permissions set karo taaki Gunicorn write kar sake
sudo chown -R ubuntu:www-data /var/www/school-app/media
sudo chmod -R 775 /var/www/school-app/media
```

---

## Step 8: Gunicorn Test Karo

Pehle manually test karo ki Gunicorn chal raha hai:

```bash
cd /var/www/school-app
source venv/bin/activate

gunicorn --bind 127.0.0.1:8000 project.wsgi:application
```

Agar koi error nahi aaye toh `Ctrl+C` se band karo aur aage badho.

---

## Step 9: Gunicorn Systemd Service Setup

Ab Gunicorn ko service ke taur pe chalayenge taaki server restart hone pe bhi automatically start ho:

```bash
# Log directory banao
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:www-data /var/log/gunicorn

# Service file copy karo
sudo cp /var/www/school-app/gunicorn.service /etc/systemd/system/gunicorn.service

# Service enable aur start karo
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn

# Status check karo
sudo systemctl status gunicorn
```

**Expected output:**
```
● gunicorn.service - Gunicorn daemon for School App
     Active: active (running)
```

> ⚠️ Agar error aaye toh logs check karo:
> ```bash
> sudo journalctl -u gunicorn -n 50
> cat /var/log/gunicorn/error.log
> ```

---

## Step 10: Nginx Configure Karo

```bash
# Default Nginx config hatao
sudo rm /etc/nginx/sites-enabled/default

# Apni config copy karo
sudo cp /var/www/school-app/nginx.conf /etc/nginx/sites-available/school-app

# Enable karo (symlink)
sudo ln -s /etc/nginx/sites-available/school-app /etc/nginx/sites-enabled/school-app

# Config test karo
sudo nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

```bash
# Nginx restart karo
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Step 11: Verify Deployment ✅

Browser mein open karo:

| URL | Expected |
|-----|----------|
| `http://34.229.200.54` | Home page dikhna chahiye |
| `http://34.229.200.54/admin/` | Django Admin login page |
| `http://34.229.200.54/students/` | Student list page |
| `http://34.229.200.54/media/students/test.jpg` | Direct image access (agar uploaded hai) |

---

## Step 12: SSL Setup (Optional — Let's Encrypt Free SSL)

```bash
# Certbot install karo
sudo apt install -y certbot python3-certbot-nginx

# SSL certificate generate karo
# NOTE: Yeh sirf domain name ke saath kaam karta hai, direct IP ke saath nahi.
# Agar aapke paas domain hai (e.g., school.example.com) toh:
sudo certbot --nginx -d school.example.com

# Auto-renewal test
sudo certbot renew --dry-run
```

> **IP pe SSL lagana hai?** Self-signed certificate use karo:
> ```bash
> sudo mkdir -p /etc/nginx/ssl
> sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
>     -keyout /etc/nginx/ssl/selfsigned.key \
>     -out /etc/nginx/ssl/selfsigned.crt \
>     -subj "/CN=34.229.200.54"
> ```
>
> Phir nginx config mein change karo:
> ```nginx
> server {
>     listen 443 ssl;
>     server_name 34.229.200.54;
>
>     ssl_certificate /etc/nginx/ssl/selfsigned.crt;
>     ssl_certificate_key /etc/nginx/ssl/selfsigned.key;
>
>     # ... baaki config same rahega ...
> }
>
> server {
>     listen 80;
>     server_name 34.229.200.54;
>     return 301 https://$host$request_uri;
> }
> ```

---

## 🔧 Common Commands (Quick Reference)

| Kaam | Command |
|------|---------|
| Gunicorn restart | `sudo systemctl restart gunicorn` |
| Gunicorn status | `sudo systemctl status gunicorn` |
| Gunicorn logs | `sudo journalctl -u gunicorn -f` |
| Nginx restart | `sudo systemctl restart nginx` |
| Nginx config test | `sudo nginx -t` |
| Code update ke baad | `cd /var/www/school-app && source venv/bin/activate && git pull && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart gunicorn` |
| Django shell | `cd /var/www/school-app && source venv/bin/activate && python manage.py shell` |

---

## 🐛 Troubleshooting

### Problem: 502 Bad Gateway
```bash
# Gunicorn chal raha hai ya nahi?
sudo systemctl status gunicorn

# Agar nahi chal raha toh restart karo:
sudo systemctl restart gunicorn

# Logs check karo:
sudo journalctl -u gunicorn -n 30
```

### Problem: Images/Media show nahi ho rahi
```bash
# Media folder permissions check karo
ls -la /var/www/school-app/media/

# Permissions fix karo
sudo chown -R ubuntu:www-data /var/www/school-app/media
sudo chmod -R 775 /var/www/school-app/media

# Nginx restart karo
sudo systemctl restart nginx
```

### Problem: Static files (CSS/JS) load nahi ho rahi
```bash
# Collectstatic run karo
cd /var/www/school-app
source venv/bin/activate
python manage.py collectstatic --noinput

# Check karo ki folder exist karta hai
ls -la /var/www/school-app/staticfiles/

# Nginx restart karo
sudo systemctl restart nginx
```

### Problem: 403 Forbidden
```bash
# Project folder permissions
sudo chown -R ubuntu:www-data /var/www/school-app
sudo chmod -R 755 /var/www/school-app
```

### Problem: CSRF verification failed
`.env` mein `CSRF_TRUSTED_ORIGINS` check karo:
```env
CSRF_TRUSTED_ORIGINS=http://34.229.200.54
```
Gunicorn restart karo after change.

---

## 📁 Server Directory Structure

Deployment ke baad server pe yeh structure hona chahiye:

```
/var/www/school-app/
├── .env                    # Environment variables
├── manage.py
├── requirements.txt
├── db.sqlite3              # SQLite database
├── project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── app/
│   ├── models.py
│   ├── views.py
│   └── templates/
├── media/                  # User-uploaded files (Nginx serves directly)
│   ├── students/
│   └── teachers/
├── staticfiles/            # Collected static files (Nginx serves directly)
├── venv/                   # Python virtual environment
├── nginx.conf              # Reference Nginx config
└── gunicorn.service        # Reference systemd service
```

---

## ✅ Deployment Checklist

- [ ] EC2 instance running (Ubuntu 22.04/24.04)
- [ ] Security Group: Port 80, 22 open
- [ ] Project cloned to `/var/www/school-app/`
- [ ] Virtual environment created and dependencies installed
- [ ] `.env` configured with correct IP
- [ ] `python manage.py migrate` run
- [ ] `python manage.py collectstatic --noinput` run
- [ ] `python manage.py createsuperuser` run
- [ ] Media folder permissions set (775, ubuntu:www-data)
- [ ] Gunicorn service enabled and running
- [ ] Nginx configured and running
- [ ] Website accessible at `http://34.229.200.54`
- [ ] Admin accessible at `http://34.229.200.54/admin/`
- [ ] Image upload working
- [ ] Images displaying on student/teacher list pages
