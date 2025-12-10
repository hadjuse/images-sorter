# Frontend Test Suite

This directory contains comprehensive tests for the React/TypeScript frontend application.

## Test Structure

- `frontend.test.ts` - Main frontend tests using React Testing Library
- `jest.config.js` - Jest configuration for frontend testing
- `setupTests.ts` - Test setup and mocks
- `test-utils.tsx` - Custom test utilities and render functions

## Test Coverage

### Components Tested

1. **ImageUploader**
   - File selection and preview
   - Drag and drop functionality
   - Image processing (mocked)
   - Error handling

2. **FolderProcessor**
   - Folder configuration
   - Image preview functionality
   - Folder processing (mocked)
   - Streaming mode
   - Auto-preview feature

3. **ImagePreview**
   - Image display
   - Preview limits
   - Clear functionality

4. **API Integration**
   - API service mocking
   - Error handling
   - Loading states

## Running Tests

### Prerequisites

```bash
cd src/frontend
npm install

# Install test dependencies (with --legacy-peer-deps for React 19 compatibility)
npm install --save-dev --legacy-peer-deps \\
    @testing-library/react@^14.2.1 \\
    @testing-library/jest-dom@^6.4.2 \\
    @testing-library/user-event@^14.5.2 \\
    @testing-library/dom@^9.3.4 \\
    jest@^29.7.0 \\
    jest-environment-jsdom@^29.7.0 \\
    ts-jest@^29.1.2 \\
    @types/jest@^29.5.12 \\
    identity-obj-proxy@^3.0.0 \\
    msw@^2.2.1 \\
    @tanstack/react-query@^5.35.0 \\
    react-router-dom@^6.22.3
```

Or use the installation script:

```bash
cd src/frontend/test
./install_and_test.sh
```

### Run Tests

```bash
cd src/frontend
npm test
```

### Run with Coverage

```bash
cd src/frontend
npm test -- --coverage
```

## Test Features

- **React Testing Library**: For realistic component testing
- **Jest**: Test runner with TypeScript support
- **Mock Service Worker**: For API mocking
- **User Event**: For realistic user interaction simulation
- **Coverage Reporting**: Istanbul coverage reports

## Development

To add new tests:

1. Create test files with `.test.ts` or `.test.tsx` extension
2. Use `renderWithProviders` from test-utils.tsx
3. Follow the existing test patterns
4. Mock external dependencies

## Troubleshooting

### React 19 Compatibility Issues

If you encounter dependency conflicts with React 19:

```bash
# Use legacy peer deps flag
npm install --save-dev --legacy-peer-deps

# Or force installation (not recommended)
npm install --save-dev --force
```

### Jest Environment Issues

If you get "jest-environment-jsdom cannot be found" error:

```bash
# Install the missing package
npm install --save-dev jest-environment-jsdom

# Or update the configuration to use 'jsdom' instead
# testEnvironment: 'jsdom',
```

### Test Failures

Common issues and solutions:

1. **API mocks not working**: Ensure Mock Service Worker is properly set up in `setupTests.ts`
2. **Component not rendering**: Check that all required providers are wrapped in `test-utils.tsx`
3. **TypeScript errors**: Ensure `ts-jest` is properly configured in `jest.config.js`
4. **Coverage issues**: Run tests with `--coverage` flag to see detailed reports

## Continuous Integration

The test suite is designed for CI/CD integration:
- Fast execution (~10-15 seconds)
- Consistent results
- Coverage reporting
- Type checking