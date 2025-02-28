from sentence_transformers import SentenceTransformer, util
import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline


# NLP modelni yuklash
model = SentenceTransformer("all-MiniLM-L6-v2")

def match_resume_to_job(resume_text, job_description):
    """
    Resume va Job Description o‘xshashligini hisoblaydi.
    """
    if not resume_text or not job_description:
        return 0  # No match

    # Resume va job description embeddinglarini olish
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)

    # O‘xshashlikni hisoblash
    similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding).item()
    return similarity_score  # 0 dan 1 gacha natija


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
    documents = [resume_text, job_title + " " + job_description]
    processed_docs = [preprocess_text(doc) for doc in documents]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    return similarity_score

def generate_interview_questions(resume_text, job_title, job_description):
    prompt = f"""
    Given the following job title and description:
    Job Title: {job_title}
    Job Description: {job_description}
    
    And the following candidate's resume:
    {resume_text}
    
    Generate 15 technical interview questions relevant to this position, along with 5 general (psychological/IQ) questions.
    """
    
    question_generator = pipeline("text-generation", model="gpt-3.5-turbo")
    questions = question_generator(prompt, max_length=300, do_sample=True)
    return questions[0]['generated_text']

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