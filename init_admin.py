from django.contrib.auth import get_user_model
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_on_campus.settings")
django.setup()

def create_admin():
    User = get_user_model()

    if not User.objects.filter(username="admin").exists():

        user = User.objects.create_superuser(
            username="admin",
            email="admin@gmail.com",
            password="admin123"
        )

        # force role AFTER creation (safer)
        user.role = "admin"
        user.save()

        print("Admin created")
    else:
        print("Admin already exists")

if __name__ == "__main__":
    create_admin()