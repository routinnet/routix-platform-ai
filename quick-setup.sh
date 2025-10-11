#!/bin/bash
# Routix Platform - Quick Setup Script
# This script automates the installation and setup of Routix Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

print_header "🎨 Routix Platform Quick Setup"
echo -e "${BLUE}This script will set up the Routix Platform for development.${NC}"
echo ""

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
    print_warning "Python version is $PYTHON_VERSION. Recommended: 3.11+"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [[ $NODE_VERSION -lt 18 ]]; then
    print_warning "Node.js version is $NODE_VERSION. Recommended: 18+"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_success "Prerequisites check completed"

# Setup Backend
print_header "🔧 Setting up Backend"

cd routix-backend

print_status "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Upgrading pip..."
pip install --upgrade pip --quiet

print_status "Installing Python dependencies..."
pip install -r requirements.txt --quiet
print_success "Python dependencies installed"

print_status "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # Generate secure keys
    SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
    JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -d '\n')
    
    # Update .env file with generated keys
    sed -i "s/your-super-secret-key-here/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-here/$JWT_SECRET_KEY/" .env
    
    print_success "Environment file created with secure keys"
else
    print_status "Environment file already exists"
fi

print_status "Testing backend imports..."
if python3 -c "
import sys
sys.path.insert(0, '$(pwd)')
from src.main import app
print('Backend imports successful')
" 2>/dev/null; then
    print_success "Backend setup completed successfully"
else
    print_error "Backend setup failed. Please check the logs above."
    exit 1
fi

cd ..

# Setup Frontend
print_header "🎨 Setting up Frontend"

cd routix-frontend

print_status "Installing Node.js dependencies..."
npm install --silent
print_success "Node.js dependencies installed"

print_status "Setting up environment variables..."
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    print_success "Frontend environment file created"
else
    print_status "Frontend environment file already exists"
fi

print_status "Testing frontend build..."
if npm run build > /dev/null 2>&1; then
    print_success "Frontend setup completed successfully"
else
    print_warning "Frontend build test failed, but setup is complete"
fi

cd ..

# Create startup scripts
print_header "📝 Creating startup scripts"

# Backend startup script
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd routix-backend
source venv/bin/activate
export PYTHONPATH=$(pwd)
echo "🚀 Starting Routix Backend on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Frontend startup script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd routix-frontend
echo "🎨 Starting Routix Frontend on http://localhost:3000"
npm run dev
EOF

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh

print_success "Startup scripts created"

# Create development script
cat > start-dev.sh << 'EOF'
#!/bin/bash
# Start both backend and frontend in development mode

echo "🚀 Starting Routix Platform in Development Mode"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting Backend..."
cd routix-backend
source venv/bin/activate
export PYTHONPATH=$(pwd)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend in background
echo "🎨 Starting Frontend..."
cd routix-frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Routix Platform is starting up!"
echo ""
echo "📍 Access Points:"
echo "   🎨 Frontend:  http://localhost:3000"
echo "   🔧 Backend:   http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "👤 Test User:"
echo "   📧 Email:     test@routix.com"
echo "   🔑 Password:  pass123"
echo "   💰 Credits:   100"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
EOF

chmod +x start-dev.sh

print_success "Development script created"

# Final instructions
print_header "🎉 Setup Complete!"

echo -e "${GREEN}Routix Platform has been successfully set up!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""
echo -e "${YELLOW}1. Configure API Keys (Optional but recommended):${NC}"
echo "   Edit routix-backend/.env and add your API keys:"
echo "   - OPENAI_API_KEY=sk-your-openai-key"
echo "   - GEMINI_API_KEY=your-gemini-key"
echo "   - MIDJOURNEY_API_KEY=your-midjourney-key"
echo ""
echo -e "${YELLOW}2. Start the application:${NC}"
echo ""
echo -e "${GREEN}   Option A - Start both services together:${NC}"
echo "   ./start-dev.sh"
echo ""
echo -e "${GREEN}   Option B - Start services separately:${NC}"
echo "   Terminal 1: ./start-backend.sh"
echo "   Terminal 2: ./start-frontend.sh"
echo ""
echo -e "${YELLOW}3. Access the application:${NC}"
echo "   🎨 Frontend:  http://localhost:3000"
echo "   🔧 Backend:   http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}4. Test login:${NC}"
echo "   📧 Email:     test@routix.com"
echo "   🔑 Password:  pass123"
echo ""
echo -e "${BLUE}📚 Additional Resources:${NC}"
echo "   📖 Full Documentation: ./INSTALLATION.md"
echo "   🐛 Troubleshooting:    ./docs/troubleshooting.md"
echo "   🚀 Deployment Guide:   ./DEPLOYMENT_GUIDE.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
