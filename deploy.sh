#!/bin/bash

# Routix Platform Deployment Script
# This script deploys the Routix platform to a VPS

set -e

echo "🚀 Starting Routix Platform Deployment..."

# Configuration
PROJECT_NAME="routix-platform"
DOMAIN="routix.com"
API_DOMAIN="api.routix.com"
DB_NAME="routix_db"
DB_USER="routix_user"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating environment file..."
    cat > .env << EOF
# Database
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Security
SECRET_KEY=$(openssl rand -base64 64)

# AI APIs
OPENAI_API_KEY=\${OPENAI_API_KEY}
GEMINI_API_KEY=AIzaSyCdkIoj8cjtMkOyM8rnJLe4J6FjV0AXq-0

# Domain
DOMAIN=${DOMAIN}
API_DOMAIN=${API_DOMAIN}
EOF
    print_success "Environment file created"
else
    print_status "Environment file already exists"
fi

# Create uploads directory
print_status "Creating uploads directory..."
mkdir -p uploads
chmod 755 uploads

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs
chmod 755 logs

# Generate SSL certificates (self-signed for development)
if [ ! -f nginx/ssl/routix.com.crt ]; then
    print_status "Generating SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/routix.com.key \
        -out nginx/ssl/routix.com.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
    print_success "SSL certificates generated"
else
    print_status "SSL certificates already exist"
fi

# Build and start services
print_status "Building Docker images..."
docker-compose -f docker-compose.prod.yml build

print_status "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U ${DB_USER} -d ${DB_NAME} > /dev/null 2>&1; then
    print_success "PostgreSQL is running"
else
    print_warning "PostgreSQL might not be ready yet"
fi

# Check Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is running"
else
    print_warning "Redis might not be ready yet"
fi

# Check Backend API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend API is running"
else
    print_warning "Backend API might not be ready yet"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is running"
else
    print_warning "Frontend might not be ready yet"
fi

# Display deployment information
echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📋 Service Information:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Database: PostgreSQL on port 5432"
echo "   Cache: Redis on port 6379"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "   Update services: docker-compose -f docker-compose.prod.yml pull && docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🔒 Security Notes:"
echo "   - Update SSL certificates for production use"
echo "   - Configure firewall rules"
echo "   - Set up regular backups"
echo "   - Monitor logs for security issues"
echo ""
echo "📚 Next Steps:"
echo "   1. Configure your domain DNS to point to this server"
echo "   2. Update SSL certificates with valid ones"
echo "   3. Set up monitoring and alerting"
echo "   4. Configure automated backups"
echo ""

print_success "Routix Platform is now running!"
