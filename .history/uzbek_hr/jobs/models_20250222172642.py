from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
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

    # **MISSING FIELD ADDED**
    age = models.PositiveIntegerField(null=True, blank=True)
    university = models.CharField(max_length=255, null=True, blank=True)

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

    def __str__(self):
        return f"{self.title} at {self.company} ({self.get_status_display()})"


# ✅ Job Application Model
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('test_assigned', 'Test Assigned'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')

    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.FileField(upload_to='cover_letters/')

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    university_or_school = models.CharField(max_length=255)
    email = models.EmailField()
    username = models.CharField(max_length=150)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    ai_review = models.TextField(blank=True, null=True)  # AI natijalari
    ai_questions = models.TextField(blank=True, null=True)  # AI-generated savollar

    class Meta:
        unique_together = ('job', 'applicant')  # Foydalanuvchi har bir vakansiyaga faqat bir marta ariza topshirishi mumkin.

    def __str__(self):
        return f"{self.name} {self.surname} - {self.job.title}"

    def save(self, *args, **kwargs):
        if self.pk:
             old_application = JobApplication.objects.filter(pk=self.pk).first()
               if old_application and old_application.status != self.status:
            self.send_status_email()
    super().save(*args, **kwargs)
        # Agar ariza allaqachon mavjud bo'lsa (update)
       
        if self.pk:
            old_application = JobApplication.objects.get(pk=self.pk)
            if old_application.status != self.status:
                self.send_status_email()
        super().save(*args, **kwargs)

    def send_status_email(self):
        """Ariza holati o'zgarganda xabarnoma yuborish"""
        subject = f"Sizning '{self.job.title}' lavozimi uchun arizangiz {self.status} holatiga o'zgardi"
        message = f"Assalomu alaykum, {self.name}!\n\n" \
                  f"Sizning '{self.job.title}' lavozimi uchun arizangiz {self.status} holatiga o'zgardi.\n\n" \
                  f"Hurmat bilan,\nUzbek HR jamoasi"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [self.email], fail_silently=False)

    def get_questions_list(self):
        return self.ai_questions.split("\n") if self.ai_questions else []


# User = get_user_model()

    class Meta:
        unique_together = (
        'job', 'applicant')  # Har bir foydalanuvchi bir vakansiyaga faqat bir marta ariza topshira oladi.

    def __str__(self):
        return f"{self.name} {self.surname} - {self.job.title}"

    def save(self, *args, **kwargs):
        """ Save method with email notification on status change """
        if self.pk:  # Agar update bo'lsa
            old_application = JobApplication.objects.get(pk=self.pk)
            if old_application.status != self.status:  # Agar status o'zgarsa
                self.send_status_email()

        super().save(*args, **kwargs)

    def send_status_email(self):
        """ Status o'zgarganda email jo'natish """
        subject = f"Sizning '{self.job.title}' lavozimi uchun arizangiz {self.status} holatiga o'zgardi"
        message = f"Assalomu alaykum, {self.name}!\n\n" \
                  f"Sizning '{self.job.title}' lavozimi uchun arizangiz {self.status} holatiga o'zgardi.\n\n" \
                  f"Hurmat bilan,\nUzbek HR jamoasi"
        send_mail(subject, message, "jurabeksodiqovich@gmail.com", [self.email], fail_silently=False)

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



class TestQuestion(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="test_questions")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text

class TestAnswer(models.Model):
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="test_answers")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.user.username}"

User = get_user_model()  # CustomUser modelini olish

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="job_seeker_profile")
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