from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('solutions/', views.solutions, name='solutions'),
    path('case-studies/', views.case_studies, name='case_studies'),
    path('feedback/', views.feedback, name='feedback'),
    path('articles/', views.articles, name='articles'),
    path('gallery/', views.gallery, name='gallery'),
    path('events/', views.events, name='events'),
    path('assistant/', views.assistant_page, name='assistant'),
    path('contact/', views.contact, name='contact'),
    path('inquiry-success/<str:reference>/', views.inquiry_success, name='inquiry_success'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/inquiries/', views.admin_inquiries, name='admin_inquiries'),
    path('dashboard/inquiries/<str:reference>/', views.admin_inquiry_detail, name='admin_inquiry_detail'),
]
