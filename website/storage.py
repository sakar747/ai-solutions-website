import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from django.conf import settings

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except Exception:  # pragma: no cover - allows demo without PyMongo installed
    MongoClient = None
    PyMongoError = Exception

DATA_DIR = Path(settings.BASE_DIR) / 'data_store'
DATA_DIR.mkdir(exist_ok=True)
INQUIRIES_FILE = DATA_DIR / 'inquiries.json'
CHATBOT_FILE = DATA_DIR / 'chatbot_responses.json'


def _json_load(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def _json_save(path: Path, data) -> None:
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _mongo_db():
    if MongoClient is None:
        return None
    try:
        client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=800)
        client.server_info()
        return client[settings.MONGO_DB_NAME]
    except Exception:
        return None


def generate_reference(prefix: str = 'INQ') -> str:
    year = datetime.now().year
    total = len(get_all_inquiries()) + 1
    return f'{prefix}-{year}-{total:04d}'


def insert_inquiry(inquiry: Dict) -> Dict:
    inquiry = inquiry.copy()
    inquiry['reference'] = inquiry.get('reference') or generate_reference()
    inquiry['status'] = inquiry.get('status') or 'New'
    inquiry['created_at'] = inquiry.get('created_at') or datetime.now().strftime('%Y-%m-%d %H:%M')

    db = _mongo_db()
    if db is not None:
        db.inquiries.insert_one(inquiry)
        inquiry.pop('_id', None)
        return inquiry

    inquiries = _json_load(INQUIRIES_FILE, [])
    inquiries.append(inquiry)
    _json_save(INQUIRIES_FILE, inquiries)
    return inquiry


def get_all_inquiries() -> List[Dict]:
    db = _mongo_db()
    if db is not None:
        rows = list(db.inquiries.find().sort('created_at', -1))
        for row in rows:
            row.pop('_id', None)
        return rows
    return list(reversed(_json_load(INQUIRIES_FILE, [])))


def get_inquiry(reference: str) -> Optional[Dict]:
    db = _mongo_db()
    if db is not None:
        row = db.inquiries.find_one({'reference': reference})
        if row:
            row.pop('_id', None)
        return row
    for row in _json_load(INQUIRIES_FILE, []):
        if row.get('reference') == reference:
            return row
    return None


def update_inquiry_status(reference: str, status: str, admin_note: str = '') -> bool:
    db = _mongo_db()
    if db is not None:
        result = db.inquiries.update_one(
            {'reference': reference},
            {'$set': {'status': status, 'admin_note': admin_note, 'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M')}}
        )
        return result.modified_count > 0

    rows = _json_load(INQUIRIES_FILE, [])
    updated = False
    for row in rows:
        if row.get('reference') == reference:
            row['status'] = status
            row['admin_note'] = admin_note
            row['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            updated = True
            break
    _json_save(INQUIRIES_FILE, rows)
    return updated


def inquiry_counts() -> Dict:
    rows = get_all_inquiries()
    by_country: Dict[str, int] = {}
    by_service: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    for row in rows:
        country = row.get('country') or 'Unknown'
        service = row.get('service_interest') or row.get('job_title') or 'General'
        status = row.get('status') or 'New'
        by_country[country] = by_country.get(country, 0) + 1
        by_service[service] = by_service.get(service, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
    return {
        'total': len(rows),
        'by_country': by_country,
        'by_service': by_service,
        'by_status': by_status,
    }


def load_chatbot_responses() -> List[Dict]:
    responses = _json_load(CHATBOT_FILE, [])
    if responses:
        return responses
    defaults = [
        {
            'intent': 'services',
            'keywords': ['service', 'solutions', 'software', 'offer', 'provide'],
            'response': 'AI-Solutions offers AI-powered virtual assistants, rapid software prototyping, digital employee experience tools and business automation solutions.'
        },
        {
            'intent': 'virtual_assistant',
            'keywords': ['virtual assistant', 'chatbot', 'assistant', 'ai bot'],
            'response': 'Our AI-powered virtual assistant helps organisations answer user questions, guide customers and reduce repetitive support work.'
        },
        {
            'intent': 'prototype',
            'keywords': ['prototype', 'prototyping', 'demo', 'mockup'],
            'response': 'Rapid software prototyping helps clients test ideas early before investing in full system development.'
        },
        {
            'intent': 'contact',
            'keywords': ['contact', 'inquiry', 'job requirement', 'job details', 'project'],
            'response': 'You can submit your job requirement using the Contact Us form. Please include your name, email, phone, company, country, job title and job details.'
        },
        {
            'intent': 'events',
            'keywords': ['event', 'events', 'workshop', 'demo day', 'upcoming'],
            'response': 'You can view upcoming demonstrations and promotional sessions on the Upcoming Events page.'
        },
        {
            'intent': 'feedback',
            'keywords': ['feedback', 'rating', 'review', 'reviews'],
            'response': 'Customer feedback and ratings are available on the Customer Feedback page.'
        },
    ]
    _json_save(CHATBOT_FILE, defaults)
    return defaults
