# Image Processing API Test Suite

This directory contains comprehensive tests for the Image Processing API.

## Test Structure

- `test_api.py` - Main test file containing all API endpoint tests
- `run_tests.py` - Test runner script
- `pytest.ini` - Pytest configuration
- `requirements-test.txt` - Test dependencies

## Running Tests

### Prerequisites

Make sure you have the required test dependencies installed:

```bash
pip install -r requirements-test.txt
```

### Running Tests

#### Method 1: Using the test runner script

```bash
cd src/backend/test
python run_tests.py
```

#### Method 2: Running pytest directly

```bash
cd src/backend/test
python -m pytest -v --tb=short --color=yes
```

#### Method 3: Running with coverage

```bash
cd src/backend/test
python -m pytest -v --cov=../api --cov-report=term-missing --cov-report=html:../coverage_report
```

## Test Coverage

The test suite covers:

### Basic Endpoints
- Root endpoint (`/`)
- Health check endpoint (`/health`)

### Single Image Processing
- Successful image processing (`POST /process/image`)
- Invalid content type handling
- Missing file handling
- Streaming image processing (`POST /process/image/stream`)

### Folder Processing
- Successful folder processing (`POST /process/folder`)
- Non-existent folder handling
- Invalid directory path handling
- Streaming folder processing (`GET /process/folder/stream`)

### Folder Preview
- Successful folder preview (`POST /preview/folder`)
- Non-existent folder handling
- Invalid directory path handling

### Image Serving
- Successful image serving (`GET /image/{path}`)
- Non-existent image handling
- Invalid file path handling
- Non-image file handling

## Test Features

- **Mocking**: Uses unittest.mock to mock the image processor and inference functions
- **Temporary Files**: Creates temporary test images and folders for realistic testing
- **Comprehensive Assertions**: Tests both success and error cases
- **Streaming Support**: Tests both regular and streaming endpoints
- **Parameter Validation**: Tests input validation and error handling

## Development

To add new tests:

1. Add test functions to `test_api.py` following the existing pattern
2. Use pytest fixtures for reusable test setup/teardown
3. Use mocking for external dependencies
4. Follow the naming convention `test_*` for test functions

## Continuous Integration

The test suite is designed to work with CI/CD pipelines. The coverage threshold is set to 80% in the pytest configuration.