from fastapi import FastAPI, HTTPException, File, UploadFile, Response
from fastapi.responses import FileResponse, StreamingResponse
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
import json
import asyncio
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

def ensure_image_processor_initialized():
    """Ensure image processor is initialized, create if not"""
    global image_processor
    if image_processor is None:
        print("Initializing image processor...")
        try:
            image_processor = ImageProcessor()
            print("Image processor initialized successfully")
        except Exception as e:
            print(f"Failed to initialize image processor: {e}")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    ensure_image_processor_initialized()
    
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

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development server
        "http://127.0.0.1:3000",  # Frontend development server (alternative)
        "http://localhost:5173",  # Vite development server
        "http://127.0.0.1:5173",  # Vite development server (alternative)
        "http://127.0.0.1:8000",  # Backend itself for internal requests
    ],
    allow_credentials=False,  # Disable credentials for security
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # All necessary methods
    allow_headers=["Content-Type", "Authorization", "Accept", "Accept-Language"],  # Common headers
)

# Special middleware for EventSource/Streaming requests
@app.middleware("http")
async def add_streaming_cors_headers(request, call_next):
    response = await call_next(request)
    # Add CORS headers specifically for streaming endpoints
    if request.url.path.endswith("/stream"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Cache-Control"
        response.headers["Access-Control-Expose-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "false"
    return response

# Additional middleware to ensure CORS headers are present on all responses
@app.middleware("http")
async def add_global_cors_headers(request, call_next):
    response = await call_next(request)
    # Add basic CORS headers to all responses for development
    if "Access-Control-Allow-Origin" not in response.headers:
        response.headers["Access-Control-Allow-Origin"] = "*"
    if "Access-Control-Allow-Methods" not in response.headers:
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    if "Access-Control-Allow-Headers" not in response.headers:
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

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
    ensure_image_processor_initialized()
    
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

@app.post("/process/image/stream")
async def process_single_image_stream(file: UploadFile = File(...)):
    """Process a single uploaded image with streaming response"""
    ensure_image_processor_initialized()
    
    # Log file details for debugging
    logger.info(f"Received file for streaming: filename={file.filename}, content_type={file.content_type}")
    
    # Check file type
    if not file.content_type or not file.content_type.startswith('image/'):
        logger.error(f"Invalid content type: {file.content_type} for file {file.filename}")
        raise HTTPException(status_code=400, detail=f"File must be an image (received: {file.content_type})")
    
    # Create temporary file
    temp_dir = None
    temp_file_path = None
    
    async def generate_stream():
        nonlocal temp_dir, temp_file_path
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
            temp_filename = f"{uuid.uuid4()}{file_extension}"
            temp_file_path = os.path.join(temp_dir, temp_filename)
            
            logger.info(f"Processing uploaded file for streaming: {file.filename}")
            logger.info(f"Temporary file path: {temp_file_path}")
            
            # Save uploaded file
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info("File saved successfully, starting streaming inference...")
            
            # Send start event
            yield json.dumps({
                "type": "start",
                "filename": file.filename,
                "message": "Starting image processing..."
            }) + "\n"
            
            # Process the image
            model, processor = image_processor._ensure_models_loaded()
            
            # Send processing event
            yield json.dumps({
                "type": "processing",
                "filename": file.filename,
                "message": "Running inference on image..."
            }) + "\n"
            
            response = inference_on_images(temp_file_path, image_processor.tokenizer, model)
            
            logger.info(f"Inference completed for {file.filename}")
            
            # Send result event
            yield json.dumps({
                "type": "result",
                "filename": file.filename,
                "status": "success",
                "description": response
            }) + "\n"
            
            # Send complete event
            yield json.dumps({
                "type": "complete",
                "filename": file.filename,
                "message": "Image processing completed successfully"
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error processing image in stream: {str(e)}")
            yield json.dumps({
                "type": "error",
                "filename": file.filename,
                "error": str(e)
            }) + "\n"
        
        finally:
            # Clean up temporary files
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temporary file: {cleanup_error}")
            
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temporary directory: {cleanup_error}")
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.post("/process/folder")
async def process_folder(request: FolderRequest):
    """Process images from a folder using the existing image processor methods"""
    ensure_image_processor_initialized()
        
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

@app.get("/process/folder/stream")
async def process_folder_stream(
    folder_path: str,
    extension: str = "jpg",
    max_images: int = 7,
    response: Response = None  # Add response parameter for header manipulation
):
    """Process images from a folder with streaming response"""
    ensure_image_processor_initialized()
        
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {folder_path}")
    
    # Set CORS headers specifically for streaming endpoints
    if response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "false"
    
    async def generate_stream():
        try:
            # Get list of images from folder
            image_paths = get_list_images(folder_path, extension)
            
            if not image_paths:
                yield json.dumps({
                    "type": "complete",
                    "message": f"No {extension} images found in folder",
                    "total_found": 0,
                    "results": []
                }) + "\n"
                return
            
            # Send initial metadata
            yield json.dumps({
                "type": "metadata",
                "folder_path": folder_path,
                "extension": extension,
                "total_found": len(image_paths),
                "processed": 0,
                "successful": 0,
                "failed": 0
            }) + "\n"
            
            # Get model and processor
            model, processor = image_processor._ensure_models_loaded()
            
            # Process limited number of images
            images_to_process = image_paths[:max_images]
            successful = 0
            
            for i, image_path in enumerate(images_to_process):
                try:
                    # Send start event for this image
                    yield json.dumps({
                        "type": "start",
                        "image_path": image_path,
                        "index": i + 1,
                        "total": len(images_to_process)
                    }) + "\n"
                    
                    # Process the image and stream the response
                    response = inference_on_images(image_path, image_processor.tokenizer, model)
                    
                    # Send the result
                    yield json.dumps({
                        "type": "result",
                        "image_path": image_path,
                        "status": "success",
                        "description": response
                    }) + "\n"
                    
                    successful += 1
                    
                except Exception as e:
                    yield json.dumps({
                        "type": "result",
                        "image_path": image_path,
                        "status": "error",
                        "error": str(e)
                    }) + "\n"
            
            # Send final summary
            yield json.dumps({
                "type": "complete",
                "processed": len(images_to_process),
                "successful": successful,
                "failed": len(images_to_process) - successful
            }) + "\n"
            
        except Exception as e:
            yield json.dumps({
                "type": "error",
                "error": str(e)
            }) + "\n"
    
    return StreamingResponse(generate_stream(), media_type="text/event-stream")

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