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

