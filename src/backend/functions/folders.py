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
                {"type": "text", "text": f"Describe the image and what you only see."},
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
    
    outputs = model.generate(**inputs, max_new_tokens=128)
    response = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    
    # Clean the response to extract only the assistant's answer
    def clean_response(raw_response: str) -> str:
        # Split by "assistant" and get the last part
        if "assistant" in raw_response:
            assistant_response = raw_response.split("assistant")[-1]
        else:
            assistant_response = raw_response
        
        # Remove common template artifacts
        assistant_response = assistant_response.strip()
        
        # Remove leading whitespace, newlines, and common template markers
        while assistant_response.startswith(('\n', ' ', '\t', ':', '<', '>')):
            assistant_response = assistant_response[1:].strip()
        
        # Remove any remaining user/system prompts that might be included
        lines = assistant_response.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip lines that look like prompts or template artifacts
            if not (line.startswith('user ') or line.startswith('Explain in detail') or line.startswith('/tmp')):
                cleaned_lines.append(line)
        
        cleaned_response = '\n'.join(cleaned_lines).strip()
        
        # If we ended up with an empty response, return the original
        if not cleaned_response:
            return raw_response.strip()
            
        return cleaned_response
    
    cleaned_response = clean_response(response)
    logging.info(f"Cleaned response: {cleaned_response}")
    return cleaned_response


if __name__ == "__main__":
    folder_test: List[str] = get_list_images(str(path_folder_env), "heic")
    