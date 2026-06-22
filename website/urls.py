from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('solutions/', views.solutions, name='solutions'),
    path('case-studies/', views.case_studies, name='case_studies'),
    path('articles/', views.articles, name='articles'),
    path('gallery/', views.gallery, name='gallery'),
    path('events/', views.events, name='events'),
    path('feedback/', views.feedback, name='feedback'),
    path('contact/', views.contact, name='contact'),
    path('assistant/', views.assistant, name='assistant'),
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-inquiry/<str:inquiry_id>/', views.admin_inquiry_detail, name='admin_inquiry_detail'),
    path('admin-inquiry/<str:inquiry_id>/update/', views.admin_update_inquiry, name='admin_update_inquiry'),
]
