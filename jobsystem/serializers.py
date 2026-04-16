from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "job_type",
            "business_type",
            "phone",
            "location",
            "start_date",
            "end_date",
            "work_time",
            "salary_estimate",
            "num_workers",
            "criteria",
        ]