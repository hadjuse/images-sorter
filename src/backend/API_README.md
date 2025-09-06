# Image Processing API

Simple API using vision-language models to analyze and describe images.

## Installation and Setup

1. Install dependencies:
```bash
cd src/backend
uv sync
```

2. Configure environment variables in `.env` file:
```
PATH_TO_FOLDER_TEST=/path/to/your/test/images
```

3. Start the API:
```bash
python run_api.py
```

API will be available at `http://localhost:8000`

## Interactive Documentation

Once the API is running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

### Health Check

#### `GET /`
Basic health check endpoint to verify the API is running.

**Response:**
```json
{
  "message": "Image Processing API is running"
}
```

### Image Processing

#### `POST /process/image`
Process a single uploaded image file.
- **Content-Type**: `multipart/form-data`
- **Parameter**: `file` (image file)

**Response:**
```json
{
  "filename": "image.jpg",
  "status": "success",
  "description": "Detailed description of the image..."
}
```

#### `POST /process/folder`
Process images from a folder path using existing ImageProcessor methods.
- **Content-Type**: `application/json`
- **Parameters**:
  - `folder_path`: Path to the folder containing images
  - `extension`: File extension to filter (default: "jpg")
  - `max_images`: Maximum number of images to process (default: 7)

**Request:**
```json
{
  "folder_path": "/path/to/images",
  "extension": "jpg",
  "max_images": 5
}
```

**Response:**
```json
{
  "folder_path": "/path/to/images",
  "extension": "jpg",
  "total_found": 10,
  "processed": 5,
  "successful": 4,
  "failed": 1,
  "results": [
    {
      "image_path": "/path/to/image1.jpg",
      "status": "success",
      "description": "Description of image 1..."
    },
    {
      "image_path": "/path/to/image2.jpg",
      "status": "error",
      "error": "Processing error message"
    }
  ]
}
```

## Usage Examples

### Curl

```bash
# Process single image
curl -X POST "http://localhost:8000/process/image" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/image.jpg"

# Process folder
curl -X POST "http://localhost:8000/process/folder" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "folder_path": "/path/to/images",
       "extension": "jpg",
       "max_images": 5
     }'
```

### Python

```python
import requests

# Process single image
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process/image',
        files={'file': f}
    )
    print(response.json())

# Process folder
response = requests.post(
    'http://localhost:8000/process/folder',
    json={
        'folder_path': '/path/to/images',
        'extension': 'jpg',
        'max_images': 5
    }
)
print(response.json())
```

### JavaScript/Fetch

```javascript
// Process single image
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/process/image', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Process folder
fetch('http://localhost:8000/process/folder', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        folder_path: '/path/to/images',
        extension: 'jpg',
        max_images: 5
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Error Handling

The API returns standard HTTP error codes:
- `400`: Bad request (invalid parameters)
- `404`: Resource not found (folder doesn't exist)
- `500`: Internal server error (processing failed)
- `503`: Service unavailable (model not initialized)

## Supported Image Formats

The API accepts common image formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)
- HEIC (.heic)

## Performance Notes

- Model uses CUDA if available
- Folder processing limited to specified max_images (default: 7)
- Temporary files are automatically cleaned up
- GPU cache is cleared on shutdown
