FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y sudo && apt-get install -y dmidecode && apt-get install -y lshw && rm -rf /var/lib/apt/lists/*

COPY projecthack/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY projecthack/ .

ENV PYTHONUNMUFFERED = 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
