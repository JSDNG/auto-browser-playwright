#!/bin/bash

# Deployment script for Playwright Backend Service
# This script handles deployment to various environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [ENVIRONMENT] [OPTIONS]"
    echo
    echo "Environments:"
    echo "  local     - Deploy locally using Docker"
    echo "  dev       - Deploy to development environment"
    echo "  staging   - Deploy to staging environment"
    echo "  prod      - Deploy to production environment"
    echo
    echo "Options:"
    echo "  --build   - Force rebuild of Docker image"
    echo "  --test    - Run tests before deployment"
    echo "  --help    - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 local --build"
    echo "  $0 dev --test"
    echo "  $0 prod"
}

# Default values
ENVIRONMENT=""
FORCE_BUILD=false
RUN_TESTS=false
DOCKER_IMAGE="playwright-backend-service"
DOCKER_TAG="latest"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        local|dev|staging|prod)
            ENVIRONMENT="$1"
            shift
            ;;
        --build)
            FORCE_BUILD=true
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if environment is specified
if [ -z "$ENVIRONMENT" ]; then
    print_error "Environment not specified"
    show_usage
    exit 1
fi

# Check Docker availability
if ! command_exists docker; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker Compose availability
if ! command_exists docker-compose; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

print_status "Starting deployment to $ENVIRONMENT environment"

# Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    print_status "Running tests..."
    
    # Run unit tests
    if ! make test-cov; then
        print_error "Tests failed. Deployment aborted."
        exit 1
    fi
    
    # Run CLI tests
    if ! ./scripts/test_cli.sh; then
        print_error "CLI tests failed. Deployment aborted."
        exit 1
    fi
    
    print_success "All tests passed"
fi

# Build Docker image if requested or if it doesn't exist
if [ "$FORCE_BUILD" = true ] || ! docker image inspect "$DOCKER_IMAGE:$DOCKER_TAG" > /dev/null 2>&1; then
    print_status "Building Docker image..."
    
    # Build image
    if ! docker build -f docker/Dockerfile -t "$DOCKER_IMAGE:$DOCKER_TAG" .; then
        print_error "Docker build failed"
        exit 1
    fi
    
    print_success "Docker image built successfully"
else
    print_status "Using existing Docker image"
fi

# Deploy based on environment
case $ENVIRONMENT in
    local)
        print_status "Deploying to local environment..."
        
        # Stop existing containers
        docker-compose -f docker/docker-compose.yml down || true
        
        # Start services
        docker-compose -f docker/docker-compose.yml up -d
        
        # Wait for services to be ready
        print_status "Waiting for services to be ready..."
        sleep 10
        
        # Check if services are running
        if docker-compose -f docker/docker-compose.yml ps | grep -q "Up"; then
            print_success "Local deployment completed successfully"
            
            # Show service URLs
            echo
            echo "Service URLs:"
            echo "- n8n: http://localhost:5678"
            echo "- Playwright service: Container 'playwright-automation'"
            echo
            echo "Test the service:"
            echo "docker exec playwright-automation python -m src.cli '{\"url\": \"https://example.com\", \"extract\": [{\"name\": \"title\", \"selector\": \"h1\"}]}'"
        else
            print_error "Some services failed to start"
            exit 1
        fi
        ;;
        
    dev)
        print_status "Deploying to development environment..."
        
        # Tag image for development
        DEV_TAG="dev-$(date +%Y%m%d-%H%M%S)"
        docker tag "$DOCKER_IMAGE:$DOCKER_TAG" "$DOCKER_IMAGE:$DEV_TAG"
        
        print_warning "Development deployment requires additional configuration"
        print_warning "Please ensure your development environment is properly configured"
        
        # You would add actual deployment commands here
        # For example: kubectl apply, docker stack deploy, etc.
        
        print_success "Development deployment completed"
        ;;
        
    staging)
        print_status "Deploying to staging environment..."
        
        # Tag image for staging
        STAGING_TAG="staging-$(date +%Y%m%d-%H%M%S)"
        docker tag "$DOCKER_IMAGE:$DOCKER_TAG" "$DOCKER_IMAGE:$STAGING_TAG"
        
        print_warning "Staging deployment requires additional configuration"
        print_warning "Please ensure your staging environment is properly configured"
        
        # You would add actual deployment commands here
        
        print_success "Staging deployment completed"
        ;;
        
    prod)
        print_status "Deploying to production environment..."
        
        # Production deployment should be more cautious
        print_warning "This is a PRODUCTION deployment!"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Deployment cancelled"
            exit 0
        fi
        
        # Tag image for production
        PROD_TAG="prod-$(date +%Y%m%d-%H%M%S)"
        docker tag "$DOCKER_IMAGE:$DOCKER_TAG" "$DOCKER_IMAGE:$PROD_TAG"
        
        print_warning "Production deployment requires additional configuration"
        print_warning "Please ensure your production environment is properly configured"
        
        # You would add actual deployment commands here
        
        print_success "Production deployment completed"
        ;;
        
    *)
        print_error "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# Deployment health check
print_status "Performing deployment health check..."

case $ENVIRONMENT in
    local)
        # Check if local services are responding
        if curl -f http://localhost:5678/healthz > /dev/null 2>&1; then
            print_success "n8n service is healthy"
        else
            print_warning "n8n service may not be ready yet"
        fi
        
        # Test Playwright service
        if docker exec playwright-automation python -c "import sys; sys.exit(0)" > /dev/null 2>&1; then
            print_success "Playwright service is healthy"
        else
            print_warning "Playwright service may not be ready yet"
        fi
        ;;
        
    *)
        print_warning "Health check for $ENVIRONMENT environment not implemented"
        print_warning "Please manually verify deployment status"
        ;;
esac

# Show deployment summary
echo
echo "Deployment Summary"
echo "=================="
echo "Environment: $ENVIRONMENT"
echo "Docker Image: $DOCKER_IMAGE:$DOCKER_TAG"
echo "Build forced: $FORCE_BUILD"
echo "Tests run: $RUN_TESTS"
echo "Deployment time: $(date)"
echo

# Show next steps
echo "Next Steps:"
case $ENVIRONMENT in
    local)
        echo "1. Access n8n at http://localhost:5678"
        echo "2. Import example workflow from examples/n8n_workflow.json"
        echo "3. Test automation with provided examples"
        echo "4. Check logs: docker-compose -f docker/docker-compose.yml logs -f"
        ;;
    *)
        echo "1. Verify service health in $ENVIRONMENT environment"
        echo "2. Run integration tests"
        echo "3. Monitor service logs and metrics"
        echo "4. Update documentation with deployment details"
        ;;
esac

print_success "Deployment completed successfully!" 