# Routix Platform Deployment Guide

This guide provides comprehensive instructions for deploying the Routix AI-powered thumbnail generation platform to a VPS.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS or newer (recommended)
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 20GB SSD
- **CPU**: 2+ cores recommended
- **Network**: Public IP address with ports 80, 443 accessible

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenSSL
- Curl

## 🚀 Quick Deployment

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply Docker group changes
```

### 2. Clone and Deploy

```bash
# Clone the repository
git clone <your-repository-url> routix-platform
cd routix-platform

# Run deployment script
./deploy.sh
```

## 🔧 Manual Deployment

### 1. Environment Configuration

Create `.env` file:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password_here

# Security
SECRET_KEY=your_super_secret_key_64_characters_long

# AI APIs
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=AIzaSyCdkIoj8cjtMkOyM8rnJLe4J6FjV0AXq-0

# Domain
DOMAIN=routix.com
API_DOMAIN=api.routix.com
```

### 2. SSL Certificates

For production, obtain SSL certificates from Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d routix.com -d www.routix.com -d api.routix.com

# Copy certificates
sudo cp /etc/letsencrypt/live/routix.com/fullchain.pem nginx/ssl/routix.com.crt
sudo cp /etc/letsencrypt/live/routix.com/privkey.pem nginx/ssl/routix.com.key
```

### 3. Build and Start Services

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🔒 Security Configuration

### 1. Firewall Setup

```bash
# Install UFW
sudo apt install ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban Protection

```bash
# Install Fail2Ban
sudo apt install fail2ban

# Configure Fail2Ban for Nginx
sudo tee /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl restart fail2ban
```

### 3. Regular Updates

```bash
# Create update script
cat > update.sh << 'EOF'
#!/bin/bash
cd /path/to/routix-platform
git pull
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --build
docker system prune -f
EOF

chmod +x update.sh

# Add to crontab for weekly updates
echo "0 2 * * 0 /path/to/routix-platform/update.sh" | sudo crontab -
```

## 📊 Monitoring and Maintenance

### 1. Log Management

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Log rotation
sudo tee /etc/logrotate.d/docker << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### 2. Database Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/routix"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U routix_user routix_db > $BACKUP_DIR/db_backup_$DATE.sql

# Uploads backup
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz uploads/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Schedule daily backups
echo "0 3 * * * /path/to/routix-platform/backup.sh" | crontab -
```

### 3. Health Monitoring

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

# Check if services are running
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend API is down, restarting..."
    docker-compose -f docker-compose.prod.yml restart backend
fi

if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend is down, restarting..."
    docker-compose -f docker-compose.prod.yml restart frontend
fi
EOF

chmod +x health_check.sh

# Run health check every 5 minutes
echo "*/5 * * * * /path/to/routix-platform/health_check.sh" | crontab -
```

## 🌐 Domain Configuration

### 1. DNS Settings

Configure your domain DNS with the following records:

```
A     routix.com          YOUR_SERVER_IP
A     www.routix.com      YOUR_SERVER_IP
A     api.routix.com      YOUR_SERVER_IP
CNAME *.routix.com        routix.com
```

### 2. CDN Setup (Optional)

For better performance, consider using a CDN like Cloudflare:

1. Sign up for Cloudflare
2. Add your domain
3. Update nameservers
4. Enable SSL/TLS encryption
5. Configure caching rules

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443

# Stop conflicting services
sudo systemctl stop apache2
sudo systemctl stop nginx
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Reset database
docker-compose -f docker-compose.prod.yml down
docker volume rm routix-platform_postgres_data
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. SSL Certificate Issues
```bash
# Renew Let's Encrypt certificates
sudo certbot renew

# Copy renewed certificates
sudo cp /etc/letsencrypt/live/routix.com/fullchain.pem nginx/ssl/routix.com.crt
sudo cp /etc/letsencrypt/live/routix.com/privkey.pem nginx/ssl/routix.com.key

# Restart Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Connect to PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U routix_user -d routix_db

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations(user_id);
CREATE INDEX IF NOT EXISTS idx_generations_status ON generations(status);
```

#### 2. Redis Configuration
```bash
# Optimize Redis memory usage
docker-compose -f docker-compose.prod.yml exec redis redis-cli CONFIG SET maxmemory 256mb
docker-compose -f docker-compose.prod.yml exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 📞 Support

For deployment issues or questions:

1. Check the logs first: `docker-compose -f docker-compose.prod.yml logs`
2. Verify all services are running: `docker-compose -f docker-compose.prod.yml ps`
3. Check system resources: `htop` or `docker stats`
4. Review this guide for common solutions

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks

1. **Weekly**: Update system packages and Docker images
2. **Daily**: Check logs for errors and monitor disk space
3. **Monthly**: Review security logs and update SSL certificates
4. **Quarterly**: Performance review and optimization

### Update Process

```bash
# 1. Backup current state
./backup.sh

# 2. Pull latest changes
git pull origin main

# 3. Update Docker images
docker-compose -f docker-compose.prod.yml pull

# 4. Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Clean up old images
docker system prune -f
```

---

**Note**: This deployment guide assumes a production environment. For development, use the regular `docker-compose.yml` file instead of `docker-compose.prod.yml`.
