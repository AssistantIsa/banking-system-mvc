FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install Flask==2.3.3
COPY . .
CMD ["python", "main.py"]
