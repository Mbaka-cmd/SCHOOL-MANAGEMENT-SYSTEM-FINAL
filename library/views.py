from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Book, BorrowRecord
from schools.views import admin_required


@admin_required
def library_dashboard(request):
    school = request.user.school
    books = Book.objects.filter(school=school)
    # Refresh overdue statuses
    for r in BorrowRecord.objects.filter(school=school, status='borrowed'):
        if timezone.now() > r.due_at:
            r.save()
    active_borrows = BorrowRecord.objects.filter(
        school=school, status__in=["borrowed", "overdue"]
    ).select_related("student", "book")
    overdue_count = BorrowRecord.objects.filter(school=school, status="overdue").count()
    total_fines = sum(r.fine_amount for r in BorrowRecord.objects.filter(school=school, status="overdue", fine_paid=False))
    return render(request, "library/dashboard.html", {
        "school": school,
        "total_books": books.count(),
        "active_borrows": active_borrows[:20],
        "active_count": active_borrows.count(),
        "overdue_count": overdue_count,
        "total_fines": total_fines,
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
            due_days = int(request.POST.get("due_days", 3))
            due_at = timezone.now() + timedelta(days=due_days)
            BorrowRecord.objects.create(
                school=school,
                book=book,
                student=student,
                due_at=due_at,
            )
            book.available_copies = max(0, book.available_copies - 1)
            book.save()
            messages.success(request, f"'{book.title}' borrowed by {student.get_full_name()}!")
            return redirect("library_dashboard")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, "library/borrow_book.html", {
        "school": school, "books": books, "students": students
    })


@admin_required
def return_book(request, pk):
    school = request.user.school
    record = get_object_or_404(BorrowRecord, id=pk, school=school)
    if request.method == "POST":
        record.returned_at = timezone.now()
        record.status = "returned"
        record.save()
        record.book.available_copies += 1
        record.book.save()
        messages.success(request, f"'{record.book.title}' returned successfully!")
        return redirect("library_dashboard")
    return render(request, "library/return_book.html", {"record": record, "school": school})


@admin_required
def manage_returns(request):
    school = request.user.school
    active_borrows = BorrowRecord.objects.filter(
        school=school, status__in=["borrowed", "overdue"]
    ).select_related("student", "book").order_by("due_at")
    return render(request, "library/manage_returns.html", {
        "school": school, "active_borrows": active_borrows
    })


@admin_required
def overdue_list(request):
    school = request.user.school
    # Refresh statuses first
    for r in BorrowRecord.objects.filter(school=school, status='borrowed'):
        if timezone.now() > r.due_at:
            r.save()
    overdue_records = BorrowRecord.objects.filter(
        school=school, status="overdue"
    ).select_related("student", "book").order_by("due_at")
    return render(request, "library/overdue_list.html", {
        "school": school, "overdue_records": overdue_records
    })


@admin_required
def add_book(request):
    school = request.user.school
    if request.method == "POST":
        try:
            copies = int(request.POST.get("copies", 1))
            Book.objects.create(
                school=school,
                title=request.POST.get("title", "").strip(),
                author=request.POST.get("author", "").strip(),
                isbn=request.POST.get("isbn", "").strip(),
                category=request.POST.get("category", "textbook").strip(),
                shelf_location=request.POST.get("location", "").strip(),
                total_copies=copies,
                available_copies=copies,
            )
            messages.success(request, "Book added successfully!")
            return redirect("book_list")
        except Exception as e:
            messages.error(request, f"Error adding book: {e}")
    return render(request, "library/add_book.html", {"school": school})
