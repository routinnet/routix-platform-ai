# 🎨 Routix Platform - AI-Powered Thumbnail Generator

A modern, AI-powered thumbnail generation platform with a ChatGPT-like interface for content creators.

## 🌟 Features

- **🤖 AI-Powered Generation**: Multiple AI algorithms (OpenAI DALL-E, Google Gemini, Midjourney)
- **💬 Chat Interface**: ChatGPT-like conversational UI for natural interaction
- **📁 File Management**: Upload and manage reference images with drag-and-drop
- **💳 Credit System**: Flexible monetization with credit-based usage
- **🔐 Authentication**: Secure user management with JWT
- **📊 Analytics**: Usage tracking and insights
- **🎨 Modern UI**: Beautiful, responsive design with Tailwind CSS
- **⚡ Real-time Updates**: Live generation progress tracking

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - Modern, fast, async API
- **Frontend**: Next.js 14 (React/TypeScript) - Server-side rendering
- **Database**: SQLite (development) / PostgreSQL (production)
- **Cache**: Redis for session management
- **AI Integration**: OpenAI, Google Gemini, Midjourney APIs
- **Deployment**: Docker & Docker Compose ready

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/routix-platform.git
cd routix-platform
```

### 2. Backend Setup

```bash
cd routix-backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start backend server
PYTHONPATH=$(pwd) uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup

```bash
cd routix-frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start frontend server
npm run dev
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Test Login

Use the pre-configured test user:
- **Email**: test@routix.com
- **Password**: pass123
- **Credits**: 100

## Project Structure

```
routix-platform/
├── routix-backend/          # FastAPI Backend
│   ├── src/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configuration and database
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   ├── uploads/            # File uploads directory
│   └── requirements.txt    # Python dependencies
├── routix-frontend/         # Next.js Frontend
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utility libraries
│   │   └── types/          # TypeScript type definitions
│   └── package.json        # Node.js dependencies
└── README.md               # This file
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Production database
- **SQLAlchemy** - ORM with async support
- **Redis** - Caching and session storage
- **JWT** - Authentication
- **WebSocket** - Real-time communication

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI components
- **Zustand** - State management
- **React Query** - Server state management
- **Socket.io** - Real-time communication

### AI Integration
- **OpenAI GPT-4** - Conversation analysis
- **Google Gemini** - Image analysis and generation
- **Midjourney API** - High-quality thumbnail generation
- **Stable Diffusion** - Cost-effective generation

## Features

- 🤖 **AI-Powered Generation** - Multiple AI algorithms for thumbnail creation
- 💬 **Chat Interface** - ChatGPT-like conversational UI
- 📁 **File Management** - Upload and manage reference images
- 💳 **Credit System** - Flexible monetization with credit-based usage
- 🔐 **Authentication** - Secure user management
- 📊 **Analytics** - Usage tracking and insights
- 🎨 **Template Database** - Curated collection of high-quality templates
- ⚡ **Real-time Updates** - Live generation progress tracking

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd routix-backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd routix-frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. Start development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/routix
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
MIDJOURNEY_API_KEY=your-midjourney-key
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Development Workflow

1. **Backend Development**: Use FastAPI's automatic documentation at `http://localhost:8000/docs`
2. **Frontend Development**: Next.js hot reload for instant feedback
3. **Database Changes**: Create migrations with `alembic revision --autogenerate -m "description"`
4. **Testing**: Run tests with `pytest` (backend) and `npm test` (frontend)

## API Documentation

The backend provides interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

### Production Deployment
1. Build frontend: `npm run build`
2. Set production environment variables
3. Use Docker Compose for orchestration
4. Configure Nginx as reverse proxy
5. Set up SSL certificates

### Development Deployment
- Use Docker Compose for local development
- Includes PostgreSQL and Redis containers
- Hot reload for both frontend and backend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions, please contact the development team.
