# Render Deployment Notes

Use the same Render + MongoDB Atlas workflow.

## Render Web Service settings

Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start Command:

```bash
gunicorn ai_solutions.wsgi:application
```

Root Directory: leave blank if the repository root contains `manage.py`.

## Required Environment Variables

```text
DJANGO_SECRET_KEY=use-any-long-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.onrender.com
MONGO_URI=your-mongodb-atlas-connection-string
MONGO_DB_NAME=ai_solutions_db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
```

## MongoDB Atlas

In Atlas Network Access, add:

```text
0.0.0.0/0
```

This allows Render to connect to the Atlas database for the student/demo deployment.

## Admin URL

```text
/admin-login/
```

Use the `ADMIN_USERNAME` and `ADMIN_PASSWORD` values from Render.
