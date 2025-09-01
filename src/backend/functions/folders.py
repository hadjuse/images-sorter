import glob
import os
from dotenv import load_dotenv, dotenv_values
from typing import List
from transformers.image_utils import load_image
from transformers import AutoProcessor, AutoModelForImageTextToText
import os
import logging
load_dotenv()

path_folder_env=os.getenv("PATH_TO_FOLDER_TEST")

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

def inference_on_images(path: str, processor, model) -> str:
    image=load_image(path)
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "What is in this image?"},
            ],
        },
    ]

    # Generate Answer
    inputs = processor.apply_chat_template(
        conversation,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
        tokenize=True,
    ).to(model.device)
    
    outputs = model.generate(**inputs, max_new_tokens=64)
    response = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    logging.info(f"{response}")
    return response

def process_images_batch(folder_test: List[str], processor, model, num_images: int = 7):
    """
    Process a batch of images and print the inference results.
    
    Args:
        folder_test: List of image paths
        processor: The image processor
        model: The model for inference
        num_images: Number of images to process (default: 7)
    """
    for i in range(min(num_images, len(folder_test))):
        images_path = folder_test[i]
        response = inference_on_images(images_path, processor, model)
        print(response)

if __name__ == "__main__":
    folder_test: List[str] = get_list_images(str(path_folder_env), "heic")
    