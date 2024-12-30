############################
# Stage 1: Build the app
############################
FROM python:3.8-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

############################
# Stage 2: NGINX + Python
############################
FROM nginx:alpine

# Install Python so we can run Uvicorn here
RUN apk add --no-cache python3 py3-pip

# Copy code from builder
COPY --from=builder /app /app
WORKDIR /app

# Reinstall dependencies in the final image
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy your NGINX config
COPY nginx/prod.nginx.conf /etc/nginx/nginx.conf

# Expose HTTP + HTTPS
EXPOSE 80 443

# Run Uvicorn in background, then keep NGINX in foreground
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & \
    nginx -g 'daemon off;'
