#!/bin/bash

# Frontend Test Installation and Execution Script

echo "🚀 Setting up frontend tests..."

# Check if we're in the right directory
if [ ! -d "test" ]; then
    echo "❌ Please run this script from src/frontend directory"
    exit 1
fi

# Install test dependencies with legacy peer deps to handle React 19 compatibility
echo "📦 Installing test dependencies..."
npm install --save-dev --legacy-peer-deps \
    @testing-library/react@^14.2.1 \
    @testing-library/jest-dom@^6.4.2 \
    @testing-library/user-event@^14.5.2 \
    @testing-library/dom@^9.3.4 \
    jest@^29.7.0 \
    jest-environment-jsdom@^29.7.0 \
    ts-jest@^29.1.2 \
    @types/jest@^29.5.12 \
    identity-obj-proxy@^3.0.0 \
    msw@^2.2.1 \
    @tanstack/react-query@^5.35.0 \
    react-router-dom@^6.22.3

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Run tests
echo "🧪 Running frontend tests..."
npm test

if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed"
    exit 1
fi