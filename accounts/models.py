import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_platform_admin", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

    def create_staff_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.is_staff = True
        user.is_active = True

        if role:
            role = role.lower()
            user.school_role = role

            if role in ["principal", "bursar", "dean", "secretary", "admin"]:
                user.is_school_admin = True

            if role == "teacher":
                user.is_teacher = True
            elif role == "parent":
                user.is_parent = True
            elif role == "student":
                user.is_student = True

        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    profile_photo = models.ImageField(upload_to="users/photos/", null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        blank=True,
    )

    national_id = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    # role flags
    is_platform_admin = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("principal", "Principal"),
        ("bursar", "Bursar"),
        ("dean", "Dean of Studies"),
        ("secretary", "Secretary"),
        ("admin", "General Admin"),
    ]

    school_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="admin",
        blank=True,
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def primary_role(self):
        if self.is_platform_admin:
            return "Platform Admin"

        if self.is_school_admin:
            role_map = {
                "bursar": "Bursar",
                "principal": "Principal",
                "dean": "Dean of Studies",
                "secretary": "Secretary",
                "super_admin": "Super Admin",
            }
            return role_map.get(self.school_role, "School Admin")

        if self.is_teacher:
            return "Teacher"
        if self.is_parent:
            return "Parent"
        if self.is_student:
            return "Student"

        return "Unknown"

    def get_dashboard_url(self):
        if self.is_platform_admin:
            return "/school-admin/dashboard/super/"

        if self.is_school_admin:
            role = self.school_role or "admin"

            if role == "bursar":
                return "/school-admin/dashboard/bursar/"
            if role == "principal":
                return "/school-admin/dashboard/principal/"
            if role == "dean":
                return "/school-admin/dashboard/dean/"
            if role == "secretary":
                return "/school-admin/dashboard/secretary/"
            if role == "super_admin":
                return "/school-admin/dashboard/super/"

            return "/school-admin/dashboard/"

        if self.is_teacher:
            return "/school-admin/dashboard/teacher/"
        if self.is_parent:
            return "/portal/parent/"
        if self.is_student:
            return "/portal/student/"

        return "/"