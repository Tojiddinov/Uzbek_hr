from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    ]

    EMPLOYER_TYPE_CHOICES = [
        ('company', 'Company'),
        ('university', 'University'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    employer_type = models.CharField(max_length=20, choices=EMPLOYER_TYPE_CHOICES, blank=True, null=True)
    age = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.role == 'job_seeker':
            self.employer_type = None  # Only employers should have an employer_type
        super().save(*args, **kwargs)

    def is_job_seeker(self):
        return self.role == 'job_seeker'

    def is_employer(self):
        return self.role == 'employer'


class Job(models.Model):
    CATEGORY_CHOICES = [
        ('IT', 'IT & Software'),
        ('Finance', 'Finance & Banking'),
        ('Marketing', 'Marketing & Sales'),
        ('Education', 'Education & Teaching'),
        ('Healthcare', 'Healthcare & Medicine'),
        ('Other', 'Other'),
    ]

    EMPLOYMENT_TYPES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="jobs")
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    requirements = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPES)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="jobs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    # employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} at {self.company} ({self.get_status_display()})"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Reviewed", "Reviewed"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="applications")

    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.FileField(upload_to="cover_letters/")
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    university_or_school = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    applied_at = models.DateTimeField(auto_now_add=True)
    ai_generated_questions = models.JSONField(default=list)
    test_answers = models.JSONField(default=dict)
    test_deadline = models.DateTimeField(null=True, blank=True)
    shortlisted = models.BooleanField(default=False)

    generated_questions = models.JSONField(default=list, blank=True)

    def shortlist(self):
        """ Nomzodni shortlist qilish funksiyasi """
        self.shortlisted = True
        self.status = "Reviewed"  # Shortlist qilinganda "Reviewed" holatiga o'tadi
        self.save()

    def __str__(self):
        return f"{self.applicant} - {self.job.title} ({self.get_status_display()})"

    class Meta:
        unique_together = ("job", "applicant")

    def __str__(self):
        return f"{self.applicant.username} - {self.job.title}"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_application = JobApplication.objects.get(pk=self.pk)
                
                if old_application.status != self.status or (not old_application.generated_questions and self.generated_questions):
                    self.send_status_email()
                    if self.status == "Reviewed" and self.generated_questions:
                        self.send_interview_questions_email()
            except JobApplication.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)

    def send_status_email(self):
        subject = f"Sizning '{self.job.title}' lavozimi uchun arizangiz {self.status} holatiga o'zgardi"
        message = f"Assalomu alaykum, {self.name}!\n\nSizning arizangiz yangilandi.\n\nHurmat bilan,\nUzbek HR jamoasi"
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [self.email], fail_silently=True)

    def send_interview_questions_email(self):
        subject = "Your AI-Generated Interview Questions"
        message = f"Congratulations, {self.name}!\n\n"
        message += "Sizning resume screening jarayoningiz muvaffaqiyatli yakunlandi.\n"
        message += "Quyida AI tomonidan yaratilgan intervyu savollarini topishingiz mumkin:\n\n"

        for idx, question in enumerate(self.generated_questions, start=1):
            message += f"{idx}. {question}\n"

        message += "\nSavollarga 3 kun ichida javob bering.\n\nHurmat bilan,\nUzbek HR jamoasi"

        send_mail(subject, message, settings.EMAIL_HOST_USER, [self.email], fail_silently=True)

class Resume(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="resumes")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    linkedin = models.URLField(blank=True, null=True)
    resume_file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}'s Resume"

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="job_seeker_profile")
    first_name = models.CharField(max_length=50, blank=True, null=False)
    last_name = models.CharField(max_length=50, blank=True, null=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    university_name = models.CharField(max_length=200, null=True, blank=True)
    faculty = models.CharField(max_length=200, null=True, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Job Seeker Profile"

class TestDashboard(models.Model):
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE)
    questions = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Test for {self.application.applicant.username}"
