from django.core.management.base import BaseCommand
from accounts.models import User
import os


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self._create_admin()
        self._create_school()
        self._create_academic_year()
        self._create_streams()
        self._create_kcse()

    def _create_admin(self):
        email = os.environ.get("ADMIN_EMAIL", "official.mercymbaka@gmail.com")
        password = os.environ.get("ADMIN_PASSWORD", "MercyAdmin2026!")
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name="Mercy",
                last_name="Mbaka",
                is_platform_admin=True,
                school_role="super_admin",
            )
            self.stdout.write("Superuser created!")
        else:
            self.stdout.write("Admin already exists.")

    def _create_school(self):
        from schools.models import School
        if not School.objects.exists():
            school = School.objects.create(
                name="St. Bakhita Chuka Girls High School",
                slug="chuka-girls",
                motto="Today's Effort is Tomorrow's Success",
                address="Kiagondu Forest Road, Karingari",
                county="Tharaka-Nithi",
                town="Chuka",
                phone="0115388019",
                email="chukagirls@gmail.com",
                po_box="3-60400",
                knec_code="19308304",
                school_type="boarding",
                gender_type="girls",
                category="extra_county",
                is_active=True,
            )
            self.stdout.write(f"School created: {school.name}")

            # Link admin to school
            from accounts.models import User
            admin = User.objects.filter(is_platform_admin=True).first()
            if admin:
                admin.school = school
                admin.is_school_admin = True
                admin.save()
                self.stdout.write("Admin linked to school.")
        else:
            self.stdout.write("School already exists.")

    def _create_academic_year(self):
        from schools.models import School, AcademicYear, Term
        school = School.objects.first()
        if not school:
            return
        year, created = AcademicYear.objects.get_or_create(
            school=school,
            year=2026,
            defaults={"is_current": True, "start_date": "2026-01-01", "end_date": "2026-11-30"}
        )
        if created:
            self.stdout.write("Academic year 2026 created.")
        for i, name in enumerate(["Term 1", "Term 2", "Term 3"], 1):
            Term.objects.get_or_create(
                academic_year=year,
                number=i,
                defaults={"name": name, "is_current": i == 1}
            )
        self.stdout.write("Terms ready.")

    def _create_streams(self):
        from schools.models import School
        from academics.models import ClassLevel, Stream
        school = School.objects.first()
        if not school:
            return
        if Stream.objects.filter(school=school).exists():
            self.stdout.write("Streams already exist.")
            return
        class_data = [
            ("Form 1", 1), ("Form 2", 2), ("Form 3", 3), ("Form 4", 4)
        ]
        stream_names = ["East", "West", "North", "South"]
        for class_name, order in class_data:
            level, _ = ClassLevel.objects.get_or_create(
                school=school,
                name=class_name,
                defaults={"level_order": order}
            )
            for stream_name in stream_names:
                Stream.objects.get_or_create(
                    school=school,
                    class_level=level,
                    name=stream_name,
                    defaults={"full_name": f"{class_name} {stream_name}"}
                )
        self.stdout.write("16 streams created.")

    def _create_kcse(self):
        from schools.models import School
        from website.models import KCSEResult
        school = School.objects.first()
        if not school:
            return
        if KCSEResult.objects.filter(school=school).exists():
            self.stdout.write("KCSE results already exist.")
            return
        KCSEResult.objects.create(
            school=school,
            year=2024,
            candidates_sat=133,
            mean_grade="B-",
            mean_points=7.20,
            university_qualifiers=85,
            count_a_plain=0,
            count_a_minus=1,
            count_b_plus=8,
            count_b_plain=26,
            count_b_minus=47,
            count_c_plus=31,
            count_c_plain=16,
            count_c_minus=2,
            count_d_plus=1,
            is_published=True,
            summary="In 2024 KCSE, 133 candidates sat the exam with 85 qualifying for university admission. The school posted a mean grade of B-.",
        )
        self.stdout.write("KCSE 2024 results seeded.")

