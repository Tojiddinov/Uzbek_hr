import openai
from django.conf import settings
from django.core.mail import send_mail
from jobs.utils.resume_analysis import match_resume_to_job
from openai import OpenAIError 
# from .nlp_model import match_resume_to_job

# OpenAI API-ni boshlash
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_resume(resume_text, job_title, job_description):
    """
    Analyzes a resume and generates AI-based interview questions.

    Args:
        resume_text (str): The candidate's resume content.
        job_title (str): The title of the job being applied for.
        job_description (str): The job description.

    Returns:
        list: A list of interview questions or an error message.
    """
    if not resume_text or not job_title or not job_description:
        return ["Error: Resume, Job Title, or Job Description is missing."]

    try:
        # Match resume to job description and title
        match_score = match_resume_to_job(resume_text, job_title, job_description)

        # Determine the prompt based on match score
        if match_score < 0.5:
            prompt = f"""
            You are an AI HR assistant. The candidate's resume is not highly relevant to the job.
            Generate **10 general interview questions** to assess their adaptability.

            **Job Title:** {job_title}

            **Job Description:** {job_description}
            """
        else:
            prompt = f"""
            You are an AI HR assistant. Analyze the following **job requirements** and **resume**, 
            and generate **20 resume-specific interview questions** based on both:

            **Job Title:** {job_title}

            **Job Description:** {job_description}

            **Candidate's Resume:** {resume_text}
            """

        # OpenAI API call
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI HR assistant specializing in resume screening and interview question generation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )

        # Extract response content
        if response and response.choices:
            ai_content = response.choices[0].message['content'].strip()
            questions = [q.strip() for q in ai_content.split("\n") if q.strip()]
            return questions if questions else ["Error: No questions generated."]

        return ["Error: No response from OpenAI."]

    except openai.error.OpenAIError as e:
        return [f"OpenAI API Error: {str(e)}"]

    except Exception as e:
        return [f"Unexpected Error: {str(e)}"]


# def send_test_notification_email(user_email, job_title):
#     """
#     Nomzodga intervyu testiga taklif yuborish uchun email jo‘natish.

#     Args:
#         user_email (str): Nomzodning email manzili.
#         job_title (str): Ish lavozimi nomi.
#     """
#     subject = "AI-Generated Test Assigned for Your Job Application"
#     message = f"""
#     Dear Candidate,

#     Your resume has been reviewed, and an AI-generated test has been assigned to you for the position of {job_title}.
    
#     Please log in to your profile and complete the test within the next **3 days**.

#     Link to Test Dashboard: http://localhost:8000/dashboard/job_seeker/

#     Best Regards,  
#     UZBEK HR Team
#     """
#     sender_email = settings.EMAIL_HOST_USER
#     recipient_list = [user_email]

#     send_mail(subject, message, sender_email, recipient_list)

def send_test_notification_email(email, job_title):
    """
    Ish qidiruvchiga intervyu testiga taklif yuborish.
    """
    subject = "Interview Questions Ready"
    message = f"Dear Candidate,\n\nYour resume has been reviewed for the position '{job_title}'. " \
              f"Please visit your dashboard to answer AI-generated interview questions.\n\nBest regards,\nUzbek HR Team"

    send_mail(subject, message, 'jurabeksodiqovich@gmail.com', [email])
