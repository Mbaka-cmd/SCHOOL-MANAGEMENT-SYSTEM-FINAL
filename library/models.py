from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from schools.models import School
from students.models import Student
import uuid


class Book(models.Model):
    CATEGORY_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('textbook', 'Textbook'),
        ('reference', 'Reference'),
        ('magazine', 'Magazine'),
        ('other', 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='textbook')
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    shelf_location = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['title']


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='borrow_records')
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='borrowed')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.due_at:
            self.due_at = self.borrowed_at + timedelta(hours=72)
        self.update_status()
        super().save(*args, **kwargs)

    def update_status(self):
        if self.returned_at:
            self.status = 'returned'
        elif timezone.now() > self.due_at:
            self.status = 'overdue'
            overdue_days = (timezone.now() - self.due_at).days
            self.fine_amount = overdue_days * 50
        else:
            self.status = 'borrowed'

    @property
    def is_overdue(self):
        return not self.returned_at and timezone.now() > self.due_at

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now() - self.due_at).days
        return 0

    @property
    def calculate_fine(self):
        days = self.days_overdue
        if days <= 0:
            return Decimal('0.00')
        return days * Decimal('50.00')

    def __str__(self):
        return f"{self.student} borrowed {self.book.title}"

    class Meta:
        ordering = ['-borrowed_at']
