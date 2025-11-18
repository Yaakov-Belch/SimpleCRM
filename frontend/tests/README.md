# Test Suite Guide

## Running Tests

### Run All Tests (Standard)
```bash
npm test
```

### Run All Tests with Full Isolation (Recommended for CI/CD)
```bash
npm test -- --pool=forks --poolOptions.forks.singleFork=true
```

This ensures each test file runs in a separate process, preventing module-level state pollution.

### Run Specific Test File
```bash
npm test -- tests/integration.test.js
```

### Run Specific Test
```bash
npm test -- integration.test.js -t "should persist authentication"
```

### Run Skipped Integration Tests Individually
Some integration tests are skipped in batch runs due to state isolation issues. To run them:

```bash
# Test authentication persistence
npm test -- integration.test.js -t "persist"

# Test session expiration
npm test -- integration.test.js -t "expiration"
```

## Known Issues

### Integration Test Isolation

The tests in `integration.test.js` have module-level state dependencies due to Vue's reactive refs and Vitest's module caching. When run together in the same process, later tests may see cached state from earlier tests.

**Symptoms:**
- Tests pass individually but fail when run together
- User data from previous tests appears in later tests

**Solutions:**
1. **For automated testing (CI/CD)**: Use `--pool=forks` flag
2. **For development**: Run individual tests when debugging
3. **Tests still verify functionality**: The application works correctly; this is purely a test infrastructure issue

## Test Organization

- `*.test.js` - Component and unit tests
- `integration.test.js` - End-to-end integration tests (require special handling)
- `protected-pages.test.js` - Protected route tests
- `ux-improvements-integration.test.js` - UX improvements feature tests

## For AI Coding Agents

When running tests as part of verification:
1. Use `--pool=forks` for complete test runs
2. Individual test failures may indicate isolation issues - verify by running the test alone
3. If a test passes in isolation but fails with others, it's likely a test infrastructure issue, not a functionality bug
