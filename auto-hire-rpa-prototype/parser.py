import re
import spacy

nlp = spacy.load("en_core_web_sm")

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s]{7,}\d)")

SKILL_KEYWORDS = [
    "python","java","c++","c#","javascript","react","node","flask","django",
    "sql","postgres","mysql","aws","azure","docker","kubernetes","nlp","ml","tensorflow","pytorch","scikit-learn"
]

def extract_skills(text):
    found = set()
    t = text.lower()
    for k in SKILL_KEYWORDS:
        if k in t:
            found.add(k)
    return list(found)

def parse_resume_text(text):
    doc = nlp(text)
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    skills = extract_skills(text)
    exp = None
    m = re.search(r"(\d+(\.\d+)?)\+?\s+(years|yrs)\b", text.lower())
    if m:
        try:
            exp = float(m.group(1))
        except:
            exp = None

    return {
        "name": name,
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "skills": skills,
        "experience_years": exp
    }
