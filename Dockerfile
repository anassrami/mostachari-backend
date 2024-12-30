############################
# Stage 1: Build with Python
############################
FROM python:3.8-slim as builder

WORKDIR /app
COPY requirements.txt .

# Create a virtual env inside /app/venv
RUN python3 -m venv /app/venv

# Activate the venv and install all packages
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy your actual project code into /app
COPY . /app


############################
# Stage 2: NGINX + Python
############################
FROM nginx:alpine

# We need python3 so we can run Uvicorn
RUN apk add --no-cache python3 py3-pip

# Copy everything (including venv) from builder
COPY --from=builder /app /app
WORKDIR /app

# Let the container know we have a venv, and want to use it by default
ENV PATH="/app/venv/bin:$PATH"

# Copy your custom NGINX config
COPY nginx/prod.nginx.conf /etc/nginx/nginx.conf

# Expose HTTP + HTTPS
EXPOSE 80 443

# Run Uvicorn in the background, then keep NGINX in the foreground
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & \
    nginx -g 'daemon off;'
