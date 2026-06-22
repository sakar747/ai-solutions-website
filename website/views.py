import json
from difflib import SequenceMatcher

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .content import ARTICLES, CASE_STUDIES, EVENTS, FAQS, FEEDBACK, GALLERY, SERVICES
from .storage import (
    get_all_inquiries,
    get_inquiry,
    inquiry_counts,
    insert_inquiry,
    load_chatbot_responses,
    update_inquiry_status,
)


def home(request):
    return render(request, 'website/home.html', {
        'services': SERVICES[:3],
        'feedback': FEEDBACK[:2],
        'events': EVENTS[:1],
    })


def solutions(request):
    return render(request, 'website/solutions.html', {'services': SERVICES})


def case_studies(request):
    return render(request, 'website/case_studies.html', {'case_studies': CASE_STUDIES})


def feedback(request):
    return render(request, 'website/feedback.html', {'feedback': FEEDBACK})


def articles(request):
    return render(request, 'website/articles.html', {'articles': ARTICLES})


def gallery(request):
    return render(request, 'website/gallery.html', {'gallery': GALLERY})


def events(request):
    return render(request, 'website/events.html', {'events': EVENTS})


def assistant_page(request):
    return render(request, 'website/assistant.html', {'faqs': FAQS})


def contact(request):
    if request.method == 'POST':
        required = ['name', 'email', 'phone', 'company_name', 'country', 'job_title', 'job_details']
        form_data = {field: request.POST.get(field, '').strip() for field in required}
        form_data['service_interest'] = request.POST.get('service_interest', '').strip()

        missing = [field.replace('_', ' ').title() for field, value in form_data.items() if field in required and not value]
        if missing:
            messages.error(request, 'Please complete all required fields: ' + ', '.join(missing))
            return render(request, 'website/contact.html', {'services': SERVICES, 'form_data': form_data})

        saved = insert_inquiry(form_data)
        return redirect('inquiry_success', reference=saved['reference'])

    return render(request, 'website/contact.html', {'services': SERVICES})


def inquiry_success(request, reference):
    return render(request, 'website/inquiry_success.html', {'reference': reference})


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _detect_response(message: str):
    message = message.lower().strip()
    if not message:
        return 'Please type your question about AI-Solutions, services, events, feedback or submitting a job requirement.'

    # Simple database-connected response search.
    best_score = 0
    best_response = None
    for item in load_chatbot_responses():
        keywords = item.get('keywords', [])
        for keyword in keywords:
            keyword = keyword.lower()
            score = 1.0 if keyword in message else _similarity(message, keyword)
            if score > best_score:
                best_score = score
                best_response = item.get('response')

    if best_score >= 0.45 and best_response:
        return best_response

    if any(word in message for word in ['hello', 'hi', 'hey']):
        return 'Hello, I am the AI-Solutions virtual assistant. I can explain our services, events, feedback and how to submit a job requirement.'

    return 'I can help with AI-Solutions services, virtual assistants, software prototypes, events, feedback and job requirement inquiries. Please ask about one of these topics.'


@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'reply': 'Please send a message using POST.'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        payload = {}
    message = payload.get('message', '')
    return JsonResponse({'reply': _detect_response(message)})


def _admin_required(request):
    return request.session.get('admin_logged_in') is True


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session['admin_logged_in'] = True
            messages.success(request, 'Logged in successfully.')
            return redirect('admin_dashboard')
        messages.error(request, 'Invalid admin username or password.')
    return render(request, 'website/admin/login.html')


def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


def admin_dashboard(request):
    if not _admin_required(request):
        return redirect('admin_login')
    counts = inquiry_counts()
    recent = get_all_inquiries()[:5]
    return render(request, 'website/admin/dashboard.html', {
        'counts': counts,
        'recent': recent,
        'service_count': len(SERVICES),
        'event_count': len(EVENTS),
        'feedback_count': len(FEEDBACK),
    })


def admin_inquiries(request):
    if not _admin_required(request):
        return redirect('admin_login')
    rows = get_all_inquiries()
    query = request.GET.get('q', '').strip().lower()
    country = request.GET.get('country', '').strip().lower()
    if query:
        rows = [r for r in rows if query in ' '.join(str(v).lower() for v in r.values())]
    if country:
        rows = [r for r in rows if country == str(r.get('country', '')).lower()]
    return render(request, 'website/admin/inquiries.html', {'inquiries': rows, 'query': query, 'country': country})


def admin_inquiry_detail(request, reference):
    if not _admin_required(request):
        return redirect('admin_login')
    inquiry = get_inquiry(reference)
    if not inquiry:
        return HttpResponseForbidden('Inquiry not found.')
    if request.method == 'POST':
        status = request.POST.get('status', 'New')
        admin_note = request.POST.get('admin_note', '')
        update_inquiry_status(reference, status, admin_note)
        messages.success(request, 'Inquiry updated.')
        return redirect('admin_inquiry_detail', reference=reference)
    return render(request, 'website/admin/inquiry_detail.html', {'inquiry': inquiry})
