from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Book, BorrowRecord
from students.models import Student


@login_required
def library_dashboard(request):
    school = request.user.school
    books = Book.objects.filter(school=school)
    active_borrows = BorrowRecord.objects.filter(school=school, status__in=['borrowed', 'overdue'])
    overdue = BorrowRecord.objects.filter(school=school, status='overdue')
    # Update overdue status
    for record in BorrowRecord.objects.filter(school=school, status='borrowed'):
        if timezone.now() > record.due_at:
            record.status = 'overdue'
            record.fine_amount = (timezone.now() - record.due_at).days * 50
            record.save()
    context = {
        'books': books,
        'total_books': books.count(),
        'active_borrows': active_borrows.count(),
        'overdue_count': overdue.count(),
        'total_fines': sum(r.fine_amount for r in overdue),
        'recent_borrows': BorrowRecord.objects.filter(school=school).select_related('book', 'student')[:10],
    }
    return render(request, 'library/dashboard.html', context)


@login_required
def book_list(request):
    school = request.user.school
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    books = Book.objects.filter(school=school)
    if search:
        books = books.filter(title__icontains=search) | books.filter(author__icontains=search)
    if category:
        books = books.filter(category=category)
    return render(request, 'library/book_list.html', {'books': books, 'search': search, 'category': category})


@login_required
def add_book(request):
    if request.method == 'POST':
        school = request.user.school
        Book.objects.create(
            school=school,
            title=request.POST['title'],
            author=request.POST['author'],
            isbn=request.POST.get('isbn', ''),
            category=request.POST.get('category', 'textbook'),
            total_copies=int(request.POST.get('total_copies', 1)),
            available_copies=int(request.POST.get('total_copies', 1)),
            shelf_location=request.POST.get('shelf_location', ''),
        )
        messages.success(request, 'Book added successfully!')
        return redirect('book_list')
    return render(request, 'library/add_book.html')


@login_required
def borrow_book(request):
    school = request.user.school
    if request.method == 'POST':
        book_id = request.POST['book_id']
        student_id = request.POST['student_id']
        book = get_object_or_404(Book, id=book_id, school=school)
        student = get_object_or_404(Student, id=student_id, school=school)
        if book.available_copies < 1:
            messages.error(request, 'No copies available!')
            return redirect('borrow_book')
        existing = BorrowRecord.objects.filter(book=book, student=student, status__in=['borrowed', 'overdue']).first()
        if existing:
            messages.error(request, f'{student.first_name} already has this book!')
            return redirect('borrow_book')
        now = timezone.now()
        BorrowRecord.objects.create(
            school=school,
            book=book,
            student=student,
            borrowed_at=now,
            due_at=now + timedelta(hours=72),
        )
        book.available_copies -= 1
        book.save()
        messages.success(request, f'Book borrowed! Due in 72 hours.')
        return redirect('library_dashboard')
    books = Book.objects.filter(school=school, available_copies__gt=0)
    students = Student.objects.filter(school=school, is_active=True)
    return render(request, 'library/borrow_book.html', {'books': books, 'students': students})


@login_required
def return_book(request, record_id):
    school = request.user.school
    record = get_object_or_404(BorrowRecord, id=record_id, school=school)
    if request.method == 'POST':
        record.returned_at = timezone.now()
        record.status = 'returned'
        if record.returned_at > record.due_at:
            overdue_days = (record.returned_at - record.due_at).days
            record.fine_amount = overdue_days * 50
        record.save()
        record.book.available_copies += 1
        record.book.save()
        if record.fine_amount > 0:
            messages.warning(request, f'Book returned! Fine: KES {record.fine_amount}')
        else:
            messages.success(request, 'Book returned on time!')
        return redirect('library_dashboard')
    return render(request, 'library/return_book.html', {'record': record})


@login_required
def manage_returns(request):
    school = request.user.school
    if request.method == 'POST':
        record_ids = request.POST.getlist('record_ids')
        return_time = timezone.now()
        returned_count = 0
        total_fine = 0
        for record_id in record_ids:
            try:
                record = BorrowRecord.objects.get(id=record_id, school=school, status__in=['borrowed', 'overdue'])
                record.returned_at = return_time
                record.status = 'returned'
                if return_time > record.due_at:
                    overdue_days = (return_time - record.due_at).days
                    record.fine_amount = overdue_days * 50
                    total_fine += record.fine_amount
                record.save()
                record.book.available_copies += 1
                record.book.save()
                returned_count += 1
            except BorrowRecord.DoesNotExist:
                continue
        if returned_count > 0:
            if total_fine > 0:
                messages.warning(request, f'{returned_count} book(s) returned! Total fine: KES {total_fine}')
            else:
                messages.success(request, f'{returned_count} book(s) returned successfully!')
        else:
            messages.info(request, 'No books were selected for return.')
        return redirect('manage_returns')
    
    # Update overdue status
    for record in BorrowRecord.objects.filter(school=school, status='borrowed'):
        if timezone.now() > record.due_at:
            record.status = 'overdue'
            record.fine_amount = (timezone.now() - record.due_at).days * 50
            record.save()
    
    records = BorrowRecord.objects.filter(school=school, status__in=['borrowed', 'overdue']).select_related('book', 'student').order_by('due_at')
    return render(request, 'library/manage_returns.html', {'records': records})


@login_required
def student_borrow_history(request, student_id):
    school = request.user.school
    student = get_object_or_404(Student, id=student_id, school=school)
    records = BorrowRecord.objects.filter(school=school, student=student).select_related('book')
    return render(request, 'library/student_history.html', {'student': student, 'records': records})


@login_required
def overdue_list(request):
    school = request.user.school
    for record in BorrowRecord.objects.filter(school=school, status='borrowed'):
        if timezone.now() > record.due_at:
            record.status = 'overdue'
            record.fine_amount = (timezone.now() - record.due_at).days * 50
            record.save()
    records = BorrowRecord.objects.filter(school=school, status='overdue').select_related('book', 'student')
    return render(request, 'library/overdue_list.html', {'records': records})