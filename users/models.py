from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from questions.models import Subject

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        username = self._generate_username(email)
        extra_fields.setdefault('username', username)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def _generate_username(self, email):
        base_username = email.split('@')[0]
        username = base_username
        count = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}{count}"
            count += 1
        return username

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('SuperAdmin', 'SuperAdmin'),
        ('Controller', 'Controller'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    pan_number = models.CharField(max_length=10, blank=True, null=True, help_text="Permanent Account Number")
    upi_id = models.CharField(max_length=50, blank=True, null=True, help_text="UPI ID for transactions")
    aadhar_number = models.CharField(max_length=12, blank=True, null=True, help_text="Aadhar Number")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Latitude coordinate")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Longitude coordinate")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    school_id = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True, help_text="Subjects taught by the teacher")
    def __str__(self):
        return self.user.name

class Student(models.Model):
    CLASS_CHOICES = [
        ("6th", "6th"),
        ("7th", "7th"),
        ("8th", "8th"),
        ("9th", "9th"),
        ("10th", "10th"),
        ("11th", "11th"),
        ("12th", "12th"),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    school_id = models.CharField(max_length=100)
    address = models.TextField()
    date_of_birth = models.DateField()
    location = models.CharField(max_length=255)
    class_name = models.CharField(max_length=4, choices=CLASS_CHOICES, default="6th")  # Restricted to valid options
    profile_picture = models.ImageField(upload_to='student_profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.name
