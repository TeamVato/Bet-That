#!/usr/bin/env bash
set -euo pipefail

# Comprehensive commit validation script for Bet-That
# Run this before committing to catch issues early

SCRIPT_DIR="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "🔍 Bet-That Commit Validation"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

# Function to run a check and track status
run_check() {
    local name="$1"
    local command="$2"
    
    echo -n "Checking $name... "
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
    else
        echo -e "${RED}❌ FAIL${NC}"
        OVERALL_STATUS=1
        echo "  Command: $command"
        echo "  Run manually to see details"
    fi
}

# Function to run a check with output
run_check_verbose() {
    local name="$1"
    local command="$2"
    
    echo "Checking $name..."
    if eval "$command"; then
        echo -e "${GREEN}✅ $name PASSED${NC}"
    else
        echo -e "${RED}❌ $name FAILED${NC}"
        OVERALL_STATUS=1
    fi
    echo
}

echo "1. Git Status Checks"
echo "-------------------"
run_check "Working tree clean" "git diff --quiet"
run_check "No untracked files" "git ls-files --others --exclude-standard | wc -l | grep -q '^0$'"
run_check "No merge conflicts" "! git grep -q '^<<<<<<< '"

echo
echo "2. File Format Checks"
echo "-------------------"
run_check "No CRLF line endings" "! find . -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' | xargs grep -l $'\r'"
run_check "No trailing whitespace" "! git diff --check"
run_check "Makefile format" "./scripts/check-makefile.sh"

echo
echo "3. Python Code Quality"
echo "-------------------"
run_check_verbose "Black formatting" ". .venv/bin/activate && python -m black --check --diff ."
run_check_verbose "Flake8 linting" ". .venv/bin/activate && python -m flake8 ."
run_check_verbose "MyPy type checking" ". .venv/bin/activate && python -m mypy . --ignore-missing-imports"

echo
echo "4. Frontend Code Quality"
echo "-------------------"
run_check_verbose "TypeScript compilation" "cd frontend && npm run build"
run_check_verbose "ESLint checks" "cd frontend && npm run lint"
run_check_verbose "Frontend tests" "cd frontend && npm test"

echo
echo "5. Python Tests"
echo "-------------------"
run_check_verbose "Unit tests" ". .venv/bin/activate && python -m pytest tests/ -m 'not integration' -x --tb=short"

echo
echo "6. Project-Specific Checks"
echo "-------------------"
run_check_verbose "Streamlit deprecations" "./scripts/lint_streamlit.sh"
run_check_verbose "System validation" "./validate_system.sh"

echo
echo "7. Security Checks"
echo "-------------------"
run_check_verbose "Bandit security scan" ". .venv/bin/activate && python -m bandit -r . -f json -o /dev/null"
run_check_verbose "Dependency audit" ". .venv/bin/activate && python -m pip_audit --desc --format=json --output=/dev/null"

echo
echo "8. Integration Tests (if applicable)"
echo "-------------------"
if git diff --name-only HEAD~1 | grep -E '\.(py|ts|tsx|js|jsx)$' | grep -q -E '(api/|engine/|jobs/)'; then
    echo "Backend changes detected, running integration tests..."
    run_check_verbose "Integration tests" ". .venv/bin/activate && python -m pytest tests/ -m integration -x --tb=short"
else
    echo "No backend changes detected, skipping integration tests"
fi

echo
echo "9. Documentation Checks"
echo "-------------------"
run_check "README exists" "test -f README.md"
run_check "No broken internal links" "! grep -r '\[.*\](.*)' --include='*.md' . | grep -v 'http' | grep -q ']('"

echo
echo "=============================="
if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Ready to commit.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix issues before committing.${NC}"
    echo
    echo "To run individual checks:"
    echo "  make quality-check    # Run all quality checks"
    echo "  make test-all        # Run all tests"
    echo "  make format          # Auto-fix formatting issues"
    exit 1
fi
