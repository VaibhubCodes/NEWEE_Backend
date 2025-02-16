from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from questions.models import Subject

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not password:
            raise ValueError("Superuser must have a password.")

        return self.create_user(email=email, username=username, password=password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('SuperAdmin', 'SuperAdmin'),
        ('SupportController', 'Support Controller'),
        ('Controller', 'Controller'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    ]

    CONTROLLER_TYPE_CHOICES = [
        ("finance", "Financial Controller"),
        ("educator", "Educator Controller"),
        ("tech", "Tech Controller"),
        ("quiz", "Quiz Controller"),
        ("product", "Product Controller"),
        ("master", "Master Controller"),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)  # ✅ Allows null values
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    controller_type = models.CharField(
        max_length=20, choices=CONTROLLER_TYPE_CHOICES, blank=True, null=True,
        help_text="Only for Controllers: Defines specialization (Finance, Educator, etc.)"
    )

    pan_number = models.CharField(max_length=10, blank=True, null=True)
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']  # ✅ Fix: username must be required

    def __str__(self):
        return self.email

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher_profile')
    school_id = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True)

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
    class_name = models.CharField(max_length=4, choices=CLASS_CHOICES, default="6th")
    profile_picture = models.ImageField(upload_to='student_profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.name
