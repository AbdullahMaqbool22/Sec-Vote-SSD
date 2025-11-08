FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY ../../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared directory
COPY ../../shared /app/shared

# Copy service files
COPY . /app/services/vote

WORKDIR /app/services/vote

EXPOSE 5000

CMD ["python", "app.py"]
