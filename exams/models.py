from django.db import models

# Create your models here.
# ── EXAMS models.py ──────────────────────────────────────────────
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

GRADE_CHOICES = [
    ("A", "A (80-100)"), ("A-", "A- (75-79)"), ("B+", "B+ (70-74)"),
    ("B", "B (65-69)"), ("B-", "B- (60-64)"), ("C+", "C+ (55-59)"),
    ("C", "C (50-54)"), ("C-", "C- (45-49)"), ("D+", "D+ (40-44)"),
    ("D", "D (35-39)"), ("D-", "D- (30-34)"), ("E", "E (0-29)"),
    ("X", "X - Absent"), ("Y", "Y - Cancelled"),
]

GRADE_POINTS = {
    "A": 12, "A-": 11, "B+": 10, "B": 9, "B-": 8,
    "C+": 7, "C": 6, "C-": 5, "D+": 4, "D": 3, "D-": 2, "E": 1,
    "X": 0, "Y": 0,
}

def score_to_grade(score):
    if score >= 80: return "A"
    if score >= 75: return "A-"
    if score >= 70: return "B+"
    if score >= 65: return "B"
    if score >= 60: return "B-"
    if score >= 55: return "C+"
    if score >= 50: return "C"
    if score >= 45: return "C-"
    if score >= 40: return "D+"
    if score >= 35: return "D"
    if score >= 30: return "D-"
    return "E"


class Exam(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="exams")
    academic_year = models.ForeignKey("schools.AcademicYear", on_delete=models.CASCADE, related_name="exams")
    term = models.ForeignKey("schools.Term", on_delete=models.CASCADE, related_name="exams", null=True, blank=True)
    name = models.CharField(max_length=200)
    exam_type = models.CharField(
        max_length=20,
        choices=[
            ("cat1", "CAT 1"), ("cat2", "CAT 2"), ("midterm", "Mid-Term"),
            ("endterm", "End of Term"), ("mock", "Mock KCSE"),
            ("kcse", "KCSE (National Exam)"), ("other", "Other"),
        ],
        default="endterm",
    )
    streams = models.ManyToManyField("academics.Stream", related_name="exams", blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    exam_paper = models.FileField(upload_to="exam_papers/", null=True, blank=True, help_text="Upload the exam paper (PDF, DOC, etc.)")
    is_published = models.BooleanField(default=False)
    is_kcse = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-academic_year__year", "-start_date"]

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class ExamResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="exam_results")
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, related_name="exam_results")
    raw_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    points = models.PositiveSmallIntegerField(null=True, blank=True)
    is_absent = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    teacher_remarks = models.CharField(max_length=300, blank=True)
    stream_position = models.PositiveSmallIntegerField(null=True, blank=True)
    school_position = models.PositiveSmallIntegerField(null=True, blank=True)
    entered_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="entered_results")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("exam", "student", "subject")

    def __str__(self):
        return f"{self.student} — {self.subject} — {self.grade or self.raw_score}"

    def save(self, *args, **kwargs):
        if self.raw_score is not None and not self.grade:
            self.grade = score_to_grade(float(self.raw_score))
        if self.grade and not self.points:
            self.points = GRADE_POINTS.get(self.grade, 0)
        super().save(*args, **kwargs)


class ReportCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="report_cards")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="report_cards")
    stream = models.ForeignKey("academics.Stream", on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    total_points = models.PositiveSmallIntegerField(null=True, blank=True)
    mean_grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    mean_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    subjects_sat = models.PositiveSmallIntegerField(default=0)
    stream_position = models.PositiveSmallIntegerField(null=True, blank=True)
    stream_size = models.PositiveSmallIntegerField(null=True, blank=True)
    school_position = models.PositiveSmallIntegerField(null=True, blank=True)
    school_size = models.PositiveSmallIntegerField(null=True, blank=True)
    class_teacher_remarks = models.TextField(blank=True)
    principal_remarks = models.TextField(blank=True)
    fee_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pdf_file = models.FileField(upload_to="report_cards/", null=True, blank=True)
    pdf_generated_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "exam")

    def __str__(self):
        return f"Report: {self.student} — {self.exam.name}"