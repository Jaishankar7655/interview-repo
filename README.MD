#  Deployment Documentation (Python + Django)

## 1. Project Overview

* **Language Used**: Python (Django Framework)
* **Deployment Tools**: Docker, Docker Compose, Nginx (Reverse Proxy), Certbot (SSL)
* **Hosting**: AWS EC2 (Ubuntu 22.04)
* **Live URL**:

  * HTTP → [http://52.66.191.149:8000/](http://52.66.191.149:8000/)
  * HTTPS → [https://52.66.191.149](https://52.66.191.149)  (SSL Enabled)

---



## 3. Deployment Steps

###  Step 1: Update Server

```bash
sudo apt update && sudo apt upgrade -y
```

###  Step 2: Install Docker & Docker Compose

```bash
# Install Docker
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo apt install docker-compose -y
```

### 🔹 Step 3: Add User to Docker Group

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---





## 6. SSL Certificate (HTTPS Setup)

### Install Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Generate Certificate

```bash
sudo certbot --nginx -d 52.66.191.149
```

### Auto-Renew SSL

```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

Now your app is accessible at:

* **HTTP → redirects to HTTPS automatically**
* **HTTPS → [https://52.66.191.149](https://52.66.191.149)**

---

## 7. Screenshots

(Save in `screenshots/` folder)

1. Docker containers running
2. Nginx configuration proof
3. HTTPS enabled webpage

---
