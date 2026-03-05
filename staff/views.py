from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User
from academics.models import Subject, Stream
from schools.views import admin_required


@admin_required
def staff_list(request):
    school = request.user.school
    staff = User.objects.filter(school=school, is_teacher=True).order_by("last_name")
    search = request.GET.get("search", "")
    if search:
        staff = User.objects.filter(school=school, is_teacher=True).filter(
            first_name__icontains=search
        ) | User.objects.filter(school=school, is_teacher=True).filter(
            last_name__icontains=search
        ) | User.objects.filter(school=school, is_teacher=True).filter(
            email__icontains=search
        )
    context = {"staff": staff, "search": search, "total": staff.count()}
    return render(request, "staff/staff_list.html", context)


@admin_required
def staff_add(request):
    school = request.user.school
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone", "")
        password = request.POST.get("password")
        try:
            if User.objects.filter(email=email).exists():
                messages.error(request, f"Email {email} already exists!")
                return redirect("staff_add")
            teacher = User.objects.create_user(
                email=email, password=password,
                first_name=first_name, last_name=last_name,
                school=school, is_teacher=True, phone=phone,
            )
            messages.success(request, f"Teacher {teacher.get_full_name()} added successfully!")
            return redirect("staff_list")
        except Exception as e:
            messages.error(request, f"Error adding teacher: {e}")
    subjects = Subject.objects.filter(school=school)
    context = {"subjects": subjects}
    return render(request, "staff/staff_add.html", context)


@admin_required
def staff_detail(request, pk):
    school = request.user.school
    teacher = get_object_or_404(User, id=pk, school=school, is_teacher=True)
    assignments = teacher.teaching_assignments.filter(
        academic_year__school=school
    ).select_related("stream", "subject", "academic_year")
    context = {"teacher": teacher, "assignments": assignments}
    return render(request, "staff/staff_detail.html", context)


@admin_required
def staff_edit(request, pk):
    school = request.user.school
    teacher = get_object_or_404(User, id=pk, school=school, is_teacher=True)
    if request.method == "POST":
        teacher.first_name = request.POST.get("first_name")
        teacher.last_name = request.POST.get("last_name")
        teacher.phone = request.POST.get("phone", "")
        teacher.is_active = "is_active" in request.POST
        teacher.save()
        messages.success(request, f"Teacher {teacher.get_full_name()} updated!")
        return redirect("staff_detail", pk=teacher.id)
    context = {"teacher": teacher}
    return render(request, "staff/staff_edit.html", context)