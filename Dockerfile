FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Run migrations and collect static files
RUN python manage.py migrate --noinput && python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "obviously.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
