from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, StudentProfile, EmployerProfile

# Student Registration Form
class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Employer Registration Form
class EmployerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']