from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Book, BookBorrow
from schools.views import admin_required


@admin_required
def library_dashboard(request):
    school = request.user.school
    books = Book.objects.filter(school=school)
    active_borrows = BookBorrow.objects.filter(book__school=school, is_returned=False).select_related("student", "book")
    overdue = active_borrows.filter(due_date__lt=timezone.now().date()).count()
    return render(request, "library/dashboard.html", {
        "school": school,
        "total_books": books.count(),
        "active_borrows": active_borrows[:20],
        "active_count": active_borrows.count(),
        "overdue_count": overdue,
    })


@admin_required
def book_list(request):
    school = request.user.school
    books = Book.objects.filter(school=school).order_by("title")
    return render(request, "library/book_list.html", {"school": school, "books": books})


@admin_required
def borrow_book(request):
    from students.models import Student
    school = request.user.school
    books = Book.objects.filter(school=school, available_copies__gt=0)
    students = Student.objects.filter(school=school, is_active=True)
    if request.method == "POST":
        try:
            book = Book.objects.get(id=request.POST.get("book_id"), school=school)
            student = Student.objects.get(id=request.POST.get("student_id"), school=school)
            due_date = timezone.now().date() + timezone.timedelta(days=int(request.POST.get("due_days", 14)))
            BookBorrow.objects.create(book=book, student=student, due_date=due_date)
            book.available_copies = max(0, book.available_copies - 1)
            book.save()
            messages.success(request, f"'{book.title}' borrowed by {student.get_full_name()}!")
            return redirect("library_dashboard")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, "library/borrow_book.html", {"school": school, "books": books, "students": students})


@admin_required
def return_book(request, pk):
    school = request.user.school
    record = get_object_or_404(BookBorrow, id=pk, book__school=school)
    if request.method == "POST":
        record.is_returned = True
        record.returned_date = timezone.now().date()
        record.save()
        record.book.available_copies += 1
        record.book.save()
        messages.success(request, f"'{record.book.title}' returned!")
        return redirect("library_dashboard")
    return render(request, "library/return_book.html", {"record": record, "school": school})


@admin_required
def manage_returns(request):
    school = request.user.school
    active_borrows = BookBorrow.objects.filter(book__school=school, is_returned=False).select_related("student", "book").order_by("due_date")
    return render(request, "library/manage_returns.html", {"school": school, "active_borrows": active_borrows})


@admin_required
def overdue_list(request):
    school = request.user.school
    overdue = BookBorrow.objects.filter(book__school=school, is_returned=False, due_date__lt=timezone.now().date()).select_related("student", "book").order_by("due_date")
    return render(request, "library/overdue_list.html", {"school": school, "overdue_records": overdue})
