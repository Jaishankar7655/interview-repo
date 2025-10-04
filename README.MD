# Django Application Deployment Guide
## Complete Setup with Custom Domain & SSL Certificate

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Overview](#project-overview)
3. [Initial Server Setup](#initial-server-setup)
4. [Domain Configuration](#domain-configuration)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Application Deployment](#application-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

---

## Prerequisites

### Required Items
- Ubuntu Server (20.04 LTS or newer)
- A registered domain name (e.g., `yourdomain.com`)
- Access to domain DNS management
- SSH access to your server
- Basic knowledge of Linux commands

### Server Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 20GB minimum
- **OS**: Ubuntu 20.04 LTS or newer

---

## Project Overview

### Architecture
```
Internet → Domain (DNS) → Server (52.66.191.149)
                              ↓
                          Nginx (Port 80/443)
                              ↓
                          Django App (Port 8000)
                              ↓
                          MySQL Database (Port 3306)
```

### Technology Stack
- **Backend**: Django (Python 3.11)
- **Database**: MySQL 8.0
- **Web Server**: Nginx
- **Container**: Docker & Docker Compose
- **SSL**: Let's Encrypt (Certbot)

---

## Initial Server Setup

### 1. Connect to Your Server
```bash
ssh ubuntu@52.66.191.149
```

### 2. Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
```

### 4. Install Docker Compose
```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 5. Install Certbot for SSL
```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

## Domain Configuration

### 1. Purchase a Domain
- Go to domain registrars like:
  - **Namecheap**: https://www.namecheap.com
  - **GoDaddy**: https://www.godaddy.com
  - **Google Domains**: https://domains.google
  - **Cloudflare**: https://www.cloudflare.com

### 2. Configure DNS Records

Log in to your domain provider's DNS management panel and add these records:

#### Required DNS Records

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 52.66.191.149 | 3600 |
| A | www | 52.66.191.149 | 3600 |

**Example for different providers:**

#### Namecheap:
1. Go to Dashboard → Domain List
2. Click "Manage" next to your domain
3. Navigate to "Advanced DNS"
4. Add records as shown above

#### Cloudflare:
1. Select your domain
2. Go to "DNS" section
3. Click "Add record"
4. Add both A records

#### GoDaddy:
1. My Products → DNS
2. Add the A records

### 3. Verify DNS Propagation
```bash
# Check DNS propagation (may take 5 minutes to 48 hours)
nslookup yourdomain.com
dig yourdomain.com

# Online tools:
# - https://dnschecker.org
# - https://www.whatsmydns.net
```

**Screenshot Location**: Take a screenshot of your DNS records configuration panel showing both A records.

---

## SSL Certificate Setup

### 1. Update Nginx Configuration for Certbot

First, create a temporary Nginx config without SSL:

```bash
cd ~/interview-repo
nano nginx.conf
```

Replace content with:
```nginx
events {}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location /static/ {
            alias /static/;
        }

        location /media/ {
            alias /media/;
        }

        location / {
            proxy_pass http://django_app:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 2. Update Docker Compose for Certbot

Update `docker-compose.yml`:
```bash
nano docker-compose.yml
```

Add Certbot volumes to nginx service:
```yaml
nginx:
  image: nginx:latest
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - static_volume:/static
    - media_volume:/media
    - ./certbot/conf:/etc/letsencrypt
    - ./certbot/www:/var/www/certbot
  depends_on:
    - django
  networks:
    - app_network
  container_name: nginx_proxy
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check if containers are running
docker ps
```

### 4. Obtain SSL Certificate

#### Method 1: Using Certbot with Docker (Recommended)
```bash
# Create directories
mkdir -p certbot/conf certbot/www

# Run Certbot
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -v $(pwd)/certbot/logs:/var/log/letsencrypt \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d yourdomain.com \
  -d www.yourdomain.com
```

#### Method 2: Using System Certbot
```bash
# Stop nginx container temporarily
docker-compose stop nginx

# Run certbot
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos

# Copy certificates to project directory
sudo mkdir -p certbot/conf/live/yourdomain.com
sudo cp -L /etc/letsencrypt/live/yourdomain.com/* certbot/conf/live/yourdomain.com/
sudo chown -R $USER:$USER certbot/

# Restart nginx
docker-compose up -d nginx
```

**Screenshot Location**: Take a screenshot showing successful certificate issuance.

### 5. Update Nginx with SSL Configuration

```bash
nano nginx.conf
```

Replace with:
```nginx
events {}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # HTTP → HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS configuration
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL certificates
        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

        # SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Increase upload size if needed
        client_max_body_size 100M;

        location /static/ {
            alias /static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /media/;
        }

        location / {
            proxy_pass http://django_app:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
    }
}
```

### 6. Restart Nginx
```bash
# Restart nginx to apply SSL configuration
docker-compose restart nginx

# Check nginx logs
docker logs nginx_proxy
```

### 7. Verify SSL Configuration
```bash
# Test SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Online tools:
# - https://www.ssllabs.com/ssltest/
# - https://www.digicert.com/help/
```

**Screenshot Location**: Take a screenshot of your browser showing the padlock icon and valid SSL certificate.

---

## Application Deployment

### 1. Prepare Environment File
```bash
cd ~/interview-repo
nano .env
```

Add your configuration:
```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,52.66.191.149
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# MySQL Configuration
MYSQL_ROOT_PASSWORD=strong_root_password
MYSQL_DATABASE=django_db
MYSQL_USER=django_user
MYSQL_PASSWORD=strong_user_password
MYSQL_HOST=mysql_db
MYSQL_PORT=3306

# MySQL Root User
MYSQL_ROOT_USER=root
```

### 2. Update Django Settings

Edit `settings.py`:
```python
# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Read from environment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
```

### 3. Build and Deploy
```bash
# Stop existing containers
docker-compose down

# Build and start services
docker-compose up -d --build

# Check container status
docker ps

# View logs
docker-compose logs -f
```

### 4. Collect Static Files
```bash
# Collect static files
docker exec -it django_app python manage.py collectstatic --noinput

# Create superuser
docker exec -it django_app python manage.py createsuperuser
```

### 5. Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Test database connection
docker exec -it django_app python manage.py dbshell

# Test application
curl https://yourdomain.com
```

**Screenshot Location**: Take a screenshot of your website loaded over HTTPS with the green padlock.

---

## SSL Certificate Auto-Renewal

### Setup Auto-Renewal

#### Method 1: Docker-based Renewal (Recommended)

Create renewal script:
```bash
nano ~/renew-ssl.sh
```

Add:
```bash
#!/bin/bash
cd ~/interview-repo

docker run --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  -v $(pwd)/certbot/logs:/var/log/letsencrypt \
  certbot/certbot renew --webroot --webroot-path=/var/www/certbot

docker-compose restart nginx
```

Make executable:
```bash
chmod +x ~/renew-ssl.sh
```

Add to crontab:
```bash
crontab -e
```

Add this line:
```
0 3 * * * /home/ubuntu/renew-ssl.sh >> /home/ubuntu/certbot-renew.log 2>&1
```

#### Method 2: System Certbot Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Auto-renewal is already set up via systemd
sudo systemctl status certbot.timer
```

---

## Firewall Configuration

### Configure UFW (Ubuntu Firewall)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## Monitoring & Logs

### View Container Logs
```bash
# All logs
docker-compose logs -f

# Specific service logs
docker logs django_app -f
docker logs nginx_proxy -f
docker logs mysql_db -f

# Last 100 lines
docker logs --tail 100 django_app
```

### Monitor Resources
```bash
# Check container stats
docker stats

# Check disk usage
df -h
docker system df
```

---

## Troubleshooting

### Common Issues

#### 1. DNS Not Resolving
```bash
# Check DNS propagation
dig yourdomain.com
nslookup yourdomain.com

# Wait for propagation (up to 48 hours)
# Use online tools: https://dnschecker.org
```

#### 2. SSL Certificate Failed
```bash
# Check if port 80 is accessible
curl -I http://yourdomain.com

# View certbot logs
docker logs certbot
cat certbot/logs/letsencrypt.log

# Verify DNS points to correct IP
dig yourdomain.com +short
```

#### 3. 502 Bad Gateway
```bash
# Check if Django is running
docker ps | grep django_app

# Check Django logs
docker logs django_app

# Restart services
docker-compose restart
```

#### 4. Database Connection Issues
```bash
# Check MySQL is running
docker ps | grep mysql_db

# Test database connection
docker exec -it mysql_db mysql -u django_user -p

# Check MySQL logs
docker logs mysql_db
```

#### 5. Static Files Not Loading
```bash
# Collect static files again
docker exec -it django_app python manage.py collectstatic --noinput

# Check nginx logs
docker logs nginx_proxy

# Verify volume mounts
docker inspect django_app | grep -A 10 Mounts
```

### Debug Commands
```bash
# Test nginx configuration
docker exec nginx_proxy nginx -t

# Reload nginx
docker exec nginx_proxy nginx -s reload

# Check Django configuration
docker exec -it django_app python manage.py check

# Run migrations
docker exec -it django_app python manage.py migrate
```

---

## Maintenance

### Regular Tasks

#### Daily
```bash
# Check logs for errors
docker-compose logs --tail=100

# Monitor disk space
df -h
```

#### Weekly
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean Docker resources
docker system prune -a --volumes -f
```

#### Monthly
```bash
# Check SSL certificate expiry
docker run --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  certbot/certbot certificates

# Backup database
docker exec mysql_db mysqldump -u root -p$MYSQL_ROOT_PASSWORD django_db > backup_$(date +%Y%m%d).sql
```

### Backup Strategy

#### Database Backup
```bash
# Manual backup
docker exec mysql_db mysqldump -u root -p django_db > backup.sql

# Automated backup script
nano ~/backup.sh
```

Add:
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker exec mysql_db mysqldump -u root -p$MYSQL_ROOT_PASSWORD django_db > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz certbot/conf

# Keep only last 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Make executable and schedule:
```bash
chmod +x ~/backup.sh
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh
```

---

## Performance Optimization

### 1. Enable Gzip Compression (Nginx)
Add to nginx.conf in the `http` block:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### 2. Optimize Django Settings
```python
# settings.py
DEBUG = False
CONN_MAX_AGE = 600  # Database connection pooling

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Use Gunicorn Instead of runserver

Update Dockerfile CMD:
```dockerfile
CMD ["sh", "-c", "until nc -z $MYSQL_HOST 3306; do echo Waiting for MySQL...; sleep 3; done; \
    python manage.py migrate && \
    gunicorn --workers 3 --bind 0.0.0.0:8000 yourproject.wsgi:application"]
```

---

## Security Checklist

- [ ] SSL certificate installed and auto-renewal configured
- [ ] Firewall enabled (UFW) with only necessary ports open
- [ ] Strong passwords set for database
- [ ] DEBUG=False in production
- [ ] SECRET_KEY changed from default
- [ ] ALLOWED_HOSTS properly configured
- [ ] Security headers enabled in Nginx
- [ ] Regular backups scheduled
- [ ] Docker images kept up to date
- [ ] Server packages regularly updated

---

## Useful Commands Reference

```bash
# Docker Compose
docker-compose up -d                 # Start all services
docker-compose down                  # Stop all services
docker-compose restart               # Restart all services
docker-compose logs -f               # View logs
docker-compose ps                    # List containers

# Docker
docker ps                            # List running containers
docker logs <container_name>         # View container logs
docker exec -it <container> bash     # Enter container shell

# SSL
sudo certbot renew --dry-run        # Test SSL renewal
sudo certbot certificates            # List certificates

# System
sudo systemctl status docker         # Check Docker status
sudo ufw status                      # Check firewall status
df -h                                # Check disk space
free -h                              # Check memory usage
```

---

## Support & Resources

### Documentation
- Django: https://docs.djangoproject.com
- Docker: https://docs.docker.com
- Nginx: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/docs/
- Certbot: https://certbot.eff.org/docs/

### Testing Tools
- SSL Test: https://www.ssllabs.com/ssltest/
- DNS Checker: https://dnschecker.org
- Website Speed: https://pagespeed.web.dev
- Security Headers: https://securityheaders.com

---

## Screenshots Checklist

For your deliverables, ensure you have these screenshots:

1. **DNS Configuration**
   - Screenshot of DNS management panel showing A records
   - Both @ and www records pointing to 52.66.191.149

2. **SSL Certificate Issuance**
   - Terminal output showing successful certificate generation
   - Certificate details showing expiry date

3. **Live Website**
   - Browser showing HTTPS with padlock icon
   - Certificate details showing valid SSL
   - Website loading successfully
   - Admin panel accessible

4. **Additional (Optional)**
   - Docker containers running (`docker ps`)
   - SSL Labs test results (A+ grade)
   - Website speed test results

---

## Conclusion

Your Django application is now deployed with:
- ✅ Custom domain configured
- ✅ SSL certificate installed (Let's Encrypt)
- ✅ Automatic HTTP → HTTPS redirection
- ✅ Production-ready setup with Docker
- ✅ Secure configuration with proper headers
- ✅ Auto-renewal for SSL certificates

Visit your website: **https://yourdomain.com**

---

**Last Updated**: October 2025  
**Maintainer**: Your Name  
**Project**: Django Docker Deployment
