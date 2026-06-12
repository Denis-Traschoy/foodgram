
FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN mkdir -p /app/media /backend_static && \
    python manage.py collectstatic --noinput

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 backend.wsgi"]