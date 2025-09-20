FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "3"]