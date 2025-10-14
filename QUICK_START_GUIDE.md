# 🚀 راهنمای سریع راه‌اندازی - Routix Platform

**آخرین به‌روزرسانی**: 14 اکتبر 2025

---

## ⚡ نصب سریع (5 دقیقه)

### پیش‌نیازها
```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Git
git --version
```

---

## 🔧 راه‌اندازی Backend

### 1. نصب Dependencies

```bash
cd routix-backend

# ایجاد virtual environment
python -m venv venv

# فعال‌سازی (Linux/Mac)
source venv/bin/activate

# فعال‌سازی (Windows)
venv\Scripts\activate

# نصب وابستگی‌ها
pip install -r requirements.txt

# نصب ابزارهای توسعه (اختیاری)
pip install -r requirements-dev.txt
```

### 2. تنظیم Environment Variables

```bash
# کپی فایل example
cp .env.example .env

# تولید SECRET_KEY امن
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env

# ویرایش .env و تنظیم سایر متغیرها
nano .env  # یا vi، vim، یا هر editor دیگر
```

**حداقل تنظیمات ضروری در `.env`:**
```bash
# MUST HAVE
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
DATABASE_URL=sqlite+aiosqlite:///./routix.db
ENVIRONMENT=development

# برای استفاده از AI (اختیاری در مرحله اول)
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=your-key-here
```

### 3. راه‌اندازی Database

```bash
# ایجاد جداول و seed data
python -c "
import asyncio
from src.core.database import init_db
asyncio.run(init_db())
"

# یا اگر main.py شامل init_db است:
# Backend خودکار database را راه‌اندازی می‌کند
```

### 4. اجرای Backend

```bash
# روش 1: استفاده از uvicorn
PYTHONPATH=$(pwd) uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# روش 2: اگر در main.py تعریف شده
python -m src.main

# روش 3: با hot-reload کامل
watchmedo auto-restart --directory=./src --pattern="*.py" --recursive \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**بررسی Backend:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- ReDoc: http://localhost:8000/redoc

---

## 🎨 راه‌اندازی Frontend

### 1. نصب Dependencies

```bash
cd routix-frontend

# نصب با npm
npm install

# یا با yarn
yarn install

# یا با pnpm
pnpm install
```

### 2. تنظیم Environment Variables

```bash
# کپی فایل example (اگر وجود دارد)
cp .env.example .env.local

# یا ایجاد فایل جدید
nano .env.local
```

**محتوای `.env.local`:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. اجرای Frontend

```bash
# Development mode
npm run dev

# یا
yarn dev

# یا
pnpm dev
```

**بررسی Frontend:**
- صفحه اصلی: http://localhost:3000
- صفحه ورود: http://localhost:3000/auth/login
- چت: http://localhost:3000/chat

---

## 🧪 تست کردن سیستم

### 1. ایجاد کاربر تست

روش A: از API مستقیماً
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@routix.com",
    "username": "testuser",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
```

روش B: از Frontend
1. برو به http://localhost:3000/auth/register
2. فرم را پر کن
3. ثبت‌نام کن

### 2. ورود به سیستم

```bash
# از API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@routix.com",
    "password": "Test123!@#"
  }'

# از Frontend: برو به /auth/login
```

### 3. تست تولید تامبنیل

1. ورود به چت: http://localhost:3000/chat
2. کلیک روی "Start New Chat"
3. ارسال پیام: "Create a gaming thumbnail with red and black colors"
4. منتظر پاسخ AI بمان

---

## 🐛 رفع مشکلات رایج

### مشکل 1: Backend اجرا نمی‌شود

**خطا: "No module named 'src'"**
```bash
# حل: PYTHONPATH را تنظیم کن
export PYTHONPATH=/path/to/routix-backend
# یا
PYTHONPATH=$(pwd) uvicorn src.main:app --reload
```

**خطا: "SECRET_KEY must be set"**
```bash
# حل: SECRET_KEY تولید و تنظیم کن
python -c "import secrets; print(secrets.token_urlsafe(32))"
# کپی خروجی و اضافه به .env
echo "SECRET_KEY=<copied-key>" >> .env
```

**خطا: "Could not import module 'asyncpg'"**
```bash
# حل: وابستگی‌های جدید را نصب کن
pip install --upgrade -r requirements.txt
```

### مشکل 2: Frontend اجرا نمی‌شود

**خطا: "Cannot connect to backend"**
- بررسی کن Backend روی port 8000 در حال اجراست
- بررسی کن `.env.local` تنظیم شده
- بررسی کن CORS در backend فعال است

**خطا: "Module not found"**
```bash
# حل: node_modules را دوباره نصب کن
rm -rf node_modules package-lock.json
npm install
```

### مشکل 3: Chat Interface در حالت "Starting..." می‌ماند

**دلایل احتمالی:**
1. WebSocket هنوز پیاده‌سازی نشده (feature در حال توسعه)
2. Token منقضی شده - logout و login مجدد
3. Backend response نمی‌دهد - چک کردن console logs

**Workaround موقت:**
- صبر کنید تا polling کار کند (5 ثانیه)
- صفحه را refresh کنید
- با تیم توسعه هماهنگ کنید برای پیاده‌سازی WebSocket

### مشکل 4: Database Errors

**خطا: "table already exists"**
```bash
# حل: پاک کردن database و ایجاد مجدد
rm routix.db
python -c "import asyncio; from src.core.database import init_db; asyncio.run(init_db())"
```

**خطا: "no such table"**
```bash
# حل: اجرای init_db
python -c "import asyncio; from src.core.database import init_db; asyncio.run(init_db())"
```

---

## 📦 نصب با Docker (اختیاری)

### Development با Docker Compose

```bash
# از روت پروژه
docker-compose up --build

# در background
docker-compose up -d --build

# مشاهده logs
docker-compose logs -f

# متوقف کردن
docker-compose down
```

### Production با Docker Compose

```bash
# استفاده از production config
docker-compose -f docker-compose.prod.yml up -d --build

# با custom .env
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

---

## 🔐 تولید SECRET_KEY امن

### روش‌های مختلف:

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32

# urandom (Linux/Mac)
head -c 32 /dev/urandom | base64

# PowerShell (Windows)
[Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Maximum 256}))
```

---

## 📊 مانیتورینگ و Logs

### Backend Logs

```bash
# با uvicorn
PYTHONPATH=$(pwd) uvicorn src.main:app --log-level debug

# در Docker
docker-compose logs -f backend

# فقط خطاها
docker-compose logs -f backend | grep ERROR
```

### Frontend Logs

```bash
# Development console
# در مرورگر: F12 > Console

# در terminal
npm run dev

# در Docker
docker-compose logs -f frontend
```

### Database Queries (Debug)

در `src/core/database.py`:
```python
engine = create_async_engine(
    database_url,
    echo=True,  # نمایش تمام queries
    future=True
)
```

---

## 🧹 پاکسازی و Reset

### پاکسازی کامل Backend

```bash
cd routix-backend

# حذف virtual environment
rm -rf venv

# حذف database
rm -f routix.db

# حذف cache
rm -rf __pycache__ src/__pycache__ src/**/__pycache__
rm -rf .pytest_cache

# حذف uploads
rm -rf uploads
```

### پاکسازی کامل Frontend

```bash
cd routix-frontend

# حذف node_modules
rm -rf node_modules

# حذف build files
rm -rf .next

# حذف cache
rm -rf .turbo
```

### نصب مجدد از صفر

```bash
# Backend
cd routix-backend
python -m venv venv
source venv/bin/activate  # یا venv\Scripts\activate در Windows
pip install -r requirements.txt

# Frontend
cd routix-frontend
npm install

# راه‌اندازی مجدد
# Terminal 1: Backend
cd routix-backend && PYTHONPATH=$(pwd) uvicorn src.main:app --reload

# Terminal 2: Frontend
cd routix-frontend && npm run dev
```

---

## 🎯 Checklist راه‌اندازی موفق

پس از راه‌اندازی، این موارد را چک کنید:

### Backend ✅
- [ ] Backend روی http://localhost:8000 اجرا می‌شود
- [ ] `/docs` صفحه Swagger را نمایش می‌دهد
- [ ] `/health` status "healthy" برمی‌گرداند
- [ ] Database ایجاد شده و tables موجودند
- [ ] Algorithms در database seed شده‌اند

### Frontend ✅
- [ ] Frontend روی http://localhost:3000 اجرا می‌شود
- [ ] Landing page به درستی لود می‌شود
- [ ] صفحه login/register کار می‌کند
- [ ] می‌توانید register و login کنید
- [ ] Dashboard و chat accessible هستند

### Integration ✅
- [ ] Frontend می‌تواند به Backend متصل شود
- [ ] CORS errors وجود ندارد
- [ ] می‌توانید login کنید و token دریافت کنید
- [ ] API calls موفقیت‌آمیز هستند

### Optional (AI Features) 🎨
- [ ] OPENAI_API_KEY تنظیم شده
- [ ] GEMINI_API_KEY تنظیم شده
- [ ] تولید تامبنیل کار می‌کند

---

## 📞 دریافت کمک

اگر با مشکلی مواجه شدید:

1. **چک کردن Logs:**
   - Backend: Console که uvicorn را اجرا کردید
   - Frontend: Browser console (F12)
   - Database: تنظیم `echo=True` در database engine

2. **جستجو در Docs:**
   - `DEEP_ANALYSIS_REPORT.md` - راهکارهای تفصیلی
   - `README.md` - اطلاعات کلی پروژه
   - `IMPROVEMENTS_SUMMARY.md` - تغییرات اخیر

3. **تماس با تیم:**
   - ایجاد Issue در GitHub
   - تماس با تیم توسعه
   - بررسی existing issues

---

## 🎉 شروع توسعه

حالا که سیستم راه‌اندازی شد:

1. **Backend Development:**
   ```bash
   cd routix-backend
   # کد بنویس، hot-reload اتوماتیک است
   ```

2. **Frontend Development:**
   ```bash
   cd routix-frontend
   # کد بنویس، Next.js اتوماتیک reload می‌کند
   ```

3. **Testing:**
   ```bash
   # Backend tests
   cd routix-backend
   pytest tests/ -v

   # Frontend tests
   cd routix-frontend
   npm run test
   ```

4. **بررسی راهکارهای بهبود:**
   - خواندن `DEEP_ANALYSIS_REPORT.md`
   - انتخاب یک feature از roadmap
   - شروع پیاده‌سازی

---

**موفق باشید! 🚀**

اگر سوالی داشتید، به مستندات مراجعه کنید یا با تیم در تماس باشید.
