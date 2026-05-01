from django.urls import path
from . import views

urlpatterns = [
    path("", views.library_dashboard, name="library_dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.add_book, name="add_book"),
    path("borrow/", views.borrow_book, name="borrow_book"),
    path("return/<uuid:pk>/", views.return_book, name="return_book"),
    path("returns/", views.manage_returns, name="manage_returns"),
    path("overdue/", views.overdue_list, name="overdue_list"),
]
