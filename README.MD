# 3-Tier School Management System

![Django](https://img.shields.io/badge/Django-4.2-blue?logo=django)
![Python](https://img.shields.io/badge/Python-3.11-yellow?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

A **3-tier architecture school management system** built using **Django**, **MySQL**, and **Nginx**, fully containerized with Docker. The project demonstrates a scalable setup with separate layers for database, backend, and web server.

---

## 🏗️ Architecture

```
      ┌───────────┐
      │   Nginx   │  <-- Serves static & media files, reverse proxy
      └────┬──────┘
           │
      ┌────┴──────┐
      │  Django   │  <-- Application backend, migrations, admin
      └────┬──────┘
           │
      ┌────┴──────┐
      │   MySQL   │  <-- Database layer
      └───────────┘
```

---

## 🚀 Features

- **Full CRUD operations** for school data management
- **User authentication** and admin management panel
- **Automatic Django migrations** on container start
- **Separate volumes** for `static` and `media` files
- **Dockerized 3-tier architecture** ready for production deployment
- **Health checks** to ensure proper service startup sequence
- **Nginx reverse proxy** with static file serving

---

## 📦 Technology Stack

| Layer      | Technology             | Purpose                    |
|------------|------------------------|---------------------------|
| Frontend   | Nginx                  | Web server, reverse proxy |
| Backend    | Python 3.11, Django   | Application logic, API    |
| Database   | MySQL 8.0             | Data persistence          |
| Container  | Docker, Docker Compose | Containerization          |

---

## ⚙️ Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git installed

### 1. Clone the repository
```bash
git clone https://github.com/Jaishankar7655/3-tier-devops-project-.git
cd 3-tier-devops-project-
```

### 2. Create environment file
Create a `.env` file in the root directory:

```env
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=school_db
MYSQL_USER=myuser
MYSQL_PASSWORD=mypassword

# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Build and start containers
```bash
docker-compose up --build
```

**Note:** The Django container waits for MySQL to be healthy before starting.

### 4. Access the application
- **Django Development Server:** http://localhost:8000
- **Nginx (Production-like):** http://localhost
- **Django Admin:** http://localhost/admin

---

## 💾 Docker Volumes

The following volumes ensure data persistence across container restarts:

- **`db_data`**: MySQL database persistent storage
- **`static_volume`**: Django static files (CSS, JS, images)
- **`media_volume`**: User uploaded files and media

---

## 🔧 Useful Commands

### Run migrations manually
```bash
docker-compose exec django python manage.py migrate
```

### Create superuser for admin access
```bash
docker-compose exec django python manage.py createsuperuser
```

### Collect static files
```bash
docker-compose exec django python manage.py collectstatic --noinput
```

### View logs
```bash
docker-compose logs django
docker-compose logs mysql
docker-compose logs nginx
```

### Stop containers
```bash
docker-compose down
```

### Remove volumes (⚠️ This will delete all data)
```bash
docker-compose down -v
```

---

## 📝 Nginx Configuration

The Nginx service is configured to:

- **Static files**: Serve from `/static/` path mapped to `static_volume`
- **Media files**: Serve from `/media/` path mapped to `media_volume`
- **Proxy pass**: Forward all other requests to Django backend at `http://django:8000`

### Key Nginx Configuration:
```nginx
server {
    listen 80;
    server_name localhost;

    # Serve static files
    location /static/ {
        alias /static/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Serve media files
    location /media/ {
        alias /media/;
        expires 1d;
        add_header Cache-Control "public";
    }

    # Proxy to Django
    location / {
        proxy_pass http://django:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📁 Project Structure

```
3-tier-devops-project/
├── Dockerfile                 # Django container configuration
├── docker-compose.yml        # Multi-container orchestration
├── requirements.txt          # Python dependencies
├── nginx.conf               # Nginx server configuration
├── .env                     # Environment variables (create this)
├── app/                     # Django application
│   ├── settings.py         # Django settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI configuration
│   ├── models.py          # Database models
│   ├── views.py           # Business logic
│   └── admin.py           # Admin interface
├── static/                 # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── templates/             # HTML templates
└── README.md             # Project documentation
```

---

## 🚀 Deployment Considerations

### For Production:
1. **Environment Variables**: Use proper secret management
2. **Database**: Consider managed MySQL service (AWS RDS, Google Cloud SQL)
3. **Static Files**: Use CDN for better performance
4. **SSL/HTTPS**: Configure SSL certificates in Nginx
5. **Security**: Update `ALLOWED_HOSTS` and disable `DEBUG`

### Environment-specific configurations:
```env
# Production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. MySQL Connection Error
```bash
# Check if MySQL container is running
docker-compose ps

# Check MySQL logs
docker-compose logs mysql
```

#### 2. Static Files Not Loading
```bash
# Collect static files
docker-compose exec django python manage.py collectstatic --noinput
```

#### 3. Permission Issues
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./static ./media
```

#### 4. Container Health Check Failed
```bash
# Restart services in order
docker-compose restart mysql
docker-compose restart django
docker-compose restart nginx
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Repository**: [3-tier-devops-project](https://github.com/Jaishankar7655/3-tier-devops-project-)
- **Django Documentation**: https://docs.djangoproject.com/
- **Docker Documentation**: https://docs.docker.com/
- **MySQL Documentation**: https://dev.mysql.com/doc/

---

## 📞 Support

If you encounter any issues or have questions, please:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing [Issues](https://github.com/Jaishankar7655/3-tier-devops-project-/issues)
3. Create a new issue with detailed information

---

**Made with ❤️ for learning DevOps and 3-tier architecture**