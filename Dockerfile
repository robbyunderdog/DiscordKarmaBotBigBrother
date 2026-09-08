FROM python:3.12-slim

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV NLTK_DATA=/usr/local/share/nltk_data
RUN python -c "import nltk; nltk.download('vader_lexicon', download_dir='$NLTK_DATA')"

COPY BigBrother.py bigbrotherdatabase.py ./

RUN chown -R app:app /app

USER app

CMD ["python", "BigBrother.py"]
