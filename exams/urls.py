from django.urls import path
from . import views

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("<uuid:pk>/", views.exam_detail, name="exam_detail"),
    path("create/", views.exam_create, name="exam_create"),
    path("<uuid:pk>/publish/", views.exam_publish, name="exam_publish"),
    path("<uuid:pk>/marks/", views.enter_marks, name="enter_marks"),
    path("<uuid:pk>/results/", views.exam_results, name="exam_results"),
    path("<uuid:pk>/report-cards/", views.report_card_list, name="report_card_list"),
    path("<uuid:pk>/generate-reports/", views.generate_report_cards, name="generate_report_cards"),
    path("report/<uuid:pk>/", views.report_card_view, name="report_card_view"),
]