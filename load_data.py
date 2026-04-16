import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_on_campus.settings")
django.setup()

from django.core.management import call_command

print("Loading data into PostgreSQL...")

call_command("loaddata", "data.json")

print("Done!")