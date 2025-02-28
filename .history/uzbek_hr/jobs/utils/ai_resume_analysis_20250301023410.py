import openai
from django.conf import settings
from django.core.mail import send_mail
from jobs.utils.resume_analysis import match_resume_to_job
from openai import OpenAIError 
# from .nlp_model import match_resume_to_job

# OpenAI API-ni boshlash
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_resume(resume_text, job_title, job_description):  # Add job_title here
    if not resume_text or not job_description or not job_title:
        return ["Error: Resume, Job Title, or Job Description is empty."]

    try:
        match_score = match_resume_to_job(resume_text, job_title, job_description)  # Now it's defined

        if match_score < 0.5:
            prompt = f"""
            You are an AI HR assistant. The candidate's resume is not highly relevant to the job.
            Generate **10 general interview questions** to assess their adaptability.

            **Job Title:**
            {job_title}

            **Job Description:**
            {job_description}
            """
        else:
            prompt = f"""
            You are an AI HR assistant. Analyze the following **job requirements** and **resume**, 
            and generate **20 resume-specific interview questions** based on both:

            **Job Title:**
            {job_title}

            **Job Description:**
            {job_description}

            **Candidate's Resume:**
            {resume_text}
            """

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI HR assistant specializing in resume screening and interview question generation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )

        if completion.choices:
            questions = completion.choices[0].message['content'].strip().split("\n")
            return [q.strip() for q in questions if q.strip()]

        return ["Error: No response from OpenAI."]
    
    except OpenAIError as e:
        return [f"OpenAI API Error: {str(e)}"]
    
    except Exception as e:
        return [f"Unexpected Error: {str(e)}"]



def send_test_notification_email(user_email, job_title):
    """
    Nomzodga intervyu testiga taklif yuborish uchun email jo‘natish.

    Args:
        user_email (str): Nomzodning email manzili.
        job_title (str): Ish lavozimi nomi.
    """
    subject = "AI-Generated Test Assigned for Your Job Application"
    message = f"""
    Dear Candidate,

    Your resume has been reviewed, and an AI-generated test has been assigned to you for the position of {job_title}.
    
    Please log in to your profile and complete the test within the next **3 days**.

    Link to Test Dashboard: http://localhost:8000/dashboard/job_seeker/

    Best Regards,  
    UZBEK HR Team
    """
    sender_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]

    send_mail(subject, message, sender_email, recipient_list)

    
