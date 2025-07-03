FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads output

# Use PORT environment variable with fallback to 5000
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} app:app