#!/usr/bin/env bash
set -euo pipefail

# Complete development environment setup for Bet-That
# This script sets up everything needed for development

SCRIPT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "🚀 Setting up Bet-That Development Environment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status="$1"
    local message="$2"
    
    case $status in
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
    esac
}

# Check if we're in the right directory
if [ ! -f "Makefile" ] || [ ! -f "requirements.txt" ]; then
    print_status "error" "This script must be run from the Bet-That project root"
    exit 1
fi

# 1. Python Environment Setup
print_status "info" "Setting up Python environment..."

if [ ! -d ".venv" ]; then
    print_status "info" "Creating Python virtual environment..."
    python3 -m venv .venv
fi

print_status "info" "Activating virtual environment..."
source .venv/bin/activate

print_status "info" "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 2. Frontend Environment Setup
print_status "info" "Setting up frontend environment..."

if [ ! -d "frontend/node_modules" ]; then
    print_status "info" "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
else
    print_status "info" "Frontend dependencies already installed"
fi

# 3. Pre-commit Hooks Setup
print_status "info" "Setting up pre-commit hooks..."

if command -v pre-commit >/dev/null 2>&1; then
    pre-commit install
    print_status "success" "Pre-commit hooks installed"
else
    print_status "warning" "pre-commit not found, installing..."
    pip install pre-commit
    pre-commit install
    print_status "success" "Pre-commit hooks installed"
fi

# 4. Git Configuration
print_status "info" "Checking Git configuration..."

if ! git config --get user.name >/dev/null 2>&1; then
    print_status "warning" "Git user.name not configured"
    echo "Please run: git config --global user.name 'Your Name'"
fi

if ! git config --get user.email >/dev/null 2>&1; then
    print_status "warning" "Git user.email not configured"
    echo "Please run: git config --global user.email 'your.email@example.com'"
fi

# 5. Validation
print_status "info" "Running validation checks..."

echo
print_status "info" "Testing Python environment..."
if python -c "import black, flake8, mypy" 2>/dev/null; then
    print_status "success" "Python tools available"
else
    print_status "error" "Python tools not properly installed"
    exit 1
fi

echo
print_status "info" "Testing frontend environment..."
cd frontend
if npm run build >/dev/null 2>&1; then
    print_status "success" "Frontend builds successfully"
else
    print_status "error" "Frontend build failed"
    exit 1
fi
cd ..

echo
print_status "info" "Testing pre-commit hooks..."
if pre-commit run --all-files >/dev/null 2>&1; then
    print_status "success" "Pre-commit hooks working"
else
    print_status "warning" "Pre-commit hooks found issues (this is normal for initial setup)"
fi

# 6. Final Setup
echo
print_status "info" "Creating development aliases..."

# Create a simple alias file
cat > .dev-aliases << 'EOF'
# Bet-That Development Aliases
# Source this file: source .dev-aliases

alias bt-activate="source .venv/bin/activate"
alias bt-test="make test-all"
alias bt-check="make commit-check"
alias bt-format="make format"
alias bt-quality="make quality-check"
alias bt-ui="make ui"
alias bt-edges="make edges"
alias bt-import="make import-odds"
EOF

print_status "success" "Development aliases created in .dev-aliases"

# 7. Summary
echo
echo "=============================================="
print_status "success" "Development environment setup complete!"
echo
echo "Next steps:"
echo "1. Source the aliases: source .dev-aliases"
echo "2. Run validation: make commit-check"
echo "3. Start developing!"
echo
echo "Useful commands:"
echo "  make help              # Show all available commands"
echo "  make commit-check      # Run full validation"
echo "  make quality-check     # Run code quality checks"
echo "  make test-all          # Run all tests"
echo "  make format            # Auto-format code"
echo "  make ui                # Launch Streamlit UI"
echo
echo "For more information, see TESTING_STRATEGY.md"
echo "=============================================="
