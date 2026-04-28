from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    active_tab = "student"
    staff_code = ""
    staff_role = ""

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "").strip()
        staff_code = request.POST.get("staff_code", "").strip()
        staff_role = request.POST.get("staff_role", "").strip()

        if staff_role or staff_code:
            active_tab = "staff"

        if active_tab == "staff" and not staff_code:
            messages.error(request, "Please enter your staff portal access code.")
            return render(request, "accounts/login.html", {
                "active_tab": active_tab,
                "staff_code": staff_code,
                "staff_role": staff_role,
            })

        if active_tab == "staff" and not staff_role:
            messages.error(request, "Please select your staff role.")
            return render(request, "accounts/login.html", {
                "active_tab": active_tab,
                "staff_code": staff_code,
                "staff_role": staff_role,
            })

        if staff_code and staff_code != "BHAKITA2026":
            messages.error(request, "Invalid staff portal code. Please use the correct code.")
            return render(request, "accounts/login.html", {
                "active_tab": active_tab,
                "staff_code": staff_code,
                "staff_role": staff_role,
            })

        user = None

        # ── Try email login first ──
        user = authenticate(request, email=identifier, password=password)

        # ── Try admission number login (students) ──
        if not user:
            from students.models import Student
            student = Student.objects.filter(
                admission_number__iexact=identifier, is_active=True
            ).select_related('user').first()

            if student and student.user:
                user = authenticate(request, email=student.user.email, password=password)

                if not user:
                    default_passwords = [
                        student.admission_number,
                        f"{student.first_name}{student.admission_number}",
                        f"{student.first_name}_{student.admission_number}",
                    ]
                    entered = password.strip()

                    if any(
                        entered.lower() == dp.lower()
                        for dp in default_passwords
                    ) and any(
                        student.user.check_password(dp)
                        for dp in default_passwords
                    ):
                        user = student.user

        # ── Try firstname_admissionnumber format e.g. "Adalyn_CGS02/2026" ──
        if not user and "_" in identifier:
            parts = identifier.split("_", 1)
            if len(parts) == 2:
                first_name, adm_number = parts
                from students.models import Student
                student = Student.objects.filter(
                    admission_number__iexact=adm_number.strip(),
                    first_name__iexact=first_name.strip(),
                    is_active=True
                ).select_related('user').first()
                if student and student.user:
                    user = authenticate(request, email=student.user.email, password=password)

        # ── Role validation helper (defined inside so it's in scope) ──
        def staff_role_matches_account(u, selected_role):
            if selected_role == "teacher":
                return getattr(u, 'is_teacher', False)
            if selected_role == "admin":
                return getattr(u, 'is_school_admin', False)
            if selected_role in ("principal", "bursar", "dean", "secretary"):
                return (
                    getattr(u, 'is_school_admin', False)
                    and getattr(u, 'school_role', '') == selected_role
                )
            return False

        if user:
            if active_tab == "staff" and not staff_role_matches_account(user, staff_role):
                messages.error(
                    request,
                    "Selected role does not match this account. "
                    "Please choose the role assigned to your email."
                )
                return render(request, "accounts/login.html", {
                    "active_tab": active_tab,
                    "staff_code": staff_code,
                    "staff_role": staff_role,
                })

            login(request, user)

            # ── Notify parent when student logs in ──
            if user.is_student:
                try:
                    student = user.student_profile
                    parents = student.parents.filter(
                        email__isnull=False
                    ).exclude(email="")
                    for parent in parents:
                        send_mail(
                            subject=f"Portal Login Alert - {student.get_full_name()}",
                            message=(
                                f"Dear {parent.first_name},\n\n"
                                f"Your child {student.get_full_name()} "
                                f"(Adm: {student.admission_number}) has just logged into "
                                f"the Chuka Girls School Portal.\n\n"
                                f"Login Time: {timezone.now().strftime('%d %b %Y at %I:%M %p')}\n\n"
                                f"If this was not your child, please contact the school immediately.\n\n"
                                f"Regards,\nChuka Girls Secondary School\n"
                                f"Tel: 064-630001 / 0115388019"
                            ),
                            from_email='mercykathomi428@gmail.com',
                            recipient_list=[parent.email],
                            fail_silently=True,
                        )
                except Exception as e:
                    print(f"Email error: {e}")

            return redirect(user.get_dashboard_url())

        else:
            messages.error(
                request,
                "Invalid credentials. Try your email, admission number, "
                "or first name + admission number."
            )

    return render(request, "accounts/login.html", {
        "active_tab": active_tab,
        "staff_code": staff_code,
        "staff_role": staff_role,
    })


def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    return redirect(request.user.get_dashboard_url())


def parent_register(request):
    from students.models import Student, ParentGuardian
    from accounts.models import User

    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    if request.method == "POST":
        admission_number = request.POST.get("admission_number", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "").strip()
        relationship = request.POST.get("relationship", "guardian")

        student = Student.objects.filter(
            admission_number=admission_number, is_active=True
        ).first()

        if not student:
            messages.error(request, "No student found with that admission number.")
            return render(request, "accounts/parent_register.html")

        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                "An account with this email already exists. Please login instead."
            )
            return render(request, "accounts/parent_register.html")

        try:
            user = User.objects.create_user(
                email=email, password=password, first_name=first_name,
                last_name=last_name, school=student.school,
                is_parent=True, phone=phone,
            )
            parent, created = ParentGuardian.objects.get_or_create(
                email=email,
                defaults={
                    "school": student.school,
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone_primary": phone,
                    "relationship": relationship,
                    "user": user,
                }
            )
            if not created:
                parent.user = user
                parent.save()
            parent.students.add(student)

            try:
                send_mail(
                    subject="Welcome to Chuka Girls School Parent Portal",
                    message=(
                        f"Dear {first_name},\n\n"
                        f"Your parent portal account has been created!\n\n"
                        f"Linked to: {student.get_full_name()} "
                        f"(Adm: {student.admission_number})\n\n"
                        f"Login at: https://school-management-system-final.onrender.com"
                        f"/accounts/login/\n\n"
                        f"Regards,\nChuka Girls Secondary School"
                    ),
                    from_email='mercykathomi428@gmail.com',
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Welcome email error: {e}")

            messages.success(
                request,
                f"Account created! Linked to {student.get_full_name()}. Please login."
            )
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Error creating account: {e}")

    return render(request, "accounts/parent_register.html")