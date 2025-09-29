# Quality Implementation Plan

## Phase 1: Critical (2-4 hours)

**Must-have for production**

### 1.1 Python Quality Tools

- [ ] Create requirements-dev.txt (black, flake8, mypy, pytest-cov)
- [ ] Create pyproject.toml config (Black, Flake8, mypy, pytest settings)
- [ ] Create .flake8 config (line length, ignore patterns)
- [ ] Update Makefile with quality targets (install-dev, quality-check, format)
- [ ] Verify: `make install-dev && make quality-check` runs

### 1.2 TypeScript Quality Enhancement

- [ ] Verify ESLint config includes TypeScript rules
- [ ] Add stricter TypeScript configuration
- [ ] Add test coverage reporting to package.json
- [ ] Verify: `pnpm run lint && pnpm run test` runs

### 1.3 Makefile Quality Integration

- [ ] Add `install-dev` target for development dependencies
- [ ] Add `quality-check` target (Black, Flake8, mypy)
- [ ] Add `format` target (Black, Prettier)
- [ ] Add `test-all` target with coverage
- [ ] Verify: `make help` shows new commands

**Time Estimate: 2-4 hours**

## Phase 2: Testing Infrastructure (3-5 hours)

**Core business logic coverage**

### 2.1 Test Structure Reorganization

- [ ] Create backend/tests/unit/ directory structure
- [ ] Create backend/tests/integration/ directory structure
- [ ] Move appropriate tests from /tests/ to backend/tests/
- [ ] Add conftest.py files for shared fixtures
- [ ] Update pytest configuration for new structure

### 2.2 Unit Test Coverage (Priority Areas)

- [ ] **engine/edge_engine.py** - Core betting logic (>90% coverage target)
- [ ] **engine/odds_math.py** - Mathematical calculations (>95% coverage target)
- [ ] **adapters/odds/** - Data ingestion (>80% coverage target)
- [ ] **api/endpoints/** - API endpoints (>80% coverage target)
- [ ] Add pytest-cov configuration for coverage reporting

### 2.3 Integration Tests

- [ ] **Database operations** - SQLite interactions, migrations
- [ ] **API workflows** - End-to-end endpoint testing
- [ ] **Data pipeline** - Odds ingestion → Edge computation
- [ ] Target: >60% overall backend coverage

### 2.4 Frontend Testing Enhancement

- [ ] Add component unit tests (React Testing Library)
- [ ] Add integration tests for critical user flows
- [ ] Configure coverage reporting with Vitest
- [ ] Target: >60% frontend coverage

**Time Estimate: 3-5 hours**

## Phase 3: Automation (1-2 hours)

**Prevent bad code from entering repo**

### 3.1 Pre-commit Configuration

- [ ] Create .pre-commit-config.yaml with hooks:
  - Black (Python formatting)
  - Flake8 (Python linting)
  - Prettier (JS/TS formatting)
  - ESLint (JS/TS linting)
  - mypy (Python type checking)
- [ ] Install: `pre-commit install`
- [ ] Test: Make dummy change, commit triggers all hooks
- [ ] Document: Add setup instructions to README

### 3.2 Git Hook Validation

- [ ] Test pre-commit catches formatting issues
- [ ] Test pre-commit catches linting issues
- [ ] Verify hooks work in CI environment

**Time Estimate: 1-2 hours**

## Phase 4: CI/CD Quality Gates (2-3 hours)

**Automated checks on PRs**

### 4.1 GitHub Actions Quality Workflow

- [ ] Create .github/workflows/quality.yml
- [ ] Add Python quality job (Black, Flake8, mypy)
- [ ] Add Python test job (pytest with coverage)
- [ ] Add TypeScript quality job (ESLint, Prettier)
- [ ] Add TypeScript test job (Vitest with coverage)

### 4.2 PR Integration

- [ ] Configure quality workflow to run on PRs
- [ ] Add status checks as required for merging
- [ ] Test: Create dummy PR, verify all checks run
- [ ] Add coverage reporting (CodeCov or similar)

### 4.3 Workflow Optimization

- [ ] Add caching for dependencies (pip, npm)
- [ ] Parallelize quality checks where possible
- [ ] Set appropriate timeout values

**Time Estimate: 2-3 hours**

## Phase 5: Advanced Quality (Optional - 2-4 hours)

**Enhanced development experience**

### 5.1 Type Safety Enhancement

- [ ] Enable strict mode in TypeScript config
- [ ] Add comprehensive mypy configuration
- [ ] Fix existing type issues revealed by strict checking

### 5.2 Security & Dependencies

- [ ] Add dependabot configuration
- [ ] Add security scanning (Bandit for Python)
- [ ] Add dependency vulnerability checks

### 5.3 Performance & Monitoring

- [ ] Add performance regression tests
- [ ] Configure test performance monitoring
- [ ] Add complexity analysis tools

**Time Estimate: 2-4 hours**

---

## Total Estimate: 8-14 hours

- **Phase 1**: 2-4 hours (Critical)
- **Phase 2**: 3-5 hours (High Priority)
- **Phase 3**: 1-2 hours (Important)
- **Phase 4**: 2-3 hours (CI/CD)
- **Phase 5**: 2-4 hours (Optional)

## Recommended Execution Order

### Week 1: Foundation (Phases 1-2)

1. **Start with Phase 1.1** - Python quality tools (enables all other checks)
2. **Then Phase 1.3** - Makefile integration (provides workflow commands)
3. **Then Phase 2.1-2.2** - Test structure + core unit tests

### Week 2: Automation (Phases 3-4)

4. **Phase 3** when ready to enforce quality standards
5. **Phase 4** for team collaboration and PR automation

### Later: Enhancement (Phase 5)

6. **Phase 5** for advanced quality features

## Success Validation Commands

After each phase, these should work:

### Phase 1 Complete:

```bash
cd /Users/vato/work/Bet-That
make install-dev     # Install quality tools
make quality-check   # Run all linters
make format         # Format all code
```

### Phase 2 Complete:

```bash
make test-all       # Run tests with coverage
# Should show >60% coverage for new test areas
```

### Phase 3 Complete:

```bash
git add . && git commit -m "test"  # Triggers pre-commit hooks
# Should run Black, Flake8, Prettier, ESLint automatically
```

### Phase 4 Complete:

```bash
# Push branch, create PR
# Should see quality checks run automatically in GitHub
```

## Risk Mitigation

### If Issues Arise:

1. **Tool conflicts** - Check version compatibility in requirements
2. **Legacy code issues** - Use gradual adoption (exclude patterns)
3. **CI failures** - Start with warnings, then upgrade to errors
4. **Team adoption** - Provide clear documentation and training

### Rollback Plan:

- Each phase is independent
- Can disable pre-commit hooks if needed: `pre-commit uninstall`
- Can remove GitHub Actions quality checks
- Configuration files can be easily reverted

## Quality Metrics Targets

### Code Coverage

- **Backend core logic**: >80% (edge_engine, odds_math)
- **Backend overall**: >60%
- **Frontend components**: >60%
- **Frontend overall**: >50%

### Quality Checks

- **Zero linting errors** in new code
- **Zero formatting inconsistencies**
- **Zero type checking errors** (where configured)
- **All tests passing** in CI

### Performance

- **Quality checks**: <2 minutes in CI
- **Test suite**: <5 minutes for full run
- **Pre-commit hooks**: <30 seconds locally
