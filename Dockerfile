# Use a lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies file first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Create the SQLite database if it doesn't exist
RUN python manage.py migrate --noinput

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 8000

# Start the Django app using Gunicorn
CMD ["gunicorn", "obviously.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3"]
