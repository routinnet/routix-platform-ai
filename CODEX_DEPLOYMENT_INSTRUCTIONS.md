# 🤖 Codex Deployment Instructions for Routix Platform

## 📋 Overview

This document provides specific instructions for deploying the Routix Platform using Codex on your VPS server.

## 🎯 Quick Deployment Commands for Codex

### Step 1: Clone Repository
```bash
git clone https://github.com/routinnet/routix-platform-ai.git
cd routix-platform-ai
```

### Step 2: Run Quick Setup
```bash
chmod +x quick-setup.sh
./quick-setup.sh
```

### Step 3: Configure API Keys (Important!)
```bash
# Edit backend environment file
nano routix-backend/.env

# Add your API keys:
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
MIDJOURNEY_API_KEY=your-midjourney-key-here
```

### Step 4: Start the Platform
```bash
# Option A: Start both services together
./start-dev.sh

# Option B: Start services separately (in different terminals)
./start-backend.sh    # Terminal 1
./start-frontend.sh   # Terminal 2
```

## 🌐 Access Points

After successful deployment:
- **Frontend**: http://your-server-ip:3000
- **Backend API**: http://your-server-ip:8000
- **API Documentation**: http://your-server-ip:8000/docs

## 👤 Test User Credentials

- **Email**: test@routix.com
- **Password**: pass123
- **Credits**: 100

## 🔧 Production Deployment (Recommended for VPS)

### Using Docker (Recommended)
```bash
# Install Docker and Docker Compose if not installed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up --build -d
```

### Manual Production Setup
```bash
# Backend (Terminal 1)
cd routix-backend
source venv/bin/activate
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend (Terminal 2)
cd routix-frontend
npm run build
npm start
```

## 🔐 Security Configuration

### 1. Generate Secure Keys
```bash
# Generate SECRET_KEY
openssl rand -base64 64

# Generate JWT_SECRET_KEY
openssl rand -base64 64
```

### 2. Update Environment Variables
```bash
# Backend (.env)
SECRET_KEY=your-generated-secret-key
JWT_SECRET_KEY=your-generated-jwt-key
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=http://your-domain.com,https://your-domain.com
```

### 3. Firewall Configuration
```bash
# Allow necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw allow 3000  # Frontend (development)
sudo ufw allow 8000  # Backend (development)
sudo ufw enable
```

## 🌍 Domain Configuration

### 1. Point Domain to Server
- Update your domain's A record to point to your VPS IP
- Wait for DNS propagation (up to 24 hours)

### 2. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 3. Nginx Configuration
```bash
# Install Nginx
sudo apt install nginx

# Use the provided nginx configuration
sudo cp nginx/nginx.conf /etc/nginx/sites-available/routix
sudo ln -s /etc/nginx/sites-available/routix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check Docker services
docker-compose -f docker-compose.prod.yml ps
```

### Logs
```bash
# Backend logs
tail -f logs/backend.log

# Docker logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Updates
```bash
# Pull latest changes
git pull origin master

# Restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🆘 Troubleshooting

### Common Issues

1. **Backend won't start**
   ```bash
   # Check Python path
   export PYTHONPATH=$(pwd)/routix-backend
   
   # Install missing dependencies
   pip install -r routix-backend/requirements.txt
   ```

2. **Frontend can't connect**
   ```bash
   # Check API URL in .env.local
   NEXT_PUBLIC_API_URL=http://your-server-ip:8000
   ```

3. **Database issues**
   ```bash
   # Check database file
   ls -la routix-backend/routix.db
   
   # Reset database (if needed)
   rm routix-backend/routix.db
   # Restart backend to recreate
   ```

4. **Port conflicts**
   ```bash
   # Check what's using ports
   sudo netstat -tulpn | grep :8000
   sudo netstat -tulpn | grep :3000
   
   # Kill processes if needed
   sudo pkill -f uvicorn
   sudo pkill -f node
   ```

## 📝 Environment Variables Reference

### Required API Keys
- **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys
- **GEMINI_API_KEY**: Get from https://makersuite.google.com/app/apikey
- **MIDJOURNEY_API_KEY**: Get from your Midjourney API provider

### Optional Configuration
- **SMTP_SERVER**: For email notifications
- **REDIS_URL**: For caching (optional)
- **SENTRY_DSN**: For error tracking (optional)

## 🎯 Success Criteria

After deployment, verify:
- ✅ Backend API responds at `/health`
- ✅ Frontend loads without errors
- ✅ User can login with test credentials
- ✅ Chat interface is functional
- ✅ File upload works
- ✅ API documentation is accessible

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check firewall and port configurations

## 🚀 Next Steps

After successful deployment:
1. **Configure real AI API keys** for full functionality
2. **Set up monitoring** and alerting
3. **Configure backups** for the database
4. **Set up CI/CD** for automated deployments
5. **Add custom domain** and SSL certificate

---

**🎉 Your Routix Platform should now be running successfully on your VPS!**

Access it at: http://your-server-ip:3000
