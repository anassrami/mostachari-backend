FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y nginx

COPY . /app
COPY nginx/prod.nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443 8000

CMD service nginx start && python -m uvicorn main:app --host 0.0.0.0 --port 8000