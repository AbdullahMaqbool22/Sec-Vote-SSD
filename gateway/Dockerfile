FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy gateway files
COPY . /app/gateway

WORKDIR /app/gateway

EXPOSE 8080

CMD ["python", "app.py"]
