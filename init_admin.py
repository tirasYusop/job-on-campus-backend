import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_on_campus.settings")
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="admin123"
        )
        print("✅ Admin created successfully")
    else:
        print("Admin already exists")

if __name__ == "__main__":
    create_admin()