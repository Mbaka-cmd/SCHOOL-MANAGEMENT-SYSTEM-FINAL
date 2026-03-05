from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            if user.is_student:
                try:
                    student = user.student_profile
                    parents = student.parents.filter(email__isnull=False).exclude(email="")
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
                                f"Regards,\nChuka Girls Secondary School\nTel: 064-630001 / 0115388019"
                            ),
                            from_email='mercykathomi428@gmail.com',
                            recipient_list=[parent.email],
                            fail_silently=False,
                        )
                except Exception as e:
                    print(f"Email error: {e}")
            return redirect(user.get_dashboard_url())
        else:
            messages.error(request, "Invalid email or password")
    return render(request, "accounts/login.html")


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

        student = Student.objects.filter(admission_number=admission_number, is_active=True).first()

        if not student:
            messages.error(request, "No student found with that admission number.")
            return render(request, "accounts/parent_register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. Please login instead.")
            return render(request, "accounts/parent_register.html")

        try:
            user = User.objects.create_user(
                email=email, password=password, first_name=first_name,
                last_name=last_name, school=student.school, is_parent=True, phone=phone,
            )
            parent, created = ParentGuardian.objects.get_or_create(
                email=email,
                defaults={
                    "school": student.school, "first_name": first_name,
                    "last_name": last_name, "phone_primary": phone,
                    "relationship": relationship, "user": user,
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
                        f"Dear {first_name},\n\nYour parent portal account has been created!\n\n"
                        f"Linked to: {student.get_full_name()} (Adm: {student.admission_number})\n\n"
                        f"Login at: http://127.0.0.1:8000/accounts/login/\n\n"
                        f"Regards,\nChuka Girls Secondary School"
                    ),
                    from_email='mercykathomi428@gmail.com',
                    recipient_list=[email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Welcome email error: {e}")
            messages.success(request, f"Account created! Linked to {student.get_full_name()}. Please login.")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")

    return render(request, "accounts/parent_register.html")
