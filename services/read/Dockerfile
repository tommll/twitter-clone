FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the common module and service code
COPY common /app/common
COPY services/read /app/services/read

# Add the current directory to PYTHONPATH
ENV PYTHONPATH=/app

CMD ["python", "services/read/main.py"] 