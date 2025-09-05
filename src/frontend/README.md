# Image Processing Frontend

Modern, clean React frontend for the Image Processing API.

## Features

- **Upload Single Images**: Drag & drop or click to upload individual images for AI analysis
- **Process Folders**: Batch process images from server folders  
- **Real-time Results**: See processing status and detailed AI descriptions
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Clean UI**: Minimalist design focused on usability

## Quick Start

1. **Install dependencies**:
```bash
npm install
```

2. **Start development server**:
```bash
npm run dev
# or use the helper script
./run_frontend.sh
```

3. **Make sure API is running**:
The frontend expects the API at `http://localhost:8000`

## Usage

### Upload Images Tab
- Drag and drop images or click to select
- Supports: JPG, PNG, GIF, WebP, HEIC, BMP, TIFF
- Get instant AI-powered descriptions

### Process Folder Tab  
- Enter server-side folder path
- Select file extension and max images to process
- View batch processing results with success/failure status

## API Integration

The frontend communicates with your Python FastAPI backend:
- `POST /process/image` - Single image upload
- `POST /process/folder` - Folder batch processing

## Tech Stack

- **React 19** with TypeScript
- **Vite** for fast development
- **Modern CSS** with Grid/Flexbox
- **Inter font** for clean typography
- **Responsive design** principles

## Development

The frontend automatically connects to the API at `http://localhost:8000`. Make sure your API server is running before testing the frontend functionality.
