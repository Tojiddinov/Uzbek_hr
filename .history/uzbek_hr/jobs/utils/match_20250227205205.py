import nltk
nltk.data.path.append("C:/Users/Umar/nltk_data")
print("Processed Documents:", processed_docs)
print("TF-IDF Matrix Shape:", tfidf_matrix.shape)
print("Feature Names:", vectorizer.get_feature_names_out())
