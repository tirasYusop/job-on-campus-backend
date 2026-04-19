import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from .models import JobApplication, User, StudentProfile, EmployerProfile, Job 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Count,F, Value
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Count, Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import StudentProfile

# STUDENT REGISTER
@csrf_exempt
def student_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)

        required_fields = [
            "username", "password",
            "email",
            "nama_penuh", "no_matrik",
            "no_telefon", "fakulti", "kolej"
        ]

        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return JsonResponse({"error": f"Missing fields: {missing}"}, status=400)

        username = data["username"]
        email = data["email"]
        if not email.endswith("@iluv.ums.edu.my"):
            return JsonResponse({
                "error": "Email must be a valid UMS student email (@iluv.ums.edu.my)"
            }, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Student ID already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)
        user = User.objects.create_user(
            username=username,
            password=data["password"],
            email=email,
            role="student"
        )

        # create profile
        StudentProfile.objects.create(
            user=user,
            nama_penuh=data["nama_penuh"],
            no_matrik=data["no_matrik"],
            no_telefon=data["no_telefon"],
            fakulti=data["fakulti"],
            kolej=data["kolej"]
        )

        # auto login
        # ✅ ADD JWT TOKEN
        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            "message": "Student registered & logged in",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employer_profile(request):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        profile = EmployerProfile.objects.get(user=request.user)

        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email,
            "full_name": profile.full_name,
            "company_name": profile.company_name,
            "phone_number": profile.phone_number,
            "verified": request.user.verified,
        })

    except EmployerProfile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)

# EMPLOYER REGISTER
@csrf_exempt
def employer_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)

        required_fields = [
            "username",
            "password",
            "email",
            "full_name",
            "company_name",
            "phone_number"
        ]

        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return JsonResponse({"error": f"Missing fields: {missing}"}, status=400)

        username = data["username"]
        email = data["email"]

        # ❌ duplicate username
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        # ❌ duplicate email
        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already registered"}, status=400)

        # (optional) email validation for employer (remove if not needed)
        # if not email.endswith("@gmail.com"):
        #     return JsonResponse({"error": "Invalid email"}, status=400)

        user = User.objects.create_user(
            username=username,
            password=data["password"],
            email=email,
            role="employer",
            verified=False
        )

        EmployerProfile.objects.create(
            user=user,
            full_name=data["full_name"],
            company_name=data["company_name"],
            phone_number=data["phone_number"]
        )

        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            "message": "Employer registered & logged in",
            "access": str(refresh.access_token),
            "refresh": str(refresh),

            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "verified": user.verified,
                "full_name": data["full_name"]
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
# LOGIN
@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)

        login_id = data.get("login_id")
        password = data.get("password")

        if not login_id or not password:
            return JsonResponse({"error": "Missing credentials"}, status=400)

        # find user
        user_obj = User.objects.filter(username=login_id).first() or \
                   User.objects.filter(email=login_id).first()

        if not user_obj:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        # authenticate
        user = authenticate(username=user_obj.username, password=password)

        if not user:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        # ✅ CREATE JWT TOKEN
        refresh = RefreshToken.for_user(user)

        role = "admin" if user.is_superuser else user.role

        return JsonResponse({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),

            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": role,
                "verified": user.verified,
            }
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)   

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_users(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    users = User.objects.all().values("id", "username", "role", "verified")
    return Response(list(users))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_students(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    students = StudentProfile.objects.select_related("user")

    data = [
        {
            "id": s.user.id,
            "username": s.user.username,
            "nama_penuh": s.nama_penuh,
            "email": s.user.email,
            "no_matrik": s.no_matrik,
            "no_telefon": s.no_telefon,
            "fakulti": s.fakulti,
            "kolej": s.kolej,
        }
        for s in students
    ]

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_employers(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    employers = EmployerProfile.objects.select_related("user").annotate(
        total_jobs=Count("jobs")
    )

    data = [
        {
            "id": e.user.id,
            "username": e.user.username,
            "full_name": e.full_name,
            "company_name": e.company_name,
            "phone_number": e.phone_number,
            "verified": e.user.verified,
            "email": e.user.email,
            "total_jobs": e.total_jobs
        }
        for e in employers
    ]

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_employer(request, user_id):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    try:
        user = User.objects.get(id=user_id, role="employer")
        user.verified = True
        user.save()

        return Response({"message": "Employer verified successfully"})

    except User.DoesNotExist:
        return Response({"error": "Employer not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_stats(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    return Response({
        "total_users": User.objects.count(),
        "total_students": StudentProfile.objects.count(),
        "total_employers": EmployerProfile.objects.count(),
        "verified_employers": User.objects.filter(role="employer", verified=True).count()
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_unverified_employers(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    employers = EmployerProfile.objects.select_related("user").filter(user__verified=False)

    data = [
        {
            "id": e.user.id,
            "username": e.user.username,
            "company_name": e.company_name,
            "phone_number": e.phone_number,
            "verified": e.user.verified
        }
        for e in employers
    ]

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_verified_employers(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    employers = EmployerProfile.objects.select_related("user").filter(user__verified=True)

    data = [
        {
            "id": e.user.id,
            "username": e.user.username,
            "company_name": e.company_name,
            "phone_number": e.phone_number,
            "verified": e.user.verified
        }
        for e in employers
    ]

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employer_status(request):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    return Response({
        "user_id": request.user.id,
        "verified": request.user.verified,
        "role": request.user.role
    })

from django.contrib.auth import logout


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    return Response({"message": "Logout successful. Please remove token on client."})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employer_jobs(request):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)
        jobs = Job.objects.filter(employer=employer_profile).order_by("-id")

        data = []

        for job in jobs:
            applications = JobApplication.objects.filter(job=job).order_by("-applied_at")

            data.append({
                "id": job.id,
                "job_type": job.job_type,
                "business_type": job.business_type,
                "phone": job.phone,
                "location": job.location,
                "start_date": job.start_date,
                "end_date": job.end_date,
                "work_time": job.work_time,
                "salary_estimate": job.salary_estimate,
                "num_workers": job.num_workers,
                "criteria": job.criteria,
                "total_applicants": applications.count(),
                "created_at": job.created_at.isoformat(),
                "applications": [
                    {
                        "id": app.id,
                        "student": {
                            "id": app.student.user.id,
                            "username": app.student.user.username,
                            "nama_penuh": app.student.nama_penuh,
                            "email": app.student.user.email,
                            "no_matrik": app.student.no_matrik,
                            "no_telefon": app.student.no_telefon,
                            "fakulti": app.student.fakulti,
                            "kolej": app.student.kolej,
                        },
                        "status": app.status,
                        "applied_at": app.applied_at,
                        "complaint": app.complaint,
                        "complaint_status": app.complaint_status,
                    }
                    for app in applications
                ]
            })

        return Response(data)

    except EmployerProfile.DoesNotExist:
        return Response({"error": "Employer profile not found"}, status=404)
  

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_job(request):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        data = request.data  # 🔥 CHANGE json.loads(request.body)

        employer_profile = EmployerProfile.objects.get(user=request.user)

        job = Job.objects.create(
            employer=employer_profile,
            job_type=data.get("job_type"),
            business_type=data.get("business_type"),
            phone=data.get("phone"),
            location=data.get("location"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            work_time=data.get("work_time"),
            salary_estimate=data.get("salary_estimate"),
            num_workers=(data.get("num_workers", 0)),
            criteria=data.get("criteria"),
        )

        return Response({
            "message": "Job posted successfully",
            "job_id": job.id,
            "created_at": job.created_at.isoformat()
        }, status=201)

    except EmployerProfile.DoesNotExist:
        return Response({"error": "Employer profile not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_jobs(request):

    jobs = Job.objects.all().order_by("-id")

    data = []
    for job in jobs:
        data.append({
            "id": job.id,
            "employer_id": job.employer.user.id,
            "job_type": job.job_type,
            "business_type": job.business_type,
            "phone": job.phone,
            "location": job.location,
            "start_date": job.start_date,
            "end_date": job.end_date,
            "work_time": job.work_time,
            "salary_estimate": job.salary_estimate,
            "num_workers": job.num_workers,
            "criteria": job.criteria,
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request, job_id):

    if request.user.role != "student":
        return Response({"error": "Not student"}, status=403)

    try:
        job = Job.objects.get(id=job_id)

        if job.end_date < timezone.now().date():
            return Response({
                "error": "This job has expired and cannot be applied"
            }, status=400)

        student = StudentProfile.objects.get(user=request.user)

        application = JobApplication.objects.filter(
            job=job,
            student=student
        ).first()

        if not application:
            application = JobApplication.objects.create(
                job=job,
                student=student,
                status="pending"
            )
        else:
            if application.status == "cancelled":
                application.status = "pending"
                application.save()
            else:
                return Response({
                    "message": "Already applied",
                    "status": application.status
                }, status=400)

        return Response({
            "message": "Applied successfully",
            "job_id": job.id,
            "application_id": application.id,
            "status": application.status
        })

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employer_applications(request):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)

        jobs = Job.objects.filter(employer=employer_profile)

        data = []

        for job in jobs:
            applications = JobApplication.objects.filter(job=job).order_by("-applied_at")

            data.append({
                "job_id": job.id,
                "job_type": job.job_type,
                "location": job.location,
                "total_applicants": applications.count(),
                "latest_application": (
                    {
                        "student_name": applications.first().student.nama_penuh,
                        "applied_at": applications.first().applied_at,
                    } if applications.exists() else None
                ),
                "applications": [
                    {
                        "id": app.id,
                        "student": {
                            "id": app.student.user.id,
                            "username": app.student.user.username,
                            "nama_penuh": app.student.nama_penuh,
                            "no_matrik": app.student.no_matrik,
                            "no_telefon": app.student.no_telefon,
                            "fakulti": app.student.fakulti,
                            "kolej": app.student.kolej,
                        },
                        "status": app.status,
                        "applied_at": app.applied_at,
                    }
                    for app in applications
                ]
            })

        return Response(data)

    except EmployerProfile.DoesNotExist:
        return Response({"error": "Employer profile not found"}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_application(request, app_id):

    try:
        data = request.data
        action = data.get("action")

        app = JobApplication.objects.get(id=app_id)

        if action == "reject":
            app.status = "rejected"
        elif action == "confirm":
            app.status = "confirmed"
        else:
            return Response({"error": "Invalid action"}, status=400)

        app.save()

        return Response({
            "message": "success",
            "status": app.status,
            "app_id": app.id
        })

    except JobApplication.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_applications(request):

    if request.user.role != "student":
        return Response({"error": "Not student"}, status=403)

    try:
        student = StudentProfile.objects.get(user=request.user)

        applications = JobApplication.objects.filter(
            student=student
        ).order_by("-applied_at")

        data = [
            {
                "id": app.id,
                "job_id": app.job.id,
                "job_type": app.job.job_type,
                "location": app.job.location,
                "company": app.job.employer.company_name,
                "status": app.status,
                "applied_at": app.applied_at.strftime("%Y-%m-%d %H:%M:%S"),
                "feedback_status": getattr(app, "feedback_status", "not_submitted"),
            }
            for app in applications
        ]

        return Response(data)

    except StudentProfile.DoesNotExist:
        return Response({"error": "Student profile not found"}, status=404)
       

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_job(request, job_id):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        job = Job.objects.get(id=job_id)

        if job.employer.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        data = request.data

        today = timezone.now().date()

        start_date = data.get("start_date", job.start_date)
        end_date = data.get("end_date", job.end_date)

        from datetime import datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_date < today:
            return Response({"error": "Start date cannot be in the past"}, status=400)

        if end_date < start_date:
            return Response({"error": "End date must be after start date"}, status=400)

        job.job_type = data.get("job_type", job.job_type)
        job.business_type = data.get("business_type", job.business_type)
        job.phone = data.get("phone", job.phone)
        job.location = data.get("location", job.location)
        job.start_date = start_date
        job.end_date = end_date
        job.work_time = data.get("work_time", job.work_time)
        job.salary_estimate = data.get("salary_estimate", job.salary_estimate)
        job.num_workers = int(data.get("num_workers", job.num_workers))
        job.criteria = data.get("criteria", job.criteria)

        job.save()

        return Response({
            "message": "Job updated successfully",
            "job_id": job.id
        })

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)
       
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_job(request, job_id):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        job = Job.objects.get(id=job_id)

        if job.employer.user != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        job.delete()

        return Response({
            "message": "Job deleted successfully"
        })

    except Job.DoesNotExist:
        return Response({"error": "Job not found"}, status=404)
       
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_application(request, job_id):

    if request.user.role != "student":
        return Response({"error": "Not student"}, status=403)

    try:
        student = StudentProfile.objects.get(user=request.user)

        app = JobApplication.objects.get(
            job_id=job_id,
            student=student,
            status="pending"
        )

        app.status = "cancelled"
        app.save()

        return Response({
            "message": "Application cancelled successfully",
            "job_id": job_id,
            "status": app.status
        })

    except JobApplication.DoesNotExist:
        return Response({
            "error": "Application not found or already processed"
        }, status=404)

    except StudentProfile.DoesNotExist:
        return Response({
            "error": "Student profile not found"
        }, status=404)
    


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_full_report(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    try:
        one_week_ago = timezone.now() - timedelta(days=7)

        weekly_accepted = (
            JobApplication.objects
            .filter(status="confirmed", applied_at__gte=one_week_ago)
            .extra(select={"date": "DATE(applied_at)"})
            .values("date")
            .annotate(total_accepted=Count("id"))
            .order_by("date")
        )

        weekly_rejected = (
            JobApplication.objects
            .filter(status="rejected", applied_at__gte=one_week_ago)
            .extra(select={"date": "DATE(applied_at)"})
            .values("date")
            .annotate(total_rejected=Count("id"))
            .order_by("date")
        )

        weekly_cancelled = (
            JobApplication.objects
            .filter(status="cancelled", applied_at__gte=one_week_ago)
            .extra(select={"date": "DATE(applied_at)"})
            .values("date")
            .annotate(total_cancelled=Count("id"))
            .order_by("date")
        )

        weekly_pending = (
            JobApplication.objects
            .filter(status="pending", applied_at__gte=one_week_ago)
            .extra(select={"date": "DATE(applied_at)"})
            .values("date")
            .annotate(total_pending=Count("id"))
            .order_by("date")
        )

        faculty_data = StudentProfile.objects.values("fakulti").annotate(total=Count("id"))
        college_data = StudentProfile.objects.values("kolej").annotate(total=Count("id"))

        total_feedback = JobApplication.objects.exclude(feedback__isnull=True).exclude(feedback="").count()
        total_complaints = JobApplication.objects.exclude(complaint__isnull=True).exclude(complaint="").count()

        total_apps = JobApplication.objects.count()

        pending_apps = JobApplication.objects.filter(status="pending").count()
        accepted_apps = JobApplication.objects.filter(status="confirmed").count()
        rejected_apps = JobApplication.objects.filter(status="rejected").count()
        cancelled_apps = JobApplication.objects.filter(status="cancelled").count()

        cancel_rate = round((cancelled_apps / total_apps) * 100, 2) if total_apps else 0
        accepted_rate = round((accepted_apps / total_apps) * 100, 2) if total_apps else 0
        rejected_rate = round((rejected_apps / total_apps) * 100, 2) if total_apps else 0
        pending_rate = round((pending_apps / total_apps) * 100, 2) if total_apps else 0

        return Response({
            "weekly_accepted": list(weekly_accepted),
            "weekly_rejected": list(weekly_rejected),
            "weekly_cancelled": list(weekly_cancelled),
            "weekly_pending": list(weekly_pending),

            "faculty_stats": list(faculty_data),
            "college_stats": list(college_data),

            "total_users": User.objects.count(),
            "total_students": StudentProfile.objects.count(),
            "total_jobs": Job.objects.count(),
            "total_employers": EmployerProfile.objects.count(),

            "active_jobs": Job.objects.filter(end_date__gte=timezone.now()).count(),
            "expired_jobs": Job.objects.filter(end_date__lt=timezone.now()).count(),

            "total_feedback": total_feedback,
            "total_complaints": total_complaints,

            "total_applications": total_apps,

            "pending_apps": pending_apps,
            "total_accepted": accepted_apps,
            "total_rejected": rejected_apps,
            "total_cancelled": cancelled_apps,

            "cancel_rate": cancel_rate,
            "accepted_rate": accepted_rate,
            "rejected_rate": rejected_rate,
            "pending_rate": pending_rate,
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)   

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_complaint_list(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    student_id = request.GET.get("student_id")

    data = JobApplication.objects.exclude(
        complaint__isnull=True
    ).exclude(complaint="").select_related("student", "job")

    if student_id:
        data = data.filter(student__user__id=student_id)

    return Response([
        {
            "id": a.id,
            "student_id": a.student.user.id,
            "student": a.student.nama_penuh,
            "job": a.job.job_type,
            "complaint": a.complaint,
            "status": a.complaint_status,
            "applied_at": a.applied_at
        }
        for a in data
    ])

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_feedback_list(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    data = JobApplication.objects.exclude(
        feedback__isnull=True
    ).exclude(feedback="").select_related("student", "job")

    return Response([
        {
            "id": a.id,
            "student": a.student.nama_penuh,
            "job": a.job.job_type,
            "feedback": a.feedback,
            "status": a.feedback_status,
            "applied_at": a.applied_at
        }
        for a in data
    ])

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_student_report(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    students = StudentProfile.objects.select_related("user")

    data = []

    for s in students:
        total_apps = JobApplication.objects.filter(student=s).count()
        accepted = JobApplication.objects.filter(student=s, status="confirmed").count()
        rejected = JobApplication.objects.filter(student=s, status="rejected").count()

        data.append({
            "student_id": s.user.id,
            "name": s.nama_penuh,
            "faculty": s.fakulti,
            "college": s.kolej,
            "total_applications": total_apps,
            "accepted": accepted,
            "rejected": rejected,
        })

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_employer_report(request):

    if request.user.role != "admin" and not request.user.is_superuser:
        return Response({"error": "Not admin"}, status=403)

    employers = EmployerProfile.objects.select_related("user")

    data = []

    for e in employers:
        jobs = Job.objects.filter(employer=e)

        total_jobs = jobs.count()

        total_apps = JobApplication.objects.filter(job__in=jobs).count()
        accepted = JobApplication.objects.filter(job__in=jobs, status="confirmed").count()

        data.append({
            "employer_id": e.user.id,
            "company": e.company_name,
            "verified": e.user.verified,
            "total_jobs": total_jobs,
            "total_applications": total_apps,
            "accepted_applications": accepted,
        })

    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_student(request, app_id):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    complaint = request.data.get("complaint")

    if not complaint:
        return Response({"error": "Complaint required"}, status=400)

    try:
        app = JobApplication.objects.get(id=app_id)

        if app.status != "confirmed":
            return Response(
                {"error": "Only accepted students can be reported"},
                status=400
            )

        app.complaint = complaint
        app.complaint_status = "reported"
        app.feedback_status = "not_submitted"
        app.save()

        return Response({
            "message": "Student reported successfully"
        })

    except JobApplication.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_feedback(request, app_id):

    if request.user.role != "student":
        return Response({"error": "Not student"}, status=403)

    feedback = request.data.get("feedback")

    if not feedback:
        return Response({"error": "Feedback required"}, status=400)

    try:
        app = JobApplication.objects.get(id=app_id)

        if app.status != "confirmed":
            return Response(
                {"error": "Only completed jobs can be reviewed"},
                status=400
            )

        app.feedback = feedback
        app.feedback_status = "submitted"
        app.save()

        return Response({
            "message": "Feedback submitted successfully",
            "status": app.feedback_status
        })

    except JobApplication.DoesNotExist:
        return Response({"error": "Application not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
      

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_employer_profile(request):

    if request.user.role != "employer":
        return Response({"error": "Not employer"}, status=403)

    try:
        data = request.data

        profile = EmployerProfile.objects.get(user=request.user)

        profile.full_name = data.get("full_name", profile.full_name)
        profile.company_name = data.get("company_name", profile.company_name)
        profile.phone_number = data.get("phone_number", profile.phone_number)

        request.user.email = data.get("email", request.user.email)

        profile.save()
        request.user.save()

        return Response({"message": "Profile updated successfully"})

    except EmployerProfile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_student_accepted_report(request):

    # 🔒 ADMIN ONLY ACCESS CONTROL
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    if request.user.role != "admin" and not request.user.is_superuser:
        return JsonResponse({"error": "Admin only access"}, status=403)

    # 📊 QUERY STUDENT DATA WITH STATS
    students = StudentProfile.objects.select_related("user").annotate(
        total_applications=Count("jobapplication"),
        accepted_jobs=Count(
            "jobapplication",
            filter=Q(jobapplication__status="confirmed")
        ),
        rejected_jobs=Count(
            "jobapplication",
            filter=Q(jobapplication__status="rejected")
        ),
        total_complaints=Count(
            "jobapplication",
            filter=Q(jobapplication__complaint__isnull=False) &
                   ~Q(jobapplication__complaint="")
        )
    )

    # 📦 FORMAT RESPONSE
    data = [
        {
            "student_id": s.user.id,
            "name": s.nama_penuh,
            "email": s.user.email,
            "faculty": s.fakulti,
            "college": s.kolej,
            "total_applications": s.total_applications,
            "accepted_jobs": s.accepted_jobs,
            "rejected_jobs": s.rejected_jobs,
            "total_complaints": s.total_complaints,
        }
        for s in students
    ]

    return JsonResponse(data, safe=False)