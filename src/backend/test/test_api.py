#!/usr/bin/env python3
"""
Comprehensive API tests for the Image Processing API
"""

import pytest
import os
import tempfile
import shutil
import urllib.parse
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys

# Add the api directory to the path so we can import the app
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

from api import app, image_processor

# Create a test client
client = TestClient(app)


class MockImageProcessor:
    """Mock image processor for testing"""
    
    def __init__(self):
        self.tokenizer = MagicMock()
        self._models_loaded = False
        
    def _ensure_models_loaded(self):
        self._models_loaded = True
        return MagicMock(), MagicMock()
        
    def clear_cache(self):
        pass


@pytest.fixture(autouse=True, scope="function")
def setup_test_environment():
    """Setup test environment with mock image processor"""
    # Import the api module to access the global image_processor
    import api
    
    # Save original processor
    original_processor = api.image_processor
    
    # Setup mock processor
    api.image_processor = MockImageProcessor()
    
    yield
    
    # Restore original processor
    api.image_processor = original_processor


def create_test_image(folder_path, filename="test.jpg", content=b"fake image data"):
    """Create a test image file"""
    image_path = os.path.join(folder_path, filename)
    with open(image_path, 'wb') as f:
        f.write(content)
    return image_path


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Image Processing API is running"}


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.fixture
def test_image_file():
    """Create a temporary test image file"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(b"fake image data")
        temp_file_path = temp_file.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)


def test_process_single_image_success(test_image_file):
    """Test successful single image processing"""
    
    with patch('api.inference_on_images', return_value="test description"):
        with open(test_image_file, 'rb') as f:
            response = client.post("/process/image", files={"file": ("test.jpg", f, "image/jpeg")})
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.jpg"
    assert data["status"] == "success"
    assert data["description"] == "test description"


def test_process_single_image_invalid_content_type():
    """Test single image processing with invalid content type"""

def test_process_single_image_no_file():
    """Test single image processing without a file"""

def test_process_single_image_stream_success(test_image_file):
    """Test successful single image streaming processing"""

def test_process_single_image_stream_invalid_content_type():
    """Test single image streaming with invalid content type"""

@pytest.fixture
def test_folder_with_images():
    """Create a temporary folder with test images"""
    temp_dir = tempfile.mkdtemp()
    
    # Create some test images
    for i in range(3):
        create_test_image(temp_dir, f"test{i}.jpg")
    
    yield temp_dir
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_process_folder_success(test_folder_with_images):
    """Test successful folder processing"""

def test_process_folder_not_found():
    """Test folder processing with non-existent folder"""

def test_process_folder_not_a_directory():
    """Test folder processing with a file path instead of directory"""

def test_process_folder_stream_success(test_folder_with_images):
    """Test successful folder streaming processing"""

def test_process_folder_stream_not_found():
    """Test folder streaming with non-existent folder"""

def test_process_folder_stream_not_a_directory():
    """Test folder streaming with a file path instead of directory"""

def test_preview_folder_images_success(test_folder_with_images):
    """Test successful folder preview"""
    response = client.post("/preview/folder", json={
        "folder_path": test_folder_with_images,
        "extension": "jpg"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["folder_path"] == test_folder_with_images
    assert data["extension"] == "jpg"
    assert data["total_found"] == 3
    assert len(data["image_paths"]) == 3


def test_preview_folder_images_not_found():
    """Test folder preview with non-existent folder"""
    response = client.post("/preview/folder", json={
        "folder_path": "/non/existent/folder",
        "extension": "jpg"
    })
    
    assert response.status_code == 404
    assert "Folder not found" in response.json()["detail"]


def test_preview_folder_images_not_a_directory():
    """Test folder preview with a file path instead of directory"""
    response = client.post("/preview/folder", json={
        "folder_path": __file__,
        "extension": "jpg"
    })
    
    assert response.status_code == 400
    assert "Path is not a directory" in response.json()["detail"]


def test_serve_image_success(test_image_file):
    """Test successful image serving"""
    # URL encode the path
    encoded_path = urllib.parse.quote(test_image_file)
    
    response = client.get(f"/image/{encoded_path}")
    
    assert response.status_code == 200
    # The content type should be image/jpeg for .jpg files
    assert response.headers["content-type"] == "image/jpeg"


def test_serve_image_not_found():
    """Test image serving with non-existent image"""
    # Use an absolute path that doesn't exist
    response = client.get("/image/" + urllib.parse.quote("/absolute/path/to/non_existent.jpg"))
    
    assert response.status_code == 404
    assert "Image not found" in response.json()["detail"]


def test_serve_image_not_a_file():
    """Test image serving with a directory path"""
    response = client.get("/image/" + urllib.parse.quote(os.path.dirname(__file__)))
    
    assert response.status_code == 400
    assert "Path is not a file" in response.json()["detail"]


def test_serve_image_not_an_image():
    """Test image serving with a non-image file"""
    response = client.get("/image/" + urllib.parse.quote(__file__))
    
    assert response.status_code == 400
    assert "File is not an image" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])