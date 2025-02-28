import re
import nltk
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nltk.download('punkt', download_dir='/path/to/nltk_data')

# Ensure NLTK stopwords are downloaded
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def preprocess_text(text):
    """Simple text preprocessing: lowercase, remove punctuation, and stopwords."""
    text = text.lower()
    text = re.sub(f"[{string.punctuation}]", "", text)
    words = word_tokenize(text)
    words = [word for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

def match_resume_to_job(resume_text, job_title, job_requirements):
    """Calculates similarity score between resume and job requirements using TF-IDF."""
    documents = [resume_text, job_title, job_requirements]
    processed_docs = [preprocess_text(doc) for doc in documents]
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    
    # Compute cosine similarity (resume vs job)
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()
    
    job_title_score = similarity_score[0]
    job_req_score = similarity_score[1]
    
    # Weighted Score (50% job title, 50% job requirements)
    final_score = (job_title_score * 0.5) + (job_req_score * 0.5)
    
    return final_score * 100  # Convert to percentage

# Example Usage
if __name__ == "__main__":
    resume_text = "Experienced Python developer with knowledge of Django, REST APIs, and PostgreSQL."
    job_title = "Python Developer"
    job_requirements = "Looking for a Python developer skilled in Django, REST frameworks, and databases."
    
    score = match_resume_to_job(resume_text, job_title, job_requirements)
    print(f"Resume Matching Score: {score:.2f}%")
