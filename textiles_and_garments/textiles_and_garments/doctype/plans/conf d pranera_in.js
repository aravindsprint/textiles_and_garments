server {
    listen 80;
    server_name pranera.in;

    location / {
        proxy_pass http://127.0.0.1:8080;  # If your Ionic/Node app runs locally
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name pranera.in www.pranera.in;

    ssl_certificate /etc/letsencrypt/live/pranera.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pranera.in/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;  # If your Ionic/Node app runs locally
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}


# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name pranera.in www.pranera.in;
    return 301 https://$host$request_uri;
}

# HTTPS with proxy to Node/Ionic backend
server {
    listen 443 ssl;
    server_name pranera.in www.pranera.in;

    ssl_certificate /etc/letsencrypt/live/pranera.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pranera.in/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}