FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# download small spaCy english model
RUN python -m spacy download en_core_web_sm

COPY . .

ENV FLASK_APP=app.py
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
