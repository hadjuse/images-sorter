#!/bin/bash

echo "Starting Image Processing Frontend..."
echo "Frontend will be available at: http://localhost:5173"
echo "Make sure the API is running at: http://localhost:8000"
echo ""

cd "$(dirname "$0")"
npm run dev
