import os

import openai
import pdfplumber
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import JobApplicationForm, ResumeForm, JobForm, JobSeekerProfileForm
from .models import Job, CustomUser, JobApplication, JobSeekerProfile, TestDashboard
from .utils.ai_resume_analysis import analyze_resume
from .utils.ai_resume_analysis import send_test_notification_email
from django.utils.timezone import now, timedelta
from django.http import JsonResponse
from datetime import timedelta
import json
global client

from openai import OpenAIError


openai.api_key = os.getenv("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")  # Load API key securely



# ===============================
# AUTHENTICATION (REGISTER, LOGIN, LOGOUT)
# ===============================

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        if not role:
            messages.error(request, "Please select a role.")
            return redirect("register")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("register")

        user = CustomUser.objects.create_user(username=username, email=email, password=password, role=role)
        user.save()

        messages.success(request, "Registration successful. You can now log in.")
        return redirect("login")

    return render(request, "login/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            print(f"User: {user.username}, Role: {user.role}")  # Debug uchun

            # Role maydonini kichik harflarga o‘tkazib tekshiramiz
            if user.role.lower() == "employer":
                return redirect("employer_dashboard")
            elif user.role.lower() == "job_seeker":
                return redirect("job_seeker_dashboard")
            else:
                messages.error(request, "Unknown role. Contact support.")
                return redirect("login")  # Xatolik bo‘lsa, login sahifasiga qaytaradi
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')


# ===============================
# DASHBOARDS
# ===============================

@login_required
def employer_dashboard(request):
    if request.user.role != "employer":
        return HttpResponse("Unauthorized", status=403)

    jobs = Job.objects.filter(posted_by=request.user)
    applications = JobApplication.objects.filter(job__posted_by=request.user)  # Employer faqat o‘zining vakansiyalarini ko‘radi

    return render(
        request,
        "jobs/employer_dashboard.html",
        {"jobs": jobs, "applications": applications}
    )

@login_required
def update_application_status(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(JobApplication, id=application_id)

        # Faqat ushbu arizaga tegishli vakansiyani joylagan employer statusni o‘zgartira oladi
        if application.job.posted_by != request.user:
            return HttpResponse("Unauthorized", status=403)

        new_status = request.POST.get("status")
        application.status = new_status
        application.save()
        messages.success(request, "Application status updated successfully!")

    return redirect("employer_dashboard")

@login_required
def redirect_user_dashboard(request):
    if request.user.role == "employer":
        return redirect("employer_dashboard")  # Employer uchun
    elif request.user.role == "job_seeker":
        return redirect("job_seeker_dashboard")  # Job Seeker uchun
    else:
        return HttpResponse("Unauthorized", status=403)

@login_required
def job_seeker_dashboard(request):
    """
    Dashboard for job seekers to manage applications and profile.
    """
    if request.user.role != "job_seeker":
        return HttpResponse("Unauthorized", status=403)

    applications = JobApplication.objects.filter(applicant=request.user)

    # JobSeekerProfile ni olish yoki yaratish
    profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)

    return render(request, "jobs/job_seeker_dashboard.html", {
        "applications": applications,
        "user": request.user,
        "profile": profile
    })

@login_required
def edit_profile(request):
    """
    Allows job seekers to edit their profile including personal details and profile picture.
    """
    user = request.user

    # JobSeekerProfile ni olish yoki yaratish
    profile, created = JobSeekerProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name = form.cleaned_data.get("last_name")
            user.age = form.cleaned_data.get("age")
            user.save()
            
            messages.success(request, "Profile updated successfully!")
            return redirect("job_seeker_dashboard")  # Redirect back to dashboard
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = JobSeekerProfileForm(instance=profile)

    return render(request, "jobs/edit_profile.html", {
        "user": request.user,
        "form": form
    })

def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Faqat o'zining e'lon qilgan ishlarini o'chirish huquqi
    if request.user == job.posted_by:
        job.delete()

    return redirect("employer_dashboard")


def application_detail(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    return render(request, 'jobs/application_detail.html', {'application': application})

# ===============================
# JOB VIEWS
# ===============================

def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'jobs/job_detail.html', {'job': job})


# ===============================
# JOB APPLICATION PROCESS
# ===============================

@login_required
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Job seeker oldin shu vakansiyaga ariza topshirganmi?
    existing_application = JobApplication.objects.filter(job=job, applicant=request.user).first()
    if existing_application:
        messages.error(request, "Siz bu vakansiya uchun allaqachon ariza topshirgansiz!")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.name = request.user.first_name  # User modeldan olamiz
            application.email = request.user.email

            application.save()

            # Email jo'natish
            send_mail(
                subject="Sizning arizangiz qabul qilindi",
                message=f"Assalomu alaykum, {application.name}!\n\n"
                        f"Sizning '{job.title}' lavozimi uchun arizangiz muvaffaqiyatli qabul qilindi.\n"
                        f"Tez orada mutaxassislarimiz siz bilan bog‘lanishadi.\n\nRahmat!",
                from_email="jurabeksodiqovich@gmail.com",
                recipient_list=[application.email],
                fail_silently=False,
            )

            messages.success(request, "Sizning arizangiz muvaffaqiyatli qabul qilindi!")
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobApplicationForm()

    return render(request, 'jobs/apply.html', {'form': form, 'job': job})


def update_application_status(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Pending", "Reviewed", "Accepted", "Rejected"]:
            application.status = new_status
            application.save()

            # Foydalanuvchiga email yuborish
            send_mail(
                subject=f"Sizning arizangiz yangilandi - {application.status}",
                message=f"Assalomu alaykum, {application.name}!\n\n"
                        f"Sizning \"{application.job.title}\" lavozimi uchun arizangiz "
                        f"yangilandi. Hozirgi status: {application.status}.\n\n"
                        f"Rahmat!",
                from_email="jurabeksodiqovich@gmail.com",
                recipient_list=[application.email],
                fail_silently=False,
            )

            messages.success(request, "Application status updated and email sent.")
            return redirect("application_detail", application_id=application.id)

    return redirect("application_detail", application_id=application.id)
@login_required
def job_applications_list(request):
    """
    Employers and Admins can see job applications only for their job postings.
    """
    if not request.user.is_staff and request.user.role != "employer":
        return HttpResponse("Unauthorized", status=403)

    # Faqat ushbu employer yaratgan vakansiyalarni olish
    employer_jobs = Job.objects.filter(posted_by=request.user)


    # Ushbu employerning vakansiyalari uchun topshirilgan applicationlarni olish
    applications = JobApplication.objects.filter(job__in=employer_jobs).order_by('-applied_at')

    return render(request, 'jobs/job_applications_list.html', {'applications': applications})


# ===============================
# AI RESUME REVIEW
# ===============================

def extract_text_from_resume(resume_file):
    """
    Extracts text from a resume file (PDF, DOCX, TXT).
    """
    if not resume_file:
        return None

    file_extension = resume_file.name.split(".")[-1].lower()

    try:
        if file_extension == "pdf":
            with pdfplumber.open(io.BytesIO(resume_file.read())) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        elif file_extension in ["doc", "docx"]:
            doc = docx.Document(io.BytesIO(resume_file.read()))
            return "\n".join([para.text for para in doc.paragraphs])
        elif file_extension == "txt":
            return resume_file.read().decode("utf-8")
    except Exception as e:
        return f"Error reading resume file: {str(e)}"

    return None



def ai_resume_review(request, application_id):
    """
    Handles AI resume review and generates interview questions based on job requirements.
    """
    application = get_object_or_404(JobApplication, id=application_id)
    job = application.job  # Application ga bog'langan Job ni olish

    if not application.resume:
        return render(request, 'jobs/ai_review.html', {
            'application': application,
            'ai_result': "Error: No resume uploaded.",
            'questions': []
        })

    # Extract resume text
    resume_text = extract_text_from_resume(application.resume)
    
    # Get job requirements from the related Job object
    job_requirements = job.requirements if job else "No job requirements provided."

    # Generate AI analysis and questions based on resume and job requirements
    questions = analyze_resume(resume_text, job_requirements)

    # Save AI review result
    application.ai_review = "\n".join(questions)
    application.save()

    return render(request, 'jobs/ai_review.html', {
        'application': application,
        'ai_result': "AI review completed successfully.",
        'questions': questions
    })
def ai_resume_screening(application_id):
    """AI orqali resume screening o'tkazish va natijani yangilash."""
    application = get_object_or_404(JobApplication, id=application_id)

    # AI resume screening (GPT yoki Transformers orqali)
    ai_generated_questions = generate_ai_questions(application.job_seeker.resume_text)  # AI savollar yaratish

    if ai_generated_questions:
        application.generated_questions = ai_generated_questions
        application.status = "Shortlisted"  # Statusni yangilaymiz (bu email yuboradi)
        application.save()

    return {"message": "AI screening completed successfully!"}
    
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('job_seeker_dashboard')  # Redirect to dashboard
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'jobs/update_profile.html', {'form': form})

@login_required
def upload_resume(request):
    """
    Resume upload view.
    """
    if request.method == "POST":
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user  # Assign the uploaded resume to the logged-in user
            resume.save()

            messages.success(request, "Resume uploaded successfully!")
            return redirect("job_seeker_dashboard")

    else:
        form = ResumeForm()

    return render(request, "jobs/upload_resume.html", {"form": form})


# password change form
@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, "Your password has been changed successfully!")
            return redirect("edit_profile")  # Redirect back to profile edit page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "login/change_password1.html", {"form": form})
# end password change form

# job create start
@login_required
def job_create(request):
    # Faqat employer yoki adminlarga ruxsat
    if request.user.role not in ["employer", "admin"]:
        return HttpResponse("Sizga vakansiya yaratishga ruxsat berilmagan.", status=403)

    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user  # Kim joylagan bo‘lsa, avtomatik qo‘shiladi
            job.is_active = True  # Vakansiya avtomatik "active" bo‘ladi
            job.save()
            messages.success(request, "Vakansiya muvaffaqiyatli yaratildi!")
            return redirect("job_list")  # Job list sahifasiga qaytish
        else:
            messages.error(request, "Xatolik yuz berdi. Ma'lumotlarni to'g'ri kiriting.")

    else:
        form = JobForm()

    return render(request, "jobs/job_create.html", {"form": form})


@login_required
def change_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.user != job.posted_by and not request.user.is_admin:
        messages.error(request, "Siz bu vakansiyani tahrirlash huquqiga ega emassiz.")
        return redirect("job_list")

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["active", "archived"]:
            job.status = new_status
            job.save()
            messages.success(request, f"Vakansiya holati {new_status.upper()} ga o‘zgartirildi!")
        else:
            messages.error(request, "Noto‘g‘ri status tanlandi.")

    return redirect("job_list")




# TEST DASHBORD FOR JOB SEEKERS


# TEST DASHBOARD END

# send invitation link 
def send_questions_view(request, application_id):
    """Employer "Send Questions" tugmachasini bossagina email yuboriladi."""
    application = get_object_or_404(JobApplication, id=application_id)

    if application.status == "Shortlisted":  # Faqatgina screeningdan o'tganlarga
        job_seeker_email = application.job_seeker.email
        questions = application.generated_questions  # AI-generated savollar

        send_interview_questions_email(job_seeker_email, questions)
        return HttpResponse("Email sent successfully.")

    return HttpResponse("This application has not passed screening.")
    
@login_required
def test_dashboard(request):
    # Kandidatga tegishli applicationni olish
    application = get_object_or_404(JobApplication, applicant=request.user, shortlisted=True)

    # ✅ Deadline tekshirish
    if application.test_deadline and now() > application.test_deadline:
        return render(request, "jobs/test_expired.html")

    if request.method == "POST":
        question_index = int(request.POST.get("question_index"))
        answer = request.POST.get("answer")

        # ✅ Javobni saqlash
        application.test_answers[str(question_index)] = answer
        application.save()

        # ✅ Keyingi savolga o'tish
        if question_index + 1 < len(application.ai_generated_questions):
            return redirect(f"/test-dashboard/?question={question_index + 1}")
        else:
            return redirect("test_complete")  # Test tugaganda boshqa sahifaga yo'naltiramiz

    # ❓ Hozirgi savolni olish
    question_index = int(request.GET.get("question", 0))
    question = application.ai_generated_questions[question_index]

    return render(request, "jobs/test_dashboard.html", {"question": question, "question_index": question_index})

# AI-generated savollar yaratish uchun funksiya
def generate_interview_questions(job_title, resume_text):
    prompt = f"""
    I am hiring for a {job_title}. Based on the following resume text, generate 5 interview questions:
    {resume_text}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    questions = response["choices"][0]["message"]["content"].split("\n")
    return [q for q in questions if q.strip()]  # Bo'sh stringlarni chiqarib tashlaymiz

@login_required
def shortlist_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)
    
    print("Current user:", request.user)  # Debugging
    print("Job employer:", application.job.employer)  # Debugging
    print("Is Staff:", request.user.is_staff)  # Debugging

    if not request.user.is_staff and request.user != application.job.employer:
        return JsonResponse({"error": "Sizga ruxsat yo'q!"}, status=403)

    # ✅ Shortlist statusini yangilash
    application.shortlisted = True

    # ✅ AI-generated interview questions
    resume_text = "Resume is attached but parsing not implemented."
    print("Generating AI questions for:", application.job.title)  # Debugging

    questions = generate_interview_questions(application.job.title, resume_text)
    
    if isinstance(questions, list):  # Convert to JSON if needed
        application.ai_generated_questions = json.dumps(questions)
    else:
        application.ai_generated_questions = questions  # If already string

    # ✅ Test uchun deadline (3 kun)
    application.test_deadline = now() + timedelta(days=3)

    # ✅ Save data
    application.save()
    print("Application updated successfully:", application.shortlisted)  # Debugging

    return JsonResponse({"success": "Applicant successfully shortlisted!"})

@login_required
def employer_test_results(request, application_id):
    # ✅ Employer faqat o'z ishlariga berilgan arizalarni ko'ra olishi kerak
    application = get_object_or_404(JobApplication, id=application_id, job__employer=request.user)

    # ✅ Kandidatning test javoblari
    test_answers = application.test_answers
    questions = application.ai_generated_questions

    # ✅ Har bir savol va javobni birga qaytarish
    question_answers = [{"question": q, "answer": test_answers.get(str(i), "No answer")} for i, q in enumerate(questions)]

    return render(request, "test/employer_test_results.html", {"application": application, "question_answers": question_answers}) 


# job create end
def home(request):
    return render(request, 'home.html')



