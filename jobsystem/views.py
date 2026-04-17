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
from django.db.models.functions import Coalesce


from django.http import JsonResponse
from django.contrib.auth import get_user_model

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
        login(request, user)

        return JsonResponse({
            "message": "Student registered & logged in",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

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

        login(request, user)

        return JsonResponse({
            "message": "Employer registered & logged in",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "verified": user.verified,
            "full_name": data["full_name"]
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
            return JsonResponse(
                {"error": "Username / Email and password required"},
                status=400
            )

        # 🔥 Find user (username OR email)
        user_obj = User.objects.filter(
            username=login_id
        ).first() or User.objects.filter(
            email=login_id
        ).first()

        if not user_obj:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        # 🔥 Authenticate properly
        user = authenticate(username=user_obj.username, password=password)

        if not user:
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        login(request, user)

        # 🔥 FORCE admin rule
        role = "admin" if user.is_superuser else user.role

        return JsonResponse({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role,
            "verified": user.verified,
            "is_superuser": user.is_superuser
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
@csrf_exempt
def get_all_users(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    users = User.objects.all().values("id", "username", "role", "verified")
    return JsonResponse(list(users), safe=False)

@csrf_exempt
def get_students(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    students = StudentProfile.objects.select_related("user")

    data = []
    for s in students:
        data.append({
            "id": s.user.id,
            "username": s.user.username,
            "nama_penuh": s.nama_penuh,
            "no_matrik": s.no_matrik,
            "no_telefon": s.no_telefon,
            "fakulti": s.fakulti,
            "kolej": s.kolej,
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def get_employers(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)
    employers = EmployerProfile.objects.select_related("user")
    data = []
    for e in employers:
        data.append({
            "id": e.user.id,
            "username": e.user.username,
            "full_name": e.full_name,
            "company_name": e.company_name,
            "phone_number": e.phone_number,
            "verified": e.user.verified
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def verify_employer(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        user = User.objects.get(id=user_id, role="employer")
        user.verified = True
        user.save()
        return JsonResponse({"message": "Employer verified successfully"})
    except User.DoesNotExist:
        return JsonResponse({"error": "Employer not found"}, status=404)
    
    
@csrf_exempt
def admin_stats(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)
    return JsonResponse({
        "total_users": User.objects.count(),
        "total_students": StudentProfile.objects.count(),
        "total_employers": EmployerProfile.objects.count(),
        "verified_employers": User.objects.filter(role="employer", verified=True).count()
    })

@csrf_exempt
def get_unverified_employers(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)
    employers = EmployerProfile.objects.select_related("user").filter(user__verified=False)
    data = []
    for e in employers:
        data.append({
            "id": e.user.id,
            "username": e.user.username,
            "company_name": e.company_name,
            "phone_number": e.phone_number,
            "verified": e.user.verified
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def get_verified_employers(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    employers = EmployerProfile.objects.select_related("user").filter(user__verified=True)

    data = []
    for e in employers:
        data.append({
            "id": e.user.id,
            "username": e.user.username,
            "company_name": e.company_name,
            "phone_number": e.phone_number,
            "verified": e.user.verified
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def employer_status(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

    return JsonResponse({
        "user_id": request.user.id,
        "verified": request.user.verified,
        "role": request.user.role
    })

from django.contrib.auth import logout

@csrf_exempt
def logout_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    logout(request)

    return JsonResponse({"message": "Logged out successfully"})

@csrf_exempt
def employer_jobs(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

    try:
        employer_profile = EmployerProfile.objects.get(user=request.user)

        jobs = Job.objects.filter(employer=employer_profile).order_by("-id")

        data = []

        for job in jobs:
            applications = JobApplication.objects.filter(job=job).order_by("-applied_at")

            data.append({
                "id": job.id,   # ✅ IMPORTANT (consistent)
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
                #SEND ARRAY 
                "applications": [
                    {
                        "id": app.id,

                        # ✅ FULL STUDENT OBJECT (MATCH FRONTEND)
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
                        "complaint": app.complaint,
                        "complaint_status": app.complaint_status,
                    }
                    for app in applications
                ]
            })

        return JsonResponse(data, safe=False)

    except EmployerProfile.DoesNotExist:
        return JsonResponse({"error": "Employer profile not found"}, status=404)
    

@csrf_exempt
def post_job(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

    try:
        data = json.loads(request.body)

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
            num_workers=int(data.get("num_workers", 0)),
            criteria=data.get("criteria"),
        )

        return JsonResponse({
            "message": "Job posted successfully",
            "job_id": job.id,
            "created_at": job.created_at.isoformat()  # ✅ ADD THIS
        }, status=201)

    except EmployerProfile.DoesNotExist:
        return JsonResponse({"error": "Employer profile not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)  

@csrf_exempt
def get_all_jobs(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

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
            "created_at": job.created_at.strftime("%Y-%m-%d %H:%M:%S")  # TEMP fallback (or use actual field if you have)
        })

    return JsonResponse(data, safe=False)


@csrf_exempt
def apply_job(request, job_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "student":
        return JsonResponse({"error": "Not student"}, status=403)

    try:
        job = Job.objects.get(id=job_id)
        student = StudentProfile.objects.get(user=request.user)
        #noduplicate applications
        application = JobApplication.objects.filter(
            job=job,
            student=student
        ).first()

        # If no application exists at all → create new
        if not application:
            application = JobApplication.objects.create(
                job=job,
                student=student,
                status="pending"
            )
        else:
            # If previously cancelled → allow re-apply
            if application.status == "cancelled":
                application.status = "pending"
                application.save()
            else:
                return JsonResponse({
                    "message": "Already applied",
                    "status": application.status
                }, status=400)

        return JsonResponse({
            "message": "Applied successfully",
            "job_id": job.id,
            "application_id": application.id,
            "status": application.status
        })

    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    except StudentProfile.DoesNotExist:
        return JsonResponse({"error": "Student profile not found"}, status=404)   


@csrf_exempt
def employer_applications(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

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
                #lates notification (for badge)
                "latest_application": (
                    {
                        "student_name": applications.first().student.nama_penuh,
                        "applied_at": applications.first().applied_at,
                    } if applications.exists() else None
                ),
                # list of all applications 
                    "applications": [
                        {
                            "id": app.id,

                            # FULL STUDENT INFO
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

        return JsonResponse(data, safe=False)

    except EmployerProfile.DoesNotExist:
        return JsonResponse({"error": "Employer profile not found"}, status=404)
    


@csrf_exempt
def confirm_application(request, app_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        data = json.loads(request.body or "{}")
        action = data.get("action")

        app = JobApplication.objects.get(id=app_id)

        # only allow valid actions
        if action == "reject":
            app.status = "rejected"
        elif action == "confirm":
            app.status = "confirmed"
        else:
            return JsonResponse({"error": "Invalid action"}, status=400)

        app.save()

        return JsonResponse({
            "message": "success",
            "status": app.status,
            "app_id": app.id
        })

    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

@csrf_exempt
def student_applications(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        # ALWAYS reload from DB to get latest role/status
        user = User.objects.get(id=request.user.id)

        if user.role != "student":
            return JsonResponse({"error": "Not student"}, status=403)

        student = StudentProfile.objects.get(user=user)

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

        return JsonResponse(data, safe=False)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    except StudentProfile.DoesNotExist:
        return JsonResponse({"error": "Student profile not found"}, status=404)
    

@csrf_exempt
def update_job(request, job_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

    try:
        job = Job.objects.get(id=job_id)

        # 🔒 Ensure only owner can edit
        if job.employer.user != request.user:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        data = json.loads(request.body)

        # update fields (only if provided)
        job.job_type = data.get("job_type", job.job_type)
        job.business_type = data.get("business_type", job.business_type)
        job.phone = data.get("phone", job.phone)
        job.location = data.get("location", job.location)
        job.start_date = data.get("start_date", job.start_date)
        job.end_date = data.get("end_date", job.end_date)
        job.work_time = data.get("work_time", job.work_time)
        job.salary_estimate = data.get("salary_estimate", job.salary_estimate)
        job.num_workers = int(data.get("num_workers", job.num_workers))
        job.criteria = data.get("criteria", job.criteria)

        job.save()

        return JsonResponse({
            "message": "Job updated successfully",
            "job_id": job.id
        })

    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)
    
@csrf_exempt
def delete_job(request, job_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

    try:
        job = Job.objects.get(id=job_id)

        # 🔒 Only owner can delete
        if job.employer.user != request.user:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        job.delete()

        return JsonResponse({
            "message": "Job deleted successfully"
        })

    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)
    
@csrf_exempt
def cancel_application(request, job_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "student":
        return JsonResponse({"error": "Not student"}, status=403)

    try:
        student = StudentProfile.objects.get(user=request.user)

        app = JobApplication.objects.get(
            job_id=job_id,
            student=student,
            status="pending"
        )

        # 🔥 FIX: DO NOT DELETE → MARK AS CANCELLED
        app.status = "cancelled"
        app.save()

        return JsonResponse({
            "message": "Application cancelled successfully",
            "job_id": job_id,
            "status": app.status
        })

    except JobApplication.DoesNotExist:
        return JsonResponse({
            "error": "Application not found or already processed"
        }, status=404)

    except StudentProfile.DoesNotExist:
        return JsonResponse({
            "error": "Student profile not found"
        }, status=404)

@csrf_exempt
def admin_full_report(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    try:
        from django.utils import timezone

        one_week_ago = timezone.now() - timedelta(days=7)

        weekly_accepted = (
            JobApplication.objects
            .filter(status="confirmed", applied_at__gte=one_week_ago)
            .extra(select={"date": "DATE(applied_at)"})
            .values("date")
            .annotate(total_accepted=Count("id"))
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
        faculty_data = (
            StudentProfile.objects
            .values("fakulti")
            .annotate(total=Count("id"))
        )

        college_data = (
            StudentProfile.objects
            .values("kolej")
            .annotate(total=Count("id"))
        )

        total_feedback = JobApplication.objects.exclude(
            feedback__isnull=True
        ).exclude(feedback="").count()

        total_complaints = JobApplication.objects.exclude(
            complaint__isnull=True
        ).exclude(complaint="").count()

        total_apps = JobApplication.objects.count()
        cancelled_apps = JobApplication.objects.filter(status="cancelled").count()

        cancel_rate = round((cancelled_apps / total_apps) * 100, 2) if total_apps else 0

        return JsonResponse({
            "weekly_accepted": list(weekly_accepted),
            "weekly_cancelled": list(weekly_cancelled),
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
            "total_cancelled": cancelled_apps,
            "cancel_rate": cancel_rate
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)    
@csrf_exempt
def admin_complaint_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    data = JobApplication.objects.exclude(
        complaint__isnull=True
    ).exclude(complaint="").select_related("student", "job")

    return JsonResponse([
        {
            "id": a.id,
            "student": a.student.nama_penuh,
            "job": a.job.job_type,
            "complaint": a.complaint,
            "status": a.complaint_status,
            "applied_at": a.applied_at
        }
        for a in data
    ], safe=False)
            

@csrf_exempt
def admin_feedback_list(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

    data = JobApplication.objects.exclude(
        feedback__isnull=True
    ).exclude(feedback="").select_related("student", "job")

    return JsonResponse([
        {
            "id": a.id,
            "student": a.student.nama_penuh,
            "job": a.job.job_type,
            "feedback": a.feedback,
            "status": a.feedback_status,
            "applied_at": a.applied_at
        }
        for a in data
    ], safe=False)

@csrf_exempt
def admin_student_report(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

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

    return JsonResponse(data, safe=False)

@csrf_exempt
def admin_employer_report(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET only"}, status=405)

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

    return JsonResponse(data, safe=False)

@csrf_exempt
def report_student(request, app_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "employer":
        return JsonResponse({"error": "Not employer"}, status=403)

    try:
        # ✅ SAFE JSON PARSE
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    complaint = data.get("complaint")

    if not complaint:
        return JsonResponse({"error": "Complaint required"}, status=400)

    try:
        app = JobApplication.objects.get(id=app_id)

        # only allow reporting accepted students
        if app.status != "confirmed":
            return JsonResponse(
                {"error": "Only accepted students can be reported"},
                status=400
            )

        # ✅ SAVE COMPLAINT
        app.complaint = complaint
        app.complaint_status = "reported"
        app.feedback_status = "not_submitted"
        app.save()

        return JsonResponse({
            "message": "Student reported successfully"
        })

    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)


@csrf_exempt
def submit_feedback(request, app_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.user.role != "student":
        return JsonResponse({"error": "Not student"}, status=403)

    try:
        data = json.loads(request.body.decode("utf-8"))
        feedback = data.get("feedback")

        if not feedback:
            return JsonResponse({"error": "Feedback required"}, status=400)

        app = JobApplication.objects.get(id=app_id)

        # only allow feedback for confirmed jobs
        if app.status != "confirmed":
            return JsonResponse({"error": "Only completed jobs can be reviewed"}, status=400)

        # save feedback
        app.feedback = feedback
        app.feedback_status = "submitted"
        app.save()

        return JsonResponse({
            "message": "Feedback submitted successfully",
            "status": app.feedback_status
        })

    except JobApplication.DoesNotExist:
        return JsonResponse({"error": "Application not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)