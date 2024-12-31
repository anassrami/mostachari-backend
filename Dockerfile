############################
# Stage 1
############################
FROM python:3.8-slim as builder
WORKDIR /app

COPY requirements.txt .
RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app

############################
# Stage 2
############################
FROM nginx:alpine
RUN apk add --no-cache python3 py3-pip
COPY --from=builder /app /app
WORKDIR /app

# This line is CRITICAL:
ENV PATH="/app/venv/bin:$PATH"

COPY nginx/prod.nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

CMD uvicorn main:app --host 0.0.0.0 --port 8000 & \
    nginx -g 'daemon off;'
