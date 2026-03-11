# Scan2Home — Production Deployment Guide

This guide covers the process of deploying the Scan2Home platform to the new VPS (`187.77.179.167`) with automated CI/CD using GitHub Actions.

## 1. Initial VPS Setup

SSH into your new VPS:

```bash
ssh root@187.77.179.167
```

### 1.1 Update & Basic Hardening

```bash
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

Add the public key (content of `id_deploy.pub`) to `~/.ssh/authorized_keys` on the new VPS (`187.77.179.167`).

### 2.2 GitHub Secrets

Update these secrets in your GitHub repo (**Settings > Secrets and variables > Actions**):

- `VPS_IP`: `187.77.179.167`
- `VPS_USER`: `root`
- `SSH_PRIVATE_KEY`: Content of `id_deploy` private key file.
- `BACKEND_ENV`: The exact content of your updated `.env.prod` file (it now contains the Hostinger SMTP settings and `scan2home.co.uk` domain).
- `AI_ENV`: Production environment variables for the AI server.

---

## 3. Manual Nginx & SSL Setup

### 3.1 Nginx Configuration

Create a configuration at `/etc/nginx/sites-available/scan2home`:

```nginx
server {
    listen 80;
    server_name scan2home.co.uk www.scan2home.co.uk api.scan2home.co.uk admwin.scan2home.co.uk app.scan2home.co.uk;

    location /static/ {
        alias /root/app/scan2home/staticfiles/;
    }

    location /media/ {
        alias /root/app/scan2home/media/;
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

Enable Nginx, test, and restart:

```bash
ln -s /etc/nginx/sites-available/scan2home /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 3.2 SSL with Certbot

Generate SSL certificates for all your domains routing to this VPS:

```bash
certbot --nginx -d scan2home.co.uk -d www.scan2home.co.uk -d api.scan2home.co.uk -d admwin.scan2home.co.uk -d app.scan2home.co.uk
```

---

## 4. Fix Media Folder Permissions for Nginx

After your first GitHub Actions deployment (when the directories are created), you must fix the permissions so Nginx can read the media and static files:

```bash
chmod 755 /root/app/scan2home/
chmod 755 /root/app/scan2home/media/
chmod 755 /root/app/scan2home/staticfiles/
chmod -R 755 /root/app/scan2home/media/
chmod -R 755 /root/app/scan2home/staticfiles/
```

---

## 5. Maintenance

- **Check Logs**: `make prod-logs` (run in `~/app/scan2home`)
- **Docker Status**: `docker compose -f docker-compose.prod.yml ps`
