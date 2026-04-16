from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    verified = models.BooleanField(default=False)

    def clean(self):
        super().clean()

        if self.role == "student":
            if not self.email:
                raise ValidationError("Student must have email")

            if not self.email.endswith("@iluv.ums.edu.my"):
                raise ValidationError("Invalid student email domain")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nama_penuh = models.CharField(max_length=100)
    no_matrik = models.CharField(max_length=20)
    no_telefon = models.CharField(max_length=15)
    fakulti = models.CharField(max_length=50)
    kolej = models.CharField(max_length=50)

    def __str__(self):
        return self.nama_penuh


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)


    def __str__(self):
        return self.company_name


class Job(models.Model):
    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    job_type = models.CharField(max_length=50)
    business_type = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    work_time = models.CharField(max_length=50)
    salary_estimate = models.CharField(max_length=50)
    num_workers = models.IntegerField()
    criteria = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.job_type} at {self.location}"


class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('rejected', 'Rejected')
        ),
        default='pending'
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    complaint = models.TextField(null=True, blank=True)

    complaint_status = models.CharField(
        max_length=20,
        default="none"
    )
    feedback = models.TextField(null=True, blank=True)
    feedback_status = models.CharField(max_length=20, default="not_submitted")

    class Meta:
        unique_together = ('job', 'student')
