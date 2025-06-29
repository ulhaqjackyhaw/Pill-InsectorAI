# sudo pip3 install pillow

from PIL import Image
import os

def resize_images(input_dir, output_dir):
    """
    Resizes all JPEG images in the input directory so that the longest side is 640 pixels.

    Args:
        input_dir: Path to the input directory containing JPEG images.
        output_dir: Path to the output directory where resized images will be saved.
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            img_path = os.path.join(input_dir, filename)
            img = Image.open(img_path)

            # Calculate the new dimensions
            width, height = img.size
            if width > height:
                new_width = 640
                new_height = int(height * (640 / width))
            else:
                new_height = 640
                new_width = int(width * (640 / height))

            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.NEAREST)

            # Save the resized image
            output_path = os.path.join(output_dir, filename)
            resized_img.save(output_path, quality=95)

if __name__ == "__main__":
    input_dir = os.getcwd()  # Use current directory as input
    output_dir = os.path.join(input_dir, "output")  # Create "output" folder in current directory
    resize_images(input_dir, output_dir)