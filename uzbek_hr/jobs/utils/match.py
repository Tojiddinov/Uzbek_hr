import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NLTK resurslarini yuklash (agar oldin yuklanmagan bo'lsa)
nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    """Matnni tozalash va tokenizatsiya qilish."""
    text = text.lower()  # Kichik harflarga o'tkazish
    text = text.translate(str.maketrans('', '', string.punctuation))  # Punktuatsiyani olib tashlash
    words = word_tokenize(text)  # So'zlarga ajratish
    words = [word for word in words if word not in stopwords.words('english')]  # Stopwords ni olib tashlash
    return ' '.join(words)

def match_resume_to_job(resume_text, job_title, job_description):
    """Rezyume va ish tavsifini solishtirib, o'xshashlik ballini qaytaradi."""
    documents = [resume_text, job_title + ' ' + job_description]
    processed_docs = [preprocess_text(doc) for doc in documents]
    
    # TF-IDF vektorizatsiya
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    
    # Kosinus o'xshashlikni hisoblash
    similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]
    return round(similarity_score, 2)  # Natijani 2 xonali kasr shaklida qaytarish

# Test qilish
if __name__ == "__main__":
    resume = "Experienced software developer with expertise in Python and Django."
    job_title = "Python Developer"
    job_description = "Looking for a developer proficient in Python and Django to build web applications."
    
    score = match_resume_to_job(resume, job_title, job_description)
    print(f"Resume-job match score: {score}")