import openai
from django.conf import settings
from django.conf import settings

# Directly set API key (Not recommended for production)
# api_key = "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"

# Initialize OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

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
def send_interview_questions_email(job_seeker_email, questions):
    """AI-generated interview questionsni job seekerga email yuborish."""
    subject = "Your AI-Generated Interview Questions"
    message = "Congratulations! You have passed resume screening.\n\n"
    message += "Please find your AI-generated interview questions below:\n\n"

    for idx, question in enumerate(questions, start=1):
        message += f"{idx}. {question}\n"

    message += "\nPlease answer these questions within 3 days.\n\nBest regards,\nUzbek HR Team"

    send_mail(subject, message, settings.EMAIL_HOST_USER, [job_seeker_email])
#
# Example usage
# resume_text = "Python developer with 3 years of experience in Django, REST APIs, and cloud deployment."
# questions = analyze_resume(resume_text)
# for q in questions:
#     print(q)
