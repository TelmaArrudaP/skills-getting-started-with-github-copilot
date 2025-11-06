# Tests for Mergington High School Activities API

This directory contains comprehensive test suites for the FastAPI application.

## Test Structure

- `test_api.py` - Core API endpoint tests including signup, unregister, and activities
- `test_edge_cases.py` - Edge cases, validation, error handling, and boundary conditions  
- `test_static.py` - Static file serving and frontend content tests
- `conftest.py` - pytest configuration and shared fixtures

## Running Tests

### Run all tests:
```bash
python -m pytest tests/
```

### Run with verbose output:
```bash
python -m pytest tests/ -v
```

### Run with coverage report:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Run specific test file:
```bash
python -m pytest tests/test_api.py -v
```

### Run specific test class:
```bash
python -m pytest tests/test_api.py::TestSignupEndpoint -v
```

### Run specific test:
```bash
python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_for_existing_activity_success -v
```

### Use the custom test runner:
```bash
python run_tests.py
```

## Test Coverage

The test suite achieves **100% code coverage** of the FastAPI application, testing:

- ✅ All API endpoints (GET /activities, POST /signup, DELETE /unregister)
- ✅ Success and error scenarios
- ✅ Edge cases and validation
- ✅ Static file serving
- ✅ HTTP method restrictions
- ✅ Data consistency and state management
- ✅ URL encoding and special characters
- ✅ Integration workflows

## Test Categories

### Core API Tests (`test_api.py`)
- Root endpoint redirection
- Activities listing and structure
- Participant signup (success, duplicates, capacity limits)
- Participant unregistration 
- Integration scenarios and workflows

### Edge Cases (`test_edge_cases.py`)
- Empty and malformed inputs
- Special characters and URL encoding
- Long inputs and boundary conditions
- HTTP method validation
- Response format validation
- API documentation endpoints

### Static Content (`test_static.py`)
- Static file accessibility (HTML, CSS, JS)
- Content validation
- 404 handling for missing files

## Dependencies

- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support  
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for testing FastAPI
- `fastapi[test]` - FastAPI testing utilities

## Notes

- Tests use automatic fixtures to reset the activities database before each test
- All tests are isolated and can run in any order
- The test suite is designed to be fast and reliable
- Coverage reports show which lines of code are tested