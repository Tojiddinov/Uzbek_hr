from sentence_transformers import SentenceTransformer, util
import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import torch
from sentence_transformers import SentenceTransformer
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)



# NLP modelni yuklash
model = SentenceTransformer("all-MiniLM-L6-v2")

def match_resume_to_job(resume_text, job_description):
    """
    Resume va Job Description o‘xshashligini hisoblaydi.
    :param resume_text: Nomzodning resume matni
    :param job_description: Ish tavsifi
    :return: O‘xshashlik darajasi (0 dan 1 gacha)
    """
    if not resume_text.strip() or not job_description.strip():
        return 0.0  # Bo‘sh bo‘lsa, 0 qaytarish

    # Resume va Job Description uchun embeddinglarni olish
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)

    # O‘xshashlikni hisoblash (cosine similarity)
    similarity_score = torch.nn.functional.cosine_similarity(
        resume_embedding.unsqueeze(0), job_embedding.unsqueeze(0)
    ).item()

    return round(similarity_score, 2)


# Ensure necessary NLTK data is available
nltk.download("punkt")
nltk.download("stopwords")

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    words = word_tokenize(text)
    words = [word for word in words if word not in stopwords.words("english")]
    return " ".join(words)

def match_resume_to_job(resume_text, job_title, job_description):
    """
    Compare the given resume text with job title and job description
    using TF-IDF and return a similarity score.

    :param resume_text: Extracted text from the candidate's resume.
    :param job_title: The job title for the position.
    :param job_description: The full job description.
    :return: A similarity score (0 to 1).
    """
    if not resume_text.strip() or not job_title.strip() or not job_description.strip():
        return 0.0  # Return 0 similarity if any input is missing.

    # Combine job title and job description for better matching
    job_text = f"{job_title} {job_description}"

    # Use TF-IDF to vectorize the resume and job text
    vectorizer = TfidfVectorizer(stop_words='english')

    try:
        vectors = vectorizer.fit_transform([resume_text, job_text])
        # Compute cosine similarity
        similarity_score = cosine_similarity(vectors[0].toarray(), vectors[1].toarray())[0][0]
    except Exception as e:
        return 0.0  # Agar xatolik bo‘lsa, 0 qaytarsin

    return round(similarity_score, 2)  # Natijani yaxlitlash (0.00 - 1.00)

ddef generate_interview_questions(resume_text, job_title, job_description):
    prompt = f"""
    You are an AI HR assistant. Your task is to generate interview questions based on the given job requirements and resume.

    **Job Title:** {job_title}
    **Job Description:** {job_description}
    
    **Candidate's Resume:** 
    {resume_text}
    
    Please generate:
    - 15 technical interview questions relevant to this position.
    - 5 general interview questions (psychological/IQ-related).
    Provide clear, well-structured questions.
    """

    # Call OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI HR assistant specializing in resume screening and interview question generation."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800
    )

    # Extract response text
    if completion.choices:
        questions = completion.choices[0].message.content.strip().split("\n")
        return [q.strip() for q in questions if q.strip()]

    return ["Error: No response from OpenAI."]

# Example Usage
resume_text = "Experienced Python developer skilled in AI and data analysis."
job_title = "Machine Learning Engineer"
job_description = "Seeking an ML Engineer with Python and AI expertise."

questions = generate_interview_questions(resume_text, job_title, job_description)

for q in questions:
    print(q)
# Example Usage
if __name__ == "__main__":
    resume_text = "Experienced software engineer skilled in Python, Django, and AI-driven solutions."
    job_title = "AI Engineer"
    job_description = "Looking for an AI engineer with experience in NLP and deep learning frameworks."
    
    match_score = match_resume_to_job(resume_text, job_title, job_description)
    print(f"Match Score: {match_score:.2f}")
    
    if match_score > 0.5:  # Only generate questions if there's a reasonable match
        questions = generate_interview_questions(resume_text, job_title, job_description)
        print("\nGenerated Interview Questions:")
        print(questions)