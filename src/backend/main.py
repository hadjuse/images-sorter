from functions import ImageProcessor, get_list_images, path_folder_env
import logging


def main():
    # Initialize the image processor
    processor = ImageProcessor()
    
    # Get list of images
    folder_test = get_list_images(str(path_folder_env), "jpg")
    
    # Process the images
    processor.process_images_batch(folder_test)
if __name__ == "__main__":
    #qtorch.cuda.empty_cache()
    main()
