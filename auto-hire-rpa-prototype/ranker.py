from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def score_candidate_for_job(resume_text, job_description):
    docs = [job_description, resume_text]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf = vectorizer.fit_transform(docs)
    sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return float(sim * 100.0)
