import re
import nltk
import string
import numpy as np
from sklearn.feature_extraction.text import Tfpip install scikit-learnidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure NLTK stopwords and tokenizer are downloaded
nltk.download('stopwords')
nltk.download('punkt')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def preprocess_text(text):
    """Preprocess text by converting to lowercase, removing punctuation, and filtering stopwords."""
    text = text.lower()
    text = re.sub(f"[{string.punctuation}]", "", text)
    words = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

def match_resume_to_job(resume_text, job_title, job_requirements):
    """Calculate similarity score between resume and job details using TF-IDF and cosine similarity."""
    documents = [resume_text, job_title, job_requirements]
    processed_docs = [preprocess_text(doc) for doc in documents]
    
    # TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    
    # Compute cosine similarity (resume vs job title & requirements)
    similarity_scores = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()
    job_title_score, job_req_score = similarity_scores
    
    # Weighted Score (50% job title, 50% job requirements)
    final_score = (job_title_score * 0.5) + (job_req_score * 0.5)
    
    return round(final_score * 100, 2)  # Convert to percentage and round off

# Example Usage
if __name__ == "__main__":
    resume_text = "Experienced Python developer with knowledge of Django, REST APIs, and PostgreSQL."
    job_title = "Python Developer"
    job_requirements = "Looking for a Python developer skilled in Django, REST frameworks, and databases."
    
    score = match_resume_to_job(resume_text, job_title, job_requirements)
    print(f"Resume Matching Score: {score}%")
