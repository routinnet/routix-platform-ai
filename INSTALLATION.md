# 📦 Routix Platform - Installation & Deployment Guide

This guide provides comprehensive instructions for installing and deploying the Routix Platform on various environments.

## 🎯 Quick Installation (Recommended)

### For Development

```bash
# Clone repository
git clone https://github.com/yourusername/routix-platform.git
cd routix-platform

# Run quick setup script
chmod +x quick-setup.sh
./quick-setup.sh
```

### For Production (VPS/Server)

```bash
# Clone repository
git clone https://github.com/yourusername/routix-platform.git
cd routix-platform

# Run production deployment
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Manual Installation

### Prerequisites

#### System Requirements
- **OS**: Ubuntu 20.04+ (recommended), macOS, or Windows with WSL2
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 10GB free space
- **CPU**: 2+ cores recommended

#### Software Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher
- **Git**: Latest version
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for containerized deployment)

### Step 1: System Preparation

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Git
sudo apt install git -y

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install Node.js 18
brew install node@18

# Install Git
brew install git

# Install Docker (optional)
brew install --cask docker
```

#### Windows (WSL2)
```bash
# Install WSL2 and Ubuntu
wsl --install -d Ubuntu

# Follow Ubuntu instructions above within WSL2
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/routix-platform.git
cd routix-platform

# Verify structure
ls -la
```

### Step 3: Backend Setup

```bash
# Navigate to backend directory
cd routix-backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit environment file (see Configuration section below)
nano .env  # or your preferred editor
```

### Step 4: Frontend Setup

```bash
# Navigate to frontend directory (in new terminal)
cd routix-frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit environment file
nano .env.local  # or your preferred editor
```

### Step 5: Database Setup

#### SQLite (Development - Default)
```bash
# No additional setup required
# Database file will be created automatically
```

#### PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE routix_db;
CREATE USER routix_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE routix_db TO routix_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://routix_user:your_secure_password@localhost:5432/routix_db
```

#### Redis (Optional - for caching)
```bash
# Install Redis
sudo apt install redis-server -y

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

## ⚙️ Configuration

### Backend Configuration (.env)

```bash
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./routix.db  # SQLite (development)
# DATABASE_URL=postgresql://user:pass@localhost:5432/routix_db  # PostgreSQL (production)

# Security Keys (Generate strong keys!)
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-minimum-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Service APIs (Required for full functionality)
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
MIDJOURNEY_API_KEY=your-midjourney-api-key-here

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp,gif,bmp,tiff

# Application Settings
DEBUG=True  # Set to False in production
ENVIRONMENT=development  # Set to production in production
LOG_LEVEL=INFO

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend Configuration (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Application Settings
NEXT_PUBLIC_APP_NAME=Routix
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=development

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_FILE_UPLOAD=true

# Upload Settings
NEXT_PUBLIC_MAX_FILE_SIZE=50MB
NEXT_PUBLIC_ALLOWED_FILE_TYPES=jpg,jpeg,png,webp,gif
```

### Generating Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -base64 64

# Generate JWT_SECRET_KEY
openssl rand -base64 64

# Generate database password
openssl rand -base64 32
```

## 🚀 Running the Application

### Development Mode

#### Terminal 1 - Backend
```bash
cd routix-backend
source venv/bin/activate  # Activate virtual environment
PYTHONPATH=$(pwd) uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Frontend
```bash
cd routix-frontend
npm run dev
```

### Production Mode

#### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose -f docker-compose.prod.yml up --build -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Manual Production Setup
```bash
# Backend
cd routix-backend
source venv/bin/activate
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd routix-frontend
npm run build
npm start
```

## 🌐 Access Points

After successful installation:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc

### Test User Credentials

- **Email**: test@routix.com
- **Password**: pass123
- **Credits**: 100

## 🔍 Verification & Testing

### Backend Health Check
```bash
# Test backend is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","message":"Routix API is running"}
```

### Frontend Health Check
```bash
# Test frontend is running
curl http://localhost:3000

# Should return HTML content
```

### API Authentication Test
```bash
# Test user login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@routix.com","password":"pass123"}'

# Should return access token
```

### Database Test
```bash
# Test database connection
curl http://localhost:8000/api/v1/algorithms

# Should return list of available algorithms
```

## 🐳 Docker Deployment

### Development with Docker
```bash
# Start development environment
docker-compose up --build

# Stop environment
docker-compose down

# View logs
docker-compose logs -f
```

### Production with Docker
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up --build -d

# Stop environment
docker-compose -f docker-compose.prod.yml down

# Update and restart
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check virtual environment
which python  # Should point to venv

# Check dependencies
pip list | grep fastapi

# Check PYTHONPATH
echo $PYTHONPATH

# Fix: Set PYTHONPATH
export PYTHONPATH=$(pwd)
```

#### Frontend won't start
```bash
# Check Node.js version
node --version  # Should be 18+

# Check npm version
npm --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Database connection issues
```bash
# Check database file (SQLite)
ls -la routix.db

# Check PostgreSQL service
sudo systemctl status postgresql

# Test database connection
psql "postgresql://routix_user:password@localhost:5432/routix_db"
```

#### API connection issues
```bash
# Check CORS settings
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/health

# Check firewall
sudo ufw status

# Check ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
```

### Performance Issues

#### Backend Performance
```bash
# Check memory usage
ps aux | grep uvicorn

# Check database performance
sqlite3 routix.db ".schema"

# Enable query logging
# Set DEBUG=True in .env
```

#### Frontend Performance
```bash
# Check bundle size
npm run build
npm run analyze  # If configured

# Check memory usage
ps aux | grep node
```

## 📊 Monitoring

### Application Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs (in development)
# Check browser console

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### System Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check network connections
netstat -tulpn
```

## 🔄 Updates & Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Update backend dependencies
cd routix-backend
pip install -r requirements.txt

# Update frontend dependencies
cd routix-frontend
npm install

# Restart services
# (Follow running instructions above)
```

### Database Maintenance
```bash
# Backup SQLite database
cp routix.db routix.db.backup

# Backup PostgreSQL database
pg_dump routix_db > routix_backup.sql

# Restore PostgreSQL database
psql routix_db < routix_backup.sql
```

## 🆘 Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review logs** for error messages
3. **Check GitHub Issues** for known problems
4. **Contact support** for additional help

### Support Channels

- **GitHub Issues**: [Report bugs and request features](https://github.com/yourusername/routix-platform/issues)
- **Documentation**: [Full documentation](./docs/)
- **Community**: [Join our community](https://discord.gg/routix)

---

**Installation complete! 🎉**

Your Routix Platform should now be running and ready for use. Visit http://localhost:3000 to get started!
