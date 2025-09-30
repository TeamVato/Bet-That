# Bet-That Testing & Validation Strategy

This document outlines the comprehensive testing and validation strategy to prevent commit/staging issues and ensure code quality.

## Overview

The Bet-That project uses a multi-layered approach to catch issues before they reach production:

1. **Pre-commit hooks** - Catch issues before they're committed
2. **Commit validation** - Comprehensive checks before pushing
3. **CI/CD pipeline** - Automated testing on every PR
4. **Manual validation** - System-wide checks before deployment

## Pre-Commit Hooks

### Installation
```bash
make pre-commit-install
# or
. .venv/bin/activate && pre-commit install
```

### What They Check
- **Python**: Black formatting, Flake8 linting, MyPy type checking
- **Frontend**: TypeScript compilation, ESLint, Prettier formatting
- **General**: Trailing whitespace, merge conflicts, large files
- **Security**: Bandit security scan, dependency audit
- **Project-specific**: Makefile validation, Streamlit deprecations

### Running Manually
```bash
. .venv/bin/activate && pre-commit run --all-files
```

## Commit Validation

### Running Before Commit
```bash
make commit-check
# or
./scripts/commit-validation.sh
```

### What It Validates
1. **Git Status**: Clean working tree, no untracked files, no merge conflicts
2. **File Format**: Line endings, whitespace, Makefile format
3. **Code Quality**: Python and frontend formatting/linting
4. **Tests**: Unit tests, frontend tests
5. **Security**: Bandit scan, dependency audit
6. **Integration**: Backend integration tests (if applicable)
7. **Documentation**: README exists, no broken links

## CI/CD Pipeline

### GitHub Actions Workflows
- **Daily Chain** (`daily.yml`): Automated data pipeline validation
- **Edges** (`edges.yml`): Edge computation validation
- **Weekly** (`weekly.yml`): Weekly reporting validation

### What CI Checks
- Python 3.12 compatibility
- Dependency installation
- Streamlit deprecation checks
- Data pipeline execution
- Edge computation
- Artifact generation

## Testing Levels

### 1. Unit Tests
```bash
make test-unit
# or
. .venv/bin/activate && python -m pytest tests/ -m "not integration" -v
```

**Coverage**: Individual functions, classes, and modules
**Location**: `tests/` directory
**Markers**: Exclude `integration` marker

### 2. Integration Tests
```bash
make test-integration
# or
. .venv/bin/activate && python -m pytest tests/ -m "integration" -v
```

**Coverage**: End-to-end workflows, API interactions
**Location**: `tests/` directory
**Markers**: Include `integration` marker

### 3. Frontend Tests
```bash
cd frontend && npm test
```

**Coverage**: React components, hooks, utilities
**Location**: `frontend/src/` directory
**Framework**: Vitest with React Testing Library

### 4. System Validation
```bash
./validate_system.sh
```

**Coverage**: Redis, API, Frontend, Edge detection
**Purpose**: Verify all services are running correctly

## Quality Checks

### Python Code Quality
```bash
make quality-check
```

**Tools**:
- **Black**: Code formatting
- **Flake8**: Linting and style
- **MyPy**: Type checking

### Frontend Code Quality
```bash
cd frontend && npm run lint
cd frontend && npm run format
```

**Tools**:
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **TypeScript**: Compilation checking

## Security Checks

### Bandit Security Scan
```bash
. .venv/bin/activate && python -m bandit -r . -f json -o bandit-report.json
```

**Purpose**: Detect common security issues in Python code

### Dependency Audit
```bash
. .venv/bin/activate && python -m pip_audit --desc --format=json --output=pip-audit-report.json
```

**Purpose**: Check for known vulnerabilities in dependencies

## Project-Specific Checks

### Streamlit Deprecations
```bash
./scripts/lint_streamlit.sh
```

**Purpose**: Ensure no deprecated Streamlit arguments are used

### Makefile Validation
```bash
./scripts/check-makefile.sh
```

**Purpose**: Validate Makefile format and syntax

### Ingestion Contract
```bash
make check-ingestion-contract
```

**Purpose**: Verify odds ingestion contract end-to-end

## Best Practices

### Before Committing
1. Run `make commit-check` to validate everything
2. Fix any issues found
3. Commit with descriptive messages

### Before Pushing
1. Ensure all tests pass locally
2. Run system validation
3. Check CI status

### Before Merging PRs
1. All CI checks must pass
2. Code review completed
3. No merge conflicts

### Before Deployment
1. Run full test suite
2. Validate system components
3. Check data pipeline integrity

## Troubleshooting

### Common Issues

#### TypeScript Compilation Errors
```bash
cd frontend && npm install
cd frontend && npm run build
```

#### Python Import Errors
```bash
. .venv/bin/activate && pip install -r requirements.txt
. .venv/bin/activate && pip install -r requirements-dev.txt
```

#### Test Failures
```bash
# Check specific test
. .venv/bin/activate && python -m pytest tests/test_specific.py -v

# Check with coverage
. .venv/bin/activate && python -m pytest --cov --cov-report=term-missing
```

#### Pre-commit Hook Failures
```bash
# Skip hooks for emergency commits
git commit --no-verify -m "Emergency fix"

# Fix and retry
. .venv/bin/activate && pre-commit run --all-files
```

## Automation

### Git Hooks
- **Pre-commit**: Run quality checks
- **Pre-push**: Run system validation

### Make Targets
- `make commit-check`: Full validation
- `make quality-check`: Code quality only
- `make test-all`: All tests
- `make format`: Auto-fix formatting

### CI Integration
- Automatic testing on PRs
- Daily pipeline validation
- Weekly reporting checks

## Monitoring

### Test Coverage
- Aim for >80% code coverage
- Track coverage trends over time
- Focus on critical paths

### Performance
- Monitor test execution time
- Track build times
- Optimize slow tests

### Quality Metrics
- Track linting errors over time
- Monitor security vulnerabilities
- Measure code complexity

## Conclusion

This comprehensive testing strategy ensures that:
- Code quality is maintained
- Security issues are caught early
- Integration problems are prevented
- Deployment issues are minimized

Follow these practices to maintain a healthy, reliable codebase.
