FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY requirements.txt .
COPY app.py .
COPY templates/ templates/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p uploads output

# Set environment variable
ENV PORT=5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]