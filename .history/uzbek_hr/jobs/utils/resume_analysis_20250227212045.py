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

