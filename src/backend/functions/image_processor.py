from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
from typing import List, Optional, Any
from dataclasses import dataclass, field
from .folders import inference_on_images


@dataclass
class ImageProcessor:
    """Encapsulates model, processor and image processing logic using dataclass"""
    
    model_id: str = "LiquidAI/LFM2-VL-1.6B"
    _model: Optional[Any] = field(default=None, init=False, repr=False)
    _processor: Optional[AutoProcessor] = field(default=None, init=False, repr=False)
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
    def processor(self) -> AutoProcessor:
        """Getter for the processor"""
        if not self._is_loaded:
            self._load_model_and_processor()
        if self._processor is None:
            raise RuntimeError("Failed to load processor")
        return self._processor
    
    @processor.setter
    def processor(self, value: AutoProcessor):
        """Setter for the processor"""
        self._processor = value
    
    @property
    def is_loaded(self) -> bool:
        """Check if model and processor are loaded"""
        return self._is_loaded
    
    def _load_model_and_processor(self):
        """Load the model and processor"""
        if self._is_loaded:
            return
            
        self._model = AutoModelForImageTextToText.from_pretrained(
            self.model_id,
            device_map="cuda:0",
            dtype=torch.bfloat16,
            trust_remote_code=True
        )
        
        self._processor = AutoProcessor.from_pretrained(
            self.model_id, 
            trust_remote_code=True
        )
        
        self._is_loaded = True
    
    def process_images_batch(self, image_paths: List[str], num_images: int = 7):
        """Process a batch of images and print the inference results"""
        for i in range(min(num_images, len(image_paths))):
            response = inference_on_images(image_paths[i], self.processor, self.model)
            print(response)
    
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
