# Render Deployment Guide

## Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

## Start Command
```bash
gunicorn ai_solutions.wsgi:application
```

## Environment Variables
Add these in Render:

```text
DJANGO_SECRET_KEY=your-long-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.onrender.com
MONGO_URI=your-full-mongodb-atlas-uri
MONGO_DB_NAME=ai_solutions_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-admin-password
```

## MongoDB Atlas
Use a free Atlas cluster. In Network Access, allow Render by adding `0.0.0.0/0` for demo deployment.
