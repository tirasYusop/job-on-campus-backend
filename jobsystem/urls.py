from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    admin_complaint_list,
    admin_employer_report,
    admin_feedback_list,
    admin_full_report,
    admin_student_accepted_report,
    admin_student_report,
    apply_job,
    cancel_application,
    delete_job,
    employer_profile,
    get_all_jobs,
    logout_view,
    report_student,
    student_applications,
    student_register,
    employer_register,
    login_view,

    get_all_users,
    get_students,
    get_employers,
    submit_feedback,
    update_employer_profile,
    update_job,
    admin_stats,
        employer_status,
        employer_jobs,
        post_job,
        employer_applications,
        confirm_application

        
)
from jobsystem import views

urlpatterns = [
    path("employer/profile/", employer_profile),
    path('student-register/', student_register, name='student_register'),
    path('employer-register/', employer_register, name='employer_register'),
    path('login/', login_view, name='login'),
    path('admin/users/', get_all_users, name='get_all_users'),
    path('admin/students/', get_students, name='get_students'),
    path('admin/employers/', get_employers, name='get_employers'),
    path('admin/stats/', admin_stats, name='admin_stats'),
    path('employer-status/', employer_status, name='employer_status'),
    path("logout/", logout_view, name="logout"),
    path("employer-jobs/", employer_jobs, name="employer_jobs"),  
    path("employer/post-job/",post_job, name="post_job"),
    path("jobs/", get_all_jobs, name="get_all_jobs"),
    path("apply-job/<int:job_id>/", apply_job, name="apply_job"),
    path("employer-applications/", employer_applications, name="employer_applications"),
    path("confirm-application/<int:app_id>/",confirm_application, name="confirm_application"),
    path("student-applications/", student_applications, name="student_applications"),
    path("employer/job/delete-job/<int:job_id>/", delete_job, name="delete_job"),
    path("employer/job/update-job/<int:job_id>/", update_job, name="update_job"),
    path("cancel-application/<int:job_id>/",cancel_application,name="cancel_application"),
    path("admin/full-report/", admin_full_report,name="admin_full_report"),
    path("admin/student-report/", admin_student_report),
    path("admin/employer-report/", admin_employer_report),
    path("admin/student-accepted-report/", admin_student_accepted_report),
    path("employer/student-report/<int:app_id>", report_student),
    path("student/submit-feedback/<int:app_id>/",submit_feedback),
    path("admin/feedback-list/", admin_feedback_list),
    path("admin/complaint-list/",admin_complaint_list),
    path("employer/update-employer-profile/", update_employer_profile),
     path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


]

