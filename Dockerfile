# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir \
    sentence-transformers \
    PyMuPDF \
    numpy \
    nltk \
    scikit-learn

# Download NLTK punkt tokenizer
RUN python -c "import nltk; nltk.download('punkt')"

ENTRYPOINT ["python", "main.py"]
