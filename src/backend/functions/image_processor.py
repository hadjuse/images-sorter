from transformers import AutoProcessor, AutoModel, AutoTokenizer
import torch
import logging
from typing import List, Optional, Any
from dataclasses import dataclass, field
from folders import inference_on_images, get_list_images, path_folder_env

# Configure logger for this module
logger = logging.getLogger(__name__)


@dataclass
class ImageProcessor:
    """Encapsulates model, processor and image processing logic using dataclass"""
    
    model_id: str = "OpenGVLab/InternVL3_5-1B"
    _model: Optional[Any] = field(default=None, init=False, repr=False)
    _processor: Optional[AutoProcessor] = field(default=None, init=False, repr=False)
    _tokenizer: Optional[AutoTokenizer] = field(default=None, init=False, repr=False)
    _is_loaded: bool = field(default=False, init=False, repr=False)
    
    def __post_init__(self):
        """Initialize model and processor after dataclass creation"""
        self._load_model_and_processor()
    
    @property
    def model(self) -> Any:
        """Getter for the model"""
        if not self._is_loaded:
            self._load_model_and_processor()
        return self._model
    
    @model.setter
    def model(self, value: Any):
        """Setter for the model"""
        self._model = value
        
    @property
    def processor(self) -> Optional[AutoProcessor]:
        """Getter for the processor - Note: InternVL3.5 doesn't use AutoProcessor"""
        if not self._is_loaded:
            self._load_model_and_processor()
        # InternVL3.5 uses direct model.chat() API, no processor needed
        return self._processor
    
    @processor.setter
    def processor(self, value: AutoProcessor):
        """Setter for the processor"""
        self._processor = value
    
    @property
    def tokenizer(self) -> AutoTokenizer:
        """Getter for the tokenizer"""
        if not self._is_loaded:
            self._load_model_and_processor()
        if self._tokenizer is None:
            raise RuntimeError("Failed to load tokenizer")
        return self._tokenizer
    
    @tokenizer.setter
    def tokenizer(self, value: AutoTokenizer):
        """Setter for the tokenizer"""
        self._tokenizer = value
    
    @property
    def is_loaded(self) -> bool:
        """Check if model and processor are loaded"""
        return self._is_loaded
    
    def _load_model_and_processor(self):
        """Load the model and processor"""
        if self._is_loaded:
            return
            
        logger.info(f"Loading InternVL3.5 model: {self.model_id}")
        
        # Load tokenizer first for InternVL3.5
        logger.info("Loading tokenizer...")
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            use_fast=False
        )
        logger.info(f"Tokenizer loaded successfully. Vocab size: {len(self._tokenizer)}")
        
        # Load the model
        logger.info("Loading model (this may take a few minutes for first download)...")
        self._model = AutoModel.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            use_flash_attn=False,  # Disabled due to CUDA compilation issues
            trust_remote_code=True,
            device_map="auto"
        ).eval()
        
        logger.info(f"Model loaded successfully on device: {self._model.device if hasattr(self._model, 'device') else 'distributed'}")
        logger.info(f"Model dtype: {next(self._model.parameters()).dtype}")
        logger.info(f"Model memory footprint: {sum(p.numel() for p in self._model.parameters()) / 1e9:.2f}B parameters")
        
        # Note: We don't need AutoProcessor for InternVL3.5 as it uses direct model.chat() API
        # Setting processor to None to avoid initialization issues
        self._processor = None
        
        self._is_loaded = True
    
    def _validate_batch_inputs(self, image_paths: List[str], num_images: int) -> None:
        """Validate input parameters for batch processing."""
        if not image_paths:
            error_msg = "No image paths provided for processing"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if num_images <= 0:
            error_msg = "num_images must be a positive integer"
            logger.error(f"{error_msg}. Received: {num_images}")
            raise ValueError(error_msg)
    
    def _ensure_models_loaded(self) -> tuple[Any, Optional[AutoProcessor]]:
        """Ensure model is loaded and return it with processor (which may be None for InternVL3.5)."""
        try:
            model = self.model
            processor = self.processor
            logger.info("Model successfully accessed")
            return model, processor
        except RuntimeError as e:
            error_msg = f"Failed to load model: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during model loading: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _process_single_image(self, image_path: str, model: Any, 
                             image_index: int, total_images: int) -> bool:
        """
        Process a single image and return success status.
        
        Returns:
            bool: True if processing was successful, False otherwise.
        """
        logger.info(f"Starting processing of image {image_index}/{total_images}: {image_path}")
        
        try:
            import time
            start_time = time.time()
            
            response = inference_on_images(image_path, self.tokenizer, model)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            logger.info(f"Image {image_index}/{total_images} processed successfully in {processing_time:.2f}s")
            logger.info(f"Response preview: {response[:100]}{'...' if len(response) > 100 else ''}")
            print(f"Image {image_index}/{total_images}: {response}")
            return True
            
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return False
            
        except PermissionError:
            logger.error(f"Permission denied accessing file: {image_path}")
            return False
            
        except ValueError as e:
            logger.error(f"Invalid image format or data for {image_path}: {e}")
            return False
            
        except torch.cuda.OutOfMemoryError:
            logger.error(f"GPU out of memory while processing {image_path}")
            logger.warning("Attempting to clear GPU cache...")
            self.clear_cache()
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error processing {image_path}: {e}")
            return False
    
    def _log_batch_summary(self, successful_count: int, failed_count: int, total_processed: int) -> None:
        """Log and print the batch processing summary."""
        logger.info(f"Batch processing complete: {successful_count}/{total_processed} images processed successfully")
        
        if failed_count > 0:
            logger.warning(f"Failed to process {failed_count} image(s)")
            print(f"\nProcessing complete: {successful_count}/{total_processed} images processed successfully.")
            print(f"Failed to process {failed_count} image(s). Check logs for details.")
        else:
            logger.info("All images processed successfully")
            print(f"\nProcessing complete: All {successful_count} images processed successfully!")
    
    def _handle_complete_failure(self, total_processed: int) -> None:
        """Handle the case where no images were processed successfully."""
        error_msg = f"Failed to process any images from the batch of {total_processed}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def process_images_batch(self, image_paths: List[str], num_images: int = 7) -> None:
        """
        Process a batch of images and print the inference results.
        
        Args:
            image_paths (List[str]): A list of file paths to images that need to be processed.
            num_images (int, optional): Maximum number of images to process. Defaults to 7.
        
        Raises:
            ValueError: If input parameters are invalid.
            RuntimeError: If models can't be loaded or no images are processed successfully.
        """
        logger.info(f"Starting batch processing of {len(image_paths)} images (max: {num_images})")
        
        # Validate inputs
        self._validate_batch_inputs(image_paths, num_images)
        
        # Ensure models are loaded
        model, processor = self._ensure_models_loaded()
        
        # Process images
        total_to_process = min(num_images, len(image_paths))
        logger.info(f"Processing {total_to_process} images...")
        
        successful_count = 0
        for i in range(total_to_process):
            if self._process_single_image(image_paths[i], model, i + 1, total_to_process):
                successful_count += 1
        
        # Handle results
        failed_count = total_to_process - successful_count
        self._log_batch_summary(successful_count, failed_count, total_to_process)
        
        if successful_count == 0:
            self._handle_complete_failure(total_to_process)
    
    def reload_model(self, new_model_id: Optional[str] = None):
        """Reload the model with a new model_id if provided"""
        if new_model_id:
            self.model_id = new_model_id
        self._is_loaded = False
        self._model = None
        self._processor = None
        self._load_model_and_processor()
    
    def clear_cache(self):
        """Clear GPU cache to free memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

if __name__ == "__main__":
    image_processor: ImageProcessor = ImageProcessor()
    folder_test: List[str] = get_list_images(str(path_folder_env), "jpg")
    image_processor.process_images_batch(folder_test)