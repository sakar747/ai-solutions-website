from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .data_store import make_reference, storage


def home(request):
    return render(request, 'website/home.html')


def solutions(request):
    return render(request, 'website/solutions.html')


def case_studies(request):
    return render(request, 'website/case_studies.html')


def articles(request):
    return render(request, 'website/articles.html')


def gallery(request):
    return render(request, 'website/gallery.html')


def events(request):
    return render(request, 'website/events.html')


def assistant(request):
    return render(request, 'website/assistant.html')


def contact(request):
    if request.method == 'POST':
        inquiry = {
            'reference_number': make_reference('AIQ'),
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'company_name': request.POST.get('company_name', '').strip(),
            'country': request.POST.get('country', '').strip(),
            'job_title': request.POST.get('job_title', '').strip(),
            'service_interest': request.POST.get('service_interest', '').strip(),
            'job_details': request.POST.get('job_details', '').strip(),
            'status': 'New',
            'priority': request.POST.get('priority', 'Medium'),
        }
        required = ['name', 'email', 'phone', 'company_name', 'country', 'job_title', 'service_interest', 'job_details']
        if not all(inquiry.get(field) for field in required):
            messages.error(request, 'Please complete all required fields.')
        else:
            storage.insert('inquiries', inquiry)
            messages.success(request, f"Your inquiry has been submitted successfully. Reference: {inquiry['reference_number']}")
            return redirect('contact')
    return render(request, 'website/contact.html')


def feedback(request):
    if request.method == 'POST':
        feedback_data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'rating': request.POST.get('rating', '5'),
            'message': request.POST.get('message', '').strip(),
        }
        if feedback_data['name'] and feedback_data['message']:
            storage.insert('feedback', feedback_data)
            messages.success(request, 'Thank you for your feedback.')
            return redirect('feedback')
        messages.error(request, 'Please provide your name and feedback message.')
    feedback_rows = storage.all('feedback')[:6]
    return render(request, 'website/feedback.html', {'feedback_rows': feedback_rows})


def get_bot_reply(message):
    text = message.lower()
    rules = [
        (['chatbot', 'bot', 'assistant'], 'AI Chatbot Development', 'You may need an AI chatbot solution. We can build a virtual assistant for FAQs, lead capture, customer support and guided service selection.'),
        (['automation', 'automate', 'workflow'], 'Business Automation', 'This sounds like a business automation requirement. We can automate repetitive tasks, inquiry workflows and follow-up processes.'),
        (['dashboard', 'analytics', 'report'], 'Business Dashboard', 'This looks like a dashboard or reporting requirement. We can build a data dashboard to track inquiries, sales, operations and KPIs.'),
        (['website', 'web app', 'application', 'portal'], 'Web Application Development', 'This sounds like a web application requirement. We can build a professional website or web platform with forms, dashboards and database features.'),
        (['price', 'cost', 'budget'], 'Consultation', 'Pricing depends on project scope. Please submit your requirements through the contact form so the team can review the features and estimate the cost.'),
        (['contact', 'inquiry', 'consultation', 'project'], 'Contact', 'You can submit your project inquiry from the Contact page. Include your company name, service interest and project details.'),
    ]
    for keywords, category, reply in rules:
        if any(keyword in text for keyword in keywords):
            return {
                'category': category,
                'reply': reply,
                'next_step': 'Please submit a detailed inquiry through the Contact page so the admin team can review it.'
            }
    return {
        'category': 'General AI Solution',
        'reply': 'I can help you choose a suitable AI or software solution. Tell me if you need a chatbot, automation, dashboard, website or custom system.',
        'next_step': 'You can also submit your project details through the Contact page.'
    }


@csrf_exempt
@require_POST
def chatbot_api(request):
    message = request.POST.get('message', '')
    if not message:
        return JsonResponse({'reply': 'Please type your question.', 'category': 'General', 'next_step': ''})
    return JsonResponse(get_bot_reply(message))


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            messages.error(request, 'Please log in to access the admin dashboard.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session['is_admin'] = True
            messages.success(request, 'Logged in successfully.')
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid admin username or password.')
    return render(request, 'website/admin_login.html')


def admin_logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')


@admin_required
def admin_dashboard(request):
    inquiries = storage.all('inquiries')
    status_filter = request.GET.get('status', '')
    service_filter = request.GET.get('service', '')
    filtered = inquiries
    if status_filter:
        filtered = [item for item in filtered if item.get('status') == status_filter]
    if service_filter:
        filtered = [item for item in filtered if item.get('service_interest') == service_filter]
    stats = {
        'total': len(inquiries),
        'new': len([i for i in inquiries if i.get('status') == 'New']),
        'progress': len([i for i in inquiries if i.get('status') == 'In Progress']),
        'completed': len([i for i in inquiries if i.get('status') == 'Completed']),
    }
    return render(request, 'website/admin_dashboard.html', {
        'inquiries': filtered,
        'stats': stats,
        'status_filter': status_filter,
        'service_filter': service_filter,
    })


@admin_required
def admin_inquiry_detail(request, inquiry_id):
    inquiry = storage.get('inquiries', inquiry_id)
    if not inquiry:
        messages.error(request, 'Inquiry not found.')
        return redirect('admin_dashboard')
    return render(request, 'website/admin_inquiry_detail.html', {'inquiry': inquiry})


@admin_required
@require_POST
def admin_update_inquiry(request, inquiry_id):
    storage.update('inquiries', inquiry_id, {
        'status': request.POST.get('status', 'New'),
        'priority': request.POST.get('priority', 'Medium'),
        'admin_note': request.POST.get('admin_note', '').strip(),
    })
    messages.success(request, 'Inquiry updated successfully.')
    return redirect('admin_inquiry_detail', inquiry_id=inquiry_id)
