# Project documentation
# To Run App:
─ uvicorn main:app --reload


## Setting Up Nginx as a Reverse Proxy with SSL for FastAPI

This section explains how we set up Nginx as a reverse proxy with SSL termination using Let's Encrypt for the FastAPI application running in Docker.

### Prerequisites

- Ubuntu server
- Domain name pointing to your server
- Docker and Docker Compose installed
- FastAPI application already set up and running

### Steps

1. **Install Certbot and Nginx:**

   ```sh
   sudo apt update
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Configure Nginx as a Reverse Proxy:**

   Create an Nginx configuration file for your FastAPI application:

   ```sh
   sudo nano /etc/nginx/sites-available/api
   ```

   Add the following configuration, replacing `api.dev.mostachari.ma` with your actual subdomain:

   ```nginx
   server {
       listen 80;
       server_name api.dev.mostachari.ma;

       location / {
           proxy_pass http://localhost:8000;  # Proxy to the internal port 8000
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   Enable the configuration and test Nginx:

   ```sh
   sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
   sudo nginx -t
   ```

   Restart Nginx to apply the changes:

   ```sh
   sudo systemctl restart nginx
   ```

3. **Obtain an SSL Certificate with Certbot:**

   Run Certbot to obtain and install the SSL certificate:

   ```sh
   sudo certbot --nginx -d api.dev.mostachari.ma
   ```

   Follow the prompts to complete the certificate issuance and automatic configuration of Nginx.

4. **Docker-Compose Configuration:**

   Ensure your `docker-compose.yml` maps the container’s port 80 to an internal port (e.g., 8000):

   ```yaml
   version: '3.8'

   services:
     web:
       build: .
       command: uvicorn main:app --host 0.0.0.0 --port 80
       ports:
         - "8000:80"
   ```

5. **Deploy FastAPI Application:**

   Build and start your Docker container:

   ```sh
   docker-compose up -d
   ```

6. **Automatic SSL Renewal:**

   Certbot sets up a cron job to renew the SSL certificates automatically. Verify the cron job:

   ```sh
   sudo systemctl status certbot.timer
   ```

By following these steps, your FastAPI application will be securely accessible via `https://api.dev.mostachari.com`.

For any issues or further assistance, please refer to the detailed setup instructions.
