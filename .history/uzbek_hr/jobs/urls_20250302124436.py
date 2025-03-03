from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("change-password/", views.change_password, name="password_change"),
    path("dashboard/", views.redirect_user_dashboard, name="dashboard"),
    path("application/update/<int:application_id>/", views.update_application_status, name="update_application_status"),
    path("delete-job/<int:job_id>/", views.delete_job, name="delete_job"),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),


    # test dashboard
    path('test-dashboard/', views.test_dashboard, name='test_dashboard'),
    path('shortlist/<int:application_id>/', views.shortlist_application, name='shortlist_application'),
    path("employer/test-results/<int:application_id>/", views.employer_test_results, name="employer_test_results"),
    path('test-complete/', views.test_complete, name='test_complete'),





    # Dashboards
    path("dashboard/employer/", views.employer_dashboard, name="employer_dashboard"),
    path("dashboard/job_seeker/", views.job_seeker_dashboard, name="job_seeker_dashboard"),
    path('shortlist-dashboard/', views.shortlist_dashboard, name='shortlist_dashboard'),
    
    # path('dashboard/', views.application_dashboard, name='application'),


    # Jobs
    path("", views.home, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:job_id>/", views.job_detail, name="job_detail"),
    path('jobs/create/', views.job_create, name='job_create'),

    # Job Applications
    path("jobs/<int:job_id>/apply/", views.apply_for_job, name="apply_for_job"),
    path("applications/", views.job_applications_list, name="job_applications_list"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),

    # AI Resume Analysis
    # path("jobs/<int:job_id>/resume/analysis/", views.ai_resume_review, name="ai_resume_review"),
    path("resume/upload/", views.upload_resume, name="upload_resume"),
    path('ai-review/<int:application_id>/', views.ai_resume_review, name='ai_resume_review'),


    # Resume Upload
    # path("jobs/<int:job_id>/resume/upload/", views.upload_resume, name="upload_resume"),
]
