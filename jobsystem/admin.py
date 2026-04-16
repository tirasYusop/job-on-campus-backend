from django.contrib import admin
from .models import User, StudentProfile, EmployerProfile, Job, JobApplication

admin.site.register(User)
admin.site.register(StudentProfile)
admin.site.register(EmployerProfile)
admin.site.register(Job)
admin.site.register(JobApplication)