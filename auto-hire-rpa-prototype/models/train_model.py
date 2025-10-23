from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

def train_sample(X_texts, y_labels, out_path="models/simple_model.joblib"):
    vect = TfidfVectorizer(stop_words="english", max_features=5000)
    X = vect.fit_transform(X_texts)
    clf = LogisticRegression(max_iter=500)
    clf.fit(X, y_labels)
    joblib.dump({"vect": vect, "clf": clf}, out_path)
    return out_path
