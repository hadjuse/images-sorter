from transformers import AutoProcessor, AutoModelForImageTextToText
from transformers.image_utils import load_image
import torch


# This image depicts a vibrant street scene in what appears to be a Chinatown or similar cultural area. The focal point is a large red stop sign with white lettering, mounted on a pole.



def main():
    # Load model and processor
    model_id = "LiquidAI/LFM2-VL-1.6B"
    model = AutoModelForImageTextToText.from_pretrained(
        model_id,
        device_map="cuda:0",
        dtype="bfloat16",
        trust_remote_code=True
    )
    processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    # Load image and create conversation
    url = "https://www.ilankelman.org/stopsigns/australia.jpg"
    image = load_image(url)
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
    print(response)
if __name__ == "__main__":
    torch.cuda.empty_cache()
    main()
