from django.urls import path
from . import views

urlpatterns = [
    path('', views.notice_list, name='notice_list'),
    path('create/', views.notice_create, name='notice_create'),
    path('delete/<int:notice_id>/', views.notice_delete, name='notice_delete'),
    path('public/', views.public_notices, name='public_notices'),
]
