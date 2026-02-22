# Scan2Home — Production Deployment Guide (Direct VPS Build)

This guide covers the process of deploying the Scan2Home platform directly to a VPS with automated CI/CD using GitHub Actions.

## 1. Initial VPS Setup

### 1.1 Update & Basic Hardening
```bash
ssh root@31.97.205.65
apt update && apt upgrade -y
apt install -y ufw curl git nginx certbot python3-certbot-nginx
ufw allow 'Nginx Full'
ufw allow 22
ufw enable
```

### 1.2 Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
apt install -y docker-compose-plugin
```

---

## 2. GitHub & CI/CD Setup

### 2.1 SSH Key for Deployment
On your local machine, generate a key for GitHub Actions:
```bash
ssh-keygen -t ed25519 -C "deploy@github-actions" -f ./id_deploy
```
Add the public key (content of `id_deploy.pub`) to `~/.ssh/authorized_keys` on the VPS.

### 2.2 GitHub Secrets
Add these secrets to your GitHub repo (**Settings > Secrets and variables > Actions**):
- `VPS_IP`: Your VPS IP address.
- `VPS_USER`: Your VPS username (e.g., `root`).
- `SSH_PRIVATE_KEY`: Content of `id_deploy` private key file.
- `BACKEND_ENV`: Production environment variables for the backend.
- `AI_ENV`: Production environment variables for the AI server.

---

## 3. Manual Nginx & SSL Setup

### 3.1 Nginx Configuration
Create a configuration at `/etc/nginx/sites-available/scan2home`:
```nginx
server {
    listen 80;
    server_name scan2home.selimreza.dev api.selimreza.dev;

    location /static/ {
        alias /app/scan2home/staticfiles/;
    }

    location /media/ {
        alias /app/scan2home/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable and test:
```bash
ln -s /etc/nginx/sites-available/scan2home /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 3.2 SSL with Certbot
```bash
certbot --nginx -d scan2home.selimreza.dev -d api.selimreza.dev
```

---

## 4. Maintenance
- **Check Logs**: `make prod-logs` (run in `/app/scan2home`)
- **Live Traffic**: `make prod-dlogs`
- **Docker Status**: `docker compose -f docker-compose.prod.yml ps`
