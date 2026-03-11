from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("academics/", views.academics, name="academics"),
    path("contact/", views.contact, name="contact"),
    path("gallery/", views.gallery, name="gallery"),
    path("kcse-results/", views.kcse_results, name="kcse_results"),
    path("co-curricular/", views.co_curricular, name="co_curricular"),
    path("parent-comments/", views.parent_comments, name="parent_comments"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
]
