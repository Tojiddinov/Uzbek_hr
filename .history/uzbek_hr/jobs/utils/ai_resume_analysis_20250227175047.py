import openai
from django.conf import settings
from django.core.mail import send_mail


# Directly set API key (Not recommended for production)
# api_key = "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"

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_resume(resume_text, job_description):
    if not resume_text or not job_description:
        return ["Error: Resume or Job Requirements is empty."]

    # Resume-job matching scoreni olish
    match_score = match_resume_to_job(resume_text, job_description)

    if match_score < 0.5:  # Agar juda kam moslik bo‘lsa, umumiy savollar chiqarish
        prompt = f"""
        You are an AI HR assistant. The candidate's resume is not highly relevant to the job.
        Generate 10 general interview questions to assess their adaptability.

        **Job Description:**
        {job_description}
        """
    else:  # Resume mos bo‘lsa, resume asosida savollar yaratish
        prompt = f"""
        You are an AI HR assistant. Analyze the following **job requirements** and **resume**, and generate 20 **resume-specific interview questions** based on both:

        **Job Description:**
        {job_description}

        **Candidate's Resume:**
        {resume_text}

        Consider the candidate's skills, experience, and education while creating questions.
        """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
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
#
# Example usage
# resume_text = "Python developer with 3 years of experience in Django, REST APIs, and cloud deployment."
# questions = analyze_resume(resume_text)
# for q in questions:
#     print(q)
