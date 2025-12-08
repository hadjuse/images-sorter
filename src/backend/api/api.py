from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
import os
import sys
import tempfile
import uuid
import shutil
import logging
from urllib.parse import unquote

# Configure logger
logger = logging.getLogger(__name__)

# Add functions folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'functions'))

try:
    from image_processor import ImageProcessor
    from folders import get_list_images, inference_on_images
except ImportError as e:
    print(f"Import error: {e}")
    raise

# Global image processor instance
image_processor: Optional[ImageProcessor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    global image_processor
    print("Initializing image processor...")
    image_processor = ImageProcessor()
    print("Image processor initialized successfully")
    
    yield
    
    # Shutdown
    if image_processor:
        print("Cleaning up resources...")
        image_processor.clear_cache()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Image Processing API", 
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Allow any origin for development (can restrict later)
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class FolderRequest(BaseModel):
    folder_path: str
    extension: str = "jpg"
    max_images: int = 7

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Image Processing API is running"}

@app.get("/health")
async def health():
    """Health check endpoint for Docker"""
    return {"status": "healthy"}

@app.post("/process/image")
async def process_single_image(file: UploadFile = File(...)):
    """Process a single uploaded image"""
    if image_processor is None:
        raise HTTPException(status_code=503, detail="Image processor not initialized")
    
    # Log file details for debugging
    logger.info(f"Received file: filename={file.filename}, content_type={file.content_type}")
    
    # Check file type
    if not file.content_type or not file.content_type.startswith('image/'):
        logger.error(f"Invalid content type: {file.content_type} for file {file.filename}")
        raise HTTPException(status_code=400, detail=f"File must be an image (received: {file.content_type})")
    
    # Create temporary file
    temp_dir = None
    temp_file_path = None
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        temp_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join(temp_dir, temp_filename)
        
        logger.info(f"Processing uploaded file: {file.filename} (size: {file.size if hasattr(file, 'size') else 'unknown'} bytes)")
        logger.info(f"Temporary file path: {temp_file_path}")
        
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info("File saved successfully, starting inference...")
        
        # Process the image
        model, processor = image_processor._ensure_models_loaded()
        response = inference_on_images(temp_file_path, image_processor.tokenizer, model)
        
        logger.info(f"Inference completed for {file.filename}")
        
        # Cleanup
        try:
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
            logger.debug(f"Cleaned up temporary files: {temp_file_path}")
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup temporary files: {cleanup_error}")
        
        return {
            "filename": file.filename,
            "status": "success",
            "description": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    finally:
        # Clean up temporary files
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

@app.post("/process/folder")
async def process_folder(request: FolderRequest):
    """Process images from a folder using the existing image processor methods"""
    if image_processor is None:
        raise HTTPException(status_code=503, detail="Image processor not initialized")
        
    if not os.path.exists(request.folder_path):
        raise HTTPException(status_code=404, detail=f"Folder not found: {request.folder_path}")
    
    if not os.path.isdir(request.folder_path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.folder_path}")
    
    try:
        # Get list of images from folder
        image_paths = get_list_images(request.folder_path, request.extension)
        
        if not image_paths:
            return {
                "message": f"No {request.extension} images found in folder",
                "total_found": 0,
                "results": []
            }
        
        # Get model and processor
        model, processor = image_processor._ensure_models_loaded()
        
        # Process limited number of images
        images_to_process = image_paths[:request.max_images]
        results = []
        successful = 0
        
        for i, image_path in enumerate(images_to_process):
            try:
                response = inference_on_images(image_path, image_processor.tokenizer, model)
                results.append({
                    "image_path": image_path,
                    "status": "success", 
                    "description": response
                })
                successful += 1
            except Exception as e:
                results.append({
                    "image_path": image_path,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "folder_path": request.folder_path,
            "extension": request.extension,
            "total_found": len(image_paths),
            "processed": len(images_to_process),
            "successful": successful,
            "failed": len(images_to_process) - successful,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing folder: {str(e)}")

@app.post("/preview/folder")
async def preview_folder_images(request: FolderRequest):
    """Get list of images in a folder for preview"""
    if not os.path.exists(request.folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")
    
    if not os.path.isdir(request.folder_path):
        raise HTTPException(status_code=400, detail="Path is not a directory")
    
    try:
        # Get list of images
        image_paths = get_list_images(request.folder_path, request.extension)
        
        return {
            "folder_path": request.folder_path,
            "extension": request.extension,
            "total_found": len(image_paths),
            "image_paths": image_paths
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing folder: {str(e)}")

@app.get("/image/{image_path:path}")
async def serve_image(image_path: str):
    """Serve images from the server filesystem for display in the frontend"""
    try:
        # Decode the URL-encoded path
        decoded_path = unquote(image_path)
        
        # Security check: ensure the path is absolute and exists
        if not os.path.isabs(decoded_path):
            raise HTTPException(status_code=400, detail="Only absolute paths are allowed")
        
        if not os.path.exists(decoded_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        if not os.path.isfile(decoded_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Additional security: check if it's actually an image file
        allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic')
        if not decoded_path.lower().endswith(allowed_extensions):
            raise HTTPException(status_code=400, detail="File is not an image")
        
        return FileResponse(decoded_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)