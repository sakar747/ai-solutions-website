# AI-Solutions Prototype

## Project title
AI-Solutions: AI-Powered Software Solutions Website with Client Inquiry Management System

## What this prototype includes
- Public company website for AI-Solutions
- Software solutions page
- Past solutions / case studies page
- Customer feedback with ratings
- Articles / insights page
- Promotional event gallery
- Upcoming events page
- AI virtual assistant chatbot
- Contact Us / job requirement inquiry form
- Password-protected admin login
- Admin dashboard with inquiry counts
- Manage inquiries and update inquiry status

## Technology stack
- Python
- Django
- MongoDB using PyMongo
- HTML
- CSS
- JavaScript

## Setup steps

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: create `.env` from `.env.example` and change credentials.

4. Start MongoDB locally if available. The app uses MongoDB through PyMongo. If MongoDB or PyMongo is unavailable, it falls back to a local JSON store so the prototype can still be demonstrated.

5. Run the Django development server:

```bash
python manage.py runserver
```

6. Open:

```text
http://127.0.0.1:8000/
```

## Admin login
Default demo credentials:

```text
Username: admin
Password: admin123
```

Change these in `.env` before final submission.

## Suggested demo flow
1. Open Home page.
2. Show Solutions, Past Solutions, Feedback, Articles, Gallery and Events pages.
3. Open Assistant page and ask: `What services do you provide?`
4. Submit a Contact Us inquiry with job requirement details.
5. Log in as admin.
6. Show dashboard inquiry counts.
7. Open Manage Inquiries and view the submitted inquiry.
8. Update inquiry status to Reviewed or Contacted.

## Assignment alignment
This prototype is designed for the Computer Systems Engineering scenario. Customers can view AI-Solutions' software services and submit job requirements without creating accounts. The admin area is password protected and shows customer inquiry data.


## Render deployment
This project has been prepared for Render deployment. Use:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

as the build command and:

```bash
gunicorn ai_solutions.wsgi:application
```

as the start command. Add MongoDB Atlas and admin credentials in Render environment variables. See `RENDER_DEPLOYMENT.md` for the full list.
