# Run this with: python manage.py shell < create_student_accounts.py
from students.models import Student
from accounts.models import User

students = Student.objects.filter(is_active=True)
created = 0
skipped = 0

for s in students:
    if s.user:
        print(f"SKIP (has account): {s.get_full_name()} - {s.admission_number}")
        skipped += 1
        continue

    # Email uses admission number — safe internal email, never sent externally
    safe_adm = s.admission_number.replace("/", "-").replace(" ", "").lower()
    email = f"{safe_adm}@chukagirls.ac.ke"

    if User.objects.filter(email=email).exists():
        # Link existing user
        u = User.objects.get(email=email)
        s.user = u
        s.save()
        print(f"LINKED: {s.get_full_name()} -> {email}")
    else:
        u = User.objects.create_user(
            email=email,
            password=s.admission_number,  # password = admission number exactly as stored
            first_name=s.first_name,
            last_name=s.last_name,
            school=s.school,
            is_student=True,
        )
        s.user = u
        s.save()
        created += 1
        print(f"CREATED: {s.get_full_name()} | login: {s.admission_number} | pw: {s.admission_number}")

print(f"\nDone! Created: {created} | Skipped: {skipped}")
