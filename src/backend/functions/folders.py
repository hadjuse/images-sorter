import glob
import os
from dotenv import load_dotenv, dotenv_values
from typing import List
import torch
import torchvision.transforms as T
import math
import numpy as np
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
from transformers.image_utils import load_image
from transformers import AutoProcessor, AutoModel
import os
import logging
load_dotenv()

path_folder_env=os.getenv("PATH_TO_FOLDER_TEST")

# InternVL3.5 Image preprocessing constants and functions
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

def build_transform(input_size):
    MEAN, STD = IMAGENET_MEAN, IMAGENET_STD
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=MEAN, std=STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio

def dynamic_preprocess(image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
        i * j <= max_num and i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images

def load_image_for_internvl(image_file, input_size=448, max_num=6):
    """Load and preprocess image for InternVL3.5 model
    
    Note: Reduced max_num to 6 and disabled thumbnail for CPU performance
    """
    image = Image.open(image_file).convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image, image_size=input_size, use_thumbnail=False, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values.to(torch.bfloat16)

def get_list_images(path: str, ext: str) -> List[str]:
    """
    This function return list of files into a folder

    Args:
        path (str): the path of where to load files
        ext (str): the extension of the file
    
    Returns:
        List[str]: The list of files from the extension 
    """
    return glob.glob(f"{path}/*.{ext}")

def inference_on_images_alternative(path: str, tokenizer, model) -> str:
    """
    Alternative inference approach using direct tokenization and generation
    """
    try:
        logging.info(f"Starting alternative inference for image: {path}")
        
        # Load and preprocess image
        pixel_values = load_image_for_internvl(path)
        
        # Move to device
        if hasattr(model, 'device'):
            device = model.device
            pixel_values = pixel_values.to(device)
        elif torch.cuda.is_available():
            pixel_values = pixel_values.cuda()
        
        # Create simple prompt
        prompt = "<image>\nDescribe this image."
        logging.info(f"Using prompt: {prompt}")
        
        # Tokenize the prompt
        inputs = tokenizer(prompt, return_tensors='pt')
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Add pixel values to inputs
        inputs['pixel_values'] = pixel_values
        
        logging.info("Starting direct generation...")
        
        # Use model.generate directly
        try:
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=128,  # Reduced for CPU performance
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the prompt from response
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            logging.info(f"Alternative inference completed: {response[:100]}...")
            return response
            
        except Exception as e:
            logging.error(f"Alternative generation failed: {e}")
            return f"Error in alternative processing: {str(e)}"
        
    except Exception as e:
        logging.error(f"Alternative inference failed: {e}")
        return f"Error in alternative inference: {str(e)}"


def inference_on_images(path: str, tokenizer, model) -> str:
    """
    Perform image inference using InternVL3.5-2B model
    """
    try:
        logging.info(f"Starting inference for image: {path}")
        
        # Load and preprocess image for InternVL3.5
        logging.info("Loading and preprocessing image...")
        pixel_values = load_image_for_internvl(path)
        logging.info(f"Image preprocessed - shape: {pixel_values.shape}, dtype: {pixel_values.dtype}")
        
        # Move to the same device as the model
        if hasattr(model, 'device'):
            device = model.device
            logging.info(f"Moving pixel values to model device: {device}")
            pixel_values = pixel_values.to(device)
        elif torch.cuda.is_available():
            logging.info("Moving pixel values to CUDA")
            pixel_values = pixel_values.cuda()
        else:
            logging.info("Using CPU for inference")
        
        # InternVL3.5 uses the model.chat() API with pixel values and <image> token
        question = "<image>\nDescribe this image briefly."
        logging.info(f"Question for model: {question}")
        
        # Use the model.chat interface with preprocessed pixel values
        logging.info("Starting model.chat() inference...")
        generation_config = dict(
            max_new_tokens=128,  # Reduced for faster CPU inference
            do_sample=False
        )
        logging.info(f"Generation config: {generation_config}")
        
        # Run inference without timeout constraints
        response = model.chat(
            tokenizer, 
            pixel_values, 
            question, 
            generation_config=generation_config
        )
        logging.info("Model chat completed successfully")
        
        logging.info(f"Inference completed successfully. Response length: {len(response) if response else 0}")
        logging.debug(f"Full response: {response}")
        
        return response
        
    except Exception as e:
        logging.error(f"Error processing image {path}: {e}")
        return f"Error processing image: {str(e)}"
    

if __name__ == "__main__":
    folder_test: List[str] = get_list_images(str(path_folder_env), "heic")
    