

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_on_campus.settings")
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()

    username = "admin"
    password = "admin123"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            password=password
        )
        print("Admin created")
    else:
        print("Admin already exists")


if __name__ == "__main__":
    create_admin()