from django.core.management.base import BaseCommand
from django.db import transaction
from students.models import Student, ParentGuardian
from exams.models import Exam, ExamResult, ReportCard
from fees.models import FeeInvoice, Payment
from attendance.models import AttendanceSession, AttendanceRecord
from communications.models import Message, MessageRecipient, ParentComment
from notices.models import Notice
from library.models import Book, BorrowRecord
from timetable.models import TimetableSlot
from accounts.models import User

class Command(BaseCommand):
    help = 'Clear all school data (students, exams, fees, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will DELETE ALL school data! Use --confirm to proceed.'
                )
            )
            return

        with transaction.atomic():
            # Clear in order to avoid foreign key issues
            self.stdout.write('Clearing attendance records...')
            AttendanceRecord.objects.all().delete()
            AttendanceSession.objects.all().delete()

            self.stdout.write('Clearing exam results and report cards...')
            ExamResult.objects.all().delete()
            ReportCard.objects.all().delete()
            Exam.objects.all().delete()

            self.stdout.write('Clearing fees...')
            Payment.objects.all().delete()
            FeeInvoice.objects.all().delete()

            self.stdout.write('Clearing communications...')
            MessageRecipient.objects.all().delete()
            Message.objects.all().delete()
            ParentComment.objects.all().delete()

            self.stdout.write('Clearing notices...')
            Notice.objects.all().delete()

            self.stdout.write('Clearing library...')
            BorrowRecord.objects.all().delete()
            Book.objects.all().delete()

            self.stdout.write('Clearing timetable...')
            TimetableSlot.objects.all().delete()

            self.stdout.write('Clearing students and parents...')
            # Clear parent relationships first
            ParentGuardian.objects.all().delete()
            Student.objects.all().delete()

            # Clear non-superuser accounts (keep admin)
            User.objects.filter(is_superuser=False).delete()

            self.stdout.write(
                self.style.SUCCESS('All school data cleared successfully!')
            )