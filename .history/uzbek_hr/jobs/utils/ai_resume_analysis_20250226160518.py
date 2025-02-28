import openai
from django.conf import settings
from django.core.mail import send_mail

# OpenAI klientini to‘g‘ri ishlatish
client = openai.OpenAI()  

def analyze_resume(resume_text, job_description):
    if not resume_text or not job_description:
        return ["Error: Resume or Job Requirements is empty."]

    prompt = f"""
    You are an AI HR assistant. Analyze the following **job requirements** and **resume**, and generate 20 **relevant interview questions** based on both:

    **Job Description:**
    {job_description}

    **Candidate's Resume:**
    {resume_text}

    Provide the questions as a structured list.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Modelni o'zgartirmaslik kerak, agar 'gpt-4o-mini' ishlatilayotgan bo'lsa
            messages=[
                {"role": "system", "content": "You are an AI HR assistant specializing in resume screening and interview question generation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )

        if completion.choices:
            questions = completion.choices[0].message.content.strip().split("\n")
            return [q.strip() for q in questions if q.strip()]

        return ["Error: No response from OpenAI."]
    except openai.OpenAIError as e:
        return [f"OpenAI API Error: {str(e)}"]
    except Exception as e:
        return [f"Unexpected Error: {str(e)}"]

def send_test_notification_email(user_email, job_title):
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
