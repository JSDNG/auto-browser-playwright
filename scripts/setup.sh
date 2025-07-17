#!/bin/bash

# Setup script for Playwright Backend Service
# This script sets up the development environment and dependencies

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'
}

# Function to check Python version
check_python_version() {
    local version=$(get_python_version)
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
        return 0
    else
        return 1
    fi
}

print_status "Starting Playwright Backend Service setup..."

# Check if Python is installed
if ! command_exists python; then
    print_error "Python is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

# Check Python version
if ! check_python_version; then
    print_error "Python 3.11+ is required. Current version: $(get_python_version)"
    exit 1
fi

print_success "Python $(get_python_version) is installed"

# Check if pip is installed
if ! command_exists pip; then
    print_error "pip is not installed. Please install pip and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
print_status "Installing production dependencies..."
pip install -r requirements.txt

# Install development dependencies
print_status "Installing development dependencies..."
pip install -r requirements-dev.txt

# Install Playwright browsers
print_status "Installing Playwright browsers..."
playwright install chromium

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p tmp
mkdir -p htmlcov

# Set up git hooks (if git is available)
if command_exists git && [ -d ".git" ]; then
    print_status "Setting up git hooks..."
    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to run linting and formatting

# Run black formatter
echo "Running black formatter..."
black src tests

# Run flake8 linter
echo "Running flake8 linter..."
flake8 src tests

# Run mypy type checker
echo "Running mypy type checker..."
mypy src
EOF
    chmod +x .git/hooks/pre-commit
    print_success "Git hooks configured"
fi

# Create .env file from template
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cp .env-example .env
    print_success ".env file created from template"
else
    print_status ".env file already exists"
fi

# Run initial tests
print_status "Running initial tests..."
if pytest tests/ -v --tb=short; then
    print_success "All tests passed"
else
    print_warning "Some tests failed. Please check the output above."
fi

# Check if Docker is available
if command_exists docker; then
    print_status "Docker detected. You can use 'make docker-build' to build Docker image."
else
    print_warning "Docker not found. Install Docker to use containerized deployment."
fi

# Display completion message
print_success "Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Test the CLI: python -m src.cli '{\"url\": \"https://example.com\", \"extract\": [{\"name\": \"title\", \"selector\": \"h1\"}]}'"
echo "3. Run tests: make test"
echo "4. Check code quality: make lint"
echo
echo "For more information, see README.md" 