# 🚀 راهنمای نصب و راه‌اندازی پلتفرم Routix

این راهنما به شما کمک می‌کند تا پلتفرم Routix را به صورت کامل نصب و راه‌اندازی کنید.

---

## 📋 پیش‌نیازها

### نرم‌افزارهای مورد نیاز:
- **Python 3.9+** (توصیه می‌شود: 3.11)
- **Node.js 18+** (توصیه می‌شود: 20 LTS)
- **PostgreSQL 14+** (برای production) یا SQLite (برای development)
- **Redis 6+** (اختیاری - برای caching)
- **Git**

### API Keys مورد نیاز:
- **OpenAI API Key** (الزامی - برای DALL-E 3 و GPT-4)
- **Google Gemini API Key** (اختیاری - برای تحلیل بهتر)
- **Stability AI API Key** (اختیاری - برای Stable Diffusion)
- **AWS Credentials** (اختیاری - برای S3 storage)

---

## 🔧 مرحله 1: دانلود و آماده‌سازی

```bash
# Clone repository
git clone https://github.com/your-repo/routix-platform.git
cd routix-platform
```

---

## 🐍 مرحله 2: راه‌اندازی Backend

### 2.1. ایجاد محیط مجازی و نصب وابستگی‌ها

```bash
cd routix-backend

# ایجاد virtual environment
python -m venv venv

# فعال‌سازی virtual environment
# در Linux/Mac:
source venv/bin/activate
# در Windows:
venv\Scripts\activate

# نصب dependencies
pip install -r requirements.txt

# نصب dependencies توسعه (اختیاری)
pip install -r requirements-dev.txt
```

### 2.2. پیکربندی Environment Variables

```bash
# کپی فایل نمونه
cp .env.example .env

# ویرایش فایل .env
nano .env
```

**مهم‌ترین تنظیمات:**

```bash
# 1. تولید SECRET_KEY امن
python -c "import secrets; print(secrets.token_urlsafe(32))"
# خروجی را در SECRET_KEY قرار دهید

# 2. افزودن OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# 3. تنظیم Database (برای development)
DATABASE_URL=sqlite:///./routix.db

# 4. تنظیم Database (برای production)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/routix
```

### 2.3. ایجاد Database

```bash
# اجرای migrations
alembic upgrade head

# اضافه کردن داده‌های اولیه (seed data)
python -c "from src.core.seed_data import seed_all; import asyncio; asyncio.run(seed_all())"
```

### 2.4. اجرای Backend Server

```bash
# Development mode
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# یا استفاده از اسکریپت
python -m src.main
```

سرور باید روی `http://localhost:8000` در دسترس باشد.

**تست API:**
```bash
# بررسی health check
curl http://localhost:8000/health

# مشاهده API Documentation
# باز کردن در مرورگر: http://localhost:8000/docs
```

---

## ⚛️ مرحله 3: راه‌اندازی Frontend

### 3.1. نصب Dependencies

```bash
cd ../routix-frontend

# نصب packages
npm install
# یا
yarn install
```

### 3.2. پیکربندی Environment Variables

```bash
# کپی فایل نمونه
cp .env.example .env.local

# ویرایش فایل
nano .env.local
```

**تنظیمات:**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=Routix
```

### 3.3. اجرای Frontend Server

```bash
# Development mode
npm run dev
# یا
yarn dev
```

فرانت‌اند روی `http://localhost:3000` در دسترس خواهد بود.

---

## 🧪 مرحله 4: تست سیستم

### 4.1. تست Backend

```bash
cd routix-backend

# اجرای تست‌ها
pytest tests/ -v

# با coverage
pytest tests/ --cov=src --cov-report=html
```

### 4.2. تست Frontend

```bash
cd routix-frontend

# Type check
npm run type-check

# Lint
npm run lint

# Build test
npm run build
```

### 4.3. تست Real-time Chat (WebSocket)

1. وارد `http://localhost:3000` شوید
2. ثبت‌نام یا ورود کنید
3. یک چت جدید ایجاد کنید
4. پیامی ارسال کنید
5. باید بلافاصله پاسخ AI را ببینید (بدون تاخیر)

---

## 🐳 مرحله 5: راه‌اندازی با Docker (Production)

### 5.1. ساخت و اجرا با Docker Compose

```bash
# در root directory پروژه
docker-compose -f docker-compose.prod.yml up --build
```

### 5.2. دسترسی به سرویس‌ها

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 🔑 مرحله 6: دریافت API Keys

### OpenAI API Key (الزامی)

1. به [platform.openai.com](https://platform.openai.com) بروید
2. ثبت‌نام یا ورود کنید
3. به بخش API Keys بروید
4. یک key جدید ایجاد کنید
5. اعتبار (credit) اضافه کنید

**هزینه تخمینی:**
- GPT-4: $0.03 per 1K tokens
- DALL-E 3 HD: $0.08 per image

### Google Gemini API Key (اختیاری)

1. به [makersuite.google.com](https://makersuite.google.com) بروید
2. API Key دریافت کنید
3. در `.env` قرار دهید

### Stability AI API Key (اختیاری)

1. به [platform.stability.ai](https://platform.stability.ai) بروید
2. ثبت‌نام کنید
3. API Key دریافت کنید
4. اعتبار خریداری کنید

---

## 🗄️ مرحله 7: پیکربندی Database (Production)

### PostgreSQL Setup

```bash
# نصب PostgreSQL
sudo apt install postgresql postgresql-contrib

# ایجاد database و user
sudo -u postgres psql

CREATE DATABASE routix;
CREATE USER routix_user WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE routix TO routix_user;
\q

# به‌روزرسانی .env
DATABASE_URL=postgresql+asyncpg://routix_user:strong_password_here@localhost:5432/routix
```

---

## ☁️ مرحله 8: پیکربندی Cloud Storage (اختیاری)

### Amazon S3 Setup

1. **ایجاد S3 Bucket:**
   - ورود به AWS Console
   - ایجاد bucket جدید (مثلاً `routix-thumbnails`)
   - تنظیم public access

2. **ایجاد IAM User:**
   - ایجاد user با دسترسی S3
   - ذخیره Access Key و Secret Key

3. **پیکربندی:**

```bash
# در .env
USE_S3=true
AWS_S3_BUCKET=routix-thumbnails
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

---

## 🚀 مرحله 9: Deploy Production

### با Nginx و Systemd

#### 9.1. Backend Service

```bash
# ایجاد systemd service
sudo nano /etc/systemd/system/routix-backend.service
```

```ini
[Unit]
Description=Routix Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/routix/routix-backend
Environment="PATH=/var/www/routix/routix-backend/venv/bin"
ExecStart=/var/www/routix/routix-backend/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# فعال‌سازی service
sudo systemctl enable routix-backend
sudo systemctl start routix-backend
sudo systemctl status routix-backend
```

#### 9.2. Frontend (Next.js)

```bash
cd routix-frontend

# Build production
npm run build

# ایجاد systemd service
sudo nano /etc/systemd/system/routix-frontend.service
```

```ini
[Unit]
Description=Routix Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/routix/routix-frontend
Environment="PATH=/usr/bin:/bin"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable routix-frontend
sudo systemctl start routix-frontend
```

#### 9.3. Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/routix
```

```nginx
# Backend API
upstream backend {
    server 127.0.0.1:8000;
}

# Frontend
upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://backend/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/v1/ws {
        proxy_pass http://backend/api/v1/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # Static files
    location /uploads {
        alias /var/www/routix/routix-backend/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# فعال‌سازی
sudo ln -s /etc/nginx/sites-available/routix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9.4. SSL با Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 📊 مرحله 10: Monitoring و Logging

### Sentry Integration

```bash
# در .env
SENTRY_DSN=your-sentry-dsn-here
```

### Logs

```bash
# مشاهده logs
sudo journalctl -u routix-backend -f
sudo journalctl -u routix-frontend -f
```

---

## 🔒 Security Checklist

- [ ] SECRET_KEY تصادفی و امن تنظیم شده
- [ ] Database password قوی
- [ ] API Keys در environment variables هستند (نه در کد)
- [ ] CORS به درستی تنظیم شده
- [ ] HTTPS فعال است (در production)
- [ ] Rate limiting فعال است
- [ ] File upload validation فعال است
- [ ] Error messages حساس را expose نمی‌کند

---

## ❓ رفع مشکلات رایج

### Backend شروع نمی‌شود

```bash
# بررسی logs
sudo journalctl -u routix-backend -n 50

# بررسی port
sudo lsof -i :8000

# بررسی dependencies
pip list
```

### WebSocket متصل نمی‌شود

1. بررسی CORS settings
2. بررسی Nginx configuration برای WebSocket
3. بررسی browser console برای errors
4. بررسی token validity

### Database connection error

```bash
# بررسی PostgreSQL
sudo systemctl status postgresql

# تست connection
psql -U routix_user -d routix -h localhost
```

### AI generation خطا می‌دهد

1. بررسی API keys
2. بررسی credit balance در OpenAI
3. بررسی network connectivity
4. بررسی logs برای error details

---

## 📞 پشتیبانی

در صورت مشکل:
- مستندات API: `http://localhost:8000/docs`
- GitHub Issues: [لینک repository]
- تیم توسعه: [ایمیل پشتیبانی]

---

## 🎉 تمام شد!

پلتفرم Routix شما آماده است! 

**مراحل بعدی:**
1. ایجاد اکانت admin
2. اضافه کردن templates
3. تست generation با الگوریتم‌های مختلف
4. مانیتورینگ performance
5. جمع‌آوری feedback کاربران

موفق باشید! 🚀
