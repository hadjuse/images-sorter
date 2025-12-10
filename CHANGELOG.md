# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Comprehensive API Test Suite** (`src/backend/test/`)
  - `test_api.py`: 20 comprehensive tests covering all API endpoints
  - `pytest.ini`: Pytest configuration with coverage settings
  - `requirements-test.txt`: Test dependencies
  - `run_tests.py`: Test runner script with coverage reporting
  - `README.md`: Test suite documentation
  - `TEST_SUMMARY.md`: Test results and coverage summary
  - **Coverage**: 42% code coverage of API module
  - **Test Categories**: Basic endpoints, single image processing, folder processing, folder preview, image serving

- **Comprehensive Frontend Test Suite** (`src/frontend/test/`)
  - `frontend.test.tsx`: 15+ comprehensive tests for React components
  - `jest.config.js`: Jest configuration with TypeScript support
  - `setupTests.ts`: Test setup with Mock Service Worker
  - `test-utils.tsx`: Custom test utilities and providers
  - `mocks/handlers.ts`: API mock handlers for all endpoints
  - `README.md`: Frontend test suite documentation
  - **Test Coverage**: ImageUploader, FolderProcessor, ImagePreview components
  - **Features**: Component rendering, user interactions, API integration, error handling

### Changed

- **Backend API CORS Configuration** (`src/backend/api/api.py`)
  - **Secure CORS Setup**:
    - Allow origins: `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:5173`, `http://127.0.0.1:5173`, `http://127.0.0.1:8000`
    - Disable credentials for security (`allow_credentials=False`)
    - Allow methods: GET, POST, PUT, DELETE, OPTIONS
    - Allow headers: Content-Type, Authorization, Accept, Accept-Language
  - **Streaming-Specific CORS Middleware**:
    - Added middleware for EventSource/Streaming requests
    - Special headers for endpoints ending with "/stream"
    - Resolves CORS issues with EventSource requests
  - **Import Response**: Added `Response` to FastAPI imports for header manipulation

- **Folder Streaming Endpoint** (`src/backend/api/api.py`)
  - Changed from POST to GET method for EventSource compatibility
  - Updated parameter handling from `request: FolderRequest` to individual parameters
  - Added Response parameter for CORS header manipulation
  - Fixed all references from `request.folder_path` to `folder_path`

- **Frontend Folder Processor** (`src/frontend/src/components/FolderProcessor.tsx`)
  - **Default Configuration**:
    - Changed default folder path from `/mnt/c/Users/pc/Pictures/madagascar/` to `/mnt/c/Users/pc/Pictures/ted/`
    - Changed default file extension from `jpg` to `png`
    - Updated extension selector to have PNG as first option
  - **Streaming Compatibility**: Uses EventSource with GET method for streaming endpoint

- **Frontend API Configuration** (`src/frontend/src/config/api.ts`)
  - **API Base URL**: Changed from `http://localhost:8000` to `http://127.0.0.1:8000` for consistency
  - Maintains hardcoded development configuration

### Fixed

- **CORS Policy Errors**:
  - Resolved "No 'Access-Control-Allow-Origin' header" errors for streaming endpoints
  - Fixed EventSource CORS issues with proper header configuration
  - Ensured consistent origin handling between frontend and backend

- **Unused Import**:
  - Removed unused `useEffect` import from `ImageUploader.tsx`
  - Fixed TypeScript compilation error in frontend build

- **Streaming Endpoint Method**:
  - Fixed mismatch between frontend (GET with EventSource) and backend (POST)
  - Changed backend to accept GET requests for streaming compatibility

- **Frontend Test Dependencies**:
  - Fixed React 19 compatibility issues with `--legacy-peer-deps` flag
  - Resolved jest-environment-jsdom dependency conflicts
  - Updated installation scripts and documentation

### Security

- **Improved CORS Security**:
  - Removed wildcard `"*"` origin from main CORS configuration
  - Added specific, secure origin list for development environments
  - Disabled credentials for enhanced security
  - Limited allowed methods and headers to necessary ones only

## [Previous Versions]

### Initial Setup
- Basic project structure with frontend and backend
- Docker configuration for development
- Image processing API with basic endpoints
- Frontend with image upload and folder processing components

### Early Development
- Added folder processing functionality
- Implemented streaming endpoints
- Basic error handling and validation
- Initial CORS configuration with wildcard origins

---

## Migration Guide

### From Previous Versions

1. **Update API Configuration**:
   - Frontend: Ensure `API_BASE_URL` points to `http://127.0.0.1:8000`
   - Backend: Update CORS configuration to match your production domains

2. **Test Suite Integration**:
   - Install test dependencies: `uv pip install pytest pytest-cov pytest-asyncio httpx responses coverage`
   - Run tests: `cd src/backend/test && python run_tests.py`

3. **Streaming Endpoint Usage**:
   - Frontend: Use EventSource with GET method for streaming
   - Backend: Ensure streaming endpoints return proper CORS headers

### Development Workflow

1. **Run Backend**:
   ```bash
   cd src/backend
   python main.py
   ```

2. **Run Frontend**:
   ```bash
   cd src/frontend
   npm run dev
   ```

3. **Run Backend Tests**:
   ```bash
   cd src/backend/test
   python run_tests.py
   ```

4. **Run Frontend Tests**:
   ```bash
   cd src/frontend
   npm test
   ```

5. **Run Frontend Tests with Coverage**:
   ```bash
   cd src/frontend
   npm test -- --coverage
   ```

6. **Run All Tests**:
   ```bash
   # Backend tests
   cd src/backend/test && python run_tests.py
   
   # Frontend tests
   cd src/frontend && npm test
   ```

## Contributing

When making changes:

### Backend Changes

1. **Update Tests**: Add or modify tests in `src/backend/test/test_api.py`
2. **Document Changes**: Add entries to this CHANGELOG.md file
3. **Follow Security Best Practices**: Maintain secure CORS configuration
4. **Run Tests**: Ensure all tests pass before committing

### Frontend Changes

1. **Update Tests**: Add or modify tests in `src/frontend/test/frontend.test.tsx`
2. **Add API Mocks**: Update mock handlers in `src/frontend/test/mocks/handlers.ts`
3. **Document Changes**: Add entries to this CHANGELOG.md file
4. **Run Tests**: Ensure frontend tests pass with `npm test`
5. **Update Test Utils**: Modify `test-utils.tsx` if new providers are needed

### Test Coverage Guidelines

- **Backend**: Aim for 80%+ coverage of API endpoints
- **Frontend**: Test all major components and user interactions
- **Edge Cases**: Test error conditions and invalid inputs
- **API Integration**: Mock all API calls for consistent testing

## Versioning

This project uses semantic versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Contact

For questions or issues, please refer to the project documentation or open an issue in the repository.